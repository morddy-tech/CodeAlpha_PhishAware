import math
import random

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.db.models import Count, Sum
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from progress.models import Notification
from progress.services import create_notification, evaluate_achievements
from quizzes.models import Question, Quiz, QuizAttempt, UserAnswer


def _attempt_session_key(quiz):
    return f"quiz_attempt_{quiz.pk}"


def _order_session_key(quiz):
    return f"quiz_order_{quiz.pk}"


def _open_attempt(user, quiz):
    return user.quiz_attempts.filter(
        quiz=quiz, completed_at__isnull=True
    ).first()


def _get_or_create_attempt(user, quiz):
    attempt = _open_attempt(user, quiz)
    if attempt is not None:
        return attempt
    try:
        return QuizAttempt.objects.create(user=user, quiz=quiz)
    except IntegrityError:
        # The conditional unique constraint won a race with another request.
        return _open_attempt(user, quiz)


def _remaining_seconds(quiz, attempt):
    if not quiz.time_limit:
        return None
    elapsed = (timezone.now() - attempt.started_at).total_seconds()
    return max(0, math.ceil(quiz.time_limit - elapsed))


def _clear_attempt_session(request, quiz):
    request.session.pop(_attempt_session_key(quiz), None)
    request.session.pop(_order_session_key(quiz), None)


def _finalize_expired_attempt(request, quiz, attempt, now):
    elapsed = max(0, int((now - attempt.started_at).total_seconds()))
    attempt.score = 0
    attempt.percentage = 0
    attempt.passed = False
    attempt.duration_seconds = min(elapsed, quiz.time_limit)
    attempt.completed_at = now
    attempt.save(
        update_fields=[
            "score",
            "percentage",
            "passed",
            "duration_seconds",
            "completed_at",
        ]
    )
    _clear_attempt_session(request, quiz)
    create_notification(
        request.user,
        "Quiz time expired",
        f'Time ran out before you submitted "{quiz.title}". No late answers were accepted.',
        Notification.NotificationType.QUIZ,
    )
    evaluate_achievements(request.user)


def quiz_list(request):
    search = request.GET.get("q", "").strip()
    quizzes = (
        Quiz.objects.filter(published=True)
        .annotate(question_count=Count("questions"))
        .prefetch_related("questions")
    )
    if search:
        quizzes = quizzes.filter(title__icontains=search)

    attempts = {}
    if request.user.is_authenticated:
        for attempt in (
            request.user.quiz_attempts.filter(completed_at__isnull=False)
            .select_related("quiz")
            .order_by("-started_at")
        ):
            current = attempts.get(attempt.quiz_id)
            if current is None:
                attempts[attempt.quiz_id] = attempt
                continue
            if attempt.percentage > current.percentage or (
                attempt.percentage == current.percentage
                and attempt.started_at > current.started_at
            ):
                attempts[attempt.quiz_id] = attempt

    return render(
        request,
        "quizzes/list.html",
        {
            "quizzes": quizzes,
            "attempts": attempts,
            "search": search,
        },
    )


@login_required
def quiz_detail(request, pk):
    quiz = get_object_or_404(
        Quiz.objects.annotate(
            question_count=Count("questions"),
            total_points_sum=Coalesce(Sum("questions__points"), 0),
        ),
        pk=pk,
        published=True,
    )
    attempts = (
        request.user.quiz_attempts.filter(quiz=quiz)
        .select_related("quiz")
        .order_by("-started_at")[:10]
    )
    return render(
        request,
        "quizzes/detail.html",
        {
            "quiz": quiz,
            "attempts": attempts,
            "total_points": quiz.total_points_sum,
        },
    )


@login_required
def quiz_take(request, pk):
    quiz = get_object_or_404(
        Quiz.objects.prefetch_related("questions__answers"),
        pk=pk,
        published=True,
    )
    questions = list(quiz.questions.all().order_by("order", "id"))
    if not questions:
        messages.error(request, "This quiz has no questions yet.")
        return redirect("quizzes:detail", pk=pk)

    total_points = sum(q.points for q in questions)

    if request.method == "POST":
        return _submit_quiz(request, quiz, questions, total_points)

    # GET: begin (or resume) an attempt. The attempt's started_at is the
    # authoritative timer; refreshing never resets it.
    attempt = _get_or_create_attempt(request.user, quiz)
    request.session[_attempt_session_key(quiz)] = attempt.pk

    order_key = _order_session_key(quiz)
    order = request.session.get(order_key)
    valid_ids = {question.id for question in questions}
    if not order or any(question_id not in valid_ids for question_id in order):
        order = [question.id for question in questions]
        random.shuffle(order)
        request.session[order_key] = order

    question_choices = []
    by_id = {question.id: question for question in questions}
    for question_id in order:
        question = by_id.get(question_id)
        if question is None:
            continue
        options = list(question.answers.all())
        random.shuffle(options)
        question_choices.append((question, options))
    if len(question_choices) != len(questions):
        question_choices = []
        for question in questions:
            options = list(question.answers.all())
            random.shuffle(options)
            question_choices.append((question, options))

    return render(
        request,
        "quizzes/take.html",
        {
            "quiz": quiz,
            "question_choices": question_choices,
            "total_points": total_points,
            "attempt": attempt,
            "remaining_seconds": _remaining_seconds(quiz, attempt),
        },
    )


def _submit_quiz(request, quiz, questions, total_points):
    attempt_id = request.session.get(_attempt_session_key(quiz))
    if not attempt_id:
        messages.error(request, "Please start the quiz before submitting answers.")
        return redirect("quizzes:detail", pk=quiz.pk)

    with transaction.atomic():
        attempt = (
            QuizAttempt.objects.select_for_update()
            .filter(pk=attempt_id, user=request.user, quiz=quiz)
            .first()
        )
        if attempt is None:
            messages.error(request, "That quiz attempt could not be found.")
            return redirect("quizzes:detail", pk=quiz.pk)

        if attempt.completed_at is not None:
            messages.info(request, "That attempt was already submitted.")
            return redirect("quizzes:result", attempt_id=attempt.pk)

        now = timezone.now()
        elapsed = max(0.0, (now - attempt.started_at).total_seconds())
        tolerance = getattr(settings, "QUIZ_CLOCK_TOLERANCE_SECONDS", 5)
        if quiz.time_limit and elapsed > quiz.time_limit + tolerance:
            _finalize_expired_attempt(request, quiz, attempt, now)
            return redirect("quizzes:result", attempt_id=attempt.pk)

        order = request.session.get(
            _order_session_key(quiz), [q.id for q in questions]
        )
        by_id = {question.id: question for question in questions}
        ordered = []
        seen = set()
        for question_id in order:
            if question_id in by_id and question_id not in seen:
                seen.add(question_id)
                ordered.append(by_id[question_id])
        if len(ordered) != len(questions):
            ordered = questions

        score = 0
        for question in ordered:
            selected_id = request.POST.get(f"question_{question.id}", "")
            selected = None
            if selected_id:
                selected = question.answers.filter(id=selected_id).first()
            is_correct = bool(selected and selected.is_correct)
            points = question.points if is_correct else 0
            score += points
            UserAnswer.objects.update_or_create(
                attempt=attempt,
                question=question,
                defaults={
                    "selected_option": selected,
                    "is_correct": is_correct,
                    "points_awarded": points,
                },
            )

        percentage = round(score / total_points * 100) if total_points else 0
        attempt.score = score
        attempt.percentage = percentage
        attempt.passed = percentage >= quiz.passing_score
        attempt.duration_seconds = min(int(elapsed), quiz.time_limit) if quiz.time_limit else int(elapsed)
        attempt.completed_at = now
        attempt.save(
            update_fields=[
                "score",
                "percentage",
                "passed",
                "duration_seconds",
                "completed_at",
            ]
        )

    _clear_attempt_session(request, quiz)
    create_notification(
        request.user,
        "Quiz completed",
        f'You scored {percentage}% on "{quiz.title}".',
        Notification.NotificationType.QUIZ,
    )
    evaluate_achievements(request.user)
    return redirect("quizzes:result", attempt_id=attempt.pk)


@login_required
def quiz_result(request, attempt_id):
    attempt = get_object_or_404(
        QuizAttempt.objects.select_related("quiz"),
        pk=attempt_id,
        user=request.user,
    )
    user_answers = list(
        UserAnswer.objects.filter(attempt=attempt).select_related(
            "question", "selected_option"
        )
    )
    answers_by_question = {ua.question_id: ua for ua in user_answers}
    questions = list(
        Question.objects.filter(quiz=attempt.quiz).order_by("order", "id")
    )
    total_points = sum(q.points for q in questions)

    return render(
        request,
        "quizzes/result.html",
        {
            "attempt": attempt,
            "quiz": attempt.quiz,
            "questions": questions,
            "answers_by_question": answers_by_question,
            "total_points": total_points,
        },
    )

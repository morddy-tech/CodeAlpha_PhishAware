import random

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from progress.models import Notification
from progress.services import create_notification, evaluate_achievements
from quizzes.models import Question, Quiz, QuizAttempt, UserAnswer


def quiz_list(request):
    search = request.GET.get("q", "").strip()
    quizzes = Quiz.objects.filter(published=True).prefetch_related("questions")
    if search:
        quizzes = quizzes.filter(title__icontains=search)

    attempts = {}
    if request.user.is_authenticated:
        attempts = {
            attempt.quiz_id: attempt
            for attempt in request.user.quiz_attempts.filter(completed_at__isnull=False)
            .select_related("quiz")
            .order_by("-started_at")
        }

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
    quiz = get_object_or_404(Quiz, pk=pk, published=True)
    attempts = (
        request.user.quiz_attempts.filter(quiz=quiz)
        .select_related("quiz")
        .order_by("-started_at")[:10]
    )
    return render(
        request,
        "quizzes/detail.html",
        {"quiz": quiz, "attempts": attempts},
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
        # Server-side scoring. The client can never set the score.
        attempt = _get_or_create_attempt(request.user, quiz)
        order = request.session.get(f"quiz_order_{quiz.pk}", [q.id for q in questions])
        ordered = [next((q for q in questions if q.id == qid), None) for qid in order]
        ordered = [q for q in ordered if q]

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
        passed = percentage >= quiz.passing_score
        attempt.score = score
        attempt.percentage = percentage
        attempt.passed = passed
        attempt.duration_seconds = max(
            0,
            int((timezone.now() - attempt.started_at).total_seconds()),
        )
        attempt.completed_at = timezone.now()
        attempt.save()

        request.session.pop(f"quiz_order_{quiz.pk}", None)

        create_notification(
            request.user,
            "Quiz completed",
            f"You scored {percentage}% on “{quiz.title}”.",
            Notification.NotificationType.QUIZ,
        )
        evaluate_achievements(request.user)

        return redirect("quizzes:result", attempt_id=attempt.pk)

    # GET: begin (or resume) an attempt and remember question order.
    attempt = _get_or_create_attempt(request.user, quiz)
    order = [q.id for q in questions]
    random.shuffle(order)
    request.session[f"quiz_order_{quiz.pk}"] = order

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
        },
    )


@login_required
def quiz_result(request, attempt_id):
    attempt = get_object_or_404(
        QuizAttempt.objects.select_related("quiz"),
        pk=attempt_id,
        user=request.user,
    )
    user_answers = list(
        UserAnswer.objects.filter(attempt=attempt)
        .select_related("question", "selected_option")
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


def _get_or_create_attempt(user, quiz):
    attempt = user.quiz_attempts.filter(quiz=quiz, completed_at__isnull=True).first()
    if attempt is None:
        attempt = QuizAttempt.objects.create(user=user, quiz=quiz)
    return attempt
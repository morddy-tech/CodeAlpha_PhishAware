"""Aggregation helpers for the user dashboard and the admin analytics dashboard."""

from django.contrib.auth.models import User
from django.db.models import Avg, Count

from core.models import Feedback
from progress.models import ModuleProgress
from quizzes.models import QuizAttempt, UserAnswer
from simulations.models import PhishingScenario, ScenarioAttempt
from training.models import TrainingModule


def recent_activity(user, limit=6):
    """Combined, time-sorted list of the user's recent learning events."""
    events = []
    for attempt in user.quiz_attempts.filter(completed_at__isnull=False).select_related("quiz")[:limit]:
        events.append(
            {
                "kind": "quiz",
                "title": f"Quiz completed: {attempt.quiz.title}",
                "detail": f"{attempt.percentage}% · {'Passed' if attempt.passed else 'Needs review'}",
                "when": attempt.completed_at,
                "url": f"/quizzes/attempt/{attempt.pk}/result/",
                "icon": "brain",
            }
        )
    for completion in user.lesson_completions.select_related("lesson")[:limit]:
        events.append(
            {
                "kind": "lesson",
                "title": f"Lesson completed: {completion.lesson.title}",
                "detail": completion.lesson.module.title,
                "when": completion.completed_at,
                "url": f"/training/lesson/{completion.lesson.slug}/",
                "icon": "book",
            }
        )
    for attempt in user.scenario_attempts.select_related("scenario")[:limit]:
        events.append(
            {
                "kind": "scenario",
                "title": f"Scenario reviewed: {attempt.scenario.title}",
                "detail": f"Score {attempt.score}%",
                "when": attempt.completed_at,
                "url": f"/simulations/scenario/{attempt.scenario.pk}/",
                "icon": "shield",
            }
        )
    events.sort(key=lambda e: e["when"], reverse=True)
    return events[:limit]


def recommended_training(user):
    """Modules the user has not yet completed, most advanced first."""
    completed_ids = ModuleProgress.objects.filter(
        user=user, completed=True
    ).values_list("module_id", flat=True)
    return (
        TrainingModule.objects.filter(published=True)
        .exclude(id__in=completed_ids)
        .order_by("order")[:3]
    )


def admin_overview():
    users = User.objects.all()
    quiz_attempts = QuizAttempt.objects.filter(completed_at__isnull=False)
    modules = TrainingModule.objects.filter(published=True)
    scenarios = PhishingScenario.objects.filter(published=True)

    total_attempts = quiz_attempts.count()
    avg_score = (
        round(quiz_attempts.aggregate(avg=Avg("percentage"))["avg"])
        if total_attempts
        else 0
    )
    passed = quiz_attempts.filter(passed=True).count()
    completion_rate = round(passed / total_attempts * 100) if total_attempts else 0

    modules_completed = ModuleProgress.objects.filter(completed=True).count()
    total_modules = modules.count()
    module_completion_rate = (
        round(modules_completed / (total_modules * max(users.count(), 1)) * 100)
        if total_modules
        else 0
    )

    return {
        "total_users": users.count(),
        "active_learners": users.filter(is_active=True).count(),
        "modules": modules.count(),
        "quizzes": _count_published_quizzes(),
        "scenarios": scenarios.count(),
        "quiz_attempts": total_attempts,
        "avg_score": avg_score,
        "completion_rate": completion_rate,
        "module_completion_rate": module_completion_rate,
        "feedback_count": Feedback.objects.count(),
        "scenario_attempts": ScenarioAttempt.objects.count(),
        "recent_users": users.order_by("-date_joined")[:8],
    }


def _count_published_quizzes():
    from quizzes.models import Quiz

    return Quiz.objects.filter(published=True).count()


def module_popularity():
    return list(
        ModuleProgress.objects.values("module__title")
        .annotate(count=Count("id"))
        .order_by("-count")[:8]
    )


def quiz_performance():
    from django.db.models import Q

    return list(
        QuizAttempt.objects.filter(completed_at__isnull=False)
        .values("quiz__title")
        .annotate(
            attempts=Count("id"),
            avg=Avg("percentage"),
            passed=Count("id", filter=Q(passed=True)),
        )
        .order_by("-attempts")[:8]
    )


def most_difficult_questions():
    return list(
        UserAnswer.objects.filter(is_correct=False)
        .values("question__question_text")
        .annotate(count=Count("id"))
        .order_by("-count")[:8]
    )


def scenario_performance():
    return list(
        ScenarioAttempt.objects.values("scenario__title")
        .annotate(
            attempts=Count("id"),
            avg_score=Avg("score"),
        )
        .order_by("-attempts")[:8]
    )


def indicator_performance():
    """Most commonly missed indicator types, from scenario attempts data."""
    from simulations.models import ScenarioIndicator

    return list(
        ScenarioIndicator.objects.filter(is_distractor=False)
        .values("indicator_type")
        .annotate(total=Count("id"))
        .order_by("-total")
    )


def training_completion_trend():
    """Modules completed per week (last 8 weeks) for the trend chart."""
    from datetime import timedelta

    from django.utils import timezone

    from progress.models import ModuleProgress

    now = timezone.now()
    weeks = []
    for i in range(7, -1, -1):
        start = now - timedelta(days=i * 7 + 7)
        end = now - timedelta(days=i * 7)
        count = ModuleProgress.objects.filter(
            completed_at__isnull=False, completed_at__gte=start, completed_at__lt=end
        ).count()
        weeks.append({"label": start.strftime("%b %d"), "count": count})
    return weeks


def all_users_data(search="", filter_status=""):
    users = User.objects.all().prefetch_related("profile")
    if search:
        from django.db.models import Q

        users = users.filter(
            Q(username__icontains=search)
            | Q(email__icontains=search)
            | Q(first_name__icontains=search)
            | Q(last_name__icontains=search)
        )
    if filter_status == "active":
        users = users.filter(is_active=True)
    elif filter_status == "inactive":
        users = users.filter(is_active=False)
    elif filter_status == "staff":
        users = users.filter(is_staff=True)

    rows = []
    for user in users[:200]:
        modules_done = ModuleProgress.objects.filter(
            user=user, completed=True
        ).count()
        quiz_avg = user.quiz_attempts.filter(completed_at__isnull=False).aggregate(
            avg=Avg("percentage")
        )["avg"]
        rows.append(
            {
                "user": user,
                "modules_completed": modules_done,
                "quiz_avg": round(quiz_avg) if quiz_avg else 0,
                "scenario_attempts": user.scenario_attempts.count(),
            }
        )
    return rows


def user_progress_rows(user):
    """Module-by-module progress for a single user (admin detail view)."""
    return list(
        ModuleProgress.objects.filter(user=user)
        .select_related("module")
        .order_by("module__order")
    )
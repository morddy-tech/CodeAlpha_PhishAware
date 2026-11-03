"""Aggregation helpers for the user dashboard and the admin analytics dashboard."""

from django.contrib.auth.models import User
from django.db.models import Avg, Count, FloatField, IntegerField, OuterRef, Subquery
from django.db.models.functions import Coalesce
from django.urls import reverse

from core.models import Feedback
from progress.models import ModuleProgress
from quizzes.models import QuizAttempt, UserAnswer
from simulations.models import PhishingScenario, ScenarioAttempt
from training.models import TrainingModule


def recent_activity(user, limit=6):
    """Combined, time-sorted list of the user's recent learning events."""
    events = []
    for attempt in (
        user.quiz_attempts.filter(completed_at__isnull=False)
        .select_related("quiz")
        .order_by("-completed_at")[:limit]
    ):
        events.append(
            {
                "kind": "quiz",
                "title": f"Quiz completed: {attempt.quiz.title}",
                "detail": f"{attempt.percentage}% - {'Passed' if attempt.passed else 'Needs review'}",
                "when": attempt.completed_at,
                "url": reverse(
                    "quizzes:result", kwargs={"attempt_id": attempt.pk}
                ),
                "icon": "brain",
            }
        )
    for completion in (
        user.lesson_completions.select_related("lesson__module")
        .order_by("-completed_at")[:limit]
    ):
        events.append(
            {
                "kind": "lesson",
                "title": f"Lesson completed: {completion.lesson.title}",
                "detail": completion.lesson.module.title,
                "when": completion.completed_at,
                "url": reverse(
                    "training:lesson_detail",
                    kwargs={"slug": completion.lesson.slug},
                ),
                "icon": "book",
            }
        )
    for attempt in (
        user.scenario_attempts.select_related("scenario")
        .order_by("-completed_at")[:limit]
    ):
        events.append(
            {
                "kind": "scenario",
                "title": f"Scenario reviewed: {attempt.scenario.title}",
                "detail": f"Score {attempt.score}%",
                "when": attempt.completed_at,
                "url": reverse(
                    "simulations:scenario_detail",
                    kwargs={"pk": attempt.scenario.pk},
                ),
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


def quiz_overall_average():
    """Mean percentage across every completed quiz attempt.

    This is an attempt-weighted average, not an average of per-quiz averages,
    so a quiz with more submissions contributes proportionally.
    """
    value = QuizAttempt.objects.filter(completed_at__isnull=False).aggregate(
        avg=Avg("percentage")
    )["avg"]
    return round(value) if value is not None else 0


def indicator_performance():
    """Real-flag miss rates calculated from persisted scenario selections.

    Legacy attempts that predate selected-ID storage and contain no clue
    selections are skipped rather than being counted as complete misses.
    """
    from collections import defaultdict

    stats = defaultdict(
        lambda: {
            "total": 0,
            "missed": 0,
        }
    )
    attempts = ScenarioAttempt.objects.select_related("scenario").prefetch_related(
        "scenario__indicators"
    )
    for attempt in attempts:
        if not attempt.selected_indicator_ids and attempt.identified_indicators == 0:
            continue
        selected = set(attempt.selected_indicator_ids or [])
        for indicator in attempt.scenario.indicators.all():
            if indicator.is_distractor:
                continue
            row = stats[
                (indicator.indicator_type, indicator.get_indicator_type_display())
            ]
            row["total"] += 1
            if indicator.id not in selected:
                row["missed"] += 1

    rows = []
    for (indicator_type, label), values in stats.items():
        total = values["total"]
        missed = values["missed"]
        rows.append(
            {
                "indicator_type": indicator_type,
                "label": label,
                "total": total,
                "missed": missed,
                "miss_rate": round(missed / total * 100) if total else 0,
            }
        )
    rows.sort(key=lambda row: (-row["miss_rate"], -row["missed"], row["label"]))
    return rows


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
    module_counts = (
        ModuleProgress.objects.filter(user=OuterRef("pk"), completed=True)
        .values("user")
        .annotate(count=Count("id"))
        .values("count")
    )
    quiz_averages = (
        QuizAttempt.objects.filter(
            user=OuterRef("pk"), completed_at__isnull=False
        )
        .values("user")
        .annotate(avg=Avg("percentage"))
        .values("avg")
    )
    scenario_counts = (
        ScenarioAttempt.objects.filter(user=OuterRef("pk"))
        .values("user")
        .annotate(count=Count("id"))
        .values("count")
    )

    users = User.objects.annotate(
        modules_completed=Coalesce(
            Subquery(module_counts, output_field=IntegerField()), 0
        ),
        quiz_avg=Subquery(quiz_averages, output_field=FloatField()),
        scenario_attempt_count=Coalesce(
            Subquery(scenario_counts, output_field=IntegerField()), 0
        ),
    )
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
        rows.append(
            {
                "user": user,
                "modules_completed": user.modules_completed,
                "quiz_avg": round(user.quiz_avg) if user.quiz_avg is not None else 0,
                "scenario_attempts": user.scenario_attempt_count,
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
"""Business logic helpers for progress tracking, achievements, and notifications."""

import logging

from django.db import transaction
from django.utils import timezone as dj_timezone

from progress.models import (
    Achievement,
    LessonCompletion,
    ModuleProgress,
    Notification,
    UserAchievement,
)

logger = logging.getLogger("app")


@transaction.atomic
def record_lesson_completion(user, lesson):
    """Mark a lesson as complete and update the module progress."""
    _, created = LessonCompletion.objects.get_or_create(
        user=user,
        lesson=lesson,
    )
    update_module_progress(user, lesson.module)
    return created


@transaction.atomic
def update_module_progress(user, module):
    """Recompute progress for a module based on completed published lessons."""
    lessons = list(module.published_lessons())
    if not lessons:
        return

    completed_ids = set(
        LessonCompletion.objects.filter(user=user, lesson__module=module).values_list(
            "lesson_id", flat=True
        )
    )
    completed_count = sum(1 for lesson in lessons if lesson.id in completed_ids)
    percentage = round(completed_count / len(lessons) * 100)

    progress, _ = ModuleProgress.objects.get_or_create(user=user, module=module)

    now = dj_timezone.now()
    was_completed = progress.completed
    newly_completed = percentage >= 100 and not was_completed

    progress.progress_percentage = percentage
    progress.completed = percentage >= 100
    progress.completed_at = now if newly_completed else progress.completed_at
    progress.save()

    if newly_completed:
        create_notification(
            user,
            "Module completed",
            f"Congratulations! You completed the module “{module.title}”.",
            Notification.NotificationType.TRAINING,
        )
        evaluate_achievements(user)
    return progress


def get_or_create_module_progress(user, module):
    progress, _ = ModuleProgress.objects.get_or_create(user=user, module=module)
    return progress


def total_training_progress(user):
    """Average module progress percentage across published modules."""
    from training.models import TrainingModule

    modules = TrainingModule.objects.filter(published=True)
    if not modules.exists():
        return 0
    records = ModuleProgress.objects.filter(user=user, module__in=modules)
    totals = sum(record.progress_percentage for record in records)
    return round(totals / modules.count())


def security_awareness_score(user):
    """Composite score of training + quizzes + simulations for the dashboard."""
    training_progress = total_training_progress(user)

    attempts = list(
        user.quiz_attempts.filter(completed_at__isnull=False).values_list(
            "percentage", flat=True
        )
    )
    quiz_avg = round(sum(attempts) / len(attempts)) if attempts else 0

    scenarios_total = len(user.scenario_attempts.all())
    scenario_scores = list(user.scenario_attempts.values_list("score", flat=True))
    scenario_avg = round(sum(scenario_scores) / scenarios_total) if scenarios_total else 0

    score = round(
        (training_progress * 0.4) + (quiz_avg * 0.35) + (scenario_avg * 0.25)
    )
    return min(score, 100)


def create_notification(user, title, message, notification_type=Notification.NotificationType.SYSTEM):
    if not getattr(user.profile, "notification_preferences", True):
        return None
    return Notification.objects.create(
        user=user,
        title=title,
        message=message,
        notification_type=notification_type,
    )


def user_stats(user):
    """Dictionary of aggregate stats used by dashboards and achievement checks."""
    from simulations.models import ScenarioAttempt

    quiz_attempts = list(
        user.quiz_attempts.filter(completed_at__isnull=False).select_related("quiz")
    )
    passed_quizzes = set(a.quiz_id for a in quiz_attempts if a.passed)
    modules_completed = ModuleProgress.objects.filter(user=user, completed=True).count()
    scenarios_completed = ScenarioAttempt.objects.filter(user=user, completed=True).count()

    return {
        "quiz_attempts": quiz_attempts,
        "passed_quizzes": passed_quizzes,
        "modules_completed": modules_completed,
        "scenarios_completed": scenarios_completed,
        "achievements_count": user.achievements.count(),
    }


def evaluate_achievements(user):
    """Award any achievements the user has newly earned."""
    stats = user_stats(user)

    criteria = {
        "first-training": lambda: stats["modules_completed"] >= 1,
        "training-complete": lambda: ModuleProgress.objects.filter(
            user=user, completed=True
        ).count()
        >= 4,
        "first-quiz": lambda: len(stats["quiz_attempts"]) >= 1,
        "quiz-master": lambda: len(stats["passed_quizzes"]) >= 1,
        "perfect-score": lambda: any(
            attempt.percentage == 100 for attempt in stats["quiz_attempts"]
        ),
        "phishing-detective": lambda: stats["scenarios_completed"] >= 1,
        "scenario-expert": lambda: stats["scenarios_completed"] >= 5,
        "security-beginner": lambda: (
            stats["modules_completed"] >= 1 and len(stats["quiz_attempts"]) >= 1
        ),
        "awareness-champion": lambda: (
            stats["modules_completed"] >= 6
            and len(stats["passed_quizzes"]) >= 4
            and stats["scenarios_completed"] >= 8
        ),
    }

    awarded = []
    for achievement in Achievement.objects.filter(active=True):
        checker = criteria.get(achievement.slug)
        if checker is None:
            continue
        try:
            earned = checker()
        except Exception:  # noqa: BLE001 - defensive: never block on achievement check
            earned = False
        if earned:
            _, created = UserAchievement.objects.get_or_create(
                user=user, achievement=achievement
            )
            if created:
                create_notification(
                    user,
                    "Achievement unlocked",
                    f"You earned the achievement “{achievement.name}”.",
                    Notification.NotificationType.ACHIEVEMENT,
                )
                awarded.append(achievement)
    return awarded


def list_notifications(user, limit=20):
    return user.notifications.select_related().order_by("-created_at")[:limit]


def unread_notification_count(user):
    return user.notifications.filter(read=False).count()
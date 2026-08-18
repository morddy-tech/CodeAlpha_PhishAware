from django.conf import settings
from django.db import models


class LessonCompletion(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="lesson_completions",
    )
    lesson = models.ForeignKey(
        "training.TrainingLesson",
        on_delete=models.CASCADE,
        related_name="completions",
    )
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "lesson"],
                name="unique_user_lesson_completion",
            )
        ]
        indexes = [
            models.Index(fields=["user", "lesson"]),
        ]

    def __str__(self):
        return f"{self.user.username} completed {self.lesson.title}"


class ModuleProgress(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="module_progress",
    )
    module = models.ForeignKey(
        "training.TrainingModule",
        on_delete=models.CASCADE,
        related_name="progress_records",
    )
    progress_percentage = models.PositiveIntegerField(default=0)
    completed = models.BooleanField(default=False)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    last_accessed = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "module"],
                name="unique_user_module_progress",
            )
        ]
        indexes = [
            models.Index(fields=["user", "module"]),
        ]

    def __str__(self):
        return f"{self.user.username} — {self.module.title} ({self.progress_percentage}%)"


class Achievement(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(
        max_length=40,
        default="award",
        help_text="Icon key used by the frontend (e.g. shield, target).",
    )
    requirement = models.TextField(
        blank=True,
        help_text="Human-readable description of how the achievement is earned.",
    )
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["id"]
        indexes = [models.Index(fields=["slug"])]

    def __str__(self):
        return self.name


class UserAchievement(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="achievements",
    )
    achievement = models.ForeignKey(
        Achievement,
        on_delete=models.CASCADE,
        related_name="awarded_to",
    )
    awarded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "achievement"],
                name="unique_user_achievement",
            )
        ]
        indexes = [models.Index(fields=["user", "achievement"])]

    def __str__(self):
        return f"{self.user.username} earned {self.achievement.name}"


class Notification(models.Model):
    class NotificationType(models.TextChoices):
        ACHIEVEMENT = "achievement", "Achievement"
        QUIZ = "quiz", "Quiz"
        TRAINING = "training", "Training"
        REMINDER = "reminder", "Reminder"
        SYSTEM = "system", "System"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    title = models.CharField(max_length=160)
    message = models.CharField(max_length=500)
    notification_type = models.CharField(
        max_length=20,
        choices=NotificationType.choices,
        default=NotificationType.SYSTEM,
    )
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "read"]),
            models.Index(fields=["-created_at"]),
        ]

    def __str__(self):
        return f"{self.user.username}: {self.title}"

    def mark_read(self):
        if not self.read:
            self.read = True
            self.save(update_fields=["read"])
from django.conf import settings
from django.db import models


class Feedback(models.Model):
    class Category(models.TextChoices):
        CONTENT = "content", "Training Content"
        QUIZ = "quiz", "Quizzes"
        SIMULATION = "simulation", "Simulations"
        PLATFORM = "platform", "Platform"
        OTHER = "other", "Other"

    class Rating(models.IntegerChoices):
        ONE = 1, "1 - Poor"
        TWO = 2, "2 - Fair"
        THREE = 3, "3 - Good"
        FOUR = 4, "4 - Very Good"
        FIVE = 5, "5 - Excellent"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="feedback",
    )
    rating = models.PositiveSmallIntegerField(choices=Rating.choices)
    message = models.TextField(blank=True, max_length=2000)
    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        default=Category.OTHER,
    )
    resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["resolved", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.user.username} rated {self.rating}/5 ({self.category})"
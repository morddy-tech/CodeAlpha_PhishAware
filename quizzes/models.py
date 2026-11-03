from django.conf import settings
from django.db import models
from django.urls import reverse


class Quiz(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    module = models.ForeignKey(
        "training.TrainingModule",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="quizzes",
    )
    passing_score = models.PositiveIntegerField(
        default=70,
        help_text="Minimum percentage required to pass.",
    )
    time_limit = models.PositiveIntegerField(
        default=0,
        help_text="Time limit in seconds. 0 means no time limit.",
    )
    published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["id"]
        indexes = [models.Index(fields=["published"])]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("quizzes:quiz_detail", kwargs={"pk": self.pk})

    def published_questions(self):
        return self.questions.all().order_by("order", "id")

    def total_points(self):
        return sum(q.points for q in self.questions.all())


class Question(models.Model):
    class QuestionType(models.TextChoices):
        MULTIPLE_CHOICE = "mc", "Multiple Choice"
        TRUE_FALSE = "tf", "True / False"

    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name="questions",
    )
    question_text = models.CharField(max_length=500)
    question_type = models.CharField(
        max_length=2,
        choices=QuestionType.choices,
        default=QuestionType.MULTIPLE_CHOICE,
    )
    explanation = models.TextField(
        blank=True,
        help_text="Educational explanation shown after answering.",
    )
    points = models.PositiveIntegerField(default=1)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]
        indexes = [models.Index(fields=["quiz", "order"])]

    def __str__(self):
        return self.question_text

    def options(self):
        return self.answers.all().order_by("order", "id")


class AnswerOption(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="answers",
    )
    option_text = models.CharField(max_length=300)
    is_correct = models.BooleanField(default=False)
    explanation = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]
        indexes = [models.Index(fields=["question"])]

    def __str__(self):
        return self.option_text


class QuizAttempt(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="quiz_attempts",
    )
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name="attempts",
    )
    score = models.PositiveIntegerField(default=0)
    percentage = models.PositiveIntegerField(default=0)
    passed = models.BooleanField(default=False)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-started_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "quiz"],
                condition=models.Q(completed_at__isnull=True),
                name="unique_open_quiz_attempt",
            )
        ]
        indexes = [
            models.Index(fields=["user", "quiz"]),
            models.Index(fields=["-started_at"]),
        ]

    def __str__(self):
        return f"{self.user.username} — {self.quiz.title} ({self.percentage}%)"

    def answers(self):
        return self.user_answers.all()


class UserAnswer(models.Model):
    attempt = models.ForeignKey(
        QuizAttempt,
        on_delete=models.CASCADE,
        related_name="user_answers",
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="user_answers",
    )
    selected_option = models.ForeignKey(
        AnswerOption,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="user_answers",
    )
    is_correct = models.BooleanField(default=False)
    points_awarded = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["attempt", "question"],
                name="unique_attempt_question",
            )
        ]
        indexes = [models.Index(fields=["attempt"])]

    def __str__(self):
        return f"Answer to Q{self.question_id} in attempt {self.attempt_id}"
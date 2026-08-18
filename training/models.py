from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class TrainingModule(models.Model):
    class Difficulty(models.TextChoices):
        BEGINNER = "beginner", "Beginner"
        INTERMEDIATE = "intermediate", "Intermediate"
        ADVANCED = "advanced", "Advanced"

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField(blank=True)
    content = models.TextField(blank=True)
    category = models.CharField(max_length=120, blank=True)
    difficulty = models.CharField(
        max_length=20,
        choices=Difficulty.choices,
        default=Difficulty.BEGINNER,
    )
    estimated_minutes = models.PositiveIntegerField(default=10)
    thumbnail = models.ImageField(upload_to="modules/", blank=True, null=True)
    published = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "id"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["published", "order"]),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:220]
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("training:module_detail", kwargs={"slug": self.slug})

    def published_lessons(self):
        return self.lessons.filter(published=True).order_by("order", "id")


class TrainingLesson(models.Model):
    module = models.ForeignKey(
        TrainingModule,
        on_delete=models.CASCADE,
        related_name="lessons",
    )
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, blank=True)
    content = models.TextField()
    order = models.PositiveIntegerField(default=0)
    estimated_minutes = models.PositiveIntegerField(default=5)
    published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["module", "slug"],
                name="unique_lesson_slug_per_module",
            )
        ]
        indexes = [
            models.Index(fields=["module", "order"]),
        ]

    def __str__(self):
        return f"{self.module.title} — {self.title}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:220]
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("training:lesson_detail", kwargs={"slug": self.slug})

    def prev_next(self):
        lessons = list(self.module.published_lessons())
        try:
            index = next(i for i, lesson in enumerate(lessons) if lesson.id == self.id)
        except StopIteration:
            return None, None
        previous = lessons[index - 1] if index > 0 else None
        next_lesson = lessons[index + 1] if index < len(lessons) - 1 else None
        return previous, next_lesson
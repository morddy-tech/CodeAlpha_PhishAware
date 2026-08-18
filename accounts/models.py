from django.conf import settings
from django.db import models


def avatar_upload_path(instance, filename):
    extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else "png"
    return f"avatars/user_{instance.user_id}.{extension}"


class UserProfile(models.Model):
    class ThemeChoices(models.TextChoices):
        LIGHT = "light", "Light"
        DARK = "dark", "Dark"
        SYSTEM = "system", "System"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    avatar = models.ImageField(
        upload_to=avatar_upload_path,
        blank=True,
        null=True,
        help_text="Optional profile picture. Max 2 MB, PNG or JPEG only.",
    )
    organization = models.CharField(max_length=120, blank=True)
    job_title = models.CharField(max_length=120, blank=True)
    timezone = models.CharField(max_length=64, default="UTC", blank=True)
    preferred_theme = models.CharField(
        max_length=10,
        choices=ThemeChoices.choices,
        default=ThemeChoices.SYSTEM,
    )
    notification_preferences = models.BooleanField(
        default=True,
        help_text="Receive in-app notifications about training reminders.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

    def __str__(self):
        return f"Profile of {self.user.username}"

    def display_name(self):
        return self.user.get_full_name() or self.user.username
from django.conf import settings
from django.db import models
from django.urls import reverse


class PhishingScenario(models.Model):
    class ScenarioType(models.TextChoices):
        EMAIL = "email", "Phishing Email"
        WEBSITE = "website", "Fake Website"
        SMS = "sms", "Smishing (SMS)"
        PHONE = "phone", "Vishing (Phone)"
        SOCIAL_ENGINEERING = "social", "Social Engineering"

    class Difficulty(models.TextChoices):
        BEGINNER = "beginner", "Beginner"
        INTERMEDIATE = "intermediate", "Intermediate"
        ADVANCED = "advanced", "Advanced"

    title = models.CharField(max_length=200)
    scenario_type = models.CharField(
        max_length=20,
        choices=ScenarioType.choices,
        default=ScenarioType.EMAIL,
    )
    description = models.TextField(blank=True)
    difficulty = models.CharField(
        max_length=20,
        choices=Difficulty.choices,
        default=Difficulty.BEGINNER,
    )
    explanation = models.TextField(
        help_text="Educational explanation and recommended action shown after interaction."
    )
    published = models.BooleanField(default=True)

    # --- Simulated display content (all fields are fictional training material) ---
    simulated_content = models.TextField(
        blank=True,
        help_text=(
            "Educational simulated content. Must be clearly fictional and must "
            "never request real credentials, payments, or personal data."
        ),
    )
    sender = models.CharField(
        max_length=200, blank=True,
        help_text="Simulated sender name (email 'from' name, caller name, or sender ID).",
    )
    source = models.CharField(
        max_length=200, blank=True,
        help_text="Simulated source: email domain, website URL, or phone number.",
    )
    recipient = models.CharField(
        max_length=200, blank=True,
        help_text="Simulated recipient shown on the message.",
    )
    subject = models.CharField(
        max_length=200, blank=True,
        help_text="Simulated email subject or message title.",
    )
    body = models.TextField(
        blank=True,
        help_text="Simulated message body / page content.",
    )
    links = models.JSONField(
        default=list, blank=True,
        help_text='List of simulated links: [{"label": "...", "url": "..."}]',
    )
    attachment_name = models.CharField(
        max_length=200, blank=True,
        help_text="Name of the simulated attachment indicator.",
    )
    site_name = models.CharField(
        max_length=200, blank=True,
        help_text="Branding shown on simulated websites.",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["scenario_type", "id"]
        indexes = [
            models.Index(fields=["scenario_type", "published"]),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("simulations:scenario_detail", kwargs={"pk": self.pk})

    def indicators(self):
        return self.indicators.all().order_by("order", "id")

    def real_flags(self):
        return self.indicators.filter(is_distractor=False).order_by("order", "id")

    def clue_options(self):
        """All selectable clues: genuine red flags plus distractor options."""
        return self.indicators.all().order_by("order", "id")


class ScenarioIndicator(models.Model):
    class IndicatorType(models.TextChoices):
        SUSPICIOUS_DOMAIN = "domain", "Suspicious Domain"
        URGENCY = "urgency", "Urgency"
        REQUEST_FOR_CREDENTIALS = "credentials", "Request for Credentials"
        ATTACHMENT = "attachment", "Suspicious Attachment"
        PAYMENT_REQUEST = "payment", "Unusual Payment Request"
        SPOOFED_IDENTITY = "spoof", "Spoofed Identity"
        UNEXPECTED_LINK = "link", "Unexpected Link"
        SOCIAL_ENGINEERING = "social", "Social Engineering"
        OTHER = "other", "Other"

    class Severity(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"

    scenario = models.ForeignKey(
        PhishingScenario,
        on_delete=models.CASCADE,
        related_name="indicators",
    )
    title = models.CharField(max_length=160)
    description = models.TextField(
        help_text="What the learner should look for and why it is suspicious."
    )
    indicator_type = models.CharField(
        max_length=20,
        choices=IndicatorType.choices,
        default=IndicatorType.OTHER,
    )
    location = models.CharField(
        max_length=80,
        blank=True,
        help_text="Where in the simulated content this clue appears, e.g. sender, subject.",
    )
    severity = models.CharField(
        max_length=10,
        choices=Severity.choices,
        default=Severity.MEDIUM,
    )
    is_distractor = models.BooleanField(
        default=False,
        help_text="True if this is a benign-looking distractor clue presented alongside the real red flags.",
    )
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]
        indexes = [models.Index(fields=["scenario", "indicator_type"])]

    def __str__(self):
        return f"{self.scenario.title}: {self.title}"


class ScenarioResponseOption(models.Model):
    """'What should you do?' choices shown for a scenario."""

    scenario = models.ForeignKey(
        PhishingScenario,
        on_delete=models.CASCADE,
        related_name="response_options",
    )
    text = models.CharField(max_length=300)
    is_correct = models.BooleanField(default=False)
    explanation = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]
        indexes = [models.Index(fields=["scenario"])]

    def __str__(self):
        return f"{self.scenario.title}: {self.text}"


class ScenarioAttempt(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="scenario_attempts",
    )
    scenario = models.ForeignKey(
        PhishingScenario,
        on_delete=models.CASCADE,
        related_name="attempts",
    )
    score = models.PositiveIntegerField(default=0)
    identified_indicators = models.PositiveIntegerField(default=0)
    selected_indicator_ids = models.JSONField(
        default=list,
        blank=True,
        help_text="IDs of the clue options selected by the learner for feedback.",
    )
    selected_response = models.ForeignKey(
        ScenarioResponseOption,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="attempts",
    )
    completed = models.BooleanField(default=True)
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-completed_at"]
        indexes = [
            models.Index(fields=["user", "scenario"]),
            models.Index(fields=["-completed_at"]),
        ]

    def __str__(self):
        return f"{self.user.username} — {self.scenario.title} ({self.score}pts)"
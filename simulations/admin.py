from django.contrib import admin

from simulations.models import (
    PhishingScenario,
    ScenarioAttempt,
    ScenarioIndicator,
    ScenarioResponseOption,
)


class ScenarioIndicatorInline(admin.TabularInline):
    model = ScenarioIndicator
    extra = 2
    fields = (
        "title",
        "indicator_type",
        "severity",
        "is_distractor",
        "location",
        "order",
    )


class ScenarioResponseOptionInline(admin.TabularInline):
    model = ScenarioResponseOption
    extra = 1
    fields = ("text", "is_correct", "explanation", "order")


@admin.register(PhishingScenario)
class PhishingScenarioAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "scenario_type",
        "difficulty",
        "published",
        "updated_at",
    )
    list_filter = ("scenario_type", "difficulty", "published")
    search_fields = ("title", "description", "body")
    inlines = [ScenarioIndicatorInline, ScenarioResponseOptionInline]


@admin.register(ScenarioIndicator)
class ScenarioIndicatorAdmin(admin.ModelAdmin):
    list_display = ("title", "scenario", "indicator_type", "severity", "is_distractor")
    list_filter = ("indicator_type", "severity", "is_distractor")
    search_fields = ("title", "description")


@admin.register(ScenarioAttempt)
class ScenarioAttemptAdmin(admin.ModelAdmin):
    list_display = ("user", "scenario", "score", "identified_indicators", "completed_at")
    list_filter = ("completed", "completed_at")
    search_fields = ("user__username", "scenario__title")
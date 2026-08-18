from django.contrib import admin

from progress.models import (
    Achievement,
    LessonCompletion,
    ModuleProgress,
    Notification,
    UserAchievement,
)


@admin.register(ModuleProgress)
class ModuleProgressAdmin(admin.ModelAdmin):
    list_display = ("user", "module", "progress_percentage", "completed", "last_accessed")
    list_filter = ("completed",)
    search_fields = ("user__username", "module__title")


@admin.register(LessonCompletion)
class LessonCompletionAdmin(admin.ModelAdmin):
    list_display = ("user", "lesson", "completed_at")
    search_fields = ("user__username", "lesson__title")


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "icon", "active")
    list_filter = ("active",)
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
    list_display = ("user", "achievement", "awarded_at")
    list_filter = ("awarded_at",)
    search_fields = ("user__username", "achievement__name")


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "title", "notification_type", "read", "created_at")
    list_filter = ("read", "notification_type")
    search_fields = ("user__username", "title")
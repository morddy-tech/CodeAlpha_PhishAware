from django.contrib import admin

from accounts.models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "organization", "job_title", "preferred_theme", "created_at")
    list_filter = ("preferred_theme", "created_at")
    search_fields = ("user__username", "user__email", "organization", "job_title")
    readonly_fields = ("created_at", "updated_at")
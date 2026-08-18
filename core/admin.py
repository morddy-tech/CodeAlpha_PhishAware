from django.contrib import admin

from core.models import Feedback


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ("user", "rating", "category", "resolved", "created_at")
    list_filter = ("resolved", "rating", "category")
    search_fields = ("user__username", "message")
    readonly_fields = ("created_at",)
from django.contrib import admin
from django.contrib.admin.exceptions import NotRegistered
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from accounts.forms import (
    UniqueEmailUserChangeForm,
    UniqueEmailUserCreationForm,
)
from accounts.models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "organization", "job_title", "preferred_theme", "created_at")
    list_filter = ("preferred_theme", "created_at")
    search_fields = ("user__username", "user__email", "organization", "job_title")
    readonly_fields = ("created_at", "updated_at")


try:
    admin.site.unregister(User)
except NotRegistered:
    pass


@admin.register(User)
class PhishAwareUserAdmin(UserAdmin):
    form = UniqueEmailUserChangeForm
    add_form = UniqueEmailUserCreationForm

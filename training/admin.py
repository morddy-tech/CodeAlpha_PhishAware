from django.contrib import admin

from training.models import TrainingLesson, TrainingModule


class TrainingLessonInline(admin.TabularInline):
    model = TrainingLesson
    extra = 1
    fields = ("title", "slug", "order", "estimated_minutes", "published")


@admin.register(TrainingModule)
class TrainingModuleAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "difficulty", "estimated_minutes", "published", "featured", "order")
    list_filter = ("published", "featured", "difficulty", "category")
    search_fields = ("title", "description", "category")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [TrainingLessonInline]


@admin.register(TrainingLesson)
class TrainingLessonAdmin(admin.ModelAdmin):
    list_display = ("title", "module", "order", "estimated_minutes", "published")
    list_filter = ("published", "module")
    search_fields = ("title", "module__title")
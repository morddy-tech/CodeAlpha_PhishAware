from django.contrib import admin

from quizzes.models import AnswerOption, Question, Quiz, QuizAttempt, UserAnswer


class AnswerOptionInline(admin.TabularInline):
    model = AnswerOption
    extra = 3
    fields = ("option_text", "is_correct", "explanation", "order")


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    fields = ("question_text", "question_type", "points", "order")


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ("title", "module", "passing_score", "time_limit", "published")
    list_filter = ("published", "module")
    search_fields = ("title", "description")
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("question_text", "quiz", "question_type", "points", "order")
    list_filter = ("question_type", "quiz")
    search_fields = ("question_text",)
    inlines = [AnswerOptionInline]


@admin.register(AnswerOption)
class AnswerOptionAdmin(admin.ModelAdmin):
    list_display = ("option_text", "question", "is_correct", "order")
    list_filter = ("is_correct",)
    search_fields = ("option_text",)


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ("user", "quiz", "score", "percentage", "passed", "completed_at")
    list_filter = ("passed", "completed_at")
    search_fields = ("user__username", "quiz__title")


@admin.register(UserAnswer)
class UserAnswerAdmin(admin.ModelAdmin):
    list_display = ("attempt", "question", "selected_option", "is_correct", "points_awarded")
    list_filter = ("is_correct",)
    search_fields = ("attempt__user__username",)
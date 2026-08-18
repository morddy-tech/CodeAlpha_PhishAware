from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from progress.models import LessonCompletion, ModuleProgress
from progress.services import get_or_create_module_progress, record_lesson_completion
from simulations.models import PhishingScenario
from training.models import TrainingLesson, TrainingModule


def training_index(request):
    search = request.GET.get("q", "").strip()
    difficulty = request.GET.get("difficulty", "").strip()
    category = request.GET.get("category", "").strip()

    modules = TrainingModule.objects.filter(published=True).prefetch_related(
        "lessons", "progress_records"
    )
    if search:
        modules = modules.filter(
            Q(title__icontains=search)
            | Q(description__icontains=search)
            | Q(category__icontains=search)
        )
    if difficulty:
        modules = modules.filter(difficulty=difficulty)
    if category:
        modules = modules.filter(category__icontains=category)

    categories = (
        TrainingModule.objects.filter(published=True)
        .values_list("category", flat=True)
        .distinct()
    )

    user_progress = {}
    if request.user.is_authenticated:
        user_progress = {
            p.module_id: p
            for p in ModuleProgress.objects.filter(user=request.user)
        }

    return render(
        request,
        "training/index.html",
        {
            "modules": modules,
            "categories": [c for c in categories if c],
            "user_progress": user_progress,
            "search": search,
            "difficulty": difficulty,
            "total_modules": modules.count(),
            "completed_modules": sum(1 for p in user_progress.values() if p.completed),
        },
    )


def module_detail(request, slug):
    module = get_object_or_404(
        TrainingModule.objects.prefetch_related("lessons"), slug=slug, published=True
    )
    progress = None
    if request.user.is_authenticated:
        progress = get_or_create_module_progress(request.user, module)

    lessons = list(module.published_lessons())
    completed_ids = set()
    if request.user.is_authenticated:
        completed_ids = set(
            LessonCompletion.objects.filter(user=request.user, lesson__module=module)
            .values_list("lesson_id", flat=True)
        )

    related_scenarios = PhishingScenario.objects.filter(published=True)[:3]
    related_quiz = module.quizzes.filter(published=True).first()

    return render(
        request,
        "training/module_detail.html",
        {
            "module": module,
            "lessons": lessons,
            "progress": progress,
            "completed_ids": completed_ids,
            "related_scenarios": related_scenarios,
            "related_quiz": related_quiz,
        },
    )


@login_required
def lesson_detail(request, slug):
    lesson = get_object_or_404(TrainingLesson, slug=slug, published=True)
    previous, next_lesson = lesson.prev_next()
    completed = LessonCompletion.objects.filter(
        user=request.user, lesson=lesson
    ).exists()

    if request.method == "POST" and request.POST.get("action") == "complete":
        # CSRF is enforced by Django's middleware for all POST requests.
        record_lesson_completion(request.user, lesson)
        messages.success(request, f"Lesson “{lesson.title}” marked as complete.")
        if next_lesson:
            return redirect("training:lesson_detail", slug=next_lesson.slug)
        return redirect("training:module_detail", slug=lesson.module.slug)

    progress = get_or_create_module_progress(request.user, lesson.module)
    related_quiz = lesson.module.quizzes.filter(published=True).first()

    return render(
        request,
        "training/lesson_detail.html",
        {
            "lesson": lesson,
            "module": lesson.module,
            "previous": previous,
            "next_lesson": next_lesson,
            "completed": completed,
            "progress": progress,
            "related_quiz": related_quiz,
        },
    )
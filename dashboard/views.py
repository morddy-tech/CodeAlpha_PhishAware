from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, render

from core.models import Feedback
from dashboard.services import (
    admin_overview,
    all_users_data,
    indicator_performance,
    module_popularity,
    most_difficult_questions,
    quiz_overall_average,
    quiz_performance,
    recent_activity,
    recommended_training,
    scenario_performance,
    training_completion_trend,
    user_progress_rows,
)
from progress.models import Achievement
from progress.services import security_awareness_score, total_training_progress, user_stats
from quizzes.models import Quiz
from simulations.models import PhishingScenario
from training.models import TrainingLesson, TrainingModule


@login_required
def home(request):
    stats = user_stats(request.user)
    total_modules = TrainingModule.objects.filter(published=True).count()
    return render(
        request,
        "dashboard/home.html",
        {
            "awareness_score": security_awareness_score(request.user),
            "total_progress": total_training_progress(request.user),
            "modules_completed": stats["modules_completed"],
            "total_modules": total_modules,
            "modules_passed": len(stats["passed_quizzes"]),
            "total_quizzes": Quiz.objects.filter(published=True).count(),
            "scenarios_completed": stats["scenarios_completed"],
            "total_scenarios": PhishingScenario.objects.filter(published=True).count(),
            "achievements_count": stats["achievements_count"],
            "recent_activity": recent_activity(request.user),
            "recommended": recommended_training(request.user),
        },
    )


def staff_required(user):
    return user.is_authenticated and user.is_staff


@login_required
@user_passes_test(staff_required, login_url="core:forbidden")
def admin_dashboard(request):
    overview = admin_overview()
    return render(
        request,
        "dashboard/admin/overview.html",
        {"overview": overview, "active_tab": "overview"},
    )


@login_required
@user_passes_test(staff_required, login_url="core:forbidden")
def admin_users(request):
    search = request.GET.get("q", "").strip()
    status = request.GET.get("status", "").strip()
    rows = all_users_data(search=search, filter_status=status)
    return render(
        request,
        "dashboard/admin/users.html",
        {"rows": rows, "search": search, "status": status, "active_tab": "users"},
    )


@login_required
@user_passes_test(staff_required, login_url="core:forbidden")
def admin_user_detail(request, user_id):
    from django.contrib.auth.models import User

    user = get_object_or_404(User, pk=user_id)
    rows = user_progress_rows(user)
    attempts = (
        user.quiz_attempts.filter(completed_at__isnull=False)
        .select_related("quiz")
        .order_by("-started_at")[:10]
    )
    scenarios = user.scenario_attempts.select_related("scenario").order_by(
        "-completed_at"
    )[:10]
    return render(
        request,
        "dashboard/admin/user_detail.html",
        {
            "target_user": user,
            "rows": rows,
            "attempts": attempts,
            "scenarios": scenarios,
            "active_tab": "users",
        },
    )


@login_required
@user_passes_test(staff_required, login_url="core:forbidden")
def admin_content(request):
    return render(
        request,
        "dashboard/admin/content.html",
        {
            "modules": TrainingModule.objects.all().count(),
            "lessons": TrainingLesson.objects.all().count(),
            "scenarios": PhishingScenario.objects.all().count(),
            "quizzes": Quiz.objects.all().count(),
            "achievements": Achievement.objects.all().count(),
            "active_tab": "content",
        },
    )


@login_required
@user_passes_test(staff_required, login_url="core:forbidden")
def admin_analytics(request):
    completion_trend = training_completion_trend()
    return render(
        request,
        "dashboard/admin/analytics.html",
        {
            "module_popularity": module_popularity(),
            "quiz_performance": quiz_performance(),
            "quiz_overall_avg": quiz_overall_average(),
            "difficult_questions": most_difficult_questions(),
            "scenario_performance": scenario_performance(),
            "indicator_performance": indicator_performance(),
            "completion_trend": completion_trend,
            "completion_trend_max": max(
                (week["count"] for week in completion_trend), default=0
            )
            or 1,
            "active_tab": "analytics",
        },
    )


@login_required
@user_passes_test(staff_required, login_url="core:forbidden")
def admin_feedback(request):
    filter_by = request.GET.get("filter", "")
    items = Feedback.objects.select_related("user").order_by("-created_at")
    if filter_by == "unresolved":
        items = items.filter(resolved=False)
    elif filter_by == "resolved":
        items = items.filter(resolved=True)
    return render(
        request,
        "dashboard/admin/feedback.html",
        {"items": items, "filter_by": filter_by, "active_tab": "feedback"},
    )


@login_required
@user_passes_test(staff_required, login_url="core:forbidden")
def admin_feedback_resolve(request, pk):
    item = get_object_or_404(Feedback, pk=pk)
    if request.method == "POST":
        item.resolved = True
        item.save(update_fields=["resolved"])
        messages.success(request, "Feedback marked as resolved.")
    return redirect("dashboard:admin_feedback")
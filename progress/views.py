from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from progress.models import Achievement, ModuleProgress, Notification, UserAchievement
from progress.services import (
    security_awareness_score,
    total_training_progress,
    unread_notification_count,
)


@login_required
def progress_overview(request):
    modules = (
        ModuleProgress.objects.filter(user=request.user)
        .select_related("module")
        .order_by("-last_accessed")
    )
    completed = modules.filter(completed=True)
    return render(
        request,
        "progress/overview.html",
        {
            "progress_records": modules,
            "completed_count": completed.count(),
            "total_progress": total_training_progress(request.user),
            "awareness_score": security_awareness_score(request.user),
        },
    )


@login_required
def achievements_view(request):
    achievements = Achievement.objects.filter(active=True)
    earned_ids = set(
        request.user.achievements.values_list("achievement_id", flat=True)
    )
    awarded = UserAchievement.objects.filter(user=request.user).select_related(
        "achievement"
    )
    return render(
        request,
        "progress/achievements.html",
        {
            "achievements": achievements,
            "earned_ids": earned_ids,
            "awarded": awarded,
        },
    )


@login_required
def notifications_view(request):
    notifications = request.user.notifications.order_by("-created_at")
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "mark_all":
            notifications.filter(read=False).update(read=True)
        elif action == "mark_one":
            notification_id = request.POST.get("notification_id", "")
            if notification_id.isdigit():
                notification = get_object_or_404(
                    Notification, pk=notification_id, user=request.user
                )
                notification.mark_read()
        return redirect("progress:notifications")
    return render(
        request,
        "progress/notifications.html",
        {
            "notifications": notifications,
            "unread_count": unread_notification_count(request.user),
        },
    )
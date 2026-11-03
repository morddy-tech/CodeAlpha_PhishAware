from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from core.decorators import rate_limit
from core.forms import FeedbackForm
from core.models import Feedback
from simulations.models import PhishingScenario
from training.models import TrainingModule


def landing_page(request):
    modules = TrainingModule.objects.filter(published=True, featured=True)[:6]
    if not modules.exists():
        modules = TrainingModule.objects.filter(published=True)[:6]
    scenarios = PhishingScenario.objects.filter(published=True)[:4]
    return render(
        request,
        "core/landing.html",
        {
            "modules": modules,
            "scenarios": scenarios,
            "module_count": TrainingModule.objects.filter(published=True).count(),
            "quiz_count": _published_quiz_count(),
            "scenario_count": PhishingScenario.objects.filter(published=True).count(),
        },
    )


def _published_quiz_count():
    from quizzes.models import Quiz

    return Quiz.objects.filter(published=True).count()


def about_page(request):
    return render(request, "core/about.html")


def security_tips(request):
    return render(request, "core/security_tips.html")


def faq_page(request):
    return render(request, "core/faq.html")


def privacy_page(request):
    return render(request, "core/privacy.html")


def forbidden_page(request):
    return render(request, "core/403.html", status=403)


@login_required
@rate_limit("feedback", attempts=10, window=600, lockout=900)
def feedback_view(request):
    form = FeedbackForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        feedback = form.save(commit=False)
        feedback.user = request.user
        feedback.save()
        messages.success(request, "Thank you for your feedback!")
        return redirect("core:feedback")

    user_feedback = Feedback.objects.filter(user=request.user).order_by("-created_at")[:5]
    return render(
        request,
        "core/feedback.html",
        {"form": form, "user_feedback": user_feedback},
    )


def custom_bad_request(request, exception=None):
    return render(request, "core/400.html", status=400)


def custom_forbidden(request, exception=None):
    return render(request, "core/403.html", status=403)


def custom_not_found(request, exception=None):
    return render(request, "core/404.html", status=404)


def custom_server_error(request, exception=None):
    return render(request, "core/500.html", status=500)
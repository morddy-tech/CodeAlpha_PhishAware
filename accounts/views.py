import logging

from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordResetView,
)
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

from accounts.forms import AvatarForm, LoginForm, ProfileForm, RegisterForm
from core.decorators import rate_limit

logger = logging.getLogger("security")


class PhishAwareLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True

    @rate_limit("login", attempts=5, window=300, lockout=900)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.get_user()
        remember = form.cleaned_data.get("remember_me", False)
        auth_login(self.request, user)
        if not remember:
            self.request.session.set_expiry(0)
        logger.info("Login success: user=%s", user.username)
        messages.success(self.request, f"Welcome back, {user.get_full_name() or user.username}!")
        return redirect(self.get_success_url())

    def form_invalid(self, form):
        logger.warning(
            "Login failure: identifier=%s from %s",
            form.data.get("username", ""),
            self.request.META.get("REMOTE_ADDR", "unknown"),
        )
        return super().form_invalid(form)


class PhishAwareLogoutView(LogoutView):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            logger.info("Logout: user=%s", request.user.username)
        return super().dispatch(request, *args, **kwargs)


@rate_limit("register", attempts=10, window=600, lockout=1800)
def register_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard:home")
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        user.backend = "django.contrib.auth.backends.ModelBackend"
        auth_login(request, user)
        logger.info("New registration: user=%s", user.username)
        messages.success(
            request,
            "Your account was created successfully. Welcome to PhishAware!",
        )
        return redirect("dashboard:home")
    return render(request, "accounts/register.html", {"form": form})


@login_required
def profile_view(request):
    profile = request.user.profile
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile was updated.")
            return redirect("accounts:profile")
    else:
        form = ProfileForm(instance=profile)
    return render(
        request,
        "accounts/profile.html",
        {"form": form, "profile": profile},
    )


@login_required
def change_password_view(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Your password was changed.")
            return redirect("accounts:profile")
    else:
        form = PasswordChangeForm(request.user)
    return render(request, "accounts/change_password.html", {"form": form})


@login_required
def avatar_upload_view(request):
    if request.method == "POST":
        form = AvatarForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Your avatar was updated.")
            return redirect("accounts:profile")
        messages.error(request, "Could not update your avatar.")
    return redirect("accounts:profile")


class PhishAwarePasswordResetView(PasswordResetView):
    template_name = "accounts/password_reset.html"
    email_template_name = "accounts/password_reset_email.html"
    subject_template_name = "accounts/password_reset_subject.txt"
    success_url = reverse_lazy("accounts:password_reset_done")

    @rate_limit("password_reset", attempts=3, window=600, lockout=1800)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
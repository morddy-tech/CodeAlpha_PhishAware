from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    UserChangeForm,
    UserCreationForm,
)
from django.contrib.auth.models import User
from PIL import Image, UnidentifiedImageError

from accounts.models import UserProfile


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "password1", "password2"]

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("A user with that email address already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"].strip()
        user.last_name = self.cleaned_data["last_name"].strip()
        if commit:
            user.save()
            UserProfile.objects.get_or_create(user=user)
        return user


class UniqueEmailUserCreationForm(UserCreationForm):
    """Admin add-user form with case-insensitive email validation."""

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email")

    def clean_email(self):
        email = (self.cleaned_data.get("email") or "").strip().lower()
        if email and User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "A user with that email address already exists."
            )
        return email


class UniqueEmailUserChangeForm(UserChangeForm):
    """Admin change-user form with case-insensitive email validation."""

    class Meta(UserChangeForm.Meta):
        model = User
        fields = "__all__"

    def clean_email(self):
        email = (self.cleaned_data.get("email") or "").strip().lower()
        duplicates = User.objects.filter(email__iexact=email)
        if self.instance.pk:
            duplicates = duplicates.exclude(pk=self.instance.pk)
        if email and duplicates.exists():
            raise forms.ValidationError(
                "A user with that email address already exists."
            )
        return email


class LoginForm(AuthenticationForm):
    """Login accepting a username or an email address, plus remember-me."""

    username = forms.CharField(
        label="Username or email",
        max_length=150,
        widget=forms.TextInput(attrs={"autofocus": True}),
    )
    remember_me = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(),
        label="Remember me on this device",
    )

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request, *args, **kwargs)
        self.fields["username"].error_messages = {
            "invalid_login": "Please enter a correct username/email and password.",
            "inactive": "This account is inactive.",
        }


class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["organization", "job_title", "timezone", "preferred_theme", "notification_preferences"]
        widgets = {
            "preferred_theme": forms.RadioSelect(
                choices=UserProfile.ThemeChoices.choices,
            ),
        }

    def clean_timezone(self):
        tz = self.cleaned_data.get("timezone", "").strip()
        if tz:
            try:
                import zoneinfo

                zoneinfo.ZoneInfo(tz)
            except Exception:  # noqa: BLE001 - any invalid timezone string is rejected
                raise forms.ValidationError("Enter a valid timezone name, e.g. UTC or America/New_York.")
        return tz


class AvatarForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["avatar"]

    def clean_avatar(self):
        avatar = self.cleaned_data.get("avatar")
        if avatar:
            if avatar.size > 2 * 1024 * 1024:
                raise forms.ValidationError("Image must be 2 MB or smaller.")
            if avatar.content_type not in {"image/png", "image/jpeg"}:
                raise forms.ValidationError("Only PNG or JPEG images are allowed.")
            try:
                image = Image.open(avatar)
                image.verify()
                avatar.seek(0)
                image = Image.open(avatar)
                image_format = image.format
                width, height = image.size
            except (
                UnidentifiedImageError,
                Image.DecompressionBombError,
                OSError,
                ValueError,
            ):
                raise forms.ValidationError(
                    "Upload a valid PNG or JPEG image."
                )
            finally:
                try:
                    avatar.seek(0)
                except (OSError, ValueError):
                    pass
            if image_format not in {"PNG", "JPEG"}:
                raise forms.ValidationError("Only PNG or JPEG images are allowed.")
            if width * height > 20_000_000:
                raise forms.ValidationError("Image dimensions are too large.")
        return avatar
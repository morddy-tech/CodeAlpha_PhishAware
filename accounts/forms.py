from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

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
        return avatar
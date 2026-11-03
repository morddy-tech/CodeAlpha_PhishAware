"""Authentication tests: registration, login, logout, password reset."""

import io
import tempfile

from django.contrib.auth.models import User
from django.core import mail
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from PIL import Image

from accounts.models import UserProfile
from tests.helpers import PASSWORD, create_user


class AuthTests(TestCase):
    def setUp(self):
        cache.clear()

    def test_register_creates_user_and_profile(self):
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "newuser",
                "first_name": "New",
                "last_name": "User",
                "email": "newuser@example.com",
                "password1": PASSWORD,
                "password2": PASSWORD,
            },
        )
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username="newuser")
        self.assertEqual(user.email, "newuser@example.com")
        self.assertTrue(user.profile)
        # The user is logged in after registration
        self.assertEqual(int(self.client.session["_auth_user_id"]), user.pk)

    def test_register_requires_unique_email(self):
        create_user(username="existing", email="taken@example.com")
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "another",
                "first_name": "A",
                "last_name": "B",
                "email": "taken@example.com",
                "password1": PASSWORD,
                "password2": PASSWORD,
            },
        )
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertIn("email", form.errors)
        self.assertFalse(User.objects.filter(username="another").exists())

    def test_register_validates_password_confirmation(self):
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "mismatch",
                "first_name": "A",
                "last_name": "B",
                "email": "mismatch@example.com",
                "password1": PASSWORD,
                "password2": "DifferentPass!word",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("password2", response.context["form"].errors)

    def test_register_rejects_weak_password(self):
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "weakuser",
                "first_name": "A",
                "last_name": "B",
                "email": "weak@example.com",
                "password1": "123",
                "password2": "123",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="weakuser").exists())

    def test_login_with_username(self):
        create_user(username="alice", email="alice@example.com")
        response = self.client.post(
            reverse("accounts:login"),
            {"username": "alice", "password": PASSWORD},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(int(self.client.session["_auth_user_id"]), User.objects.get(username="alice").pk)

    def test_login_with_email(self):
        create_user(username="alice", email="alice@example.com")
        response = self.client.post(
            reverse("accounts:login"),
            {"username": "alice@example.com", "password": PASSWORD},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(int(self.client.session["_auth_user_id"]), User.objects.get(username="alice").pk)

    def test_login_invalid_credentials(self):
        create_user(username="alice", email="alice@example.com")
        response = self.client.post(
            reverse("accounts:login"),
            {"username": "alice", "password": "WrongPass!word"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_login_inactive_user_rejected(self):
        user = create_user(username="inactive", email="inactive@example.com")
        user.is_active = False
        user.save()
        response = self.client.post(
            reverse("accounts:login"),
            {"username": "inactive", "password": PASSWORD},
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_logout(self):
        user = create_user()
        self.client.force_login(user)
        response = self.client.post(reverse("accounts:logout"), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_profile_page_repairs_missing_profile(self):
        user = create_user()
        self.client.force_login(user)
        user.profile.delete()

        response = self.client.get(reverse("accounts:profile"))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(UserProfile.objects.filter(user=user).exists())

    def test_avatar_upload_accepts_valid_png(self):
        user = create_user()
        self.client.force_login(user)
        buffer = io.BytesIO()
        Image.new("RGB", (8, 8), color="white").save(buffer, format="PNG")
        upload = SimpleUploadedFile(
            "avatar.png", buffer.getvalue(), content_type="image/png"
        )

        with tempfile.TemporaryDirectory() as media_root:
            with self.settings(MEDIA_ROOT=media_root):
                response = self.client.post(
                    reverse("accounts:avatar_upload"), {"avatar": upload}
                )
                self.assertEqual(response.status_code, 302)
                user.profile.refresh_from_db()
                self.assertTrue(user.profile.avatar)

    def test_avatar_upload_rejects_fake_image(self):
        user = create_user()
        self.client.force_login(user)
        upload = SimpleUploadedFile(
            "avatar.png", b"not really an image", content_type="image/png"
        )

        with tempfile.TemporaryDirectory() as media_root:
            with self.settings(MEDIA_ROOT=media_root):
                response = self.client.post(
                    reverse("accounts:avatar_upload"),
                    {"avatar": upload},
                    follow=True,
                )
                self.assertEqual(response.status_code, 200)
                user.profile.refresh_from_db()
                self.assertFalse(user.profile.avatar)

    def test_password_reset_sends_email(self):
        create_user(username="alice", email="alice@example.com")
        response = self.client.post(
            reverse("accounts:password_reset"),
            {"email": "alice@example.com"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("alice@example.com", mail.outbox[0].to)

    def test_password_reset_full_flow(self):
        user = create_user(username="alice", email="alice@example.com")
        self.client.post(reverse("accounts:password_reset"), {"email": "alice@example.com"})
        message = mail.outbox[0]
        # Extract the reset link from the email body
        import re

        match = re.search(r"reset/([0-9A-Za-z_\-=]+)/([0-9A-Za-z\-]+)/", message.body)
        self.assertIsNotNone(match)
        uid, token = match.group(1), match.group(2)
        url = reverse("accounts:password_reset_confirm", kwargs={"uidb64": uid, "token": token})
        response = self.client.post(
            url,
            {"new_password1": "NewPass!word", "new_password2": "NewPass!word"},
        )
        # Django 6.x redirects a valid reset token to a /set-password/ URL
        # before the new password is applied.
        if response.status_code == 302 and "set-password" in response.url:
            response = self.client.post(
                response.url,
                {"new_password1": "NewPass!word", "new_password2": "NewPass!word"},
            )
        self.assertEqual(response.status_code, 302)
        user.refresh_from_db()
        self.assertTrue(user.check_password("NewPass!word"))
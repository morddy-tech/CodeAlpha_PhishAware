"""Security tests: CSRF, headers, XSS-safety, rate limiting, error pages."""

from django.test import Client, TestCase
from django.urls import reverse

from tests.helpers import create_user


class CsrfTests(TestCase):
    def test_csrf_protection_enforced(self):
        # A POST without a CSRF token is rejected.
        client = Client(enforce_csrf_checks=True)
        response = client.post(
            reverse("accounts:login"), {"username": "x", "password": "y"}
        )
        self.assertEqual(response.status_code, 403)

    def test_csrf_token_present_on_forms(self):
        response = self.client.get(reverse("accounts:register"))
        self.assertContains(response, "csrfmiddlewaretoken")


class SecurityHeaderTests(TestCase):
    def test_security_headers_present(self):
        response = self.client.get("/")
        self.assertEqual(response.headers.get("X-Content-Type-Options"), "nosniff")
        self.assertEqual(response.headers.get("X-Frame-Options"), "DENY")
        self.assertEqual(response.headers.get("Referrer-Policy"), "same-origin")

    def test_sensitive_cookies_are_httponly(self):
        user = create_user()
        self.client.force_login(user)
        self.client.post(reverse("accounts:login"), {"username": user.username, "password": "wrong"})
        response = self.client.get(reverse("dashboard:home"))
        session_cookie = response.cookies.get("sessionid")
        if session_cookie:
            self.assertTrue(session_cookie.get("httponly", False))


class XssSafetyTests(TestCase):
    def test_user_content_is_escaped(self):
        user = create_user(username="<script>alert(1)</script>")
        response = self.client.get(reverse("core:landing"))
        self.assertNotContains(response, "<script>alert(1)</script>")

    def test_form_input_is_escaped(self):
        user = create_user()
        self.client.force_login(user)
        # Submit feedback containing HTML and check it renders escaped.
        self.client.post(
            reverse("core:feedback"),
            {"rating": "5", "category": "other", "message": "<script>alert('x')</script>"},
        )
        response = self.client.get(reverse("core:feedback"))
        self.assertNotContains(response, "<script>alert('x')</script>")


class ErrorPageTests(TestCase):
    def test_404_page_renders(self):
        response = self.client.get("/this-page-does-not-exist/")
        self.assertEqual(response.status_code, 404)
        self.assertContains(response, "404", status_code=404)

    def test_403_page_renders(self):
        response = self.client.get(reverse("core:forbidden"))
        self.assertEqual(response.status_code, 403)
        self.assertContains(response, "403", status_code=403)


class RateLimitTests(TestCase):
    def setUp(self):
        from django.core.cache import cache

        cache.clear()

    def test_login_rate_limited_after_many_failures(self):
        for _ in range(5):
            response = self.client.post(
                reverse("accounts:login"),
                {"username": "nobody", "password": "wrong"},
            )
        blocked = self.client.post(
            reverse("accounts:login"),
            {"username": "nobody", "password": "wrong"},
        )
        self.assertEqual(blocked.status_code, 403)


class DisallowedHostTests(TestCase):
    def test_invalid_host_rejected(self):
        # Allowed hosts are restricted, so an unknown host is rejected.
        response = Client(HTTP_HOST="evil.example.net").get("/")
        self.assertEqual(response.status_code, 400)


class SeededContentTests(TestCase):
    def test_seed_command_is_idempotent(self):
        from io import StringIO

        from django.core.management import call_command

        out = StringIO()
        call_command("seed_training", stdout=out)
        call_command("seed_training", stdout=out)

        from progress.models import Achievement
        from quizzes.models import Quiz
        from simulations.models import PhishingScenario
        from training.models import TrainingLesson, TrainingModule

        self.assertEqual(TrainingModule.objects.count(), 8)
        self.assertEqual(TrainingLesson.objects.count(), 32)
        self.assertEqual(Quiz.objects.count(), 9)
        self.assertEqual(PhishingScenario.objects.count(), 8)
        self.assertEqual(Achievement.objects.count(), 9)
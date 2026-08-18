"""Authorization tests: admin access control and IDOR protection."""

from django.test import TestCase
from django.urls import reverse

from quizzes.models import QuizAttempt
from tests.helpers import create_quiz, create_staff, create_user


class AuthorizationTests(TestCase):
    def setUp(self):
        self.user = create_user()
        self.staff = create_staff()

    def test_anonymous_cannot_access_dashboard(self):
        response = self.client.get(reverse("dashboard:home"))
        self.assertIn(response.status_code, (302, 403))

    def test_anonymous_cannot_access_admin(self):
        response = self.client.get(reverse("dashboard:admin_dashboard"))
        self.assertIn(response.status_code, (302, 403))

    def test_regular_user_cannot_access_admin(self):
        self.client.force_login(self.user)
        for url in [
            reverse("dashboard:admin_dashboard"),
            reverse("dashboard:admin_users"),
            reverse("dashboard:admin_content"),
            reverse("dashboard:admin_analytics"),
            reverse("dashboard:admin_feedback"),
        ]:
            response = self.client.get(url)
            self.assertIn(response.status_code, (302, 403))

    def test_staff_can_access_admin(self):
        self.client.force_login(self.staff)
        for url in [
            reverse("dashboard:admin_dashboard"),
            reverse("dashboard:admin_users"),
            reverse("dashboard:admin_content"),
            reverse("dashboard:admin_analytics"),
            reverse("dashboard:admin_feedback"),
        ]:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

    def test_admin_user_detail_protected(self):
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("dashboard:admin_user_detail", kwargs={"user_id": self.staff.pk})
        )
        self.assertIn(response.status_code, (302, 403))

    def test_regular_user_cannot_view_other_users_quiz_result(self):
        quiz = create_quiz()
        other = create_user(username="other")
        attempt = QuizAttempt.objects.create(
            user=other, quiz=quiz, score=3, percentage=100, passed=True
        )
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("quizzes:result", kwargs={"attempt_id": attempt.pk})
        )
        self.assertEqual(response.status_code, 404)

    def test_user_can_view_own_quiz_result(self):
        quiz = create_quiz()
        attempt = QuizAttempt.objects.create(
            user=self.user, quiz=quiz, score=3, percentage=100, passed=True
        )
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("quizzes:result", kwargs={"attempt_id": attempt.pk})
        )
        self.assertEqual(response.status_code, 200)

    def test_lesson_requires_login(self):
        module = __import__("tests.helpers", fromlist=["create_module"]).create_module()
        lesson = module.lessons.first()
        response = self.client.get(
            reverse("training:lesson_detail", kwargs={"slug": lesson.slug})
        )
        self.assertIn(response.status_code, (302, 403))

    def test_quiz_take_requires_login(self):
        quiz = create_quiz()
        response = self.client.get(reverse("quizzes:take", kwargs={"pk": quiz.pk}))
        self.assertIn(response.status_code, (302, 403))

    def test_notifications_are_user_scoped(self):
        other = create_user(username="other")
        notification = other.notifications.create(title="Secret", message="x")
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("progress:notifications"),
            {"action": "mark_one", "notification_id": notification.pk},
        )
        self.assertIn(response.status_code, (302, 404))
        notification.refresh_from_db()
        self.assertFalse(notification.read)
"""Dashboard and analytics regression tests."""

from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from dashboard.services import (
    all_users_data,
    indicator_performance,
    quiz_overall_average,
    recent_activity,
)
from progress.models import LessonCompletion
from quizzes.models import QuizAttempt
from simulations.models import ScenarioAttempt
from tests.helpers import create_module, create_quiz, create_scenario, create_staff, create_user


class DashboardAnalyticsTests(TestCase):
    def setUp(self):
        self.staff = create_staff()

    def test_analytics_page_renders_for_staff(self):
        user = create_user()
        quiz = create_quiz(questions=1)
        QuizAttempt.objects.create(
            user=user,
            quiz=quiz,
            percentage=80,
            completed_at=timezone.now(),
        )
        self.client.force_login(self.staff)
        response = self.client.get(reverse("dashboard:admin_analytics"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("completion_trend_max", response.context)
        self.assertGreaterEqual(response.context["completion_trend_max"], 1)
        self.assertContains(response, "Overall quiz average")

    def test_overall_quiz_average_uses_all_attempts(self):
        user = create_user()
        quiz = create_quiz(questions=2)
        now = timezone.now()
        QuizAttempt.objects.create(
            user=user, quiz=quiz, percentage=50, completed_at=now
        )
        QuizAttempt.objects.create(
            user=user, quiz=quiz, percentage=100, completed_at=now
        )
        self.assertEqual(quiz_overall_average(), 75)

    def test_indicator_performance_uses_persisted_selections(self):
        user = create_user()
        scenario, parts = create_scenario()
        ScenarioAttempt.objects.create(
            user=user,
            scenario=scenario,
            identified_indicators=1,
            selected_indicator_ids=[parts["flag"].id],
        )
        ScenarioAttempt.objects.create(
            user=user,
            scenario=scenario,
            identified_indicators=1,
            selected_indicator_ids=[],
        )

        rows = indicator_performance()
        domain_row = next(row for row in rows if row["indicator_type"] == "domain")
        self.assertEqual(domain_row["total"], 2)
        self.assertEqual(domain_row["missed"], 1)
        self.assertEqual(domain_row["miss_rate"], 50)

    def test_recent_activity_is_ordered_by_completion_time(self):
        user = create_user()
        module = create_module(with_lessons=2)
        lesson = module.lessons.first()
        completion = LessonCompletion.objects.create(user=user, lesson=lesson)
        LessonCompletion.objects.filter(pk=completion.pk).update(
            completed_at=timezone.now() - timedelta(days=2)
        )
        quiz = create_quiz(questions=1)
        QuizAttempt.objects.create(
            user=user,
            quiz=quiz,
            percentage=100,
            completed_at=timezone.now(),
        )

        events = recent_activity(user)
        self.assertEqual(events[0]["kind"], "quiz")

    def test_all_users_data_uses_one_query(self):
        create_user()
        create_user("bob", "bob@example.com")
        with self.assertNumQueries(1):
            rows = all_users_data()
        self.assertEqual(len(rows), 3)

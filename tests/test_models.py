"""Model-level tests: constraints, relationships, unique fields, progress."""

from django.contrib.auth.models import User
from django.db import IntegrityError
from django.test import TestCase

from progress.models import (
    Achievement,
    LessonCompletion,
    ModuleProgress,
    UserAchievement,
)
from progress.services import record_lesson_completion, update_module_progress
from tests.helpers import PASSWORD, create_module, create_quiz, create_user


class ModelConstraintTests(TestCase):
    def test_user_profile_created_automatically(self):
        user = create_user()
        self.assertTrue(hasattr(user, "profile"))
        self.assertEqual(str(user.profile), f"Profile of {user.username}")

    def test_lesson_slug_unique_per_module(self):
        module = create_module(with_lessons=0)
        TrainingLesson = module.lessons.model
        TrainingLesson.objects.create(
            module=module, title="Duplicate", content="x", slug="duplicate"
        )
        with self.assertRaises(IntegrityError):
            TrainingLesson.objects.create(
                module=module, title="Duplicate", content="x", slug="duplicate"
            )

    def test_module_slug_unique(self):
        create_module(title="Same Title", with_lessons=0)
        from training.models import TrainingModule

        duplicate = TrainingModule(title="Same Title", published=True)
        with self.assertRaises(IntegrityError):
            duplicate.save()

    def test_duplicate_module_progress_prevented(self):
        user = create_user()
        module = create_module(with_lessons=2)
        ModuleProgress.objects.create(user=user, module=module)
        with self.assertRaises(IntegrityError):
            ModuleProgress.objects.create(user=user, module=module)

    def test_duplicate_lesson_completion_prevented(self):
        user = create_user()
        module = create_module(with_lessons=1)
        lesson = module.lessons.first()
        LessonCompletion.objects.create(user=user, lesson=lesson)
        with self.assertRaises(IntegrityError):
            LessonCompletion.objects.create(user=user, lesson=lesson)

    def test_duplicate_achievement_award_prevented(self):
        user = create_user()
        achievement = Achievement.objects.create(
            name="Test", slug="test-achievement", active=True
        )
        UserAchievement.objects.create(user=user, achievement=achievement)
        with self.assertRaises(IntegrityError):
            UserAchievement.objects.create(user=user, achievement=achievement)

    def test_quiz_attempt_relationship(self):
        user = create_user()
        quiz = create_quiz(questions=2)
        attempt = user.quiz_attempts.create(quiz=quiz, score=2, percentage=100, passed=True)
        self.assertEqual(attempt.quiz, quiz)
        self.assertEqual(user.quiz_attempts.count(), 1)
        self.assertEqual(attempt.answers().count(), 0)

    def test_scenario_relationships(self):
        from tests.helpers import create_scenario

        scenario, parts = create_scenario("Relational Scenario")
        self.assertEqual(scenario.indicators.count(), 2)
        self.assertEqual(scenario.real_flags().count(), 1)
        self.assertEqual(scenario.response_options.count(), 2)
        self.assertEqual(parts["flag"].scenario, scenario)


class ProgressCalculationTests(TestCase):
    def test_progress_updates_with_lessons(self):
        user = create_user()
        module = create_module(with_lessons=4)
        lessons = list(module.published_lessons())
        self.assertEqual(len(lessons), 4)

        record_lesson_completion(user, lessons[0])
        record_lesson_completion(user, lessons[1])

        progress = ModuleProgress.objects.get(user=user, module=module)
        self.assertEqual(progress.progress_percentage, 50)
        self.assertFalse(progress.completed)

        record_lesson_completion(user, lessons[2])
        record_lesson_completion(user, lessons[3])
        progress.refresh_from_db()
        self.assertEqual(progress.progress_percentage, 100)
        self.assertTrue(progress.completed)
        self.assertIsNotNone(progress.completed_at)

    def test_module_completion_creates_notification(self):
        user = create_user()
        module = create_module(with_lessons=1)
        lesson = module.lessons.first()
        record_lesson_completion(user, lesson)
        self.assertEqual(
            user.notifications.filter(title="Module completed").count(), 1
        )

    def test_update_module_progress_is_idempotent(self):
        user = create_user()
        module = create_module(with_lessons=2)
        for lesson in module.lessons.all():
            LessonCompletion.objects.create(user=user, lesson=lesson)
        update_module_progress(user, module)
        first_notifications = user.notifications.count()
        update_module_progress(user, module)
        self.assertEqual(user.notifications.count(), first_notifications)

    def test_user_password_is_hashed(self):
        user = create_user()
        self.assertNotEqual(user.password, PASSWORD)
        self.assertTrue(user.password.startswith("pbkdf2") or user.password.startswith("argon2"))
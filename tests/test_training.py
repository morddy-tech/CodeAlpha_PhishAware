"""Training module/lesson tests."""

from django.test import TestCase
from django.urls import reverse

from progress.models import LessonCompletion, ModuleProgress
from tests.helpers import create_module, create_user


class TrainingTests(TestCase):
    def setUp(self):
        self.user = create_user()

    def test_module_listing_shows_published_only(self):
        published = create_module(title="Visible Module")
        create_module(title="Hidden Module", published=False)
        response = self.client.get(reverse("training:index"))
        self.assertContains(response, "Visible Module")
        self.assertNotContains(response, "Hidden Module")

    def test_module_search(self):
        create_module(title="Email Phishing Basics")
        create_module(title="Social Engineering")
        response = self.client.get(reverse("training:index"), {"q": "phishing"})
        self.assertContains(response, "Email Phishing Basics")
        self.assertNotContains(response, "Social Engineering")

    def test_module_detail_contains_lessons(self):
        module = create_module(title="Detail Module", with_lessons=3)
        response = self.client.get(
            reverse("training:module_detail", kwargs={"slug": module.slug})
        )
        self.assertEqual(response.status_code, 200)
        for lesson in module.lessons.all():
            self.assertContains(response, lesson.title)

    def test_lesson_completion_tracks_progress(self):
        self.client.force_login(self.user)
        module = create_module(with_lessons=4)
        lesson = module.lessons.first()
        response = self.client.post(
            reverse("training:lesson_detail", kwargs={"slug": lesson.slug}),
            {"action": "complete"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            LessonCompletion.objects.filter(user=self.user, lesson=lesson).exists()
        )
        progress = ModuleProgress.objects.get(user=self.user, module=module)
        self.assertEqual(progress.progress_percentage, 25)

    def test_lesson_completion_is_idempotent(self):
        self.client.force_login(self.user)
        module = create_module(with_lessons=2)
        lesson = module.lessons.first()
        self.client.post(
            reverse("training:lesson_detail", kwargs={"slug": lesson.slug}),
            {"action": "complete"},
        )
        self.client.post(
            reverse("training:lesson_detail", kwargs={"slug": lesson.slug}),
            {"action": "complete"},
        )
        self.assertEqual(
            LessonCompletion.objects.filter(user=self.user, lesson=lesson).count(), 1
        )
        progress = ModuleProgress.objects.get(user=self.user, module=module)
        self.assertEqual(progress.progress_percentage, 50)

    def test_module_marks_complete_at_100(self):
        self.client.force_login(self.user)
        module = create_module(with_lessons=2)
        for lesson in module.lessons.all():
            self.client.post(
                reverse("training:lesson_detail", kwargs={"slug": lesson.slug}),
                {"action": "complete"},
            )
        progress = ModuleProgress.objects.get(user=self.user, module=module)
        self.assertTrue(progress.completed)
        self.assertEqual(progress.progress_percentage, 100)

    def test_published_lesson_only(self):
        module = create_module(with_lessons=1)
        from training.models import TrainingLesson

        hidden = TrainingLesson.objects.create(
            module=module, title="Hidden Lesson", content="x", published=False
        )
        response = self.client.get(
            reverse("training:module_detail", kwargs={"slug": module.slug})
        )
        self.assertNotContains(response, "Hidden Lesson")
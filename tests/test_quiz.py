"""Quiz engine tests: scoring, passing thresholds, attempts, and timing."""

from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from quizzes.models import QuizAttempt, UserAnswer
from tests.helpers import create_quiz, create_user


class QuizTests(TestCase):
    def setUp(self):
        self.user = create_user()
        self.client.force_login(self.user)

    def _start(self, quiz):
        return self.client.get(
            reverse("quizzes:take", kwargs={"pk": quiz.pk})
        )

    def _submit_answers(self, quiz, answer_all_correct=True):
        payload = {}
        for question in quiz.questions.all():
            if answer_all_correct:
                option = question.answers.filter(is_correct=True).first()
            else:
                option = question.answers.filter(is_correct=False).first()
            payload[f"question_{question.id}"] = option.id
        self._start(quiz)
        return self.client.post(
            reverse("quizzes:take", kwargs={"pk": quiz.pk}), payload
        )

    def test_quiz_list_published_only(self):
        create_quiz(title="Visible Quiz")
        from quizzes.models import Quiz

        Quiz.objects.create(title="Hidden Quiz", published=False)
        response = self.client.get(reverse("quizzes:list"))
        self.assertContains(response, "Visible Quiz")
        self.assertNotContains(response, "Hidden Quiz")

    def test_quiz_detail_shows_questions(self):
        quiz = create_quiz(questions=2)
        response = self.client.get(reverse("quizzes:detail", kwargs={"pk": quiz.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Questions")

    def test_take_page_shows_all_questions(self):
        quiz = create_quiz(questions=3)
        response = self.client.get(reverse("quizzes:take", kwargs={"pk": quiz.pk}))
        self.assertEqual(response.status_code, 200)
        for question in quiz.questions.all():
            self.assertContains(response, question.question_text)

    def test_correct_answers_full_score(self):
        quiz = create_quiz(questions=3)
        response = self._submit_answers(quiz, answer_all_correct=True)
        self.assertEqual(response.status_code, 302)
        attempt = QuizAttempt.objects.get(user=self.user, quiz=quiz)
        self.assertEqual(attempt.score, 3)
        self.assertEqual(attempt.percentage, 100)
        self.assertTrue(attempt.passed)
        self.assertEqual(attempt.user_answers.filter(is_correct=True).count(), 3)

    def test_wrong_answers_zero_score(self):
        quiz = create_quiz(questions=3)
        response = self._submit_answers(quiz, answer_all_correct=False)
        self.assertEqual(response.status_code, 302)
        attempt = QuizAttempt.objects.get(user=self.user, quiz=quiz)
        self.assertEqual(attempt.score, 0)
        self.assertEqual(attempt.percentage, 0)
        self.assertFalse(attempt.passed)

    def test_passing_threshold(self):
        quiz = create_quiz(questions=4, passing_score=75)
        # Answer 3 of 4 correctly = 75% -> passes
        payload = {}
        for i, question in enumerate(quiz.questions.all()):
            correct = i < 3
            payload[f"question_{question.id}"] = (
                question.answers.filter(is_correct=True).first().id
                if correct
                else question.answers.filter(is_correct=False).first().id
            )
        self._start(quiz)
        self.client.post(reverse("quizzes:take", kwargs={"pk": quiz.pk}), payload)
        attempt = QuizAttempt.objects.get(user=self.user, quiz=quiz)
        self.assertEqual(attempt.percentage, 75)
        self.assertTrue(attempt.passed)

    def test_client_cannot_inject_score(self):
        quiz = create_quiz(questions=2)
        # A malicious client posts a fake 'score' field; the server ignores it.
        payload = {}
        for question in quiz.questions.all():
            payload[f"question_{question.id}"] = (
                question.answers.filter(is_correct=True).first().id
            )
        payload["score"] = 9999
        payload["percentage"] = 1000
        self._start(quiz)
        response = self.client.post(
            reverse("quizzes:take", kwargs={"pk": quiz.pk}), payload
        )
        self.assertEqual(response.status_code, 302)
        attempt = QuizAttempt.objects.get(user=self.user, quiz=quiz)
        self.assertEqual(attempt.score, 2)  # server-computed, not injected
        self.assertEqual(attempt.percentage, 100)

    def test_result_page_shows_explanations(self):
        quiz = create_quiz(questions=2)
        self._submit_answers(quiz, answer_all_correct=True)
        attempt = QuizAttempt.objects.get(user=self.user, quiz=quiz)
        response = self.client.get(
            reverse("quizzes:result", kwargs={"attempt_id": attempt.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "PASSED")
        self.assertContains(response, "Correct answer")

    def test_partial_answers_recorded(self):
        quiz = create_quiz(questions=3)
        # Answer only the first question.
        first = quiz.questions.first()
        payload = {
            f"question_{first.id}": first.answers.filter(is_correct=True).first().id
        }
        self._start(quiz)
        self.client.post(reverse("quizzes:take", kwargs={"pk": quiz.pk}), payload)
        attempt = QuizAttempt.objects.get(user=self.user, quiz=quiz)
        self.assertEqual(attempt.score, 1)
        self.assertEqual(attempt.user_answers.count(), 3)  # one per question
        unanswered = attempt.user_answers.filter(selected_option__isnull=True).count()
        self.assertEqual(unanswered, 2)

    def test_retry_creates_new_attempt(self):
        quiz = create_quiz(questions=2)
        self._submit_answers(quiz, answer_all_correct=True)
        self._submit_answers(quiz, answer_all_correct=False)
        self.assertEqual(QuizAttempt.objects.filter(user=self.user, quiz=quiz).count(), 2)

    def test_quiz_list_uses_best_completed_attempt(self):
        quiz = create_quiz(questions=2)
        old = QuizAttempt.objects.create(
            user=self.user,
            quiz=quiz,
            score=1,
            percentage=50,
            passed=False,
            completed_at=timezone.now() - timedelta(days=1),
        )
        QuizAttempt.objects.create(
            user=self.user,
            quiz=quiz,
            score=2,
            percentage=100,
            passed=True,
            completed_at=timezone.now(),
        )
        response = self.client.get(reverse("quizzes:list"))
        self.assertEqual(response.context["attempts"][quiz.pk].percentage, 100)
        self.assertGreater(response.context["attempts"][quiz.pk].pk, old.pk)

    def test_refresh_does_not_reset_timer_or_create_attempt(self):
        quiz = create_quiz(questions=2, time_limit=60)
        first = self._start(quiz)
        attempt = QuizAttempt.objects.get(user=self.user, quiz=quiz)
        attempt.started_at = timezone.now() - timedelta(seconds=20)
        attempt.save(update_fields=["started_at"])

        second = self._start(quiz)

        self.assertEqual(
            QuizAttempt.objects.filter(user=self.user, quiz=quiz).count(), 1
        )
        self.assertLessEqual(second.context["remaining_seconds"], 40)
        self.assertGreaterEqual(second.context["remaining_seconds"], 35)
        self.assertEqual(first.context["attempt"].pk, attempt.pk)

    def test_expired_submission_is_finalized_without_credit(self):
        quiz = create_quiz(questions=2, time_limit=10)
        self._start(quiz)
        attempt = QuizAttempt.objects.get(user=self.user, quiz=quiz)
        attempt.started_at = timezone.now() - timedelta(seconds=30)
        attempt.save(update_fields=["started_at"])

        payload = {}
        for question in quiz.questions.all():
            payload[f"question_{question.id}"] = (
                question.answers.filter(is_correct=True).first().id
            )
        response = self.client.post(
            reverse("quizzes:take", kwargs={"pk": quiz.pk}), payload
        )

        self.assertEqual(response.status_code, 302)
        attempt.refresh_from_db()
        self.assertEqual(attempt.score, 0)
        self.assertEqual(attempt.percentage, 0)
        self.assertFalse(attempt.passed)
        self.assertIsNotNone(attempt.completed_at)
        self.assertEqual(attempt.user_answers.count(), 0)

    def test_post_without_starting_quiz_is_rejected(self):
        quiz = create_quiz(questions=2)
        response = self.client.post(
            reverse("quizzes:take", kwargs={"pk": quiz.pk}),
            {"question_1": "1"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            QuizAttempt.objects.filter(user=self.user, quiz=quiz).count(), 0
        )

    def test_replayed_submission_does_not_create_second_attempt(self):
        quiz = create_quiz(questions=2)
        payload = {}
        for question in quiz.questions.all():
            payload[f"question_{question.id}"] = (
                question.answers.filter(is_correct=True).first().id
            )
        self._start(quiz)
        first = self.client.post(
            reverse("quizzes:take", kwargs={"pk": quiz.pk}), payload
        )
        second = self.client.post(
            reverse("quizzes:take", kwargs={"pk": quiz.pk}), payload
        )

        self.assertEqual(first.status_code, 302)
        self.assertEqual(second.status_code, 302)
        self.assertEqual(
            QuizAttempt.objects.filter(user=self.user, quiz=quiz).count(), 1
        )
        self.assertEqual(
            UserAnswer.objects.filter(attempt__user=self.user).count(),
            quiz.questions.count(),
        )

    def test_quiz_without_time_limit_has_no_server_deadline(self):
        quiz = create_quiz(questions=2, time_limit=0)
        response = self._start(quiz)
        self.assertIsNone(response.context["remaining_seconds"])
        self.assertNotContains(response, 'id="quiz-timer"')
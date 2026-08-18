"""Quiz engine tests: scoring, passing thresholds, attempts."""

from django.test import TestCase
from django.urls import reverse

from quizzes.models import QuizAttempt, UserAnswer
from tests.helpers import create_module, create_quiz, create_user


class QuizTests(TestCase):
    def setUp(self):
        self.user = create_user()
        self.client.force_login(self.user)

    def _submit_answers(self, quiz, answer_all_correct=True):
        payload = {}
        for question in quiz.questions.all():
            if answer_all_correct:
                option = question.answers.filter(is_correct=True).first()
            else:
                option = question.answers.filter(is_correct=False).first()
            payload[f"question_{question.id}"] = option.id
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
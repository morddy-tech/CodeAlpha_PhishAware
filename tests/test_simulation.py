"""Simulation tests: scenario display, scoring, and credential safety."""

import re

from django.test import TestCase
from django.urls import reverse

from simulations.models import ScenarioAttempt
from simulations.services import score_scenario
from tests.helpers import create_scenario, create_user


class SimulationTests(TestCase):
    def setUp(self):
        self.user = create_user()
        self.scenario, self.parts = create_scenario("Test Phishing Email")

    def test_scenario_list_shows_published_only(self):
        create_scenario("Another Scenario")
        from simulations.models import PhishingScenario

        PhishingScenario.objects.create(
            title="Hidden Scenario", published=False
        )
        response = self.client.get(reverse("simulations:list"))
        self.assertContains(response, "Test Phishing Email")
        self.assertNotContains(response, "Hidden Scenario")

    def test_scenario_detail_loads(self):
        response = self.client.get(
            reverse("simulations:scenario_detail", kwargs={"pk": self.scenario.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Suspicious domain")

    def test_scenario_detail_shows_distractor_and_real_flags(self):
        response = self.client.get(
            reverse("simulations:scenario_detail", kwargs={"pk": self.scenario.pk})
        )
        self.assertContains(response, "Suspicious domain")
        self.assertContains(response, "Polite wording")

    def test_perfect_detection_score(self):
        result = score_scenario(
            self.scenario,
            [self.parts["flag"].id],
            self.parts["response"].id,
        )
        self.assertEqual(result["correct_detected"], 1)
        self.assertEqual(result["false_positives"], 0)
        self.assertEqual(result["detection_percent"], 100)
        self.assertTrue(result["response_correct"])

    def test_false_positive_penalty(self):
        result = score_scenario(
            self.scenario,
            [self.parts["flag"].id, self.parts["distractor"].id],
            self.parts["response"].id,
        )
        self.assertEqual(result["correct_detected"], 1)
        self.assertEqual(result["false_positives"], 1)
        self.assertEqual(result["detection_percent"], 0)

    def test_selecting_only_distractor_scores_zero(self):
        result = score_scenario(
            self.scenario,
            [self.parts["distractor"].id],
            self.parts["response"].id,
        )
        self.assertEqual(result["correct_detected"], 0)
        self.assertEqual(result["detection_percent"], 0)

    def test_wrong_response_reduces_score(self):
        wrong_response = self.scenario.response_options.filter(is_correct=False).first()
        result = score_scenario(
            self.scenario,
            [self.parts["flag"].id],
            wrong_response.id,
        )
        self.assertFalse(result["response_correct"])
        self.assertLess(result["score"], 100)

    def test_forged_indicator_ids_are_ignored(self):
        result = score_scenario(
            self.scenario,
            ["999999", "abc", self.parts["flag"].id],
            self.parts["response"].id,
        )
        self.assertEqual(result["correct_detected"], 1)
        self.assertEqual(result["false_positives"], 0)

    def test_submission_creates_attempt(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("simulations:scenario_submit", kwargs={"pk": self.scenario.pk}),
            {
                "indicators": [self.parts["flag"].id],
                "response": self.parts["response"].id,
            },
        )
        self.assertEqual(response.status_code, 302)
        attempt = ScenarioAttempt.objects.get(user=self.user, scenario=self.scenario)
        self.assertEqual(attempt.score, 100)
        self.assertEqual(attempt.identified_indicators, 1)
        self.assertEqual(attempt.selected_indicator_ids, [self.parts["flag"].id])
        feedback = self.client.get(response.url)
        self.assertEqual(feedback.status_code, 200)
        self.assertContains(feedback, "You correctly identified")

    def test_submission_requires_login(self):
        response = self.client.post(
            reverse("simulations:scenario_submit", kwargs={"pk": self.scenario.pk}),
            {"indicators": [self.parts["flag"].id]},
        )
        self.assertIn(response.status_code, (302, 403))
        self.assertFalse(ScenarioAttempt.objects.filter(user=self.user).exists())

    def test_website_scenario_dummy_fields_not_stored(self):
        """The fake-website scenario's username/password fields must never be stored."""
        from simulations.models import PhishingScenario

        website = PhishingScenario.objects.create(
            title="Fake Login Site",
            scenario_type="website",
            explanation="Do not enter real credentials.",
            published=True,
        )
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("simulations:scenario_submit", kwargs={"pk": website.pk}),
            {
                "sim_username": "victim@example.com",
                "sim_password": "SuperSecret!123",
                "indicators": [],
            },
        )
        self.assertEqual(response.status_code, 302)
        attempt = ScenarioAttempt.objects.get(user=self.user, scenario=website)
        self.assertEqual(attempt.score, 0)
        # Ensure the submitted dummy credentials were not persisted anywhere.
        self.assertFalse(
            ScenarioAttempt.objects.filter(
                identified_indicators__gt=0
            ).exists()
        )
        from progress.models import Notification

        self.assertFalse(
            Notification.objects.filter(message__icontains="SuperSecret").exists()
        )
        feedback = self.client.get(response.url)
        self.assertEqual(feedback.status_code, 200)
        content = feedback.content.decode()
        self.assertNotIn("SuperSecret", content)

    def test_website_scenario_inputs_are_not_form_controls(self):
        """Rendered demo inputs must not be successful controls in the scoring form."""
        from simulations.models import PhishingScenario

        website = PhishingScenario.objects.create(
            title="Fake Login Site",
            scenario_type="website",
            explanation="Do not enter real credentials.",
            published=True,
        )
        response = self.client.get(
            reverse("simulations:scenario_detail", kwargs={"pk": website.pk})
        )
        html = response.content.decode()
        submitted_names = set(re.findall(r'<input[^>]*\bname="([^"]+)"', html))
        self.assertNotIn("sim_username", submitted_names)
        self.assertNotIn("sim_password", submitted_names)
        self.assertIn("never submitted, stored, or transmitted", html)

    def test_feedback_refresh_does_not_create_another_attempt(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("simulations:scenario_submit", kwargs={"pk": self.scenario.pk}),
            {
                "indicators": [self.parts["flag"].id],
                "response": self.parts["response"].id,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.client.get(response.url)
        self.client.get(response.url)
        self.assertEqual(
            ScenarioAttempt.objects.filter(
                user=self.user, scenario=self.scenario
            ).count(),
            1,
        )

    def test_feedback_is_scoped_to_the_authenticated_user(self):
        other = create_user("bob", "bob@example.com")
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("simulations:scenario_submit", kwargs={"pk": self.scenario.pk}),
            {
                "indicators": [self.parts["flag"].id],
                "response": self.parts["response"].id,
            },
        )
        attempt = ScenarioAttempt.objects.get(user=self.user, scenario=self.scenario)
        self.client.force_login(other)
        response = self.client.get(response.url)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(attempt.user, self.user)

    def test_feedback_requires_login(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("simulations:scenario_submit", kwargs={"pk": self.scenario.pk}),
            {
                "indicators": [self.parts["flag"].id],
                "response": self.parts["response"].id,
            },
        )
        self.client.logout()
        response = self.client.get(response.url)
        self.assertIn(response.status_code, (302, 403))
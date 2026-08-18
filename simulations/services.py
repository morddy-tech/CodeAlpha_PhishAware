"""Scoring logic for educational phishing simulations.

No real credentials are ever collected, transmitted, or stored.
"""

from django.db import transaction

from progress.models import Notification
from progress.services import create_notification, evaluate_achievements
from simulations.models import ScenarioAttempt, ScenarioResponseOption


def score_scenario(scenario, selected_indicator_ids, selected_response_id=None):
    """Compute the learner's score for a scenario.

    Detection scoring:
      * +1 for each genuine red flag correctly selected
      * -1 for each false positive (a distractor clue wrongly flagged)
      * Score is normalized to 0-100 based on the total number of real flags.

    Action scoring (optional):
      * Choosing the recommended 'what should you do?' option is worth weight.

    Returns a dict of results for the feedback view.
    """
    real_flags = list(scenario.real_flags())
    distractors = list(scenario.indicators.filter(is_distractor=True))

    real_ids = {flag.id for flag in real_flags}
    distractor_ids = {flag.id for flag in distractors}
    valid_ids = real_ids | distractor_ids

    selected = set()
    for value in selected_indicator_ids:
        try:
            selected.add(int(value))
        except (TypeError, ValueError):
            continue
    selected = selected & valid_ids

    correct_detected = len(selected & real_ids)
    false_positives = len(selected & distractor_ids)

    total = max(len(real_ids), 1)
    detection_raw = max(0, correct_detected - false_positives)
    detection_percent = round(detection_raw / total * 100)

    response_option = None
    response_correct = None
    if selected_response_id and scenario.response_options.exists():
        try:
            response_option = scenario.response_options.get(
                id=int(selected_response_id)
            )
        except (ScenarioResponseOption.DoesNotExist, ValueError, TypeError):
            response_option = None
        response_correct = bool(response_option and response_option.is_correct)

    if response_correct is None:
        score = detection_percent
    else:
        action_weight = 0.3
        action_percent = 100 if response_correct else 0
        score = round(
            detection_percent * (1 - action_weight) + action_percent * action_weight
        )

    return {
        "score": score,
        "detection_percent": detection_percent,
        "correct_detected": correct_detected,
        "false_positives": false_positives,
        "total_indicators": total,
        "selected_ids": selected,
        "real_ids": real_ids,
        "distractor_ids": distractor_ids,
        "response_option": response_option,
        "response_correct": response_correct,
        "real_flags": real_flags,
        "distractors": distractors,
    }


@transaction.atomic
def record_scenario_attempt(user, scenario, result):
    attempt = ScenarioAttempt.objects.create(
        user=user,
        scenario=scenario,
        score=result["score"],
        identified_indicators=result["correct_detected"],
        selected_response=result["response_option"],
        completed=True,
    )

    if result["score"] >= 70:
        create_notification(
            user,
            "Scenario completed",
            f"You scored {result['score']}% on “{scenario.title}”.",
            Notification.NotificationType.TRAINING,
        )
    evaluate_achievements(user)
    return attempt
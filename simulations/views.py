from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render

from simulations.models import PhishingScenario, ScenarioAttempt
from simulations.services import record_scenario_attempt, score_scenario


def scenario_list(request):
    scenario_type = request.GET.get("type", "")
    difficulty = request.GET.get("difficulty", "")

    scenarios = (
        PhishingScenario.objects.filter(published=True)
        .prefetch_related("indicators")
        .annotate(
            real_flag_count=Count(
                "indicators",
                filter=Q(indicators__is_distractor=False),
            )
        )
    )
    if scenario_type:
        scenarios = scenarios.filter(scenario_type=scenario_type)
    if difficulty:
        scenarios = scenarios.filter(difficulty=difficulty)

    completed_ids = set()
    if request.user.is_authenticated:
        completed_ids = set(
            ScenarioAttempt.objects.filter(user=request.user).values_list(
                "scenario_id", flat=True
            )
        )

    return render(
        request,
        "simulations/list.html",
        {
            "scenarios": scenarios,
            "scenario_type": scenario_type,
            "difficulty": difficulty,
            "completed_ids": completed_ids,
            "type_choices": PhishingScenario.ScenarioType.choices,
            "difficulty_choices": PhishingScenario.Difficulty.choices,
        },
    )


def scenario_detail(request, pk):
    scenario = get_object_or_404(
        PhishingScenario.objects.prefetch_related(
            "indicators", "response_options"
        ),
        pk=pk,
        published=True,
    )
    return render(
        request,
        "simulations/detail.html",
        {
            "scenario": scenario,
            "clues": scenario.clue_options(),
        },
    )


@login_required
def scenario_submit(request, pk):
    scenario = get_object_or_404(
        PhishingScenario.objects.prefetch_related("indicators", "response_options"),
        pk=pk,
        published=True,
    )
    if request.method != "POST":
        return redirect("simulations:scenario_detail", pk=pk)

    selected_ids = request.POST.getlist("indicators")
    selected_response = request.POST.get("response", "")

    result = score_scenario(scenario, selected_ids, selected_response)
    attempt = record_scenario_attempt(request.user, scenario, result)

    # Post-Redirect-Get: refreshing the feedback page must never score again.
    return redirect("simulations:scenario_feedback", attempt_id=attempt.pk)


@login_required
def scenario_feedback(request, attempt_id):
    attempt = get_object_or_404(
        ScenarioAttempt.objects.select_related("scenario").prefetch_related(
            "scenario__indicators", "scenario__response_options"
        ),
        pk=attempt_id,
        user=request.user,
    )
    scenario = attempt.scenario
    result = score_scenario(
        scenario,
        attempt.selected_indicator_ids,
        attempt.selected_response_id,
    )
    # Legacy attempts created before selected clue IDs were persisted only have
    # aggregate counts. Preserve their displayed result without inventing data.
    if not attempt.selected_indicator_ids:
        result["correct_detected"] = attempt.identified_indicators
        result["score"] = attempt.score

    return render(
        request,
        "simulations/feedback.html",
        {
            "scenario": scenario,
            "result": result,
            "attempt": attempt,
        },
    )
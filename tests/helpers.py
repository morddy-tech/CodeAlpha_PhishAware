"""Shared factories and helpers for the PhishAware test suite."""

from django.contrib.auth.models import User
from django.core.cache import cache

from quizzes.models import AnswerOption, Question, Quiz
from simulations.models import PhishingScenario, ScenarioIndicator, ScenarioResponseOption
from training.models import TrainingLesson, TrainingModule

PASSWORD = "Str0ngPass!word"


def create_user(username="alice", email="alice@example.com", **kwargs):
    # Deliberately do not create a profile here: the post_save signal must be
    # responsible for it, so the test suite actually guards that behaviour.
    return User.objects.create_user(
        username=username,
        email=email,
        password=PASSWORD,
        first_name=kwargs.pop("first_name", "Alice"),
        last_name=kwargs.pop("last_name", "Example"),
        **kwargs,
    )


def create_staff(username="admin", email="admin@example.com"):
    user = create_user(username=username, email=email, is_staff=True, is_superuser=True)
    return user


def create_module(title="Test Module", with_lessons=2, **kwargs):
    module = TrainingModule.objects.create(
        title=title,
        description="A test module.",
        category="Test",
        difficulty=kwargs.pop("difficulty", "beginner"),
        published=kwargs.pop("published", True),
        order=kwargs.pop("order", 1),
        **kwargs,
    )
    for index in range(with_lessons):
        TrainingLesson.objects.create(
            module=module,
            title=f"Lesson {index + 1}",
            content="Lesson content for testing.",
            order=index,
            published=True,
        )
    return module


def create_quiz(
    title="Test Quiz",
    questions=3,
    passing_score=70,
    module=None,
    time_limit=0,
):
    quiz = Quiz.objects.create(
        title=title,
        description="A test quiz.",
        module=module,
        passing_score=passing_score,
        time_limit=time_limit,
        published=True,
    )
    for index in range(questions):
        question = Question.objects.create(
            quiz=quiz,
            question_text=f"Question {index + 1}?",
            question_type="mc",
            points=1,
            order=index,
        )
        AnswerOption.objects.create(
            question=question,
            option_text="Correct answer",
            is_correct=True,
            order=0,
        )
        AnswerOption.objects.create(
            question=question,
            option_text="Wrong answer",
            is_correct=False,
            order=1,
        )
    return quiz


def create_scenario(title="Test Scenario", scenario_type="email"):
    scenario = PhishingScenario.objects.create(
        title=title,
        scenario_type=scenario_type,
        description="A test scenario.",
        explanation="This is the educational explanation.",
        published=True,
    )
    flag = ScenarioIndicator.objects.create(
        scenario=scenario,
        title="Suspicious domain",
        description="The domain is wrong.",
        indicator_type="domain",
        severity="high",
    )
    distractor = ScenarioIndicator.objects.create(
        scenario=scenario,
        title="Polite wording",
        description="Benign text.",
        is_distractor=True,
    )
    response = ScenarioResponseOption.objects.create(
        scenario=scenario,
        text="Report it",
        is_correct=True,
    )
    ScenarioResponseOption.objects.create(
        scenario=scenario,
        text="Click the link",
        is_correct=False,
    )
    return scenario, {"flag": flag, "distractor": distractor, "response": response}


def clear_rate_limit_cache():
    cache.clear()
"""Idempotent management command that seeds PhishAware training content.

Usage:
    python manage.py seed_training

Running it twice does not create duplicates: all records are keyed by
unique slugs (or titles) and updated in place.
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from core.seed_final import ACHIEVEMENTS, FINAL_ASSESSMENT
from core.seed_modules_a import MODULES_A
from core.seed_modules_b import MODULES_B
from core.seed_quizzes import QUIZZES
from core.seed_scenarios import SCENARIOS
from progress.models import Achievement
from quizzes.models import AnswerOption, Question, Quiz
from simulations.models import (
    PhishingScenario,
    ScenarioIndicator,
    ScenarioResponseOption,
)
from training.models import TrainingLesson, TrainingModule


class Command(BaseCommand):
    help = "Seed PhishAware with modules, lessons, scenarios, quizzes and achievements."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete existing seeded content before re-seeding.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options["reset"]:
            self._reset()
            self.stdout.write("Cleared existing seeded content.")

        modules = self._seed_modules(MODULES_A + MODULES_B)
        quizzes = self._seed_quizzes(QUIZZES + [FINAL_ASSESSMENT], modules)
        scenarios = self._seed_scenarios(SCENARIOS)
        achievements = self._seed_achievements()

        self.stdout.write(self.style.SUCCESS(
            f"Seeded {len(modules)} modules, {len(quizzes)} quizzes, "
            f"{len(scenarios)} scenarios, and {len(achievements)} achievements."
        ))

    def _reset(self):
        Quiz.objects.all().delete()
        PhishingScenario.objects.all().delete()
        TrainingModule.objects.all().delete()
        Achievement.objects.all().delete()

    def _seed_modules(self, module_specs):
        modules = []
        for spec in module_specs:
            module, _ = TrainingModule.objects.update_or_create(
                slug=slugify(spec["title"]),
                defaults={
                    "title": spec["title"],
                    "category": spec["category"],
                    "difficulty": spec["difficulty"],
                    "estimated_minutes": spec["estimated_minutes"],
                    "featured": spec.get("featured", False),
                    "order": spec["order"],
                    "description": spec["description"],
                    "published": True,
                },
            )
            for index, lesson_spec in enumerate(spec["lessons"]):
                TrainingLesson.objects.update_or_create(
                    module=module,
                    slug=slugify(lesson_spec["title"]),
                    defaults={
                        "title": lesson_spec["title"],
                        "content": lesson_spec["content"],
                        "order": index,
                        "estimated_minutes": 5,
                        "published": True,
                    },
                )
            modules.append(module)
        return modules

    def _seed_quizzes(self, quiz_specs, modules):
        quizzes = []
        for spec in quiz_specs:
            module = None
            if spec.get("module_title"):
                module = TrainingModule.objects.filter(
                    slug=slugify(spec["module_title"])
                ).first()
            quiz, _ = Quiz.objects.update_or_create(
                title=spec["title"],
                defaults={
                    "description": spec["description"],
                    "module": module,
                    "passing_score": spec["passing_score"],
                    "time_limit": spec["time_limit"],
                    "published": True,
                },
            )
            for index, question_spec in enumerate(spec["questions"]):
                question, _ = Question.objects.update_or_create(
                    quiz=quiz,
                    question_text=question_spec["question_text"],
                    defaults={
                        "question_type": question_spec["question_type"],
                        "points": question_spec["points"],
                        "explanation": question_spec.get("explanation", ""),
                        "order": index,
                    },
                )
                for option_index, option_spec in enumerate(question_spec["options"]):
                    AnswerOption.objects.update_or_create(
                        question=question,
                        option_text=option_spec["text"],
                        defaults={
                            "is_correct": option_spec["is_correct"],
                            "explanation": option_spec.get("explanation", ""),
                            "order": option_index,
                        },
                    )
            quizzes.append(quiz)
        return quizzes

    def _seed_scenarios(self, scenario_specs):
        scenarios = []
        for spec in scenario_specs:
            scenario, _ = PhishingScenario.objects.update_or_create(
                title=spec["title"],
                defaults={
                    "scenario_type": spec["scenario_type"],
                    "difficulty": spec["difficulty"],
                    "description": spec.get("description", ""),
                    "simulated_content": spec.get("simulated_content", ""),
                    "sender": spec.get("sender", ""),
                    "source": spec.get("source", ""),
                    "recipient": spec.get("recipient", ""),
                    "subject": spec.get("subject", ""),
                    "body": spec.get("body", ""),
                    "links": spec.get("links", []),
                    "attachment_name": spec.get("attachment_name", ""),
                    "site_name": spec.get("site_name", ""),
                    "explanation": spec["explanation"],
                    "published": True,
                },
            )
            for index, indicator_spec in enumerate(spec.get("indicators", [])):
                ScenarioIndicator.objects.update_or_create(
                    scenario=scenario,
                    title=indicator_spec["title"],
                    defaults={
                        "description": indicator_spec["description"],
                        "indicator_type": indicator_spec["indicator_type"],
                        "location": indicator_spec.get("location", ""),
                        "severity": indicator_spec["severity"],
                        "is_distractor": indicator_spec.get("is_distractor", False),
                        "order": index,
                    },
                )
            for index, response_spec in enumerate(spec.get("response_options", [])):
                ScenarioResponseOption.objects.update_or_create(
                    scenario=scenario,
                    text=response_spec["text"],
                    defaults={
                        "is_correct": response_spec["is_correct"],
                        "explanation": response_spec.get("explanation", ""),
                        "order": index,
                    },
                )
            scenarios.append(scenario)
        return scenarios

    def _seed_achievements(self):
        created = []
        for spec in ACHIEVEMENTS:
            achievement, _ = Achievement.objects.update_or_create(
                slug=spec["slug"],
                defaults={
                    "name": spec["name"],
                    "description": spec["description"],
                    "icon": spec["icon"],
                    "requirement": spec["requirement"],
                    "active": True,
                },
            )
            created.append(achievement)
        return created
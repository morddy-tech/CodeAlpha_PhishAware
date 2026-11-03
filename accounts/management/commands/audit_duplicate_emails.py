"""Report case-insensitive duplicate email identities.

This command is intentionally read-only. It gives an operator the information
needed to resolve conflicts manually before a database-level unique index on
``LOWER(email)`` is introduced. It never deletes or merges accounts.
"""

from collections import defaultdict

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "List case-insensitive duplicate email addresses without changing data."

    def add_arguments(self, parser):
        parser.add_argument(
            "--fail-on-duplicates",
            action="store_true",
            help="Exit with a non-zero status if duplicates are found (useful in CI).",
        )

    def handle(self, *args, **options):
        User = get_user_model()
        buckets = defaultdict(list)
        for user_id, email in User.objects.exclude(email="").values_list(
            "id", "email"
        ):
            buckets[email.strip().lower()].append(user_id)

        duplicates = {
            email: ids for email, ids in buckets.items() if len(ids) > 1
        }
        if not duplicates:
            self.stdout.write(self.style.SUCCESS("No duplicate emails found."))
            return

        for email, ids in sorted(duplicates.items()):
            self.stdout.write(
                self.style.WARNING(
                    f"{email}: user IDs {', '.join(str(i) for i in ids)}"
                )
            )
        message = (
            f"{len(duplicates)} duplicate email group(s) found. "
            "Resolve manually; no accounts were changed."
        )
        if options["fail_on_duplicates"]:
            raise CommandError(message)
        self.stdout.write(self.style.WARNING(message))

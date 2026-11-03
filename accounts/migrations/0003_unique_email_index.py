"""Add a case-insensitive uniqueness guarantee for non-empty user emails.

This runs after :mod:`accounts.0002` and deliberately aborts (with an
actionable message) if existing data contains conflicts. It never deletes or
merges accounts. The partial index is supported by SQLite and PostgreSQL, the
two databases this project targets.
"""

from collections import defaultdict

from django.db import migrations


def check_duplicate_emails(apps, schema_editor):
    User = apps.get_model("auth", "User")
    buckets = defaultdict(list)
    for user_id, email in User.objects.exclude(email="").values_list(
        "id", "email"
    ):
        buckets[email.strip().lower()].append(user_id)
    duplicates = {
        email: ids for email, ids in buckets.items() if len(ids) > 1
    }
    if duplicates:
        details = "; ".join(
            f"{email}: {', '.join(str(i) for i in ids)}"
            for email, ids in sorted(duplicates.items())
        )
        raise RuntimeError(
            "Duplicate case-insensitive emails must be resolved manually before "
            f"this migration can run: {details}. Run "
            "`python manage.py audit_duplicate_emails` for details."
        )


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0002_backfill_user_profiles"),
    ]

    operations = [
        migrations.RunPython(check_duplicate_emails, migrations.RunPython.noop),
        migrations.RunSQL(
            sql=(
                "CREATE UNIQUE INDEX IF NOT EXISTS auth_user_email_ci_unique "
                "ON auth_user (LOWER(email)) WHERE email <> '';"
            ),
            reverse_sql="DROP INDEX IF EXISTS auth_user_email_ci_unique;",
        ),
    ]

"""Backfill ``UserProfile`` rows for accounts created before the signal existed."""

from django.conf import settings
from django.db import migrations


def backfill_profiles(apps, schema_editor):
    User = apps.get_model("auth", "User")
    UserProfile = apps.get_model("accounts", "UserProfile")

    existing_user_ids = set(
        UserProfile.objects.values_list("user_id", flat=True)
    )
    missing = [
        UserProfile(user_id=user_id)
        for user_id in User.objects.exclude(id__in=existing_user_ids).values_list(
            "id", flat=True
        )
    ]
    if missing:
        UserProfile.objects.bulk_create(missing, ignore_conflicts=True)


def remove_backfilled_profiles(apps, schema_editor):
    # Deliberately a no-op: profile data may have been edited after creation and
    # must never be deleted by a reverse migration.
    pass


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(backfill_profiles, remove_backfilled_profiles),
    ]

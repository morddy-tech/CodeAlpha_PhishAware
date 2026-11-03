"""Signals that keep user-related records consistent.

A ``UserProfile`` is created automatically for every user, regardless of how
the account was created (registration form, ``createsuperuser``, Django admin,
fixtures, or tests). The signal is idempotent and uses ``get_or_create`` so it
is safe under concurrent account creation.
"""

from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from accounts.models import UserProfile


@receiver(
    post_save,
    sender=get_user_model(),
    dispatch_uid="accounts.ensure_user_profile",
)
def ensure_user_profile(sender, instance, created, raw=False, **kwargs):
    """Create the profile for a user unless this is a raw fixture load."""
    if raw:
        return
    UserProfile.objects.get_or_create(user=instance)

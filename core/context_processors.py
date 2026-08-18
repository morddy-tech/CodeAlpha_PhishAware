"""Template context processors shared across the site."""

from progress.services import unread_notification_count

SITE_NAME = "PhishAware"
SITE_TAGLINE = "Learn to Detect. Learn to Defend."
GITHUB_URL = "https://github.com/morddy-tech/CodeAlpha_PhishAware"


def site_settings(request):
    context = {
        "site_name": SITE_NAME,
        "site_tagline": SITE_TAGLINE,
        "github_url": GITHUB_URL,
        "unread_notifications": 0,
    }
    user = getattr(request, "user", None)
    if user and user.is_authenticated:
        context["unread_notifications"] = unread_notification_count(user)
    return context
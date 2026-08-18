"""Security headers middleware."""

from django.conf import settings
from django.utils.deprecation import MiddlewareMixin


class SecurityHeadersMiddleware(MiddlewareMixin):
    """Add defensive security headers not covered by Django core middleware."""

    def process_response(self, request, response):
        response.setdefault("X-Content-Type-Options", "nosniff")
        response.setdefault("Referrer-Policy", getattr(settings, "SECURE_REFERRER_POLICY", "same-origin"))
        if getattr(settings, "X_FRAME_OPTIONS", None):
            response.setdefault("X-Frame-Options", settings.X_FRAME_OPTIONS)
        if not settings.DEBUG:
            response.setdefault("Permissions-Policy", "geolocation=(), microphone=(), camera=()")
        return response
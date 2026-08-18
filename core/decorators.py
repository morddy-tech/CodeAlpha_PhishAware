"""Application-level rate limiting for sensitive endpoints.

Uses Django's cache framework (locmem by default) to limit how often a
client can submit to authentication-sensitive endpoints. This is a defensive
abuse-protection measure and is not used for any offensive purpose.
"""

import functools
import logging
import time

from django.conf import settings
from django.core.cache import cache
from django.http import HttpRequest, HttpResponseForbidden

logger = logging.getLogger("security")


def _client_key(request, scope):
    ip = request.META.get("REMOTE_ADDR", "unknown")
    return f"ratelimit:{scope}:{ip}"


def rate_limit(scope, attempts=None, window=None, lockout=None):
    """Decorator that limits the number of requests per client IP per window.

    Works with both plain views (def view(request)) and view methods
    (def dispatch(self, request)). After the limit is exceeded the client is
    locked out for `lockout` seconds (defaults to the configured value).
    """

    attempts = attempts or getattr(settings, "RATE_LIMIT_ATTEMPTS", 5)
    window = window or getattr(settings, "RATE_LIMIT_WINDOW_SECONDS", 300)
    lockout = lockout or getattr(settings, "RATE_LIMIT_LOCKOUT_SECONDS", 900)

    def decorator(view):
        @functools.wraps(view)
        def wrapper(*args, **kwargs):
            request = _find_request(args, kwargs)
            if request is None or request.method not in {"POST", "PUT", "PATCH"}:
                return view(*args, **kwargs)

            key = _client_key(request, scope)
            lockout_key = f"{key}:lockout"

            if cache.get(lockout_key) is not None:
                logger.warning("Rate limit: client %s locked out for %s", key, scope)
                return HttpResponseForbidden(
                    "Too many requests. Please try again later.",
                    content_type="text/plain",
                )

            now = int(time.time())
            window_key = f"{key}:window:{now // window}"
            count = cache.get(window_key, 0) + 1
            cache.set(window_key, count, timeout=window * 2)

            if count > attempts:
                cache.set(lockout_key, True, timeout=lockout)
                logger.warning("Rate limit exceeded: client %s blocked on %s", key, scope)
                return HttpResponseForbidden(
                    "Too many attempts. Please wait a few minutes and try again.",
                    content_type="text/plain",
                )
            return view(*args, **kwargs)

        return wrapper

    return decorator


def _find_request(args, kwargs):
    request = kwargs.get("request")
    if request is not None:
        return request
    for arg in args:
        if isinstance(arg, HttpRequest):
            return arg
    return None
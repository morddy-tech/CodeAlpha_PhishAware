"""Application-level rate limiting for sensitive endpoints.

Uses Django's cache framework (locmem by default, Redis in production) to limit
how often a client can submit to authentication-sensitive endpoints. This is a
defensive abuse-protection measure and is not used for any offensive purpose.

Only ``REMOTE_ADDR`` is trusted unless ``TRUST_PROXY_HEADERS`` is explicitly
enabled for a deployment whose proxy overwrites client-supplied forwarding
headers.
"""

import functools
import logging
import time

from django.conf import settings
from django.core.cache import cache
from django.http import HttpRequest, HttpResponse

logger = logging.getLogger("security")


def client_ip(request):
    """Return the client address, honouring X-Forwarded-For only when trusted."""
    if getattr(settings, "TRUST_PROXY_HEADERS", False):
        forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR", "")
        if forwarded_for:
            # The left-most entry is the original client when (and only when)
            # the edge proxy sanitises the header and appends the chain.
            candidate = forwarded_for.split(",")[0].strip()
            if candidate:
                return candidate
    return request.META.get("REMOTE_ADDR", "unknown")


def _client_key(request, scope):
    return f"ratelimit:{scope}:{client_ip(request)}"


def _too_many(retry_after):
    response = HttpResponse(
        "Too many requests. Please try again later.",
        status=429,
        content_type="text/plain",
    )
    response.headers["Retry-After"] = str(max(1, int(retry_after)))
    return response


def rate_limit(scope, attempts=None, window=None, lockout=None, key_func=None):
    """Decorate a view with a cache-backed rate limit.

    Works with both plain views (``def view(request)``) and view methods
    (``def dispatch(self, request)``). Only state-changing methods are counted
    so ordinary page views are never blocked.

    ``key_func`` may return one or more full cache keys. If any bucket exceeds
    its limit the request is rejected with HTTP 429 and a ``Retry-After``
    header.
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

            keys = (
                key_func(request)
                if key_func is not None
                else [_client_key(request, scope)]
            )
            keys = [key for key in keys if key]
            if not keys:
                keys = [_client_key(request, scope)]

            for key in keys:
                if cache.get(f"{key}:lockout") is not None:
                    logger.warning("Rate limit: client locked out for %s", scope)
                    return _too_many(lockout)

            now = int(time.time())
            exceeded = False
            for key in keys:
                window_key = f"{key}:window:{now // window}"
                count = cache.get(window_key, 0) + 1
                cache.set(window_key, count, timeout=window * 2)
                if count > attempts:
                    exceeded = True

            if exceeded:
                for key in keys:
                    cache.set(f"{key}:lockout", True, timeout=lockout)
                logger.warning("Rate limit exceeded: client blocked on %s", scope)
                return _too_many(lockout)

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

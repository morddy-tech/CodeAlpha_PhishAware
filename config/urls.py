"""Root URL configuration for PhishAware."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.views import serve as staticfiles_serve
from django.urls import include, path, re_path

handler400 = "core.views.custom_bad_request"
handler403 = "core.views.custom_forbidden"
handler404 = "core.views.custom_not_found"
handler500 = "core.views.custom_server_error"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("training/", include("training.urls")),
    path("simulations/", include("simulations.urls")),
    path("quizzes/", include("quizzes.urls")),
    path("progress/", include("progress.urls")),
    path("dashboard/", include("dashboard.urls")),
    path("", include("core.urls")),
]

# Serve static/media from the local dev server (including when DEBUG=False on
# a development machine, e.g. via SERVE_STATIC_FILES=True). In production you
# must run `collectstatic` and let your web server serve STATIC_ROOT instead,
# keeping SERVE_STATIC_FILES=False.
if settings.SERVE_STATIC_FILES:
    urlpatterns += [
        re_path(
            r"^static/(?P<path>.*)$",
            staticfiles_serve,
            name="static_dev",
            kwargs={"insecure": True},
        ),
    ]

if settings.SERVE_MEDIA_FILES:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
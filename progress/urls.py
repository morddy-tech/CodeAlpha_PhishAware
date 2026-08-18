from django.urls import path

from progress import views

app_name = "progress"

urlpatterns = [
    path("", views.progress_overview, name="overview"),
    path("achievements/", views.achievements_view, name="achievements"),
    path("notifications/", views.notifications_view, name="notifications"),
]
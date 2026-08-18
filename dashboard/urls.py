from django.urls import path

from dashboard import views

app_name = "dashboard"

urlpatterns = [
    path("", views.home, name="home"),
    path("admin/", views.admin_dashboard, name="admin_dashboard"),
    path("admin/users/", views.admin_users, name="admin_users"),
    path("admin/users/<int:user_id>/", views.admin_user_detail, name="admin_user_detail"),
    path("admin/content/", views.admin_content, name="admin_content"),
    path("admin/analytics/", views.admin_analytics, name="admin_analytics"),
    path("admin/feedback/", views.admin_feedback, name="admin_feedback"),
    path(
        "admin/feedback/<int:pk>/resolve/",
        views.admin_feedback_resolve,
        name="admin_feedback_resolve",
    ),
]
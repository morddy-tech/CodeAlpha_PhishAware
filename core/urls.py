from django.urls import path

from core import views

app_name = "core"

urlpatterns = [
    path("", views.landing_page, name="landing"),
    path("about/", views.about_page, name="about"),
    path("security-tips/", views.security_tips, name="security_tips"),
    path("faq/", views.faq_page, name="faq"),
    path("privacy/", views.privacy_page, name="privacy"),
    path("feedback/", views.feedback_view, name="feedback"),
    path("forbidden/", views.forbidden_page, name="forbidden"),
]
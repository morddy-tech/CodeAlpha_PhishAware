from django.urls import path

from training import views

app_name = "training"

urlpatterns = [
    path("", views.training_index, name="index"),
    path("module/<slug:slug>/", views.module_detail, name="module_detail"),
    path("lesson/<slug:slug>/", views.lesson_detail, name="lesson_detail"),
]
from django.urls import path

from quizzes import views

app_name = "quizzes"

urlpatterns = [
    path("", views.quiz_list, name="list"),
    path("quiz/<int:pk>/", views.quiz_detail, name="detail"),
    path("quiz/<int:pk>/take/", views.quiz_take, name="take"),
    path("attempt/<int:attempt_id>/result/", views.quiz_result, name="result"),
]
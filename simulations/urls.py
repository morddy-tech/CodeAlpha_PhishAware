from django.urls import path

from simulations import views

app_name = "simulations"

urlpatterns = [
    path("", views.scenario_list, name="list"),
    path("scenario/<int:pk>/", views.scenario_detail, name="scenario_detail"),
    path("scenario/<int:pk>/submit/", views.scenario_submit, name="scenario_submit"),
]
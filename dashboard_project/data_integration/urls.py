from django.urls import path

from . import views

app_name = "data_integration"

urlpatterns = [
    path("manual-refresh/", views.manual_data_refresh, name="manual_data_refresh"),
    path(
        "refresh/<int:source_id>/",
        views.refresh_specific_datasource,
        name="refresh_specific_datasource",
    ),
]

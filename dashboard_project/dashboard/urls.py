# dashboard/urls.py

from django.urls import path

from . import views

urlpatterns = [
    path("", views.dashboard_view, name="dashboard"),
    path("upload/", views.upload_data_view, name="upload_data"),
    path(
        "data-source/<int:data_source_id>/",
        views.data_source_detail_view,
        name="data_source_detail",
    ),
    path(
        "chat-session/<str:session_id>/",
        views.chat_session_detail_view,
        name="chat_session_detail",
    ),
    path("dashboard/create/", views.create_dashboard_view, name="create_dashboard"),
    path(
        "dashboard/<int:dashboard_id>/edit/",
        views.edit_dashboard_view,
        name="edit_dashboard",
    ),
    path(
        "dashboard/<int:dashboard_id>/delete/",
        views.delete_dashboard_view,
        name="delete_dashboard",
    ),
    path(
        "data-source/<int:data_source_id>/delete/",
        views.delete_data_source_view,
        name="delete_data_source",
    ),
    path(
        "api/dashboard/<int:dashboard_id>/data/",
        views.dashboard_data_api,
        name="dashboard_data_api",
    ),
    path("search/", views.search_chat_sessions, name="search_chat_sessions"),
    path("data-view/", views.data_view, name="data_view"),
]

# accounts/urls.py

from allauth.account import views as allauth_views
from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="accounts/login.html"),
        name="login",
    ),
    path("logout/", allauth_views.LogoutView.as_view(), name="logout"),  # Use allauth logout view
    path("register/", views.register_view, name="register"),
    path("profile/", views.profile_view, name="profile"),
    path(
        "password_change/",
        auth_views.PasswordChangeView.as_view(template_name="accounts/password_change.html"),
        name="password_change",
    ),
    path(
        "password_change/done/",
        auth_views.PasswordChangeDoneView.as_view(template_name="accounts/password_change_done.html"),
        name="password_change_done",
    ),
]

# dashboard_project/urls.py

from data_integration.views import refresh_specific_datasource
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    # Additional admin URLs should come BEFORE admin.site.urls
    path(
        "admin/data_integration/externaldatasource/refresh/<int:source_id>/",
        refresh_specific_datasource,
        name="admin_refresh_datasource",
    ),
    # Alternative URL pattern for direct access
    path(
        "admin/data_integration/refresh/<int:source_id>/",
        refresh_specific_datasource,
        name="admin_refresh_datasource_alt",
    ),
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("dashboard/", include("dashboard.urls")),
    path("", RedirectView.as_view(url="dashboard/", permanent=False)),
    path("data/", include("data_integration.urls", namespace="data_integration")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

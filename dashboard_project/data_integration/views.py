from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect
from django.utils.http import url_has_allowed_host_and_scheme

from .models import ExternalDataSource
from .tasks import periodic_fetch_chat_data, refresh_specific_source
from .utils import fetch_and_store_chat_data

# Create your views here.


def is_superuser(user):
    return user.is_superuser


@login_required
@user_passes_test(is_superuser)
def manual_data_refresh(request):
    if request.method == "POST":
        try:
            # Try to use Celery first
            try:
                # Asynchronous with Celery
                periodic_fetch_chat_data.delay()
                messages.success(
                    request,
                    "Manual data refresh triggered successfully. The data will be updated shortly.",
                )
            except Exception:
                # Fall back to synchronous if Celery is not available
                fetch_and_store_chat_data()
                messages.success(
                    request,
                    "Manual data refresh completed successfully (synchronous mode).",
                )
        except Exception as e:
            messages.error(request, f"Failed to refresh data: {e}")
    referer = request.headers.get("referer", "")
    if url_has_allowed_host_and_scheme(referer, allowed_hosts=None):
        return redirect(referer)
    return redirect("dashboard")  # Redirect to a safe default


@staff_member_required
def refresh_specific_datasource(request, source_id):
    """View to trigger refresh of a specific data source. Used as a backup for admin URLs."""
    source = get_object_or_404(ExternalDataSource, pk=source_id)

    try:
        # Try to use Celery
        task = refresh_specific_source.delay(source_id)
        messages.success(request, f"Data refresh task started for {source.name} (Task ID: {task.id})")
    except Exception as e:
        messages.error(request, f"Failed to refresh data source {source.name}: {e}")

    referer = request.headers.get("referer", "")
    if url_has_allowed_host_and_scheme(referer, allowed_hosts=None):
        return redirect(referer)
    return redirect("/admin/data_integration/externaldatasource/")  # Redirect to a safe default

# dashboard/views.py

import json
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Avg, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.utils import timezone

from .forms import DashboardForm, DataSourceUploadForm
from .models import ChatSession, Dashboard, DataSource
from .utils import generate_dashboard_data, process_csv_file


def is_ajax_navigation(request):
    """Check if this is an AJAX navigation request"""
    return request.headers.get("X-AJAX-Navigation") == "true"


@login_required
def dashboard_view(request):
    """Main dashboard view"""
    user = request.user
    company = user.company

    if not company:
        messages.warning(
            request,
            "You are not associated with any company. Please contact an administrator.",
        )
        return render(request, "dashboard/no_company.html")

    # Get the user's dashboards or create a default one
    dashboards = Dashboard.objects.filter(company=company)

    if not dashboards.exists():
        # Create a default dashboard if none exists
        data_sources = DataSource.objects.filter(company=company)
        if data_sources.exists():
            default_dashboard = Dashboard.objects.create(
                name="Default Dashboard",
                description="Automatically created dashboard",
                company=company,
            )
            default_dashboard.data_sources.set(data_sources)
            dashboards = [default_dashboard]
        else:
            # No data sources available
            return redirect("upload_data")

    # Use the first dashboard by default or the one specified in the request
    selected_dashboard_id = request.GET.get("dashboard_id")
    if selected_dashboard_id:
        selected_dashboard = get_object_or_404(Dashboard, id=selected_dashboard_id, company=company)
    else:
        selected_dashboard = dashboards.first()

    # Generate dashboard data
    dashboard_data = generate_dashboard_data(selected_dashboard.data_sources.all())

    # Convert each component of dashboard data to JSON
    sentiment_data_json = json.dumps(dashboard_data["sentiment_data"])
    country_data_json = json.dumps(dashboard_data["country_data"])
    category_data_json = json.dumps(dashboard_data["category_data"])
    time_series_data_json = json.dumps(dashboard_data["time_series_data"])

    context = {
        "dashboards": dashboards,
        "selected_dashboard": selected_dashboard,
        "dashboard_data": dashboard_data,
        "sentiment_data_json": sentiment_data_json,
        "country_data_json": country_data_json,
        "category_data_json": category_data_json,
        "time_series_data_json": time_series_data_json,
    }

    # Check if this is an AJAX navigation request
    if is_ajax_navigation(request):
        html_content = render_to_string("dashboard/dashboard.html", context, request=request)
        return JsonResponse({"html": html_content, "title": "Dashboard | Chat Analytics"})

    return render(request, "dashboard/dashboard.html", context)


@login_required
def upload_data_view(request):
    """View for uploading CSV files"""
    user = request.user
    company = user.company

    if not company:
        messages.warning(
            request,
            "You are not associated with any company. Please contact an administrator.",
        )
        return redirect("dashboard")

    if request.method == "POST":
        form = DataSourceUploadForm(request.POST, request.FILES, company=company)
        if form.is_valid():
            data_source = form.save()

            # Process the uploaded CSV file
            success, message = process_csv_file(data_source)

            if success:
                messages.success(request, f"File uploaded successfully. {message}")

                # Add the new data source to all existing dashboards
                dashboards = Dashboard.objects.filter(company=company)
                for dashboard in dashboards:
                    dashboard.data_sources.add(data_source)

                return redirect("dashboard")
            else:
                # If processing failed, delete the data source
                data_source.delete()
                messages.error(request, message)
        else:
            messages.error(request, "Form is invalid. Please correct the errors.")
    else:
        form = DataSourceUploadForm()

    # List existing data sources
    data_sources = DataSource.objects.filter(company=company).order_by("-uploaded_at")

    context = {
        "form": form,
        "data_sources": data_sources,
    }

    # Check if this is an AJAX navigation request
    if is_ajax_navigation(request):
        html_content = render_to_string("dashboard/upload.html", context, request=request)
        return JsonResponse({"html": html_content, "title": "Upload Data | Chat Analytics"})

    return render(request, "dashboard/upload.html", context)


@login_required
def data_source_detail_view(request, data_source_id):
    """View for viewing details of a data source"""
    user = request.user
    company = user.company

    if not company:
        messages.warning(
            request,
            "You are not associated with any company. Please contact an administrator.",
        )
        return redirect("dashboard")

    data_source = get_object_or_404(DataSource, id=data_source_id, company=company)

    # Get all chat sessions for this data source
    chat_sessions = ChatSession.objects.filter(data_source=data_source).order_by("-start_time")

    # Pagination
    paginator = Paginator(chat_sessions, 20)  # Show 20 records per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "data_source": data_source,
        "page_obj": page_obj,
    }

    # Check if this is an AJAX navigation request
    if is_ajax_navigation(request):
        html_content = render_to_string("dashboard/data_source_detail.html", context, request=request)
        return JsonResponse({"html": html_content, "title": f"{data_source.name} | Chat Analytics"})

    return render(request, "dashboard/data_source_detail.html", context)


@login_required
def chat_session_detail_view(request, session_id):
    """View for viewing details of a chat session"""
    user = request.user
    company = user.company

    if not company:
        messages.warning(
            request,
            "You are not associated with any company. Please contact an administrator.",
        )
        return redirect("dashboard")

    chat_session = get_object_or_404(ChatSession, session_id=session_id, data_source__company=company)

    context = {
        "session": chat_session,
    }

    # Check if this is an AJAX navigation request
    if is_ajax_navigation(request):
        html_content = render_to_string("dashboard/chat_session_detail.html", context, request=request)
        return JsonResponse(
            {
                "html": html_content,
                "title": f"Chat Session {session_id} | Chat Analytics",
            }
        )

    return render(request, "dashboard/chat_session_detail.html", context)


@login_required
def create_dashboard_view(request):
    """View for creating a custom dashboard"""
    user = request.user
    company = user.company

    if not company:
        messages.warning(
            request,
            "You are not associated with any company. Please contact an administrator.",
        )
        return redirect("dashboard")

    if request.method == "POST":
        form = DashboardForm(request.POST, company=company)
        if form.is_valid():
            dashboard = form.save()
            messages.success(request, f"Dashboard '{dashboard.name}' created successfully.")
            return redirect("dashboard")
        else:
            messages.error(request, "Failed to create dashboard. Please correct the errors.")
    else:
        form = DashboardForm(company=company)

    context = {
        "form": form,
        "is_create": True,
    }

    # Check if this is an AJAX navigation request
    if is_ajax_navigation(request):
        html_content = render_to_string("dashboard/dashboard_form.html", context, request=request)
        return JsonResponse({"html": html_content, "title": "Create Dashboard | Chat Analytics"})

    return render(request, "dashboard/dashboard_form.html", context)


@login_required
def edit_dashboard_view(request, dashboard_id):
    """View for editing a dashboard"""
    user = request.user
    company = user.company

    if not company:
        messages.warning(
            request,
            "You are not associated with any company. Please contact an administrator.",
        )
        return redirect("dashboard")

    dashboard = get_object_or_404(Dashboard, id=dashboard_id, company=company)

    if request.method == "POST":
        form = DashboardForm(request.POST, instance=dashboard, company=company)
        if form.is_valid():
            dashboard = form.save()
            messages.success(request, f"Dashboard '{dashboard.name}' updated successfully.")
            return redirect("dashboard")
        else:
            messages.error(request, "Failed to update dashboard. Please correct the errors.")
    else:
        form = DashboardForm(instance=dashboard, company=company)

    context = {
        "form": form,
        "dashboard": dashboard,
        "is_create": False,
    }

    # Check if this is an AJAX navigation request
    if is_ajax_navigation(request):
        html_content = render_to_string("dashboard/dashboard_form.html", context, request=request)
        return JsonResponse(
            {
                "html": html_content,
                "title": f"Edit Dashboard: {dashboard.name} | Chat Analytics",
            }
        )

    return render(request, "dashboard/dashboard_form.html", context)


@login_required
def delete_dashboard_view(request, dashboard_id):
    """View for deleting a dashboard"""
    user = request.user
    company = user.company

    if not company:
        messages.warning(
            request,
            "You are not associated with any company. Please contact an administrator.",
        )
        return redirect("dashboard")

    dashboard = get_object_or_404(Dashboard, id=dashboard_id, company=company)

    if request.method == "POST":
        dashboard_name = dashboard.name
        dashboard.delete()
        messages.success(request, f"Dashboard '{dashboard_name}' deleted successfully.")
        return redirect("dashboard")

    context = {
        "dashboard": dashboard,
    }

    return render(request, "dashboard/dashboard_confirm_delete.html", context)


@login_required
def delete_data_source_view(request, data_source_id):
    """View for deleting a data source"""
    user = request.user
    company = user.company

    if not company:
        messages.warning(
            request,
            "You are not associated with any company. Please contact an administrator.",
        )
        return redirect("dashboard")

    data_source = get_object_or_404(DataSource, id=data_source_id, company=company)

    if request.method == "POST":
        data_source_name = data_source.name
        data_source.delete()
        messages.success(request, f"Data source '{data_source_name}' deleted successfully.")
        return redirect("upload_data")

    context = {
        "data_source": data_source,
    }

    return render(request, "dashboard/data_source_confirm_delete.html", context)


# API views for dashboard data
@login_required
def dashboard_data_api(request, dashboard_id):
    """API endpoint for dashboard data"""
    user = request.user
    company = user.company

    if not company:
        return JsonResponse({"error": "User not associated with a company"}, status=403)

    # Get time range filter if provided
    time_range = request.GET.get("time_range", "all")

    dashboard = get_object_or_404(Dashboard, id=dashboard_id, company=company)

    # Get data sources for this dashboard
    data_sources = dashboard.data_sources.all()

    # Apply time filter if needed
    filtered_data_sources = data_sources
    if time_range and time_range != "all":
        # This is a placeholder comment - implement time filtering in a real app
        # You would filter ChatSessions based on time_range here
        pass

    # Generate the dashboard data
    dashboard_data = generate_dashboard_data(filtered_data_sources)

    # Ensure values are JSON serializable
    for key in ["sentiment_data", "country_data", "category_data"]:
        dashboard_data[key] = list(dashboard_data[key])

    # Format time series data for proper date serialization
    if "time_series_data" in dashboard_data:
        for item in dashboard_data["time_series_data"]:
            if "date" in item and not isinstance(item["date"], str):
                item["date"] = item["date"].strftime("%Y-%m-%d")

    return JsonResponse(dashboard_data)


@login_required
def search_chat_sessions(request):
    """View for searching chat sessions"""
    user = request.user
    company = user.company

    if not company:
        messages.warning(
            request,
            "You are not associated with any company. Please contact an administrator.",
        )
        return redirect("dashboard")

    query = request.GET.get("q", "")
    data_source_id = request.GET.get("data_source_id")

    # Base queryset
    chat_sessions = ChatSession.objects.filter(data_source__company=company)

    # Filter by data source if provided
    if data_source_id:
        chat_sessions = chat_sessions.filter(data_source_id=data_source_id)

    # Apply search query if provided
    if query:
        chat_sessions = chat_sessions.filter(
            Q(session_id__icontains=query)
            | Q(country__icontains=query)
            | Q(language__icontains=query)
            | Q(sentiment__icontains=query)
            | Q(category__icontains=query)
            | Q(initial_msg__icontains=query)
            | Q(full_transcript__icontains=query)
        )

    # Order by most recent first
    chat_sessions = chat_sessions.order_by("-start_time")

    # Pagination
    paginator = Paginator(chat_sessions, 20)  # Show 20 records per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Get data source for context if filtered by data source
    data_source = None
    if data_source_id:
        data_source = get_object_or_404(DataSource, id=data_source_id, company=company)

    context = {
        "query": query,
        "page_obj": page_obj,
        "data_source": data_source,
    }

    # Check if this is an AJAX navigation request
    if is_ajax_navigation(request):
        html_content = render_to_string("dashboard/search_results.html", context, request=request)
        return JsonResponse({"html": html_content, "title": "Search Chat Sessions | Chat Analytics"})

    # Check if this is an AJAX pagination request
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse(
            {
                "status": "success",
                "html_data": render(request, "dashboard/partials/search_results_table.html", context).content.decode(
                    "utf-8"
                ),
                "page_obj": {
                    "number": page_obj.number,
                    "has_previous": page_obj.has_previous(),
                    "has_next": page_obj.has_next(),
                    "previous_page_number": page_obj.previous_page_number() if page_obj.has_previous() else None,
                    "next_page_number": page_obj.next_page_number() if page_obj.has_next() else None,
                    "paginator": {
                        "num_pages": page_obj.paginator.num_pages,
                        "count": page_obj.paginator.count,
                    },
                },
                "query": query,
            }
        )

    return render(request, "dashboard/search_results.html", context)


@login_required
def data_view(request):
    """View for viewing all data with filtering options"""
    user = request.user
    company = user.company

    if not company:
        messages.warning(
            request,
            "You are not associated with any company. Please contact an administrator.",
        )
        return redirect("dashboard")

    # Get available data sources
    data_sources = DataSource.objects.filter(company=company)

    # Get selected data source if any
    data_source_id = request.GET.get("data_source_id")
    selected_data_source = None
    if data_source_id:
        selected_data_source = get_object_or_404(DataSource, id=data_source_id, company=company)

    # Base queryset
    chat_sessions = ChatSession.objects.filter(data_source__company=company)

    # Apply data source filter if selected
    if selected_data_source:
        chat_sessions = chat_sessions.filter(data_source=selected_data_source)

    # Apply view filter if any
    view = request.GET.get("view", "all")

    if view == "recent":
        # Sessions from the last 7 days
        seven_days_ago = timezone.now() - timedelta(days=7)
        chat_sessions = chat_sessions.filter(start_time__gte=seven_days_ago)
    elif view == "positive":
        # Sessions with positive sentiment
        chat_sessions = chat_sessions.filter(Q(sentiment__icontains="positive"))
    elif view == "negative":
        # Sessions with negative sentiment
        chat_sessions = chat_sessions.filter(Q(sentiment__icontains="negative"))
    elif view == "escalated":
        # Escalated sessions
        chat_sessions = chat_sessions.filter(escalated=True)

    # Order by most recent first
    chat_sessions = chat_sessions.order_by("-start_time")

    # Calculate some statistics
    total_sessions = chat_sessions.count()
    avg_response_time = (
        chat_sessions.filter(avg_response_time__isnull=False).aggregate(avg=Avg("avg_response_time"))["avg"] or 0
    )
    avg_messages = chat_sessions.filter(messages_sent__gt=0).aggregate(avg=Avg("messages_sent"))["avg"] or 0
    escalated_count = chat_sessions.filter(escalated=True).count()
    escalation_rate = (escalated_count / total_sessions * 100) if total_sessions > 0 else 0

    # Pagination
    paginator = Paginator(chat_sessions, 20)  # Show 20 records per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "data_sources": data_sources,
        "selected_data_source": selected_data_source,
        "page_obj": page_obj,
        "view": view,
        "avg_response_time": avg_response_time,
        "avg_messages": avg_messages,
        "escalation_rate": escalation_rate,
    }

    # Check if this is an AJAX navigation request
    if is_ajax_navigation(request):
        html_content = render_to_string("dashboard/data_view.html", context, request=request)
        return JsonResponse({"html": html_content, "title": "Data View | Chat Analytics"})

    # Check if this is an AJAX pagination request
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse(
            {
                "status": "success",
                "html_data": render(request, "dashboard/partials/data_table.html", context).content.decode("utf-8"),
                "page_obj": {
                    "number": page_obj.number,
                    "has_previous": page_obj.has_previous(),
                    "has_next": page_obj.has_next(),
                    "previous_page_number": page_obj.previous_page_number() if page_obj.has_previous() else None,
                    "next_page_number": page_obj.next_page_number() if page_obj.has_next() else None,
                    "paginator": {
                        "num_pages": page_obj.paginator.num_pages,
                        "count": page_obj.paginator.count,
                    },
                },
                "view": view,
                "avg_response_time": avg_response_time,
                "avg_messages": avg_messages,
                "escalation_rate": escalation_rate,
            }
        )

    return render(request, "dashboard/data_view.html", context)

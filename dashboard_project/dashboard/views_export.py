# dashboard/views_export.py

import csv
from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import ChatSession, Dashboard, DataSource


@login_required
def export_chats_csv(request):
    """Export chat sessions to CSV with filtering options"""
    user = request.user
    company = user.company

    if not company:
        return HttpResponse("You are not associated with any company.", status=403)

    # Get and apply filters
    data_source_id = request.GET.get("data_source_id")
    dashboard_id = request.GET.get("dashboard_id")
    view = request.GET.get("view", "all")
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")
    country = request.GET.get("country")
    sentiment = request.GET.get("sentiment")
    escalated = request.GET.get("escalated")

    # Base queryset
    sessions = ChatSession.objects.filter(data_source__company=company)

    # Apply data source filter if selected
    if data_source_id:
        data_source = get_object_or_404(DataSource, id=data_source_id, company=company)
        sessions = sessions.filter(data_source=data_source)

    # Apply dashboard filter if selected
    if dashboard_id:
        dashboard = get_object_or_404(Dashboard, id=dashboard_id, company=company)
        data_sources = dashboard.data_sources.all()
        sessions = sessions.filter(data_source__in=data_sources)

    # Apply view filter
    if view == "recent":
        seven_days_ago = timezone.now() - timedelta(days=7)
        sessions = sessions.filter(start_time__gte=seven_days_ago)
    elif view == "positive":
        sessions = sessions.filter(Q(sentiment__icontains="positive"))
    elif view == "negative":
        sessions = sessions.filter(Q(sentiment__icontains="negative"))
    elif view == "escalated":
        sessions = sessions.filter(escalated=True)

    # Apply additional filters
    if start_date:
        sessions = sessions.filter(start_time__date__gte=start_date)
    if end_date:
        sessions = sessions.filter(start_time__date__lte=end_date)
    if country:
        sessions = sessions.filter(country__icontains=country)
    if sentiment:
        sessions = sessions.filter(sentiment__icontains=sentiment)
    if escalated:
        escalated_val = escalated.lower() == "true"
        sessions = sessions.filter(escalated=escalated_val)

    # Order by most recent first
    sessions = sessions.order_by("-start_time")

    # Create the HttpResponse with CSV header
    filename = "chat_sessions"
    if dashboard_id:
        dashboard = Dashboard.objects.get(id=dashboard_id)
        filename = f"{dashboard.name.replace(' ', '_').lower()}_chat_sessions"
    elif data_source_id:
        data_source = DataSource.objects.get(id=data_source_id)
        filename = f"{data_source.name.replace(' ', '_').lower()}_chat_sessions"

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="{filename}.csv"'

    # Create CSV writer
    writer = csv.writer(response)

    # Write CSV header
    writer.writerow(
        [
            "Session ID",
            "Start Time",
            "End Time",
            "IP Address",
            "Country",
            "Language",
            "Messages Sent",
            "Sentiment",
            "Escalated",
            "Forwarded HR",
            "Full Transcript",
            "Avg Response Time (s)",
            "Tokens",
            "Tokens EUR",
            "Category",
            "Initial Message",
            "User Rating",
        ]
    )

    # Write data rows
    for session in sessions:
        writer.writerow(
            [
                session.session_id,
                session.start_time,
                session.end_time,
                session.ip_address,
                session.country,
                session.language,
                session.messages_sent,
                session.sentiment,
                "Yes" if session.escalated else "No",
                "Yes" if session.forwarded_hr else "No",
                session.full_transcript,
                session.avg_response_time,
                session.tokens,
                session.tokens_eur,
                session.category,
                session.initial_msg,
                session.user_rating,
            ]
        )

    return response

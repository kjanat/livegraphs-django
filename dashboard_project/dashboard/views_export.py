# dashboard/views_export.py

import csv
import io
import json
from datetime import timedelta

import xlsxwriter
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


@login_required
def export_chats_json(request):
    """Export chat sessions to JSON with filtering options"""
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

    # Create the filename
    filename = "chat_sessions"
    if dashboard_id:
        dashboard = Dashboard.objects.get(id=dashboard_id)
        filename = f"{dashboard.name.replace(' ', '_').lower()}_chat_sessions"
    elif data_source_id:
        data_source = DataSource.objects.get(id=data_source_id)
        filename = f"{data_source.name.replace(' ', '_').lower()}_chat_sessions"

    # Add company name, date, and timestamp to the filename
    current_time = timezone.now().strftime("%Y%m%d_%H%M%S")
    company_name = company.name.replace(" ", "_").lower()
    filename = f"{company_name}_{filename}_{current_time}"

    # Prepare the data for JSON export using list comprehension
    data = [
        {
            "session_id": session.session_id,
            "start_time": (session.start_time.isoformat() if session.start_time else None),
            "end_time": session.end_time.isoformat() if session.end_time else None,
            "ip_address": session.ip_address,
            "country": session.country,
            "language": session.language,
            "messages_sent": session.messages_sent,
            "sentiment": session.sentiment,
            "escalated": session.escalated,
            "forwarded_hr": session.forwarded_hr,
            "full_transcript": session.full_transcript,
            "avg_response_time": session.avg_response_time,
            "tokens": session.tokens,
            "tokens_eur": session.tokens_eur,
            "category": session.category,
            "initial_msg": session.initial_msg,
            "user_rating": session.user_rating,
        }
        for session in sessions
    ]

    # Create the HttpResponse with JSON header
    response = HttpResponse(content_type="application/json")
    response["Content-Disposition"] = f'attachment; filename="{filename}.json"'

    # Add company and timestamp to the exported JSON
    current_time = timezone.now().isoformat()
    export_data = {
        "company": company.name,
        "export_date": current_time,
        "export_type": "chat_sessions",
        "data": data,
    }

    # Write JSON data to the response
    json.dump(export_data, response, indent=2)

    return response


@login_required
def export_chats_excel(request):
    """Export chat sessions to Excel with filtering options"""
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

    # Create the filename
    filename = "chat_sessions"
    if dashboard_id:
        dashboard = Dashboard.objects.get(id=dashboard_id)
        filename = f"{dashboard.name.replace(' ', '_').lower()}_chat_sessions"
    elif data_source_id:
        data_source = DataSource.objects.get(id=data_source_id)
        filename = f"{data_source.name.replace(' ', '_').lower()}_chat_sessions"

    # Add company name, date, and timestamp to the filename
    current_time = timezone.now().strftime("%Y%m%d_%H%M%S")
    company_name = company.name.replace(" ", "_").lower()
    filename = f"{company_name}_{filename}_{current_time}"

    # Create in-memory output file
    output = io.BytesIO()

    # Create Excel workbook and worksheet
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet("Chat Sessions")

    # Add a bold format to use to highlight cells
    bold = workbook.add_format({"bold": True, "bg_color": "#D9EAD3"})
    date_format = workbook.add_format({"num_format": "yyyy-mm-dd hh:mm:ss"})

    # Write header row with formatting
    headers = [
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

    for col, header in enumerate(headers):
        worksheet.write(0, col, header, bold)

    # Write data rows
    for row_num, session in enumerate(sessions, 1):
        worksheet.write(row_num, 0, session.session_id)
        # Write dates with proper formatting if not None
        if session.start_time:
            worksheet.write_datetime(row_num, 1, session.start_time, date_format)
        else:
            worksheet.write(row_num, 1, None)

        if session.end_time:
            worksheet.write_datetime(row_num, 2, session.end_time, date_format)
        else:
            worksheet.write(row_num, 2, None)

        worksheet.write(row_num, 3, session.ip_address)
        worksheet.write(row_num, 4, session.country)
        worksheet.write(row_num, 5, session.language)
        worksheet.write(row_num, 6, session.messages_sent)
        worksheet.write(row_num, 7, session.sentiment)
        worksheet.write(row_num, 8, "Yes" if session.escalated else "No")
        worksheet.write(row_num, 9, "Yes" if session.forwarded_hr else "No")
        worksheet.write(row_num, 10, session.full_transcript)
        worksheet.write(row_num, 11, session.avg_response_time)
        worksheet.write(row_num, 12, session.tokens)
        worksheet.write(row_num, 13, session.tokens_eur)
        worksheet.write(row_num, 14, session.category)
        worksheet.write(row_num, 15, session.initial_msg)
        worksheet.write(row_num, 16, session.user_rating)

    # Add summary sheet with metadata
    summary = workbook.add_worksheet("Summary")
    summary.write(0, 0, "Export Information", bold)
    summary.write(1, 0, "Company:", bold)
    summary.write(1, 1, company.name)
    summary.write(2, 0, "Export Date:", bold)
    summary.write(2, 1, timezone.now().strftime("%Y-%m-%d %H:%M:%S"))
    summary.write(3, 0, "Total Records:", bold)
    summary.write(3, 1, len(sessions))

    # Add filters if used
    filter_row = 5
    summary.write(filter_row, 0, "Filters Applied:", bold)
    filter_row += 1

    if data_source_id:
        data_source = DataSource.objects.get(id=data_source_id)
        summary.write(filter_row, 0, "Data Source:")
        summary.write(filter_row, 1, data_source.name)
        filter_row += 1

    if dashboard_id:
        dashboard = Dashboard.objects.get(id=dashboard_id)
        summary.write(filter_row, 0, "Dashboard:")
        summary.write(filter_row, 1, dashboard.name)
        filter_row += 1

    if view != "all":
        summary.write(filter_row, 0, "View:")
        summary.write(filter_row, 1, view.title())
        filter_row += 1

    # Auto-adjust column widths for better readability
    for i, width in enumerate([20, 20, 20, 15, 15, 10, 12, 15, 10, 12, 30, 15, 10, 10, 20, 50, 10]):
        worksheet.set_column(i, i, width)

    # Close the workbook
    workbook.close()

    # Set up the response
    output.seek(0)
    response = HttpResponse(output, content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = f'attachment; filename="{filename}.xlsx"'

    return response

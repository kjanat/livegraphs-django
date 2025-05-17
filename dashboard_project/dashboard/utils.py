# dashboard/utils.py

import contextlib

import numpy as np
import pandas as pd
from django.db import models
from django.utils.timezone import make_aware

from .models import ChatSession


def process_csv_file(data_source):
    """
    Process the uploaded CSV file and create ChatSession objects

    Args:
        data_source: DataSource model instance containing the CSV file
    """
    try:
        # Read the CSV file
        file_path = data_source.file.path
        df = pd.read_csv(file_path)

        # Process each row and create ChatSession objects
        for _, row in df.iterrows():
            # Handle datetime fields
            start_time = None
            end_time = None
            if "start_time" in row and pd.notna(row["start_time"]):
                with contextlib.suppress(Exception):
                    start_time = make_aware(pd.to_datetime(row["start_time"]))

            if "end_time" in row and pd.notna(row["end_time"]):
                with contextlib.suppress(Exception):
                    end_time = make_aware(pd.to_datetime(row["end_time"]))
                    pass

            # Convert boolean fields
            escalated = str(row.get("escalated", "")).lower() in [
                "true",
                "yes",
                "1",
                "t",
                "y",
            ]
            forwarded_hr = str(row.get("forwarded_hr", "")).lower() in [
                "true",
                "yes",
                "1",
                "t",
                "y",
            ]

            # Create ChatSession object
            session = ChatSession(
                data_source=data_source,
                session_id=str(row.get("session_id", "")),
                start_time=start_time,
                end_time=end_time,
                ip_address=row.get("ip_address") if pd.notna(row.get("ip_address", np.nan)) else None,
                country=str(row.get("country", "")),
                language=str(row.get("language", "")),
                messages_sent=int(row.get("messages_sent", 0)) if pd.notna(row.get("messages_sent", np.nan)) else 0,
                sentiment=str(row.get("sentiment", "")),
                escalated=escalated,
                forwarded_hr=forwarded_hr,
                full_transcript=str(row.get("full_transcript", "")),
                avg_response_time=float(row.get("avg_response_time", 0))
                if pd.notna(row.get("avg_response_time", np.nan))
                else None,
                tokens=int(row.get("tokens", 0)) if pd.notna(row.get("tokens", np.nan)) else 0,
                tokens_eur=float(row.get("tokens_eur", 0)) if pd.notna(row.get("tokens_eur", np.nan)) else None,
                category=str(row.get("category", "")),
                initial_msg=str(row.get("initial_msg", "")),
                user_rating=str(row.get("user_rating", "")),
            )
            session.save()

        return True, f"Successfully processed {len(df)} records."

    except Exception as e:
        return False, f"Error processing CSV file: {str(e)}"


def generate_dashboard_data(data_sources):
    """
    Generate aggregated data for dashboard visualization

    Args:
        data_sources: QuerySet of DataSource objects

    Returns:
        dict: Dictionary containing aggregated data for various charts
    """
    # Get all chat sessions for the selected data sources
    chat_sessions = ChatSession.objects.filter(data_source__in=data_sources)

    if not chat_sessions.exists():
        return {
            "total_sessions": 0,
            "avg_response_time": 0,
            "total_tokens": 0,
            "total_cost": 0,
            "sentiment_data": [],
            "country_data": [],
            "category_data": [],
            "time_series_data": [],
        }

    # Basic statistics
    total_sessions = chat_sessions.count()
    avg_response_time = (
        chat_sessions.filter(avg_response_time__isnull=False).aggregate(avg=models.Avg("avg_response_time"))["avg"] or 0
    )
    total_tokens = chat_sessions.aggregate(sum=models.Sum("tokens"))["sum"] or 0
    total_cost = chat_sessions.filter(tokens_eur__isnull=False).aggregate(sum=models.Sum("tokens_eur"))["sum"] or 0

    # Sentiment distribution
    sentiment_data = (
        chat_sessions.exclude(sentiment="").values("sentiment").annotate(count=models.Count("id")).order_by("-count")
    )

    # Country distribution
    country_data = (
        chat_sessions.exclude(country="")
        .values("country")
        .annotate(count=models.Count("id"))
        .order_by("-count")[:10]  # Top 10 countries
    )

    # Category distribution
    category_data = (
        chat_sessions.exclude(category="").values("category").annotate(count=models.Count("id")).order_by("-count")
    )

    # Time series data (sessions per day)
    time_series_query = (
        chat_sessions.filter(start_time__isnull=False)
        .annotate(date=models.functions.TruncDate("start_time"))
        .values("date")
        .annotate(count=models.Count("id"))
        .order_by("date")
    )

    time_series_data = [
        {"date": entry["date"].strftime("%Y-%m-%d"), "count": entry["count"]} for entry in time_series_query
    ]

    return {
        "total_sessions": total_sessions,
        "avg_response_time": round(avg_response_time, 2),
        "total_tokens": total_tokens,
        "total_cost": round(total_cost, 2),
        "sentiment_data": list(sentiment_data),
        "country_data": list(country_data),
        "category_data": list(category_data),
        "time_series_data": time_series_data,
    }

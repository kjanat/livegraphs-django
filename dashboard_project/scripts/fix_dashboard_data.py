#!/usr/bin/env python
# scripts/fix_dashboard_data.py

import os
import sys
from datetime import datetime

import django
from accounts.models import Company
from dashboard.models import ChatSession as DashboardChatSession
from dashboard.models import DataSource
from data_integration.models import ChatSession as ExternalChatSession
from data_integration.models import ExternalDataSource
from django.db import transaction
from django.utils.timezone import make_aware

# Set up Django environment
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dashboard_project.settings")
django.setup()

# SCRIPT CONFIG
CREATE_TEST_DATA = False  # Set to True to create sample data if none exists
COMPANY_NAME = "Notso AI"  # The company name to use


def main():
    print("Starting dashboard data fix...")

    # Get company
    company = Company.objects.filter(name=COMPANY_NAME).first()
    if not company:
        print(f"Error: Company '{COMPANY_NAME}' not found.")
        print("Available companies:")
        for c in Company.objects.all():
            print(f" - {c.name} (ID: {c.id})")
        return

    print(f"Using company: {company.name} (ID: {company.id})")

    # Get or create external data source
    ext_source, created = ExternalDataSource.objects.get_or_create(
        name="External API Data",
        defaults={
            "api_url": "https://proto.notso.ai/jumbo/chats",
            "is_active": True,
            "sync_interval": 3600,
            "last_synced": make_aware(datetime.now()),
        },
    )

    if created:
        print(f"Created external data source: {ext_source.name} (ID: {ext_source.id})")
    else:
        print(f"Using existing external data source: {ext_source.name} (ID: {ext_source.id})")

    # Get or create dashboard data source linked to external source
    dash_source, created = DataSource.objects.get_or_create(
        external_source=ext_source,
        company=company,
        defaults={
            "name": "External API Data",
            "description": "External data source for chat analytics",
        },
    )

    if created:
        print(f"Created dashboard data source: {dash_source.name} (ID: {dash_source.id})")
    else:
        print(f"Using existing dashboard data source: {dash_source.name} (ID: {dash_source.id})")

    # Check for external chat sessions
    ext_count = ExternalChatSession.objects.count()
    print(f"Found {ext_count} external chat sessions")

    if ext_count == 0 and CREATE_TEST_DATA:
        print("No external chat sessions found. Creating test data...")
        create_test_data(ext_source)

    # Sync data from external to dashboard
    sync_data(ext_source, dash_source)

    print("Done! Check your dashboard for data.")


def create_test_data(ext_source):
    """Create sample chat sessions in the external data source"""
    sessions_created = 0

    # Create test data with association to the external data source
    test_data = [
        {
            "session_id": "test-session-1",
            "start_time": make_aware(datetime.strptime("01.05.2025 10:00:00", "%d.%m.%Y %H:%M:%S")),
            "end_time": make_aware(datetime.strptime("01.05.2025 10:15:00", "%d.%m.%Y %H:%M:%S")),
            "country": "Netherlands",
            "language": "Dutch",
            "messages_sent": 10,
            "sentiment": "Positive",
            "initial_msg": "Can you help me with my order?",
        },
        {
            "session_id": "test-session-2",
            "start_time": make_aware(datetime.strptime("02.05.2025 14:30:00", "%d.%m.%Y %H:%M:%S")),
            "end_time": make_aware(datetime.strptime("02.05.2025 14:45:00", "%d.%m.%Y %H:%M:%S")),
            "country": "Belgium",
            "language": "French",
            "messages_sent": 12,
            "sentiment": "Neutral",
            "initial_msg": "Je cherche des informations sur les produits.",
        },
        {
            "session_id": "test-session-3",
            "start_time": make_aware(datetime.strptime("03.05.2025 09:15:00", "%d.%m.%Y %H:%M:%S")),
            "end_time": make_aware(datetime.strptime("03.05.2025 09:30:00", "%d.%m.%Y %H:%M:%S")),
            "country": "Germany",
            "language": "German",
            "messages_sent": 8,
            "sentiment": "Negative",
            "initial_msg": "Ich habe ein Problem mit meiner Bestellung.",
        },
    ]

    for data in test_data:
        ExternalChatSession.objects.create(
            session_id=data["session_id"],
            start_time=data["start_time"],
            end_time=data["end_time"],
            ip_address="127.0.0.1",
            country=data["country"],
            language=data["language"],
            messages_sent=data["messages_sent"],
            sentiment=data["sentiment"],
            escalated=False,
            forwarded_hr=False,
            initial_msg=data["initial_msg"],
            user_rating=5,
            external_source=ext_source,
        )
        sessions_created += 1

    print(f"Created {sessions_created} test sessions")


def sync_data(ext_source, dash_source):
    """Sync data from external data source to dashboard data source"""
    external_sessions = ExternalChatSession.objects.filter(external_source=ext_source)
    session_count = external_sessions.count()

    if session_count == 0:
        print("No external sessions to sync")
        return

    print(f"Syncing {session_count} sessions...")

    # Clear existing data
    existing_count = DashboardChatSession.objects.filter(data_source=dash_source).count()
    if existing_count > 0:
        print(f"Clearing {existing_count} existing dashboard sessions")
        DashboardChatSession.objects.filter(data_source=dash_source).delete()

    # Process each external session
    synced_count = 0
    error_count = 0

    for ext_session in external_sessions:
        try:
            with transaction.atomic():
                # Create dashboard chat session
                dashboard_session = DashboardChatSession.objects.create(
                    data_source=dash_source,
                    session_id=ext_session.session_id,
                    start_time=ext_session.start_time,
                    end_time=ext_session.end_time,
                    ip_address=ext_session.ip_address,
                    country=ext_session.country or "",
                    language=ext_session.language or "",
                    messages_sent=ext_session.messages_sent or 0,
                    sentiment=ext_session.sentiment or "",
                    escalated=ext_session.escalated or False,
                    forwarded_hr=ext_session.forwarded_hr or False,
                    full_transcript=ext_session.full_transcript_url or "",
                    avg_response_time=ext_session.avg_response_time,
                    tokens=ext_session.tokens or 0,
                    tokens_eur=ext_session.tokens_eur,
                    category=ext_session.category or "",
                    initial_msg=ext_session.initial_msg or "",
                    user_rating=(str(ext_session.user_rating) if ext_session.user_rating is not None else ""),
                )
                synced_count += 1
                print(f"Synced session: {dashboard_session.session_id}")
        except Exception as e:
            print(f"Error syncing session {ext_session.session_id}: {str(e)}")
            error_count += 1

    print(f"Sync complete. Total: {synced_count} sessions synced, {error_count} errors")


if __name__ == "__main__":
    main()

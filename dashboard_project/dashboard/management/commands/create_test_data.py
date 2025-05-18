# dashboard/management/commands/create_test_data.py

import csv
import os
from datetime import datetime, timedelta

from dashboard.models import DataSource
from data_integration.models import ChatMessage, ChatSession, ExternalDataSource
from django.core.management.base import BaseCommand
from django.utils.timezone import make_aware


class Command(BaseCommand):
    help = "Create test data for external data source and link it to a dashboard data source"

    def add_arguments(self, parser):
        parser.add_argument(
            "--company-id",
            type=int,
            help="Company ID to associate with the data source",
            required=True,
        )
        parser.add_argument(
            "--sample-file",
            type=str,
            help="Path to sample CSV file",
            default="examples/sample.csv",
        )

    def handle(self, *args, **options):  # noqa: ARG002
        company_id = options["company_id"]
        sample_file = options["sample_file"]

        # Check if sample file exists
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
        sample_path = os.path.join(project_root, sample_file)

        if not os.path.exists(sample_path):
            self.stdout.write(self.style.ERROR(f"Sample file not found: {sample_path}"))
            return

        # Create or get external data source
        ext_source, created = ExternalDataSource.objects.get_or_create(
            name="Test External Source",
            defaults={
                "api_url": "https://example.com/api",
                "is_active": True,
                "sync_interval": 3600,
                "last_synced": make_aware(datetime.now()),
            },
        )

        if created:
            self.stdout.write(
                self.style.SUCCESS(f"Created external data source: {ext_source.name} (ID: {ext_source.id})")
            )
        else:
            self.stdout.write(f"Using existing external data source: {ext_source.name} (ID: {ext_source.id})")

        # Create or get dashboard data source linked to external source
        dash_source, created = DataSource.objects.get_or_create(
            name="Test Dashboard Source",
            company_id=company_id,
            external_source=ext_source,
            defaults={"description": "Test data source linked to external API"},
        )

        if created:
            self.stdout.write(
                self.style.SUCCESS(f"Created dashboard data source: {dash_source.name} (ID: {dash_source.id})")
            )
        else:
            self.stdout.write(f"Using existing dashboard data source: {dash_source.name} (ID: {dash_source.id})")

        # Import test data from CSV
        session_count = 0
        message_count = 0

        # First clear any existing sessions
        existing_count = ChatSession.objects.filter().count()
        if existing_count > 0:
            self.stdout.write(f"Clearing {existing_count} existing chat sessions")
            ChatSession.objects.all().delete()

        # Parse sample CSV
        with open(sample_path, "r") as f:
            reader = csv.reader(f)
            header = next(reader)  # Skip header

            for row in reader:
                # Make sure row has enough elements
                padded_row = row + [""] * (len(header) - len(row))

                # Create a dict from the row
                data = dict(zip(header, padded_row, strict=False))

                # Create a chat session
                try:
                    # Parse dates
                    try:
                        start_time = make_aware(datetime.strptime(data.get("start_time", ""), "%d.%m.%Y %H:%M:%S"))
                    except ValueError:
                        start_time = make_aware(datetime.now() - timedelta(hours=1))

                    try:
                        end_time = make_aware(datetime.strptime(data.get("end_time", ""), "%d.%m.%Y %H:%M:%S"))
                    except ValueError:
                        end_time = make_aware(datetime.now())

                    # Convert values to appropriate types
                    escalated = data.get("escalated", "").lower() == "true"
                    forwarded_hr = data.get("forwarded_hr", "").lower() == "true"
                    messages_sent = int(data.get("messages_sent", 0) or 0)
                    tokens = int(data.get("tokens", 0) or 0)
                    tokens_eur = float(data.get("tokens_eur", 0) or 0)
                    user_rating = int(data.get("user_rating", 0) or 0) if data.get("user_rating", "") else None

                    # Create session
                    session = ChatSession.objects.create(
                        session_id=data.get("session_id", f"test-{session_count}"),
                        start_time=start_time,
                        end_time=end_time,
                        ip_address=data.get("ip_address", "127.0.0.1"),
                        country=data.get("country", ""),
                        language=data.get("language", ""),
                        messages_sent=messages_sent,
                        sentiment=data.get("sentiment", ""),
                        escalated=escalated,
                        forwarded_hr=forwarded_hr,
                        full_transcript_url=data.get("full_transcript", ""),
                        avg_response_time=float(data.get("avg_response_time", 0) or 0),
                        tokens=tokens,
                        tokens_eur=tokens_eur,
                        category=data.get("category", ""),
                        initial_msg=data.get("initial_msg", ""),
                        user_rating=user_rating,
                    )

                    session_count += 1

                    # Create messages for this session
                    if data.get("initial_msg"):
                        # User message
                        ChatMessage.objects.create(
                            session=session,
                            sender="User",
                            message=data.get("initial_msg", ""),
                            timestamp=start_time,
                        )
                        message_count += 1

                        # Assistant response
                        ChatMessage.objects.create(
                            session=session,
                            sender="Assistant",
                            message=f"This is a test response to {data.get('initial_msg', '')}",
                            timestamp=start_time + timedelta(seconds=30),
                        )
                        message_count += 1

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error creating session: {e}"))

        self.stdout.write(self.style.SUCCESS(f"Created {session_count} chat sessions with {message_count} messages"))

        # Run the sync command to copy data to dashboard
        self.stdout.write("Syncing data to dashboard...")

        from django.core.management import call_command

        call_command("sync_external_data", source_id=ext_source.id)

        self.stdout.write(self.style.SUCCESS("Done! Your dashboard should now show test data."))

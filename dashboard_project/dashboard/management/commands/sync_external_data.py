# dashboard/management/commands/sync_external_data.py

import logging

from dashboard.models import ChatSession as DashboardChatSession
from dashboard.models import DataSource
from data_integration.models import ChatSession as ExternalChatSession
from django.core.management.base import BaseCommand
from django.db import transaction

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Synchronize data from external data sources to dashboard data sources"

    def add_arguments(self, parser):
        parser.add_argument(
            "--source-id",
            type=int,
            help="Specific external data source ID to sync",
            required=False,
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing dashboard data before sync",
        )

    def handle(self, *args, **options):  # noqa: ARG002
        source_id = options.get("source_id")
        clear_existing = options.get("clear", False)

        # Get all datasources that have an external_source
        if source_id:
            data_sources = DataSource.objects.filter(external_source_id=source_id)
            if not data_sources.exists():
                self.stdout.write(
                    self.style.WARNING(f"No dashboard data sources linked to external source ID {source_id}")
                )
                return
        else:
            data_sources = DataSource.objects.exclude(external_source=None)
            if not data_sources.exists():
                self.stdout.write(self.style.WARNING("No dashboard data sources with external sources found"))
                return

        total_synced = 0
        total_errors = 0

        for data_source in data_sources:
            self.stdout.write(f"Processing dashboard data source: {data_source.name} (ID: {data_source.id})")

            if not data_source.external_source:
                self.stdout.write(self.style.WARNING(f"  - No external source linked to {data_source.name}"))
                continue

            # Get all external chat sessions for this source
            external_sessions = ExternalChatSession.objects.all()
            session_count = external_sessions.count()

            if session_count == 0:
                self.stdout.write(self.style.WARNING("  - No external sessions found"))
                continue

            self.stdout.write(f"  - Found {session_count} external sessions")

            # Clear existing data if requested
            if clear_existing:
                existing_count = DashboardChatSession.objects.filter(data_source=data_source).count()
                if existing_count > 0:
                    self.stdout.write(f"  - Clearing {existing_count} existing dashboard sessions")
                    DashboardChatSession.objects.filter(data_source=data_source).delete()

            # Process each external session
            synced_count = 0
            error_count = 0

            for ext_session in external_sessions:
                try:
                    with transaction.atomic():
                        # Create or update dashboard chat session
                        (
                            dashboard_session,
                            created,
                        ) = DashboardChatSession.objects.update_or_create(
                            data_source=data_source,
                            session_id=ext_session.session_id,
                            defaults={
                                "start_time": ext_session.start_time,
                                "end_time": ext_session.end_time,
                                "ip_address": ext_session.ip_address,
                                "country": ext_session.country or "",
                                "language": ext_session.language or "",
                                "messages_sent": ext_session.messages_sent or 0,
                                "sentiment": ext_session.sentiment or "",
                                "escalated": ext_session.escalated or False,
                                "forwarded_hr": ext_session.forwarded_hr or False,
                                "full_transcript": ext_session.full_transcript_url or "",
                                "avg_response_time": ext_session.avg_response_time,
                                "tokens": ext_session.tokens or 0,
                                "tokens_eur": ext_session.tokens_eur,
                                "category": ext_session.category or "",
                                "initial_msg": ext_session.initial_msg or "",
                                "user_rating": (
                                    str(ext_session.user_rating) if ext_session.user_rating is not None else ""
                                ),
                            },
                        )
                        synced_count += 1
                        action = "Created" if created else "Updated"
                        self.stdout.write(f"  - {action} session: {dashboard_session.session_id}")

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"  - Error syncing session {ext_session.session_id}: {str(e)}"))
                    logger.error(
                        f"Error syncing session {ext_session.session_id}: {e}",
                        exc_info=True,
                    )
                    error_count += 1

            self.stdout.write(self.style.SUCCESS(f"  - Synced {synced_count} sessions with {error_count} errors"))
            total_synced += synced_count
            total_errors += error_count

        self.stdout.write(
            self.style.SUCCESS(f"Sync complete. Total: {total_synced} sessions synced, {total_errors} errors")
        )

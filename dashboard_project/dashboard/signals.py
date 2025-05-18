# dashboard/signals.py

import logging

from dashboard.models import ChatSession as DashboardChatSession
from dashboard.models import DataSource
from data_integration.models import ChatSession as ExternalChatSession
from django.db.models.signals import post_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)


@receiver(post_save, sender=ExternalChatSession)
def sync_external_session_to_dashboard(
    sender,  # noqa: ARG001
    instance,
    created,
    **kwargs,  # noqa: ARG001
):
    """
    Signal handler to sync external chat sessions to dashboard chat sessions
    whenever an external session is created or updated.

    Args:
        sender: The model class that sent the signal (unused but required by Django's signal interface)
        instance: The ExternalChatSession instance that was saved
        created: Boolean indicating if this is a new instance
        **kwargs: Additional keyword arguments (unused but required by Django's signal interface)
    """
    # Find all dashboard data sources that are linked to this external data source
    # Since ExternalChatSession doesn't have a direct link to ExternalDataSource,
    # we need to sync to all dashboard data sources with external sources
    data_sources = DataSource.objects.exclude(external_source=None)

    if not data_sources.exists():
        logger.warning(f"No dashboard data sources with external sources found for session {instance.session_id}")
        return

    for data_source in data_sources:
        try:
            # Create or update dashboard chat session
            dashboard_session, created = DashboardChatSession.objects.update_or_create(
                data_source=data_source,
                session_id=instance.session_id,
                defaults={
                    "start_time": instance.start_time,
                    "end_time": instance.end_time,
                    "ip_address": instance.ip_address,
                    "country": instance.country or "",
                    "language": instance.language or "",
                    "messages_sent": instance.messages_sent or 0,
                    "sentiment": instance.sentiment or "",
                    "escalated": instance.escalated or False,
                    "forwarded_hr": instance.forwarded_hr or False,
                    "full_transcript": instance.full_transcript_url or "",
                    "avg_response_time": instance.avg_response_time,
                    "tokens": instance.tokens or 0,
                    "tokens_eur": instance.tokens_eur,
                    "category": instance.category or "",
                    "initial_msg": instance.initial_msg or "",
                    "user_rating": (str(instance.user_rating) if instance.user_rating is not None else ""),
                },
            )

            if created:
                logger.info(
                    f"Created dashboard session: {dashboard_session.session_id} for data source {data_source.name}"
                )
            else:
                logger.info(
                    f"Updated dashboard session: {dashboard_session.session_id} for data source {data_source.name}"
                )

        except Exception as e:
            logger.error(
                f"Error syncing session {instance.session_id} to data source {data_source.name}: {e}",
                exc_info=True,
            )

import logging
import os

from celery import shared_task
from django.db import utils as django_db_utils
from django.utils import timezone

from .models import ExternalDataSource
from .utils import fetch_and_store_chat_data

logger = logging.getLogger(__name__)


@shared_task(name="data_integration.tasks.test_task", bind=True)
def test_task(self):
    """A simple test task to verify Celery is working without external dependencies."""
    logger.info("Test task executed at %s (task_id: %s)", timezone.now(), self.request.id)
    return "Test task completed successfully!"


@shared_task(
    name="data_integration.tasks.periodic_fetch_chat_data",
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3, "countdown": 60},
    soft_time_limit=int(os.environ.get("FETCH_DATA_TIMEOUT", 300)),  # 5 minutes default
)
def periodic_fetch_chat_data(self):
    """Periodically fetch and process chat data from external sources.

    This task:
    1. Fetches data from all active external data sources
    2. Processes and stores the data in the database
    3. Updates the last_synced timestamp on each source
    4. Handles errors with retries
    """
    logger.info("Starting periodic chat data fetch (task_id: %s)...", self.request.id)
    try:
        # Get all active data sources
        active_sources = ExternalDataSource.objects.filter(is_active=True)

        if not active_sources.exists():
            logger.warning("No active external data sources found. Skipping fetch.")
            return "No active data sources found"

        successful_sources = []
        failed_sources = []

        for source in active_sources:
            try:
                logger.info(f"Processing source: {source.name} (ID: {source.id})")
                fetch_and_store_chat_data(source_id=source.id)
                source.last_synced = timezone.now()
                # Check if error_count field exists in the model
                update_fields = ["last_synced"]
                try:
                    source.error_count = 0
                    source.last_error = None
                    update_fields.extend(["error_count", "last_error"])
                except AttributeError:
                    # Fields might not exist yet if migrations haven't been applied
                    logger.warning("New fields not available. Run migrations to enable error tracking.")
                source.save(update_fields=update_fields)
                successful_sources.append(source.name)
            except Exception as e:
                logger.error(f"Error fetching data from source {source.name}: {e}", exc_info=True)
                try:
                    source.error_count = getattr(source, "error_count", 0) + 1
                    source.last_error = str(e)[:255]  # Truncate to fit in the field
                    source.save(update_fields=["error_count", "last_error"])
                except (AttributeError, django_db_utils.OperationalError):
                    # If fields don't exist, just update last_synced
                    logger.warning("Could not update error fields. Run migrations to enable error tracking.")
                    source.last_synced = timezone.now()
                    source.save(update_fields=["last_synced"])
                failed_sources.append(source.name)

        if failed_sources and not successful_sources:
            # If all sources failed, we should raise an exception to trigger retry
            raise Exception(f"All data sources failed: {', '.join(failed_sources)}")

        result_message = f"Completed: {len(successful_sources)} successful, {len(failed_sources)} failed"
        logger.info(result_message)
        return result_message

    except Exception as e:
        logger.error(f"Error during periodic chat data fetch: {e}", exc_info=True)
        raise  # Re-raise to trigger Celery retry


@shared_task(name="data_integration.tasks.refresh_specific_source", bind=True)
def refresh_specific_source(self, source_id):
    """Manually refresh a specific data source.

    Args:
        source_id: ID of the ExternalDataSource to refresh
    """
    logger.info(f"Starting manual refresh of data source ID: {source_id} (task_id: {self.request.id})")
    try:
        source = ExternalDataSource.objects.get(id=source_id)
        fetch_and_store_chat_data(source_id=source_id)
        source.last_synced = timezone.now()
        source.error_count = 0
        source.last_error = None
        source.save(update_fields=["last_synced", "error_count", "last_error"])
        logger.info(f"Manual refresh of data source {source.name} completed successfully")
        return f"Successfully refreshed data source: {source.name}"
    except ExternalDataSource.DoesNotExist:
        logger.error(f"Data source with ID {source_id} does not exist")
        return f"Error: Data source with ID {source_id} does not exist"
    except Exception as e:
        logger.error(
            f"Error during manual refresh of data source {source_id}: {e}",
            exc_info=True,
        )
        return f"Error: {str(e)}"

import logging

from data_integration.tasks import test_task
from django.core.management.base import BaseCommand
from django.utils import timezone

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Test Celery configuration by executing a simple task"

    def handle(self, *args, **options):  # noqa: ARG002
        self.stdout.write(f"Testing Celery configuration at {timezone.now()}")

        try:
            # Run the test task
            self.stdout.write("Submitting test task to Celery...")
            result = test_task.delay()
            task_id = result.id

            self.stdout.write(f"Task submitted with ID: {task_id}")
            self.stdout.write("Waiting for task result (this may take a few seconds)...")

            # Try to get the result with a timeout
            try:
                task_result = result.get(timeout=10)  # 10 second timeout
                self.stdout.write(self.style.SUCCESS(f"✅ Task completed successfully with result: {task_result}"))
                return
            except TimeoutError:
                self.stdout.write(
                    self.style.WARNING(
                        "⚠️ Task did not complete within the timeout period. "
                        "This might be normal if Celery worker isn't running."
                    )
                )

            self.stdout.write(
                "To check task status, run Celery worker in another terminal with:\n"
                "    make celery\n"
                f"And then check status of task {task_id}"
            )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error testing Celery: {e}"))
            self.stdout.write("Make sure the Celery broker (Redis or SQLite) is properly configured.")
            self.stdout.write("To start Celery, run:\n    make celery")

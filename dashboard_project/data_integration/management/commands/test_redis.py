import logging

from django.conf import settings
from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Test Redis connection for Celery"

    def handle(self, *args, **options):  # noqa: ARG002
        self.stdout.write("Testing Redis connection...")

        try:
            import redis

            # Get Redis configuration from settings
            redis_host = getattr(settings, "REDIS_HOST", "localhost")
            redis_port = int(getattr(settings, "REDIS_PORT", 6379))
            redis_db = int(getattr(settings, "REDIS_DB", 0))

            # Override from environment if set
            import os

            if "REDIS_URL" in os.environ:
                self.stdout.write(f"REDIS_URL environment variable found: {os.environ['REDIS_URL']}")

            # Try to connect and ping
            redis_client = redis.Redis(host=redis_host, port=redis_port, db=redis_db, socket_connect_timeout=2)

            ping_result = redis_client.ping()

            if ping_result:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✅ Redis connection successful! Connected to {redis_host}:{redis_port}/{redis_db}"
                    )
                )
                self.stdout.write(f"Broker URL: {settings.CELERY_BROKER_URL}")
                self.stdout.write(f"Result backend: {settings.CELERY_RESULT_BACKEND}")

                # Try to set and get a value
                test_key = "test_redis_connection"
                test_value = "success"
                redis_client.set(test_key, test_value)
                retrieved_value = redis_client.get(test_key)

                if retrieved_value and retrieved_value.decode() == test_value:
                    self.stdout.write(self.style.SUCCESS("✅ Redis SET/GET test passed!"))
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f"⚠️ Redis SET/GET test failed: Got {retrieved_value} instead of {test_value}"
                        )
                    )

                # Clean up
                redis_client.delete(test_key)
            else:
                self.stdout.write(self.style.ERROR("❌ Redis ping failed!"))
        except redis.exceptions.ConnectionError as e:
            self.stdout.write(self.style.ERROR(f"❌ Redis connection error: {e}"))
            self.stdout.write("Celery will use SQLite fallback if configured.")
        except ImportError:
            self.stdout.write(self.style.ERROR("❌ Redis package not installed. Install with: pip install redis"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error: {e}"))

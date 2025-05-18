from data_integration.models import ExternalDataSource
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create default external data source configuration"

    def handle(self, *_args, **_options):
        if not ExternalDataSource.objects.exists():
            source = ExternalDataSource.objects.create(  # nosec: B106
                name="Notso AI Chat API",
                api_url="https://HOST/COMPANY/chats",
                auth_username="DEFAULT_USERNAME",  # Will be set via environment variables
                auth_password="DEFAULT_PASSWORD",  # Will be set via environment variables
                is_active=True,
                sync_interval=int(self.get_env_var("CHAT_DATA_FETCH_INTERVAL", "3600")),
                timeout=int(self.get_env_var("FETCH_DATA_TIMEOUT", "300")),
            )
            self.stdout.write(self.style.SUCCESS(f"Created default external data source: {source.name}"))
        else:
            self.stdout.write(self.style.SUCCESS("External data source already exists, no action taken."))

    def get_env_var(self, name, default):
        """Get environment variable or return default"""
        import os

        return os.environ.get(name, default)

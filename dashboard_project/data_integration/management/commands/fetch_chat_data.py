from data_integration.utils import fetch_and_store_chat_data
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Fetches chat data from the external API and stores it in the database"

    def handle(self, *_args, **_options):  # Mark as unused
        self.stdout.write(self.style.SUCCESS("Starting data fetch..."))
        fetch_and_store_chat_data()
        self.stdout.write(self.style.SUCCESS("Successfully fetched and stored chat data."))

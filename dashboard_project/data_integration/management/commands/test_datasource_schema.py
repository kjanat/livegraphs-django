#!/usr/bin/env python
"""
Test the ExternalDataSource Model Schema

This management command tests if the ExternalDataSource schema has been correctly updated.
"""

import logging

from data_integration.models import ExternalDataSource
from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Test ExternalDataSource model fields"

    def handle(self, *args, **options):  # noqa: ARG002
        self.stdout.write("Testing ExternalDataSource schema...")

        try:
            # Get or create a test source
            source, created = ExternalDataSource.objects.get_or_create(
                name="Test Source",
                defaults={
                    "api_url": "https://example.com/api",
                    "is_active": False,
                },
            )

            if created:
                self.stdout.write(f"Created test source with ID: {source.id}")
            else:
                self.stdout.write(f"Using existing test source with ID: {source.id}")

            # Test setting each field
            fields_to_test = {
                "error_count": 0,
                "last_error": "Test error message",
                "sync_interval": 7200,
                "timeout": 600,
            }

            for field, value in fields_to_test.items():
                try:
                    setattr(source, field, value)
                    self.stdout.write(self.style.SUCCESS(f"✅ Successfully set {field} = {value}"))
                except AttributeError:
                    self.stdout.write(self.style.ERROR(f"❌ Field {field} doesn't exist on the model"))

            try:
                source.save()
                self.stdout.write(self.style.SUCCESS("✅ Successfully saved with all fields"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Error saving model: {e}"))

            # Read back the values to verify
            refreshed_source = ExternalDataSource.objects.get(id=source.id)
            self.stdout.write("\nVerifying saved values:")
            for field, expected_value in fields_to_test.items():
                actual_value = getattr(refreshed_source, field, "MISSING")
                if actual_value == expected_value:
                    self.stdout.write(self.style.SUCCESS(f"✅ {field} = {actual_value} (correct)"))
                else:
                    self.stdout.write(self.style.ERROR(f"❌ {field} = {actual_value} (expected: {expected_value})"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Test failed: {e}"))

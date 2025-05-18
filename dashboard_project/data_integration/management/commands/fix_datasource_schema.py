#!/usr/bin/env python
"""
Migration Fix Script for ExternalDataSource

This management command adds the missing fields to ExternalDataSource
model directly using SQL, which is useful if Django migrations
are having issues.
"""

import logging

from django.core.management.base import BaseCommand
from django.db import connection

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Fix missing columns in ExternalDataSource table"

    def handle(self, *args, **options):  # noqa: ARG002
        self.stdout.write("Checking ExternalDataSource schema...")

        # Check if columns exist
        with connection.cursor() as cursor:
            cursor.execute("PRAGMA table_info(data_integration_externaldatasource)")
            columns = [col[1] for col in cursor.fetchall()]

            missing_columns = []
            if "error_count" not in columns:
                missing_columns.append("error_count")
            if "last_error" not in columns:
                missing_columns.append("last_error")
            if "sync_interval" not in columns:
                missing_columns.append("sync_interval")
            if "timeout" not in columns:
                missing_columns.append("timeout")

            if not missing_columns:
                self.stdout.write(self.style.SUCCESS("✅ All columns exist in ExternalDataSource table"))
                return

            self.stdout.write(f"Missing columns: {', '.join(missing_columns)}")
            self.stdout.write("Adding missing columns...")

            try:
                # Add missing columns with SQLite
                for col in missing_columns:
                    if col == "error_count":
                        cursor.execute(
                            "ALTER TABLE data_integration_externaldatasource ADD COLUMN error_count integer DEFAULT 0"
                        )
                    elif col == "last_error":
                        cursor.execute(
                            "ALTER TABLE data_integration_externaldatasource ADD COLUMN last_error varchar(255) NULL"
                        )
                    elif col == "sync_interval":
                        cursor.execute(
                            "ALTER TABLE data_integration_externaldatasource ADD COLUMN sync_interval integer DEFAULT 3600"
                        )
                    elif col == "timeout":
                        cursor.execute(
                            "ALTER TABLE data_integration_externaldatasource ADD COLUMN timeout integer DEFAULT 300"
                        )

                self.stdout.write(
                    self.style.SUCCESS(f"✅ Successfully added missing columns: {', '.join(missing_columns)}")
                )

                # Verify columns were added
                cursor.execute("PRAGMA table_info(data_integration_externaldatasource)")
                updated_columns = [col[1] for col in cursor.fetchall()]
                self.stdout.write(f"Current columns: {', '.join(updated_columns)}")

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Error adding columns: {e}"))
                self.stdout.write(self.style.WARNING("Consider running Django migrations instead:"))
                self.stdout.write("  python manage.py makemigrations data_integration")
                self.stdout.write("  python manage.py migrate data_integration")

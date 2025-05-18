# dashboard_project/scripts/cleanup_duplicates.py

import os
import sys

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dashboard_project.settings")
import django  # noqa: I001

django.setup()

from dashboard.models import ChatSession  # noqa: E402, I001
from django.db.models import Count  # noqa: E402


def cleanup_duplicates():
    print("Looking for duplicate ChatSessions...")
    duplicates = ChatSession.objects.values("session_id", "data_source").annotate(count=Count("id")).filter(count__gt=1)

    total_deleted = 0
    for dup in duplicates:
        session_id = dup["session_id"]
        data_source = dup["data_source"]
        # Get all ids for this duplicate group, order by id (keep the first, delete the rest)
        ids = list(
            ChatSession.objects.filter(session_id=session_id, data_source=data_source)
            .order_by("id")
            .values_list("id", flat=True)
        )
        # Keep the first, delete the rest
        to_delete = ids[1:]
        deleted, _ = ChatSession.objects.filter(id__in=to_delete).delete()
        total_deleted += deleted
        print(f"Removed {deleted} duplicates for session_id={session_id}, data_source={data_source}")

    print(f"Done. Total duplicates removed: {total_deleted}")


if __name__ == "__main__":
    cleanup_duplicates()

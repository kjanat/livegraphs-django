# dashboard/admin.py

from django.contrib import admin

from .models import ChatSession, Dashboard, DataSource


@admin.register(DataSource)
class DataSourceAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "company",
        "uploaded_at",
        "get_external_source",
        "get_session_count",
    )
    list_filter = ("company", "uploaded_at")
    search_fields = ("name", "description", "company__name")
    ordering = ("-uploaded_at",)
    readonly_fields = ("get_external_data_status",)

    fieldsets = (
        (None, {"fields": ("name", "description", "company")}),
        (
            "Data Source",
            {
                "fields": ("file", "external_source"),
                "description": "Either upload a file OR select an external data source. Not both.",
            },
        ),
        (
            "Stats",
            {
                "fields": ("get_external_data_status",),
            },
        ),
    )

    @admin.display(description="Sessions")
    def get_session_count(self, obj):
        return obj.chat_sessions.count()

    @admin.display(description="External Source")
    def get_external_source(self, obj):
        if obj.external_source:
            return obj.external_source.name
        return "None"

    @admin.display(description="External Data Status")
    def get_external_data_status(self, obj):
        if obj.external_source:
            return f"Last synced: {obj.external_source.last_synced or 'Never'} | Status: {obj.external_source.get_status()}"
        return "No external data source linked"


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = (
        "session_id",
        "get_company",
        "start_time",
        "end_time",
        "country",
        "language",
        "sentiment",
    )
    list_filter = (
        "data_source__company",
        "start_time",
        "country",
        "language",
        "sentiment",
        "escalated",
        "forwarded_hr",
    )
    search_fields = (
        "session_id",
        "country",
        "language",
        "initial_msg",
        "full_transcript",
    )
    ordering = ("-start_time",)

    @admin.display(
        description="Company",
        ordering="data_source__company__name",
    )
    def get_company(self, obj):
        return obj.data_source.company.name


@admin.register(Dashboard)
class DashboardAdmin(admin.ModelAdmin):
    list_display = ("name", "company", "created_at", "updated_at")
    list_filter = ("company", "created_at")
    search_fields = ("name", "description", "company__name")
    filter_horizontal = ("data_sources",)
    ordering = ("-updated_at",)

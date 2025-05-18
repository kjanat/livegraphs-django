from django.contrib import admin
from django.utils.html import format_html

from .models import ChatMessage, ChatSession, ExternalDataSource
from .tasks import refresh_specific_source


@admin.register(ExternalDataSource)
class ExternalDataSourceAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "api_url",
        "is_active",
        "last_synced",
        "status_badge",
        "sync_interval",
        "refresh_action",
    )
    list_filter = ("is_active",)
    search_fields = ("name", "api_url")
    readonly_fields = ("last_synced", "error_count", "last_error")
    fieldsets = (
        (None, {"fields": ("name", "api_url", "is_active")}),
        (
            "Authentication",
            {
                "fields": ("auth_username", "auth_password"),
                "description": "Credentials can also be provided via environment variables.",
            },
        ),
        ("Sync Settings", {"fields": ("sync_interval", "timeout")}),
        ("Status", {"fields": ("last_synced", "error_count", "last_error")}),
    )

    @admin.display(description="Status")
    def status_badge(self, obj):
        """Display a colored status badge"""
        status = obj.get_status()
        if status == "Active":
            return format_html(
                '<span style="color: white; background-color: green; padding: 3px 8px; border-radius: 10px;">{}</span>',
                status,
            )
        elif status == "Inactive":
            return format_html(
                '<span style="color: white; background-color: gray; padding: 3px 8px; border-radius: 10px;">{}</span>',
                status,
            )
        elif "Error" in status:
            return format_html(
                '<span style="color: white; background-color: red; padding: 3px 8px; border-radius: 10px;">{}</span>',
                status,
            )
        else:
            return format_html(
                '<span style="color: white; background-color: orange; padding: 3px 8px; border-radius: 10px;">{}</span>',
                status,
            )

    @admin.display(description="Actions")
    def refresh_action(self, obj):
        """Button to manually refresh a data source"""
        if obj.is_active:
            url = f"/admin/data_integration/externaldatasource/refresh/{obj.id}/"
            return format_html('<a class="button" href="{}">Refresh Now</a>', url)
        return "Inactive"

    def refresh_source(self, request, source_id):
        """Run a task to refresh the source data"""
        task = refresh_specific_source.delay(source_id)
        self.message_user(request, f"Data refresh task started (Task ID: {task.id})")

    def get_urls(self):
        from django.urls import path

        urls = super().get_urls()
        custom_urls = [
            path(
                "refresh/<int:source_id>/",
                self.admin_site.admin_view(self.refresh_source),
                name="data_integration_externaldatasource_refresh",
            ),
        ]
        return custom_urls + urls


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = (
        "session_id",
        "start_time",
        "end_time",
        "country",
        "language",
        "messages_sent",
        "sentiment",
    )
    list_filter = ("country", "language", "sentiment")
    search_fields = ("session_id", "country", "ip_address")
    readonly_fields = ("session_id",)


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ("session", "sender", "timestamp", "message_preview")
    list_filter = ("sender", "timestamp")
    search_fields = ("message", "session__session_id")
    readonly_fields = ("safe_html_display",)

    @admin.display(description="Message")
    def message_preview(self, obj):
        """Show a preview of the message"""
        if len(obj.message) > 50:
            return obj.message[:50] + "..."
        return obj.message

    @admin.display(description="Sanitized HTML Preview")
    def safe_html_display(self, obj):
        """Display the sanitized HTML"""
        if obj.safe_html_message:
            return format_html(
                '<div style="padding: 10px; border: 1px solid #ccc; background-color: #f9f9f9;">{}</div>',
                obj.safe_html_message,
            )
        return "No HTML content"

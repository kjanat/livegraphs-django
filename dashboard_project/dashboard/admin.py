# dashboard/admin.py

from django.contrib import admin

from .models import ChatSession, Dashboard, DataSource


class DataSourceAdmin(admin.ModelAdmin):
    list_display = ("name", "company", "uploaded_at", "get_session_count")
    list_filter = ("company", "uploaded_at")
    search_fields = ("name", "description", "company__name")
    ordering = ("-uploaded_at",)

    def get_session_count(self, obj):
        return obj.chat_sessions.count()

    get_session_count.short_description = "Sessions"


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

    def get_company(self, obj):
        return obj.data_source.company.name

    get_company.short_description = "Company"
    get_company.admin_order_field = "data_source__company__name"


class DashboardAdmin(admin.ModelAdmin):
    list_display = ("name", "company", "created_at", "updated_at")
    list_filter = ("company", "created_at")
    search_fields = ("name", "description", "company__name")
    filter_horizontal = ("data_sources",)
    ordering = ("-updated_at",)


admin.site.register(DataSource, DataSourceAdmin)
admin.site.register(ChatSession, ChatSessionAdmin)
admin.site.register(Dashboard, DashboardAdmin)

import os

from django.db import models


class ChatSession(models.Model):
    session_id = models.CharField(max_length=255, unique=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    country = models.CharField(max_length=255, null=True, blank=True)
    language = models.CharField(max_length=255, null=True, blank=True)
    messages_sent = models.IntegerField(null=True, blank=True)
    sentiment = models.CharField(max_length=255, null=True, blank=True)
    escalated = models.BooleanField(null=True, blank=True)
    forwarded_hr = models.BooleanField(null=True, blank=True)
    full_transcript_url = models.URLField(max_length=1024, null=True, blank=True)
    avg_response_time = models.FloatField(null=True, blank=True)
    tokens = models.IntegerField(null=True, blank=True)
    tokens_eur = models.FloatField(null=True, blank=True)
    category = models.CharField(max_length=255, null=True, blank=True)
    initial_msg = models.TextField(null=True, blank=True)
    user_rating = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.session_id


class ChatMessage(models.Model):
    session = models.ForeignKey(ChatSession, related_name="messages", on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)  # Changed to auto_now_add for simplicity
    sender = models.CharField(max_length=255)  # "User" or "Assistant"
    message = models.TextField()
    safe_html_message = models.TextField(blank=True, null=True)  # For storing sanitized HTML

    def __str__(self):
        return f"{self.session.session_id} - {self.sender} at {self.timestamp}"


class ExternalDataSource(models.Model):
    name = models.CharField(max_length=255, default="External API")
    api_url = models.URLField(default="https://proto.notso.ai/jumbo/chats")
    auth_username = models.CharField(max_length=255, blank=True, null=True)
    auth_password = models.CharField(
        max_length=255, blank=True, null=True
    )  # Consider using a more secure way to store credentials
    last_synced = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    error_count = models.IntegerField(default=0)
    last_error = models.CharField(max_length=255, blank=True, null=True)
    sync_interval = models.IntegerField(default=3600, help_text="Sync interval in seconds. Default is 3600 (1 hour)")
    timeout = models.IntegerField(
        default=300,
        help_text="Timeout in seconds for each sync operation. Default is 300 (5 minutes)",
    )

    def get_auth_username(self):
        """Get username from environment variable if set, otherwise use stored value"""
        env_username = os.environ.get("EXTERNAL_API_USERNAME")
        return env_username if env_username else self.auth_username

    def get_auth_password(self):
        """Get password from environment variable if set, otherwise use stored value"""
        env_password = os.environ.get("EXTERNAL_API_PASSWORD")
        return env_password if env_password else self.auth_password

    def get_status(self):
        """Get the status of this data source"""
        if not self.is_active:
            return "Inactive"
        if not self.last_synced:
            return "Never synced"
        if self.error_count > 0:
            return f"Error ({self.error_count})"
        return "Active"

    def __str__(self):
        return self.name

# dashboard/models.py

from accounts.models import Company
from django.db import models


class DataSource(models.Model):
    """Model for uploaded data sources (CSV files)"""

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to="data_sources/")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="data_sources")

    def __str__(self):
        return self.name


class ChatSession(models.Model):
    """Model to store parsed chat session data from CSV"""

    data_source = models.ForeignKey(DataSource, on_delete=models.CASCADE, related_name="chat_sessions")
    session_id = models.CharField(max_length=255)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    country = models.CharField(max_length=100, blank=True)
    language = models.CharField(max_length=50, blank=True)
    messages_sent = models.IntegerField(default=0)
    sentiment = models.CharField(max_length=50, blank=True)
    escalated = models.BooleanField(default=False)
    forwarded_hr = models.BooleanField(default=False)
    full_transcript = models.TextField(blank=True)
    avg_response_time = models.FloatField(null=True, blank=True)
    tokens = models.IntegerField(default=0)
    tokens_eur = models.FloatField(null=True, blank=True)
    category = models.CharField(max_length=100, blank=True)
    initial_msg = models.TextField(blank=True)
    user_rating = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"Session {self.session_id}"


class Dashboard(models.Model):
    """Model for custom dashboards that can be created by users"""

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="dashboards")
    data_sources = models.ManyToManyField(DataSource, related_name="dashboards")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

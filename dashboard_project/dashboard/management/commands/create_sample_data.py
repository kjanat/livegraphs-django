# dashboard/management/commands/create_sample_data.py

import csv
import io
import random
from datetime import datetime, timedelta

from accounts.models import Company
from dashboard.models import ChatSession, Dashboard, DataSource
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils import timezone

User = get_user_model()


class Command(BaseCommand):
    help = "Create sample data for testing"

    def handle(self, **_options):
        self.stdout.write("Creating sample data...")

        # Create admin user if it doesn't exist
        if not User.objects.filter(username="admin").exists():
            admin_user = User.objects.create_superuser(username="admin", email="admin@example.com", password="admin123")
            self.stdout.write(self.style.SUCCESS(f"Created admin user: {admin_user.username}"))
        else:
            admin_user = User.objects.get(username="admin")
            self.stdout.write(f"Admin user already exists: {admin_user.username}")

        # Create companies
        companies = []
        company_names = ["Acme Inc.", "TechCorp", "GlobalServices"]

        for name in company_names:
            company, created = Company.objects.get_or_create(
                name=name, defaults={"description": f"Sample company: {name}"}
            )
            companies.append(company)

            if created:
                self.stdout.write(self.style.SUCCESS(f"Created company: {company.name}"))
            else:
                self.stdout.write(f"Company already exists: {company.name}")

        # Create users for each company
        for _i, company in enumerate(companies):
            # Company admin
            username = f"admin_{company.name.lower().replace(' ', '_')}"
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username,
                    email=f"{username}@example.com",
                    password="password123",
                    company=company,
                    is_company_admin=True,
                )
                self.stdout.write(self.style.SUCCESS(f"Created company admin: {user.username}"))

            # Regular users
            for j in range(2):
                username = f"user_{company.name.lower().replace(' ', '_')}_{j + 1}"
                if not User.objects.filter(username=username).exists():
                    user = User.objects.create_user(
                        username=username,
                        email=f"{username}@example.com",
                        password="password123",
                        company=company,
                    )
                    self.stdout.write(self.style.SUCCESS(f"Created user: {user.username}"))

        # Create sample data for each company
        for company in companies:
            self._create_sample_data_for_company(company)

        self.stdout.write(self.style.SUCCESS("Sample data created successfully!"))

    def _create_sample_data_for_company(self, company):
        # Create sample CSV data
        csv_data = self._generate_sample_csv_data(company.name)

        # Create data source
        data_source_name = f"{company.name} Chat Data"
        try:
            data_source = DataSource.objects.get(name=data_source_name, company=company)
            self.stdout.write(f"Data source already exists: {data_source.name}")
        except DataSource.DoesNotExist:
            # Create file from CSV data
            csv_file = ContentFile(csv_data.encode("utf-8"))
            data_source = DataSource.objects.create(
                name=data_source_name,
                description=f"Sample chat data for {company.name}",
                company=company,
            )
            data_source.file.save(f"{company.name.lower().replace(' ', '_')}_chat_data.csv", csv_file)
            self.stdout.write(self.style.SUCCESS(f"Created data source: {data_source.name}"))

            # Parse CSV data and create chat sessions
            reader = csv.DictReader(io.StringIO(csv_data))
            for row in reader:
                # Convert datetime strings to datetime objects
                start_time = datetime.strptime(row["start_time"], "%Y-%m-%d %H:%M:%S")
                end_time = datetime.strptime(row["end_time"], "%Y-%m-%d %H:%M:%S")

                # Convert boolean strings to actual booleans
                escalated = row["escalated"].lower() in ["true", "yes", "1", "t", "y"]
                forwarded_hr = row["forwarded_hr"].lower() in [
                    "true",
                    "yes",
                    "1",
                    "t",
                    "y",
                ]

                # Create chat session
                ChatSession.objects.create(
                    data_source=data_source,
                    session_id=row["session_id"],
                    start_time=timezone.make_aware(start_time),
                    end_time=timezone.make_aware(end_time),
                    ip_address=row["ip_address"],
                    country=row["country"],
                    language=row["language"],
                    messages_sent=int(row["messages_sent"]),
                    sentiment=row["sentiment"],
                    escalated=escalated,
                    forwarded_hr=forwarded_hr,
                    full_transcript=row["full_transcript"],
                    avg_response_time=float(row["avg_response_time"]),
                    tokens=int(row["tokens"]),
                    tokens_eur=float(row["tokens_eur"]),
                    category=row["category"],
                    initial_msg=row["initial_msg"],
                    user_rating=row["user_rating"],
                )

            self.stdout.write(self.style.SUCCESS(f"Created {reader.line_num} chat sessions"))

        # Create default dashboard
        dashboard_name = f"{company.name} Dashboard"
        try:
            dashboard = Dashboard.objects.get(name=dashboard_name, company=company)
            self.stdout.write(f"Dashboard already exists: {dashboard.name}")
        except Dashboard.DoesNotExist:
            dashboard = Dashboard.objects.create(
                name=dashboard_name,
                description=f"Default dashboard for {company.name}",
                company=company,
            )
            dashboard.data_sources.add(data_source)
            self.stdout.write(self.style.SUCCESS(f"Created dashboard: {dashboard.name}"))

    def _generate_sample_csv_data(self, company_name):
        """Generate sample CSV data for a company"""
        rows = []
        headers = [
            "session_id",
            "start_time",
            "end_time",
            "ip_address",
            "country",
            "language",
            "messages_sent",
            "sentiment",
            "escalated",
            "forwarded_hr",
            "full_transcript",
            "avg_response_time",
            "tokens",
            "tokens_eur",
            "category",
            "initial_msg",
            "user_rating",
        ]

        # Sample data for generating random values
        countries = [
            "USA",
            "UK",
            "Germany",
            "France",
            "Spain",
            "Italy",
            "Japan",
            "Australia",
            "Canada",
            "Brazil",
        ]
        languages = ["English", "Spanish", "German", "French", "Japanese", "Portuguese"]
        sentiments = [
            "Positive",
            "Negative",
            "Neutral",
            "Very Positive",
            "Very Negative",
        ]
        categories = ["Support", "Sales", "Technical", "Billing", "General"]
        ratings = ["Excellent", "Good", "Average", "Poor", "Terrible", ""]

        # Generate rows
        num_rows = random.randint(50, 100)

        for i in range(num_rows):
            # Generate random dates in the last 30 days
            end_date = datetime.now() - timedelta(days=random.randint(0, 30))
            start_date = end_date - timedelta(minutes=random.randint(5, 60))

            # Generate random IP address
            ip = ".".join(str(random.randint(0, 255)) for _ in range(4))

            # Random country and language
            country = random.choice(countries)
            language = random.choice(languages)

            # Random message count
            messages_sent = random.randint(3, 20)

            # Random sentiment
            sentiment = random.choice(sentiments)

            # Random escalation and forwarding
            escalated = random.random() < 0.2  # 20% chance of escalation
            forwarded_hr = random.random() < 0.1  # 10% chance of forwarding to HR

            # Generate a sample transcript
            transcript = (
                "User: Hello, I need help with my account.\n"
                "Agent: Hello! I'd be happy to help. What seems to be the issue?\n"
                "User: I can't log in to my account.\n"
                "Agent: I understand. Let me help you reset your password."
            )

            # Random response time, tokens, and cost
            avg_response_time = round(random.uniform(0.5, 10.0), 2)
            tokens = random.randint(100, 2000)
            tokens_eur = round(tokens * 0.00002, 4)  # Example rate: €0.00002 per token

            # Random category
            category = random.choice(categories)

            # Initial message
            initial_msg = "Hello, I need help with my account."

            # Random rating
            user_rating = random.choice(ratings)

            # Create row
            row = {
                "session_id": f"{company_name.lower().replace(' ', '_')}_{i + 1}",
                "start_time": start_date.strftime("%Y-%m-%d %H:%M:%S"),
                "end_time": end_date.strftime("%Y-%m-%d %H:%M:%S"),
                "ip_address": ip,
                "country": country,
                "language": language,
                "messages_sent": str(messages_sent),
                "sentiment": sentiment,
                "escalated": str(escalated),
                "forwarded_hr": str(forwarded_hr),
                "full_transcript": transcript,
                "avg_response_time": str(avg_response_time),
                "tokens": str(tokens),
                "tokens_eur": str(tokens_eur),
                "category": category,
                "initial_msg": initial_msg,
                "user_rating": user_rating,
            }

            rows.append(row)

        # Write to CSV string
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)

        return output.getvalue()

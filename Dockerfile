# Dockerfile

FROM python:3.13-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE=dashboard_project.settings

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN uv pip install -e .

# Copy project
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Run gunicorn
CMD ["gunicorn", "dashboard_project.wsgi:application", "--bind", "0.0.0.0:8000"]

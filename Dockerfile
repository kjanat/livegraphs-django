# Dockerfile

FROM python:3.13-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE=dashboard_project.settings

# Set work directory
WORKDIR /app

# Install UV for Python package management
RUN pip install uv

# Copy project files
COPY pyproject.toml .
COPY uv.lock .
COPY . .

# Install dependencies
RUN uv pip install -e .

# Change to the Django project directory
WORKDIR /app/dashboard_project

# Collect static files
RUN python manage.py collectstatic --noinput

# Change back to the app directory
WORKDIR /app

# Run gunicorn
CMD ["gunicorn", "dashboard_project.wsgi:application", "--bind", "0.0.0.0:8000"]

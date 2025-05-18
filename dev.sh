#!/bin/bash
# LiveGraphsDjango Development Helper Script

# Set UV_LINK_MODE to copy to avoid hardlink warnings
export UV_LINK_MODE=copy

# Function to print section header
print_header() {
  echo "======================================"
  echo "🚀 $1"
  echo "======================================"
}

# Display help menu
if [[ $1 == "help" ]] || [[ $1 == "-h" ]] || [[ $1 == "--help" ]] || [[ -z $1 ]]; then
  print_header "LiveGraphsDjango Development Commands"
  echo "Usage: ./dev.sh COMMAND"
  echo ""
  echo "Available commands:"
  echo "  start          - Start Redis and run the application with foreman"
  echo "  redis-start    - Start Redis server in background"
  echo "  redis-test     - Test Redis connection"
  echo "  redis-stop     - Stop Redis server"
  echo "  migrate        - Run database migrations"
  echo "  makemigrations - Create database migrations"
  echo "  superuser      - Create a superuser account"
  echo "  test-celery    - Send a test task to Celery"
  echo "  logs-celery    - View logs for Celery"
  echo "  logs-beat      - View logs for Celery Beat"
  echo "  shell          - Open Django shell"
  echo "  help           - Show this help menu"
  exit 0
fi

# Start Redis server
if [[ $1 == "redis-start" ]]; then
  print_header "Starting Redis Server"
  redis-server --daemonize yes
  sleep 1
  if redis-cli ping >/dev/null 2>&1; then
    echo "✅ Redis server is now running"
  else
    echo "❌ Failed to start Redis server"
  fi
  exit 0
fi

# Test Redis connection
if [[ $1 == "redis-test" ]]; then
  print_header "Testing Redis Connection"
  cd dashboard_project && python manage.py test_redis
  exit 0
fi

# Stop Redis server
if [[ $1 == "redis-stop" ]]; then
  print_header "Stopping Redis Server"
  redis-cli shutdown
  echo "✅ Redis server has been stopped"
  exit 0
fi

# Run migrations
if [[ $1 == "migrate" ]]; then
  print_header "Running Migrations"
  cd dashboard_project && UV_LINK_MODE=copy uv run python manage.py migrate
  exit 0
fi

# Make migrations
if [[ $1 == "makemigrations" ]]; then
  print_header "Creating Migrations"
  cd dashboard_project && UV_LINK_MODE=copy uv run python manage.py makemigrations
  exit 0
fi

# Create superuser
if [[ $1 == "superuser" ]]; then
  print_header "Creating Superuser"
  cd dashboard_project && UV_LINK_MODE=copy uv run python manage.py createsuperuser
  exit 0
fi

# Test Celery
if [[ $1 == "test-celery" ]]; then
  print_header "Testing Celery"
  cd dashboard_project && UV_LINK_MODE=copy uv run python manage.py test_celery
  exit 0
fi

# View Celery logs
if [[ $1 == "logs-celery" ]]; then
  print_header "Celery Worker Logs"
  echo "Press Ctrl+C to exit"
  cd dashboard_project && UV_LINK_MODE=copy uv run celery -A dashboard_project worker --loglevel=info
  exit 0
fi

# View Celery Beat logs
if [[ $1 == "logs-beat" ]]; then
  print_header "Celery Beat Logs"
  echo "Press Ctrl+C to exit"
  cd dashboard_project && UV_LINK_MODE=copy uv run celery -A dashboard_project beat --scheduler django_celery_beat.schedulers:DatabaseScheduler
  exit 0
fi

# Django shell
if [[ $1 == "shell" ]]; then
  print_header "Django Shell"
  cd dashboard_project && UV_LINK_MODE=copy uv run python manage.py shell
  exit 0
fi

# Start the application
if [[ $1 == "start" ]]; then
  print_header "Starting LiveGraphsDjango Application"
  ./start.sh
  exit 0
fi

# Invalid command
echo "❌ Unknown command: $1"
echo "Run './dev.sh help' to see available commands"
exit 1

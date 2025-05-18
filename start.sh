#!/bin/bash
# Set UV_LINK_MODE to copy to avoid hardlink warnings
export UV_LINK_MODE=copy

# Check if Redis is running
if ! redis-cli ping >/dev/null 2>&1; then
  echo "Starting Redis server..."
  redis-server --daemonize yes
  sleep 1

  # Verify Redis is now running
  if redis-cli ping >/dev/null 2>&1; then
    echo "✅ Redis server is now running"
  else
    echo "❌ Failed to start Redis server"
    echo "Falling back to SQLite for Celery"
    export CELERY_BROKER_URL=sqla+sqlite:///dashboard_project/celery.sqlite
    export CELERY_RESULT_BACKEND=db+sqlite:///dashboard_project/results.sqlite
  fi
else
  echo "✅ Redis server is already running"
fi

# Set environment variables for Redis if it's running
if redis-cli ping >/dev/null 2>&1; then
  export CELERY_BROKER_URL=redis://localhost:6379/0
  export CELERY_RESULT_BACKEND=redis://localhost:6379/0
  echo "Using Redis for Celery broker and result backend"
else
  export CELERY_BROKER_URL=sqla+sqlite:///dashboard_project/celery.sqlite
  export CELERY_RESULT_BACKEND=db+sqlite:///dashboard_project/results.sqlite
  echo "Using SQLite for Celery broker and result backend"
fi

# Start the application using foreman
foreman start

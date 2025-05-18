# Redis and Celery Configuration

This document explains how to set up and use Redis and Celery for background task processing in the LiveGraphs application.

## Overview

The data integration module uses Celery to handle:

- Periodic data fetching from external APIs
- Processing and storing CSV data
- Downloading and parsing transcript files
- Manual data refresh triggered by users

## Installation

### Redis (Recommended)

Redis is the recommended message broker for Celery due to its performance and reliability:

#### Ubuntu/Debian

```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Verify that Redis is running
redis-cli ping  # Should output PONG
```

After installation, check if Redis is properly configured:

1. Open Redis configuration file:

   ```bash
   sudo nano /etc/redis/redis.conf
   ```

2. Ensure the following settings:

   ```bash
   # For development (localhost only)
   bind 127.0.0.1

   # For production (accept connections from specific IP)
   # bind 127.0.0.1 your.server.ip.address

   # Protected mode (recommended)
   protected-mode yes

   # Port
   port 6379
   ```

3. Restart Redis after any changes:
   ```bash
   sudo systemctl restart redis-server
   ```

#### macOS

```bash
brew install redis
brew services start redis
```

#### Windows

Download and install from [microsoftarchive/redis](https://github.com/microsoftarchive/redis/releases)

### SQLite Fallback

If Redis is not available, the application will automatically fall back to using SQLite for Celery tasks. This works well for development but is not recommended for production.

## Configuration

### Environment Variables

Set these environment variables in your `.env` file or deployment environment:

```env
# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Task Scheduling
CHAT_DATA_FETCH_INTERVAL=3600  # In seconds (1 hour)
FETCH_DATA_TIMEOUT=300         # In seconds (5 minutes)
```

### Testing Redis Connection

To test if Redis is properly configured:

```bash
cd dashboard_project
python manage.py test_redis
```

### Testing Celery

To test if Celery is working correctly:

```bash
# Start a Celery worker in one terminal
make celery

# In another terminal, run the test task
cd dashboard_project
python manage.py test_celery
```

## Running with Docker

The included `docker-compose.yml` file sets up Redis, Celery worker, and Celery beat for you:

```bash
docker-compose up -d
```

## Running in Development

Development requires multiple terminal windows:

1. **Django Development Server**:

   ```bash
   make run
   ```

2. **Redis Server** (if needed):

   ```bash
   make run-redis
   ```

3. **Celery Worker**:

   ```bash
   make celery
   ```

4. **Celery Beat** (for scheduled tasks):
   ```bash
   make celery-beat
   ```

Or use the combined command:

```bash
make run-all
```

## Common Issues

### Redis Connection Failures

If you see connection errors:

1. Check that Redis is running: `redis-cli ping` should return `PONG`
2. Verify firewall settings are not blocking port 6379
3. Check Redis binding in `/etc/redis/redis.conf` (should be `bind 127.0.0.1` for local dev)

### Celery Workers Not Processing Tasks

1. Ensure the worker is running with the correct app name: `celery -A dashboard_project worker`
2. Check the Celery logs for errors
3. Verify broker URL settings in both code and environment variables

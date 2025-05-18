# Redis and Celery Troubleshooting Guide

This guide provides detailed steps to diagnose and fix issues with Redis and Celery in the LiveGraphs project.

## Diagnosing Redis Connection Issues

### Check if Redis is Running

```bash
# Check Redis server status
sudo systemctl status redis-server

# Try to ping Redis
redis-cli ping   # Should return PONG
```

### Test Redis Connectivity

Use our built-in test tool:

```bash
cd dashboard_project
python manage.py test_redis
```

If this fails, check the following:

1. Redis might not be running. Start it with:

   ```bash
   sudo systemctl start redis-server
   ```

2. Connection credentials may be incorrect. Check your environment variables:

   ```bash
   echo $REDIS_URL
   echo $CELERY_BROKER_URL
   echo $CELERY_RESULT_BACKEND
   ```

3. Redis might be binding only to a specific interface. Check `/etc/redis/redis.conf`:

   ```bash
   grep "bind" /etc/redis/redis.conf
   ```

4. Firewall rules might be blocking Redis. If you're connecting remotely:
   ```bash
   sudo ufw status   # Check if firewall is enabled
   sudo ufw allow 6379/tcp  # Allow Redis port if needed
   ```

## Fixing CSV Data Processing Issues

If you see the error `zip() argument 2 is shorter than argument 1`, it means the data format doesn't match the expected headers. We've implemented a fix that:

1. Pads shorter rows with empty strings
2. Uses more flexible date format parsing
3. Provides better error handling

After these changes, your data should be processed correctly regardless of format variations.

## Testing Celery Tasks

To verify if your Celery configuration is working:

```bash
# Start a Celery worker in one terminal
cd dashboard_project
celery -A dashboard_project worker --loglevel=info

# In another terminal, run the test task
cd dashboard_project
python manage.py test_celery
```

If the task isn't completing, check:

1. Look for errors in the Celery worker terminal
2. Verify broker URL settings match in both terminals:
   ```bash
   echo $CELERY_BROKER_URL
   ```
3. Check if Redis is accessible from both terminals:
   ```bash
   redis-cli ping
   ```

## Checking Scheduled Tasks

To verify if scheduled tasks are configured correctly:

```bash
# List all scheduled tasks
cd dashboard_project
python manage.py celery inspect scheduled
```

Common issues with scheduled tasks:

1. **Celery Beat not running**: Start it with:

   ```bash
   cd dashboard_project
   celery -A dashboard_project beat
   ```

2. **Task registered but not running**: Check worker logs for any errors

3. **Wrong schedule**: Check the interval in settings.py and CELERY_BEAT_SCHEDULE

## Data Source Configuration

If data sources aren't being processed correctly:

1. Verify active data sources exist:

   ```bash
   cd dashboard_project
   python manage.py shell -c "from data_integration.models import ExternalDataSource; print(ExternalDataSource.objects.filter(is_active=True).count())"
   ```

2. Create a default data source if needed:

   ```bash
   cd dashboard_project
   python manage.py create_default_datasource
   ```

3. Check source URLs and credentials in the admin interface or environment variables.

## Manually Triggering Data Refresh

To manually trigger a data refresh for testing:

```bash
cd dashboard_project
python manage.py shell -c "from data_integration.tasks import periodic_fetch_chat_data; periodic_fetch_chat_data()"
```

This will execute the task directly without going through Celery, which is useful for debugging.

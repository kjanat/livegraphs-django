.PHONY: venv install install-dev lint test format clean run migrate makemigrations superuser setup-node celery celery-beat docker-build docker-up docker-down reset-db setup-dev procfile

# Create a virtual environment
venv:
	uv venv -p 3.13

# Install production dependencies
install:
	uv pip install -e .

# Install development dependencies
install-dev:
	uv pip install -e ".[dev]"

# Run linting
lint:
	uv run -m ruff check dashboard_project

# Run tests
test:
	uv run -m pytest

# Format Python code
format:
	uv run -m ruff format dashboard_project
	uv run -m black dashboard_project

# Setup Node.js dependencies
setup-node:
	npm install --include=dev

# Clean Python cache files
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name "*.egg" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".coverage" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".tox" -exec rm -rf {} +
	find . -type d -name "node_modules" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/

# Run the development server
run:
	cd dashboard_project && uv run python manage.py runserver 8001

# Run Celery worker for background tasks
celery:
	cd dashboard_project && uv run celery -A dashboard_project worker --loglevel=info

# Run Celery Beat for scheduled tasks
celery-beat:
	cd dashboard_project && uv run celery -A dashboard_project beat --scheduler django_celery_beat.schedulers:DatabaseScheduler

# Apply migrations
migrate:
	cd dashboard_project && uv run python manage.py migrate

# Create migrations
makemigrations:
	cd dashboard_project && uv run python manage.py makemigrations

# Create a superuser
superuser:
	cd dashboard_project && uv run python manage.py createsuperuser

# Update uv lock file
lock:
	uv pip freeze > requirements.lock

# Setup pre-commit hooks
setup-pre-commit:
	pre-commit install

# Run pre-commit on all files
lint-all:
	pre-commit run --all-files

# Docker commands
docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

# Initialize or reset the database in development
reset-db:
	cd dashboard_project && uv run python manage.py flush --no-input
	cd dashboard_project && uv run python manage.py migrate

# Start a Redis server in development (if not installed, fallback to SQLite)
run-redis:
	redis-server || echo "Redis not installed, using SQLite fallback"

# Start all development services (web, redis, celery, celery-beat)
run-all:
	make run-redis & \
	make run & \
	make celery & \
	make celery-beat

# Test Celery task
test-celery:
	cd dashboard_project && uv run python manage.py test_celery

# Initialize data integration
init-data-integration:
	cd dashboard_project && uv run python manage.py create_default_datasource
	cd dashboard_project && uv run python manage.py create_default_datasource
	cd dashboard_project && uv run python manage.py test_celery

# Setup development environment
setup-dev: venv install-dev migrate create_default_datasource
	@echo "Development environment setup complete"

procfile:
	foreman start

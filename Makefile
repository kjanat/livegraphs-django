.PHONY: venv install install-dev lint test format clean run migrate makemigrations superuser setup-node

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
	uv pip install pre-commit
	pre-commit install

# Run pre-commit on all files
lint-all:
	pre-commit run --all-files

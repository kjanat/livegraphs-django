#!/bin/bash
# Run linting, formatting and type checking

echo "Running Ruff linter..."
uv run -m ruff check dashboard_project

echo "Running Ruff formatter..."
uv run -m ruff format dashboard_project

echo "Running Black formatter..."
uv run -m black dashboard_project

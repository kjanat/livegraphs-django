#!/bin/bash
# Run tests with coverage

echo "Running tests with coverage..."
uv run -m coverage run -m pytest
uv run -m coverage report -m

.PHONY: all-checks lint format test test-cov typecheck clean help setup

# Run all quality checks
all-checks: lint typecheck test
	@echo "All checks passed!"

# Lint code using ruff
lint:
	@echo "Running linter..."
	uv run ruff check

# Format code using ruff
format:
	@echo "Formatting code..."
	uv run ruff check --fix

# Run tests
test:
	@echo "Running tests..."
	uv run pytest

# Run tests with coverage
test-cov:
	@echo "Running tests with coverage..."
	uv run pytest --cov=sprout --cov-report=term-missing

# Run type checking with mypy
typecheck:
	@echo "Running type checking with mypy..."
	uv run mypy src

# Clean up temporary files
clean:
	@echo "Cleaning up..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf tmp/*

# Install development dependencies
setup:
	@echo "Installing development dependencies..."
	uv sync --dev

# Show help
help:
	@echo "Available targets:"
	@echo "  make all-checks  - Run all quality checks (lint, typecheck, test)"
	@echo "  make lint        - Run code linter (ruff)"
	@echo "  make format      - Format code (ruff)"
	@echo "  make test        - Run tests"
	@echo "  make test-cov    - Run tests with coverage report"
	@echo "  make typecheck   - Run type checking (mypy)"
	@echo "  make clean       - Clean up temporary files"
	@echo "  make setup       - Install development dependencies"
	@echo "  make help        - Show this help message"
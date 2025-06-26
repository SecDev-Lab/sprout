.PHONY: lint format test clean help setup

# Lint code using ruff
lint:
	@echo "Running linter..."
	uv run ruff check .

# Format code using ruff
format:
	@echo "Formatting code..."
	uv run ruff format .

# Run tests
test:
	@echo "Running tests..."
	uv run pytest

# Run tests with coverage
test-cov:
	@echo "Running tests with coverage..."
	uv run pytest --cov=. --cov-report=term-missing

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
	@echo "  make lint        - Run code linter (ruff)"
	@echo "  make format      - Format code (ruff)"
	@echo "  make test        - Run tests"
	@echo "  make test-cov    - Run tests with coverage report"
	@echo "  make clean       - Clean up temporary files"
	@echo "  make setup       - Install development dependencies"
	@echo "  make help        - Show this help message"
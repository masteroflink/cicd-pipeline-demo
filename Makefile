.PHONY: help build up down logs shell test test-cov lint format clean

# Default target
help:
	@echo "CI/CD Pipeline Demo - Development Commands"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Docker:"
	@echo "  build       Build the development Docker image"
	@echo "  up          Start the development server"
	@echo "  down        Stop all containers"
	@echo "  logs        View container logs"
	@echo "  shell       Open a shell in the container"
	@echo ""
	@echo "Testing:"
	@echo "  test        Run tests"
	@echo "  test-cov    Run tests with coverage report"
	@echo ""
	@echo "Linting:"
	@echo "  lint        Run all linters (black, ruff, mypy)"
	@echo "  format      Auto-format code with black and ruff"
	@echo ""
	@echo "Cleanup:"
	@echo "  clean       Remove containers and cache files"

# Docker commands
build:
	docker compose build

up:
	docker compose up

up-d:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

shell:
	docker compose run --rm api /bin/bash

# Testing
test:
	docker compose run --rm api pytest tests/ -v

test-cov:
	docker compose run --rm api pytest tests/ -v --cov=app --cov-report=term-missing --cov-report=html

# Linting
lint:
	docker compose run --rm api black --check src tests
	docker compose run --rm api ruff check src tests
	docker compose run --rm api mypy src --ignore-missing-imports

format:
	docker compose run --rm api black src tests
	docker compose run --rm api ruff check --fix src tests

# Cleanup
clean:
	docker compose down -v --remove-orphans
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true

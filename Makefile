# ==============================================================================
# Relent AI Makefile
# ==============================================================================

.PHONY: help install dev test lint format clean docker-build docker-up frontend-build

help:
	@echo "Relent AI - Development Commands:"
	@echo "  make install        Install backend and frontend dependencies"
	@echo "  make dev            Run local development servers (Backend & Frontend)"
	@echo "  make test           Run backend pytest test suite"
	@echo "  make lint           Check code with Ruff"
	@echo "  make format         Auto-format code with Ruff"
	@echo "  make frontend-build Build React production bundle"
	@echo "  make docker-build   Build Docker container"
	@echo "  make docker-up      Start full stack via Docker Compose"
	@echo "  make clean          Clean temporary files and cache directories"

install:
	python -m pip install --upgrade pip
	pip install -r requirements.txt
	cd frontend && npm install

dev:
	@echo "Starting Relent AI backend & frontend..."
	python server.py &
	cd frontend && npm run dev

test:
	pytest tests/ -v --cov=core --cov=utils

lint:
	ruff check .
	ruff format --check .

format:
	ruff check --fix .
	ruff format .

frontend-build:
	cd frontend && npm run build

docker-build:
	docker build -t relent-ai:latest .

docker-up:
	docker-compose up --build

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .coverage htmlcov dist build *.egg-info 2>/dev/null || true

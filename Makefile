.PHONY: install dev lint format typecheck test test-cov run worker migrate docker-up docker-down docker-test clean

# ── Dependencies ──────────────────────────────────────────────
install:
	pip install -e .

dev:
	pip install -e ".[dev]"

# ── Code quality ──────────────────────────────────────────────
lint:
	ruff check src/ tests/

format:
	ruff check src/ tests/ --fix
	ruff format src/ tests/

typecheck:
	mypy src/ --ignore-missing-imports

# ── Testing ───────────────────────────────────────────────────
test:
	pytest tests/ -v

test-cov:
	pytest tests/ --cov=src --cov-report=term-missing -v

# ── Run ───────────────────────────────────────────────────────
run:
	uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

worker:
	python -m src.workers.main

# ── Database ──────────────────────────────────────────────────
migrate:
	alembic upgrade head

migrate-create:
	alembic revision --autogenerate -m "$(msg)"

migrate-downgrade:
	alembic downgrade -1

# ── Docker ────────────────────────────────────────────────────
docker-up:
	docker compose up --build -d

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f

docker-test:
	docker compose -f docker-compose.test.yml up --build --abort-on-container-exit

# ── Cleanup ───────────────────────────────────────────────────
clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage test.db

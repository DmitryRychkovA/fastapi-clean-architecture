# Medical Study Metadata API

Production-grade FastAPI microservice for managing medical study metadata, built with **Clean Architecture** and distributed systems patterns.

---

## Architecture

```
src/
├── domain/                  # Business entities, repository interfaces, exceptions
│   ├── entities/            # Core dataclasses (Study) with business methods
│   ├── repositories/        # Abstract repository contracts (ABC)
│   └── exceptions.py        # Domain exceptions (StudyNotFoundError)
├── application/             # Use cases & DTOs
│   ├── use_cases/           # Business logic orchestration
│   └── dto/                 # Pydantic request/response schemas
├── infrastructure/          # External concerns
│   ├── database/            # SQLAlchemy models, connection, Alembic migrations
│   ├── repositories/        # Generic base repository + SQLAlchemy implementations
│   ├── broker/              # RabbitMQ connection pooling & message publishing
│   └── cache/               # Redis caching layer
├── presentation/            # API layer
│   ├── api/                 # FastAPI routers & dependency injection
│   └── middleware.py        # Request ID, logging, error handling middleware
└── workers/                 # Async RabbitMQ consumers with auto-restart
```

Layers follow the **Dependency Inversion Principle** — inner layers (domain, application) have zero knowledge of outer layers (infrastructure, presentation).

---

## Tech Stack

| Category | Technology |
|----------|-----------|
| **Framework** | FastAPI (async) |
| **ORM** | SQLAlchemy 2.0 (async, Mapped columns) |
| **Database** | PostgreSQL 16 |
| **Migrations** | Alembic |
| **Message Broker** | RabbitMQ (aio-pika, connection pooling) |
| **Cache** | Redis (async, JSON serialization) |
| **Logging** | structlog (JSON in production, console in dev) |
| **Validation** | Pydantic v2 |
| **Testing** | pytest + pytest-asyncio + httpx |
| **Linting** | ruff + mypy (strict) |
| **Containerization** | Docker (multi-stage, non-root) + Docker Compose |
| **CI** | GitHub Actions (PostgreSQL service) |

---

## Quick Start

### With Docker (full stack)

```bash
git clone https://github.com/yourusername/fastapi-clean-architecture.git
cd fastapi-clean-architecture
docker compose up --build
```

This starts: **app** + **worker** + **PostgreSQL** + **RabbitMQ** + **Redis**

- API: http://localhost:8000/docs
- RabbitMQ Management: http://localhost:15672 (guest/guest)

### With Make (local development)

```bash
make dev                    # Install dependencies
cp .env.example .env        # Configure environment
docker compose up db redis rabbitmq -d  # Start infrastructure
make migrate                # Run database migrations
make run                    # Start API server
make worker                 # Start async workers (separate terminal)
```

### Manual setup

```bash
python -m venv .venv
source .venv/bin/activate   # Linux/Mac
pip install -e ".[dev]"

docker compose up db -d
alembic upgrade head
uvicorn src.main:app --reload
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/health` | Health check (DB + Redis) |
| `POST` | `/api/v1/studies` | Create a new study |
| `GET` | `/api/v1/studies` | List studies (pagination + filtering) |
| `GET` | `/api/v1/studies/{id}` | Get study by ID |
| `PATCH` | `/api/v1/studies/{id}` | Partial update study |
| `DELETE` | `/api/v1/studies/{id}` | Delete study |

### Filtering

```
GET /api/v1/studies?modality=CT&status=pending&patient_id=PAT-001&limit=10
```

### Health Check Response

```json
{
  "status": "ok",
  "db": "connected",
  "cache": "connected"
}
```

---

## Testing

```bash
make test                   # Run all tests
make test-cov               # Run with coverage report
make lint                   # Run ruff linter
make typecheck              # Run mypy strict mode
```

Run tests with real PostgreSQL:

```bash
make docker-test
```

**Test stats:** 40 tests | 85% coverage | ruff clean | mypy strict clean

---

## Project Structure

```
.
├── src/
│   ├── main.py                           # App factory + lifespan
│   ├── config.py                         # Settings factory (Local/Prod/Test)
│   ├── logging_config.py                 # structlog configuration
│   ├── domain/
│   │   ├── entities/study.py             # Study dataclass + business methods
│   │   ├── repositories/study_repository.py  # Abstract repository (ABC)
│   │   └── exceptions.py                 # DomainError, StudyNotFoundError
│   ├── application/
│   │   ├── dto/study_dto.py              # Pydantic schemas + from_entity()
│   │   └── use_cases/                    # Create, Get, List, Update, Delete
│   ├── infrastructure/
│   │   ├── database/
│   │   │   ├── connection.py             # AsyncEngine + session factory
│   │   │   ├── models.py                 # SQLAlchemy ORM model
│   │   │   └── migrations/              # Alembic migrations
│   │   ├── repositories/
│   │   │   ├── base.py                   # Generic BaseRepository[ModelT, EntityT]
│   │   │   └── sqlalchemy_study_repository.py
│   │   ├── broker/
│   │   │   ├── connection.py             # RabbitMQ pool init/shutdown
│   │   │   └── publisher.py             # Message publishing
│   │   └── cache/
│   │       └── redis.py                  # Redis get/set/invalidate
│   ├── presentation/
│   │   ├── middleware.py                 # Request ID, logging, error handler
│   │   └── api/
│   │       ├── router.py                # Endpoints + health check
│   │       └── dependencies.py          # DI chain (interface types)
│   └── workers/
│       ├── main.py                       # Worker entry point
│       ├── consumer.py                   # Base RabbitMQ consumer
│       └── study_events.py              # Study event handlers
├── tests/
│   ├── conftest.py                       # Fixtures (engine, session, client)
│   ├── unit/                             # Entity, use case, exception tests
│   └── integration/                      # API endpoint tests
├── alembic.ini
├── Dockerfile                            # Multi-stage, non-root user
├── docker-compose.yml                    # Full stack (app+worker+db+rmq+redis)
├── docker-compose.test.yml              # Test stack (PostgreSQL + pytest)
├── Makefile
├── pyproject.toml
└── CHANGES.md                            # Detailed changelog
```

---

## Configuration

Environment-specific settings via `APP_ENV`:

| `APP_ENV` | Class | Debug | Testing |
|-----------|-------|-------|---------|
| `local` | `LocalSettings` | True | False |
| `production` | `ProductionSettings` | False | False |
| `testing` | `TestSettings` | False | True |

See `.env.example` for all available variables.

---

## Makefile Commands

```bash
make install        # Install production dependencies
make dev            # Install dev dependencies
make lint           # Run ruff linter
make format         # Auto-fix + format
make typecheck      # Run mypy strict
make test           # Run pytest
make test-cov       # Run pytest with coverage
make run            # Start uvicorn dev server
make worker         # Start async RabbitMQ workers
make migrate        # alembic upgrade head
make migrate-create # alembic revision --autogenerate
make docker-up      # docker compose up --build -d
make docker-down    # docker compose down
make docker-test    # Run tests in Docker with PostgreSQL
make clean          # Remove caches and temp files
```

---

## Design Decisions

- **Authentication intentionally omitted** to keep focus on architecture patterns. In production, add JWT/OAuth2 middleware in `presentation/` layer.
- **Workers, broker, and migrations excluded from coverage** — they require live infrastructure (RabbitMQ, PostgreSQL) and are tested via `docker-compose.test.yml`.

---

## License

MIT

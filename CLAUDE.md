# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build & Run Commands

```bash
# Install dependencies
poetry install

# Run development server (from src/)
python src/main.py                    # starts on 0.0.0.0:8080
uvicorn src.main:app --reload         # alternative with hot reload

# Run tests
pytest src/test/

# Pre-commit hooks (black, flake8, isort, toml-sort)
pre-commit install                    # one-time setup
pre-commit run --all-files            # manual run

# Code formatting
black --line-length 120 .
isort --profile black .
```

## Architecture

This is a **layered Clean Architecture** FastAPI project with a single `auth` module as reference implementation.

### Request Flow

```
HTTP Request → Middleware (JWT validation) → Endpoint → UseCase → Service(s) → Repository → DB
```

### Layer Responsibilities

- **Endpoint** (`app/{module}/endpoint/`): Route handlers, receives Pydantic request models, delegates to UseCases
- **UseCase** (`app/{module}/usecases/`): Orchestrates business workflows, coordinates multiple services for complete use cases (e.g., login, register, logout)
- **Service** (`app/{module}/services/`): Business logic (password verification, token generation, Redis caching)
- **Repository** (`app/{module}/repository/`): Raw SQL queries via async SQLAlchemy sessions
- **Domain** (`app/{module}/domain/`): Plain dataclass entities with `to_dict()`/`from_dict()` conversion
- **Model** (`app/{module}/model/request|response/`): Pydantic v2 request/response schemas

### Dependency Injection

Uses `dependency-injector` library with constructor-based DI and `@inject` decorator.

- **Root container** (`src/container.py`): Provides Redis, DB engine, Config, Logging
- **Module container** (`app/auth/container.py`): Provides module-specific repositories/services
- Wiring is automatic via `WiringConfiguration` — containers wire to their declared packages
- In endpoints, dependencies are resolved via `FastAPI Depends()` + `@inject`

### Database

- **Async SQLAlchemy 2.0** with `asyncpg` driver against PostgreSQL
- Session management via `AsyncEngine.session()` context manager (auto-commit/rollback)
- Schema models in `infrastructure/db/schema/` extend a shared `Base`
- Helper functions `exec()`, `first()`, `all()` in `sqlalchemy.py` for raw SQL execution

### Authentication

- JWT access + refresh tokens via `python-jose` and `passlib` bcrypt
- `middleware.py` validates tokens on every request, sets `request.state.user`
- Public routes hardcoded in middleware: `/docs`, `/redoc`, `/api/v1/auth/login`, `/api/v1/auth/register`
- Redis caches user info on login with key pattern `cache_user_info_{login_id}`

### Error Handling

Custom `APIException` hierarchy in `src/errors.py`. Middleware catches these and returns structured JSON. Key exceptions: `NotAuthorization`, `ExpireJwtToken`, `NotFoundUserEx`, `BadPassword`, `DuplicateUserEx`.

## Key Configuration

- **Config**: `src/config.py` — Pydantic `BaseSettings` loading from `.env`, with `LocalConfig`/`TestConfig`/`ProdConfig` variants
- **Environment**: Copy `src/.env.example` to `src/.env` — requires JWT secrets, PostgreSQL, and Redis connection details
- **Formatting**: black (line-length=120), isort (black profile), flake8
- **Pre-commit**: `.pre-commit-config.yaml` runs formatters/linters automatically on commit

## Conventions

- All database operations are async (`async/await` throughout)
- Routes are aggregated in `app/{module}/routes.py` and registered in `src/presentation.py`
- Logging uses structured JSON format via `LogAdapter` in `src/logs/log.py` (includes KST timestamps)
- Korean language comments exist throughout the codebase

## Archive

Historical documentation and completed work can be found in the `archive/` directory:

- **project_analysis_report.md** - Comprehensive project analysis (improvements implemented in commit `0c8c8ef`)
- **USECASE_ANALYSIS_AND_REFACTORING.md** - UseCase pattern refactoring guide (refactoring completed)

See `archive/README.md` for full index and usage guidelines.

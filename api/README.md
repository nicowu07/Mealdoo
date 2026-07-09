# Mealdoo API

FastAPI backend for Mealdoo, providing REST endpoints for household grocery 
management, receipt processing, and meal planning.

## Tech Stack

- Python 3.12 + FastAPI
- SQLAlchemy 2.0 (ORM)
- Alembic (migrations)
- PostgreSQL 16 + pgvector (data + vector search)
- pydantic-settings (config)
- uv (package management)

## Project Structure

```
api/
├── app/
│   ├── main.py           # FastAPI application entry
│   ├── config.py         # Settings loaded from environment
│   ├── db.py             # Database engine and session
│   ├── models/           # SQLAlchemy ORM models
│   ├── schemas/          # Pydantic request/response schemas
│   ├── routers/          # FastAPI route handlers
│   └── services/         # Business logic
├── alembic/              # Database migrations
└── pyproject.toml
```

## Common Commands

```bash
# Run development server
uv run uvicorn app.main:app --reload

# Create a new migration after model changes
uv run alembic revision --autogenerate -m "description"

# Apply migrations
uv run alembic upgrade head

# Rollback last migration
uv run alembic downgrade -1

# Format and lint code
uv run ruff format .
uv run ruff check --fix .
```
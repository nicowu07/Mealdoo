<div align="center">
  <img src="./docs/assets/logo.svg" alt="Mealdoo logo" width="180"/>
  
  # Mealdoo
  
  A web application for household grocery management and meal planning.
</div>

---

## 🥑 Overview

Mealdoo helps households track pantry inventory, plan meals, and optimize grocery shopping around local supermarket specials. It combines computer vision for receipt and product recognition with LLM-based meal planning.

## Planned Features

- 🧾 **Receipt scanning**: Extract items and expiry dates automatically via OCR
- 📸 **Product recognition**: Identify pantry items from photos using vision models
- 📖 **Recipe management**: Store recipes with ingredient requirements and cooking time
- 🛒 **Shopping recommendations**: Suggest purchases based on inventory, usage patterns, and current Australian supermarket specials
- 📅 **Meal planning**: Generate multi-day meal plans from pantry stock, shopping list, saved recipes, and household size

## Tech Stack (planned)

- **Frontend**: Next.js 14 (App Router), TypeScript, Tailwind CSS
- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL with pgvector
- **AI**: Cloud Vision API (OCR), CLIP embeddings (product recognition), LLM APIs (meal planning)
- **Deployment**: DigitalOcean

## 🚧 Status
Schema and database layer complete. API and frontend in progress.

- ✅ Database schema (10 tables, 5 enums, 15 foreign keys)
- ✅ Docker Compose local development environment
- ✅ SQLAlchemy models + Alembic migrations
- 🚧 FastAPI backend routes
- 📅 Next.js frontend

## 🛠️ Development

### Prerequisites
- Docker Desktop with WSL2 backend (or native Docker on Linux/macOS)
- Python 3.12+ (managed by [uv](https://docs.astral.sh/uv/))

### Setup

1. Clone the repository
2. Copy `.env.example` to `.env` and configure passwords
3. Start Postgres:
```bash
   docker compose up -d
```
4. Set up the backend:
```bash
   cd api
   cp .env.example .env  # configure DATABASE_URL
   uv sync
   uv run alembic upgrade head
```
5. Verify the API runs:
```bash
   uv run uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.

## Documentation

- [Database design](./docs/database-design.md)

## 📄 License

MIT
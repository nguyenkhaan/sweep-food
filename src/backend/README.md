# Sweep Food Backend

Backend API for inventory batches, expiry tracking, authentication, and meal recommendations.

## Technology

![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.141-009688?logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Neon-4169E1?logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-7.4-DC382D?logo=redis&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)
![WireMock](https://img.shields.io/badge/WireMock-3.13.2-FF6F00)

## Requirements

- Python 3.11
- uv 0.12.5
- A Neon PostgreSQL connection string

## Setup and Run

Run these commands from this directory (`src/backend`):

```bash
cp .env.example .env
uv sync
uv run main.py
```

Set `DATABASE_URL` in `.env`, or contact Cloudian for the project environment file.

The API runs at `http://localhost:4000/api`.

You can visit API docs here: `http://localhost:4000/docs`

```text
GET /api/health/liveness
GET /api/health/error
GET /api/health/text
```

## Structure

```text
.
├── main.py                  # Application entry point
├── alembic/                 # Async Alembic environment and revisions
│   └── versions/
├── docs/                    # PRD, database contract, ADRs, and task specs
├── src/
│   ├── app.py               # FastAPI application factory and lifespan
│   ├── db.py                # Async SQLAlchemy session lifecycle
│   ├── base/
│   │   └── constant/        # Shared constants, including email templates
│   ├── core/                # Settings, OpenAPI, and global exception handlers
│   ├── helper/              # OTP generation and password hashing helpers
│   ├── middleware/          # JWT authentication and role dependencies
│   ├── model/               # SQLAlchemy base, enums, and one *_model.py per table
│   ├── module/              # Feature modules
│   │   ├── auth/            # Registration, login, OTP, and session APIs
│   │   ├── health/          # Health and local service-test APIs
│   │   └── user/            # Current user profile, email, and phone APIs
│   ├── service/             # JWT, Redis, OTP, SMS, and email services
│   ├── template/            # Jinja HTML email templates
│   └── test/                # Unit, API-contract, and optional integration tests
├── wiremock/
│   ├── mappings/            # Local SMS provider fixtures
│   └── __files/             # WireMock response bodies
├── docker-compose.yaml      # API, Redis, WireMock, and Mailpit local services
└── pyproject.toml           # Dependencies and quality-tool configuration
```

Each feature module uses four files: `*_router.py`, `*_service.py`, `*_dependency.py`, and `*_dto.py`.

Build with Cloudian 💙 Cloud

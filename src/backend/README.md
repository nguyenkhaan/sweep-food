# Sweep Food Backend

Backend API for inventory batches, expiry tracking, authentication, and meal recommendations, including in-process AI (recommendation, OCR, ASR, and pantry text parsing).

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

## Email delivery

Development uses Mailpit without SMTP authentication. `docker compose up` overrides
the API's SMTP host to `mailpit:1025`; its inbox UI is at
`http://localhost:8025`. For a direct local run, `.env.example` points to
`localhost:1025` instead.

On Render, configure the API service with these environment variables:

```text
ENV=production
EMAIL_SMTP_HOST=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_SMTP_USERNAME=<your Gmail address>
EMAIL_SMTP_PASSWORD=<new Google App Password, stored as a secret>
EMAIL_SMTP_USE_STARTTLS=true
EMAIL_FROM=<the same Gmail address or a verified send-as alias>
```

Production requires STARTTLS and credentials; missing values fail closed. The
public `/api/health/test-email` route is development-only and is unavailable in
production. Verify production delivery through a real OTP flow. Render Free Web
Services block outbound SMTP ports, including 587, so Gmail SMTP requires a
paid Render instance or a different delivery provider/API. Never put the App
Password in the image, repository, or shared `.env` file.

You can visit API docs here: `http://localhost:4000/docs`

```text
GET /api/health/liveness
GET /api/health/error
GET /api/health/text
```

## FreshCheck operations

FreshCheck release build, Neon migration, activation, smoke verification, and
rollback procedures are documented in
[`docs/freshcheck-operations-runbook.md`](docs/freshcheck-operations-runbook.md).

## Structure

```text
.
├── main.py                  # Application entry point
├── AI/                      # Central home for all in-process AI workloads
│   ├── catalog/             # Catalog importer and in-memory snapshot loaded from Postgres
│   ├── recommendation/      # LightGBM ranking engine and heuristic fallback
│   ├── extraction/          # OpenAI OCR, Groq ASR, and extraction orchestration
│   ├── smart_parser/        # Four-tier pantry text parser
│   ├── llm/                 # Shared OpenAI client
│   └── data/                # Bundled catalog, master ingredients, and ranker model
├── alembic/                 # Async Alembic environment and revisions
│   └── versions/
├── docs/                    # Product planning, database notes, ADRs, and runbooks
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
│   │   ├── inventory/       # Batch inventory and ledger-backed mutations
│   │   ├── recommendations/ # Recommendation API over AI.recommendation
│   │   └── user/            # Current user profile and verified-contact APIs
│   ├── service/             # Shared auth, delivery, and domain services
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

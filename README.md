# AI PRODUCTIVITY PLATFORM

A production-inspired REST API for managing todo items, built with **FastAPI** and **Python**. Designed as a learning project to demonstrate professional backend architecture patterns applied to a simple, approachable domain.

---

## Version History

| Version | Major Features |
|----------|----------------|
| **v1.0** | JSON-based Todo CRUD |
| **v1.1** | PostgreSQL (AWS RDS), SQLAlchemy, Alembic |
| **v1.2** | AWS Cognito Authentication, JWT Authorization, Multi-user support |
| **v1.3** | Priority, Category, Filtering, Extended Testing |
| **v2.0** | Project renamed to AI Productivity Platform |
| **v2.1** | Transcript Module, AWS S3 Integration, Transcript APIs, Storage Service, Health Checks |
| **v2.2** *(Current)* | Docker, RabbitMQ, Celery, ETL Infrastructure, Processing Lifecycle |


> **Current Version: v2.2 (In Progress)**

Current development focuses on building the infrastructure required for asynchronous transcript processing, semantic search, and Retrieval-Augmented Generation (RAG).

---

## Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [Architecture](#architecture)
- [API Endpoints](#api-endpoints)
- [Schemas](#schemas)
- [Getting Started](#getting-started)
- [Database Migrations](#database-migrations)
- [Running Tests](#running-tests)

---

## Overview

This project is evolving from a production-inspired Todo backend into an AI Productivity Platform.

Version 1.x focuses on building a production-grade backend foundation using FastAPI, PostgreSQL, AWS Cognito, SQLAlchemy, and layered architecture. Future versions extend this backend with transcript ingestion, cloud storage, Retrieval-Augmented Generation (RAG), semantic search, and AI-powered productivity features.

**Key features:**

- 🔐 **AWS Cognito authentication** — user sign-up, confirmation, login, token refresh, global sign-out
- 🔑 **JWT authorization** — every todo endpoint requires a valid access token
- 👤 **Multi-user isolation** — users can only see and modify their own todos
- 🏷️ **Priority & Category support** — enum-based fields with request validation
- 🔍 **Filtering endpoints** — retrieve todos by completion status, priority, or category
- 🗄️ **PostgreSQL + Alembic migrations** — production-grade database with version-controlled schema evolution
- 🧪 **Comprehensive test suite** — 60 automated tests covering API, authentication, service, repository, and storage layers
- 📝 **Request logging & middleware** — structured logs for every request

### AI Productivity Platform

Current AI capabilities

- Transcript Upload
- Transcript Download
- Transcript Deletion
- Transcript Authorization
- AWS S3 Storage
- Background Processing Infrastructure
- Celery Worker
- RabbitMQ Message Queue
- Processing Status Tracking
- ETL Service Architecture


The codebase is intentionally structured to mirror real-world production patterns — layered concerns, dependency injection, custom exception handling, and isolated test environments.

![FastAPI Production](FastAPI_production.PNG)

**Tech Stack:**

| Tool | Purpose |
|---|---|
| FastAPI 0.138 | Web framework |
| Uvicorn 0.49 | ASGI server |
| Pydantic v2 | Data validation and serialization |
| pydantic-settings | Environment configuration |
| SQLAlchemy | ORM and database session management |
| psycopg2-binary | PostgreSQL driver |
| AWS RDS (PostgreSQL) | Cloud-hosted relational database |
| **AWS Cognito** | **User authentication & user pool management** |
| **boto3** | **AWS SDK for Python (Cognito integration)** |
| **PyJWT** | **JWT token decoding and verification** |
| **python-jose** | **JWT signature validation (JWKS)** |
| **requests** | **HTTP client for JWKS endpoint** |
| Alembic | Database migration tool |
| Pytest 9.1 | Testing framework |
| HTTPX | HTTP client for testing |
| Docker | Containerization |
| Docker Compose | Local orchestration |
| RabbitMQ | Message Broker |
| Celery | Background Task Queue |

---

## Project Structure

```
app/
├── main.py                           # FastAPI app factory (no startup event — Alembic owns schema)
│
├── api/
│   ├── v1/
│   │   ├── router.py                 # Combines all v1 route groups
│   │   └── routes/
│   │       ├── health.py             # GET /api/v1/health
│   │       └── todos.py              # Todo CRUD + Filtering endpoints (requires auth)
│   └── v2/
│       ├── router.py
│       └── routes/
│           └── transcript.py         # Transcript Upload, Delete, Search (requires auth)
│
│
├── celery/
│   ├── celery_app.py                 # asynchronous task processing
│   └── tasks/
│       └── transcript_tasks.py       # Background task Logic
│
├── auth/
│   ├── cognito.py                    # AWS Cognito client (sign-up, login, token refresh, sign-out)
│   ├── jwt_verifier.py               # JWT verification (downloads JWKS, validates signatures)
│   ├── dependencies.py               # get_current_user, get_current_db_user
│   ├── exceptions.py                 # Auth-specific exceptions
│   ├── router.py                     # /auth endpoints (signup, confirm, login, refresh, sign-out)
│   ├── schemas.py                    # TokenClaims, LoginRequest/Response, etc.
│   └── service.py                    # Auth service layer
│
├── core/
│   ├── config.py                     # Settings loaded from .env (pydantic-settings)
│   ├── dependencies.py               # FastAPI dependency injection chain
│   ├── exception_handlers.py         # Maps custom exceptions to HTTP responses
│   ├── logging.py                    # Logging configuration
│   └── middleware.py                 # Request/response timing, logging, security headers
│
├── database/
│   ├── base.py                       # SQLAlchemy DeclarativeBase
│   ├── database.py                   # Engine, SessionLocal, get_db() dependency
│   └── models.py                     # TodoModel + UserModel + Transcript ORM definitions
│
├── schemas/
│   ├── todo.py                       # Todo Pydantic models (includes user_id)
│   ├── user.py                       # User Pydantic models (UserCreate, CurrentUserResponse)
│   └── transcript.py                 # transcript Pydantic model (TranscriptCreate, TranscriptResponse)
│
├── services/
│   ├── todo_service.py               # Todo business logic (now user-scoped)
│   ├── user_service.py               # User business logic (get_or_create on first login)
│   ├── transcript_service.py         # transcript business logic (get_or_create for todo task)
│   ├── storage_service.py            # Storage business Logic (get_or_delete for S3)
│   └── etl_service.py                # Extract Transform Load Logic (For RAG pipeline)
│
├── repositories/
│   ├── postgres_todo_repository.py   # Todo CRUD with user_id filtering
│   ├── postgres_user_repository.py   # User CRUD via Cognito sub lookup
│   ├── json_todo_repository.py       # Legacy JSON CRUD (retained for reference)
│   └── transcript_repository.py      # transcript CRD with user_id & Todo_id filtering
│
├── storage/
│   └── json_storage.py               # Legacy JSON file I/O (retained for reference)
│
├── exceptions/
│   └── todo.py                       # TodoNotFoundError custom exception
│
├── tests/
│   ├── conftest.py                   # Pytest fixtures (SQLite in-memory, auth bypass)
│   ├── fakes.py                      # FakeTodoRepository, FakeCognitoClient, FakeJWTVerifier
│   ├── test_api.py                   # API integration tests (SQLite, isolated)
│   ├── test_auth.py                  # Auth endpoint tests (fake Cognito)
│   ├── test_service.py               # Service unit tests (in-memory fake)
│   ├── test_repository.py            # JSON repository unit tests
│   └── test_storage.py               # JSON storage tests
│
migrations/
├── env.py                            # Alembic environment (reads DATABASE_URL from .env)
├── script.py.mako                    # Migration file template
└── versions/
    ├── 20260703_0637_fabbfc95d6f4_initial_schema.py              # Baseline: todos table
    ├── 20260707_0325_d463e870d8f6_add_users_table_and_user_relationship.py  # Users + FK
    ├── 20260709_0503_7e1a7423a064_addition_of_priority_category_to_todo_.py  # Users (Priority + Category)
    ├── 20260710_0431_29027f8a809c_add_transcript_table.py                      # transcript table (FK todo_id)
    └── 20260714_0444_1dca2c4573a2_addition_processing_status_to_transcript.py  # Transcripts (Status, Started_at, Completed_at, error_msg)
alembic.ini                           # Alembic configuration
```

---

## Architecture

The app follows a **layered architecture** with **JWT-based authentication** — each layer has a single responsibility and communicates only with the layer directly below it.

```
                    HTTP Request
                          │
                          ▼
                   Authentication
                          │
                          ▼
                       Routes
                          │
                          ▼
                Transcript Service
                          │
        ┌─────────────────┴────────────────┐
        ▼                                  ▼
 Storage Service                    ETL Service
        │                                  │
        ▼                                  ▼
      AWS S3                     Celery + RabbitMQ
                                            │
                                            ▼
                                      Celery Worker
                                            │
                                            ▼
                                   Transcript Repository
                                            │
                                            ▼
                                       PostgreSQL
```

## Transcript Processing Pipeline

The platform now supports asynchronous transcript processing.

Current workflow

Client

  ↓

Upload Transcript

   ↓

AWS S3

   ↓

Save Metadata

   ↓

Status = UPLOADED

   ↓

Submit Celery Task

   ↓

RabbitMQ Queue

   ↓

Celery Worker

   ↓

Status = PROCESSING

   ↓

ETL Pipeline (Coming)

   ↓

Status = READY


## Transcript Lifecycle

Each transcript moves through a processing lifecycle.

UPLOADED

   ↓

PROCESSING

   ↓  

READY

or

FAILED

Processing metadata stored in PostgreSQL

- processing_status
- processing_started_at
- processing_completed_at
- error_message


## Docker

The project now supports containerized development.

Services

- FastAPI
- RabbitMQ
- Celery Worker

Managed using

docker-compose.yml



### Health

Application startup validates

✓ PostgreSQL

✓ AWS S3

Future

- RabbitMQ
- ChromaDB

---

### Todos

**⚠️ All todo endpoints require authentication** — you must include a valid JWT access token in the `Authorization: Bearer <token>` header.

| Method | Path | Description | Success Status |
|---|---|---|---|
| GET | `/api/v1/todos` | List all todos **for the authenticated user** | 200 |
| POST | `/api/v1/todos` | Create a new todo | 201 |
| GET | `/api/v1/todos/{todo_id}` | Get a todo by UUID (user-scoped) | 200 |
| PUT | `/api/v1/todos/{todo_id}` | Update a todo (user-scoped) | 200 |
| DELETE | `/api/v1/todos/{todo_id}` | Delete a todo (user-scoped) | 204 |
| GET | `/api/v1/todos/completed/{completed}` | Filter todos by completion status | 200 |
| GET | `/api/v1/todos/priority/{priority}` | Filter todos by priority | 200 |
| GET | `/api/v1/todos/category/{category}` | Filter todos by category | 200 |
| POST | `/api/v2/todos/{todo_id}/transcript` | Upload a new transcript for todo | 201 |
| GET | `/api/v2/todos/{todo_id}/transcript` | Get a transcript by todo if uploaded | 200 |
| DELETE | `/api/v2/transcripts/{transcript_id}` | Delete transcript by transcript id | 204 |
| GET | `/api/v2/transcripts/{transcript_id}` | Get transcript by transcript id | 200 |

#### Error Responses

| Scenario | Status | Body |
|---|---|---|
| Missing or invalid token | 401 | `{"detail": "Invalid or expired token."}` |
| Todo not found (or belongs to another user) | 404 | `{"detail": "Todo with id '...' was not found."}` |
| Invalid UUID format | 422 | Pydantic validation error |
| Invalid request body | 422 | Pydantic validation error |

---

## Schemas

### `TodoCreate` (POST request body)

| Field | Type | Rules |
|---|---|---|
| `title` | `string` | Required, 3–100 characters |
| `description` | `string \| null` | Optional, max 500 characters |
| `priority` | `Priority` | Required. One of: `low`, `medium`, `high` |
| `category` | `Category` | Required. One of: `work`, `personal` |

### `TodoUpdate` (PUT request body)

All fields are optional — send only the fields you want to change.

| Field | Type |
|---|---|
| `title` | `string \| null` |
| `description` | `string \| null` |
| `completed` | `boolean \| null` |
| `priority` | `Priority \| null` |
| `category` | `Category \| null` |

### `TodoResponse`

| Field | Type |
|---|---|
| `id` | `UUID` |
| `title` | `string` |
| `description` | `string \| null` |
| `completed` | `boolean` |
| `user_id` | `string \| null` |
| `priority` | `Priority` |
| `category` | `Category` |
| `created_at` | `datetime (UTC)` |
| `updated_at` | `datetime (UTC)` |

### `TodoListResponse`

| Field | Type |
|---|---|
| `total` | `integer` |
| `items` | `TodoResponse[]` |

---

## Getting Started

### Prerequisites

- Python 3.11+
- A PostgreSQL database (local or cloud — e.g. AWS RDS)

### Installation

```bash
# Clone the repository
git clone <repo-url>
cd Fast_api

# Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1   # Windows PowerShell
# source .venv/bin/activate   # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the project root:

```env
APP_NAME=ToDo API
APP_VERSION=1.2.0
DEBUG=True
DATA_FILE=app/data/todo.json
DATABASE_URL=postgresql+psycopg2://<user>:<password>@<host>:<port>/<database>

# AWS Cognito settings
AWS_REGION=us-east-1
COGNITO_USER_POOL_ID=us-east-1_XXXXXXXXX
COGNITO_CLIENT_ID=xxxxxxxxxxxxxxxxxxxxxxxxxx
COGNITO_CLIENT_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

| Variable | Description |
|---|---|
| `APP_NAME` | Name shown in API metadata |
| `APP_VERSION` | Version shown in API metadata |
| `DEBUG` | Enables debug mode |
| `DATA_FILE` | Path to legacy JSON file (unused in v1.2, kept for reference) |
| `DATABASE_URL` | Full SQLAlchemy connection string to your PostgreSQL database |
| `AWS_REGION` | AWS region where your Cognito User Pool is hosted |
| `COGNITO_USER_POOL_ID` | Your Cognito User Pool ID |
| `COGNITO_CLIENT_ID` | Your Cognito App Client ID |
| `COGNITO_CLIENT_SECRET` | Your Cognito App Client Secret |

> **First-time setup:** run `alembic upgrade head` after configuring `.env` to create all tables (including `users` and `todos`) via the migration history. See the [Database Migrations](#database-migrations) section below.

### Running the Server

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.

Interactive docs are served automatically at:
- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

---

## Database Migrations

Schema changes are managed with **Alembic**. Every change to a model column is captured in a versioned migration file and applied to the database in a controlled, reversible way.

### Common commands

```bash
# Apply all pending migrations (use on a fresh database or after pulling new migrations)
alembic upgrade head

# Check which revision the database is currently at
alembic current

# Show the full migration history
alembic history --verbose

# Roll back the last applied migration
alembic downgrade -1
```

### Adding a new column (example workflow)

**Step 1 — Update the model** in `app/database/models.py`:
```python
priority: Mapped[int] = mapped_column(Integer, default=0)
```

**Step 2 — Generate the migration** (Alembic diffs the model against the live DB):
```bash
alembic revision --autogenerate -m "add_priority_to_todos"
```

**Step 3 — Review** the generated file in `migrations/versions/` and confirm the SQL is correct.

**Step 4 — Apply it:**
```bash
alembic upgrade head
```

> `alembic.ini` does **not** contain the database URL. Alembic reads `DATABASE_URL` directly from `.env` at runtime, so credentials are never stored in a config file.

---

## Running Tests

```bash
pytest
```

The project currently contains **60 automated tests** covering API, authentication, business logic, repositories, and storage.

| File | Layer | Approach | Database |
|---|---|---|---|
| `test_api.py` | API (integration) | CRUD, filtering endpoints, validation | SQLite in-memory |
| `test_auth.py` | Authentication | Fake Cognito authentication flow | None |
| `test_service.py` | Service | In-memory fake repositories | None |
| `test_repository.py` | Repository | CRUD + filtering operations | None |
| `test_storage.py` | Storage | Storage fixture validation | None |

> Integration tests use a shared **in-memory SQLite database** built from the same SQLAlchemy models as production. The schema is identical, the production PostgreSQL database is never opened, and all rows are cleared between tests. This also makes the test suite run significantly faster (~24 s vs ~65 s over the network).

Run with verbose output:

```bash
pytest -v
```

## License

See [LICENSE](LICENSE).


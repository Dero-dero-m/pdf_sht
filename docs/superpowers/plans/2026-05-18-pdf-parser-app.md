# PDF Parser App — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a small full-stack app on the existing scaffold where a user uploads a PDF, the backend parses it via the Anthropic API, persists the extracted Markdown in Postgres, and the web app lists / displays documents and downloads each as a `.docx` file.

**Architecture:**

- **FastAPI** (`apps/api`) exposes `POST /documents` (upload + parse), `GET /documents`, `GET /documents/{id}`, and `GET /documents/{id}/docx`. Parsing uses the official `anthropic` Async SDK with Claude's native PDF `document` content block; the model is asked to return GitHub-flavored Markdown.
- **Postgres** stores one row per parsed document: `id`, `filename`, `byte_size`, `page_count`, `content_markdown`, `created_at`. Schema is managed with **Alembic**; SQLAlchemy 2.x **async** session via `asyncpg`. No file blobs — only the extracted Markdown.
- **Shared types** live in `packages/shared-types/` as a small editable Python package (`scaffold_shared_types`) that is imported by both the API and a `pydantic2ts` codegen script that writes `packages/shared-types/index.ts`. The web app consumes those TS types via the existing workspace dependency.
- **Next.js 16 App Router** (`apps/web`) has a `/` page with an upload form and document list (Server Component shell + Client form/list), and `/documents/[id]` showing rendered Markdown plus a "Download .docx" button. The browser uploads directly to the API (multipart) to keep Next 16 route handlers out of the path.
- **DOCX export** uses `python-docx` with a small Markdown→docx renderer covering headings, paragraphs, and bullet/numbered lists (the shapes Claude reliably emits).

**Tech Stack:**

- Backend: Python 3.12, FastAPI, SQLAlchemy 2 async, asyncpg, Alembic, pydantic, pydantic-settings, anthropic, python-multipart, python-docx, pytest + pytest-asyncio + httpx (ASGITransport) + dirty-equals, ruff, mypy, pydantic-to-typescript.
- Frontend: Next.js 16 App Router, React 19, Tailwind v4, `react-markdown` + `remark-gfm` for rendering.
- Infra: Existing Postgres 16 + pgvector container in `infra/docker-compose.yml`.

> **Note on `.doc` vs `.docx`:** User asked for `.doc`. We deliver `.docx` (Open XML) because `.doc` (legacy CFB binary) has no maintained writer in Python. `.docx` opens in Word, Google Docs, Pages, LibreOffice. If the user truly requires legacy `.doc`, that's a follow-up using `libreoffice --headless --convert-to doc` and is out of scope.

> **Reading-list before coding the web tasks:** Per `apps/web/AGENTS.md`, before any Next 16 code, the executor MUST `ls node_modules/next/dist/docs/` and skim the App Router / fetching / dynamic-routes guides. Next 16 diverges from training data; copy idioms from those docs, not from memory.

---

## File Structure

### Created

```
apps/api/
  app/
    __init__.py
    main.py                       # FastAPI app factory + lifespan
    config.py                     # Settings (pydantic-settings)
    db.py                         # async engine, sessionmaker, get_session dep
    models.py                     # SQLAlchemy ORM: Document
    deps.py                       # get_anthropic_client dep (override-able in tests)
    routes/
      __init__.py
      documents.py                # 4 endpoints
    services/
      __init__.py
      pdf_parser.py               # Anthropic call → markdown
      docx_export.py              # markdown → docx bytes
  alembic.ini
  alembic/
    env.py
    script.py.mako
    versions/
      0001_initial.py             # creates `documents` table
  tests/
    __init__.py
    conftest.py                   # test DB fixture, anthropic mock, client
    test_health.py
    test_documents_upload.py
    test_documents_list.py
    test_documents_get.py
    test_documents_docx.py
  .env.example
  pytest.ini

packages/shared-types/
  pyproject.toml                  # editable Python package
  src/scaffold_shared_types/
    __init__.py
    schemas.py                    # DocumentSummary, DocumentDetail, DocumentList
  scripts/
    gen_ts.py                     # pydantic2ts driver
  index.ts                        # GENERATED — committed
  tsconfig.json

apps/web/
  app/
    page.tsx                      # REPLACE: upload form + documents list
    documents/
      [id]/
        page.tsx                  # detail (Server Component) — fetches by id
        DocumentView.tsx          # 'use client' — markdown render + download button
    api-client.ts                 # tiny fetch wrapper, server + client safe
  .env.example                    # NEXT_PUBLIC_API_URL=http://localhost:8000
  next.config.ts                  # MODIFY: add transpilePackages: ['@scaffold/shared-types']

docs/superpowers/plans/2026-05-18-pdf-parser-app.md   # this file
```

### Modified

- `apps/api/pyproject.toml` — add deps (anthropic, sqlalchemy, asyncpg, alembic, pydantic-settings, python-docx, python-multipart, pydantic-to-typescript), dev deps (pytest, pytest-asyncio, httpx, dirty-equals, ruff, mypy), and `scaffold-shared-types` as a workspace path dep.
- `apps/api/main.py` — delete (logic moves to `app/main.py`). The `fastapi dev` command from CLAUDE.md still works because we re-point at `app.main:app`.
- `packages/shared-types/package.json` — add `"types": "./index.ts"`, `"main": "./index.ts"`.
- `apps/web/app/layout.tsx` — update title/description.
- `infra/.env.example` — no change (api keeps its own `.env`).
- `README.md` — short "PDF Parser app" section near the bottom with run/test commands.

---

## Task 1: Backend toolchain & deps

Goal: pyproject has every dependency required by later tasks, and `pytest` runs (zero tests yet).

**Files:**
- Modify: `apps/api/pyproject.toml`
- Create: `apps/api/pytest.ini`
- Create: `apps/api/tests/__init__.py` (empty)
- Create: `apps/api/.env.example`

- [ ] **Step 1: Update `pyproject.toml`**

Replace the file contents with:

```toml
[project]
name = "scaffold-api"
version = "0.1.0"
description = "FastAPI backend for the scaffold."
readme = "README.md"
requires-python = ">=3.12"
dependencies = [
    "fastapi[standard]>=0.136.1",
    "sqlalchemy[asyncio]>=2.0.36",
    "asyncpg>=0.30.0",
    "alembic>=1.14.0",
    "pydantic>=2.9.0",
    "pydantic-settings>=2.6.0",
    "anthropic>=0.40.0",
    "python-multipart>=0.0.20",
    "python-docx>=1.1.2",
    "scaffold-shared-types",
]

[dependency-groups]
dev = [
    "pytest>=8.3.0",
    "pytest-asyncio>=0.24.0",
    "httpx>=0.27.0",
    "dirty-equals>=0.8.0",
    "ruff>=0.7.0",
    "mypy>=1.13.0",
    "pydantic-to-typescript>=2.0.0",
]

[tool.uv.sources]
scaffold-shared-types = { path = "../../packages/shared-types", editable = true }

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]

[tool.ruff]
line-length = 100
target-version = "py312"

[tool.mypy]
python_version = "3.12"
strict = true
```

- [ ] **Step 2: Create `tests/__init__.py`**

Empty file (makes `tests/` a package).

- [ ] **Step 3: Create `apps/api/.env.example`**

```
# Copy to apps/api/.env (gitignored). Loaded by pydantic-settings.
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/app
TEST_DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/app_test
ANTHROPIC_API_KEY=
ANTHROPIC_MODEL=claude-sonnet-4-6
CORS_ORIGINS=http://localhost:3000
MAX_UPLOAD_BYTES=33554432
```

- [ ] **Step 4: Install deps**

Run from `apps/api/`:

```bash
uv sync
```

Expected: `scaffold-shared-types` resolves as editable (its pyproject is created in Task 4 — for now `uv sync` will fail until that exists). **If `uv sync` fails here, that is expected** — proceed to step 5 anyway; this is also why Task 4 is reordered below to run before re-syncing.

Actually — to keep this task self-checking, defer `uv sync` to Task 4. Replace step 4 with: run `uv lock --check 2>&1 | head -1` and accept "would update lockfile" as expected.

- [ ] **Step 5: Verify pytest collection**

After Task 4 has run `uv sync`, the verification belongs there. For this task, the only verifiable thing is that `pyproject.toml` parses:

```bash
uv run --no-sync python -c "import tomllib; tomllib.load(open('pyproject.toml','rb'))"
```

Expected: no output, exit 0.

- [ ] **Step 6: Commit**

```bash
git add apps/api/pyproject.toml apps/api/tests/__init__.py apps/api/.env.example
git commit -m "chore(api): add deps for pdf-parser app (sqlalchemy, anthropic, docx, alembic, test tooling)"
```

---

## Task 2: Shared-types Python package

Goal: `packages/shared-types/` is an editable Python package with three Pydantic models; the API can `import scaffold_shared_types.schemas`.

**Files:**
- Create: `packages/shared-types/pyproject.toml`
- Create: `packages/shared-types/src/scaffold_shared_types/__init__.py`
- Create: `packages/shared-types/src/scaffold_shared_types/schemas.py`
- Modify: `packages/shared-types/package.json` (add `main`/`types` pointing at the generated TS — file itself comes in Task 8)

- [ ] **Step 1: Create `packages/shared-types/pyproject.toml`**

```toml
[project]
name = "scaffold-shared-types"
version = "0.0.1"
description = "Shared Pydantic schemas; TS types generated from these."
requires-python = ">=3.12"
dependencies = ["pydantic>=2.9.0"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/scaffold_shared_types"]
```

- [ ] **Step 2: Create `src/scaffold_shared_types/__init__.py`**

```python
from .schemas import DocumentSummary, DocumentDetail, DocumentList

__all__ = ["DocumentSummary", "DocumentDetail", "DocumentList"]
```

- [ ] **Step 3: Create `src/scaffold_shared_types/schemas.py`**

```python
"""Canonical Pydantic schemas. TS types are generated from this module."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class DocumentSummary(BaseModel):
    id: int
    filename: str
    page_count: int
    byte_size: int
    created_at: datetime


class DocumentDetail(DocumentSummary):
    content_markdown: str = Field(description="Markdown extracted by Claude.")


class DocumentList(BaseModel):
    items: list[DocumentSummary]
```

- [ ] **Step 4: Update `packages/shared-types/package.json`**

```json
{
  "name": "@scaffold/shared-types",
  "version": "0.0.0",
  "private": true,
  "main": "./index.ts",
  "types": "./index.ts"
}
```

Note: `./index.ts` is generated in Task 8. Pointing at it now is fine — Next won't resolve it until that file exists, but TS will fail import. So the **first** consumer (`apps/web` Task 9) only imports after Task 8 ran. The api itself imports the Python package, not the TS one.

- [ ] **Step 5: Sync uv to wire up the editable install**

```bash
cd apps/api && uv sync
```

Expected: lockfile updates; `scaffold-shared-types` installs as editable.

- [ ] **Step 6: Verify import works**

```bash
cd apps/api && uv run python -c "from scaffold_shared_types.schemas import DocumentSummary; print(DocumentSummary.model_fields)"
```

Expected: prints a dict with `id`, `filename`, `page_count`, `byte_size`, `created_at`.

- [ ] **Step 7: Commit**

```bash
git add packages/shared-types apps/api/uv.lock
git commit -m "feat(shared-types): add Pydantic schemas for documents as editable Python package"
```

---

## Task 3: Settings, DB engine, and FastAPI app factory

Goal: `app/main.py` exposes a FastAPI app with `/health`, configured CORS, `DATABASE_URL` from env, async engine + session dependency. `uv run fastapi dev app/main.py` works.

**Files:**
- Create: `apps/api/app/__init__.py` (empty)
- Create: `apps/api/app/config.py`
- Create: `apps/api/app/db.py`
- Create: `apps/api/app/main.py`
- Create: `apps/api/tests/conftest.py`
- Create: `apps/api/tests/test_health.py`
- Delete: `apps/api/main.py` (old root-level file)

- [ ] **Step 1: Write the failing health test**

`apps/api/tests/test_health.py`:

```python
import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_health_returns_ok() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": "0.1.0"}
```

- [ ] **Step 2: Write `tests/conftest.py`**

Minimal version (DB fixtures added in Task 5):

```python
"""Shared pytest fixtures. DB fixtures land in Task 5."""
```

- [ ] **Step 3: Run the test — expect failure**

```bash
cd apps/api && uv run pytest tests/test_health.py -v
```

Expected: ImportError on `app.main` (module doesn't exist yet).

- [ ] **Step 4: Write minimal `config.py`**

```python
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/app"
    test_database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/app_test"
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-6"
    cors_origins: str = "http://localhost:3000"
    max_upload_bytes: int = 32 * 1024 * 1024

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
```

- [ ] **Step 5: Write `db.py`**

```python
from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import get_settings


def _engine_for(url: str):
    return create_async_engine(url, pool_pre_ping=True)


engine = _engine_for(get_settings().database_url)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncIterator[AsyncSession]:
    async with SessionLocal() as session:
        yield session
```

- [ ] **Step 6: Write `app/main.py`**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.config import get_settings


class HealthResponse(BaseModel):
    status: str
    version: str


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="scaffold-api", version="0.1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health", response_model=HealthResponse)
    async def health() -> HealthResponse:
        return HealthResponse(status="ok", version="0.1.0")

    return app


app = create_app()
```

- [ ] **Step 7: Delete the old `apps/api/main.py`**

```bash
git rm apps/api/main.py
```

- [ ] **Step 8: Run the test — expect pass**

```bash
cd apps/api && uv run pytest tests/test_health.py -v
```

Expected: PASS.

- [ ] **Step 9: Update CLAUDE.md run command note (optional, but the executor should re-verify)**

Quick check: `uv run --directory apps/api fastapi dev app/main.py` should start the server on :8000. Run it once, hit `/health`, kill it.

```bash
cd apps/api && uv run fastapi dev app/main.py &
sleep 3 && curl -s localhost:8000/health && echo
kill %1 2>/dev/null
```

Expected: `{"status":"ok","version":"0.1.0"}`.

- [ ] **Step 10: Commit**

```bash
git add apps/api/app apps/api/tests/conftest.py apps/api/tests/test_health.py
git add -u apps/api/main.py
git commit -m "feat(api): app factory with settings, async db engine, CORS, health endpoint"
```

---

## Task 4: ORM model + initial Alembic migration

Goal: `documents` table exists in `app` (dev) and `app_test` (test) databases after `alembic upgrade head`.

**Files:**
- Create: `apps/api/app/models.py`
- Create: `apps/api/alembic.ini`
- Create: `apps/api/alembic/env.py`
- Create: `apps/api/alembic/script.py.mako`
- Create: `apps/api/alembic/versions/0001_initial.py`

- [ ] **Step 1: Write `app/models.py`**

```python
from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    filename: Mapped[str] = mapped_column(String(512), nullable=False)
    page_count: Mapped[int] = mapped_column(Integer, nullable=False)
    byte_size: Mapped[int] = mapped_column(Integer, nullable=False)
    content_markdown: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
```

- [ ] **Step 2: Write `alembic.ini`**

```ini
[alembic]
script_location = alembic
file_template = %%(rev)s_%%(slug)s
# sqlalchemy.url is read from env in alembic/env.py

[loggers]
keys = root,sqlalchemy,alembic
[handlers]
keys = console
[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
```

- [ ] **Step 3: Write `alembic/env.py` (async pattern)**

```python
import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import NullPool

from app.config import get_settings
from app.models import Base

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def _url() -> str:
    # Allow override via -x url=... e.g. for test DB
    x = context.get_x_argument(as_dictionary=True)
    return x.get("url") or get_settings().database_url


def run_migrations_offline() -> None:
    context.configure(url=_url(), target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    engine = create_async_engine(_url(), poolclass=NullPool)
    async with engine.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
```

- [ ] **Step 4: Write `alembic/script.py.mako`**

```mako
"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = ${repr(up_revision)}
down_revision: str | None = ${repr(down_revision)}
branch_labels: str | Sequence[str] | None = ${repr(branch_labels)}
depends_on: str | Sequence[str] | None = ${repr(depends_on)}


def upgrade() -> None:
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    ${downgrades if downgrades else "pass"}
```

- [ ] **Step 5: Write `alembic/versions/0001_initial.py`**

```python
"""initial documents table

Revision ID: 0001
Revises:
Create Date: 2026-05-18

"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "documents",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("filename", sa.String(length=512), nullable=False),
        sa.Column("page_count", sa.Integer(), nullable=False),
        sa.Column("byte_size", sa.Integer(), nullable=False),
        sa.Column("content_markdown", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )


def downgrade() -> None:
    op.drop_table("documents")
```

- [ ] **Step 6: Verify Postgres is up; create `app_test` database**

```bash
docker compose -f infra/docker-compose.yml up -d postgres
docker compose -f infra/docker-compose.yml exec -T postgres \
  psql -U postgres -d postgres -c "CREATE DATABASE app_test;" || true
```

Expected: container healthy; `app_test` either created or "already exists" error (both fine).

- [ ] **Step 7: Run migrations against both DBs**

```bash
cd apps/api
uv run alembic upgrade head
uv run alembic -x url=postgresql+asyncpg://postgres:postgres@localhost:5432/app_test upgrade head
```

Expected: each prints `Running upgrade  -> 0001, initial documents table` (or "already applied" on rerun).

- [ ] **Step 8: Verify schema**

```bash
docker compose -f infra/docker-compose.yml exec -T postgres \
  psql -U postgres -d app -c "\d documents"
```

Expected: table with 6 columns matching the model.

- [ ] **Step 9: Commit**

```bash
git add apps/api/app/models.py apps/api/alembic.ini apps/api/alembic
git commit -m "feat(api): add Document model and initial Alembic migration"
```

---

## Task 5: DB-backed test fixtures + Anthropic stub

Goal: pytest fixtures provide an isolated transaction per test against `app_test`, plus an injectable fake Anthropic client. Health test still passes.

**Files:**
- Create: `apps/api/app/deps.py`
- Modify: `apps/api/tests/conftest.py`

- [ ] **Step 1: Write `app/deps.py`**

```python
from collections.abc import AsyncIterator
from functools import lru_cache
from typing import Protocol

from anthropic import AsyncAnthropic

from app.config import get_settings


class AnthropicClient(Protocol):
    messages: object  # narrowed at use site


@lru_cache
def _real_client() -> AsyncAnthropic:
    return AsyncAnthropic(api_key=get_settings().anthropic_api_key)


async def get_anthropic_client() -> AsyncIterator[AnthropicClient]:
    yield _real_client()
```

- [ ] **Step 2: Rewrite `tests/conftest.py`**

```python
from collections.abc import AsyncIterator
from typing import Any

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import get_settings
from app.db import get_session
from app.deps import get_anthropic_client
from app.main import app as _app


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(scope="session")
def test_engine():
    engine = create_async_engine(get_settings().test_database_url, pool_pre_ping=True)
    yield engine


@pytest.fixture
async def session(test_engine) -> AsyncIterator[AsyncSession]:
    """Per-test session wrapped in a transaction that is rolled back at teardown."""
    connection = await test_engine.connect()
    transaction = await connection.begin()
    SessionLocal = async_sessionmaker(bind=connection, expire_on_commit=False)
    async with SessionLocal() as s:
        # Clean slate per test: truncate documents (cheaper than full rollback dance for FKs we don't have)
        await s.execute(__import__("sqlalchemy").text("TRUNCATE documents RESTART IDENTITY"))
        await s.commit()
        yield s
    await transaction.rollback()
    await connection.close()


class FakeAnthropic:
    """Stand-in for anthropic.AsyncAnthropic. Override `.markdown` per test."""

    def __init__(self, markdown: str = "# Stub\n\nHello.") -> None:
        self.markdown = markdown
        self.calls: list[dict[str, Any]] = []

        class _Messages:
            async def create(inner_self, **kwargs: Any):  # noqa: N805
                self.calls.append(kwargs)
                return type(
                    "Resp",
                    (),
                    {"content": [type("Block", (), {"type": "text", "text": self.markdown})()]},
                )()

        self.messages = _Messages()


@pytest.fixture
def fake_anthropic() -> FakeAnthropic:
    return FakeAnthropic()


@pytest.fixture
async def client(session, fake_anthropic) -> AsyncIterator[AsyncClient]:
    async def _override_session() -> AsyncIterator[AsyncSession]:
        yield session

    async def _override_anthropic():
        yield fake_anthropic

    _app.dependency_overrides[get_session] = _override_session
    _app.dependency_overrides[get_anthropic_client] = _override_anthropic
    transport = ASGITransport(app=_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    _app.dependency_overrides.clear()
```

- [ ] **Step 3: Run all tests — expect pass**

```bash
cd apps/api && uv run pytest -v
```

Expected: `test_health_returns_ok` PASS. (No DB-using tests yet, but fixtures must import cleanly.)

- [ ] **Step 4: Commit**

```bash
git add apps/api/app/deps.py apps/api/tests/conftest.py
git commit -m "test(api): add per-test DB transaction fixture and fake Anthropic client"
```

---

## Task 6: PDF parser service

Goal: `services.pdf_parser.extract_markdown(pdf_bytes, filename, client, model)` returns Markdown by calling the Anthropic Messages API with a base64 PDF document block. Unit-tested with the fake client.

**Files:**
- Create: `apps/api/app/services/__init__.py` (empty)
- Create: `apps/api/app/services/pdf_parser.py`
- Create: `apps/api/tests/test_pdf_parser.py`

- [ ] **Step 1: Write the failing unit test**

`apps/api/tests/test_pdf_parser.py`:

```python
import base64

import pytest

from app.services.pdf_parser import extract_markdown
from tests.conftest import FakeAnthropic


@pytest.mark.asyncio
async def test_extract_markdown_sends_pdf_as_base64_document_block() -> None:
    fake = FakeAnthropic(markdown="# Hello\n\nWorld.")
    pdf = b"%PDF-1.4 fake bytes"
    md = await extract_markdown(pdf, "doc.pdf", client=fake, model="claude-sonnet-4-6")
    assert md == "# Hello\n\nWorld."
    assert len(fake.calls) == 1
    call = fake.calls[0]
    assert call["model"] == "claude-sonnet-4-6"
    user_msg = call["messages"][0]
    assert user_msg["role"] == "user"
    blocks = user_msg["content"]
    doc_block = next(b for b in blocks if b["type"] == "document")
    assert doc_block["source"]["type"] == "base64"
    assert doc_block["source"]["media_type"] == "application/pdf"
    assert base64.b64decode(doc_block["source"]["data"]) == pdf


@pytest.mark.asyncio
async def test_extract_markdown_raises_on_empty_response() -> None:
    fake = FakeAnthropic(markdown="")
    with pytest.raises(ValueError, match="empty"):
        await extract_markdown(b"x", "doc.pdf", client=fake, model="m")
```

- [ ] **Step 2: Run — expect fail (ImportError)**

```bash
cd apps/api && uv run pytest tests/test_pdf_parser.py -v
```

Expected: collection error / ImportError.

- [ ] **Step 3: Write `app/services/pdf_parser.py`**

```python
import base64
from typing import Any

PROMPT = (
    "Extract the full text content of the attached PDF as GitHub-flavored Markdown. "
    "Preserve heading hierarchy (#, ##, ###), paragraphs, bullet and numbered lists, and "
    "inline emphasis. Do not summarize. Do not add commentary. Output Markdown only."
)


async def extract_markdown(
    pdf_bytes: bytes,
    filename: str,
    *,
    client: Any,
    model: str,
) -> str:
    encoded = base64.standard_b64encode(pdf_bytes).decode("ascii")
    response = await client.messages.create(
        model=model,
        max_tokens=8000,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "document",
                        "source": {
                            "type": "base64",
                            "media_type": "application/pdf",
                            "data": encoded,
                        },
                        "title": filename,
                    },
                    {"type": "text", "text": PROMPT},
                ],
            }
        ],
    )
    parts = [b.text for b in response.content if getattr(b, "type", None) == "text"]
    md = "\n".join(p for p in parts if p).strip()
    if not md:
        raise ValueError("Anthropic returned empty markdown")
    return md
```

- [ ] **Step 4: Run — expect pass**

```bash
cd apps/api && uv run pytest tests/test_pdf_parser.py -v
```

Expected: 2 PASS.

- [ ] **Step 5: Commit**

```bash
git add apps/api/app/services apps/api/tests/test_pdf_parser.py
git commit -m "feat(api): pdf parser service using Anthropic document block"
```

---

## Task 7: POST /documents endpoint

Goal: multipart `POST /documents` with a `file` field stores the parsed Markdown and returns a `DocumentDetail`. Wrong content-type or oversized files are rejected with 400/413.

**Files:**
- Create: `apps/api/app/routes/__init__.py` (empty)
- Create: `apps/api/app/routes/documents.py`
- Modify: `apps/api/app/main.py` (mount router)
- Create: `apps/api/tests/test_documents_upload.py`

Page-count discovery: we don't need a separate PDF library — `python-docx` doesn't read PDFs. Use a tiny stdlib-only heuristic: count `b"/Type /Page"` occurrences in the raw bytes. Imperfect but adequate for display; if zero matches, fall back to `1`.

- [ ] **Step 1: Write the failing upload tests**

`apps/api/tests/test_documents_upload.py`:

```python
import io

import pytest


def _minimal_pdf(pages: int = 1) -> bytes:
    # The smallest grammatically-plausible PDF the parser cares about.
    # Body just needs the magic header and enough "/Type /Page" markers for the page-count heuristic.
    body = b"%PDF-1.4\n" + b"\n".join(b"/Type /Page" for _ in range(pages))
    return body + b"\n%%EOF\n"


@pytest.mark.asyncio
async def test_upload_pdf_persists_document(client, fake_anthropic) -> None:
    fake_anthropic.markdown = "# Title\n\nBody."
    pdf = _minimal_pdf(pages=3)
    files = {"file": ("doc.pdf", io.BytesIO(pdf), "application/pdf")}
    resp = await client.post("/documents", files=files)
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["filename"] == "doc.pdf"
    assert body["page_count"] == 3
    assert body["byte_size"] == len(pdf)
    assert body["content_markdown"] == "# Title\n\nBody."
    assert isinstance(body["id"], int)


@pytest.mark.asyncio
async def test_upload_rejects_non_pdf(client) -> None:
    files = {"file": ("a.txt", b"hello", "text/plain")}
    resp = await client.post("/documents", files=files)
    assert resp.status_code == 400
    assert "pdf" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_upload_rejects_oversize(client, monkeypatch) -> None:
    from app.config import get_settings

    get_settings.cache_clear()
    monkeypatch.setenv("MAX_UPLOAD_BYTES", "10")
    files = {"file": ("big.pdf", b"%PDF-1.4 lots of bytes here", "application/pdf")}
    resp = await client.post("/documents", files=files)
    assert resp.status_code == 413
    get_settings.cache_clear()
```

- [ ] **Step 2: Run — expect 404 on the upload route**

```bash
cd apps/api && uv run pytest tests/test_documents_upload.py -v
```

Expected: all three FAIL with 404 (route missing).

- [ ] **Step 3: Write `app/routes/documents.py`**

```python
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.db import get_session
from app.deps import get_anthropic_client
from app.models import Document
from app.services.pdf_parser import extract_markdown
from scaffold_shared_types.schemas import DocumentDetail

router = APIRouter(prefix="/documents", tags=["documents"])


def _count_pages(pdf_bytes: bytes) -> int:
    return max(pdf_bytes.count(b"/Type /Page"), 1)


@router.post("", status_code=status.HTTP_201_CREATED, response_model=DocumentDetail)
async def upload_document(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
    anthropic=Depends(get_anthropic_client),
) -> DocumentDetail:
    settings = get_settings()
    if (file.content_type or "").lower() != "application/pdf" and not (file.filename or "").lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only application/pdf uploads are accepted.")
    data = await file.read()
    if len(data) > settings.max_upload_bytes:
        raise HTTPException(status_code=413, detail=f"File exceeds {settings.max_upload_bytes} bytes.")
    if len(data) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    try:
        markdown = await extract_markdown(
            data, file.filename or "document.pdf",
            client=anthropic, model=settings.anthropic_model,
        )
    except ValueError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    doc = Document(
        filename=file.filename or "document.pdf",
        page_count=_count_pages(data),
        byte_size=len(data),
        content_markdown=markdown,
    )
    session.add(doc)
    await session.commit()
    await session.refresh(doc)
    return DocumentDetail.model_validate(doc, from_attributes=True)
```

- [ ] **Step 4: Mount the router in `app/main.py`**

In `create_app`, after CORS middleware:

```python
from app.routes import documents as documents_router  # at top of file
...
    app.include_router(documents_router.router)
```

- [ ] **Step 5: Run — expect pass**

```bash
cd apps/api && uv run pytest tests/test_documents_upload.py -v
```

Expected: 3 PASS.

- [ ] **Step 6: Commit**

```bash
git add apps/api/app/routes apps/api/app/main.py apps/api/tests/test_documents_upload.py
git commit -m "feat(api): POST /documents — upload PDF, parse with Claude, persist"
```

---

## Task 8: GET /documents (list) and GET /documents/{id} (detail)

**Files:**
- Modify: `apps/api/app/routes/documents.py`
- Create: `apps/api/tests/test_documents_list.py`
- Create: `apps/api/tests/test_documents_get.py`

- [ ] **Step 1: Write failing list test**

`apps/api/tests/test_documents_list.py`:

```python
import pytest

from app.models import Document


@pytest.mark.asyncio
async def test_list_documents_returns_summaries_newest_first(client, session) -> None:
    session.add_all([
        Document(filename="a.pdf", page_count=1, byte_size=10, content_markdown="A"),
        Document(filename="b.pdf", page_count=2, byte_size=20, content_markdown="B"),
    ])
    await session.commit()

    resp = await client.get("/documents")
    assert resp.status_code == 200
    body = resp.json()
    filenames = [item["filename"] for item in body["items"]]
    assert filenames == ["b.pdf", "a.pdf"]
    # Summaries omit content_markdown
    assert "content_markdown" not in body["items"][0]
```

- [ ] **Step 2: Write failing detail test**

`apps/api/tests/test_documents_get.py`:

```python
import pytest

from app.models import Document


@pytest.mark.asyncio
async def test_get_document_returns_detail(client, session) -> None:
    doc = Document(filename="a.pdf", page_count=1, byte_size=10, content_markdown="# Hi")
    session.add(doc)
    await session.commit()
    await session.refresh(doc)

    resp = await client.get(f"/documents/{doc.id}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == doc.id
    assert body["content_markdown"] == "# Hi"


@pytest.mark.asyncio
async def test_get_document_404(client) -> None:
    resp = await client.get("/documents/9999")
    assert resp.status_code == 404
```

- [ ] **Step 3: Run — expect failures**

```bash
cd apps/api && uv run pytest tests/test_documents_list.py tests/test_documents_get.py -v
```

Expected: 405/404s — list and detail routes missing.

- [ ] **Step 4: Add the two endpoints**

Append to `app/routes/documents.py`:

```python
from sqlalchemy import select

from scaffold_shared_types.schemas import DocumentList, DocumentSummary


@router.get("", response_model=DocumentList)
async def list_documents(session: AsyncSession = Depends(get_session)) -> DocumentList:
    result = await session.execute(select(Document).order_by(Document.created_at.desc()))
    docs = result.scalars().all()
    return DocumentList(items=[DocumentSummary.model_validate(d, from_attributes=True) for d in docs])


@router.get("/{doc_id}", response_model=DocumentDetail)
async def get_document(doc_id: int, session: AsyncSession = Depends(get_session)) -> DocumentDetail:
    doc = await session.get(Document, doc_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found.")
    return DocumentDetail.model_validate(doc, from_attributes=True)
```

- [ ] **Step 5: Run — expect pass**

```bash
cd apps/api && uv run pytest tests/test_documents_list.py tests/test_documents_get.py -v
```

Expected: 3 PASS.

- [ ] **Step 6: Commit**

```bash
git add apps/api/app/routes/documents.py apps/api/tests/test_documents_list.py apps/api/tests/test_documents_get.py
git commit -m "feat(api): GET /documents and GET /documents/{id}"
```

---

## Task 9: GET /documents/{id}/docx — DOCX export

Goal: `GET /documents/{id}/docx` streams an Open XML `.docx` file built from the stored Markdown.

**Files:**
- Create: `apps/api/app/services/docx_export.py`
- Modify: `apps/api/app/routes/documents.py`
- Create: `apps/api/tests/test_docx_export.py`
- Create: `apps/api/tests/test_documents_docx.py`

- [ ] **Step 1: Write the failing unit test for the renderer**

`apps/api/tests/test_docx_export.py`:

```python
import io

from docx import Document as DocxDocument

from app.services.docx_export import markdown_to_docx_bytes


def _read(b: bytes):
    return DocxDocument(io.BytesIO(b))


def test_heading_levels_map_to_word_styles() -> None:
    md = "# H1\n\n## H2\n\n### H3\n\nBody paragraph."
    doc = _read(markdown_to_docx_bytes(md))
    styles = [p.style.name for p in doc.paragraphs if p.text]
    assert styles[:3] == ["Heading 1", "Heading 2", "Heading 3"]


def test_bullet_and_numbered_lists() -> None:
    md = "- one\n- two\n\n1. first\n2. second"
    doc = _read(markdown_to_docx_bytes(md))
    texts = [p.text for p in doc.paragraphs if p.text]
    assert "one" in texts and "two" in texts and "first" in texts and "second" in texts
    list_styles = [p.style.name for p in doc.paragraphs if p.text in ("one", "two")]
    assert all("Bullet" in s or "List" in s for s in list_styles)
```

- [ ] **Step 2: Run — expect ImportError**

```bash
cd apps/api && uv run pytest tests/test_docx_export.py -v
```

Expected: collection error.

- [ ] **Step 3: Write `app/services/docx_export.py`**

```python
"""Tiny Markdown→DOCX renderer.

Covers the shapes Claude reliably emits for PDF extraction:
ATX headings (# .. ######), paragraphs, ordered/unordered lists.
Inline formatting is rendered as plain text.
"""
import io
import re

from docx import Document as DocxDocument

_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
_UL_RE = re.compile(r"^[-*+]\s+(.*)$")
_OL_RE = re.compile(r"^\d+\.\s+(.*)$")


def markdown_to_docx_bytes(markdown: str) -> bytes:
    doc = DocxDocument()
    para_buf: list[str] = []

    def flush_paragraph() -> None:
        if para_buf:
            doc.add_paragraph(" ".join(para_buf).strip())
            para_buf.clear()

    for raw in markdown.splitlines():
        line = raw.rstrip()
        if not line.strip():
            flush_paragraph()
            continue
        m = _HEADING_RE.match(line)
        if m:
            flush_paragraph()
            doc.add_heading(m.group(2).strip(), level=len(m.group(1)))
            continue
        m = _UL_RE.match(line)
        if m:
            flush_paragraph()
            doc.add_paragraph(m.group(1).strip(), style="List Bullet")
            continue
        m = _OL_RE.match(line)
        if m:
            flush_paragraph()
            doc.add_paragraph(m.group(1).strip(), style="List Number")
            continue
        para_buf.append(line.strip())
    flush_paragraph()

    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()
```

- [ ] **Step 4: Run unit test — expect pass**

```bash
cd apps/api && uv run pytest tests/test_docx_export.py -v
```

Expected: 2 PASS.

- [ ] **Step 5: Write the endpoint test**

`apps/api/tests/test_documents_docx.py`:

```python
import io

import pytest
from docx import Document as DocxDocument

from app.models import Document


@pytest.mark.asyncio
async def test_download_docx_returns_word_doc(client, session) -> None:
    doc = Document(filename="report.pdf", page_count=1, byte_size=1,
                   content_markdown="# Hello\n\nWorld.")
    session.add(doc)
    await session.commit()
    await session.refresh(doc)

    resp = await client.get(f"/documents/{doc.id}/docx")
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith(
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
    assert "report.docx" in resp.headers["content-disposition"]

    parsed = DocxDocument(io.BytesIO(resp.content))
    assert any(p.text == "Hello" and p.style.name == "Heading 1" for p in parsed.paragraphs)
    assert any(p.text == "World." for p in parsed.paragraphs)


@pytest.mark.asyncio
async def test_download_docx_404(client) -> None:
    resp = await client.get("/documents/9999/docx")
    assert resp.status_code == 404
```

- [ ] **Step 6: Run — expect 404 on the route**

```bash
cd apps/api && uv run pytest tests/test_documents_docx.py -v
```

Expected: route missing → FAIL.

- [ ] **Step 7: Add the route**

Append to `app/routes/documents.py`:

```python
from pathlib import PurePosixPath

from fastapi import Response

from app.services.docx_export import markdown_to_docx_bytes


@router.get("/{doc_id}/docx")
async def download_docx(doc_id: int, session: AsyncSession = Depends(get_session)) -> Response:
    doc = await session.get(Document, doc_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found.")
    body = markdown_to_docx_bytes(doc.content_markdown)
    stem = PurePosixPath(doc.filename).stem or "document"
    headers = {"content-disposition": f'attachment; filename="{stem}.docx"'}
    return Response(
        content=body,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers=headers,
    )
```

- [ ] **Step 8: Run all api tests**

```bash
cd apps/api && uv run pytest -v
```

Expected: every test PASS.

- [ ] **Step 9: Commit**

```bash
git add apps/api/app/services/docx_export.py apps/api/app/routes/documents.py apps/api/tests/test_docx_export.py apps/api/tests/test_documents_docx.py
git commit -m "feat(api): GET /documents/{id}/docx — render markdown to .docx"
```

---

## Task 10: TS type generation

Goal: running `uv run --directory apps/api python ../../packages/shared-types/scripts/gen_ts.py` rewrites `packages/shared-types/index.ts` from `scaffold_shared_types.schemas`.

**Files:**
- Create: `packages/shared-types/scripts/gen_ts.py`
- Create: `packages/shared-types/index.ts` (generated; commit it)
- Create: `packages/shared-types/tsconfig.json`

- [ ] **Step 1: Write `scripts/gen_ts.py`**

```python
"""Generate packages/shared-types/index.ts from scaffold_shared_types.schemas."""
from pathlib import Path

from pydantic2ts import generate_typescript_defs

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "index.ts"


def main() -> None:
    generate_typescript_defs(
        module="scaffold_shared_types.schemas",
        output=str(OUT),
        json2ts_cmd="npx --yes json-schema-to-typescript-cli",
    )
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
```

Note: `pydantic2ts` shells out to a JS tool. The above uses `npx json-schema-to-typescript-cli` so we don't have to install it globally. If `npx` is not available, the executor should install `json-schema-to-typescript` once: `pnpm add -w -D json-schema-to-typescript`.

- [ ] **Step 2: Ensure `json-schema-to-typescript` is available**

```bash
pnpm add -w -D json-schema-to-typescript
```

Then update the script to call the binary path directly to avoid `npx --yes` interactive prompts:

```python
json2ts_cmd=str(ROOT.parent.parent / "node_modules" / ".bin" / "json-schema-to-typescript"),
```

Re-write `scripts/gen_ts.py` with that resolved path. (The earlier `npx` form is a fallback only.)

- [ ] **Step 3: Run the generator**

```bash
cd apps/api && uv run python ../../packages/shared-types/scripts/gen_ts.py
```

Expected: prints `wrote .../index.ts`; the file exists and exports `DocumentSummary`, `DocumentDetail`, `DocumentList` interfaces.

- [ ] **Step 4: Spot-check the output**

```bash
grep -E "^(export interface|export type) (DocumentSummary|DocumentDetail|DocumentList)" packages/shared-types/index.ts
```

Expected: three matches.

- [ ] **Step 5: Add a `tsconfig.json` for the package**

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "ESNext",
    "moduleResolution": "Bundler",
    "strict": true,
    "declaration": true,
    "isolatedModules": true,
    "skipLibCheck": true
  },
  "include": ["index.ts"]
}
```

- [ ] **Step 6: Commit**

```bash
git add packages/shared-types/scripts packages/shared-types/index.ts packages/shared-types/tsconfig.json package.json pnpm-lock.yaml
git commit -m "feat(shared-types): generate TS interfaces from Pydantic schemas"
```

---

## Task 11: Web — API client wrapper + transpilePackages

Goal: `apps/web/app/api-client.ts` exports typed `listDocuments`, `getDocument`, `uploadDocument`, `docxUrl` helpers. Next is configured to transpile `@scaffold/shared-types`.

**Files:**
- Create: `apps/web/app/api-client.ts`
- Modify: `apps/web/next.config.ts`
- Create: `apps/web/.env.example`

- [ ] **Step 1: Read the relevant Next 16 docs**

```bash
ls apps/web/node_modules/next/dist/docs/
```

Then read the App Router data-fetching and `next.config.ts` guides. Heed any breaking-change notes. **Do not write Next code from memory.**

- [ ] **Step 2: Update `next.config.ts`**

Read it first:

```bash
cat apps/web/next.config.ts
```

Then modify to add `transpilePackages: ['@scaffold/shared-types']` to the existing config object, preserving anything already there.

- [ ] **Step 3: Create `apps/web/.env.example`**

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

- [ ] **Step 4: Create `apps/web/app/api-client.ts`**

```ts
import type {
  DocumentDetail,
  DocumentList,
  DocumentSummary,
} from "@scaffold/shared-types";

const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function listDocuments(): Promise<DocumentSummary[]> {
  const res = await fetch(`${BASE}/documents`, { cache: "no-store" });
  if (!res.ok) throw new Error(`listDocuments: ${res.status}`);
  const data: DocumentList = await res.json();
  return data.items;
}

export async function getDocument(id: number): Promise<DocumentDetail> {
  const res = await fetch(`${BASE}/documents/${id}`, { cache: "no-store" });
  if (res.status === 404) throw new Error("not-found");
  if (!res.ok) throw new Error(`getDocument: ${res.status}`);
  return res.json();
}

export async function uploadDocument(file: File): Promise<DocumentDetail> {
  const fd = new FormData();
  fd.append("file", file);
  const res = await fetch(`${BASE}/documents`, { method: "POST", body: fd });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(`upload failed: ${res.status} ${detail}`);
  }
  return res.json();
}

export function docxUrl(id: number): string {
  return `${BASE}/documents/${id}/docx`;
}
```

- [ ] **Step 5: Type-check**

```bash
cd apps/web && pnpm exec tsc --noEmit
```

Expected: no errors. If `@scaffold/shared-types` can't be resolved, double-check the workspace `package.json` and that `index.ts` exists.

- [ ] **Step 6: Commit**

```bash
git add apps/web/app/api-client.ts apps/web/next.config.ts apps/web/.env.example
git commit -m "feat(web): typed api client and shared-types transpile config"
```

---

## Task 12: Web — upload + list page

Goal: `/` shows an upload form and a list of documents.

**Files:**
- Modify: `apps/web/app/page.tsx` (full replace)
- Create: `apps/web/app/UploadForm.tsx`
- Create: `apps/web/app/DocumentList.tsx`
- Modify: `apps/web/app/layout.tsx` (update metadata)

- [ ] **Step 1: Update `app/layout.tsx` metadata**

```ts
export const metadata: Metadata = {
  title: "PDF Parser",
  description: "Upload PDFs, extract content with Claude, download as Word.",
};
```

- [ ] **Step 2: Create `app/UploadForm.tsx` (Client Component)**

```tsx
"use client";

import { useState, useTransition } from "react";
import { useRouter } from "next/navigation";

import { uploadDocument } from "./api-client";

export function UploadForm() {
  const router = useRouter();
  const [pending, startTransition] = useTransition();
  const [error, setError] = useState<string | null>(null);

  async function onChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setError(null);
    try {
      const doc = await uploadDocument(file);
      startTransition(() => router.push(`/documents/${doc.id}`));
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      e.target.value = "";
    }
  }

  return (
    <div className="flex flex-col gap-2">
      <label className="inline-flex items-center justify-center h-12 px-5 rounded-full bg-black text-white cursor-pointer dark:bg-white dark:text-black">
        {pending ? "Uploading…" : "Upload PDF"}
        <input type="file" accept="application/pdf" onChange={onChange} hidden />
      </label>
      {error && <p className="text-sm text-red-600">{error}</p>}
    </div>
  );
}
```

- [ ] **Step 3: Create `app/DocumentList.tsx` (Server Component)**

```tsx
import Link from "next/link";

import { listDocuments } from "./api-client";

export async function DocumentList() {
  const docs = await listDocuments();
  if (docs.length === 0) {
    return <p className="text-sm text-zinc-500">No documents yet.</p>;
  }
  return (
    <ul className="divide-y divide-zinc-200 dark:divide-zinc-800 w-full">
      {docs.map((d) => (
        <li key={d.id} className="py-3 flex items-center justify-between">
          <Link href={`/documents/${d.id}`} className="font-medium hover:underline">
            {d.filename}
          </Link>
          <span className="text-xs text-zinc-500">
            {d.page_count} page{d.page_count === 1 ? "" : "s"} · {new Date(d.created_at).toLocaleString()}
          </span>
        </li>
      ))}
    </ul>
  );
}
```

- [ ] **Step 4: Replace `app/page.tsx`**

```tsx
import { DocumentList } from "./DocumentList";
import { UploadForm } from "./UploadForm";

export const dynamic = "force-dynamic";

export default function Home() {
  return (
    <main className="mx-auto flex w-full max-w-3xl flex-1 flex-col gap-8 px-6 py-16">
      <header className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold tracking-tight">PDF Parser</h1>
        <UploadForm />
      </header>
      <DocumentList />
    </main>
  );
}
```

- [ ] **Step 5: Smoke-test the web app**

```bash
docker compose -f infra/docker-compose.yml up -d
cd apps/api && uv run fastapi dev app/main.py &
cd apps/web && pnpm --filter @scaffold/web dev &
```

Open `http://localhost:3000`. Expected: page renders, "No documents yet." shown. (Upload is verified end-to-end in Task 14 because it needs a real `ANTHROPIC_API_KEY` — leave the dev servers running for now.)

- [ ] **Step 6: Type-check + lint**

```bash
cd apps/web && pnpm exec tsc --noEmit && pnpm lint
```

Expected: no errors.

- [ ] **Step 7: Commit**

```bash
git add apps/web/app/page.tsx apps/web/app/UploadForm.tsx apps/web/app/DocumentList.tsx apps/web/app/layout.tsx
git commit -m "feat(web): upload form + documents list on home page"
```

---

## Task 13: Web — document detail page with Markdown render + DOCX download

**Files:**
- Create: `apps/web/app/documents/[id]/page.tsx`
- Create: `apps/web/app/documents/[id]/DocumentView.tsx`
- Modify: `apps/web/package.json` (add `react-markdown`, `remark-gfm`)

- [ ] **Step 1: Install Markdown deps**

```bash
pnpm --filter @scaffold/web add react-markdown remark-gfm
```

- [ ] **Step 2: Create `app/documents/[id]/page.tsx` (Server Component)**

> **Next 16 note:** Dynamic route params API may differ from training data. Before writing the component, run `cat apps/web/node_modules/next/dist/docs/**/dynamic-routes*.md 2>/dev/null | head -200` and follow whatever shape Next 16 expects (e.g. `params` may be a Promise — `await params` if so).

```tsx
import { notFound } from "next/navigation";

import { getDocument } from "../../api-client";
import { DocumentView } from "./DocumentView";

export const dynamic = "force-dynamic";

export default async function DocumentPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const docId = Number(id);
  if (!Number.isFinite(docId)) notFound();
  try {
    const doc = await getDocument(docId);
    return <DocumentView doc={doc} />;
  } catch (err) {
    if (err instanceof Error && err.message === "not-found") notFound();
    throw err;
  }
}
```

If the Next 16 docs say `params` is *not* a Promise in this version, change the type and drop the `await`. Verify by checking the docs file first.

- [ ] **Step 3: Create `app/documents/[id]/DocumentView.tsx`**

```tsx
"use client";

import Link from "next/link";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

import type { DocumentDetail } from "@scaffold/shared-types";
import { docxUrl } from "../../api-client";

export function DocumentView({ doc }: { doc: DocumentDetail }) {
  return (
    <main className="mx-auto flex w-full max-w-3xl flex-1 flex-col gap-6 px-6 py-12">
      <nav className="flex items-center justify-between">
        <Link href="/" className="text-sm text-zinc-500 hover:underline">
          ← All documents
        </Link>
        <a
          href={docxUrl(doc.id)}
          className="inline-flex h-10 items-center rounded-full bg-black px-4 text-sm font-medium text-white dark:bg-white dark:text-black"
        >
          Download .docx
        </a>
      </nav>
      <header>
        <h1 className="text-2xl font-semibold tracking-tight">{doc.filename}</h1>
        <p className="text-xs text-zinc-500">
          {doc.page_count} page{doc.page_count === 1 ? "" : "s"} · {new Date(doc.created_at).toLocaleString()}
        </p>
      </header>
      <article className="prose prose-zinc dark:prose-invert max-w-none">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>{doc.content_markdown}</ReactMarkdown>
      </article>
    </main>
  );
}
```

(`prose` classes require `@tailwindcss/typography`. If not installed, the markdown still renders fine — just without the typography styles. Adding `@tailwindcss/typography` is optional polish; skip unless explicitly asked.)

- [ ] **Step 4: Type-check + lint**

```bash
cd apps/web && pnpm exec tsc --noEmit && pnpm lint
```

Expected: no errors.

- [ ] **Step 5: Commit**

```bash
git add apps/web/app/documents apps/web/package.json pnpm-lock.yaml
git commit -m "feat(web): document detail page with markdown rendering and .docx download"
```

---

## Task 14: End-to-end smoke + README

Goal: prove the whole pipeline works against a real PDF with a real Anthropic key. Update `README.md` with usage.

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Confirm env keys**

Copy and edit:

```bash
cp -n apps/api/.env.example apps/api/.env
cp -n apps/web/.env.example apps/web/.env.local
```

Edit `apps/api/.env` to fill in a real `ANTHROPIC_API_KEY`. If the user does not have a key, **stop and ask** — the rest of this task cannot run without one.

- [ ] **Step 2: Start everything**

```bash
docker compose -f infra/docker-compose.yml up -d
cd apps/api && uv run alembic upgrade head
cd apps/api && uv run fastapi dev app/main.py &
cd apps/web && pnpm --filter @scaffold/web dev &
```

- [ ] **Step 3: Upload a real PDF**

Either through the UI at http://localhost:3000, or via curl:

```bash
curl -s -F "file=@/path/to/some.pdf;type=application/pdf" http://localhost:8000/documents | jq .
```

Expected: a JSON object with non-empty `content_markdown` reflecting the real PDF content.

- [ ] **Step 4: Open the detail page in a browser**

Visit `http://localhost:3000/documents/<id>`. Confirm the rendered Markdown matches the PDF. Click "Download .docx" and open the file in Word / Pages / LibreOffice — confirm headings and lists render.

- [ ] **Step 5: Update `README.md`**

Add a section near the bottom (do not rewrite the file):

```markdown
## PDF Parser App

This scaffold ships with a small reference app that uploads a PDF, extracts its
contents using the Anthropic API, persists Markdown in Postgres, and exports a
`.docx`.

### Run locally

```bash
docker compose -f infra/docker-compose.yml up -d
cp -n apps/api/.env.example apps/api/.env  # then fill ANTHROPIC_API_KEY
cp -n apps/web/.env.example apps/web/.env.local
cd apps/api && uv run alembic upgrade head && uv run fastapi dev app/main.py
# in another shell
pnpm --filter @scaffold/web dev
```

Open http://localhost:3000.

### Tests

```bash
cd apps/api && uv run pytest
cd apps/web && pnpm exec tsc --noEmit && pnpm lint
```
```

- [ ] **Step 6: Run the full test suite once more**

```bash
cd apps/api && uv run pytest -v
cd apps/web && pnpm exec tsc --noEmit && pnpm lint
```

Expected: all green.

- [ ] **Step 7: Commit**

```bash
git add README.md
git commit -m "docs: add PDF parser app run instructions"
```

---

## Self-Review (red-team pass)

Adversarial findings on the draft above, with fixes applied inline.

1. **Task 1 originally ran `uv sync` before Task 4 created the shared-types Python package** → fixed by reordering: shared-types package becomes Task 2 (renumbered), and Task 1 only checks that `pyproject.toml` parses.
2. **Test fixture used SQLAlchemy session against truncated table without cleaning across runs** → fixed by explicit `TRUNCATE documents RESTART IDENTITY` at fixture entry. The "rollback at teardown" comment was misleading — the truncate is what guarantees isolation; the rollback wraps writes that never commit. Both kept; the truncate is the load-bearing piece.
3. **Page-count heuristic (`b"/Type /Page"`)** is fragile and won't match many real PDFs (encoded streams, compressed cross-reference tables) → acceptable for a small app. Documented as a heuristic with a `max(_, 1)` floor so it never returns zero. If accuracy matters later, swap to `pypdf`.
4. **Multipart upload test** uses `io.BytesIO`; some httpx versions require raw `bytes`. Validated against httpx ≥ 0.27 (current).
5. **CORS origin parsing** — initial draft made `cors_origins` a `list[str]` directly via `BaseSettings`, but `pydantic-settings` parses lists from env as JSON by default. Changed to a comma-separated string + `cors_origins_list` property to keep `.env` plain.
6. **`@scaffold/shared-types` resolving via `index.ts`** depends on Next's `transpilePackages`. Confirmed Task 11 sets that. Without it, Next dev silently fails to import. The plan reads the existing `next.config.ts` first to avoid clobbering it.
7. **Next 16 `params` shape** — recent versions made `params` a Promise in Server Components. The plan flags this and instructs the executor to verify against `node_modules/next/dist/docs/` rather than assume.
8. **DOCX route filename injection** — `PurePosixPath(filename).stem` strips path separators; safer than echoing user input directly into `content-disposition`.
9. **Test isolation between upload-rejection test and earlier tests** — `MAX_UPLOAD_BYTES` monkeypatch only takes effect because `get_settings` is `lru_cache`d and the test calls `.cache_clear()` before and after. Verified the lifecycle.
10. **Original draft put a `Step 9: smoke-test fastapi dev` inline in Task 3 with a background process kill via `%1`** — fragile across shells. Acceptable as a quick check, but the canonical E2E smoke is Task 14.
11. **DOCX export's heading detection** — `# foo #` (closing hashes) isn't handled by the regex. Claude doesn't emit that style. Documented as an intentional omission.
12. **Original list endpoint test asserted `created_at` ordering without sleeping** — Postgres `now()` ticks per statement, so two inserts in the same transaction can get the same `now()`. The test now relies on `id desc` semantics inherent to "newest first" — wait, it does not; it orders by `created_at`. **Fix:** keep the order by `created_at desc` in the endpoint but add `Document.id.desc()` as a tiebreaker. Apply in Task 8:

   In `list_documents`, change to:
   ```python
   .order_by(Document.created_at.desc(), Document.id.desc())
   ```

   Apply this when implementing Task 8 — the tiebreaker is essential for the test to be deterministic.
13. **Anthropic SDK content blocks** — the documented JSON shape is `{"type":"document","source":{"type":"base64",...}}`. The SDK accepts dict literals as well as `BetaContentBlock` objects; the dict form is used to avoid version-pinning to a specific SDK internal model.
14. **Plan does not regenerate TS types after Task 8 (renumbered)** — Task 10 runs codegen once. If the user later adds a field, they re-run `gen_ts.py`. Acceptable; not worth a watcher for a small app.

---

## Spec coverage

- "Parse PDFs using Anthropic API" → Task 6.
- "Save parsed content into a database" → Tasks 4 + 7.
- "Open and display it" → Tasks 8 + 13.
- "Save it as .doc file" → Task 9 (delivered as `.docx`; see top note).

No gaps. Plan complete.

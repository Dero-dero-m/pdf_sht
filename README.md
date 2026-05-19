# PDF Parser

Upload a PDF, extract its contents with the Anthropic API, view the result as Markdown, and download it as a Word `.docx`.

A Next.js 16 web app talks to a FastAPI backend; parsed Markdown is persisted in Postgres; shared types are generated from Pydantic models into TypeScript.

## Stack

- **Web:** Next.js 16 (App Router, Turbopack), React 19, TypeScript, Tailwind v4, `react-markdown` + `remark-gfm`
- **API:** FastAPI on Python 3.12 (async), SQLAlchemy 2 + asyncpg, Alembic, `anthropic`, `pypdf`, `python-docx`
- **Data:** Postgres 16 + pgvector, Redis 7 (loopback-bound via Docker Compose)
- **Shared types:** Pydantic models in `packages/shared-types/`, TypeScript generated via `pydantic2ts`
- **Package managers:** `pnpm` (Node 22), `uv` (Python 3.12)

## Quickstart

```bash
# 1. Local services (Postgres + Redis), loopback-bound
docker compose -f infra/docker-compose.yml up -d

# 2. Node deps
pnpm install

# 3. Python deps
uv sync --directory apps/api

# 4. API env — fill in your Anthropic key
cp -n apps/api/.env.example apps/api/.env
# edit apps/api/.env and set ANTHROPIC_API_KEY=sk-…

# 5. Web env
cp -n apps/web/.env.example apps/web/.env.local

# 6. Migrations
cd apps/api && uv run alembic upgrade head
```

### Run dev servers

```bash
# API (port 8000)
uv run --directory apps/api fastapi dev app/main.py

# Web (port 3000) — must use the workspace filter; no root dev script
pnpm --filter @scaffold/web dev
```

Open <http://localhost:3000>. Upload a PDF; the detail page renders the extracted Markdown and offers a `.docx` download.

Without `ANTHROPIC_API_KEY` set, the home page still loads but uploads will fail at the model call.

## Layout

```
apps/
  web/                      Next.js 16 App Router (workspace: @scaffold/web)
    app/
      page.tsx              Home: upload form + documents list
      documents/[id]/       Detail page + DOCX download
      loading.tsx           Suspense skeletons
      api-client.ts         Typed fetch wrapper using @scaffold/shared-types
  api/                      FastAPI service (project: scaffold-api)
    app/
      main.py               App factory, CORS, health
      config.py             Settings via pydantic-settings
      db.py                 Async engine + get_session dep
      models.py             SQLAlchemy: Document
      deps.py               Anthropic client dep (override-able in tests)
      routes/documents.py   Upload + list + get + docx endpoints
      services/             pdf_parser (Anthropic call), docx_export (Markdown → docx)
    alembic/                Migrations
    tests/                  pytest against real Postgres + FakeAnthropic
packages/
  shared-types/             Pydantic schemas (Python) + generated index.ts (TS)
  ui/                       Workspace stub
infra/
  docker-compose.yml        Postgres 16 + pgvector, Redis 7-alpine
  init/postgres/            First-boot SQL (auto-enables pgvector)
```

## API surface

| Method | Path                       | Purpose                                  |
| ------ | -------------------------- | ---------------------------------------- |
| POST   | `/documents`               | multipart PDF upload → parse → persist   |
| GET    | `/documents`               | list summaries (newest first)            |
| GET    | `/documents/{id}`          | full document (incl. extracted Markdown) |
| GET    | `/documents/{id}/docx`     | stream `.docx` rendered from the Markdown |
| GET    | `/health`                  | liveness probe                            |

CORS is locked to `http://localhost:3000` by default; override via `CORS_ORIGINS` in `apps/api/.env`.

## Regenerate TypeScript types after a schema change

```bash
cd apps/api && uv run python ../../packages/shared-types/scripts/gen_ts.py
```

This rewrites `packages/shared-types/index.ts` from the Pydantic models in `scaffold_shared_types.schemas`. The web app consumes those types via the workspace dep + `transpilePackages` in `apps/web/next.config.ts`.

## Tests

```bash
cd apps/api && uv run pytest                          # against real Postgres (app_test DB)
cd apps/api && uv run mypy app/ tests/ alembic/       # strict
cd apps/web && pnpm exec tsc --noEmit && pnpm lint
```

The api test fixtures TRUNCATE `documents` per test (no SQLite substitution); the Anthropic client is dependency-injected with a `FakeAnthropic` that records each call. Create the test DB once with:

```bash
docker compose -f infra/docker-compose.yml exec -T postgres \
  psql -U postgres -d postgres -c "CREATE DATABASE app_test;"
uv run --directory apps/api alembic \
  -x url=postgresql+asyncpg://postgres:postgres@localhost:5432/app_test upgrade head
```

## Local infra notes

- **Docker runtime is OrbStack**, not Docker Desktop. If `docker info` hangs, `orb stop && orb start` is the usual fix.
- **All service ports bind to `127.0.0.1`** (web 3000, api 8000, postgres 5432, redis 6379) — deliberate for the SSH-tunnel workflow:
  ```bash
  ssh -L 3000:localhost:3000 -L 8000:localhost:8000 \
      -L 5432:localhost:5432 -L 6379:localhost:6379 \
      lazarus@<host>
  ```
- **pgvector is auto-enabled** on first DB boot via `infra/init/postgres/01-enable-extensions.sql`. (The app doesn't currently use it; it's there for follow-ups like semantic search over extracted Markdown.)
- **Default DB URL:** `postgresql://postgres:postgres@localhost:5432/app`. Compose-side env overrides live in `infra/.env` (gitignored).
- **Port conflicts with other local projects** are common. Diagnose with `lsof -iTCP:<port> -sTCP:LISTEN`; stop the offending container with `docker stop <name>`.

## Limitations

- Uploads buffer the whole PDF into memory before the size check (cap defaults to 32 MiB via `MAX_UPLOAD_BYTES`).
- The DOCX renderer covers ATX headings, paragraphs, and bullet/numbered lists — the shapes Claude reliably emits for PDF extraction. Inline emphasis renders as plain text.
- `.doc` (legacy CFB) is not supported; the export is `.docx` (Open XML), which opens in Word, Pages, Google Docs, and LibreOffice.

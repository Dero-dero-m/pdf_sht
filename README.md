# freelance-starter

The starter monorepo forked for every freelance project. Phase 0 scaffolding — most
pieces are wired enough to boot end-to-end; the rest are deliberate stubs that fill in
during Phase 1.

See `phase-0-deep-dive.md` for the reasoning behind every choice and `CLAUDE.md` for
the conventions Claude Code follows in this repo.

## Layout

```
apps/
  web/             Next.js 16 App Router + React 19 + Tailwind v4 (workspace: @scaffold/web)
  api/             FastAPI on Python 3.12, managed by uv (project: scaffold-api)
packages/
  shared-types/    Pydantic models → generated TS types  [stub]
  ui/              Shared components                     [stub]
infra/
  docker-compose.yml          Postgres 16 + pgvector, Redis 7 (loopback-bound)
  .env.example                Compose env template
  init/postgres/              First-boot SQL (auto-enables pgvector)
  neon-branch.sh              Per-PR Neon branches       [Phase 1 placeholder]
.claude/
  commands/        Custom slash commands                 [empty]
  agents/          Subagent configs                      [empty]
  mcp.json         MCP server wiring                     [empty {}]
CLAUDE.md          Project context for Claude Code
phase-0-deep-dive.md   Phase 0 reference + reasoning
```

## Stack

- **Frontend:** Next.js 16 (App Router, Turbopack), React 19, TypeScript, Tailwind v4
- **Backend:** FastAPI (async), Pydantic — Pydantic AI lands when Phase 1 needs it
- **Data:** Postgres 16 + pgvector locally via Docker; Neon in prod
- **Cache/queue:** Redis 7
- **Package managers:** `pnpm` (Node 22), `uv` (Python 3.12)
- **Source control:** GitLab (`git@gitlab.com:lazarus_id_group/scaffold.git`), not GitHub

## Quickstart

```bash
# 1. Local services (Postgres + pgvector + Redis), loopback-bound
docker compose -f infra/docker-compose.yml up -d

# 2. Node deps for the monorepo
pnpm install

# 3. Python deps for the api
uv sync --directory apps/api
```

### Run dev servers

```bash
# Web (port 3000) — must use the workspace filter; there is no root dev script
pnpm --filter @scaffold/web dev

# API (port 8000)
uv run --directory apps/api fastapi dev main.py

# Smoke
curl http://localhost:8000/health   # → {"status":"ok","version":"0.1.0"}
```

Target: clone → running local dev env in under 10 minutes.

## Local infra notes

- **Docker runtime is OrbStack**, not Docker Desktop. If `docker info` hangs, the
  daemon is wedged — `orb stop && orb start` is the usual fix.
- **All service ports bind to `127.0.0.1`** (web 3000, api 8000, postgres 5432,
  redis 6379). This is deliberate for the SSH-tunnel workflow into the Mac Mini:
  ```bash
  ssh -L 3000:localhost:3000 -L 8000:localhost:8000 \
      -L 5432:localhost:5432 -L 6379:localhost:6379 \
      lazarus@<host>
  ```
- **pgvector is auto-enabled** on first DB boot via
  `infra/init/postgres/01-enable-extensions.sql`. Don't `CREATE EXTENSION vector`
  by hand unless the data volume has been wiped.
- **Default DB URL:** `postgresql://postgres:postgres@localhost:5432/app`. Override
  by copying `infra/.env.example` to `infra/.env` (gitignored; Compose auto-loads).
- **Port conflicts with other freelance projects on the same Mac** are common.
  Diagnose with `lsof -iTCP:<port> -sTCP:LISTEN`; stop the offending container
  with `docker stop <name>`.

## What's not done yet

Tracked in `CLAUDE.md` under *Current state*:

- `packages/shared-types/` — Pydantic→TS codegen pipeline (only `package.json` stub)
- `packages/ui/` — workspace stub
- `.claude/commands/` — the five Phase 0 slash commands (`/plan`, `/review`,
  `/explain`, `/test`, `/decompose`)
- Root `Makefile` with `make test|lint|format` targets
- API deployment target — Railway vs. Fly.io (open)

## PDF Parser App (Phase 0 reference)

This scaffold ships with a small reference app that uploads PDFs, extracts content with the Anthropic API, persists Markdown in Postgres, and exports a `.docx`. The full flow lives at:

- API: `apps/api/` — `POST /documents`, `GET /documents`, `GET /documents/{id}`, `GET /documents/{id}/docx`
- Web: `apps/web/` — upload form at `/`, detail page at `/documents/{id}`
- Shared types: `packages/shared-types/` — Pydantic schemas + generated TS in `index.ts`

### Run locally

```bash
docker compose -f infra/docker-compose.yml up -d

# api: copy env, set ANTHROPIC_API_KEY, then start
cp -n apps/api/.env.example apps/api/.env
# edit apps/api/.env and fill in ANTHROPIC_API_KEY
cd apps/api && uv run alembic upgrade head
uv run fastapi dev app/main.py

# web: in another shell
cp -n apps/web/.env.example apps/web/.env.local
pnpm --filter @scaffold/web dev
```

Open http://localhost:3000.

### Try it

Upload a PDF through the UI. The API base64-encodes it, sends it to Claude as a `document` content block, stores the returned Markdown in `documents`, and renders it. Click "Download .docx" on the detail page for an Open XML export.

Without an `ANTHROPIC_API_KEY` set, the home page renders and the empty-state list works, but uploads will fail at the Anthropic call. Use the [Anthropic console](https://console.anthropic.com/) for a key.

### Regenerate TypeScript types after a schema change

```bash
cd apps/api && uv run python ../../packages/shared-types/scripts/gen_ts.py
```

### Tests

```bash
cd apps/api && uv run pytest
cd apps/api && uv run mypy app/ tests/ alembic/
cd apps/web && pnpm exec tsc --noEmit && pnpm lint
```

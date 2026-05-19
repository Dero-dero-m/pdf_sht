# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project: pdf-parser

## What this is

A small web app: a user uploads a PDF, the backend extracts the contents with the Anthropic API, the parsed Markdown is persisted in Postgres, the web app displays it, and the user can download a `.docx` rendering. Next.js 16 (App Router) on the web side, FastAPI on the api side, shared types generated from Pydantic models.

Production hosting is not yet wired (open question: Railway vs. Fly.io for the api).

## Stack & conventions

- **Source control:** GitLab. `origin` is `git@gitlab.com:lazarus_id_group/pdf_sht.git`. A second remote `scaffold` points at the freelance-starter template this was forked from — leave it alone unless intentionally backporting infrastructure improvements.
- **Languages/runtimes:** Node 22, Python 3.12
- **Package managers:** `pnpm` (never `npm`/`yarn`), `uv` (never `pip`/`poetry`/`conda`)
- **Frontend:** Next.js 16 App Router. Server Components by default; push `"use client"` as far down the tree as possible. `apps/web/AGENTS.md` warns that Next 16 has breaking changes vs. training data — read `apps/web/node_modules/next/dist/docs/` before writing Next code.
- **Backend:** FastAPI, async by default. Use `AsyncAnthropic` (never sync clients inside `async def`). For unavoidable sync work, use `run_in_threadpool`.
- **Shared types:** Pydantic models in `packages/shared-types/src/scaffold_shared_types/schemas.py`; TS generated to `packages/shared-types/index.ts` via `pydantic2ts`. Regenerate after any schema change (see README).
- **Lint/format/typecheck:** `ruff` + `mypy strict` on the Python side; `eslint` + `tsc --noEmit` on the JS side.
- **Tests:** `pytest` (api, against a real `app_test` Postgres DB — no SQLite substitution). No web tests yet beyond `tsc` + `pnpm lint`; smoke-test the UI in a browser.

## Workflows

- **New API endpoint:** define the Pydantic schema in `packages/shared-types/src/scaffold_shared_types/schemas.py`, regenerate TS, add the route in `apps/api/app/routes/`, add a pytest integration test alongside (use the `client` + `session` fixtures from `tests/conftest.py`; inject `FakeAnthropic` if the endpoint calls the model).
- **Local dev:** `docker compose -f infra/docker-compose.yml up -d` for services; `pnpm --filter @scaffold/web dev` for web (port 3000); `uv run --directory apps/api fastapi dev app/main.py` for api (port 8000). The web workspace name is still `@scaffold/web` — cosmetic legacy, harmless.
- **Migrations:** `uv run --directory apps/api alembic upgrade head` against the dev DB; pass `-x url=postgresql+asyncpg://postgres:postgres@localhost:5432/app_test` to target the test DB. Always check `alembic current` before applying.
- **Don't:**
  - mark components `"use client"` reflexively
  - use sync clients in async handlers
  - commit `packages/shared-types/index.ts` without regenerating it from the Pydantic source
  - run migrations without checking `alembic current` first
  - run `pnpm dev` from the repo root (there's no root dev script — always use `--filter`)
  - write Next.js code without first reading `apps/web/AGENTS.md` + the relevant guide under `apps/web/node_modules/next/dist/docs/`

## Local infra

- **Docker runtime is OrbStack, not Docker Desktop.** If `docker info` hangs, the daemon is in a broken state — `orb stop && orb start` is the typical fix. Docker CLI binary is symlinked into `/usr/local/bin/docker` from `/Applications/OrbStack.app/Contents/MacOS/xbin/docker`.
- **Default DB connection in dev:** `postgresql://postgres:postgres@localhost:5432/app`. Override by copying `infra/.env.example` to `infra/.env` (gitignored, auto-loaded by Compose).
- **Default ports** (all loopback-bound — never `0.0.0.0`): web 3000, api 8000, postgres 5432, redis 6379.
- **SSH-tunnel workflow:** the Mac Mini is typically accessed via SSH from another machine. Loopback binding is deliberate. Multi-port tunnel from the client: `ssh -L 3000:localhost:3000 -L 8000:localhost:8000 -L 5432:localhost:5432 -L 6379:localhost:6379 lazarus@<host>`.
- **pgvector is auto-enabled** on first DB boot via `infra/init/postgres/01-enable-extensions.sql`. The app doesn't use vectors yet; the extension is there for follow-ups (e.g. semantic search over extracted Markdown).
- **Multi-project port conflicts** on this Mac are common. Diagnosis: `lsof -iTCP:<port> -sTCP:LISTEN`. Fix: stop the conflicting container (`docker stop <name>`) — `unless-stopped` policy keeps it stopped.

## App-specific notes

- **`apps/api/.env` must include `ANTHROPIC_API_KEY`**. Without it, upload succeeds at the HTTP layer but `extract_markdown` fails at the model call and the route returns 502. The home page and the empty list still render.
- **Page count uses `pypdf.PdfReader(...).pages`** with a fallback of `1` on `PdfReadError`. The earlier `/Type /Page` substring heuristic was wrong (matched object-stream artifacts).
- **`.doc` (legacy CFB) is not supported.** Export is `.docx` (Open XML) via `python-docx`.
- **CORS is locked to `http://localhost:3000`** by default; override via `CORS_ORIGINS` in `apps/api/.env`.
- **Upload buffers the whole PDF into memory** before the size check (`MAX_UPLOAD_BYTES`, default 32 MiB). Acceptable for the cap; revisit if the cap grows.

## Plan / history

`docs/superpowers/plans/2026-05-18-pdf-parser-app.md` is the original implementation plan executed via subagent-driven development. It captures the original task decomposition and reasoning behind each major choice.

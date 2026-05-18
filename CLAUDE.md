# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project: freelance-starter

## What this is

The starter monorepo forked for every freelance project. A Next.js 16 web app (App Router, Server Components by default) talks to a FastAPI backend that uses Pydantic AI for LLM work. Shared types are generated from Pydantic models so the frontend and backend never drift. Local services (Postgres + pgvector, Redis) run via `docker compose`. Production hosting: Vercel (web), Railway or Fly.io (api), Neon (db).

## Stack & conventions

- **Source control:** GitLab, not GitHub. Remote is `git@gitlab.com:lazarus_id_group/scaffold.git`. The phase-0 doc generically recommends GitHub; this repo is the exception. CI lives on GitLab Pipelines, not GitHub Actions.
- **Languages/runtimes:** Node 22, Python 3.12
- **Package managers:** `pnpm` (never `npm`/`yarn`), `uv` (never `pip`/`poetry`/`conda`)
- **Frontend:** Next.js 16 App Router. Server Components by default; push `"use client"` as far down the tree as possible (a button is client; the page wrapper is server).
- **Backend:** FastAPI, async by default. Use `AsyncOpenAI` / async Anthropic client — never sync clients inside `async def`. For unavoidable sync work, use `run_in_threadpool`.
- **Shared types:** Pydantic models in `packages/shared-types/`, TypeScript types generated from them (e.g. via `pydantic2ts`). Regenerate after any schema change.
- **Lint/format/typecheck:** ruff (lint + format) + mypy strict on the Python side; ESLint + Prettier + `tsc --noEmit` on the JS side.
- **Tests:** pytest (api), Vitest or Playwright (web).
- **Commands:** A root `Makefile` with `make test|lint|format` targets is planned but not yet authored.

## Workflows

- **New API endpoint:** define Pydantic schema in `packages/shared-types/`, route in `apps/api/`, integration test alongside.
- **New UI component:** if reusable across apps, put it in `packages/ui/`; otherwise colocate in `apps/web/`.
- **Local dev:** `docker compose -f infra/docker-compose.yml up -d` for services; `pnpm --filter @scaffold/web dev` for web (port 3000); `uv run --directory apps/api fastapi dev app/main.py` for api (port 8000).
- **Don't:**
  - mark components `"use client"` reflexively
  - use sync clients in async handlers
  - commit generated TS types without regenerating
  - run migrations without checking `alembic current` first
  - run `pnpm dev` from the repo root (there's no root dev script — always use `--filter`)
  - write Next.js code without first reading `apps/web/AGENTS.md` (Next 16 has breaking changes that may not match training data)

## Local infra

- **Docker runtime is OrbStack, not Docker Desktop.** If `docker info` hangs, the daemon is in a broken state — `orb stop && orb start` is the typical fix. Docker CLI binary is symlinked into `/usr/local/bin/docker` from `/Applications/OrbStack.app/Contents/MacOS/xbin/docker`.
- **Default DB connection in dev:** `postgresql://postgres:postgres@localhost:5432/app`. Override by copying `infra/.env.example` to `infra/.env` (gitignored, auto-loaded by Compose).
- **Default ports** (all loopback-bound — never `0.0.0.0`): web 3000, api 8000, postgres 5432, redis 6379.
- **SSH-tunnel workflow:** the Mac Mini is typically accessed via SSH from another machine. Loopback binding is deliberate. Multi-port tunnel from the client: `ssh -L 3000:localhost:3000 -L 8000:localhost:8000 -L 5432:localhost:5432 -L 6379:localhost:6379 lazarus@<host>`.
- **pgvector is auto-enabled** on first DB boot via `infra/init/postgres/01-enable-extensions.sql`. Do not `CREATE EXTENSION vector` manually unless the data volume has been wiped.
- **Multi-project port conflicts** on this Mac are common (other freelance projects run their own Postgres/Redis). Diagnosis: `lsof -iTCP:<port> -sTCP:LISTEN`. Fix: stop the conflicting container (`docker stop <name>`) — `unless-stopped` policy keeps it stopped.

## Current state

Phase 0 scaffolding, partially wired:

- ✓ `apps/web/` — Next.js 16 App Router, TypeScript, Tailwind v4, Turbopack. Workspace name `@scaffold/web`.
- ✓ `apps/api/` — FastAPI on Python 3.12 (managed by `uv`), with a single `/health` endpoint as a smoke target. Project name `scaffold-api`.
- ✓ `infra/docker-compose.yml` — Postgres 16 + pgvector and Redis 7-alpine, both bound to `127.0.0.1` only, with healthchecks and `${VAR:-default}` env interpolation.
- ☐ `packages/shared-types/` — Pydantic→TS codegen pipeline (only `package.json` stub exists).
- ☐ `packages/ui/` — workspace stub (only `package.json` exists).
- ☐ `.claude/commands/` — five slash commands (`/plan`, `/review`, `/explain`, `/test`, `/decompose`) not yet authored.
- ☐ Root `Makefile` with `make test|lint|format` targets — not yet authored.

Open question: pick a deployment target for the api (Railway vs. Fly.io).

# Project: freelance-starter

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
- **Commands:** `make test`, `make lint`, `make format` (to be added in Phase 1).

## Workflows

- **New API endpoint:** define Pydantic schema in `packages/shared-types/`, route in `apps/api/`, integration test alongside.
- **New UI component:** if reusable across apps, put it in `packages/ui/`; otherwise colocate in `apps/web/`.
- **Local dev:** `docker compose -f infra/docker-compose.yml up -d`, then `pnpm dev` and `uv run --directory apps/api fastapi dev`.
- **Don't:** mark components `"use client"` reflexively; use sync clients in async handlers; commit generated TS types without regenerating; run migrations without checking `alembic current` first.

## Current state / TODO

- Phase 0: scaffolding only. Folders + skeleton files exist; nothing wired up yet.
- Next: install Claude Code on the Mac Mini, author the five Phase 0 slash commands (`/plan`, `/review`, `/explain`, `/test`, `/decompose`) in `.claude/commands/`, fill `infra/docker-compose.yml` with real services, ship a throwaway dogfood project end-to-end.
- Open question: pick a deployment target for the api (Railway vs. Fly.io).

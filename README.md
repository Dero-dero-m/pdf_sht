# freelance-starter

The starter monorepo for solo freelance work. Forked per project.

## Layout

```
apps/
  web/             Next.js 16 (App Router) frontend
  api/             FastAPI + Pydantic AI backend
packages/
  shared-types/    Pydantic models → generated TS types
  ui/              Shared shadcn components
infra/
  docker-compose.yml   Local services (Postgres + pgvector, Redis)
  neon-branch.sh       Per-PR Neon DB branches
.claude/
  commands/        Custom slash commands
  agents/          Subagent configs
  mcp.json         MCP server wiring
CLAUDE.md          Project context for Claude Code
```

## Quickstart

```bash
docker compose -f infra/docker-compose.yml up -d   # local services
pnpm install                                       # JS deps
uv sync --directory apps/api                       # Python deps
```

Target: clone → running local dev env in under 10 minutes.

## Stack

- Frontend: Next.js 16 (App Router), React Server Components by default
- Backend: FastAPI (async), Pydantic AI
- DB: Postgres + pgvector (local via Docker; Neon in prod)
- Cache/queue: Redis
- Package managers: `pnpm` (Node), `uv` (Python)

See `CLAUDE.md` for conventions and `phase-0-deep-dive.md` for the reasoning behind every choice.

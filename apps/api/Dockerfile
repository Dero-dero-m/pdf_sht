# syntax=docker/dockerfile:1.7
#
# Build context: REPO ROOT (so the workspace dep `../../packages/shared-types`
# in apps/api/pyproject.toml resolves). On Railway: set the service's
# Dockerfile Path to `apps/api/Dockerfile` with Root Directory at the repo root.

FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /repo

# Workspace member first so the editable [tool.uv.sources] entry resolves.
COPY packages/shared-types /repo/packages/shared-types
COPY apps/api /repo/apps/api

WORKDIR /repo/apps/api

# --frozen requires uv.lock to be current.
# --no-dev skips the test/lint group.
# --no-editable builds the workspace member as a wheel instead of editable.
RUN uv sync --frozen --no-dev --no-editable

ENV PYTHONUNBUFFERED=1 \
    UV_NO_SYNC=1
EXPOSE 8000

# Railway's UI Start Command overrides this; kept for local `docker run` parity.
CMD ["sh", "-c", "uv run alembic upgrade head && uv run fastapi run app/main.py --host 0.0.0.0 --port ${PORT:-8000}"]

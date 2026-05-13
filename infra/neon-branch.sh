#!/usr/bin/env bash
# Spin up a Neon DB branch for a PR / feature branch.
#
# Phase 0: placeholder. Phase 1 fills this in with real `neonctl` calls.
#
# Expected env:
#   NEON_API_KEY        - API token
#   NEON_PROJECT_ID     - target project
# Expected arg:
#   $1                  - branch name (defaults to current git branch)

set -euo pipefail

BRANCH="${1:-$(git rev-parse --abbrev-ref HEAD)}"

echo "TODO: create Neon branch '${BRANCH}' via neonctl"
echo "  neonctl branches create --name \"${BRANCH}\" --project-id \"\${NEON_PROJECT_ID}\""
exit 1

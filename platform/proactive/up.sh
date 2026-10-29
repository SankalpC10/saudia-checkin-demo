#!/usr/bin/env bash
# Start the proactive agent (host port 8002) and anomaly scorer against the local backends.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROACTIVE="${PROACTIVE_REPO:-$HOME/PycharmProjects/rt-ai-proactive-monitoring}"
export SAUDIA_PLATFORM="$(cd "$HERE/.." && pwd)"
export AGENT_HOST_PORT=8002
docker compose -f "$PROACTIVE/docker-compose.yml" -f "$HERE/compose.override.yml" \
  up -d mongodb agent anomaly-scorer "$@"   # add --build to rebuild images

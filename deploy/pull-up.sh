#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.nginx.prod.yml}"
IMAGE_TAG="${IMAGE_TAG:-main}"

echo "COMPOSE_FILE=$COMPOSE_FILE"
echo "IMAGE_TAG=$IMAGE_TAG"

# Note: if GHCR packages are private, run once:
#   docker login ghcr.io -u <github_user>

IMAGE_TAG="$IMAGE_TAG" docker compose -f "$COMPOSE_FILE" pull
IMAGE_TAG="$IMAGE_TAG" docker compose -f "$COMPOSE_FILE" up -d

IMAGE_TAG="$IMAGE_TAG" docker compose -f "$COMPOSE_FILE" exec -T -w /app backend sh -lc "PYTHONPATH=/app alembic upgrade head"

curl -fsS http://127.0.0.1:18000/health >/dev/null
echo "OK: backend health"


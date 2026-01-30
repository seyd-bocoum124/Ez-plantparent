#!/bin/sh
set -eu

COMPOSE_FILE="docker-compose.yml"

if [ $# -lt 1 ]; then
  echo "Usage: $0 <test-file>"
  exit 1
fi

TEST_FILE="$1"

# lance pytest uniquement sur ce fichier
docker compose -f "$COMPOSE_FILE" exec -e TESTING=1 backend pytest --log-cli-level=INFO --disable-warnings "$TEST_FILE"
#!/usr/bin/env bash
set -euo pipefail

CONTAINER_NAME="${CONTAINER_NAME:-morai_noetic_topic}"

if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
  echo "[ERROR] Container is not running: ${CONTAINER_NAME}"
  echo "Run this first:"
  echo "  ./run_noetic.sh"
  exit 1
fi

docker exec -it "${CONTAINER_NAME}" bash
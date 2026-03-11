#!/usr/bin/env bash
set -euo pipefail

NEO4J_URI="${NEO4J_URI:-bolt://localhost:7687}"
NEO4J_USER="${NEO4J_USER:-neo4j}"
NEO4J_PASSWORD="${NEO4J_PASSWORD:-openudi-dev-2026}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "==> Loading schema..."
if command -v cypher-shell &>/dev/null; then
  cypher-shell -u "$NEO4J_USER" -p "$NEO4J_PASSWORD" -a "$NEO4J_URI" -f "$SCRIPT_DIR/../neo4j/init.cypher"
  echo "==> Loading seed data..."
  cypher-shell -u "$NEO4J_USER" -p "$NEO4J_PASSWORD" -a "$NEO4J_URI" -f "$SCRIPT_DIR/seed-dev.cypher"
elif docker ps --format '{{.Names}}' | grep -q 'neo4j'; then
  CONTAINER=$(docker ps --format '{{.Names}}' | grep 'neo4j' | head -1)
  echo "Using container: $CONTAINER"
  docker exec -i "$CONTAINER" cypher-shell -u "$NEO4J_USER" -p "$NEO4J_PASSWORD" < "$SCRIPT_DIR/../neo4j/init.cypher"
  echo "==> Loading seed data..."
  docker exec -i "$CONTAINER" cypher-shell -u "$NEO4J_USER" -p "$NEO4J_PASSWORD" < "$SCRIPT_DIR/seed-dev.cypher"
else
  echo "ERROR: cypher-shell not found and no Neo4j container running"
  exit 1
fi

echo "==> Seed complete!"

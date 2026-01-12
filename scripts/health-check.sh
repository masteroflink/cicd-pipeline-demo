#!/bin/bash
set -e

# Health check script for CI/CD Pipeline Demo
# Usage: ./scripts/health-check.sh <base_url>

BASE_URL=${1:-http://localhost:8000}
MAX_RETRIES=5
RETRY_DELAY=2

echo "Health check for $BASE_URL"

for i in $(seq 1 $MAX_RETRIES); do
  echo "Attempt $i of $MAX_RETRIES..."

  RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/health" 2>/dev/null || echo "000")

  if [ "$RESPONSE" == "200" ]; then
    echo "Health check passed! (HTTP $RESPONSE)"

    # Get full health response
    echo "Health details:"
    curl -s "$BASE_URL/health" | python3 -m json.tool 2>/dev/null || curl -s "$BASE_URL/health"

    exit 0
  fi

  echo "Health check failed (HTTP $RESPONSE), retrying in ${RETRY_DELAY}s..."
  sleep $RETRY_DELAY
done

echo "Health check failed after $MAX_RETRIES attempts!"
exit 1

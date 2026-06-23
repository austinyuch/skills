#!/bin/bash
# CI/CD Example: Committee Decision Making (Shell)
#
# Usage in GitLab CI:
#   ./ci-cd.sh "Should we deploy this change?"
#
# Exit codes:
#   0 - Approved (go)
#   1 - Rejected (no-go) or error
#   2 - Conditional

set -e

SERVER_URL="${MCP_SERVER_URL:-http://localhost:8000/mcp}"
TOPIC="${1:-Should we deploy this change?}"

echo "🤖 CI/CD Committee Decision"
echo "📋 Topic: $TOPIC"
echo ""

# Start session
RESPONSE=$(curl -s -X POST "$SERVER_URL/tools/start_committee_session" \
  -H "Content-Type: application/json" \
  -d "{
    \"topic\": \"$TOPIC\",
    \"participants\": [
      {\"role\": \"architect\", \"provider\": \"openai\", \"model\": \"gpt-4\"},
      {\"role\": \"security\", \"provider\": \"anthropic\", \"model\": \"claude-3-sonnet\"}
    ],
    \"debate_rounds\": 1
  }")

SESSION_ID=$(echo "$RESPONSE" | jq -r '.session_id')

if [ -z "$SESSION_ID" ] || [ "$SESSION_ID" = "null" ]; then
  echo "❌ Failed to start session"
  exit 1
fi

echo "Session: $SESSION_ID"
echo "⏳ Waiting for decision..."

# Poll for completion
MAX_ATTEMPTS=60
ATTEMPT=0

while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
  STATUS_RESPONSE=$(curl -s -X POST "$SERVER_URL/tools/get_session_status" \
    -H "Content-Type: application/json" \
    -d "{\"session_id\": \"$SESSION_ID\"}")
  
  STATUS=$(echo "$STATUS_RESPONSE" | jq -r '.status')
  
  if [ "$STATUS" = "completed" ]; then
    break
  elif [ "$STATUS" = "error" ]; then
    echo "❌ Session failed"
    exit 1
  fi
  
  sleep 5
  ATTEMPT=$((ATTEMPT + 1))
done

# Get synthesis
SYNTHESIS=$(curl -s -X POST "$SERVER_URL/tools/synthesize_discussion" \
  -H "Content-Type: application/json" \
  -d "{\"session_id\": \"$SESSION_ID\"}")

DECISION=$(echo "$SYNTHESIS" | jq -r '.synthesis.decision // "no-go"')
SUMMARY=$(echo "$SYNTHESIS" | jq -r '.synthesis.summary' | cut -c1-200)

echo ""
echo "📊 Decision: $DECISION"
echo "Summary: $SUMMARY..."
echo ""

# Exit based on decision
case "$DECISION" in
  "go")
    echo "✅ APPROVED - Proceeding with deployment"
    exit 0
    ;;
  "conditional")
    echo "⚠️  CONDITIONAL - Review required"
    echo "Conditions:"
    echo "$SYNTHESIS" | jq -r '.synthesis.conditions[]?' | sed 's/^/  - /'
    exit 2
    ;;
  *)
    echo "❌ REJECTED - Deployment blocked"
    exit 1
    ;;
esac

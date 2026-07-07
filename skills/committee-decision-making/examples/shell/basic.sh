#!/bin/bash
# Basic Example: Committee Decision Making (Shell)
#
# Usage:
#   ./basic.sh "Should we adopt microservices?"

set -e

SERVER_URL="${MCP_SERVER_URL:-http://localhost:8000/mcp}"
TOPIC="${1:-Should we adopt microservices architecture?}"

echo "🚀 Starting committee discussion..."
echo "📋 Topic: $TOPIC"
echo ""

# Start session
echo "Starting session..."
RESPONSE=$(curl -s -X POST "$SERVER_URL/tools/start_committee_session" \
  -H "Content-Type: application/json" \
  -d "{
    \"topic\": \"$TOPIC\",
    \"participants\": [
      {\"role\": \"architect\", \"provider\": \"openai\", \"model\": \"gpt-4\"},
      {\"role\": \"devops\", \"provider\": \"anthropic\", \"model\": \"claude-3-sonnet\"}
    ],
    \"debate_rounds\": 1
  }")

SESSION_ID=$(echo "$RESPONSE" | jq -r '.session_id')

if [ -z "$SESSION_ID" ] || [ "$SESSION_ID" = "null" ]; then
  echo "❌ Failed to start session"
  echo "$RESPONSE" | jq .
  exit 1
fi

echo "✅ Session started: $SESSION_ID"
echo ""

# Poll for completion
echo "⏳ Waiting for completion..."
MAX_ATTEMPTS=60
ATTEMPT=0

while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
  STATUS_RESPONSE=$(curl -s -X POST "$SERVER_URL/tools/get_session_status" \
    -H "Content-Type: application/json" \
    -d "{\"session_id\": \"$SESSION_ID\"}")
  
  STATUS=$(echo "$STATUS_RESPONSE" | jq -r '.status')
  PHASE=$(echo "$STATUS_RESPONSE" | jq -r '.current_phase')
  
  echo "   Status: $STATUS, Phase: $PHASE"
  
  if [ "$STATUS" = "completed" ]; then
    break
  elif [ "$STATUS" = "error" ]; then
    echo "❌ Session failed"
    exit 1
  fi
  
  sleep 5
  ATTEMPT=$((ATTEMPT + 1))
done

if [ $ATTEMPT -eq $MAX_ATTEMPTS ]; then
  echo "⏱️  Timeout"
  exit 1
fi

echo ""
echo "📊 Getting synthesis..."

# Get synthesis
SYNTHESIS=$(curl -s -X POST "$SERVER_URL/tools/synthesize_discussion" \
  -H "Content-Type: application/json" \
  -d "{\"session_id\": \"$SESSION_ID\"}")

# Display results
echo ""
echo "=== Committee Decision ==="
echo ""
echo "Summary:"
echo "$SYNTHESIS" | jq -r '.synthesis.summary'
echo ""
echo "Recommendations:"
echo "$SYNTHESIS" | jq -r '.synthesis.recommendations[]' | nl
echo ""
echo "✅ Done!"

# Troubleshooting Guide

Common issues and solutions for LLM Committee Agent.

## Connection Issues

### Error: Connection refused

```
Error: Post "http://localhost:8000/mcp": dial tcp: connection refused
```

**Cause**: MCP server not running

**Solution**:
```bash
# Start server
go run cmd/server/main.go

# Or use Docker
docker run -p 8000:8000 llm-committee-agent
```

---

### Error: Timeout

```
Error: timeout after 300 seconds
```

**Causes**:
- LLM API slow response
- Network issues
- Complex discussion taking too long

**Solutions**:
1. Increase timeout:
```javascript
--timeout 600  // CLI
// or
timeout: 600000  // JavaScript (ms)
```

2. Check LLM API status
3. Reduce participants or rounds

---

## API Errors

### Error: SESSION_NOT_FOUND

```json
{
  "error": "Session not found",
  "code": "SESSION_NOT_FOUND"
}
```

**Causes**:
- Invalid session_id
- Session expired (TTL: 24 hours)

**Solutions**:
- Verify session_id
- Start new session if expired

---

### Error: PROVIDER_ERROR

```json
{
  "error": "Provider API error",
  "code": "PROVIDER_ERROR"
}
```

**Causes**:
- Invalid API key
- API quota exceeded
- Provider service down

**Solutions**:
1. Check API keys:
```bash
echo $OPENAI_API_KEY
echo $ANTHROPIC_API_KEY
echo $GEMINI_API_KEY
```

2. Check API quotas
3. Try different provider

---

### Error: RATE_LIMIT_EXCEEDED

```json
{
  "error": "Rate limit exceeded",
  "code": "RATE_LIMIT_EXCEEDED"
}
```

**Cause**: Too many requests (100/min limit)

**Solution**:
```javascript
// Implement retry with backoff
async function withRetry(fn, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error) {
      if (error.code === 'RATE_LIMIT_EXCEEDED' && i < maxRetries - 1) {
        await sleep(Math.pow(2, i) * 1000);
        continue;
      }
      throw error;
    }
  }
}
```

---

## SSE Issues

### No events received

**Causes**:
- Not connected to SSE endpoint
- No event_config in start_committee_session
- Firewall blocking SSE

**Solutions**:
1. Connect to SSE:
```javascript
const eventSource = new EventSource('http://localhost:8000/sse');
```

2. Configure events:
```javascript
await startSession({
  ...,
  event_config: {
    default_level: "progress"
  }
});
```

3. Check firewall settings

---

### SSE connection drops

**Cause**: Network instability

**Solution**:
```javascript
eventSource.onerror = (error) => {
  console.error('SSE error, reconnecting...');
  // Reconnect logic
  setTimeout(() => {
    eventSource = new EventSource('http://localhost:8000/sse');
  }, 5000);
};
```

---

## Performance Issues

### Slow response times

**Causes**:
- Too many participants
- Too many rounds
- Complex topic
- LLM API slow

**Solutions**:
1. Reduce participants (3-5 optimal)
2. Start with fewer rounds
3. Use faster models (claude-3-haiku, gpt-3.5-turbo)
4. Check LLM API status

---

### High costs

**Causes**:
- Not using prompt caching
- Too many rounds
- Using expensive models

**Solutions**:
1. Prompt caching is automatic (50-90% savings)
2. Start with 1-2 rounds
3. Use cost-effective models:
   - `claude-3-haiku` (cheapest)
   - `gpt-3.5-turbo` (fast and cheap)
   - `claude-3-sonnet` (balanced)

---

## CLI Issues

### Invalid participants format

```
Error: invalid format: architect:openai (expected role:provider:model)
```

**Solution**: Use correct format:
```bash
--participants "architect:openai:gpt-4,devops:anthropic:claude-3-sonnet"
```

---

### Command not found

```
bash: committee-discuss: command not found
```

**Solution**:
```bash
# Build and install
go install ./cmd/committee-discuss

# Or use full path
./committee-discuss --topic "..."
```

---

## Debugging

### Enable debug logging

```bash
# Server
LOG_LEVEL=debug go run cmd/server/main.go

# CLI
committee-discuss --topic "..." 2> debug.log
```

### Check server logs

```bash
# Docker
docker logs <container-id>

# Local
tail -f server.log
```

### Inspect HTTP traffic

```bash
# Use curl for debugging
curl -X POST http://localhost:8000/mcp/tools/start_committee_session \
  -H "Content-Type: application/json" \
  -d '{"topic":"test","participants":[...]}'
```

---

## Getting Help

1. Check [API Reference](./api-reference.md)
2. Check [Best Practices](./best-practices.md)
3. Check server logs
4. Open issue on GitLab

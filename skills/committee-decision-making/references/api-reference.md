# API Reference

Complete API reference for LLM Committee Agent MCP Server.

## Base URL

```
http://localhost:8000/mcp
```

## Authentication

Currently no authentication required for local development.

For production, use JWT/OAuth tokens in Authorization header:
```
Authorization: Bearer <token>
```

## MCP Tools

### 1. start_committee_session

Start a new committee discussion session.

**Endpoint**: `POST /mcp/tools/start_committee_session`

**Request Body**:
```json
{
  "topic": "string (required)",
  "participants": [
    {
      "role": "string (required)",
      "provider": "string (required)",
      "model": "string (required)"
    }
  ],
  "debate_rounds": "integer (optional, default: 1, max: 5)",
  "event_config": {
    "default_level": "string (optional: silent|minimal|progress|detailed)"
  }
}
```

**Response**:
```json
{
  "session_id": "string (UUID)",
  "status": "string (pending|running)",
  "topic": "string",
  "participants": [...],
  "created_at": "string (ISO 8601)"
}
```

**Error Responses**:
- `400 Bad Request`: Invalid parameters
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

---

### 2. get_session_status

Query session status and progress.

**Endpoint**: `POST /mcp/tools/get_session_status`

**Request Body**:
```json
{
  "session_id": "string (required)"
}
```

**Response**:
```json
{
  "session_id": "string",
  "status": "string (pending|running|completed|error)",
  "current_phase": "string (initial_opinions|debate|synthesis)",
  "progress": "number (0-100)",
  "total_opinions": "integer",
  "created_at": "string (ISO 8601)",
  "updated_at": "string (ISO 8601)",
  "error": "string (optional)"
}
```

---

### 3. read_discussion

Retrieve full discussion history.

**Endpoint**: `POST /mcp/tools/read_discussion`

**Request Body**:
```json
{
  "session_id": "string (required)",
  "filter": {
    "role": "string (optional)",
    "round": "integer (optional)"
  }
}
```

**Response**:
```json
{
  "session_id": "string",
  "opinions": [
    {
      "role": "string",
      "round": "integer",
      "content": "string",
      "timestamp": "string (ISO 8601)",
      "provider": "string",
      "model": "string"
    }
  ],
  "total_opinions": "integer"
}
```

---

### 4. synthesize_discussion

Generate consensus analysis.

**Endpoint**: `POST /mcp/tools/synthesize_discussion`

**Request Body**:
```json
{
  "session_id": "string (required)",
  "synthesis_prompt": "string (optional)"
}
```

**Response**:
```json
{
  "session_id": "string",
  "synthesis": {
    "summary": "string",
    "key_points": ["string"],
    "consensus": ["string"],
    "disagreements": ["string"],
    "recommendations": ["string"]
  },
  "metadata": {
    "total_opinions": "integer",
    "participants": ["string"],
    "rounds": "integer",
    "generated_at": "string (ISO 8601)"
  }
}
```

---

## Supported Roles

- `architect` - System design and architecture
- `devops` - Operations and deployment
- `security` - Security analysis
- `product` - Product and user experience
- `qa` - Quality assurance and testing

## Supported Providers

### OpenAI
- Models: `gpt-4`, `gpt-4-turbo`, `gpt-3.5-turbo`
- Features: Prompt caching

### Anthropic
- Models: `claude-3-opus`, `claude-3-sonnet`, `claude-3-haiku`
- Features: Prompt caching

### Google
- Models: `gemini-pro`, `gemini-1.5-pro`
- Features: Context caching

## Rate Limits

- **Default**: 100 requests per minute per client
- **Headers**:
  - `X-RateLimit-Limit`: Total allowed
  - `X-RateLimit-Remaining`: Remaining requests
  - `X-RateLimit-Reset`: Reset timestamp (Unix)

## Error Codes

| Code | Message | Description | Solution |
|------|---------|-------------|----------|
| `SESSION_NOT_FOUND` | Session not found | Invalid session_id | Check session_id value |
| `INVALID_PARAMETERS` | Invalid parameters | Missing/invalid params | Verify required parameters |
| `PROVIDER_ERROR` | LLM provider error | LLM API error | Check API keys and quotas |
| `RATE_LIMIT_EXCEEDED` | Rate limit exceeded | Too many requests | Wait and retry |
| `TIMEOUT` | Request timeout | Operation timed out | Increase timeout or retry |

## SSE Events

Connect to `/sse` endpoint for real-time events.

**Connection**:
```
GET http://localhost:8000/sse
Accept: text/event-stream
```

**Event Format**:
```
event: agent.completed
data: {"event_type":"agent.completed","session_id":"...","data":{...}}
```

**Event Types**:
- `session.started`
- `session.completed`
- `session.error`
- `phase.started`
- `phase.completed`
- `agent.started`
- `agent.completed`
- `agent.sub_invoke.completed`

## Performance

- **Session Duration**: 30-60 seconds per round
- **Concurrent Sessions**: 100+ supported
- **Event Latency**: < 100ms
- **Cost Savings**: 50-90% with prompt caching

## Versioning

API version is included in response headers:
```
X-API-Version: 1.5.0
```

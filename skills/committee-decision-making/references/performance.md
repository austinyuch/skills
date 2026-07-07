# Performance Metrics

Performance characteristics and optimization strategies.

## Benchmarks

### Session Duration

| Participants | Rounds | Avg Duration | Range |
|--------------|--------|--------------|-------|
| 2 | 1 | 35s | 30-45s |
| 3 | 1 | 50s | 45-60s |
| 3 | 2 | 90s | 80-110s |
| 5 | 2 | 120s | 100-150s |
| 5 | 3 | 180s | 150-220s |

### Concurrent Sessions

- **Supported**: 100+ concurrent sessions
- **Tested**: 150 concurrent sessions
- **Resource usage**: ~50MB RAM per session

### Event Latency

- **SSE events**: < 100ms from generation to delivery
- **Polling interval**: 2s (CLI)
- **Status query**: < 50ms

### Cost Savings

With prompt caching:
- **OpenAI**: 50-70% savings
- **Anthropic**: 70-90% savings
- **Google**: 60-80% savings

## Resource Usage

### Server

- **CPU**: 2 vCPU recommended
- **RAM**: 4GB minimum, 8GB recommended
- **Network**: 1Mbps per concurrent session
- **Storage**: 1GB for session data

### Client

- **CLI**: < 10MB RAM
- **JavaScript**: < 50MB RAM
- **Network**: Minimal (HTTP requests only)

## Optimization Strategies

### 1. Participant Selection

**Optimal**: 3-5 participants
- Good balance of diversity and speed
- Covers main perspectives
- Reasonable duration

**Avoid**: 7+ participants
- Diminishing returns
- Significantly longer duration
- Higher costs

### 2. Round Selection

**Start with 1 round**:
- Quick initial assessment
- Can always run more rounds if needed

**Use 2 rounds for standard decisions**:
- Good balance
- Allows refinement
- Not too long

**Reserve 3+ rounds for critical decisions**:
- High-stakes decisions
- Complex trade-offs
- Need deep exploration

### 3. Model Selection

**For speed**:
- `gpt-3.5-turbo` (fastest)
- `claude-3-haiku` (fast and cheap)

**For quality**:
- `gpt-4` (best reasoning)
- `claude-3-opus` (best analysis)

**For balance**:
- `claude-3-sonnet` (recommended)
- `gpt-4-turbo` (good balance)

### 4. Caching

**Automatic optimizations**:
- Prompt caching enabled by default
- Context reuse across rounds
- Efficient token management

**Manual optimizations**:
- Reuse similar topics
- Batch related questions
- Use consistent participant roles

## Scaling

### Horizontal Scaling

```yaml
# Docker Compose
services:
  committee-agent:
    image: llm-committee-agent
    replicas: 3
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
```

### Load Balancing

```
Load Balancer
    │
    ├─── Server 1 (sessions 1-50)
    ├─── Server 2 (sessions 51-100)
    └─── Server 3 (sessions 101-150)
```

### Session Affinity

- Use session_id for routing
- Sticky sessions recommended
- Share session storage (S3, Redis)

## Monitoring

### Key Metrics

1. **Session duration**: Track p50, p95, p99
2. **Success rate**: % of completed sessions
3. **Error rate**: % of failed sessions
4. **Cost per session**: Track LLM API costs
5. **Concurrent sessions**: Current load

### Alerts

- Session duration > 300s
- Error rate > 5%
- Concurrent sessions > 80% capacity
- Cost per session > threshold

## Limits

### Hard Limits

- **Max participants**: 10
- **Max rounds**: 5
- **Max session duration**: 600s (10 min)
- **Session TTL**: 24 hours
- **Rate limit**: 100 req/min per client

### Soft Limits (Recommended)

- **Participants**: 3-5
- **Rounds**: 1-3
- **Session duration**: < 180s
- **Concurrent sessions**: < 100

## Future Optimizations

### Planned

- [ ] Streaming responses (partial results)
- [ ] Parallel round execution
- [ ] Smart caching (cross-session)
- [ ] Model selection optimization

### Under Consideration

- [ ] GPU acceleration
- [ ] Edge deployment
- [ ] Offline mode
- [ ] Result caching

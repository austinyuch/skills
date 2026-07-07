# Best Practices

Recommendations for using LLM Committee Agent effectively.

## Participant Selection

### Number of Participants

**2-3 participants**: Quick decisions
- ✅ Fast execution (30-45s per round)
- ✅ Clear trade-offs
- ❌ Limited perspectives

**3-5 participants**: Balanced analysis
- ✅ Diverse viewpoints
- ✅ Comprehensive coverage
- 🟡 Moderate duration (45-60s per round)

**5+ participants**: Comprehensive analysis
- ✅ Maximum diversity
- ✅ All aspects covered
- ❌ Longer duration (60-90s per round)

### Role Combinations

**Architecture Decision**:
```
architect + devops + security
```
Focus: Technical feasibility, operations, security

**Technology Stack**:
```
architect + devops + product
```
Focus: Technical fit, operations, user impact

**Security Review**:
```
security + architect + devops
```
Focus: Threat analysis, design, operations

**Feature Planning**:
```
product + architect + qa
```
Focus: User value, feasibility, quality

## Debate Rounds

### 1 Round (Lean Coffee)
- **Use when**: Simple decisions, time-sensitive
- **Duration**: ~30-45 seconds
- **Example**: Library version upgrade

### 2 Rounds (Double Diamond)
- **Use when**: Standard complexity
- **Duration**: ~60-90 seconds
- **Process**: Discover/Define → Develop/Deliver
- **Example**: Technology stack selection

### 3+ Rounds (Delphi Method)
- **Use when**: Complex, high-stakes decisions
- **Duration**: ~90-180 seconds
- **Process**: Multiple iterations for consensus
- **Example**: Architecture redesign

## Cost Optimization

### Automatic Optimizations
- ✅ Prompt caching (50-90% savings)
- ✅ Parallel execution
- ✅ Efficient context management

### Manual Optimizations

**Start with fewer rounds**:
```javascript
// Start with 1 round
const session = await startSession({rounds: 1});

// If needed, start new session with more rounds
if (needsMoreAnalysis) {
  const deeperSession = await startSession({rounds: 3});
}
```

**Use appropriate models**:
- `gpt-4`: Complex reasoning, critical decisions
- `claude-3-sonnet`: Balanced performance/cost
- `claude-3-haiku`: Simple decisions, cost-sensitive

**Reuse sessions**:
```javascript
// Don't create new session for related questions
const session1 = await startSession({topic: "Should we use microservices?"});
// ... get result

// For follow-up, reference previous discussion
const session2 = await startSession({
  topic: "Given we're adopting microservices, how should we handle auth?",
  // Include context from session1 in topic
});
```

## Error Handling

### Retry Strategy

```javascript
async function startSessionWithRetry(args, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await startSession(args);
    } catch (error) {
      if (error.code === 'RATE_LIMIT_EXCEEDED') {
        // Exponential backoff
        await sleep(Math.pow(2, i) * 1000);
        continue;
      }
      if (error.code === 'PROVIDER_ERROR') {
        // Check if transient error
        if (i < maxRetries - 1) {
          await sleep(5000);
          continue;
        }
      }
      throw error;
    }
  }
}
```

### Timeout Handling

```javascript
async function startSessionWithTimeout(args, timeoutMs = 120000) {
  const timeoutPromise = new Promise((_, reject) =>
    setTimeout(() => reject(new Error('Timeout')), timeoutMs)
  );
  
  return Promise.race([
    startSession(args),
    timeoutPromise
  ]);
}
```

## Real-Time Progress

### SSE Event Handling

```javascript
const eventSource = new EventSource('http://localhost:8000/sse');

// Track progress
let progress = 0;
eventSource.addEventListener('agent.completed', (event) => {
  progress += 1;
  console.log(`Progress: ${progress}/${totalAgents}`);
});

// Handle completion
eventSource.addEventListener('session.completed', (event) => {
  console.log('Session completed!');
  eventSource.close();
});

// Handle errors
eventSource.onerror = (error) => {
  console.error('SSE error:', error);
  eventSource.close();
};
```

### Event Level Selection

**silent**: No agent events
- Use when: Don't need progress updates
- Benefit: Minimal overhead

**minimal**: Only completion events
- Use when: Just need to know when agents finish
- Benefit: Low overhead, basic progress

**progress**: Start + completion (default)
- Use when: Need progress tracking
- Benefit: Good balance

**detailed**: All events including sub-invokes
- Use when: Need detailed debugging
- Benefit: Full visibility

## Session Management

### Cleanup

```javascript
// Store session IDs for cleanup
const activeSessions = new Set();

async function startManagedSession(args) {
  const result = await startSession(args);
  activeSessions.add(result.session_id);
  return result;
}

// Cleanup on exit
process.on('exit', () => {
  activeSessions.forEach(sessionId => {
    // Sessions auto-expire, but good practice to track
  });
});
```

### Concurrent Sessions

```javascript
// Run multiple sessions in parallel
const sessions = await Promise.all([
  startSession({topic: "Question 1", ...}),
  startSession({topic: "Question 2", ...}),
  startSession({topic: "Question 3", ...})
]);

// Wait for all to complete
const results = await Promise.all(
  sessions.map(s => pollUntilComplete(s.session_id))
);
```

## Topic Formulation

### Good Topics

✅ **Specific and focused**:
```
"Should we use PostgreSQL or MongoDB for user data storage?"
```

✅ **Clear decision needed**:
```
"Should we adopt microservices architecture for our e-commerce platform?"
```

✅ **Actionable**:
```
"What's the best approach to implement authentication: JWT or session-based?"
```

### Poor Topics

❌ **Too broad**:
```
"How should we build our system?"
```

❌ **No clear decision**:
```
"Tell me about microservices"
```

❌ **Multiple questions**:
```
"Should we use React or Vue, and also should we use TypeScript?"
```

## Synthesis Customization

### Custom Synthesis Prompt

```javascript
const synthesis = await synthesizeDiscussion({
  session_id: sessionId,
  synthesis_prompt: `
    Focus on:
    1. Security implications
    2. Cost analysis (development + operational)
    3. Timeline estimates
    4. Risk assessment
    
    Provide specific recommendations with justification.
  `
});
```

## Monitoring and Logging

### Log Important Events

```javascript
const logger = createLogger();

eventSource.addEventListener('session.started', (event) => {
  const data = JSON.parse(event.data);
  logger.info('Session started', {
    session_id: data.session_id,
    topic: data.data.topic,
    participants: data.data.participants.length
  });
});

eventSource.addEventListener('session.completed', (event) => {
  const data = JSON.parse(event.data);
  logger.info('Session completed', {
    session_id: data.session_id,
    duration_ms: data.data.duration_ms,
    total_opinions: data.data.total_opinions
  });
});
```

## Testing

### Unit Testing

```javascript
describe('Committee Discussion', () => {
  it('should complete session successfully', async () => {
    const result = await startSession({
      topic: "Test topic",
      participants: [
        {role: "architect", provider: "openai", model: "gpt-4"}
      ]
    });
    
    expect(result.session_id).toBeDefined();
    expect(result.status).toBe('running');
  });
});
```

### Integration Testing

```javascript
describe('Full Discussion Flow', () => {
  it('should complete full discussion', async () => {
    // Start session
    const session = await startSession({...});
    
    // Poll until complete
    await pollUntilComplete(session.session_id);
    
    // Get synthesis
    const synthesis = await synthesizeDiscussion({
      session_id: session.session_id
    });
    
    expect(synthesis.synthesis.summary).toBeDefined();
    expect(synthesis.synthesis.recommendations.length).toBeGreaterThan(0);
  }, 120000); // 2 minute timeout
});
```

## Related Documentation

- [API Reference](./api-reference.md)
- [Troubleshooting](./troubleshooting.md)
- [Performance Metrics](./performance.md)

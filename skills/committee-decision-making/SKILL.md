---
name: committee-decision-making
version: 1.5.0
category: collaborative-ai
provider: mcp-server
transport: http-streamable
endpoint: http://localhost:8000/mcp
description: Multi-LLM collaborative decision-making through structured committee discussions inspired by Double Diamond, Delphi Method, and Lean Coffee

# References - Additional knowledge for coordinator agents
references:
  - type: api-reference
    title: API Reference
    path: ./references/api-reference.md
    description: Detailed API endpoints, parameters, and responses
  - type: best-practices
    title: Best Practices
    path: ./references/best-practices.md
    description: Usage patterns, optimization tips, and recommendations
  - type: troubleshooting
    title: Troubleshooting Guide
    path: ./references/troubleshooting.md
    description: Common issues and solutions
  - type: performance
    title: Performance Metrics
    path: ./references/performance.md
    description: Benchmarks, limits, and optimization strategies

# Examples - Ready-to-use code samples
examples:
  - language: javascript
    path: ./examples/javascript/
    files:
      - basic.js
      - advanced.js
      - ci-cd.js
  - language: python
    path: ./examples/python/
    files:
      - basic.py
      - advanced.py
      - ci-cd.py
  - language: shell
    path: ./examples/shell/
    files:
      - basic.sh
      - ci-cd.sh

# Documentation - Related documentation
documentation:
  - type: agent-reference
    title: MCP Server Reference
    path: ../../AGENT.md
    description: Complete MCP tool reference for coordinator agents
  - type: api-quick-reference
    title: API Quick Reference
    path: ../../docs/API_QUICK_REFERENCE.md
    description: Quick API reference with examples
  - type: sse-events
    title: SSE Events Specification
    path: ../../docs/SSE_EVENTS.md
    description: Real-time event streaming specification
  - type: cli-tool
    title: CLI Tool
    path: ../../cmd/committee-discuss/README.md
    description: Command-line tool for script integration

# Auto-generated metadata
generated_at: 2026-02-25T16:00:31+08:00
generated_from_version: 1.5.0
code_repository: https://[YOUR_REPO_URL]

keywords:
  - decision-making
  - multi-llm
  - committee
  - consensus
  - architecture
  - technical-decision
  - collaborative-ai
  - structured-discussion
  - risk-assessment
  - technology-selection
  - double-diamond
  - delphi-method
  - lean-coffee
  - facilitation
  - divergent-thinking
  - convergent-thinking
  - expert-panel
  - iterative-refinement
capabilities:
  - structured-discussion
  - multi-perspective-analysis
  - consensus-building
  - real-time-events
  - cost-optimization
  - iterative-refinement
  - expert-facilitation
use_cases:
  - technical-architecture-decisions
  - technology-stack-selection
  - risk-assessment
  - complex-problem-analysis
  - security-review
  - devops-strategy
  - design-thinking-workshops
  - expert-panel-discussions
supported_roles:
  - architect
  - devops
  - security
  - product
  - qa
supported_providers:
  - openai
  - anthropic
  - gemini
mcp_tools:
  - start_committee_session
  - get_session_status
  - read_discussion
  - synthesize_discussion
---

# Committee Decision Making Skill

Multi-LLM collaborative decision-making through structured committee discussions inspired by proven facilitation methodologies.

## Overview

This skill enables complex decision-making by orchestrating discussions between multiple LLM experts with different roles (architect, devops, security, product, qa). The system coordinates structured debates to reach consensus and provide comprehensive analysis from multiple perspectives.

### Inspired by Proven Methodologies

This skill combines elements from established decision-making and facilitation frameworks:

**🔷 Double Diamond (Design Thinking)**
- **Discover & Define**: Initial opinions phase explores the problem space (divergent thinking)
- **Develop & Deliver**: Debate rounds refine solutions (convergent thinking)
- Systematic exploration before convergence to solutions

**🎯 Delphi Method (Expert Panel)**
- **Expert Anonymity**: Each AI expert provides independent opinions
- **Iterative Rounds**: Multiple debate rounds for refinement
- **Controlled Feedback**: Experts see others' opinions between rounds
- **Consensus Building**: Synthesis phase aggregates expert insights

**☕ Lean Coffee (Structured Discussion)**
- **Topic-Driven**: Clear discussion topic/question
- **Time-Boxed**: Efficient rounds with clear phases
- **Democratic**: All participants contribute equally
- **Action-Oriented**: Synthesis produces actionable recommendations

### Core Value

- **Diverse Perspectives**: Get insights from multiple domain experts simultaneously
- **Structured Process**: Clear phases (initial opinions → debate → synthesis)
- **Consensus Building**: Systematic approach to reach agreement
- **Cost Efficient**: 50-90% cost savings with prompt caching
- **Real-Time Tracking**: SSE events for progress monitoring

## When to Use

Use this skill when you need:

✅ **Multiple Expert Perspectives** (Delphi Method)
- Architecture decisions requiring input from multiple domains
- Technology choices affecting different teams
- Complex trade-offs needing balanced analysis
- Independent expert opinions before group discussion

✅ **Complex Technical Decisions** (Double Diamond)
- Microservices vs monolith architecture
- Database selection (SQL vs NoSQL)
- Cloud provider selection
- Framework and library choices
- Explore problem space before converging on solutions

✅ **Risk Assessment** (Expert Panel)
- Security implications of architectural changes
- Operational risks of new technologies
- Cost-benefit analysis from multiple angles
- Comprehensive threat modeling

✅ **Consensus Building** (Lean Coffee)
- Resolving conflicting opinions
- Finding common ground between teams
- Structured debate for better decisions
- Time-boxed, action-oriented discussions

✅ **Comprehensive Analysis** (Iterative Refinement)
- Full coverage of technical, operational, and security aspects
- Identifying blind spots and edge cases
- Exploring alternatives systematically
- Multiple rounds for deeper insights

## MCP Tools

### 1. start_committee_session

Start a new committee discussion session.

**Purpose**: Initiate collaborative decision-making with multiple AI experts.

**Parameters**:
```json
{
  "topic": "Should we adopt microservices architecture?",
  "participants": [
    {
      "role": "architect",
      "provider": "openai",
      "model": "gpt-4"
    },
    {
      "role": "devops",
      "provider": "anthropic",
      "model": "claude-3-sonnet"
    },
    {
      "role": "security",
      "provider": "gemini",
      "model": "gemini-pro"
    }
  ],
  "debate_rounds": 2,
  "event_config": {
    "default_level": "progress"
  }
}
```

**Returns**:
```json
{
  "session_id": "abc-123-def-456",
  "status": "running",
  "created_at": "2026-02-25T15:00:00Z"
}
```

---

### 2. get_session_status

Query session status and progress.

**Purpose**: Monitor long-running discussions.

**Parameters**:
```json
{
  "session_id": "abc-123-def-456"
}
```

**Returns**:
```json
{
  "status": "running",
  "current_phase": "debate",
  "progress": 50,
  "total_opinions": 4
}
```

---

### 3. read_discussion

Retrieve full discussion history.

**Purpose**: Analyze individual perspectives and discussion flow.

**Parameters**:
```json
{
  "session_id": "abc-123-def-456",
  "filter": {
    "role": "architect"
  }
}
```

**Returns**:
```json
{
  "opinions": [
    {
      "role": "architect",
      "round": 1,
      "content": "From an architectural perspective...",
      "timestamp": "2026-02-25T15:00:30Z"
    }
  ]
}
```

---

### 4. synthesize_discussion

Generate consensus analysis and recommendations.

**Purpose**: Extract actionable insights from the discussion.

**Parameters**:
```json
{
  "session_id": "abc-123-def-456",
  "synthesis_prompt": "Focus on security and cost implications"
}
```

**Returns**:
```json
{
  "synthesis": {
    "summary": "The committee reached consensus on...",
    "key_points": [...],
    "consensus": [...],
    "disagreements": [...],
    "recommendations": [...]
  }
}
```

## Usage Examples

### Example 1: Quick Decision (Single Round)

For simple decisions with clear trade-offs:

```javascript
// 1. Start session
const session = await callTool("start_committee_session", {
  topic: "Should we use PostgreSQL or MongoDB for user data?",
  participants: [
    {role: "architect", provider: "openai", model: "gpt-4"},
    {role: "devops", provider: "anthropic", model: "claude-3-sonnet"}
  ],
  debate_rounds: 1
});

// 2. Wait for completion
let status;
do {
  await sleep(5000);
  status = await callTool("get_session_status", {
    session_id: session.session_id
  });
} while (status.status !== "completed");

// 3. Get synthesis
const result = await callTool("synthesize_discussion", {
  session_id: session.session_id
});

console.log("Recommendation:", result.synthesis.recommendations);
```

**Use Case**: Database selection, library choices, simple architecture decisions

---

### Example 2: Deep Analysis (Multiple Rounds)

For complex decisions requiring thorough exploration:

```javascript
const session = await callTool("start_committee_session", {
  topic: "Microservices migration strategy for legacy monolith",
  participants: [
    {role: "architect", provider: "openai", model: "gpt-4"},
    {role: "devops", provider: "anthropic", model: "claude-3-sonnet"},
    {role: "security", provider: "gemini", model: "gemini-pro"},
    {role: "product", provider: "openai", model: "gpt-4"}
  ],
  debate_rounds: 3  // More rounds for deeper analysis
});

// Read discussion to see evolution of arguments
const discussion = await callTool("read_discussion", {
  session_id: session.session_id
});

// Analyze how opinions evolved across rounds
discussion.opinions.forEach(opinion => {
  console.log(`Round ${opinion.round} - ${opinion.role}:`, 
              opinion.content.substring(0, 100));
});
```

**Use Case**: Architecture migrations, major technology changes, strategic decisions

---

### Example 3: Real-Time Monitoring

For interactive applications needing progress updates:

```javascript
// Connect to SSE for real-time events
const eventSource = new EventSource('http://localhost:8000/sse');

eventSource.addEventListener('agent.completed', (event) => {
  const data = JSON.parse(event.data);
  console.log(`✅ ${data.data.agent.role} completed`);
  console.log(`   ${data.data.output.content.substring(0, 150)}...`);
});

eventSource.addEventListener('phase.completed', (event) => {
  const data = JSON.parse(event.data);
  console.log(`📍 Phase ${data.data.phase} completed`);
});

// Start session with event config
const session = await callTool("start_committee_session", {
  topic: "Cloud provider selection: AWS vs GCP vs Azure",
  participants: [
    {role: "architect", provider: "openai", model: "gpt-4"},
    {role: "devops", provider: "anthropic", model: "claude-3-sonnet"},
    {role: "security", provider: "gemini", model: "gemini-pro"}
  ],
  debate_rounds: 2,
  event_config: {
    default_level: "progress"  // Get real-time updates
  }
});
```

**Use Case**: Interactive dashboards, long-running analyses, user-facing applications

## Best Practices

### 1. Choose Appropriate Participants

**2-3 participants**: Quick decisions, clear trade-offs
- Example: Database selection (architect + devops)
- Duration: ~30-45 seconds per round

**3-5 participants**: Complex decisions, multiple dimensions
- Example: Architecture migration (architect + devops + security + product)
- Duration: ~45-60 seconds per round

**5+ participants**: Comprehensive analysis, high-stakes decisions
- Example: Major platform change (all roles)
- Duration: ~60-90 seconds per round

### 2. Select Debate Rounds

The system supports iterative refinement inspired by the Delphi Method:

**1 round**: Simple decisions, time-sensitive (Lean Coffee style)
- Use when: Clear options, well-understood trade-offs
- Example: Library version upgrade
- Duration: ~30-45 seconds

**2 rounds**: Standard complexity, balanced analysis (Double Diamond)
- Use when: Multiple factors, need discussion
- Example: Technology stack selection
- Process: Discover/Define (round 1) → Develop/Deliver (round 2)
- Duration: ~60-90 seconds

**3+ rounds**: Complex decisions, need deep exploration (Delphi Method)
- Use when: High stakes, many unknowns
- Example: Architecture redesign
- Process: Multiple iterations for consensus building
- Duration: ~90-180 seconds

### 3. Role Selection

Common combinations:

**Architecture Decision**
- Roles: architect + devops + security
- Focus: Technical feasibility, operational impact, security

**Technology Stack**
- Roles: architect + devops + product
- Focus: Technical fit, operations, user impact

**Security Review**
- Roles: security + architect + devops
- Focus: Threat analysis, design review, operational security

**Feature Planning**
- Roles: product + architect + qa
- Focus: User value, technical feasibility, quality

### 4. Cost Optimization

**Automatic Optimizations**:
- ✅ Prompt caching (50-90% savings)
- ✅ Parallel execution (faster completion)
- ✅ Efficient context management

**Manual Optimizations**:
- Start with fewer rounds, add more if needed
- Use appropriate models:
  - `gpt-4`: Complex reasoning, critical decisions
  - `claude-3-sonnet`: Balanced performance
  - `claude-3-haiku`: Simple decisions, cost-sensitive
- Reuse sessions for related questions

### 5. Error Handling

Always handle common errors:

```javascript
try {
  const session = await callTool("start_committee_session", {...});
} catch (error) {
  if (error.code === "PROVIDER_ERROR") {
    // LLM API error - check API keys and quotas
    console.error("Provider error:", error.message);
  } else if (error.code === "RATE_LIMIT_EXCEEDED") {
    // Too many requests - wait and retry
    await sleep(60000);
    // Retry...
  } else {
    // Other errors
    console.error("Unexpected error:", error);
  }
}
```

## Methodology Mapping

This skill implements proven decision-making methodologies adapted for AI collaboration:

### Decision Techniques Used

**✅ Currently Implemented**:
- **Consensus Analysis**: AI-powered synthesis identifies agreement areas
- **Diversity Scoring**: Measures variety of perspectives
- **Coverage Analysis**: Ensures all aspects are addressed
- **Iterative Refinement**: Multiple rounds for deeper exploration
- **Expert Synthesis**: Moderator aggregates insights (Delphi-style)

**❌ Not Implemented** (Future Consideration):
- **Dot Voting**: Participants vote on ideas/solutions
- **Weighted Scoring**: Assign numerical weights to options
- **Ranked Choice**: Participants rank preferences
- **Affinity Mapping**: Group similar ideas together

**Why No Voting?**
- Each AI expert provides comprehensive analysis, not simple votes
- Focus on understanding reasoning, not counting preferences
- Synthesis extracts consensus through semantic analysis
- Better suited for complex technical decisions requiring nuanced understanding

### Double Diamond (Design Thinking)

```
Phase 1: Discover (Divergent)
├── Initial Opinions: Each expert explores the problem space
└── Parallel execution: Maximum diversity of perspectives

Phase 2: Define (Convergent)
├── Debate Round 1: Experts respond to each other
└── Identify key themes and constraints

Phase 3: Develop (Divergent)
├── Debate Round 2+: Explore solution alternatives
└── Consider trade-offs and implications

Phase 4: Deliver (Convergent)
├── Synthesis: Aggregate insights
└── Actionable recommendations
```

**Use Case**: Architecture decisions, design choices, innovation projects

---

### Delphi Method (Expert Panel)

```
Round 1: Independent Expert Opinions
├── Each AI expert provides initial assessment
├── No influence from other experts
└── Capture diverse viewpoints

Round 2+: Controlled Feedback
├── Experts see anonymized opinions from Round 1
├── Refine positions based on new information
├── Identify areas of agreement/disagreement
└── Move toward consensus

Synthesis: Aggregate Expert Judgment
├── Statistical aggregation of opinions
├── Identify consensus areas
├── Document remaining disagreements
└── Provide confidence levels
```

**Use Case**: Risk assessment, forecasting, expert judgment needed

---

### Lean Coffee (Structured Discussion)

```
Setup: Topic Definition
├── Clear, focused discussion question
└── Time-boxed rounds

Discussion: Structured Rounds
├── Round 1: Initial perspectives (5-10 min)
├── Round 2: Deeper exploration (5-10 min)
└── Round 3: Action items (optional)

Synthesis: Action-Oriented Output
├── Key decisions made
├── Action items identified
└── Next steps defined
```

**Use Case**: Quick decisions, team alignment, sprint planning

---

### Methodology Comparison

| Methodology | Rounds | Participants | Best For | Duration |
|-------------|--------|--------------|----------|----------|
| **Lean Coffee** | 1-2 | 2-3 | Quick decisions, team sync | 30-60s |
| **Double Diamond** | 2 | 3-4 | Design thinking, innovation | 60-90s |
| **Delphi Method** | 3+ | 4-5 | Expert consensus, forecasting | 90-180s |

### Choosing the Right Approach

**Use Lean Coffee when**:
- Time is limited
- Decision is relatively straightforward
- Need quick team alignment
- Action-oriented output required

**Use Double Diamond when**:
- Problem space needs exploration
- Multiple solution paths exist
- Innovation and creativity needed
- Design thinking approach fits

**Use Delphi Method when**:
- Expert judgment is critical
- High-stakes decision
- Need consensus from diverse experts
- Multiple iterations beneficial

**Hybrid Approach** (Recommended):
- Start with Double Diamond (explore problem)
- Use Delphi rounds (refine solutions)
- End with Lean Coffee (action items)

Example:
```javascript
const session = await callTool("start_committee_session", {
  topic: "Should we migrate to microservices?",
  participants: [
    {role: "architect", provider: "openai", model: "gpt-4"},
    {role: "devops", provider: "anthropic", model: "claude-3-sonnet"},
    {role: "security", provider: "gemini", model: "gemini-pro"}
  ],
  debate_rounds: 2,  // Double Diamond: Discover/Define → Develop/Deliver
  event_config: {
    default_level: "progress"
  }
});
```

## Performance

- **Session Duration**: 30-60 seconds per round
- **Concurrent Sessions**: 100+ supported
- **Cost Savings**: 50-90% with prompt caching
- **Event Latency**: < 100ms for SSE events
- **Throughput**: 10+ sessions per minute

## Configuration

### Environment Variables

```bash
# Required: LLM Provider API Keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GEMINI_API_KEY=...

# Optional: Server Configuration
PORT=8000
LOG_LEVEL=info

# Optional: Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60s
```

### Server Startup

```bash
# Start MCP server
go run cmd/server/main.go

# Or use Docker
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=$OPENAI_API_KEY \
  -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY \
  -e GEMINI_API_KEY=$GEMINI_API_KEY \
  llm-committee-agent
```

## Supported Models

### OpenAI
- `gpt-4` - Most capable, best for complex reasoning
- `gpt-4-turbo` - Faster, cost-effective
- `gpt-3.5-turbo` - Fast, economical

### Anthropic
- `claude-3-opus` - Most capable, best for nuanced analysis
- `claude-3-sonnet` - Balanced performance and cost
- `claude-3-haiku` - Fast, economical

### Google
- `gemini-pro` - Balanced performance
- `gemini-1.5-pro` - Enhanced capabilities, larger context

## Error Codes

| Code | Description | Solution |
|------|-------------|----------|
| `SESSION_NOT_FOUND` | Invalid session ID | Check session_id value |
| `INVALID_PARAMETERS` | Missing/invalid params | Verify required parameters |
| `PROVIDER_ERROR` | LLM API error | Check API keys and quotas |
| `RATE_LIMIT_EXCEEDED` | Too many requests | Wait and retry |

## Related Documentation

- [examples/](examples/) - Client examples

## Support

- **Repository**: https://[YOUR_REPO_URL]
- **MCP Specification**: https://modelcontextprotocol.io/
- **Issues**: Use GitLab issue tracker

---

**Version**: 1.5.0-dev  
**Last Updated**: 2026-02-25  
**License**: MIT

# Committee Decision Making Skill

Quick start guide for using this skill.

## Quick Copy

```bash
# Copy this entire folder to your skills directory
cp -r .kiro/skills/committee-decision-making ~/.config/opencode/skills/

# The skill will be automatically discovered by coordinator agents
```

## What's Included

```
committee-decision-making/
├── SKILL.md                    # Main skill definition (auto-generated metadata)
├── README.md                   # This file
├── metadata.json               # Machine-readable metadata (auto-generated)
├── references/                 # Additional knowledge for agents
│   ├── api-reference.md        # Complete API documentation
│   ├── best-practices.md       # Usage recommendations
│   ├── troubleshooting.md      # Common issues and solutions
│   └── performance.md          # Performance metrics and optimization
└── examples/                   # Ready-to-use code samples
    ├── javascript/
    ├── python/
    └── shell/
```

## Auto-Generated Content

The following files are automatically generated from the codebase:

- **metadata.json** - Extracted from code (MCP tools, providers, models)
- **SKILL.md frontmatter** - Updated with generation timestamp and version

To regenerate:
```bash
make generate-skill
```

This ensures the skill definition always reflects the current codebase.

## For Coordinator Agents

When a coordinator agent loads this skill, it will:

1. **Read SKILL.md** - Understand capabilities and usage
2. **Access references/** - Get detailed knowledge as needed
3. **Use examples/** - Reference working code samples

The `references` field in SKILL.md frontmatter tells the agent where to find additional context.

## For Humans

### Quick Start

1. **Read SKILL.md** - Understand what this skill does
2. **Check examples/** - See working code
3. **Read references/best-practices.md** - Learn optimal usage

### Documentation

- **SKILL.md** - Skill definition and overview
- **references/api-reference.md** - Complete API reference
- **references/best-practices.md** - Usage patterns and tips
- **references/troubleshooting.md** - Common issues
- **references/performance.md** - Performance metrics

### Examples

See `examples/` directory for ready-to-use code in:
- JavaScript (Node.js)
- Python
- Shell scripts

## Usage

### Via MCP Client

```javascript
import { Client } from "@modelcontextprotocol/sdk/client/index.js";

const client = new Client({...});
await client.connect(...);

const result = await client.callTool({
  name: "start_committee_session",
  arguments: {
    topic: "Should we adopt microservices?",
    participants: [...]
  }
});
```

### Via CLI

```bash
committee-discuss \
  --topic "Should we adopt microservices?" \
  --participants "architect:openai:gpt-4,devops:anthropic:claude-3-sonnet"
```

## Requirements

- MCP server running at `http://localhost:8000/mcp`
- LLM API keys (OpenAI, Anthropic, or Google)
- Network connection

## Support

- **Repository**: https://[YOUR_REPO_URL]
- **Documentation**: See `references/` directory
- **Issues**: Use GitLab issue tracker

## License

MIT

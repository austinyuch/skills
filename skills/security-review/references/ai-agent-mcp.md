# AI agent and MCP lane

Use this lane when code touches LLM prompts, tool invocation, retrieval, memory, agent orchestration, MCP servers, or autonomous actions.

## Main question

What untrusted content can influence a privileged tool or decision?

## Prompt and retrieval checks

- Treat user text, retrieved documents, issue comments, emails, and web content as untrusted.
- Look for instruction-following across trust boundaries: “ignore previous rules”, “call this tool”, “exfiltrate secrets”.
- Keep system policy, tool policy, and user content distinct.
- Strip or downgrade unsafe markup when feeding tools or chain-of-thought-like scaffolds.

## Tool and capability checks

- Narrow tool schemas; avoid free-form shell or broad file writes unless essential.
- Require explicit confirmation or policy gates for destructive actions.
- Do not let the model choose identities, tenants, or secret names from raw text alone.
- Constrain file paths, URL domains, and side-effect scope.

## MCP-specific checks

- Tool descriptions should make safe usage obvious and risky usage hard.
- Server should validate inputs, not trust client schemas alone.
- Bound open-world operations such as filesystem, HTTP, database, and git mutation.
- Ensure auth context from the caller cannot be silently widened inside the server.

## Output handling checks

- Never directly execute generated code or commands without validation.
- Sanitize model output before rendering as HTML or rich markdown.
- Record which tool calls were made and with what principal.

## Memory and data retention checks

- Keep secrets and access tokens out of long-lived memory stores.
- Separate user memory, org memory, and system memory.
- Define retention and deletion behavior for sensitive traces.

## Common failure patterns

- retrieved README text steering deployment or deletion steps
- tool accepts arbitrary path or URL because “the model will use it correctly”
- MCP server trusts upstream auth but never checks resource-level authorization
- background agent replays stale tokens or cached secrets

# Python lane

Use this lane for Python APIs, workers, automation scripts, AI services, and MCP servers.

## Focus areas

- Pydantic or equivalent validation at the boundary.
- Deserialization: avoid unsafe YAML, pickle, or dynamic import paths.
- Requests/httpx clients need timeouts and SSRF-conscious URL handling.
- Async task queues must re-check identity and tenant context.

## Review checks

- subprocess use has fixed argv and no shell unless tightly justified
- Jinja templates use autoescape for HTML contexts
- secrets do not leak through exception traces or debug config dumps
- ORM filters and row ownership are applied in reusable query helpers, not ad hoc

## Common failure patterns

- `yaml.load` with unsafe loader
- `pickle` or job payloads trusted from queues
- FastAPI dependency provides user context, but deeper service code skips object-level authorization

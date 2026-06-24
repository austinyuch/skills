# .NET / C# lane

Use this lane for ASP.NET Core APIs, background services, worker queues, and desktop/service integrations.

## Focus areas

- middleware order in ASP.NET Core: auth, routing, CORS, antiforgery, endpoints
- model binding and validation for DTOs
- claims-based authorization plus resource-level checks
- data protection keys, cookie settings, and token handling

## Review checks

- `[Authorize]` is not the only check; verify object-level authorization inside handlers
- antiforgery applied where cookie-authenticated state changes exist
- EF Core queries include tenant boundaries and avoid string-built SQL
- logging filters exclude secrets, tokens, and raw request bodies for sensitive paths

## Common failure patterns

- middleware order leaves endpoint exposed before auth
- background hosted service reuses elevated service principal for user-derived work
- data protection keys ephemeral in production, breaking session integrity assumptions

# JavaScript / TypeScript lane

Use this lane for Node.js, browser code, React, Next.js, and TypeScript services.

## Focus areas

- Split server-only and client-exposed code clearly.
- Validate untrusted input with schemas near the server boundary.
- Prefer `HttpOnly` cookies over browser storage for sensitive sessions.
- Guard SSR/edge handlers against implicit trust of headers and query params.

## Review checks

- no secrets or server tokens imported into client bundles
- `dangerouslySetInnerHTML` only with sanitization and a tight allowlist
- dynamic `eval`, `Function`, or broad template interpolation justified or removed
- outbound fetches use allowlists or safe resolvers when URLs are user-controlled
- background job or webhook code re-checks authorization, not just the UI flow

## Common failure patterns

- client component reads privileged env vars because of incorrect bundling assumptions
- Next.js route handler trusts middleware-added headers without signature or server derivation
- unsafe markdown or HTML rendering in admin panels
- package scripts or build steps execute unreviewed downloaded code

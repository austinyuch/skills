# Vercel / Next.js overlay

Use this overlay for Next.js apps running on Vercel or similar edge/serverless platforms.

## Checks

- confirm which code runs in browser, edge, or server runtime
- secrets remain server-side and are not exposed via `NEXT_PUBLIC_` or client imports
- route handlers and server actions enforce auth and object-level authorization
- preview deployments do not receive production-grade secrets by default
- CSP, headers, and cache behavior reviewed for personalized responses

## Common failure patterns

- relying on middleware-only auth while server actions or route handlers skip resource checks
- preview environment accidentally talking to production data
- cached response missing user or tenant variance

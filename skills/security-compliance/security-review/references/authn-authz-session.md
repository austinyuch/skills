# Authentication, authorization, and session lane

Use this lane for login, signup, password reset, SSO, session middleware, service identity, role checks, tenancy, impersonation, and admin actions.

## Review order

1. Identity proofing
2. Session issuance and rotation
3. Authorization decisions at the resource boundary
4. Tenant isolation and impersonation controls
5. Auditability and revocation

## Authentication checks

- Verify the real identity source: password, OAuth/OIDC, SAML, passkey, magic link, service role.
- Ensure step-up auth exists for destructive or payout-like actions.
- Check rate limiting, lockout/backoff, and enumeration resistance.
- Confirm reset flows expire quickly and invalidate older sessions.

## Session checks

- Prefer server-managed sessions or `HttpOnly`, `Secure`, `SameSite` cookies.
- Rotate session identifiers after login, privilege change, or reset.
- Enforce absolute TTL plus inactivity timeout for sensitive apps.
- Bind CSRF defense to state-changing requests.
- Ensure logout revokes server-side state, not just client storage.

## Token checks

- Minimize JWT claims; avoid turning tokens into stale authorization databases.
- Validate issuer, audience, expiry, not-before, and signing algorithm.
- Reject algorithm confusion and unsigned-token fallbacks.
- Short TTL for access tokens; refresh tokens stored and rotated safely.
- Treat service tokens separately from user sessions.

## Authorization checks

- Check authorization where the resource is loaded, not only at the route edge.
- Prefer deny-by-default role and permission models.
- Verify object-level authorization: record owner, tenant, policy, organization scope.
- Look for missing checks in batch endpoints, exports, background jobs, and admin tools.
- Confirm “read” paths are as strict as “write” paths for sensitive data.

## Multi-tenant and impersonation checks

- Tenant id must come from trusted context, not solely from request body or query params.
- Ensure admin impersonation is explicit, logged, time-bounded, and visually surfaced.
- Prevent cross-tenant caching or background-job fanout.

## Evidence to request

- middleware or policy code path
- tests for unauthorized access, cross-tenant access, and stale session rejection
- token/cookie config
- audit log examples for login, privilege changes, and impersonation

## Common failure patterns

- role check at page load but not in API handler
- client-side role gating treated as authorization
- refresh token reuse without detection
- password reset not invalidating extant sessions
- long-lived service tokens committed to CI or local env files

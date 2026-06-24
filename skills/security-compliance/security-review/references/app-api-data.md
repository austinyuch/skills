# App, API, and data lane

Use this lane for handlers, forms, uploads, background jobs, queries, caches, logs, and data movement.

## Inputs and parsing

- Validate at the first trusted boundary with allowlists and size limits.
- Parse once; pass typed data inward.
- Reject unknown fields when privilege or billing is involved.
- Watch for Unicode normalization, path traversal, and archive extraction issues.

## APIs and web boundaries

- Check auth before expensive work and before data fetches that reveal existence.
- Enforce pagination, rate limits, and body size limits.
- For webhooks, verify signature, timestamp, and replay protection before parsing payload.
- Review CORS narrowly; avoid wildcard credentials.

## Outbound calls

- Review SSRF controls: allowlists, resolved-IP validation, block metadata services, block link-local.
- Separate fetchers for public URLs versus trusted service URLs.
- Confirm timeouts, retries, and circuit breakers do not amplify abuse.

## Data access

- Parameterize queries; no raw string concatenation.
- Verify tenant filters and row policies on read and write paths.
- Review bulk operations, CSV export, and admin reports for over-broad scopes.
- Mask or avoid sensitive fields in logs and traces.

## Files and object storage

- Validate extension, media type, size, and content where practical.
- Store outside executable paths.
- Prefer generated filenames and scoped download URLs.
- Scan or quarantine high-risk uploads when business risk justifies it.

## Background jobs, queues, and events

- Re-check authorization when jobs consume user-originated work later.
- Ensure messages carry trusted identity and tenant context.
- Prevent poison-message loops and duplicate side effects.

## Privacy and observability

- Keep secrets, tokens, and high-risk PII out of logs.
- Use structured logs with redaction.
- Audit exports, admin reads, and policy changes.

## Common failure patterns

- schema validation only on frontend
- hidden form fields trusted for role or price
- webhook endpoint accepting unsigned JSON
- cache key missing tenant or role dimension
- export endpoint bypassing row-level filters

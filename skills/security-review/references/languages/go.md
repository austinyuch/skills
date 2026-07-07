# Go lane

Use this lane for Go services, CLIs, workers, and MCP servers.

## Focus areas

- `http.Handler` chains: auth middleware must protect every route variant.
- `context.Context`: propagate deadlines and auth context deliberately; do not smuggle optional security state.
- JSON decoding: reject unknown fields for sensitive payloads.
- Templates: use `html/template` for HTML, not `text/template`.
- File paths and archives: clean paths and prevent Zip Slip.

## Review checks

- `sql` calls parameterized; ORM scopes include tenant filters.
- `http.Client` has timeout and restricted transports when fetching untrusted URLs.
- `exec.Command` inputs are fixed or strongly validated.
- goroutines handling security events do not drop errors silently.
- secrets are not logged through `%+v` dumps of config structs.

## Common failure patterns

- missing `DisallowUnknownFields()` on admin or billing endpoints
- shared package-level `http.Client` without sane timeout or transport policy
- race between auth check and async privileged work

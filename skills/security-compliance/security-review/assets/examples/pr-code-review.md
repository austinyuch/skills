# Worked example: PR security review

## Change summary

PR adds a Next.js route handler that accepts CSV uploads, stores rows in Postgres, and lets admins trigger an LLM-based classification job.

## Lane selection

- `references/review-workflow.md`
- `references/app-api-data.md`
- `references/ai-agent-mcp.md`
- `references/authn-authz-session.md`
- `references/languages/javascript-typescript.md`
- `references/platforms/vercel-nextjs.md`
- `references/platforms/supabase.md`
- `references/zero-day-resilience.md`

## Example review output

### Reviewed surface

`app/api/import/route.ts`, upload parsing, admin authorization, job enqueue path, and the LLM classification worker.

### Confirmed issues

1. **Object-level authorization missing on import target.** The route checks `isAdmin` but trusts `organizationId` from the request body before inserting rows. A cross-org admin or compromised admin session could write into another tenant.
2. **Service-role overreach in worker.** The classifier uses a Supabase service-role key and fetches records by caller-supplied ids without re-checking tenant ownership.

### Risks to verify before merge

1. Upload parser enforces extension and size, but the PR does not show row-count limits or CSV formula neutralization for later export.
2. The classification prompt includes raw uploaded text. Confirm the tool path cannot escalate into arbitrary outbound fetches or secret lookup.

### Remediation

- Derive tenant/org id from the authenticated admin context server-side.
- In worker code, load candidate rows through a tenant-scoped query helper, not direct service-role fetch by arbitrary ids.
- Cap CSV row count and sanitize spreadsheet-triggering prefixes (`=`, `+`, `-`, `@`) if exports exist downstream.
- Add a tool policy boundary around the classifier so hostile content cannot trigger side-effect tools.

### Evidence checked

- route handler auth branch
- database insert path
- worker fetch path
- absence of tenant-scoped tests for cross-org ids

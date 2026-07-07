# Supabase overlay

Use this overlay for Supabase Auth, Postgres, RLS, storage, Edge Functions, and service-role usage.

## Checks

- RLS enabled on every exposed table and storage bucket policy reviewed
- policies enforce tenant and ownership on `SELECT`, `INSERT`, `UPDATE`, and `DELETE`
- service-role key kept strictly server-side and isolated from user-request paths unless necessary
- auth hooks and edge functions verify caller context before privileged access
- storage signed URLs are scoped and expire quickly

## Common failure patterns

- table has RLS but one operation type lacks policy
- service-role key used in route handler that processes user-controlled ids
- client code assumes RLS covers backend paths that actually bypass it with service credentials

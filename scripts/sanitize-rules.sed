# Leak-hygiene redaction rules applied to every synced skill (post-rsync).
#
# Upstream (~/.config/opencode/skills) is the live working copy and is NOT sanitized;
# this open-source repo keeps extra hygiene. These rules redact machine-specific
# identifiers so a raw upstream sync cannot reintroduce them. Each rule is idempotent
# and reproduces the repo's hand-sanitized form exactly, so re-running the sync leaves
# already-clean files Unchanged.
#
# Add new rules here as further real identifiers are discovered; keep them specific
# (target known real usernames / project ids), never blanket-rewrite generic
# placeholders like /home/user/, /home/ci/, or ~/.

# Real GCP service-account credential file path -> placeholder
s#/home/ga6653/\.config/gcloud/gcputil-[0-9a-f]\{12\}\.json#/home/user/.config/gcloud/<service-account>.json#g

# Real GCP project id -> placeholder
s#VERTEX_PROJECT_ID=gcputil#VERTEX_PROJECT_ID=<gcp-project-id>#g

# Real machine .kiro skills path -> home-relative
s#/home/ac/\.kiro/#~/.kiro/#g

# Real machine project path -> generic user placeholder
s#/home/ac/projects/#/home/user/projects/#g
s#/home/ga6653/projects/#/home/user/projects/#g

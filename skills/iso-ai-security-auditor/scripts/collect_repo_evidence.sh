#!/usr/bin/env bash
set -euo pipefail

target="${1:-.}"
out="${2:-./iso-ai-security-audit-evidence}"

mkdir -p "$out"

if ! command -v rg >/dev/null 2>&1; then
  echo "ripgrep (rg) is required" >&2
  exit 2
fi

{
  echo "# Repository Evidence Collection"
  echo
  echo "- Target: $target"
  echo "- Output: $out"
  echo "- Generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
} > "$out/README.md"

find "$target" -maxdepth 3 -type f \
  \( -iname "README*" -o -iname "SECURITY.md" -o -iname "AGENTS.md" -o -iname "Dockerfile" -o -iname "docker-compose*" -o -iname "*.yml" -o -iname "*.yaml" -o -iname "*.tf" -o -iname "*.md" \) \
  | sort > "$out/high_value_files.txt"

rg -n --hidden --glob '!node_modules' --glob '!.git' \
  "auth|authorization|RBAC|MFA|session|cookie|csrf|cors|rate.?limit|audit.?log|trace.?id|secret|vault|kms|encrypt|token|jwt|oauth|saml|oidc" \
  "$target" > "$out/security_auth_access.txt" || true

rg -n --hidden --glob '!node_modules' --glob '!.git' \
  "threat.?model|risk|incident|postmortem|vulnerability|dependency|SBOM|SAST|secret.?scan|signing|provenance|backup|restore|BCP|DR" \
  "$target" > "$out/security_operations.txt" || true

rg -n --hidden --glob '!node_modules' --glob '!.git' \
  "AI|LLM|model|prompt|embedding|RAG|MCP|tool.?call|guardrail|eval|dataset|data.?card|model.?card|provenance|drift|human.?oversight|impact.?assessment" \
  "$target" > "$out/ai_governance.txt" || true

rg -n --hidden --glob '!node_modules' --glob '!.git' \
  "prompt.?injection|data.?poison|model.?theft|model.?inversion|hallucination|PII|privacy|consent|retention" \
  "$target" > "$out/ai_security_privacy.txt" || true

rg -n --hidden --glob '!node_modules' --glob '!.git' \
  "log|logger|logging|audit.?event|audit.?trail|trace.?id|span.?id|OpenTelemetry|otel|SIEM|CloudTrail|retention|redact|mask|sanitize|scrub|request.?body|response.?body|prompt|completion|tool.?call|PII|personal.?data|secret|token|password" \
  "$target" > "$out/log_governance.txt" || true

rg -n --hidden --glob '!node_modules' --glob '!.git' \
  "PDPA|GDPR|ePrivacy|cookie|CCPA|CPRA|Colorado|EU AI Act|NIS2|Cyber Resilience Act|CRA|Digital Services Act|DSA|Data Act|DORA|HIPAA|GLBA|COPPA|FERPA|FCRA|PCI|SEC|SOX|PIPL|Data Security Law|Cybersecurity Law" \
  "$target" > "$out/legal_regulatory_triggers.txt" || true

rg -n --hidden --glob '!node_modules' --glob '!.git' \
  "Okta|Auth0|Azure AD|Entra|Cognito|CloudTrail|Security Hub|GuardDuty|SIEM|SOC|Snyk|Dependabot|Wiz|Vault|KMS|Datadog|Sentry|OpenTelemetry|DPA|SOC 2|ISO 27001" \
  "$target" > "$out/external_controls.txt" || true

echo "Evidence collection complete: $out"

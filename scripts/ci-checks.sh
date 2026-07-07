#!/usr/bin/env bash
# Tree-level repo checks — run in CI and locally before a PR:
#   bash scripts/ci-checks.sh
# Mirrors the git hooks but operates on the whole working tree (CI has nothing
# staged). Exits non-zero if any check fails.
set -uo pipefail
cd "$(git rev-parse --show-toplevel)" || exit 1

FAIL=0
ok()  { echo "  ✅ $1"; }
bad() { echo "  ❌ $1"; FAIL=1; }

echo "== aclab/skills CI checks =="

# 1. manifest <-> filesystem consistency
echo "[1] manifest <-> filesystem"
python3 - <<'PY' || FAIL=1
import json, glob, os, sys
m = json.load(open("skills-manifest.json"))
listed = set(m.get("skills", []))  # flat single-level layout
allow = set()  # standalone reference files ship via standalone_files, not as skills
disk = {os.path.basename(os.path.dirname(p)) for p in glob.glob("skills/*/SKILL.md")}
missing = sorted(s for s in listed if s not in disk and s not in allow)
orphan  = sorted(s for s in disk if s not in listed)
bad = False
if missing: print("  ❌ manifest lists missing skill(s):", missing); bad = True
if orphan:  print("  ❌ on-disk skill(s) not in manifest:", orphan); bad = True
if not bad: print("  ✅ %d skills, no orphans/missing" % len(disk))
sys.exit(1 if bad else 0)
PY

# 2. markdown -> HTML twin freshness — re-render and see if anything CHANGES
#    (independent of git state, so it's correct in CI and when run locally).
echo "[2] doc twin freshness"
TWINS="README.html README.zh-TW.html AGENTS.html CREDITS.html docs/README.html \
docs/agentic-delivery-methodology.html docs/methodology-diagram.html \
skills/spec-master/README.html skills/code-review/README.html"
BEFORE="$(md5sum $TWINS 2>/dev/null)"
python3 scripts/render-docs.py >/dev/null 2>&1 || true
AFTER="$(md5sum $TWINS 2>/dev/null)"
if [ "$BEFORE" = "$AFTER" ]; then
  ok "twins fresh"
else
  bad "twins stale vs their markdown source — run: python3 scripts/render-docs.py && git add -A"
fi

# 3. bilingual HTML balance (hand-built landing pages)
echo "[3] bilingual HTML balance"
python3 - <<'PY' || FAIL=1
import re, sys
pages = ["methodology.html", "skills/spec-master/index.html", "skills/code-review/index.html"]
bad = False
for p in pages:
    h = open(p, encoding="utf-8").read()
    en = len(re.findall(r"\bdata-en\b", h)); zh = len(re.findall(r"\bdata-zh\b", h))
    miss = len([t for t in re.findall(r"<[^>]*\bdata-en\b[^>]*>", h) if "data-zh" not in t])
    if en != zh or miss:
        print(f"  ❌ {p}: en={en} zh={zh} missing_zh={miss}"); bad = True
if not bad: print("  ✅ all landing pages balanced")
sys.exit(1 if bad else 0)
PY

# 4. no machine-specific absolute paths under skills/** (evals/fixtures excluded)
echo "[4] machine-path scan"
HITS="$(grep -rInE '/home/[a-z_][a-z0-9_-]*/' skills 2>/dev/null \
        | grep -vE '/(evals|fixtures|__fixtures__|testdata|test-fixtures)/' \
        | grep -vE '/home/<[^>]+>' \
        | grep -vE '/home/(user|users|agent|ci|me|you|username|youruser|example|test)/' || true)"
if [ -n "$HITS" ]; then bad "machine-specific /home/<user>/ path under skills/**"; printf '%s\n' "$HITS" | head -5 | sed 's/^/      /'
else ok "no machine paths"; fi

# 5. relative-link check across key docs/HTML
echo "[5] relative-link check"
python3 - <<'PY' || FAIL=1
import os, re, sys, glob
docs = ["README.md","README.zh-TW.md","AGENTS.md","CREDITS.md","docs/README.md",
        "methodology.html","skills/spec-master/index.html","skills/code-review/index.html",
        "skills/spec-master/README.md","skills/code-review/README.md"]
bad = False
for d in docs:
    if not os.path.exists(d): continue
    base = os.path.dirname(d); t = open(d, encoding="utf-8").read()
    links = re.findall(r'href="([^"]+)"', t) + re.findall(r'\]\(([^)]+)\)', t)
    for l in links:
        if re.match(r'^(https?:|#|mailto:)', l): continue
        p = l.split('#')[0]
        if not p: continue
        if not (os.path.exists(os.path.join(base, p)) or os.path.exists(p)):
            print(f"  ❌ {d} -> {l}"); bad = True
if not bad: print("  ✅ all relative links resolve")
sys.exit(1 if bad else 0)
PY

# 6. installer smoke (syntax + dry-run)
echo "[6] installer smoke"
node --check bin/aclab-skills.mjs 2>/dev/null && python3 -m py_compile bin/aclab_skills.py 2>/dev/null \
  && bash -n scripts/install.sh && bash -n scripts/install-git-hooks.sh \
  && bash -n scripts/git-hooks/pre-commit && bash -n scripts/git-hooks/pre-push \
  && ok "scripts parse" || bad "a script failed to parse"
T="$(mktemp -d)"
node bin/aclab-skills.mjs claude --target "$T/n" --dry-run >/dev/null 2>&1 && ok "node CLI dry-run" || bad "node CLI dry-run failed"
python3 bin/aclab_skills.py claude --target "$T/p" --dry-run >/dev/null 2>&1 && ok "python CLI dry-run" || bad "python CLI dry-run failed"
if command -v pwsh >/dev/null; then
  pwsh -NoProfile -Command "[void][System.Management.Automation.Language.Parser]::ParseFile('scripts/install.ps1',[ref]\$null,[ref]\$null)" >/dev/null 2>&1 \
    && ok "ps1 parses" || bad "ps1 parse failed"
else echo "  ·· pwsh not present — skipping ps1 parse"; fi
rm -rf "$T"

# 7. basic secret scan (tree, evals excluded)
echo "[7] secret scan"
SEC="$(grep -rInE 'AKIA[0-9A-Z]{16}|gh[pousr]_[A-Za-z0-9]{20,}|xox[baprs]-[A-Za-z0-9-]{10,}|-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----' \
        --include='*' skills bin scripts docs *.md *.json 2>/dev/null \
        | grep -vE '/(evals|fixtures|testdata)/' \
        | grep -vE '/(test_[^/:]*|[^/:]*_test|[^/:]*\.test)\.[A-Za-z]+:' \
        | grep -v 'AKIAIOSFODNN7EXAMPLE' || true)"
if [ -n "$SEC" ]; then bad "possible secret material"; printf '%s\n' "$SEC" | head -5 | sed 's/^/      /'
else ok "no high-entropy secrets"; fi

echo "============================="
if [ "$FAIL" -eq 0 ]; then echo "✅ CI checks passed"; else echo "❌ CI checks FAILED"; fi
exit "$FAIL"

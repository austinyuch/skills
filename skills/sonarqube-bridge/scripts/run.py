#!/usr/bin/env python3
"""sonarqube-bridge — ingest SonarQube findings and fuse them with the code graph (hybrid).

SonarQube is the department's authoritative static-scan / SAST and quality-gate tool. This
bridge does NOT scan — it *consumes* SonarQube findings (from the live Web API or an offline
export), normalizes them into the shared review-finding schema, and enriches each with graph
blast-radius, business capability, and the project's remediation vocabulary (a Fowler move +
test safety-net for smells; an OWASP pointer for vulnerabilities; a regression test for bugs).
The result is one ranked, context-rich report the code-review skill folds in next to the
heuristic helper skills (test-quality-reviewer, code-refactoring-advisor, security-risk-reviewer).

  invocation : python3 run.py '<json>'        (also accepts the JSON on stdin)
  input JSON : {"source":"file","issues_file":"sonar-issues.json","impact_map":{...},"capability_map":{...}}
               or {"source":"api","host":"https://sonar","project_key":"p","token_env":"SONAR_TOKEN"}
  output JSON: {"skill_version","project","source","explained","summary","risk_ranking","findings":[...]}

The deterministic normalize+enrich pass is the source of truth and runs offline with no
provider. Exit non-zero only on bad input / unreadable file / unconfigured API, or when
--explain was forced but the provider failed; never fabricates.
"""

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from llm_provider import ProviderError, explain, parse_json_block  # noqa: E402

SKILL_VERSION = "sonarqube-bridge/1.0"

SEV_MAP = {"BLOCKER": "high", "CRITICAL": "high", "MAJOR": "medium", "MINOR": "low", "INFO": "low"}
SEV_WEIGHT = {"high": 3, "medium": 2, "low": 1}
TYPE_FACTOR = {"VULNERABILITY": 1.5, "BUG": 1.5, "SECURITY_HOTSPOT": 1.2, "CODE_SMELL": 1.0}

# A small embedded sample for offline/mock mode (clearly labelled, never mistaken for a real scan).
MOCK_ISSUES = [
    {"key": "MOCK1", "rule": "go:S2076", "severity": "CRITICAL", "type": "VULNERABILITY",
     "component": "proj:internal/api/handler.go", "line": 42,
     "message": "Make sure running this OS command is safe.", "tags": ["cwe-78", "owasp-a3"]},
    {"key": "MOCK2", "rule": "csharpsquid:S3776", "severity": "MAJOR", "type": "CODE_SMELL",
     "component": "proj:src/Pricing.cs", "line": 10,
     "message": "Refactor this method to reduce its Cognitive Complexity.", "tags": ["brain-overload"]},
]


def fail(msg, code=2):
    print(f"sonarqube-bridge: {msg}", file=sys.stderr)
    sys.exit(code)


def read_input(argv):
    args = [a for a in argv[1:] if a not in ("--mock", "--explain")]
    raw = args[0] if args else (sys.stdin.read() if not sys.stdin.isatty() else None)
    if not raw:
        fail("no input JSON provided (argv[1] or stdin)")
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        fail(f"invalid input JSON: {e}")
    if not isinstance(data, dict):
        fail("input JSON must be an object")
    return data


# ---------------------------------------------------------------------- ingest (REQ-001)

def load_issues(cfg, mock):
    if mock:
        return list(MOCK_ISSUES), "mock"
    source = (cfg.get("source") or "file").lower()
    if source == "file":
        path = cfg.get("issues_file")
        if not path:
            fail("source 'file' requires 'issues_file'")
        try:
            with open(path, "r", encoding="utf-8") as fh:
                doc = json.load(fh)
        except (OSError, json.JSONDecodeError) as e:
            fail(f"cannot read issues_file {path!r}: {e}")
        return _issues_of(doc), "file"
    if source == "api":
        return _load_api(cfg), "api"
    fail(f"unsupported source {source!r} (expected 'file' or 'api')")


def _issues_of(doc):
    if isinstance(doc, list):
        return doc
    if isinstance(doc, dict) and isinstance(doc.get("issues"), list):
        return doc["issues"]
    fail("issues JSON must be a list or an object with an 'issues' array")


def _load_api(cfg):
    host = cfg.get("host")
    project = cfg.get("project_key")
    if not host:
        fail("source 'api' requires 'host' (e.g. https://sonarqube.example.com)")
    if not project:
        fail("source 'api' requires 'project_key'")
    token = os.environ.get(cfg.get("token_env") or "SONAR_TOKEN")
    if not token:
        fail(f"source 'api' requires a token in env ${cfg.get('token_env') or 'SONAR_TOKEN'}")
    url = (host.rstrip("/") + "/api/issues/search?componentKeys="
           + urllib.parse.quote(project) + "&resolved=false&ps=500")
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            doc = json.loads(r.read().decode("utf-8"))
    except (urllib.error.URLError, json.JSONDecodeError) as e:
        fail(f"SonarQube API request failed: {e}")
    return _issues_of(doc)


# --------------------------------------------------------------- normalize (REQ-002)

def map_severity(sonar_sev):
    return SEV_MAP.get(str(sonar_sev or "").upper(), "medium")


def normalize_issue(iss):
    comp = str(iss.get("component", ""))
    file = comp.split(":", 1)[1] if ":" in comp else comp
    tags = iss.get("tags") or []
    owasp = next((t for t in tags if str(t).lower().startswith("owasp")), "")
    cwe = next((t for t in tags if str(t).lower().startswith("cwe")), "")
    return {
        "source": "sonarqube", "rule": iss.get("rule", ""), "type": iss.get("type", "CODE_SMELL"),
        "severity": map_severity(iss.get("severity")), "file": file, "line": iss.get("line", 0),
        "message": iss.get("message", ""), "owasp": owasp, "cwe": cwe,
    }


# --------------------------------------------------------------- enrich (REQ-003/004)

def remediation_for(finding):
    typ = finding.get("type", "")
    msg = (finding.get("message", "") + " " + finding.get("rule", "")).lower()
    if typ in ("VULNERABILITY", "SECURITY_HOTSPOT"):
        owasp = (" (" + finding["owasp"] + ")") if finding.get("owasp") else ""
        return ("Security: validate/parameterize/encode per OWASP" + owasp
                + " — see the security-risk-reviewer skill's owasp-patterns reference. Add a test that "
                "reproduces the unsafe input.")
    if typ == "BUG":
        return "Fix the defect and add a regression test (write it red first, then make it pass)."
    # CODE_SMELL — map to a named refactoring move + the test safety-net it needs first.
    if any(k in msg for k in ("cognitive", "complex", "brain", "too long", "long method")):
        return ("Extract Function to reduce complexity; add a characterization test on current "
                "output first (see code-refactoring-advisor).")
    if "duplicat" in msg:
        return "Extract the shared code into one function called from all sites; cover both sites with a test."
    if "parameter" in msg:
        return "Introduce a Parameter Object; pin each call site with a test before changing the signature."
    return "Refactor per the smell; ensure a trustworthy test exists before changing structure."


def enrich(findings, impact_map, capability_map):
    impact_map = impact_map or {}
    capability_map = capability_map or {}
    for f in findings:
        blast = impact_map.get(f["file"], 1)
        try:
            blast = max(float(blast), 1.0)
        except (TypeError, ValueError):
            blast = 1.0
        f["blast_radius"] = blast
        f["capability"] = capability_map.get(f["file"], "")
        f["risk_score"] = round(SEV_WEIGHT[f["severity"]] * TYPE_FACTOR.get(f["type"], 1.0) * blast, 2)
        f["remediation"] = remediation_for(f)
    return findings


def rank(findings):
    order = sorted(findings, key=lambda f: (-f["risk_score"], str(f["file"]), f.get("line", 0)))
    return [{"file": f["file"], "line": f.get("line", 0), "rule": f["rule"], "type": f["type"],
             "severity": f["severity"], "risk_score": f["risk_score"], "capability": f.get("capability", "")}
            for f in order]


def summarize(findings):
    by_sev, by_type = {"high": 0, "medium": 0, "low": 0}, {}
    for f in findings:
        by_sev[f["severity"]] = by_sev.get(f["severity"], 0) + 1
        by_type[f["type"]] = by_type.get(f["type"], 0) + 1
    top = max((f["risk_score"] for f in findings), default=0)
    return {"total": len(findings), "by_severity": by_sev, "by_type": by_type, "max_risk_score": top}


def process(issues, impact_map=None, capability_map=None):
    """Pure pipeline used by both main() and the property tests."""
    findings = enrich([normalize_issue(i) for i in issues], impact_map, capability_map)
    return findings, rank(findings), summarize(findings)


# --------------------------------------------------------------- explain (opt-in, REQ-005)

def build_explain_prompt(findings):
    items = [{"rule": f["rule"], "type": f["type"], "file": f["file"], "line": f["line"],
              "message": f["message"]} for f in findings[:40]]
    return (
        "You are a senior reviewer. SonarQube messages are terse. For each finding, return a "
        "calibrated severity (high|medium|low) and one concrete, actionable remediation sentence in "
        'the developer\'s context. Return ONLY JSON: {"findings":[{"rule":str,"line":int,"severity":str,'
        '"remediation":str}]}.\n\n' + json.dumps(items)
    )


def apply_explanation(findings, text):
    obj = parse_json_block(text)
    by_key = {(str(f.get("rule")), int(f.get("line", -1))): f for f in obj.get("findings", []) if isinstance(f, dict)}
    for f in findings:
        upd = by_key.get((f["rule"], f.get("line", -1)))
        if upd:
            if upd.get("severity") in ("high", "medium", "low"):
                f["severity"] = upd["severity"]
            if upd.get("remediation"):
                f["remediation"] = str(upd["remediation"])
    return findings


def main():
    argv = sys.argv
    cfg = read_input(argv)
    mock = os.environ.get("SONARQUBE_BRIDGE_MOCK") == "1" or "--mock" in argv[1:]
    want_explain = "--explain" in argv[1:] or os.environ.get("SONARQUBE_BRIDGE_EXPLAIN") == "1"

    issues, source = load_issues(cfg, mock)
    findings, ranking, summary = process(issues, cfg.get("impact_map"), cfg.get("capability_map"))

    explained = False
    if findings and (want_explain or mock):
        if mock:
            for f in findings:
                f["remediation"] = "MOCK: " + f["remediation"]
            explained = True
        else:
            try:
                findings = apply_explanation(findings, explain(build_explain_prompt(findings)))
                ranking, summary = rank(findings), summarize(findings)
                explained = True
            except ProviderError as e:
                if want_explain and not mock:
                    fail(f"--explain requested but provider failed: {e}")

    print(json.dumps({
        "skill_version": SKILL_VERSION + ("-mock" if mock else ""),
        "project": cfg.get("project_key", "unknown"), "source": source, "explained": explained,
        "summary": summary, "risk_ranking": ranking, "findings": findings,
    }))


if __name__ == "__main__":
    main()

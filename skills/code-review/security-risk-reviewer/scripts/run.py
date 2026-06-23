#!/usr/bin/env python3
"""security-risk-reviewer — OWASP pattern scan + risk-based prioritization (hybrid skill).

Deterministic detectors (offline, source of truth) flag common OWASP Top-10 patterns in a
source file and rank them by risk so a reviewer knows what to look at FIRST. An OPTIONAL
--explain pass asks the LLM to judge exploitability (security regex is noisy — true vs false
positive) and tighten remediation. This is the concrete detector behind the code-review
skill's existing prose security guidance (Spec #42 REQ-CRQAQC-003).

  invocation : python3 run.py '<json>'        (also accepts the JSON on stdin)
  input JSON : {"file": "<path>"}  (optional {"content": "..."}; optional {"blast_radius": N})
  output JSON: {"skill_version","target","explained","summary","risk_ranking","findings":[...]}

Each finding carries `owasp`, `cwe`, `severity`, `risk_score`, `remediation`. Exit non-zero
only on bad input or a forced --explain provider failure; no findings is a valid PASS.
"""

import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from llm_provider import ProviderError, explain, parse_json_block  # noqa: E402

SKILL_VERSION = "security-risk-reviewer/1.0"
MAX_CONTENT_BYTES = 256 * 1024
SEV_WEIGHT = {"high": 3, "medium": 2, "low": 1}

# (rule, compiled regex, severity, owasp, cwe, confidence, remediation)
RULES = [
    ("HARDCODED_SECRET", re.compile(r"AKIA[0-9A-Z]{16}|gh[pousr]_[A-Za-z0-9]{20,}|xox[baprs]-[A-Za-z0-9-]{10,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
     "high", "A07:2021 Identification & Auth", "CWE-798", 0.9,
     "Move the secret to a secret manager / env var; rotate the exposed credential immediately."),
    ("HARDCODED_SECRET", re.compile(r"""(?i)(password|passwd|secret|api[_-]?key|access[_-]?token|private[_-]?key)\s*[:=]\s*['"][^'"\s]{6,}['"]"""),
     "high", "A07:2021 Identification & Auth", "CWE-798", 0.55,
     "Do not embed credentials in source; load from env/secret store. (Verify it is not a placeholder/test value.)"),
    ("SQL_INJECTION", re.compile(r"""(?i)(select|insert|update|delete|where|from)\b[^;\n]*?(['"]\s*\+|\+\s*['"]|\.format\(|%\s*\(|f['"])"""),
     "high", "A03:2021 Injection", "CWE-89", 0.55,
     "Use parameterized queries / prepared statements; never build SQL by string concatenation or interpolation."),
    ("COMMAND_INJECTION", re.compile(r"os\.system\(|subprocess\.[A-Za-z_]+\([^)]*shell\s*=\s*True|\bexec\.Command\(\s*['\"](?:sh|bash|cmd)['\"]\s*,\s*['\"]-c['\"]|child_process\.(?:exec|execSync)\(|\bProcess\.Start\(|new\s+ProcessStartInfo|Runtime\.getRuntime\(\)\.exec"),
     "high", "A03:2021 Injection", "CWE-78", 0.6,
     "Avoid the shell; pass argv arrays, validate/allow-list inputs, never concatenate user data into a command."),
    ("INSECURE_DESERIALIZE", re.compile(r"pickle\.loads?\(|yaml\.load\((?![^)]*Safe)|cPickle\.|marshal\.loads\(|\bBinaryFormatter\b|TypeNameHandling\.(?:All|Auto)|new\s+JavaScriptSerializer|node-serialize"),
     "high", "A08:2021 Data Integrity", "CWE-502", 0.7,
     "Use a safe loader (yaml.safe_load) / a non-executable format (JSON); never deserialize untrusted data. In .NET avoid BinaryFormatter and TypeNameHandling.All."),
    ("DISABLED_TLS_VERIFY", re.compile(r"(?i)verify\s*=\s*False|InsecureSkipVerify\s*:\s*true|rejectUnauthorized\s*:\s*false|CURLOPT_SSL_VERIFYPEER\s*,\s*0|ServerCertificate\w*ValidationCallback\s*\+?=|RemoteCertificateValidationCallback\s*\+?="),
     "high", "A05:2021 Security Misconfiguration", "CWE-295", 0.75,
     "Enable certificate verification; pin/trust a proper CA instead of disabling TLS validation."),
    ("SSRF", re.compile(r"(?:requests\.(?:get|post|put|patch|delete|head)|urllib\.request\.urlopen|httpx\.(?:get|post)|http\.Get|axios\.(?:get|post)|fetch|WebRequest\.Create|\.GetAsync|\.DownloadString)\(\s*(?:url|uri|endpoint|target|link|address)\b"),
     "medium", "A10:2021 Server-Side Request Forgery", "CWE-918", 0.4,
     "Allow-list permitted hosts/schemes and block internal/metadata addresses; never fetch a user-supplied URL directly."),
    ("XSS", re.compile(r"dangerouslySetInnerHTML|\.innerHTML\s*=|document\.write\(|v-html|render_template_string\(|\|\s*safe\b|Html\.Raw\(|@Html\.Raw"),
     "medium", "A03:2021 Injection (XSS)", "CWE-79", 0.55,
     "Escape/encode output; prefer textContent / auto-escaping templates; sanitize any HTML you must render."),
    ("WEAK_CRYPTO", re.compile(r"(?i)\b(md5|sha1)\s*\(|hashlib\.(md5|sha1)\b|\bDES\b|MODE_ECB|Math\.random\(\)|MD5\.Create|SHA1\.Create|DESCryptoServiceProvider|crypto\.createHash\(\s*['\"](?:md5|sha1)['\"]"),
     "medium", "A02:2021 Cryptographic Failures", "CWE-327", 0.5,
     "Use SHA-256+/bcrypt/argon2 for the right purpose; use a CSPRNG (secrets/crypto.rand) for tokens."),
    ("PATH_TRAVERSAL", re.compile(r"(?i)(open|readfile|sendfile|os\.path\.join|filepath\.Join|File\.Open|File\.ReadAll\w*|Path\.Combine|fs\.readfile|fs\.createreadstream)\([^)]*(request|req\.|params|query|input|argv|user)"),
     "medium", "A01:2021 Broken Access Control", "CWE-22", 0.45,
     "Canonicalize and allow-list paths; reject '..'; resolve against a fixed base dir before opening."),
]


def fail(msg, code=2):
    print(f"security-risk-reviewer: {msg}", file=sys.stderr)
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
    if not isinstance(data, dict) or not data.get("file"):
        fail("input JSON must be an object with a non-empty 'file' field")
    try:
        blast = float(data.get("blast_radius", 1) or 1)
    except (TypeError, ValueError):
        blast = 1.0
    return str(data["file"]), data.get("content"), blast


def detect(path, content, blast):
    findings = []
    for ln_no, line in enumerate(content.splitlines(), start=1):
        if len(line) > 2000:
            line = line[:2000]
        for rule, rx, sev, owasp, cwe, conf, remediation in RULES:
            if rx.search(line):
                risk = round(SEV_WEIGHT[sev] * conf * max(blast, 1.0), 2)
                findings.append({
                    "rule": rule, "title": rule.replace("_", " ").title(), "file": path,
                    "line": ln_no, "severity": sev, "confidence": conf, "owasp": owasp,
                    "cwe": cwe, "risk_score": risk, "evidence": line.strip()[:200],
                    "reasoning": f"{owasp} ({cwe}) pattern matched on this line.",
                    "remediation": remediation,
                })
    return findings


def rank(findings):
    order = sorted(findings, key=lambda f: (-f["risk_score"], f["line"]))
    return [{"line": f["line"], "rule": f["rule"], "severity": f["severity"],
             "risk_score": f["risk_score"]} for f in order]


def summarize(findings):
    by_sev, by_rule = {"high": 0, "medium": 0, "low": 0}, {}
    for f in findings:
        by_sev[f["severity"]] = by_sev.get(f["severity"], 0) + 1
        by_rule[f["rule"]] = by_rule.get(f["rule"], 0) + 1
    top = max((f["risk_score"] for f in findings), default=0)
    return {"total": len(findings), "by_severity": by_sev, "by_rule": by_rule, "max_risk_score": top}


def build_explain_prompt(path, findings, content):
    items = [{"rule": f["rule"], "line": f["line"], "evidence": f["evidence"]} for f in findings]
    return (
        "You are an application security reviewer. Security pattern matches are noisy. For each "
        "finding, judge exploitability and return a calibrated severity (high|medium|low), whether "
        "it is likely a true positive, and one concrete remediation sentence. Return ONLY JSON: "
        '{"findings":[{"rule":str,"line":int,"severity":str,"true_positive":bool,"reasoning":str}]}.\n\n'
        f"File: {path}\nFindings: {json.dumps(items)}\n\nSource:\n```\n{content[:8000]}\n```\n"
    )


def apply_explanation(findings, text):
    obj = parse_json_block(text)
    by_key = {(str(f.get("rule")), int(f.get("line", -1))): f for f in obj.get("findings", []) if isinstance(f, dict)}
    for f in findings:
        upd = by_key.get((f["rule"], f["line"]))
        if upd:
            if upd.get("severity") in ("high", "medium", "low"):
                f["severity"] = upd["severity"]
            if upd.get("reasoning"):
                f["reasoning"] = str(upd["reasoning"])
            if "true_positive" in upd:
                f["true_positive"] = bool(upd["true_positive"])
    return findings


def main():
    argv = sys.argv
    path, content, blast = read_input(argv)
    mock = os.environ.get("SECURITY_RISK_REVIEWER_MOCK") == "1" or "--mock" in argv[1:]
    want_explain = "--explain" in argv[1:] or os.environ.get("SECURITY_RISK_REVIEWER_EXPLAIN") == "1"
    if content is None:
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as fh:
                content = fh.read(MAX_CONTENT_BYTES)
        except OSError as e:
            fail(f"cannot read target file {path!r}: {e}")

    findings = detect(path, content, blast)
    explained = False
    if findings and (want_explain or mock):
        if mock:
            for f in findings:
                f["reasoning"] = "MOCK: " + f["reasoning"]
            explained = True
        else:
            try:
                findings = apply_explanation(findings, explain(build_explain_prompt(path, findings, content)))
                explained = True
            except ProviderError as e:
                if want_explain and not mock:
                    fail(f"--explain requested but provider failed: {e}")

    print(json.dumps({
        "skill_version": SKILL_VERSION + ("-mock" if mock else ""), "target": path,
        "explained": explained, "summary": summarize(findings),
        "risk_ranking": rank(findings), "findings": findings,
    }))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""capability-mapper Agent Skill (Spec #54).

Maps a code file (+ its symbols) to a single business capability with a confidence
score and human-reviewable reasoning (REQ-0 transparency). Honors the fixed Layer 5
contract enforced by internal/indexer/skill_runner.go:

  invocation : python3 run.py '<json>'        (also accepts the JSON on stdin)
  input JSON : {"file": "<path>", "symbols": ["fn1", ...]}
  output JSON: {"capability","description","confidence","reasoning","skill_version"}

On any failure (bad input, unconfigured/missing provider, unparseable model output)
this script exits non-zero and writes the reason to stderr — it never fabricates a
capability. The only synthetic output is the explicitly-labelled mock mode.

Formal product/runtime LLM-API execution is owned by the Go/ADK provider path. This
script keeps a legacy standalone provider adapter only behind an explicit legacy env
gate; default and CI paths are agent-instruction or mock only.
"""

import json
import os
import re
import sys
import urllib.error
import urllib.request

SKILL_VERSION = "capability-mapper/1.1"
MAX_CONTENT_BYTES = 12 * 1024  # bound prompt size (FM-CAPM-04)
MAX_REQUIREMENTS = 500  # bound the requirement corpus so it cannot blow the prompt (Spec #96)


def _eprint(*args):
    print(*args, file=sys.stderr)


def fail(msg, code=2):
    _eprint(f"capability-mapper: {msg}")
    sys.exit(code)


def read_input(argv):
    """Parse the {file, symbols} JSON from argv[1], falling back to stdin."""
    raw = None
    args = [a for a in argv[1:] if a != "--mock"]
    if args:
        raw = args[0]
    elif not sys.stdin.isatty():
        raw = sys.stdin.read()
    if not raw:
        fail("no input JSON provided (argv[1] or stdin)")
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        fail(f"invalid input JSON: {e}")
    if not isinstance(data, dict) or not data.get("file"):
        fail("input JSON must be an object with a non-empty 'file' field")
    symbols = data.get("symbols") or []
    if not isinstance(symbols, list):
        symbols = []
    # Optional ubiquitous-language glossary (Spec #91): the canonical capabilities
    # already chosen for this project, so the model maps into them instead of
    # minting near-duplicate free-text names.
    glossary = []
    for e in data.get("glossary") or []:
        if isinstance(e, dict) and e.get("name"):
            glossary.append({
                "canonical_id": str(e.get("canonical_id") or ""),
                "name": str(e["name"]),
                "aliases": [str(a) for a in (e.get("aliases") or []) if a],
            })
    # Optional declared requirement corpus (Spec #96): the project requirements this
    # capability may serve, so the mapping can carry a business-value linkage. Mirrors
    # the glossary contract — absent/empty means byte-for-byte v1.0 behavior.
    requirements = []
    for e in data.get("requirements") or []:
        if isinstance(e, dict) and e.get("req_id"):
            requirements.append({
                "req_id": str(e["req_id"]),
                "title": str(e.get("title") or ""),
                "source": str(e.get("source") or ""),
            })
    return str(data["file"]), [str(s) for s in symbols], glossary, requirements


def read_file_best_effort(path):
    """Read up to MAX_CONTENT_BYTES of the file; return ('', note) on failure."""
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            content = fh.read(MAX_CONTENT_BYTES + 1)
    except OSError:
        return "", "file content unavailable (could not open); mapped from symbols and path only"
    if len(content) > MAX_CONTENT_BYTES:
        return content[:MAX_CONTENT_BYTES], "file content truncated to bound prompt size"
    return content, ""


# --------------------------------------------------------------------------- mock


def _tokens(text):
    return set(re.findall(r"[a-z0-9]+", (text or "").lower()))


def best_requirement(seed, requirements):
    """Deterministically pick the requirement whose req_id/title shares the most
    lowercased tokens with the seed. Ties (incl. zero overlap) resolve to the first
    requirement, so the choice is stable for the mock/offline path (Spec #96)."""
    seed_toks = _tokens(seed)
    best, best_score = None, -1
    for rq in requirements:
        score = len(seed_toks & _tokens(rq.get("req_id", "") + " " + rq.get("title", "")))
        if score > best_score:
            best, best_score = rq, score
    return best


def mock_result(file_path, symbols, glossary=None, requirements=None):
    """Deterministic, clearly-labelled offline output (REQ-CAPM-003). When a
    glossary is supplied, snap to the first term whose name/alias token appears in
    the seed (demonstrates the ubiquitous-language behavior offline; the Go writer
    is the authoritative canonicalizer). When a requirement corpus is supplied,
    attach a deterministic, labelled requirement/business-value linkage (Spec #96)."""
    base = os.path.basename(file_path)
    stem = os.path.splitext(base)[0]
    seed = stem
    if symbols:
        seed = f"{stem} {symbols[0]}"
    words = [w for w in seed.replace("_", " ").replace("-", " ").split() if w]
    capability = " ".join(w.capitalize() for w in words) or "Unclassified Capability"
    if glossary:
        low = seed.lower()
        for t in glossary:
            for cand in [t["name"]] + t.get("aliases", []):
                first = cand.split()[0].lower() if cand.split() else ""
                if first and first in low:
                    capability = t["name"]
                    break
            else:
                continue
            break
    result = {
        "capability": capability,
        "description": f"MOCK mapping for {base} derived from filename and symbols.",
        "confidence": 0.4,
        "reasoning": "MOCK: deterministic offline output (CAPABILITY_MAPPER_MOCK); not a real model judgement.",
        "skill_version": SKILL_VERSION + "-mock",
    }
    if requirements:
        rq = best_requirement(seed, requirements)
        if rq:
            result["requirements"] = [{"req_id": rq["req_id"], "confidence": 0.4}]
            result["business_value"] = (
                f"MOCK: {capability} serves {rq['req_id']}"
                + (f" ({rq['title']})" if rq.get("title") else "")
            )
    return result


# ----------------------------------------------------------------------- prompting


def build_prompt(file_path, symbols, content, glossary=None, requirements=None):
    sym = ", ".join(symbols) if symbols else "(none provided)"
    gloss = ""
    if glossary:
        names = "\n".join(f"  - {t['name']}" for t in glossary)
        gloss = (
            "\nUbiquitous language (DDD) — map into the project's EXISTING capability vocabulary so\n"
            "names do not drift. Reuse the best-matching existing capability name VERBATIM. Only if\n"
            "NONE fits, propose a new one and prefix the `capability` value with 'NEW: ' so a human\n"
            "can curate it. Prefer the base capability, not a per-variant label — a country/region/\n"
            "document suffix (e.g. _BE/_NL/_US, …Europe, _SalesTable) is a VARIANT of one capability,\n"
            "not a distinct one.\n"
            "Existing capabilities:\n" + names + "\n"
        )
    # Requirement / business-value grounding (Spec #96). Only present when a corpus is
    # supplied; otherwise the prompt and the required output keys are unchanged from v1.0.
    reqs = ""
    extra_keys = ""
    if requirements:
        listed = "\n".join(
            f"  - {r['req_id']}: {r['title']}" if r.get("title") else f"  - {r['req_id']}"
            for r in requirements
        )
        reqs = (
            "\nDeclared requirements / business value — these are the project's declared\n"
            "requirements. Identify which ones THIS capability actually serves (it may be none).\n"
            "Also return a one-line `business_value` stating, in business terms, the value this\n"
            "capability delivers. Do not invent requirement ids that are not listed below.\n"
            "Requirements:\n" + listed + "\n"
        )
        extra_keys = (
            "- requirements: array of {\"req_id\": str (from the list above), \"confidence\": number 0..1}\n"
            "  for the requirements this capability serves; omit or use [] if none apply.\n"
            "- business_value: one-line business-value statement.\n"
        )
        key_line = (
            '  {"capability": str, "description": str, "confidence": number 0..1, "reasoning": str,\n'
            '   "requirements": [{"req_id": str, "confidence": number 0..1}], "business_value": str}\n'
        )
    else:
        key_line = '  {"capability": str, "description": str, "confidence": number 0..1, "reasoning": str}\n'
    return (
        "You map source code to a single business capability for a code knowledge graph.\n"
        "Return ONLY a JSON object with these keys and nothing else:\n"
        f"{key_line}"
        "- capability: a short business-capability name (e.g. 'Order Fulfilment').\n"
        "- confidence: your calibrated confidence in the mapping.\n"
        "- reasoning: brief justification a human reviewer can audit.\n"
        f"{extra_keys}"
        f"{gloss}"
        f"{reqs}\n"
        f"File: {file_path}\n"
        f"Symbols: {sym}\n"
        "Content:\n"
        "```\n"
        f"{content}\n"
        "```\n"
    )


def parse_model_json(text):
    """Extract and validate the JSON object the model returned."""
    text = (text or "").strip()
    # Tolerate fenced ```json blocks.
    if text.startswith("```"):
        text = text.strip("`")
        if text.lstrip().lower().startswith("json"):
            text = text.lstrip()[4:]
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1 or end < start:
        fail(f"model output is not JSON: {text[:200]!r}")
    try:
        obj = json.loads(text[start : end + 1])
    except json.JSONDecodeError as e:
        fail(f"model output JSON parse failed: {e}")
    for field in ("capability", "description", "reasoning"):
        if not obj.get(field):
            fail(f"model output missing required field: {field}")
    try:
        conf = float(obj.get("confidence", 0.0))
    except (TypeError, ValueError):
        conf = 0.0
    obj["confidence"] = max(0.0, min(1.0, conf))
    # Optional requirement / business-value linkage (Spec #96). Validated and pruned —
    # absent or malformed means the key is dropped, never fabricated.
    clean_reqs = []
    for it in obj.get("requirements") or []:
        if isinstance(it, dict) and it.get("req_id"):
            try:
                rc = float(it.get("confidence", 0.0))
            except (TypeError, ValueError):
                rc = 0.0
            clean_reqs.append({"req_id": str(it["req_id"]), "confidence": max(0.0, min(1.0, rc))})
    if clean_reqs:
        obj["requirements"] = clean_reqs
    else:
        obj.pop("requirements", None)
    bv = obj.get("business_value")
    if isinstance(bv, str) and bv.strip():
        obj["business_value"] = bv.strip()
    else:
        obj.pop("business_value", None)
    obj["skill_version"] = SKILL_VERSION
    return obj


# ----------------------------------------------------------------------- providers


def env(*names, default=""):
    for n in names:
        v = os.environ.get(n)
        if v:
            return v
    return default


def annotation_mode():
    return env(
        "CODE_REVIEW_CAPABILITY_MODE",
        "CODE_REVIEW_ANNOTATION_MODE",
        "CODE_REVIEW_SEMANTIC_MODE",
        default="agent-instruction",
    ).lower()


def require_llm_api_mode():
    mode = annotation_mode()
    if mode not in ("agent-instruction", "llm-api"):
        fail("unsupported capability annotation mode %r (expected agent-instruction|llm-api)" % mode)
    if mode != "llm-api":
        fail(
            "capability-mapper default mode is agent-instruction: use the skill instructions with a subscription coding agent, "
            "or set CODE_REVIEW_CAPABILITY_MODE=llm-api to call provider APIs explicitly"
        )
    if os.environ.get("CODE_REVIEW_ALLOW_LEGACY_PYTHON_LLM_API") != "1":
        fail(
            "formal llm-api execution is Go/ADK based; this Python provider adapter is legacy/standalone. "
            "Set CODE_REVIEW_ALLOW_LEGACY_PYTHON_LLM_API=1 only for legacy adapter tests."
        )


def bedrock_model_candidates():
    model = env("CODE_REVIEW_LLM_BEDROCK_MODEL")
    if model:
        return [model]
    seq = env("CODE_REVIEW_LLM_BEDROCK_MODEL_SEQUENCE")
    if seq:
        models = [m.strip() for m in seq.split(",") if m.strip()]
        if models:
            return models
    return ["moonshotai.kimi-k2.5", "minimax.minimax-m2.5"]


def call_bedrock(prompt):
    region = env("CODE_REVIEW_LLM_BEDROCK_REGION", "AWS_REGION", "AWS_DEFAULT_REGION")
    if not region:
        fail("bedrock provider requires CODE_REVIEW_LLM_BEDROCK_REGION (or AWS_REGION)")
    try:
        import boto3  # optional dependency (FM-CAPM-01)
    except ImportError:
        fail("bedrock provider requires boto3 (pip install boto3) — refusing to fabricate")
    kwargs = {"region_name": region}
    ak = env("CODE_REVIEW_LLM_BEDROCK_ACCESS_KEY_ID")
    sk = env("CODE_REVIEW_LLM_BEDROCK_SECRET_ACCESS_KEY")
    if ak and sk:
        kwargs["aws_access_key_id"] = ak
        kwargs["aws_secret_access_key"] = sk
        st = env("CODE_REVIEW_LLM_BEDROCK_SESSION_TOKEN")
        if st:
            kwargs["aws_session_token"] = st
    errors = []
    try:
        client = boto3.client("bedrock-runtime", **kwargs)
    except Exception as e:  # noqa: BLE001 — surface any AWS error honestly
        fail(f"bedrock client setup failed: {e}")
    for model in bedrock_model_candidates():
        if hasattr(client, "converse"):
            try:
                resp = client.converse(
                    modelId=model,
                    messages=[{"role": "user", "content": [{"text": prompt}]}],
                    inferenceConfig={"temperature": 0.1, "maxTokens": 2048},
                )
                return _extract_bedrock_text(resp)
            except Exception as e:  # noqa: BLE001 — try declared fallback model
                errors.append(f"{model}: {e}")
                continue
        elif model.startswith("anthropic."):
            try:
                resp = _bedrock_invoke_model_anthropic(client, model, prompt)
                return _extract_bedrock_text(resp)
            except Exception as e:  # noqa: BLE001 — try declared fallback model
                errors.append(f"{model}: {e}")
                continue
        else:
            errors.append(
                f"installed boto3 lacks the Converse API needed for non-anthropic model {model!r}"
                " — upgrade boto3 (pip install -U boto3) or use an anthropic.* model"
            )
    fail(f"bedrock invocation failed for all declared models: {'; '.join(errors)}")


def _extract_bedrock_text(resp):
    """Return the first non-empty text block from a Bedrock response.

    Handles both Converse ({"output": {"message": {"content": [...]}}}) and
    anthropic invoke_model ({"content": [...]}) shapes. Reasoning-capable
    models (e.g. minimax.minimax-m2.5) emit a reasoningContent block before
    the text block, so blocks without usable "text" are skipped instead of
    assuming content[0] is text (2026-06-07 live-spike fix).
    """
    try:
        if "output" in resp:
            blocks = resp["output"]["message"]["content"]
        else:
            blocks = resp["content"]
        for block in blocks:
            if isinstance(block, dict):
                text = block.get("text")
                if isinstance(text, str) and text.strip():
                    return text
        fail(f"no text content block in bedrock response (blocks: {[sorted(b) for b in blocks if isinstance(b, dict)]})")
    except (KeyError, IndexError, TypeError) as e:
        fail(f"unexpected bedrock response shape: {e}")


def _bedrock_invoke_model_anthropic(client, model, prompt):
    payload = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 2048,
        "temperature": 0.1,
        "messages": [{"role": "user", "content": [{"type": "text", "text": prompt}]}],
    }
    resp = client.invoke_model(
        modelId=model,
        body=json.dumps(payload).encode("utf-8"),
        contentType="application/json",
        accept="application/json",
    )
    return json.loads(resp["body"].read().decode("utf-8"))


def _http_post_json(url, payload, headers, timeout):
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.URLError as e:
        fail(f"http request to {url} failed: {e}")
    except json.JSONDecodeError as e:
        fail(f"http response from {url} not JSON: {e}")


def call_openai_compatible(prompt):
    base = env("CODE_REVIEW_LLM_OPENAI_BASE_URL")
    if not base:
        fail("openai provider requires CODE_REVIEW_LLM_OPENAI_BASE_URL")
    api_key = env("CODE_REVIEW_LLM_OPENAI_API_KEY")
    model = env("CODE_REVIEW_LLM_OPENAI_MODEL", "CODE_REVIEW_LLM_MODEL",
                default="moonshotai.kimi-k2.5")
    auth_mode = env("CODE_REVIEW_LLM_OPENAI_AUTH_MODE", default="bearer").lower()
    headers = {"Content-Type": "application/json"}
    if api_key:
        if auth_mode == "x-api-key":
            headers["x-api-key"] = api_key
        else:
            headers["Authorization"] = f"Bearer {api_key}"
    payload = {
        "model": model,
        "temperature": 0.1,
        "messages": [{"role": "user", "content": prompt}],
    }
    data = _http_post_json(base.rstrip("/") + "/chat/completions", payload, headers, 60)
    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError) as e:
        fail(f"unexpected openai response shape: {e}")


def call_gateway(prompt):
    endpoint = env("CODE_REVIEW_LLM_GATEWAY_ENDPOINT", "CODE_REVIEW_AWS_BEDROCK_API_URL")
    if not endpoint:
        fail("bedrock-gateway provider requires CODE_REVIEW_LLM_GATEWAY_ENDPOINT")
    api_key = env("CODE_REVIEW_LLM_GATEWAY_API_KEY", "CODE_REVIEW_AWS_BEDROCK_API_KEY")
    if not api_key:
        fail("bedrock-gateway provider requires CODE_REVIEW_LLM_GATEWAY_API_KEY")
    model = env("CODE_REVIEW_LLM_GATEWAY_MODEL", "CODE_REVIEW_AWS_BEDROCK_MODEL",
                default="moonshotai.kimi-k2.5")
    headers = {"Content-Type": "application/json", "x-api-key": api_key}
    user_id = env("CODE_REVIEW_LLM_GATEWAY_USER_ID", "CODE_REVIEW_AWS_BEDROCK_USER_ID")
    if user_id:
        headers["user-id"] = user_id
    payload = {
        "model": model,
        "temperature": 0.1,
        "messages": [{"role": "user", "content": prompt}],
    }
    data = _http_post_json(endpoint, payload, headers, 60)
    # Accept either OpenAI-style or a simple {"content": "..."} gateway shape.
    if isinstance(data, dict):
        if "choices" in data:
            try:
                return data["choices"][0]["message"]["content"]
            except (KeyError, IndexError):
                pass
        for key in ("content", "output", "text"):
            if isinstance(data.get(key), str):
                return data[key]
    fail(f"unexpected gateway response shape: {str(data)[:200]}")


PROVIDERS = {
    "bedrock": call_bedrock,
    "bedrock-gateway": call_gateway,
    "openai": call_openai_compatible,
}


# ----------------------------------------------------------- requirement collector (Spec #96)

# Bold form in spec requirements.md: "- **REQ-FOO-001 (generic)** — Title text."
_REQ_TITLE_RE = re.compile(r"\*\*\s*(REQ-[A-Z0-9]+-\d+)\b[^*]*\*\*\s*[—:\-]+\s*(.+)")
# Family token used in RTM.md / SPECS.md rows, e.g. "REQ-FOO-*".
_REQ_FAMILY_RE = re.compile(r"REQ-[A-Z0-9]+-\*")


def _spec_requirements_files(root):
    """All */requirements.md under the .agents/.kiro/.claude spec trees of root."""
    files = []
    for rel in (".agents/specs", ".kiro/specs", ".claude/specs"):
        base = os.path.join(root, *rel.split("/"))
        if os.path.isdir(base):
            for name in sorted(os.listdir(base)):
                p = os.path.join(base, name, "requirements.md")
                if os.path.isfile(p):
                    files.append(p)
    return files


def _parse_requirements_md(path):
    out = []
    specdir = os.path.basename(os.path.dirname(path))
    source = f"spec:{specdir}/requirements.md"
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            for line in fh:
                m = _REQ_TITLE_RE.search(line)
                if m:
                    title = re.sub(r"\s+", " ", m.group(2)).strip().rstrip("*").strip()
                    out.append({"req_id": m.group(1), "title": title[:200], "source": source})
    except OSError:
        pass
    return out


def _parse_table_families(path, source):
    """Extract REQ-*-* family rows from a markdown table (RTM.md / SPECS.md), using the
    second table cell (the spec name) as the title when available."""
    out = []
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            for line in fh:
                if not line.lstrip().startswith("|"):
                    continue
                cells = [c.strip() for c in line.strip().strip("|").split("|")]
                fam = next((_REQ_FAMILY_RE.search(c).group(0) for c in cells
                            if _REQ_FAMILY_RE.search(c)), None)
                if fam:
                    title = cells[1] if len(cells) > 1 else ""
                    out.append({"req_id": fam, "title": title, "source": source})
    except OSError:
        pass
    return out


def collect_requirements(root):
    """Parse the project requirement corpus under root into a deduped requirement list
    (Spec #96 REQ-CMRG-003 — the spec-tracer replacement). Concrete REQ ids from spec
    requirements.md take precedence over RTM.md / SPECS.md family rows. Fails closed when
    no corpus is found; never fabricates."""
    if not os.path.isdir(root):
        fail(f"--collect-requirements root not a directory: {root}")
    by_id, order = {}, []

    def add(entry):
        rid = entry["req_id"]
        if rid not in by_id:  # first (highest-precedence) title wins
            by_id[rid] = entry
            order.append(rid)

    spec_files = _spec_requirements_files(root)
    for p in spec_files:  # precedence 1: concrete ids + titles
        for e in _parse_requirements_md(p):
            add(e)
    rtm = os.path.join(root, ".agents", "specs", "RTM.md")
    if os.path.isfile(rtm):  # precedence 2: RTM family rows
        for e in _parse_table_families(rtm, "RTM.md"):
            add(e)
    specs = os.path.join(root, ".agents", "specs", "SPECS.md")
    if os.path.isfile(specs):  # precedence 3: SPECS family rows
        for e in _parse_table_families(specs, "SPECS.md"):
            add(e)

    if not order:
        fail(f"no spec corpus found under {root} "
             "(looked for .agents/.kiro/.claude specs requirements.md, RTM.md, SPECS.md)")
    dropped = max(0, len(order) - MAX_REQUIREMENTS)
    kept = order[:MAX_REQUIREMENTS]
    return {
        "requirements": [by_id[r] for r in kept],
        "stats": {"count": len(kept), "dropped": dropped, "specs_scanned": len(spec_files)},
    }


# ------------------------------------------------------------------------------------ main


def _flag_value(argv, name):
    """Return the value following --name, or None."""
    if name in argv:
        i = argv.index(name)
        if i + 1 < len(argv):
            return argv[i + 1]
    return None


def emit_result_envelope(argv):
    """Wrap per-file capability annotations into an agent-instruction-capabilities-result/v1
    envelope that `review-cli apply-handoff` ingests (Spec #97 CR-2026-06-22-001).

    Input is a JSON array of annotation objects (or {"results": [...]}), each with at
    least source_file + capability, read from --annotations <file> or stdin. The
    Go apply path is the validation authority; this only assembles the envelope so an
    agent does not hand-build it. --target-root must match the handoff's target_root.
    """
    target_root = _flag_value(argv, "--target-root") or "."
    ann_path = _flag_value(argv, "--annotations")
    try:
        raw = open(ann_path, encoding="utf-8").read() if ann_path else sys.stdin.read()
    except OSError as e:
        fail(f"--emit-result-envelope cannot read annotations: {e}")
    try:
        items = json.loads(raw)
    except json.JSONDecodeError as e:
        fail(f"--emit-result-envelope invalid annotations JSON: {e}")
    if isinstance(items, dict) and isinstance(items.get("results"), list):
        items = items["results"]
    if not isinstance(items, list):
        fail("--emit-result-envelope expects a JSON array of annotation objects (or {results:[...]})")
    for it in items:
        if not isinstance(it, dict) or not it.get("source_file") or not it.get("capability"):
            fail("each annotation needs at least source_file + capability")
    print(json.dumps({
        "schema_version": "agent-instruction-capabilities-result/v1",
        "cost_class": "subscription-agent",
        "provenance": "agent-instruction",
        "target_root": target_root,
        "candidate_count": len(items),
        "results": items,
    }))


def main():
    argv = sys.argv

    if "--emit-result-envelope" in argv[1:]:
        emit_result_envelope(argv)
        return

    if "--collect-requirements" in argv[1:]:
        i = argv.index("--collect-requirements")
        root = argv[i + 1] if i + 1 < len(argv) else None
        if not root:
            fail("--collect-requirements requires a project root path")
        print(json.dumps(collect_requirements(root)))
        return

    file_path, symbols, glossary, requirements = read_input(argv)

    mock = os.environ.get("CAPABILITY_MAPPER_MOCK") == "1" or "--mock" in argv[1:]
    if mock:
        print(json.dumps(mock_result(file_path, symbols, glossary, requirements)))
        return

    require_llm_api_mode()

    content, note = read_file_best_effort(file_path)
    prompt = build_prompt(file_path, symbols, content, glossary, requirements)

    provider = env("CODE_REVIEW_LLM_PROVIDER", "CODE_REVIEW_AWS_BEDROCK_PROVIDER",
                   default="bedrock").lower()
    fn = PROVIDERS.get(provider)
    if fn is None:
        fail(f"unsupported provider {provider!r} (expected one of {sorted(PROVIDERS)})")

    text = fn(prompt)
    result = parse_model_json(text)
    if note:
        result["reasoning"] = f"{result['reasoning']} [{note}]"
    print(json.dumps(result))


if __name__ == "__main__":
    main()

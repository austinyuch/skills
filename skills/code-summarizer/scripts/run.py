#!/usr/bin/env python3
"""code-summarizer Agent Skill (Spec #56).

Generates a structured, file-level summary with a confidence score and
human-reviewable reasoning (REQ-0 transparency). Honors the Layer-style enrichment
contract invoked by internal/indexer/skill_runner.go (RunSummaryEnrichment):

  invocation : python3 run.py '<json>'        (also accepts the JSON on stdin)
  input JSON : {"file": "<path>", "symbols": ["fn1", ...]}
  output JSON: {"summary","confidence","reasoning","skill_version"}

On any failure (bad input, unconfigured/missing provider, unparseable model output)
this script exits non-zero and writes the reason to stderr — it never fabricates a
summary. The only synthetic output is the explicitly-labelled mock mode.

Formal product/runtime LLM-API execution is owned by the Go/ADK provider path. This
script keeps a legacy standalone provider adapter only behind an explicit legacy env
gate; default and CI paths are agent-instruction or mock only.
"""

import json
import os
import sys
import urllib.error
import urllib.request

SKILL_VERSION = "code-summarizer/1.0"
MAX_CONTENT_BYTES = 12 * 1024  # bound prompt size


def _eprint(*args):
    print(*args, file=sys.stderr)


def fail(msg, code=2):
    _eprint(f"code-summarizer: {msg}")
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
    return str(data["file"]), [str(s) for s in symbols]


def read_file_best_effort(path):
    """Read up to MAX_CONTENT_BYTES of the file; return ('', note) on failure."""
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            content = fh.read(MAX_CONTENT_BYTES + 1)
    except OSError:
        return "", "file content unavailable (could not open); summarized from symbols and path only"
    if len(content) > MAX_CONTENT_BYTES:
        return content[:MAX_CONTENT_BYTES], "file content truncated to bound prompt size"
    return content, ""


# --------------------------------------------------------------------------- mock


def mock_result(file_path, symbols):
    """Deterministic, clearly-labelled offline output (REQ-CSUM-003)."""
    base = os.path.basename(file_path)
    sym = ", ".join(symbols[:3]) if symbols else "no exported symbols"
    return {
        "summary": f"{base}: defines {sym}.",
        "confidence": 0.4,
        "reasoning": "MOCK: deterministic offline output (CODE_SUMMARIZER_MOCK); not a real model judgement.",
        "skill_version": SKILL_VERSION + "-mock",
    }


# ----------------------------------------------------------------------- prompting


def build_prompt(file_path, symbols, content):
    sym = ", ".join(symbols) if symbols else "(none provided)"
    return (
        "You write a concise, structured summary of a source file for a code knowledge graph.\n"
        "Return ONLY a JSON object with these keys and nothing else:\n"
        '  {"summary": str, "confidence": number 0..1, "reasoning": str}\n'
        "- summary: 1-3 sentences on the file's responsibility and key behavior.\n"
        "- confidence: your calibrated confidence in the summary.\n"
        "- reasoning: brief justification a human reviewer can audit.\n\n"
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
    for field in ("summary", "reasoning"):
        if not obj.get(field):
            fail(f"model output missing required field: {field}")
    try:
        conf = float(obj.get("confidence", 0.0))
    except (TypeError, ValueError):
        conf = 0.0
    obj["confidence"] = max(0.0, min(1.0, conf))
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
        "CODE_REVIEW_SUMMARY_MODE",
        "CODE_REVIEW_ANNOTATION_MODE",
        "CODE_REVIEW_SEMANTIC_MODE",
        default="agent-instruction",
    ).lower()


def require_llm_api_mode():
    mode = annotation_mode()
    if mode not in ("agent-instruction", "llm-api"):
        fail("unsupported summary annotation mode %r (expected agent-instruction|llm-api)" % mode)
    if mode != "llm-api":
        fail(
            "code-summarizer default mode is agent-instruction: use the skill instructions with a subscription coding agent, "
            "or set CODE_REVIEW_SUMMARY_MODE=llm-api to call provider APIs explicitly"
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
        import boto3
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


def _flag_value(argv, name):
    """Return the value following --name, or None."""
    if name in argv:
        i = argv.index(name)
        if i + 1 < len(argv):
            return argv[i + 1]
    return None


def emit_result_envelope(argv):
    """Wrap per-file summary annotations into an agent-instruction-summaries-result/v1
    envelope that `review-cli apply-handoff` ingests (Spec #97 CR-2026-06-22-001).

    Input is a JSON array of annotation objects (or {"results": [...]}), each with at
    least source_file + summary, read from --annotations <file> or stdin. The Go apply
    path is the validation authority; this only assembles the envelope. --target-root
    must match the handoff's target_root.
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
        if not isinstance(it, dict) or not it.get("source_file") or not it.get("summary"):
            fail("each annotation needs at least source_file + summary")
    print(json.dumps({
        "schema_version": "agent-instruction-summaries-result/v1",
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

    file_path, symbols = read_input(argv)

    mock = os.environ.get("CODE_SUMMARIZER_MOCK") == "1" or "--mock" in argv[1:]
    if mock:
        print(json.dumps(mock_result(file_path, symbols)))
        return

    require_llm_api_mode()

    content, note = read_file_best_effort(file_path)
    prompt = build_prompt(file_path, symbols, content)

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

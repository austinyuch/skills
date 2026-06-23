#!/usr/bin/env python3
"""Shared optional LLM-explain provider for the code-review helper skills.

The deterministic detector in each skill's run.py is the source of truth and runs
fully offline. This module adds an OPTIONAL natural-language explanation / severity
calibration pass, reusing the Go service's CODE_REVIEW_LLM_* env vars and the
workspace Bedrock-first preference (docs/provider-support-matrix.md).

Unlike the pure-LLM siblings (capability-mapper / code-summarizer) this helper raises
ProviderError instead of calling sys.exit, so run.py owns the degrade policy: an
opt-in --explain forces a hard failure when the provider is unconfigured, while the
default deterministic mode keeps its findings and only notes that explanation was
skipped. The same copy of this file is vendored into each skill's scripts/ dir so each
skill stays self-contained and installs independently.
"""

import json
import os
import urllib.error
import urllib.request


class ProviderError(Exception):
    """Raised on any provider misconfiguration or call failure."""


def env(*names, default=""):
    for n in names:
        v = os.environ.get(n)
        if v:
            return v
    return default


def parse_json_block(text):
    """Tolerantly extract the first JSON object the model returned."""
    text = (text or "").strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lstrip().lower().startswith("json"):
            text = text.lstrip()[4:]
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1 or end < start:
        raise ProviderError(f"model output is not JSON: {text[:200]!r}")
    try:
        return json.loads(text[start : end + 1])
    except json.JSONDecodeError as e:
        raise ProviderError(f"model JSON parse failed: {e}")


def _extract_bedrock_text(resp):
    """First non-empty text block (skips reasoningContent blocks)."""
    try:
        blocks = resp["output"]["message"]["content"] if "output" in resp else resp["content"]
        for block in blocks:
            if isinstance(block, dict):
                text = block.get("text")
                if isinstance(text, str) and text.strip():
                    return text
        raise ProviderError("no text content block in bedrock response")
    except (KeyError, IndexError, TypeError) as e:
        raise ProviderError(f"unexpected bedrock response shape: {e}")


def call_bedrock(prompt):
    region = env("CODE_REVIEW_LLM_BEDROCK_REGION", "AWS_REGION", "AWS_DEFAULT_REGION")
    if not region:
        raise ProviderError("bedrock requires CODE_REVIEW_LLM_BEDROCK_REGION (or AWS_REGION)")
    model = env("CODE_REVIEW_LLM_BEDROCK_MODEL", default="us.anthropic.claude-sonnet-4-6")
    try:
        import boto3
    except ImportError:
        raise ProviderError("bedrock requires boto3 (pip install boto3)")
    kwargs = {"region_name": region}
    ak = env("CODE_REVIEW_LLM_BEDROCK_ACCESS_KEY_ID")
    sk = env("CODE_REVIEW_LLM_BEDROCK_SECRET_ACCESS_KEY")
    if ak and sk:
        kwargs["aws_access_key_id"] = ak
        kwargs["aws_secret_access_key"] = sk
        st = env("CODE_REVIEW_LLM_BEDROCK_SESSION_TOKEN")
        if st:
            kwargs["aws_session_token"] = st
    try:
        client = boto3.client("bedrock-runtime", **kwargs)
        if hasattr(client, "converse"):
            resp = client.converse(
                modelId=model,
                messages=[{"role": "user", "content": [{"text": prompt}]}],
                inferenceConfig={"temperature": 0.1, "maxTokens": 2048},
            )
        elif model.startswith("anthropic."):
            payload = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 2048,
                "temperature": 0.1,
                "messages": [{"role": "user", "content": [{"type": "text", "text": prompt}]}],
            }
            raw = client.invoke_model(
                modelId=model, body=json.dumps(payload).encode("utf-8"),
                contentType="application/json", accept="application/json",
            )
            resp = json.loads(raw["body"].read().decode("utf-8"))
        else:
            raise ProviderError(f"installed boto3 lacks Converse for non-anthropic model {model!r}")
    except ProviderError:
        raise
    except Exception as e:  # noqa: BLE001 — surface any AWS error honestly
        raise ProviderError(f"bedrock invocation failed: {e}")
    return _extract_bedrock_text(resp)


def _http_post_json(url, payload, headers, timeout=60):
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.URLError as e:
        raise ProviderError(f"http request to {url} failed: {e}")
    except json.JSONDecodeError as e:
        raise ProviderError(f"http response from {url} not JSON: {e}")


def call_openai_compatible(prompt):
    base = env("CODE_REVIEW_LLM_OPENAI_BASE_URL")
    if not base:
        raise ProviderError("openai provider requires CODE_REVIEW_LLM_OPENAI_BASE_URL")
    api_key = env("CODE_REVIEW_LLM_OPENAI_API_KEY")
    model = env("CODE_REVIEW_LLM_MODEL", default="gpt-4o-mini")
    auth_mode = env("CODE_REVIEW_LLM_OPENAI_AUTH_MODE", default="bearer").lower()
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["x-api-key" if auth_mode == "x-api-key" else "Authorization"] = (
            api_key if auth_mode == "x-api-key" else f"Bearer {api_key}"
        )
    payload = {"model": model, "temperature": 0.1, "messages": [{"role": "user", "content": prompt}]}
    data = _http_post_json(base.rstrip("/") + "/chat/completions", payload, headers)
    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError) as e:
        raise ProviderError(f"unexpected openai response shape: {e}")


def call_gateway(prompt):
    endpoint = env("CODE_REVIEW_LLM_GATEWAY_ENDPOINT", "CODE_REVIEW_AWS_BEDROCK_API_URL")
    if not endpoint:
        raise ProviderError("gateway provider requires CODE_REVIEW_LLM_GATEWAY_ENDPOINT")
    api_key = env("CODE_REVIEW_LLM_GATEWAY_API_KEY", "CODE_REVIEW_AWS_BEDROCK_API_KEY")
    if not api_key:
        raise ProviderError("gateway provider requires CODE_REVIEW_LLM_GATEWAY_API_KEY")
    model = env("CODE_REVIEW_LLM_GATEWAY_MODEL", "CODE_REVIEW_AWS_BEDROCK_MODEL",
                default="anthropic.claude-sonnet-4-6")
    headers = {"Content-Type": "application/json", "x-api-key": api_key}
    user_id = env("CODE_REVIEW_LLM_GATEWAY_USER_ID", "CODE_REVIEW_AWS_BEDROCK_USER_ID")
    if user_id:
        headers["user-id"] = user_id
    payload = {"model": model, "temperature": 0.1, "messages": [{"role": "user", "content": prompt}]}
    data = _http_post_json(endpoint, payload, headers)
    if isinstance(data, dict):
        if "choices" in data:
            try:
                return data["choices"][0]["message"]["content"]
            except (KeyError, IndexError):
                pass
        for key in ("content", "output", "text"):
            if isinstance(data.get(key), str):
                return data[key]
    raise ProviderError(f"unexpected gateway response shape: {str(data)[:200]}")


PROVIDERS = {
    "bedrock": call_bedrock,
    "bedrock-gateway": call_gateway,
    "openai": call_openai_compatible,
}


def explain(prompt):
    """Call the configured provider. Raises ProviderError on any failure."""
    provider = env("CODE_REVIEW_LLM_PROVIDER", "CODE_REVIEW_AWS_BEDROCK_PROVIDER",
                   default="bedrock").lower()
    fn = PROVIDERS.get(provider)
    if fn is None:
        raise ProviderError(f"unsupported provider {provider!r} (expected one of {sorted(PROVIDERS)})")
    return fn(prompt)

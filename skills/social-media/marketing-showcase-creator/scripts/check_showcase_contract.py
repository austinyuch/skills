#!/usr/bin/env python3
"""Validate a generated marketing showcase's bilingual + print contract.

This is intentionally a lightweight structural guard, not visual QA. It catches
the common regressions before a human does the final Save-as-PDF review:
missing Print button, missing window.print() handler, broken language pairing,
or print CSS that lost the disappearing-section / paper-contrast fix.
"""
from __future__ import annotations

import argparse
import os
import re
import sys
import tempfile
from html.parser import HTMLParser
from pathlib import Path


class TagCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.tags: list[tuple[str, dict[str, str]]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.tags.append((tag.lower(), {k.lower(): v or "" for k, v in attrs}))


def read_optional(path: Path | None) -> str:
    if path is None or not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def attr_has(attrs: dict[str, str], name: str, pattern: str) -> bool:
    return re.search(pattern, attrs.get(name, ""), re.I) is not None


def validate(html_path: Path, css_path: Path | None = None, js_path: Path | None = None) -> list[str]:
    errors: list[str] = []
    if not html_path.exists():
        return [f"missing html file: {html_path}"]

    html = html_path.read_text(encoding="utf-8")
    base = html_path.parent
    css = read_optional(css_path or base / "style.css")
    js = read_optional(js_path or base / "showcase.js")
    combined = "\n".join([html, css, js])

    parser = TagCollector()
    parser.feed(html)

    buttons = [
        attrs for tag, attrs in parser.tags
        if tag == "button" and attrs.get("id") == "print-button"
    ]
    if not buttons:
        errors.append("missing <button id=\"print-button\">")
    else:
        button = buttons[0]
        if button.get("type", "").lower() != "button":
            errors.append("print button must use type=\"button\"")
        if not (
            attr_has(button, "onclick", r"\bprintShowcase\s*\(")
            or "printShowcase" in js
            or re.search(r"addEventListener\s*\(\s*['\"]click['\"]", combined)
        ):
            errors.append("print button is not wired to printShowcase() or a click listener")

    if not re.search(r"function\s+printShowcase\s*\(", combined):
        errors.append("missing printShowcase() function")
    if "window.print" not in combined:
        errors.append("printShowcase() must call window.print()")

    lang_en = len(re.findall(r"class=[\"'][^\"']*\blang-en\b", html))
    lang_zh = len(re.findall(r"class=[\"'][^\"']*\blang-zh\b", html))
    if lang_en == 0 or lang_zh == 0:
        errors.append("missing paired .lang-en / .lang-zh nodes")
    elif lang_en != lang_zh:
        errors.append(f"language node count mismatch: lang-en={lang_en}, lang-zh={lang_zh}")

    if "@media print" not in combined:
        errors.append("missing @media print block")
    if not re.search(r"print-color-adjust\s*:\s*exact", combined):
        errors.append("missing print-color-adjust: exact")
    if "#print-button" not in combined or not re.search(r"#print-button[\s\S]{0,240}display\s*:\s*none", combined):
        errors.append("print CSS must hide #print-button")
    if not re.search(r"\[hidden\][\s\S]{0,160}display\s*:\s*none", combined):
        errors.append("CSS must keep [hidden] language nodes hidden, including in print")
    if not re.search(r"color\s*:\s*#111827", combined, re.I):
        errors.append("print CSS should force dark text (#111827)")
    if not re.search(r"background\s*:\s*#fff", combined, re.I):
        errors.append("print CSS should include a contrast-safe background fallback (#fff)")
    if not re.search(r"text-decoration\s*:\s*underline", combined, re.I):
        errors.append("print CSS should underline links")

    return errors


def self_test() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        html = root / "index.html"
        css = root / "style.css"
        js = root / "showcase.js"
        html.write_text(
            """<!doctype html><html lang="zh-TW"><body>
<nav><div data-noprint>
<button id="lang-toggle" type="button" onclick="toggleLang()">English</button>
<button id="print-button" type="button" onclick="printShowcase()">
<span class="lang-zh">列印</span><span class="lang-en" hidden>Print</span>
</button></div></nav>
<h1><span class="lang-zh">標題</span><span class="lang-en" hidden>Headline</span></h1>
</body></html>""",
            encoding="utf-8",
        )
        css.write_text(
            """@media print {
html, body { color: #111827 !important; background: #fff !important; print-color-adjust: exact !important; }
#print-button { display: none !important; }
[hidden] { display: none !important; }
a { text-decoration: underline !important; }
}""",
            encoding="utf-8",
        )
        js.write_text("function printShowcase() { window.print(); }\n", encoding="utf-8")

        ok_errors = validate(html, css, js)
        if ok_errors:
            print("self-test valid fixture failed:", ok_errors, file=sys.stderr)
            return 1

        broken = root / "broken.html"
        broken.write_text("<html><body><p>No print</p></body></html>", encoding="utf-8")
        broken_errors = validate(broken, css, js)
        if not broken_errors:
            print("self-test broken fixture unexpectedly passed", file=sys.stderr)
            return 1

    print("self-test passed")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("html", nargs="?", help="generated docs/showcase/index.html")
    ap.add_argument("--css", help="generated showcase CSS path (default: sibling style.css)")
    ap.add_argument("--js", help="generated showcase JS path (default: sibling showcase.js)")
    ap.add_argument("--self-test", action="store_true", help="run built-in positive/negative checks")
    args = ap.parse_args()

    if args.self_test:
        return self_test()
    if not args.html:
        ap.error("provide an html path, or use --self-test")

    errors = validate(
        Path(args.html),
        Path(args.css) if args.css else None,
        Path(args.js) if args.js else None,
    )
    if errors:
        for err in errors:
            print(f"FAIL {err}", file=sys.stderr)
        return 1
    print(f"PASS showcase print contract: {args.html}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

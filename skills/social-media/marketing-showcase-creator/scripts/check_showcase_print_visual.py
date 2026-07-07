#!/usr/bin/env python3
"""Render a showcase in screen + print media and check print contrast.

This is a visual-regression helper for generated showcase HTML. It captures
screen and print-emulated screenshots for agent review, then performs a
computed-style WCAG contrast probe in print media so "white text on missing
background" fails before a human sends the PDF.

Requires Playwright for Python:
    python -m pip install playwright
    python -m playwright install chromium

Usage:
    python check_showcase_print_visual.py docs/showcase/index.html --out temp/showcase-visual
    python check_showcase_print_visual.py http://localhost:5173/showcase --out temp/showcase-visual
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path


CONTRAST_PROBE = r"""
({ maxSamples }) => {
  const parseRgb = (s) => {
    const m = String(s || '').match(/rgba?\(([^)]+)\)/);
    if (!m) return null;
    const p = m[1].split(',').map((x) => Number.parseFloat(x.trim()));
    if (p.length < 3 || p.some((x, i) => i < 3 && Number.isNaN(x))) return null;
    const a = p.length >= 4 && !Number.isNaN(p[3]) ? p[3] : 1;
    return { r: p[0], g: p[1], b: p[2], a };
  };
  const relLum = (c) => {
    const f = (v) => {
      v = v / 255;
      return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4);
    };
    return 0.2126 * f(c.r) + 0.7152 * f(c.g) + 0.0722 * f(c.b);
  };
  const ratio = (a, b) => {
    const l1 = relLum(a), l2 = relLum(b);
    const hi = Math.max(l1, l2), lo = Math.min(l1, l2);
    return (hi + 0.05) / (lo + 0.05);
  };
  const effectiveBg = (el) => {
    for (let cur = el; cur; cur = cur.parentElement) {
      const bg = parseRgb(getComputedStyle(cur).backgroundColor);
      if (bg && bg.a > 0.05) return bg;
    }
    return { r: 255, g: 255, b: 255, a: 1 };
  };
  const visible = (el) => {
    const cs = getComputedStyle(el);
    const r = el.getBoundingClientRect();
    return cs.visibility !== 'hidden' &&
      cs.display !== 'none' &&
      Number.parseFloat(cs.opacity || '1') > 0.05 &&
      r.width > 0 && r.height > 0;
  };
  const nodes = Array.from(document.querySelectorAll(
    'h1,h2,h3,h4,h5,h6,p,li,a,button,figcaption,blockquote,dt,dd,.stat,.card'
  ));
  const failures = [];
  const samples = [];
  for (const el of nodes) {
    const text = (el.innerText || el.textContent || '').replace(/\s+/g, ' ').trim();
    if (!text || !visible(el)) continue;
    const cs = getComputedStyle(el);
    const fg = parseRgb(cs.color);
    const bg = effectiveBg(el);
    if (!fg || !bg) continue;
    const fontSize = Number.parseFloat(cs.fontSize || '16');
    const weight = Number.parseInt(cs.fontWeight || '400', 10);
    const large = fontSize >= 24 || (fontSize >= 18.66 && weight >= 700);
    const min = large ? 3.0 : 4.5;
    const cr = ratio(fg, bg);
    const item = {
      selector: el.tagName.toLowerCase() + (el.id ? '#' + el.id : '') +
        (el.className && typeof el.className === 'string' ? '.' + el.className.trim().split(/\s+/).slice(0, 3).join('.') : ''),
      text: text.slice(0, 120),
      color: cs.color,
      backgroundColor: getComputedStyle(el).backgroundColor,
      effectiveBackground: `rgb(${Math.round(bg.r)}, ${Math.round(bg.g)}, ${Math.round(bg.b)})`,
      fontSize,
      fontWeight: cs.fontWeight,
      contrast: Number(cr.toFixed(2)),
      required: min,
    };
    samples.push(item);
    if (cr < min) failures.push(item);
    if (samples.length >= maxSamples) break;
  }
  const printButton = document.querySelector('#print-button');
  const printButtonHidden = printButton ? getComputedStyle(printButton).display === 'none' : null;
  const overflowX = document.documentElement.scrollWidth > document.documentElement.clientWidth;
  return { failures, samples, printButtonHidden, overflowX };
}
"""


def to_url(target: str) -> str:
    if target.startswith(("http://", "https://", "file://")):
        return target
    path = Path(target).resolve()
    return path.as_uri()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", help="HTML file path, file:// URL, or http(s) URL")
    parser.add_argument("--out", default="temp/showcase-print-visual",
                        help="output directory for screenshots/report")
    parser.add_argument("--viewports", default="390,768,1440",
                        help="comma-separated viewport widths")
    parser.add_argument("--max-samples", type=int, default=240,
                        help="max visible text nodes to inspect per viewport")
    args = parser.parse_args()

    try:
        from playwright.sync_api import sync_playwright
    except Exception:
        print("FAIL playwright is not installed; visual print regression unavailable", file=sys.stderr)
        print("Install with: python -m pip install playwright && python -m playwright install chromium", file=sys.stderr)
        return 3

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    url = to_url(args.target)
    widths = [int(x) for x in args.viewports.split(",") if x.strip()]
    report: dict[str, object] = {"target": args.target, "url": url, "viewports": {}}
    failed = False

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        for width in widths:
            page = browser.new_page(viewport={"width": width, "height": 900}, device_scale_factor=1)
            page.goto(url, wait_until="networkidle")
            page.screenshot(path=str(out / f"screen-{width}.png"), full_page=True)
            page.emulate_media(media="print")
            page.screenshot(path=str(out / f"print-{width}.png"), full_page=True)
            probe = page.evaluate(CONTRAST_PROBE, {"maxSamples": args.max_samples})
            report["viewports"][str(width)] = probe
            if probe.get("failures") or probe.get("overflowX") or probe.get("printButtonHidden") is False:
                failed = True
            page.close()
        browser.close()

    report_path = out / "report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    if failed:
        print(f"FAIL showcase print visual regression: {report_path}", file=sys.stderr)
        print("Review screen-*.png and print-*.png, fix CSS/HTML, then rerun.", file=sys.stderr)
        return 1
    print(f"PASS showcase print visual regression: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env node
// visual-review.mjs — turnkey frontend visual-review probe for Phase 3.
// Renders a URL at multiple viewports, screenshots (full + optional element),
// and runs a computed-CSS probe (overflow / box-model / token-relevant styles).
// Then Read the PNGs and judge; use the JSON metrics to corroborate findings.
//
// Usage:
//   node visual-review.mjs <url> [--out DIR] [--selector CSS] [--viewports 375,768,1440]
// Requires: playwright (`npm i -D playwright` or `npx playwright`). Honest-fail if absent.
//
// Output: <out>/review-<w>.png per viewport (+ <out>/element-<w>.png if --selector),
//         and <out>/metrics.json with per-viewport probes.

import { mkdirSync, writeFileSync } from "node:fs";
import { argv } from "node:process";

function arg(flag, def) {
  const i = argv.indexOf(flag);
  return i >= 0 && argv[i + 1] ? argv[i + 1] : def;
}

const url = argv[2];
if (!url || url.startsWith("--")) {
  console.error("usage: node visual-review.mjs <url> [--out DIR] [--selector CSS] [--viewports 375,768,1440]");
  process.exit(2);
}
const out = arg("--out", "./visual-review-out");
const selector = arg("--selector", null);
const viewports = arg("--viewports", "375,768,1440").split(",").map((n) => parseInt(n, 10));

let chromium;
try {
  ({ chromium } = await import("playwright"));
} catch {
  console.error("[visual-review] playwright not installed — Lane 2 (visual) unavailable.");
  console.error("  install: npm i -D playwright && npx playwright install chromium");
  console.error("  (Honest degradation: run Lane 1 static review only; record 'visual review unavailable'.)");
  process.exit(3);
}

mkdirSync(out, { recursive: true });
const browser = await chromium.launch();
const metrics = { url, viewports: {} };

for (const w of viewports) {
  const ctx = await browser.newContext({ viewport: { width: w, height: 900 }, deviceScaleFactor: 2 });
  const page = await ctx.newPage();
  try {
    await page.goto(url, { waitUntil: "networkidle", timeout: 30000 });
  } catch (e) {
    metrics.viewports[w] = { error: String(e) };
    await ctx.close();
    continue;
  }
  await page.screenshot({ path: `${out}/review-${w}.png`, fullPage: true });
  if (selector) {
    const el = await page.$(selector);
    if (el) await el.screenshot({ path: `${out}/element-${w}.png` });
  }
  // computed-CSS probe — corroborate layout/contrast/brand findings with measurements
  const probe = await page.evaluate((sel) => {
    const de = document.documentElement;
    const read = (q) => {
      const el = document.querySelector(q);
      if (!el) return null;
      const cs = getComputedStyle(el);
      const r = el.getBoundingClientRect();
      return { color: cs.color, bg: cs.backgroundColor, fontFamily: cs.fontFamily,
               fontSize: cs.fontSize, fontWeight: cs.fontWeight, borderRadius: cs.borderRadius,
               box: { w: Math.round(r.width), h: Math.round(r.height) } };
    };
    return {
      horizontalOverflow: de.scrollWidth > de.clientWidth,     //破版訊號
      scrollWidth: de.scrollWidth, clientWidth: de.clientWidth,
      body: read("body"),
      h1: read("h1"),
      cta: read("button, .btn, [role=button], a.button"),
      element: sel ? read(sel) : null,
    };
  }, selector);
  metrics.viewports[w] = probe;
  await ctx.close();
}
await browser.close();

writeFileSync(`${out}/metrics.json`, JSON.stringify(metrics, null, 2));
console.log(`[visual-review] wrote screenshots + ${out}/metrics.json for viewports ${viewports.join(", ")}`);
console.log("Next: Read each review-<w>.png and judge layout/hierarchy/contrast/brand/anti-slop;");
console.log("use metrics.json (overflow, computed sizes/colors) to corroborate findings vs design-system tokens.");

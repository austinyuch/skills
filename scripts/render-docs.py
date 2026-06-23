#!/usr/bin/env python3
"""Render markdown docs to static, browsable HTML twins (markdown-first).

Markdown stays the single source of truth. Run this after editing any listed doc:

    python3 scripts/render-docs.py

Each `<doc>.md` gets a `<doc>.html` sibling using the project's dark theme. Relative
links to other rendered docs are rewritten `.md` -> `.html` so the twins link to twins.
Fenced ```mermaid blocks are rendered client-side via mermaid (CDN) on pages that need it.
No server required — the twins are plain static HTML (work over file:// and GitHub Pages).
"""
import html
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Docs that get an HTML twin. Paths are repo-root-relative.
DOCS = [
    "docs/agentic-delivery-methodology.md",
    "docs/methodology-diagram.md",
    "docs/README.md",
    "CREDITS.md",
    "AGENTS.md",
    "README.md",
    "README.zh-TW.md",
    "skills/spec-master/README.md",
    "skills/code-review/README.md",
]
# basenames (without .md) whose twin exists -> safe to rewrite .md links to .html
TWIN_BASENAMES = {os.path.splitext(os.path.basename(d))[0] for d in DOCS}

TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} · aclab Skills</title>
<!-- Generated from {src} by scripts/render-docs.py — edit the markdown, then re-run. -->
<style>
:root{{--bg:#07111e;--line:#27344d;--text:#eef4ff;--muted:#b7c4dc;--blue:#4ea1ff;--teal:#43d6c2;--max:880px}}
*{{box-sizing:border-box}}
body{{margin:0;background:radial-gradient(circle at top left,rgba(78,161,255,.14),transparent 32%),radial-gradient(circle at top right,rgba(67,214,194,.12),transparent 28%),var(--bg);color:var(--text);font-family:Inter,ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif;line-height:1.65}}
a{{color:var(--blue)}}
.bar{{position:sticky;top:0;z-index:5;display:flex;gap:12px;align-items:center;justify-content:space-between;padding:12px 20px;background:rgba(7,17,30,.86);backdrop-filter:blur(10px);border-bottom:1px solid var(--line)}}
.bar .crumb{{color:var(--muted);font-size:.9rem;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}
.bar a{{text-decoration:none;border:1px solid rgba(255,255,255,.14);padding:6px 12px;border-radius:999px;font-size:.85rem;white-space:nowrap}}
main{{max-width:var(--max);margin:0 auto;padding:32px 22px 80px}}
h1,h2,h3,h4{{line-height:1.25;margin:1.6em 0 .5em}}
h1{{font-size:2rem;margin-top:.2em}}h2{{font-size:1.5rem;border-bottom:1px solid var(--line);padding-bottom:.3em}}h3{{font-size:1.2rem}}
p,li{{color:#dbe4f3}}
blockquote{{margin:1em 0;padding:.4em 1em;border-left:4px solid var(--blue);background:rgba(78,161,255,.07);border-radius:0 8px 8px 0;color:var(--muted)}}
code{{background:rgba(78,161,255,.12);border:1px solid rgba(78,161,255,.18);padding:1px 6px;border-radius:6px;font-size:.86em;color:#dceaff}}
pre{{background:#0b1626;border:1px solid var(--line);border-radius:10px;padding:14px 16px;overflow:auto}}
pre code{{background:none;border:0;padding:0;color:#cfe0f5}}
table{{width:100%;border-collapse:collapse;margin:1.2em 0;font-size:.95rem}}
th,td{{padding:10px 11px;border:1px solid var(--line);text-align:left;vertical-align:top}}
th{{background:rgba(255,255,255,.04);color:#dfe8ff}}
td{{color:var(--muted)}}
hr{{border:0;border-top:1px solid var(--line);margin:2em 0}}
img{{max-width:100%}}
.mermaid{{background:#0b1626;border:1px solid var(--line);border-radius:10px;padding:16px;margin:1.2em 0;text-align:center}}
</style>
</head>
<body>
<div class="bar">
  <span class="crumb">{src}</span>
  <span style="display:flex;gap:8px">
    <a href="{raw}">Raw .md</a><a href="{home}">Methodology →</a>
  </span>
</div>
<main>
{body}
</main>
{mermaid}
</body>
</html>
"""

MERMAID = """<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<script>mermaid.initialize({startOnLoad:true,theme:'dark',securityLevel:'loose'});</script>
"""


def esc(s):
    return html.escape(s, quote=False)


def inline(text):
    """Render inline markdown on already-block-stripped text."""
    # protect inline code spans
    codes = []
    def stash(m):
        codes.append(m.group(1))
        return f"\x00{len(codes)-1}\x00"
    text = re.sub(r"`([^`]+)`", stash, text)
    text = esc(text)
    # links [t](u) — rewrite relative .md -> .html when a twin exists
    def link(m):
        t, u = m.group(1), m.group(2)
        if not re.match(r"^[a-z]+://|^#|^mailto:", u):
            base = os.path.splitext(os.path.basename(u.split('#')[0]))[0]
            if u.split('#')[0].endswith(".md") and base in TWIN_BASENAMES:
                frag = u[len(u.split('#')[0]):]
                u = u[:-len('.md') - len(frag)] + ".html" + frag if frag else u[:-3] + ".html"
        return f'<a href="{u}">{t}</a>'
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", link, text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    # italics: *text* with non-space inner edges (handles CJK-adjacent emphasis); bold already consumed
    text = re.sub(r"\*(\S(?:[^*\n]*\S)?)\*", r"<em>\1</em>", text)
    text = re.sub(r"\x00(\d+)\x00", lambda m: f"<code>{esc(codes[int(m.group(1))])}</code>", text)
    return text


def render(md):
    lines = md.split("\n")
    out, i, n, has_mermaid = [], 0, len(lines), False
    while i < n:
        ln = lines[i]
        # fenced code
        m = re.match(r"^```(\w*)\s*$", ln)
        if m:
            lang, buf, i = m.group(1), [], i + 1
            while i < n and not re.match(r"^```\s*$", lines[i]):
                buf.append(lines[i]); i += 1
            i += 1
            if lang == "mermaid":
                has_mermaid = True
                out.append(f'<div class="mermaid">{esc(chr(10).join(buf))}</div>')
            else:
                out.append(f"<pre><code>{esc(chr(10).join(buf))}</code></pre>")
            continue
        # table: header | --- | rows
        if "|" in ln and i + 1 < n and re.match(r"^\s*\|?[\s:|-]*-[\s:|-]*\|?\s*$", lines[i + 1]) and "|" in lines[i + 1]:
            def cells(row):
                row = row.strip().strip("|")
                return [c.strip() for c in row.split("|")]
            head = cells(ln); i += 2
            rows = []
            while i < n and "|" in lines[i] and lines[i].strip():
                rows.append(cells(lines[i])); i += 1
            t = ["<table><thead><tr>"] + [f"<th>{inline(c)}</th>" for c in head] + ["</tr></thead><tbody>"]
            for r in rows:
                t.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>")
            t.append("</tbody></table>")
            out.append("".join(t)); continue
        # header
        m = re.match(r"^(#{1,6})\s+(.*)$", ln)
        if m:
            lvl = len(m.group(1)); out.append(f"<h{lvl}>{inline(m.group(2))}</h{lvl}>"); i += 1; continue
        # hr
        if re.match(r"^(-{3,}|\*{3,}|_{3,})\s*$", ln):
            out.append("<hr>"); i += 1; continue
        # blockquote
        if ln.startswith(">"):
            buf = []
            while i < n and lines[i].startswith(">"):
                buf.append(lines[i][1:].lstrip()); i += 1
            out.append(f"<blockquote>{inline(' '.join(b for b in buf if b))}</blockquote>"); continue
        # list (one level; - * or ordered)
        if re.match(r"^\s*([-*]|\d+\.)\s+", ln):
            ordered = bool(re.match(r"^\s*\d+\.\s+", ln))
            tag = "ol" if ordered else "ul"; items = []
            while i < n and re.match(r"^\s*([-*]|\d+\.)\s+", lines[i]):
                items.append(re.sub(r"^\s*([-*]|\d+\.)\s+", "", lines[i])); i += 1
            out.append(f"<{tag}>" + "".join(f"<li>{inline(it)}</li>" for it in items) + f"</{tag}>"); continue
        # raw html line (e.g. <a name="...">) — passthrough
        if ln.lstrip().startswith("<"):
            out.append(ln); i += 1; continue
        # blank
        if not ln.strip():
            i += 1; continue
        # paragraph (gather until blank / block start)
        buf = []
        while i < n and lines[i].strip() and not re.match(r"^(#{1,6}\s|```|>|\s*([-*]|\d+\.)\s|-{3,}\s*$)", lines[i]) and not lines[i].lstrip().startswith("<"):
            buf.append(lines[i]); i += 1
        out.append(f"<p>{inline(' '.join(buf))}</p>")
    return "\n".join(out), has_mermaid


def main():
    home_for = lambda src: ("../" * src.count("/")) + "methodology.html"
    made = 0
    for rel in DOCS:
        path = os.path.join(REPO, rel)
        if not os.path.exists(path):
            print(f"  skip (missing): {rel}"); continue
        md = open(path, encoding="utf-8").read()
        body, has_mermaid = render(md)
        title = os.path.splitext(os.path.basename(rel))[0]
        out_path = os.path.splitext(path)[0] + ".html"
        htmlout = TEMPLATE.format(
            title=title, src=rel, raw=os.path.basename(rel),
            home=home_for(rel), body=body, mermaid=(MERMAID if has_mermaid else ""))
        open(out_path, "w", encoding="utf-8").write(htmlout)
        print(f"  ✅ {rel} -> {os.path.relpath(out_path, REPO)}{'  (mermaid)' if has_mermaid else ''}")
        made += 1
    print(f"Rendered {made} HTML twin(s).")


if __name__ == "__main__":
    main()

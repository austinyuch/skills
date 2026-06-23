# docs/ — methodology & family briefs (markdown-first)

This folder is the **source of truth** for the project's explanatory material. The rule here is
**markdown-first**: write/update the markdown, then (re)generate the HTML landing page from it.
Never edit an HTML page as the primary source — its markdown counterpart is canonical.

> 本資料夾是專案說明文件的**單一事實來源**。規則是 **markdown-first**：先寫／改 markdown，再由它
> 產生 HTML landing page。HTML 不是來源，對應的 markdown 才是。

## Generation order

```
markdown (source of truth)  ──►  *.html (generated, browsable twin)
```

Every listed markdown doc has a static **`.html` twin** next to it (e.g.
`agentic-delivery-methodology.md` → `agentic-delivery-methodology.html`). The twins are plain static
HTML — browsable directly on GitHub Pages **and** over `file://`, with no server and no fetch. Mermaid
diagrams render via a CDN script only on pages that contain them.

Regenerate the twins after editing any markdown:

```bash
python3 scripts/render-docs.py
```

When content changes:
1. Edit the markdown source (it is the source of truth).
2. Run `scripts/render-docs.py` to regenerate the `.html` twins.
3. For the hand-built bilingual landing pages (`methodology.html`, the family `index.html`), keep both
   languages in sync (each `data-en` needs a matching `data-zh`).

> The landing pages link to the `.html` twins (not the raw `.md`) so a browser never lands on raw
> markdown. Each twin's top bar still offers a **Raw .md** link back to the source.

## Source ↔ rendered map

| Markdown source (canonical) | Rendered HTML (generated) | Topic |
|---|---|---|
| [`agentic-delivery-methodology.md`](agentic-delivery-methodology.md) | [`../methodology.html`](../methodology.html) | The Spec Master Method (whole 14-skill methodology) |
| [`methodology-diagram.md`](methodology-diagram.md) | *(rendered inline by GitHub)* | Handoff / evidence-flow / practice-map diagrams |
| [`../skills/spec-master/README.md`](../skills/spec-master/README.md) | [`../skills/spec-master/index.html`](../skills/spec-master/index.html) | Spec Master + Spec-Driven Development (merged family brief) |
| [`../skills/code-review/README.md`](../skills/code-review/README.md) | [`../skills/code-review/index.html`](../skills/code-review/index.html) | Code Review family (deep brief) |

## Conventions

- **Bilingual HTML.** Every rendered page carries an EN/繁中 toggle; markdown sources are
  English-primary with a 繁中 section or bilingual tables where it helps.
- **One brief per family.** The Spec Master router (`spec-master`) and the lifecycle
  (`spec-driven-development`) share **one** merged brief — do not split them again.
- **Attribution travels with the doc.** External influences are credited in
  [`../CREDITS.md`](../CREDITS.md) and inline where used.

# FEATURES_HTML Contract

`{{FEATURES_HTML}}` 必須渲染為一組 `feature-card`，每張卡片至少包含以下結構與順序：

共用 evidence 欄位定義請先參考：`../../../docs/EVIDENCE_METADATA_CONTRACT.md`

```html
<article class="feature-card">
  <div class="feature-screenshot">...</div>
  <div class="feature-body">
    <span class="feature-tag">...</span>
    <div class="feature-evidence">
      <span class="evidence-badge live|hybrid|mock|na">...</span>
      <span class="evidence-badge live|hybrid|mock|na">...</span>
    </div>
    <h3>...</h3>
    <p>...</p>
    <div class="feature-disclaimer">...</div>
  </div>
</article>
```

## Required fields

每張卡片至少要可見呈現：

- `Evidence Source`
- `Coverage Tier`
- `Readiness State`

若不是 `live_screenshot`，還必須可見呈現：

- `Fallback Reason`
- 至少一個 canonical warning code（例如 `DEMO_NOT_ASSESSED`、`MOCK_DOMINANT_EVIDENCE`、`ARTIFACT_HONESTY_GAP`）

若畫面依賴 auth fixture / storageState / preset session，必須可見呈現：

- `AUTH_FIXTURE_COUPLING`

## Badge mapping

### Evidence Source → badge class

| Evidence Source | Badge class |
| --- | --- |
| `live_screenshot` | `evidence-badge live` |
| `fixture-backed screenshot` | `evidence-badge mock` |
| `css_illustration` | `evidence-badge mock` |
| `static_placeholder` | `evidence-badge na` |

### Coverage Tier → badge class

| Coverage Tier | Badge class |
| --- | --- |
| `full-integration` | `evidence-badge live` |
| `hybrid` | `evidence-badge hybrid` |
| `mock-heavy` | `evidence-badge mock` |
| `not_assessed` | `evidence-badge na` |

### Readiness State → badge class

| Readiness State | Badge class |
| --- | --- |
| `PASS` | `evidence-badge live` |
| `CONDITIONAL` | `evidence-badge hybrid` |
| `FAIL` | `evidence-badge mock` |
| `not_assessed` | `evidence-badge na` |

## Disclaimer rules

- `feature-disclaimer` 用來放置 canonical warning codes、fallback reason、以及 claim-cap 說明。
- 若 evidence 為 `live_screenshot` 且 `Readiness State = PASS`，`feature-disclaimer` 可省略或僅顯示簡短 `Source Ref`。
- 若 evidence 不是 `live_screenshot`、readiness 不是 `PASS`、或存在 warning code，必須顯示 `feature-disclaimer`。

## Source Ref visibility

- `Source Ref` 可以用較低調的方式顯示在 `feature-disclaimer` 末尾，但不可完全隱藏於生成過程。
- 建議格式：`Source Ref: .agents/specs/foo/review.md#live-demo-readiness`

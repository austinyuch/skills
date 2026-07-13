# TESTS.md Schema Guidance

本文件定義 `test-registry-manager` 期望的最小欄位集合。

## 1. Folder-level `TESTS.md`

folder-level `TESTS.md` 是 row-level authority。

建議最小欄位：

| Field | Purpose |
|---|---|
| `Test ID` | 穩定識別碼，跨 rename / move 仍可對照 |
| `Test Artifact` | test file / suite / scenario path |
| `Test Type` | unit / integration / e2e / smoke / contract / security 等 |
| `Code Surface` | route / component / module / API / CLI / workflow |
| `Primary Source Under Test` | 實際被驗證的 function / class / page / endpoint |
| `Task / Spec Trace` | task ID 或 spec 名稱 |
| `Requirement / AC Trace` | `REQ-*` 與 `AC` 映射 |
| `Trace Status` | explicit / partial / unmapped / stale / obsolete |
| `Execution Status` | pass / fail / not_run / blocked / conditional |
| `Canonical Command` | 官方執行指令 |
| `Evidence Ref` | report / log / CI / screenshot / artifact path |
| `Owner` | team / package / maintainer |
| `Notes / Risk` | caveat、mock-heavy、known gap |

## 2. Workspace `.agents/specs/TESTS.md`

workspace `TESTS.md` 是 derived rollup。

建議最小欄位：

| Field | Purpose |
|---|---|
| `Spec / Subsystem / Package` | rollup 單位 |
| `Catalog Ref` | 指向 folder-level `TESTS.md` |
| `Canonical Commands` | 該 scope 的主要執行入口 |
| `Coverage / Trace Summary` | complete / partial / gap / not_assessed |
| `Evidence Summary` | 最新高階 evidence pointer |
| `Cross-Spec Dependency` | cross-spec / integration 風險摘要 |
| `Warnings` | duplicate ID / missing owner / stale evidence 等 |

## 3. Mapping rules

- 無法可靠映射時，標 `unmapped` 或 `unmapped_to_spec`
- 不可把 `SPECS.md` / `RTM.md` 當成 row-level trace truth
- `review.md` 的 verdict 可被引用，但不可在 `TESTS.md` 中重寫成新的 authority

## 4. Legacy compatibility aliases

`test-registry-manager` 必須先 normalize legacy rows，再提出 rewrite 建議。下列 aliases 應被視為相容輸入：

| Normalized Field | Accepted Aliases |
|---|---|
| `Test ID` | `Test ID`, `ID`, `Case ID` |
| `Test Type` | `Test Type`, `Type`, `Type Tag`, `Category` |
| `Canonical Command` | `Canonical Command`, `Command`, `Run`, `How to Run` |
| `Requirement / AC Trace` | `Requirement / AC Trace`, `Req / Trace`, `Req Trace`, `Requirement Trace`, `AC Trace` |
| `Task / Spec Trace` | `Task / Spec Trace`, `Task Trace`, `Spec Trace` |
| `Evidence Ref` | `Evidence Ref`, `Evidence`, `Evidence Summary`, `Latest Evidence` |
| `Execution Status` | `Execution Status`, `Execution`, `Status`, `Result` |
| `Owner` | `Owner`, `Maintainer`, `Team` |

Alias recognition does not mean all legacy rows are complete. Missing command, owner, trace, or evidence should
be reported as advisory gaps, not fabricated.

## 5. Safe update mechanism

Preferred behavior:

1. Read legacy rows into a normalized view.
2. Emit a recommendation plan with per-row actions: `recommended`, `applied`, `blocked`, `not_applicable`.
3. Apply changes only when the caller explicitly asks for writeback or the target workflow authorizes it.
4. Preserve user-authored prose and table ordering.
5. Use managed marker blocks only for generated summary sections, not for whole-file ownership.
6. Create a backup before automated high-risk rewrites.

Fresh repositories may use the suggested schema directly. Legacy repositories should receive compatibility
diagnostics and incremental migration guidance.

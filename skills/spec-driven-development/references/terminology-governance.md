# 術語治理 (Terminology Governance)

本檔是 spec-driven-development **所有「術語 / 詞彙」的單一查詢入口**。當你需要一個 canonical 名稱、想標一個風險訊號、或不確定某個詞該寫在哪、由誰管、能不能改時，先看這裡。

SDD 有**兩種 vocabulary**，由本檔統一治理。它們用途、scope、生命週期不同，但同屬一套治理框架——**不互相覆寫、各司其職**：

| 維度 | Kind 1：Risk / Warning-Code Taxonomy | Kind 2：Per-Spec Domain Glossary（Ubiquitous Language）+ ADR |
| --- | --- | --- |
| 內容 | 固定的 readiness / review 風險代碼 enum（如 `MOCK_DOMINANT_EVIDENCE`） | 某個 feature/spec 的業務/領域術語共識（如「account 指 Customer 還是 User」） |
| Scope | 跨 skill、跨 spec | per-spec |
| 穩定性 | 穩定、controlled、慎增刪 | 隨 feature 成長、可演進 |
| Source of Truth | `../../docs/DEMO_RISK_WARNING_TAXONOMY.md`（repo 共用） | `design.md` 的 glossary 段落，或 spec-local `CONTEXT.md` |
| 治理規則 | 不引入新 code，除非現有 code 無法覆蓋 | opinionated 選一詞、被拒詞列 `_Avoid_`；lazy 建立 |
| 用途 | 標記 false-green / over-state / demo 風險 | 讓需求、設計、契約、測試對同一概念用同一個詞 |

> **為什麼放在一起治理**：兩者都是「對某個概念用哪個 canonical 表述」的決定。把它們放同一個入口，agent 才不會（a）發明新的 risk code 去描述本該用既有 taxonomy 的風險，或（b）把 per-spec 業務詞硬塞進跨 skill 的 risk enum。需要術語時，先判斷它屬於哪一種，再到對應 SoT 操作。

---

## Kind 1：Risk / Warning-Code Taxonomy

- **SoT**：`../../docs/DEMO_RISK_WARNING_TAXONOMY.md`（跨 skill 共用對照表）。本檔不複製 code 清單，避免雙份漂移；要用 code 一律以該檔為準。
- **何時用**：requirements / design / tasks / review 任一階段，一旦能識別 false-green、over-state、mock-dominant evidence、auth fixture coupling、cross-spec demo dependency、artifact honesty gap、evidence staleness，就用既有 code 保守降級，不要等到 review 才補標。
- **治理紀律**：
  - 不引入新 code，除非現有 code 確實無法覆蓋（依 AGENTS.md / repo taxonomy 規則）。
  - 各 skill 只能在自己的責任邊界內使用：SDD 是 authoritative review gate（可輸出 `PASS/CONDITIONAL/FAIL`）；registry / project-review 只能輸出 risk signal / claim cap，不得自行發明 readiness verdict。
  - 早期階段揭露這些 code 時，必須表述為 **pre-review caution summary**，不是 readiness verdict。

## Kind 2：Per-Spec Domain Glossary（Ubiquitous Language）+ ADR

與 contract-first 互補：**contract 管「介面/資料的機器定義」，glossary 管「語彙的人類共識」**。兩者都不是 Kind 1 的 risk enum。

- **Ubiquitous language（詞彙表）**：對模糊 / 重疊 / 過載的術語主動 challenge，挑一個 canonical 詞（例「account 指 Customer 還是 User？兩者不同」）。**要 opinionated**：選定一詞，被拒同義詞列在 `_Avoid_`。只收此 spec *特有*的術語，一般程式概念不收；只放定義、不放實作細節。
- **何時建立（lazy）**：第一個術語被釐清時才建立 glossary 段落（放 `design.md` 或 spec-local `CONTEXT.md`）。多情境 repo 可用根層 `CONTEXT-MAP.md` 指向各情境的 glossary。
- **In-session 動作**：對照詞彙表挑矛盾、用具體 edge-case 情境壓測概念邊界、與程式碼交叉驗證、當下就更新詞彙表（不要批次累積）。
- **ADR（Architecture Decision Record）謹慎使用**：只有**三條件全中**才寫——(1) 難以回退、(2) 無背景會讓人意外、(3) 是有真實替代方案的取捨結果。ADR 可只有一段；價值在記錄「做了這個決定 + 為什麼」。design 階段被排除的實作方案理由，常是好的 ADR 素材。

---

## 與其他治理 artifact 的關係

- glossary / ADR 是 **spec-local** 設計共識，不是 `SPECS.md` / `RTM.md` / `TESTS.md` 的 registry 內容；不得把詞彙表當 registry，也不得讓 registry 反向定義業務術語。
- warning-code taxonomy 的 verdict authority 仍在 `review.md`；taxonomy 只提供標準化措辭，不取代 readiness 判定。

## Attribution

Kind 2 的 ubiquitous-language 詞彙表與 ADR 三條件改編自 [mattpocock/skills](https://github.com/mattpocock/skills) 的 `domain-modeling` skill，MIT License, Copyright (c) 2026 Matt Pocock。Kind 1 為本 repo 既有的跨 skill 共用 taxonomy。

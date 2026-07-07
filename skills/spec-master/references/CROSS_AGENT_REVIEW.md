# Cross-Agent Independent Review（`xreview`）

本文件定義在 SDD **Phase 5 Review** 中，如何用 `cross-agent-review`（`xreview`）讓**不同 model family** 的 agent 對本輪工作做一次獨立複核，避免「作者自己審自己」的 single-model blind spot。

> **一句話**：Phase 5 的 `05-review.md` 已要求 review 不能只靠作者自述完成（Agentic Review Trigger Scope）。`xreview` 正是把「獨立性」變成真實機制的工具——它由 model-card registry **自動偵測**作者身分並挑一個與作者**不同 family** 的 reviewer，跑 review↔revise consensus loop，並在無跨 family 可用時**誠實降級**，絕不無聲自審。
>
> **不要寫死配對**：作者可以是 `claude` / `codex` / `opencode` / `kiro` / `antigravity` 任一（全部有可用的 trigger installer）；reviewer 是「registry 依 SOTA/可用性選出的、與作者不同 family 的那一個」。**Claude↔Codex 只是 default preference，不是硬編碼規則**——SDD 不得假設固定的作者/reviewer 配對，一律讓 `xreview` 自行偵測與選擇。

## 1. 定位與 Authority 邊界

- `xreview` 是 Phase 5 的 **capability-gated required-input（非 verdict）**，與 `code-review` 家族其他成員同一層級。
- 它**不自己審程式碼**——它把 `code-review` skill dispatch 給另一個 family 的 agent 去跑。payload 仍是 `code-review` 的 review contract。
- **`review.md` 仍是最終 readiness authority**。`xreview` 的 findings 只是併入 review 的輸入；跨 model 複核意見與作者自評衝突時，由人／`review.md` 裁決，不是由 reviewer 自動改判。
- 預設 **advisory、non-blocking**，不阻塞 host session（除非明確設 `on_findings: blocking`）。

## 2. 兩層 Capability Gate（沿用 Global Constraint #14）

與其他 `code-review` 家族成員一樣，分清「skill/binary 是否可用」與「依賴是否就緒」：

1. **skill / binary 是否可用**：`cross-agent-review` skill 存在（workspace / global skill home），且能解析到對應 OS/arch 的 `xreview-<os>-<arch>` binary。皆無 → 沿用既有內建 Phase 5 評估，於 `review.md` 記 `cross-agent-review unavailable`。
2. **依賴是否就緒（是否有真正不同 family 的 reviewer + 憑證）**：這是 `xreview` 特有的關鍵 gate。reviewer **必定**是與作者不同的 family（由 model-card registry 在 model 層決定），且需要可用的 transport／key：
   - **Direct LLM-API（首選）**：`ANTHROPIC_API_KEY` / `OPENAI_API_KEY` / `GEMINI_API_KEY` / `DEEPSEEK_API_KEY` 任一真實 provider key；或 opencode Zen/Go（`OPENCODE_API_KEY`）作為 portable 訂閱 fallback。
   - **exec（agent CLI）**：僅限 OAuth-friendly、乾淨退出的 CLI（主要是 **codex**）。
   - **ToS 注意**：**Claude Code 訂閱 CLI 不得**被當成自動化 reviewer 驅動；Anthropic-family 的複核需要 `ANTHROPIC_API_KEY`（作為你自己的 author session 則沒問題）。Kiro / Antigravity 為 AWS/GCP-OAuth 綁定、無 portable key，其 family 需經真實 key（如 google→Gemini API）或 opencode Zen 服務。
   - 若 skill 可用但**沒有任何跨 family reviewer 憑證** → `dependency not configured`：honest no-op、不阻塞，於 `review.md` 記 `cross-agent-review: no cross-family reviewer configured`（與 `unavailable` 分開記，因補救動作不同：前者要裝/發布 skill，後者要設定 key）。

## 3. 誠實降級（Honest Degradation）

`xreview` 每次執行都會 resolve 到**恰好一個** outcome，且都誠實、都不阻塞 host session：

`consensus-reached` · `max-rounds-exhausted` · `single-round` · `skipped-already-reviewed` · `skipped-empty-scope` · `skipped-reentrant` · `same-family-degraded` · `backend-unavailable` · `dispatch-timeout` · `reviewer-unavailable-midloop`

- **`same-family-degraded`** 是關鍵誠實訊號：當只有同 family model 可用時，它明說降級，**不會**偽裝成獨立複核。Phase 5 遇到此 outcome 時，不得把它當成「已獲得跨 model 獨立確認」。
- records 落在 `~/.xreview/records/<repo-id>.jsonl`；`reviewer.provider`（如 `gemini-api`、`opencode-zen`、`exec:codex`）顯示實際用的 transport。

## 4. Phase 5 執行方式（導引到 `cross-agent-review` skill）

**SDD 不自行 re-implement xreview 機制。** 這條 review lane 的 owner 是 `cross-agent-review` skill——由它負責 binary 解析（`scripts/xreview-bin.sh` 依 host OS/arch）、作者身分偵測、跨 family reviewer 選擇、consensus loop、與 review-record 寫入。SDD 的職責只有「何時該觸發、傳入什麼 scope、把結果寫回 `review.md`」。

1. **判定可用性**（上方兩層 gate）。可用且有跨 family reviewer 憑證 → 執行為 required input。
2. **導引到 `cross-agent-review` skill**：讓該 skill 對當前 git working-tree 變更跑一次獨立複核。**不要**在 SDD 這邊 hard-code `--host-agent` 值或固定的作者/reviewer 配對——作者身分與跨 family reviewer 一律由該 skill 自行偵測與選擇（作者可為 claude / codex / opencode / kiro / antigravity 任一）。實際命令、config 覆寫（切換 reviewer、關 consensus、`on_findings: blocking`）、outcome 語意皆以 `cross-agent-review` skill 的 SKILL.md 為準。
3. **把 findings 併入** Phase 5 的「程式碼品質評估」，並在 `review.md` 記錄 outcome / reviewer family / provider（見 §5）。
4. **衝突處理**：跨 model reviewer 的意見與作者自評衝突時，由人／`review.md` 裁決；不得自動採信任一方。

> 若使用者要求「換另一個 model 複核」「設定/切換哪個 agent 來 review」「安裝自動複核 hook」「更新 SOTA model-card」等，這些都**屬於 `cross-agent-review` skill 的職責**，SDD 應把它們導引過去，而不是在本 workflow 內另行實作。

## 5. `review.md` 應記錄的 Cross-Agent Review Summary

- **Outcome**：上方 outcome 之一（尤其要如實標 `same-family-degraded` / `no cross-family reviewer configured` / `unavailable`）。
- **Reviewer**：reviewer family 與 `provider`（如 `codex / exec:codex`、`gemini-api`）。
- **Independence 判定**：本次複核是否真的來自不同 family（是 → 可作為獨立確認；否 → 只能當作額外一輪 self-consistency，不得宣稱獨立）。
- **Folded findings**：跨 model reviewer 提出、且併入本輪 review 的關鍵 findings 與其 disposition。
- 三態不可混記：`ran (cross-family)` / `dependency-not-configured` / `unavailable`，避免讓 review 看起來覆蓋了實際未跑的獨立複核（另一種 false-green）。

## 6. Optional：Auto-Trigger Stop-Hook（環境設定，非 SDD 內建步驟）

`xreview install --agent <claude|codex|opencode|kiro|antigravity>` 可安裝一個 stop/idle hook，讓作者 agent 一結束回合就自動觸發跨 family 複核。這屬於**使用者的全域 agent 環境設定**，SDD 只**建議**、不代為安裝，也不把「已安裝 hook」當成 Phase 5 的前置條件——即使沒有 hook，Phase 5 仍應在可用時主動導引到 `cross-agent-review` skill 跑一次 one-off 獨立複核。

## 7. Forbidden Anti-Patterns

- 把 `xreview` 的 findings 當成 verdict、直接覆蓋 `review.md`
- 在 `same-family-degraded` / `unavailable` 時，仍宣稱「已通過跨 model 獨立複核」
- 用訂閱制 Claude Code CLI 當自動化 reviewer（ToS 違規）
- 因 `xreview` 暫不可用就阻塞 host session（它永遠 non-blocking）

## 8. Why

💡 **原因 (WHY)**：作者模型審自己的產出會漏掉自己的 blind spot；Phase 5 早就要求「不能只靠作者自述」，但先前缺一個真正保證獨立性的機制。`xreview` 用**不同 model family** dispatch `code-review`，把獨立性變成可執行、可記錄的步驟。把它設計成 capability-gated required-input（可用就跑、寫回 `review.md`）、advisory non-blocking、且**誠實降級**，能在提升複核可信度的同時，避免把降級偽裝成獨立、也不讓外部 reviewer 篡奪 `review.md` 的 readiness authority。

# NEXT_STEPS.md Template

`{workspace}/.agents/specs/NEXT_STEPS.md` 是一份 **跨 spec、滾動式、高階摘要** 的 operational memo。

它的目的不是取代 `SPECS.md`、spec 文件、或完整 CR，而是讓 Agent 在 **中斷後恢復、跨 spec 影響評估、change request 推進、以及換 session 交棒** 時，能快速找到「現在在哪裡、下一步做什麼」。

## 與其他文件的分工

- `SPECS.md`：穩定治理登錄表。記錄 spec 狀態、`Depends On`、`Impacts`、`Open Change Requests`、external contract metadata。
- `NEXT_STEPS.md`：滾動中的 operational state。記錄目前活躍 spec、最新驗證狀態、下一步、阻塞、恢復提示，以及 external execution / handoff 的當前操作摘要。
- `ISSUE_LOG.md`：unresolved improvement holding surface。它持有尚未 owner-resolved 的 issue，不應被複製進 `NEXT_STEPS.md`；`NEXT_STEPS.md` 最多只放 issue ID / pointer 與下一個 owner-resolution action。
- `change-requests/{cr-id}.md`：完整 CR overlay。
- `.agents/specs/{spec-directory}/*.md`：正式 spec 基線文件。
- `RTM.md`：requirement traceability rollup。它可以作為 resume 時的覆蓋視圖，但不可取代 active spec artifacts。

## 何時讀取

1. 新 session 或 resumed session 一開始
2. 讀完 `SPECS.md` 後，決定要展開哪些 spec 文件之前
3. 準備執行 re-sync gate、impact triage、或跨 spec 變更評估之前
4. 準備繼續被中斷的實作 / review / optimization 之前

## 何時更新

1. requirements 階段完成工作分類（`continue active spec` / `new spec` / `retrofit` / `CR against completed spec` / `issue-log candidate`）時
2. `Open Change Requests` / impact triage / re-sync 結果改變時
3. 任一 phase 準備暫停、等待人類確認、等待外部資訊、或結束 session 時
4. 發生 blocker、circuit breaker、或需要 handoff 到 new session 時
5. issue-log item 被 folded / promoted / closed，且下一步需要回到正式 SDD lane 時
6. review / optimization 後需要標示 closure、handoff、或 superseded state 時

## 最小內容要求

```markdown
# NEXT_STEPS

- **Last Updated**:
- **Current Phase**:
- **Active Spec(s)**:
- **Work Classification**: continue active spec | new spec | retrofit | CR against completed spec | issue-log candidate
- **Impacted Specs / Contracts**:
- **Open CRs**:
- **Next Action**:
- **Blockers / Waiting On**:
- **Resume Hint**:
- **Related Artifacts**:
```

若本次工作確實涉及 external execution / handoff，再**按需補充** `Repo-side Closure State`、`External Execution State`、`Authoritative Handoff Path`、`External Executor / Owner` 等欄位；不要把它們當成每個 spec 都必須展開的 verbose 模板。

## 撰寫原則

- 保持高層摘要，不要貼上完整 spec 內容。
- 若引用 `ISSUE_LOG.md`，只寫 issue ID / pointer / owner-resolution next action，不複製 row 內容，不把 issue log 當 task list。
- `Open CRs` 只寫 ID / label；完整內容留在 canonical CR 檔案。
- `Impacted Specs / Contracts` 只寫本輪判定需要看的對象，不要複製整份 registry。
- `Resume Hint` 要讓下個 session 可以直接知道先讀哪個檔、先做哪個 gate、先確認哪個 blocker；它應優先指向 `{spec-directory}/tasks.md`、`review.md`、或 reports，而不是用長篇 task-step recap 取代這些 artifact。
- `NEXT_STEPS.md` 必須保持高階、簡短、可追溯；它不是 task list，也不是 progress ledger。
- 若狀態已失效，應直接覆寫為最新摘要，不要把 `NEXT_STEPS.md` 當成歷史日誌。
- 若 spec 已完成或被取代，將 `Next Action` 改成 closure / superseded / no-local-action 狀態；不要同時保留舊的 active work wording。
- 不可使用 dual-state wording。若已寫 `completed-handoff` 或 `completed-elsewhere`，就不得在其他欄位同時保留「still active local work」一類描述。
- 不可把 runtime allocation inventory、RTM rows、TESTS rows、或 SPECS entries 整段貼入；只能放 canonical artifact links。

## 範例

```markdown
# NEXT_STEPS

- **Last Updated**: 2026-04-09T09:30:00+08:00
- **Current Phase**: Design
- **Active Spec(s)**: session-refresh-hardening
- **Work Classification**: CR against completed spec
- **Impacted Specs / Contracts**: user-authentication, contract/session-refresh.yaml#rotation
- **Open CRs**: CR-2026-004
- **Next Action**: 完成 design.md 的 requested delta 說明，之後在 baseline-touch / review 前執行 re-sync gate
- **Blockers / Waiting On**: 等待安全團隊確認 refresh token rotation 約束
- **Resume Hint**: 先讀 `.agents/specs/session-refresh-hardening/tasks.md` 與 `change-requests/CR-2026-004.md`
- **Related Artifacts**: `.agents/specs/session-refresh-hardening/tasks.md`, `.agents/specs/session-refresh-hardening/design.md`, `.agents/specs/session-refresh-hardening/change-requests/CR-2026-004.md`
```

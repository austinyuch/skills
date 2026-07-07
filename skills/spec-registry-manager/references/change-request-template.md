# Change Request Template

本文件提供一個 **輕量 Change Request (CR) template**，用於處理以下情境：
- 新 spec 影響 `[Completed]` spec（此處的 `[Completed]` 指 repo-local baseline closure，不自動表示 external execution 也已完成）
- 新 spec 影響 shared contract
- 新 spec 依賴 external contract assumption，且需要明確記錄調整內容

使用原則：
- `SPECS.md` 只摘要顯示 `Open Change Requests` 的 ID / label
- 完整 CR 內容固定放在 `.agents/specs/{linked-active-spec}/change-requests/{cr-id}.md`
- completed spec 仍保持 immutable；CR 是 overlay，不是覆寫基線
- 若 target baseline 為 `[Completed]` spec，應理解為穩定的 repo-local spec baseline；若 external execution 仍 pending / externalized，必須在 active spec / review / registry 摘要中另外聲明，不可由 CR template 隱含「全部工作都已完成」。

## Minimal Template

```markdown
# Change Request

- **CR ID**:
- **Status**: Open
- **Linked Active Spec**:
- **CR Relation**: impacts
- **Target Baseline**: Completed spec | Shared contract | External contract assumption
- **Target Identifier**:
- **Summary**:
- **Requested Delta**:
- **Why Now**:
- **Resolution Notes**:

## Re-sync Freshness Evidence

- **Checked At**:
- **Valid Until**:
- **SPECS.md Read**:
- **Upstream Source Checked**:
- **Observed Pin/Version**:
- **Outcome**: ok | needs redesign

## External Contract Only

- **Source of Truth**:
- **Pin/Version**:
- **Assumption Snapshot**:
- **Observed Constraint / Behavior**:
```

## Field Notes

- `CR ID`: 在 `SPECS.md` 的 `Open Change Requests` 只放這個摘要 ID / label
- `Status`: 僅使用 `Open | Closed | Superseded`
- `Linked Active Spec`: 提出變更的當前 spec
- `CR Relation`: 使用既有治理語意即可，預設為 `impacts`，避免再發明新的關係類型
- `Target Baseline`: 指出 CR 針對的是哪種穩定基線
- `Target Identifier`: 必須標準化
  - completed spec: `<spec-directory>`
  - shared contract: `contract/<relative-path>#<pointer-or-anchor>`
  - external assumption: `<system-slug>:<assumption-slug>`
- `Requested Delta`: 說明要求改動的是什麼，而不是重寫完整設計
- `Resolution Notes`: 在 CR 關閉前可留空
- `Valid Until`: freshness evidence 的最晚可信時間。若未定義更精細規則，可用簡單日期或條件（例如「until next upstream release notes drop」）表示，避免 evidence 長期掛著卻沒人重查
- `Source of Truth` / `Pin/Version`: 僅當 target 是 external contract assumption 時必填
- `Assumption Snapshot` / `Observed Constraint / Behavior`: 僅當 target 是 external contract assumption 時必填，用來記錄本次依賴的上游假設，而不是只記版本號

## Closure Rules

- `Closed`: 僅在 `Resolution Notes` 記錄落地結果後使用，且對應 CR ID 必須從 active spec 與 `SPECS.md` 的 `Open Change Requests` 摘要移除
- `Superseded`: 僅在 `Resolution Notes` 指向替代 CR ID 時使用
- 若 CR 仍是 `Open`，其 `Re-sync Freshness Evidence` 不可長期留空

## Minimal Example

```markdown
# Change Request

- **CR ID**: CR-2026-004
- **Status**: Open
- **Linked Active Spec**: session-refresh-hardening
- **CR Relation**: impacts
- **Target Baseline**: Completed spec
- **Target Identifier**: user-authentication
- **Summary**: 對齊 refresh token rotation 的既有規則與新 session 安全需求。
- **Requested Delta**: 更新 refresh-session contract 假設，並同步修正下游 validation 行為。
- **Why Now**: 新 active spec 依賴更嚴格的 session refresh 邏輯，若不先登錄 CR，後續 drift repair 無法正確追溯。
- **Resolution Notes**:

## Re-sync Freshness Evidence

- **Checked At**: 2026-04-09
- **Valid Until**: 2026-04-16
- **SPECS.md Read**: `.agents/specs/SPECS.md`
- **Upstream Source Checked**: `contract/session-refresh.yaml`
- **Observed Pin/Version**: local-contract
- **Outcome**: ok

## External Contract Only

- **Source of Truth**:
- **Pin/Version**:
- **Assumption Snapshot**:
- **Observed Constraint / Behavior**:
```

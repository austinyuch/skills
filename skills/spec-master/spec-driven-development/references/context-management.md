# Context Management & Session Optimization

為了縮減接續進行時的 context 負擔，所有 Profile 都必須執行以下三層減壓策略。

詳細說明請參閱 `skills/spec-driven-development/SKILL.md` 的 Execution Profile 機制區段。

## 1. Strategic Compact（策略性壓縮）

每個 Phase 完成時，產出 `phase-{n}-compact.md`：

```markdown
## Phase {N} Compact Summary
- **Phase**: {N} - {Phase Name}
- **Profile**: {prototype | harden | default}
- **Key Decisions**: 
  - [Decision 1] 選擇了 X 而非 Y，因為 Z
- **Open Questions**: 
  - [Q1] 是否需要在 Harden 階段重新評估 Boundary Context 劃分？
- **Artifacts Produced**: 
  - `sketch.md` (v0.1)
- **Next Phase Trigger**: 
  - 條件：Happy Path E2E 通過
  - 輸入：本 Compact Summary + sketch.md
```

- **自動觸發**：每個 Phase 結束時自動執行。
- **決策優先**：只保留「做了什麼決定」和「還有什麼沒決定」，刪除「如何想到的」。

## 2. Phase Gate Handoff（階段閘門交接）

五個強制拆分點，每個點產出 `handoff-{from}-{to}.md`：

1. Phase 1 (Requirements) → Phase 2 (Design)
2. Phase 2 (Design) → Phase 3 (Tasks Planning)
3. Phase 3 (Tasks) → Phase 3 (Implementation Execution)
4. Phase 3+4 (Implementation+Integration) → Phase 5 (Review)
5. Prototype → Harden

**通用格式**：

```markdown
# Handoff: {Spec ID} - {From Phase} → {To Phase}

## 1. Outcome Summary
- **Phase Completed**: {Phase Name}
- **Profile**: {prototype | harden | default}
- **Validation Result**: PASS / FAIL / PARTIAL

## 2. Essential Context (Compressed)
- **Key Decisions**: [D-1] 選擇了 X 而非 Y
- **Open Questions**: [Q-1] 需要在下一階段解答的問題
- **Architecture Snapshot**: 當前分層、已知耦合/技術債

## 3. Deliverables Registry
- **Completed Artifacts**: `{artifact-name}`: {file-path}
- **Task Registry**: [{TAG}-N] {Task description} → {Status}

## 4. Technical Debt & Blockers
- **From ISSUE_LOG.md**: [TD-N] {Description}
- **Blockers for Next Phase**: [B-N] {Description}

## 5. Files & Assets
- **Source Code**: {repo-path / branch / PR link}
- **Spec Artifacts**: {paths}

## 6. Next Phase Entry Criteria
- [ ] 前一階段產出物已確認存在且可讀
- [ ] 無未解決的阻擋問題（或已記錄於 handoff）
```

## 3. Sub-agent Delegation（子代理分派）

將單一 Session 的「全階段負擔」拆分為獨立 sub-agent：

**Prototype Profile 拆分**：
| Sub-agent | 職責 | Input | Output |
|---|---|---|---|
| Prototype-Sketch Agent | Phase 1+2: Sketch-DD | User intent + domain keywords | `sketch.md` |
| Prototype-Coder Agent | Phase 3+4: Behavior-Only TDD + Sandbox Integration | `sketch.md` + boilerplate | Prototype code + `[PROTOTYPE]` tests |
| Prototype-Validate Agent | Phase 5: Hypothesis Validation | Test results + `sketch.md` | `review-prototype.md` |
| Prototype-Log Agent | Phase 6: Issue Log compaction | `[PROTOTYPE]` tasks + code review notes | `ISSUE_LOG.md` entries |

**Harden Profile 拆分**：
| Sub-agent | 職責 | Input | Output |
|---|---|---|---|
| Harden-Spec Agent | Phase 1+2: Reverse-Engineer Spec | `handoff-prototype-harden.md` + Code | `requirements.md` + `design.md` |
| Harden-Backfill Agent | Phase 3: Backfill TDD | `design.md` + Code | `[HARDEN]` unit tests |
| Harden-Integrate Agent | Phase 4: Real Integration | Code + real DB/API config | Integration test results |
| Harden-Review Agent | Phase 5: Full DoD Review | `tasks.md` + evidence refs | `review.md` |
| Harden-Guardrail Agent | Phase 6: DevSecOps + Refactor | Code + security task templates | SAST report + refactored code |

## Context Budget 管理

| Profile | Max Phases / Session | Compact Trigger | Sub-agent Split | Handoff Required |
|---|---|---|---|---|
| `prototype` | 3 | Every Phase end | **強制**拆分 | **強制** |
| `harden` | 2 | Every Phase end | **強制**拆分 | **強制** |
| `default` | 4 | Every 2 Phases | 可選 | 可選 |

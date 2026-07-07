# BA Analyst v3.0.0 Integration Guide

## 概述

本文件說明 **requirements-workflow-skill** 如何整合 **ba-analyst-skill v3.0.0** 的新架構。

ba-analyst 已從獨立 BA (v2.x) 升級為 **Central Coordinator（中央協調者）** (v3.0)，現在可自行協調 6 個其他 skills 完成完整的需求到規格流程。

---

## 🔄 Architecture Change Impact

### v2.x Architecture (Old)
```
requirements-workflow-skill
    ├─ Phase 1: ba-analyst (ANALYSIS)
    ├─ Phase 2: meeting-ba (MEETING_DOCUMENTATION)
    ├─ Phase 3: brd-writer (BRD)
    ├─ Phase 4: ba-analyst or prd-skill (SPECIFICATION)
    └─ Phase 5: requirements-workflow (HANDOFF)
```

### v3.0 Architecture (New)
```
requirements-workflow-skill
    └─ ba-analyst v3.0 (Central Coordinator)
        ├─ Phase 0: Preparation
        ├─ Phase 1: Problem Space Exploration
        ├─ Phase 2: Requirements Elicitation
        │   └─ Coordinates: SME skills (problem domain)
        ├─ Phase 3: Validation & Confirmation
        ├─ Phase 4: DoR Review
        │   └─ Invokes: ba-critic-skill
        ├─ Phase 5: Solution Design
        │   └─ Delegates: solution-designer-skill
        │       └─ Coordinates: SME skills (solution domain)
        └─ Phase 6: Specification Generation
            └─ Delegates: spec-writer-skill
```

---

## 📋 Integration Strategy

### Option A: Simplified Workflow (Recommended)

**requirements-workflow-skill becomes a simple launcher:**

```
requirements-workflow-skill (v2.0+)
    ↓
    Single delegation to ba-analyst v3.0
    ↓
ba-analyst v3.0 handles entire workflow:
    - Phase 0-6 orchestration
    - meeting-ba invocation
    - brd-writer invocation
    - ba-critic invocation
    - solution-designer delegation
    - spec-writer delegation
```

**Pros:**
- ✅ Simpler architecture (1 delegation instead of 5 phases)
- ✅ BA v3.0 already has all coordination logic
- ✅ No duplication of orchestration logic
- ✅ Automatic benefit from BA v3.0 quality gates

**Cons:**
- ❌ Less granular control over individual phases
- ❌ requirements-workflow becomes a thin wrapper

### Option B: Phase-by-Phase Coordination (Complex)

Keep current 5-phase structure but update each phase to work with ba-analyst v3.0 capabilities.

**Pros:**
- ✅ Maintains existing phase boundaries
- ✅ More explicit control over workflow

**Cons:**
- ❌ Complex integration (need to understand BA v3.0 internal phases)
- ❌ Duplicated orchestration logic
- ❌ More maintenance burden

---

## 🚀 Recommended Implementation: Option A

### Updated requirements-workflow-skill Phases

#### Phase 1: Complete Requirements-to-Specification (NEW)

**Executor:** ba-analyst-skill v3.0 (Central Coordinator)

**Input:**
- User's initial requirements description
- Project name/identifier
- Any domain-specific context

**Process:**
```
requirements-workflow invokes ba-analyst v3.0 with:
  - Initial requirements context
  - Target output directory (.opencode/)
  - Quality level expectations

ba-analyst v3.0 executes:
  Phase 0: Preparation
  Phase 1: Problem Space Exploration
  Phase 2: Requirements Elicitation (+ SME coordination)
  Phase 3: Validation & Confirmation (Human Checkpoint 1)
  [Quality Gate 1: Requirements Quality]
  Phase 4: DoR Review (ba-critic-skill)
  [Quality Gate 2: DoR PASSED]
  Phase 5: Solution Design (solution-designer-skill)
  [Quality Gate 3: Design Quality] (Human Checkpoint 2)
  Phase 6: Specification Generation (spec-writer-skill)
  [Quality Gate 4: Specification Quality] (Human Checkpoint 3)
```

**Output:**
```
.opencode/
├── ba-specs/{project}/
│   ├── requirements/requirements.md (v1.0, frozen)
│   ├── analysis/
│   ├── validation/
│   ├── sme-feedback/
│   └── coordination-log.md
├── ba-specs/{project}/brd/BRD.md
├── meeting-records/{project}/
├── solution-design/{project}/design.md (v1.0, frozen)
└── specs/{project}/
    ├── interface/
    ├── function/
    ├── report/
    ├── integration/
    ├── api/
    └── database/
```

**Checkpoint:**
- [ ] ba-analyst v3.0 completed all 6 phases
- [ ] All 4 quality gates passed
- [ ] All 3 human checkpoints obtained approval
- [ ] coordination-log.md shows complete workflow

**Duration Estimate:** 2-5 hours (depending on project complexity)

---

#### Phase 2: Handoff & Delivery (Simplified)

**Executor:** requirements-workflow-skill

**Input:**
- Complete artifact set from ba-analyst v3.0 (from Phase 1)

**Process:**
1. Verify artifact completeness:
   - Requirements documentation (ba-specs/)
   - BRD (brd/)
   - Design document (solution-design/)
   - Technical specifications (specs/)
   - Meeting records (meeting-records/)
   - Coordination log (ba-specs/{project}/coordination-log.md)

2. Generate delivery package:
   - Create delivery summary
   - List all deliverable paths
   - Create traceability matrix (requirements → design → specs)
   - Generate stakeholder-specific views

3. Create handoff checklist:
   - [ ] All quality gates passed
   - [ ] All human approvals obtained
   - [ ] Traceability complete
   - [ ] No open issues
   - [ ] Development team notified

**Output:**
```
.opencode/delivery/{project}/
├── DELIVERY_SUMMARY.md
├── TRACEABILITY_MATRIX.md
├── ARTIFACT_CATALOG.md
├── STAKEHOLDER_VIEWS/
│   ├── business-view.md
│   ├── technical-view.md
│   └── compliance-view.md
└── HANDOFF_CHECKLIST.md
```

**Checkpoint:**
- [ ] Delivery package complete
- [ ] Traceability verified
- [ ] Handoff checklist 100% checked
- [ ] Development team ready to start

**Duration Estimate:** 15-30 minutes

---

## 🔧 Updated Workflow Definition

### workflow_state.json Schema (Updated)

```json
{
  "project": "inventory-system",
  "workflow_version": "2.0.0",
  "ba_analyst_version": "3.0.0",
  "current_phase": "REQUIREMENTS_TO_SPECIFICATION",
  "phases": [
    {
      "phase_id": "REQUIREMENTS_TO_SPECIFICATION",
      "phase_number": 1,
      "status": "in_progress",
      "executor": "ba-analyst-skill",
      "executor_version": "3.0.0",
      "started_at": "2026-02-06T10:00:00Z",
      "expected_duration_hours": 3,
      "sub_phases": [
        {
          "name": "Phase 0: Preparation",
          "status": "completed",
          "completed_at": "2026-02-06T10:15:00Z"
        },
        {
          "name": "Phase 1: Problem Space Exploration",
          "status": "completed",
          "completed_at": "2026-02-06T11:00:00Z"
        },
        {
          "name": "Phase 2: Requirements Elicitation",
          "status": "in_progress",
          "progress": "45%"
        },
        {
          "name": "Phase 3: Validation",
          "status": "pending"
        },
        {
          "name": "Phase 4: DoR Review",
          "status": "pending"
        },
        {
          "name": "Phase 5: Solution Design",
          "status": "pending"
        },
        {
          "name": "Phase 6: Specification",
          "status": "pending"
        }
      ],
      "quality_gates": [
        {
          "gate_id": "gate_1",
          "name": "Requirements Quality",
          "status": "pending",
          "validator": "ba-analyst-skill"
        },
        {
          "gate_id": "gate_2",
          "name": "DoR Review",
          "status": "pending",
          "validator": "ba-critic-skill"
        },
        {
          "gate_id": "gate_3",
          "name": "Design Quality",
          "status": "pending",
          "validator": "ba-analyst-skill"
        },
        {
          "gate_id": "gate_4",
          "name": "Specification Quality",
          "status": "pending",
          "validator": "ba-analyst-skill"
        }
      ],
      "human_checkpoints": [
        {
          "checkpoint_id": "checkpoint_1",
          "name": "Requirements Confirmation",
          "status": "pending",
          "required_after_phase": 3
        },
        {
          "checkpoint_id": "checkpoint_2",
          "name": "Design Review",
          "status": "pending",
          "required_after_phase": 5
        },
        {
          "checkpoint_id": "checkpoint_3",
          "name": "Final Specification Approval",
          "status": "pending",
          "required_after_phase": 6
        }
      ]
    },
    {
      "phase_id": "HANDOFF",
      "phase_number": 2,
      "status": "pending",
      "executor": "requirements-workflow-skill",
      "expected_duration_minutes": 20
    }
  ],
  "metadata": {
    "created_at": "2026-02-06T10:00:00Z",
    "updated_at": "2026-02-06T11:30:00Z",
    "created_by": "requirements-workflow-skill v2.0.0"
  }
}
```

---

## 📊 Updated Checkpoints

### Phase 1 Checkpoint: Requirements-to-Specification Complete

**Validation Criteria:**

```yaml
ba_analyst_completion:
  - [ ] ba-analyst v3.0 Phase 0-6 completed
  - [ ] coordination-log.md exists and shows complete workflow
  
quality_gates:
  - [ ] Gate 1: Requirements Quality (PASSED)
  - [ ] Gate 2: DoR Review (PASSED)
  - [ ] Gate 3: Design Quality (PASSED)
  - [ ] Gate 4: Specification Quality (PASSED)
  
human_approvals:
  - [ ] Checkpoint 1: Requirements Confirmation (APPROVED)
  - [ ] Checkpoint 2: Design Review (APPROVED)
  - [ ] Checkpoint 3: Final Specification Approval (APPROVED)
  
artifact_completeness:
  - [ ] ba-specs/{project}/requirements/requirements.md exists
  - [ ] ba-specs/{project}/brd/BRD.md exists (if invoked)
  - [ ] solution-design/{project}/design.md exists
  - [ ] specs/{project}/ contains all required specs
  - [ ] All specs trace back to design
  - [ ] All design elements trace back to requirements
  
traceability:
  - [ ] Requirements → Design traceability 100%
  - [ ] Design → Specifications traceability 100%
  - [ ] No orphaned requirements
  - [ ] No orphaned design elements
```

### Phase 2 Checkpoint: Handoff Complete

**Validation Criteria:**

```yaml
delivery_package:
  - [ ] DELIVERY_SUMMARY.md created
  - [ ] TRACEABILITY_MATRIX.md created
  - [ ] ARTIFACT_CATALOG.md created
  - [ ] STAKEHOLDER_VIEWS/ all generated
  - [ ] HANDOFF_CHECKLIST.md 100% checked
  
stakeholder_notifications:
  - [ ] Business stakeholders notified
  - [ ] Technical stakeholders notified
  - [ ] Development team ready to start
  - [ ] Project manager acknowledged
```

---

## 🔄 Migration Guide

### For Existing requirements-workflow-skill Users

**Step 1: Update requirements-workflow-skill to v2.0.0**

```bash
cd ~/.config/opencode/skills/requirements-workflow-skill
# Update SKILL.md to reference ba-analyst v3.0.0
# Update workflow phases (5 phases → 2 phases)
# Update workflow_state.json schema
```

**Step 2: Update Active Projects**

For projects currently in progress:

```
If current phase is Phase 1-4 (old structure):
  1. Complete current phase
  2. Switch to ba-analyst v3.0 for remaining phases
  3. Update workflow_state.json to v2.0 schema

If starting new project:
  1. Use requirements-workflow-skill v2.0.0 directly
  2. It will invoke ba-analyst v3.0.0 automatically
```

**Step 3: Update Documentation**

Update project references to new workflow structure:
- README.md
- USAGE_GUIDE.md
- EXAMPLES.md

---

## 🎯 Usage Examples

### Example 1: New Project (Full Workflow)

```
User: "使用 requirements-workflow-skill 管理庫存系統需求"

requirements-workflow-skill v2.0:
  ↓
  Phase 1: REQUIREMENTS_TO_SPECIFICATION
    └─ Invokes ba-analyst v3.0
        ├─ Phase 0: Preparation
        ├─ Phase 1: Problem Space Exploration
        ├─ Phase 2: Requirements Elicitation
        │   └─ Coordinates SME (SAP, MES, etc.)
        ├─ Phase 3: Validation
        │   └─ Human Checkpoint 1 ✓
        ├─ [Quality Gate 1 ✓]
        ├─ Phase 4: DoR Review (ba-critic)
        ├─ [Quality Gate 2 ✓]
        ├─ Phase 5: Solution Design (solution-designer)
        │   └─ Human Checkpoint 2 ✓
        ├─ [Quality Gate 3 ✓]
        └─ Phase 6: Specification (spec-writer)
            └─ Human Checkpoint 3 ✓
        └─ [Quality Gate 4 ✓]
  ↓
  Phase 2: HANDOFF
    ├─ Generate delivery package
    ├─ Create traceability matrix
    └─ Handoff to development team ✓
```

### Example 2: Resume from Interruption

```
User: "繼續庫存系統的需求管理流程"

requirements-workflow-skill:
  1. Read workflow_state.json
  2. Identify current phase: "REQUIREMENTS_TO_SPECIFICATION"
  3. Identify ba-analyst v3.0 sub-phase: "Phase 5: Solution Design"
  4. Resume ba-analyst v3.0 from Phase 5
  5. Complete remaining phases
  6. Proceed to Phase 2: HANDOFF
```

---

## 🛠️ Implementation Checklist

### For requirements-workflow-skill v2.0.0 Update

- [ ] Update `SKILL.md`:
  - [ ] Change description to reference ba-analyst v3.0
  - [ ] Update workflow from 5 phases to 2 phases
  - [ ] Update "整合 Skills" section
  - [ ] Add note about ba-analyst v3.0 orchestration
  
- [ ] Update `VERSION.md`:
  - [ ] Add v2.0.0 entry
  - [ ] Document breaking changes
  - [ ] Add migration guide reference
  
- [ ] Update `README.md`:
  - [ ] Update quick start to show simplified workflow
  - [ ] Update output structure
  
- [ ] Create/Update Phase Files:
  - [ ] `phases/01-requirements-to-specification.md` (NEW)
  - [ ] `phases/02-handoff.md` (UPDATE)
  - [ ] Archive old phase files to `phases/archive-v1/`
  
- [ ] Update `workflows/default-workflow.md`:
  - [ ] Update workflow diagram
  - [ ] Update phase definitions
  - [ ] Add ba-analyst v3.0 sub-phase tracking
  
- [ ] Update `USAGE_GUIDE.md`:
  - [ ] Update usage examples
  - [ ] Add v2.0.0 migration notes
  
- [ ] Update `EXAMPLES.md`:
  - [ ] Update example projects to show v2.0 workflow
  - [ ] Add ba-analyst v3.0 coordination examples
  
- [ ] Create this file:
  - [x] `BA_ANALYST_V3_INTEGRATION.md` (THIS FILE)

---

## 📚 Reference Documentation

### ba-analyst v3.0 Documentation
- ba-analyst-skill/README.md (removed from this bundle) - v3.0.0 overview
- ba-analyst-skill/SKILL.md (removed from this bundle) - Complete workflow
- ba-analyst-skill/VERSION.md (removed from this bundle) - Change history
- ba-analyst-skill/reference/ORCHESTRATION_GUIDE.md (removed from this bundle) - Quick reference

### Coordination Protocols
- ba-analyst-skill/coordination/solution-designer-delegation.md (removed from this bundle)
- ba-analyst-skill/coordination/spec-writer-delegation.md (removed from this bundle)
- ba-analyst-skill/coordination/sme-coordination.md (removed from this bundle)

### Quality Gates
- ba-analyst-skill/reference/QUALITY_GATES.md (removed from this bundle)

---

## ❓ FAQ

### Q1: 為什麼要簡化成 2 個 phases？

**A**: ba-analyst v3.0 已經是一個完整的 orchestrator，它內部管理 6 個 phases。requirements-workflow-skill 不需要再重複這些協調邏輯，只需要：
1. 啟動 ba-analyst v3.0 (Phase 1)
2. 彙整交付 (Phase 2)

### Q2: 如果我不想用 ba-analyst v3.0 的某些功能怎麼辦？

**A**: 
- 可以直接調用單個 skills (meeting-ba, brd-writer, etc.)
- 可以使用 ba-analyst v2.x（如果還保留的話）
- requirements-workflow-skill v1.x 仍然可用（不升級到 v2.0）

### Q3: v1.x 的 workflow_state.json 會不相容嗎？

**A**: 是的。v2.0 schema 結構改變。需要：
- 完成現有 v1.x 項目
- 新項目使用 v2.0.0
- 或手動遷移 workflow_state.json

### Q4: ba-analyst v3.0 需要多久完成？

**A**: 
- Phase 1-4 (需求): 1-2 小時
- Phase 5 (設計): 0.5-1 小時
- Phase 6 (規格): 0.5-1 小時
- 總計: 2-4 小時（中等複雜度專案）

### Q5: 是否可以只用 ba-analyst v3.0 而不用 requirements-workflow-skill？

**A**: 可以！ba-analyst v3.0 已經是 self-contained orchestrator。requirements-workflow-skill v2.0 主要增加：
- 標準化的 workflow tracking (workflow_state.json)
- 交付彙整 (Phase 2: HANDOFF)
- 專案管理視角的儀表板

如果不需要這些，直接使用 ba-analyst v3.0 即可。

---

## 🎉 Summary

**requirements-workflow-skill v2.0.0** 透過簡化架構來適配 **ba-analyst-skill v3.0.0**：

| Aspect | v1.x | v2.0 |
|--------|------|------|
| **Phases** | 5 (ANALYSIS, MEETING, BRD, SPEC, HANDOFF) | 2 (REQUIREMENTS_TO_SPEC, HANDOFF) |
| **BA Role** | Phase executor (Phase 1, 4) | Complete orchestrator (Phase 1) |
| **Coordination** | requirements-workflow coordinates | ba-analyst v3.0 coordinates |
| **Quality Gates** | None | 4 (inherited from ba-analyst v3.0) |
| **Human Checkpoints** | Ad-hoc | 3 (formalized) |
| **Complexity** | Medium | Low (delegated to BA) |
| **Maintenance** | High | Low (leverage BA v3.0) |

**Bottom Line**: requirements-workflow-skill v2.0 becomes a lightweight launcher + delivery packager, leveraging ba-analyst v3.0's powerful orchestration capabilities.

---

**版本**: 1.0.0  
**建立日期**: 2026-02-06  
**作者**: ba-analyst ecosystem upgrade team  
**維護者**: requirements-workflow-skill maintainers

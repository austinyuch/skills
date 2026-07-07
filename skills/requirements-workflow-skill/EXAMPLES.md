# Requirements Workflow Usage Examples

**Version**: 1.0.0  
**Last Updated**: 2026-02-06  
**Purpose**: Real-world examples of requirements-workflow-skill usage

---

## Example 1: New Inventory Management Module (ERP)

### Scenario

**Company**: Manufacturing company using SAP ERP  
**Need**: New inventory alert system to prevent stockouts  
**Timeline**: 6 months  
**Budget**: NT$2M  

### Approach: Automated Workflow

**User Command**:
```
"啟動需求工作流程 for inventory-alert-system"
```

### Execution Timeline

#### Phase 1: Requirements Analysis (90 minutes)

**What Happened**:
- BA Analyst asked about business problem
- User explained manual Excel tracking takes 2 hours/day
- Identified pain points: stockouts happen 3 times/month
- Each stockout costs NT$500K
- Defined KPIs: reduce query time to 5 minutes, zero stockouts

**Output**:
```
.opencode/ba-specs/inventory-alert-system/
├── requirements.md (15 requirements documented)
├── design.md (Solution architecture)
├── tasks.md (32 implementation tasks)
└── dor_audit_result.json (PASSED ✅)
```

---

#### Phase 2: Meeting Documentation (3 minutes)

**What Happened**:
- System auto-captured BA conversation
- Created hierarchical documentation
- Generated topic and session summaries

**Output**:
```
.opencode/ba-meetings/by-user/john/inventory-alert-system/
├── USER_SUMMARY.md
├── 2026-02-06-10-30/
│   ├── SESSION_SUMMARY.md
│   └── TRANSCRIPT.md
```

---

#### Phase 3: BRD Generation (12 minutes)

**What Happened**:
- System read BA specs + meeting docs
- Generated 8-section BRD automatically
- Validated completeness

**Output**:
```
.opencode/ba-specs/inventory-alert-system/brd/BRD.md (8 sections, 5.2KB)

Sections:
1. Executive Summary
2. Business Background & Context
3. Business Objectives (KPI: 5min query, 0 stockouts)
4. Stakeholders (Warehouse Manager, Purchaser, IT)
5. Business Requirements (Functional + NFRs)
6. Constraints & Assumptions (SAP integration, NT$2M budget)
7. Success Criteria & KPIs
8. Risks & Dependencies
```

---

#### Phase 4: Technical Specifications (45 minutes)

**System Asked**:
```
根據 BRD 分析，建議生成以下規格:

1. ✅ Interface Spec (推薦)
   理由: 需要 SAP 整合 (RFC/IDoc/OData)

2. ✅ Function Spec (推薦)
   理由: 庫存監控和預警業務邏輯

3. ⚪ Report Spec (可選)
   理由: 有報表需求但非核心功能

請選擇要生成的規格類型:
```

**User Choice**: `"1,2"` (Interface + Function)

**Output**:
```
.opencode/ba-specs/inventory-alert-system/
├── interface/
│   ├── requirements.md (SAP RFC, IDoc, OData specs)
│   ├── design.md (Integration architecture)
│   ├── tasks.md (API implementation tasks)
│   └── dor_audit_result.json (PASSED ✅)
└── function/
    ├── requirements.md (Alert logic, thresholds)
    ├── design.md (Business rules engine)
    ├── tasks.md (Feature implementation tasks)
    └── dor_audit_result.json (PASSED ✅)
```

---

#### Phase 5: Handoff Package (22 minutes)

**What Happened**:
- Collected all artifacts
- Generated 7 handoff documents
- Created traceability matrix
- Validated completeness

**Output**:
```
.opencode/handoff/inventory-alert-system/
├── README.md (Package overview)
├── HANDOFF_CHECKLIST.md (✅ All items checked)
├── TRACEABILITY_MATRIX.md (98% coverage)
├── ARTIFACT_INDEX.md (28 artifacts cataloged)
├── 01-analysis/ (symlink)
├── 02-meetings/ (symlink)
├── 03-brd/ (BRD.md copy)
├── 04-specifications/ (interface + function symlinks)
└── metadata/
    ├── workflow-state.json
    ├── generation-log.md
    └── statistics.json
```

---

### Total Time: 2 hours 52 minutes

### Deliverables Ready for Dev Team:
- ✅ Complete requirements analysis
- ✅ Business requirements document (BRD)
- ✅ 2 technical specifications (Interface + Function)
- ✅ Requirements traceability matrix (98% coverage)
- ✅ Professional handoff package
- ✅ 28 artifacts organized and indexed

---

## Example 2: Supply Chain Dashboard (Incremental)

### Scenario

**Company**: Logistics company  
**Need**: Analytics dashboard for supply chain visibility  
**Approach**: Manual mode with stakeholder reviews  

### Execution Timeline

#### Day 1: Initial Analysis

**User Command**:
```
"我要做 supply-chain-dashboard 的需求分析"
```

**What Happened**:
- BA Analyst gathered requirements
- Defined 5 key metrics to track
- Identified 3 stakeholder groups
- DoR audit: PASSED

**Result**: BA specs created

---

#### Day 2: Stakeholder Review Meeting

**User Command**:
```
"記錄這次會議 for supply-chain-dashboard"
```

**What Happened**:
- Reviewed BA specs with stakeholders
- Documented additional requirements
- Updated pain points with quantified data

**Result**: Meeting docs created with new insights

---

#### Day 3: BRD Generation

**User Command**:
```
"生成 BRD for supply-chain-dashboard"
```

**What Happened**:
- System combined BA specs + meeting notes
- Generated comprehensive BRD
- Stakeholders approved

**Result**: BRD.md (8 sections, 4.8KB)

---

#### Day 4: Report Specification

**User Command**:
```
"生成 Report Spec for supply-chain-dashboard"
```

**What Happened**:
- Generated report specification
- Defined 12 report layouts
- Specified data sources and refresh rates

**Result**: Report spec with design + tasks

---

#### Day 5: Final Handoff

**User Command**:
```
"進入 Phase 5 for supply-chain-dashboard"
```

**What Happened**:
- Created handoff package
- All artifacts organized
- Ready for BI team

**Result**: Complete handoff package

---

### Total Time: Spread over 5 days (3-4 hours active work)

### Benefits of Manual Mode:
- ✅ Stakeholder checkpoints after each phase
- ✅ Iterative refinement with feedback
- ✅ Team alignment throughout process
- ✅ Same professional deliverables as automated mode

---

## Example 3: Emergency Bug Fix Interruption (Recovery)

### Scenario

**Company**: E-commerce platform  
**Need**: New payment integration  
**Problem**: Urgent bug interrupted workflow  

### Execution Timeline

#### Session 1: Started Workflow (Interrupted)

**09:00 - User Command**:
```
"啟動需求工作流程 for payment-integration"
```

**09:00-10:30**: Phase 1 complete (BA analysis)  
**10:30-10:35**: Phase 2 complete (Meeting docs)  
**10:35-10:42**: Phase 3 started (BRD generation)  

**10:42 - INTERRUPTED**: Production bug requires immediate attention!

**Workflow State Saved**:
```json
{
  "project": "payment-integration",
  "current_phase": 3,
  "status": "paused",
  "phases_complete": {
    "phase1_analysis": true,
    "phase2_meeting": true,
    "phase3_brd": false,
    "phase4_spec": false,
    "phase5_handoff": false
  },
  "checkpoints": [
    {"phase": 1, "status": "complete"},
    {"phase": 2, "status": "complete"}
  ]
}
```

---

#### Session 2: Bug Fixed, Resume Workflow

**14:30 - User Command** (after fixing bug):
```
"繼續需求工作流程 for payment-integration"
```

**System Response**:
```
檢測到工作流程在 Phase 3 (BRD) 中斷。

已完成:
✅ Phase 1: Requirements Analysis
✅ Phase 2: Meeting Documentation

從 Phase 3 繼續執行...
```

**14:30-14:45**: Phase 3 complete (BRD)  
**14:45-15:30**: Phase 4 complete (Interface Spec)  
**15:30-15:55**: Phase 5 complete (Handoff)  

**15:55 - COMPLETE**: Workflow finished!

---

### Total Time: 2h 32min active work (spread across 2 sessions)

### Benefits of Checkpoint Recovery:
- ✅ No work lost from interruption
- ✅ Seamless continuation after 4-hour gap
- ✅ State preserved automatically
- ✅ Can check status anytime with `"顯示工作流程狀態"`

---

## Example 4: Multi-Spec Complex Project

### Scenario

**Company**: Healthcare provider  
**Need**: Patient management system integration  
**Complexity**: Multiple interfaces + business logic + reporting  

### Approach: Automated with Multi-Spec

**User Command**:
```
"啟動需求工作流程 for patient-management-integration"
```

### Phase 4: Multiple Specifications

**System Analysis**:
```
根據 BRD 分析，這是複雜的整合專案，建議生成:

1. ✅ Interface Spec (必須)
   理由: 需整合 3 個外部系統 (HIS, LIS, RIS)

2. ✅ Function Spec (必須)
   理由: 複雜的患者資料同步與衝突解決邏輯

3. ✅ Report Spec (必須)
   理由: 法規要求的 8 種報表格式

請選擇要生成的規格類型:
```

**User Choice**: `"1,2,3"` (All three)

**System Execution** (Sequential):
```
生成 Interface Spec... ✅ (18 minutes)
生成 Function Spec... ✅ (22 minutes)
生成 Report Spec... ✅ (15 minutes)

總計: 55 minutes for 3 specifications
```

---

### Deliverables

```
.opencode/ba-specs/patient-management-integration/
├── interface/
│   ├── requirements.md (15 interface specs)
│   ├── design.md (Integration patterns)
│   └── tasks.md (45 implementation tasks)
├── function/
│   ├── requirements.md (22 business rules)
│   ├── design.md (State machine design)
│   └── tasks.md (38 implementation tasks)
└── report/
    ├── requirements.md (8 report formats)
    ├── design.md (Report architecture)
    └── tasks.md (24 implementation tasks)

Total: 107 implementation tasks across 3 specs
```

---

### Traceability Matrix

```
Requirements Coverage:
- BRD Requirements: 42
- Traced to Interface Spec: 15
- Traced to Function Spec: 22
- Traced to Report Spec: 8
- Overlapping Requirements: 3

Coverage: 100% (45/42 - some requirements map to multiple specs)
```

---

### Total Time: 3 hours 28 minutes

### Benefits of Multi-Spec:
- ✅ Comprehensive coverage of complex project
- ✅ Clear separation of concerns
- ✅ Parallel development possible (3 teams)
- ✅ Each spec has own DoR audit
- ✅ Complete traceability across all specs

---

## Example 5: Quick POC (Proof of Concept)

### Scenario

**Company**: Startup  
**Need**: Quick POC for investor demo  
**Timeline**: 1 week  
**Approach**: Manual mode, skip optional phases  

### Execution

#### Skip Phase 2 (Meeting Docs)

**User Commands**:
```
"我要做 investor-demo-poc 的需求分析"
→ Phase 1 complete

"生成 BRD for investor-demo-poc"
→ Phase 3 complete (skipped Phase 2)

"生成 Function Spec for investor-demo-poc"
→ Phase 4 complete

"進入 Phase 5"
→ Phase 5 complete
```

---

### Handoff Package Note

```
⚠️ Phase 5 完成（部分）

已包含的交付物:
- ✅ BA 規格 (Phase 1)
- ✅ BRD (Phase 3)
- ✅ Function Spec (Phase 4)
- ✅ 交付包 (Phase 5)

缺失的交付物:
- ❌ 會議記錄 (Phase 2) - Skipped for speed

警告: 不完整的交付包可能缺少業務脈絡。
建議: POC 轉正式專案後補充會議記錄。
```

---

### Total Time: 1 hour 45 minutes

### Trade-offs:
- ✅ Fast turnaround for POC
- ✅ Essential documents completed
- ⚠️ Missing business context from meetings
- ⚠️ Lower BRD quality (no meeting inputs)
- 📝 Note to self: Backfill Phase 2 if POC approved

---

## Summary Table

| Example | Mode | Duration | Phases | Specs | Use Case |
|---------|------|----------|--------|-------|----------|
| #1 Inventory | Automated | 2h 52min | All 5 | Interface + Function | New ERP module |
| #2 Dashboard | Manual | 5 days (3-4h) | All 5 | Report | Incremental with reviews |
| #3 Payment | Recovery | 2h 32min (2 sessions) | All 5 | Interface | Interrupted workflow |
| #4 Healthcare | Automated Multi-Spec | 3h 28min | All 5 | Interface + Function + Report | Complex integration |
| #5 POC | Manual Skip | 1h 45min | 4/5 (no Phase 2) | Function only | Quick proof of concept |

---

## Key Takeaways

### When to Use Automated Mode
- ✅ New projects with complete requirements
- ✅ Standard workflows without special reviews
- ✅ Want fastest path to complete deliverables

### When to Use Manual Mode
- ✅ Stakeholder checkpoints needed
- ✅ Iterative refinement process
- ✅ Only need specific phases
- ✅ Learning/exploring the workflow

### When to Use Recovery Mode
- ✅ Workflow was interrupted
- ✅ Come back after a break
- ✅ Error occurred and fixed

### When to Generate Multiple Specs
- ✅ Complex projects with multiple domains
- ✅ Parallel development teams
- ✅ Clear separation of concerns needed
- ✅ Different stakeholders own different specs

### When to Skip Phases
- ⚠️ Only for POC or time-critical situations
- ⚠️ Accept lower documentation quality
- ⚠️ Plan to backfill later if project continues

---

## Pro Tips

### Tip 1: Name Projects Clearly
```
Good: "inventory-alert-system"
Good: "patient-mgmt-integration"
Bad: "project-123"
Bad: "new-feature"
```

### Tip 2: Review State.json Periodically
```bash
cat ~/.opencode/workflow/{project}/state.json

Check:
- Which phases are complete?
- Any errors logged?
- What artifacts generated?
```

### Tip 3: Use Handoff Checklist
```bash
cat ~/.opencode/handoff/{project}/HANDOFF_CHECKLIST.md

Before distributing to team:
- All phases marked complete?
- Traceability > 95%?
- All specs passed DoR?
```

### Tip 4: Pause Between Phases
```
In manual mode, pause for:
- Stakeholder reviews
- Budget approvals
- Technical feasibility checks
- Team alignment meetings
```

### Tip 5: Export Handoff Packages
```bash
# Create distributable archive
cd ~/.opencode/handoff/
tar -czf inventory-alert-system.tar.gz inventory-alert-system/

# Share with development team
# Symlinks preserved in archive
```

---

## FAQ from Real Usage

**Q: Can I modify artifacts mid-workflow?**
A: Yes! Edit files in `.opencode/` directly. Regenerate downstream phases if needed.

**Q: What if I realize I need another spec type after Phase 4?**
A: Run `"生成 {spec-type} for {project}"` then `"重新執行 Phase 5"`.

**Q: Can I run workflows for multiple projects simultaneously?**
A: Yes! Each project has its own state.json. Just use different project names.

**Q: How do I know if workflow is complete?**
A: Check: `"顯示工作流程狀態"` → status should be "complete".

**Q: Can I customize the workflow?**
A: Yes! Edit `.opencode/workflow/{project}/.config.json` or create custom workflow definition.

---

*For more examples and use cases, see USAGE_GUIDE.md and INTEGRATION_TEST_REPORT.md*

*Questions? Contact: requirements-workflow-skill team*

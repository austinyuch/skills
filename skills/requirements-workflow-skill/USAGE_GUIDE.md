# Requirements Workflow Usage Guide

**Version**: 1.0.0  
**Last Updated**: 2026-02-06  
**Skill**: requirements-workflow-skill

---

## Quick Start

### Single Command (Automated Mode)

```
User: "啟動需求工作流程 for inventory-system"
```

This will automatically execute all 5 phases:
1. Phase 1: BA requirements analysis → DoR PASSED
2. Phase 2: Meeting documentation → Docs created
3. Phase 3: BRD generation → BRD.md ready
4. Phase 4: Technical specs → [You choose spec types]
5. Phase 5: Handoff package → Complete delivery

**Result**: `.opencode/handoff/inventory-system/` ready for development team

---

## Usage Modes

### Mode 1: Automated (Recommended for New Projects)

**When to Use**:
- Starting a new project from scratch
- Want complete documentation coverage
- Need professional handoff package

**How to Use**:
```
"啟動需求工作流程 for {project-name}"
```

**What Happens**:
1. System runs ba-analyst (you answer questions)
2. System documents the meeting automatically
3. System generates BRD from your answers
4. System asks you to choose spec type(s)
5. System creates complete handoff package

**Time**: 2-3.5 hours total

---

### Mode 2: Manual (For Iterative Work)

**When to Use**:
- Want to review each phase before continuing
- Need to make decisions between phases
- Only need specific phases (not full workflow)

**How to Use**:

**Step 1: Analysis**
```
"我要做 {project} 的需求分析"
```
→ Completes Phase 1 only
→ Output: `.opencode/ba-specs/{project}/`

**Step 2: Meeting Documentation**
```
"記錄這次會議"
```
→ Completes Phase 2 only
→ Output: `.opencode/ba-meetings/`

**Step 3: BRD Generation**
```
"生成 BRD for {project}"
```
→ Completes Phase 3 only
→ Output: `.opencode/ba-specs/{project}/brd/BRD.md`

**Step 4: Specification**
```
"生成 Interface Spec for {project}"
"生成 Function Spec for {project}"
"生成 PRD for {project}"
```
→ Completes Phase 4 (one spec type at a time)
→ Output: `.opencode/ba-specs/{project}/{type}/` or `.opencode/prd/{project}/`

**Step 5: Handoff Package**
```
"進入 Phase 5 for {project}"
"生成交付包 for {project}"
```
→ Completes Phase 5
→ Output: `.opencode/handoff/{project}/`

**Time**: Same total, but spread across multiple sessions

---

### Mode 3: Checkpoint Recovery

**When to Use**:
- Workflow was interrupted (crash, timeout, etc.)
- You paused and want to continue later
- Error occurred and you've fixed it

**How to Use**:
```
"繼續需求工作流程"
"resume workflow"
```

**What Happens**:
1. System reads `.opencode/workflow/{project}/state.json`
2. Finds last completed phase checkpoint
3. Resumes from next phase
4. Continues until complete

**Example**:
```
Session 1:
  - Phase 1 ✅ Complete
  - Phase 2 ✅ Complete
  - Phase 3 ❌ Interrupted

[Later...]

Session 2:
  User: "繼續需求工作流程"
  System: "檢測到 Phase 3 中斷，繼續執行..."
  → Runs Phase 3-5
  → Complete!
```

---

## Phase-by-Phase Guide

### Phase 1: Requirements Analysis

**What It Does**: Conducts structured BA session using ba-analyst-skill

**Your Role**:
- Answer questions about business problem
- Describe current pain points
- Define requirements and acceptance criteria

**System Output**:
```
.opencode/ba-specs/{project}/
├── requirements.md      # Requirements documented
├── design.md            # Solution design
├── tasks.md             # Implementation tasks
└── dor_audit_result.json  # DoR status: PASSED
```

**Time**: 1-2 hours

**Tips**:
- Be specific about pain points and goals
- Provide concrete examples when possible
- Review DoR audit results carefully

---

### Phase 2: Meeting Documentation

**What It Does**: Auto-captures BA conversation and creates searchable docs

**Your Role**:
- Minimal! System works automatically
- Optional: Say "記錄這次會議" to finalize

**System Output**:
```
.opencode/ba-meetings/
├── by-user/{user}/
│   └── {topic}/
│       ├── USER_SUMMARY.md
│       └── [sessions...]
├── by-topic/{topic}/
│   ├── TOPIC_SUMMARY.md
│   └── [sessions...]
├── by-date/{date}/
│   └── [sessions...]
└── INDEX.md
```

**Time**: 5 minutes

**Tips**:
- Let system auto-capture; don't interrupt
- Meeting docs enhance BRD quality
- Skip this phase if pressed for time (but not recommended)

---

### Phase 3: BRD Generation

**What It Does**: Generates 8-section Business Requirements Document

**Your Role**:
- Confirm project name
- Review generated BRD
- Request regeneration if needed

**System Output**:
```
.opencode/ba-specs/{project}/brd/
└── BRD.md  # 8 standard sections:
    1. Executive Summary
    2. Business Background & Context
    3. Business Objectives
    4. Stakeholders
    5. Business Requirements
    6. Constraints & Assumptions
    7. Success Criteria & KPIs
    8. Risks & Dependencies
```

**Time**: 6-14 minutes

**Tips**:
- BRD quality improves with meeting docs (Phase 2)
- Review all 8 sections for completeness
- BRD becomes foundation for Phase 4

---

### Phase 4: Technical Specification

**What It Does**: Generates technical specs based on BRD

**Your Role**:
- **CRITICAL**: Choose spec type(s)
- Can select multiple types
- Review generated specs

**Spec Type Decision Tree**:

```
Need external system integration?
├─ Yes → Choose "Interface Spec"
└─ No → Continue...

Need internal business logic?
├─ Yes → Choose "Function Spec"
└─ No → Continue...

Need data reports/analytics?
├─ Yes → Choose "Report Spec"
└─ No → Continue...

Need complete product document?
└─ Yes → Choose "PRD"
```

**System Output**:

**Option A: ba-analyst spec(s)**
```
.opencode/ba-specs/{project}/
├── interface/
│   ├── requirements.md
│   ├── design.md
│   ├── tasks.md
│   └── dor_audit_result.json
├── function/
│   └── [same structure]
└── report/
    └── [same structure]
```

**Option B: PRD**
```
.opencode/prd/{project}/
└── PRD.md
```

**Time**: 12-60 minutes (depends on type/count)

**Tips**:
- Complex projects: Choose Interface + Function
- Simple projects: Choose Function only
- B2B products: Consider PRD
- Can generate multiple types sequentially

---

### Phase 5: Handoff Package

**What It Does**: Creates complete delivery package for dev team

**Your Role**:
- Minimal! System works automatically
- Review generated checklist
- Distribute to team

**System Output**:
```
.opencode/handoff/{project}/
├── README.md                   # Package overview
├── HANDOFF_CHECKLIST.md        # Delivery checklist
├── TRACEABILITY_MATRIX.md      # Requirement tracing
├── ARTIFACT_INDEX.md           # File catalog
├── 01-analysis/                # BA specs (symlink)
├── 02-meetings/                # Meeting docs (symlink)
├── 03-brd/                     # BRD (copy)
├── 04-specifications/          # Specs (symlink)
└── metadata/
    ├── workflow-state.json
    ├── generation-log.md
    └── statistics.json
```

**Time**: 18-23 minutes

**Tips**:
- Review HANDOFF_CHECKLIST.md first
- Check TRACEABILITY_MATRIX.md for coverage
- Use README.md to orient team members
- Symlinks keep package in sync with originals

---

## Common Commands Reference

### Workflow Control

```bash
# Start workflow
"啟動需求工作流程 for {project}"
"start requirements workflow"

# Pause workflow
"暫停工作流程"
"pause workflow"

# Resume workflow
"繼續需求工作流程"
"resume workflow"

# Check status
"顯示工作流程狀態"
"show workflow status"
```

### Phase Execution

```bash
# Execute specific phase
"執行 Phase 1"  # or "Phase 2", "Phase 3", etc.
"run phase 1"

# Skip phase
"跳過 Phase 2"
"skip phase 2"

# Retry phase
"重新執行 Phase 3"
"retry phase 3"
```

### Artifact Viewing

```bash
# View BA specs
"顯示 BA 規格"
"show ba specs"

# View BRD
"顯示 BRD"
"show brd"

# View specifications
"顯示 Interface Spec"
"show function spec"

# View handoff package
"顯示交付包"
"show handoff package"
```

---

## Use Case Examples

### Use Case 1: New ERP Module

**Scenario**: Building new inventory management module for SAP system

**Approach**: Automated Mode

**Steps**:
1. `"啟動需求工作流程 for inventory-module"`
2. Answer BA questions about current pain points
3. System auto-documents meeting
4. Review generated BRD
5. Choose: Interface Spec (SAP integration) + Function Spec (business logic)
6. System creates handoff package
7. Distribute to development team

**Result**: Complete documentation ready in ~2.5 hours

---

### Use Case 2: Supply Chain Dashboard

**Scenario**: Analytics dashboard for supply chain visibility

**Approach**: Manual Mode

**Day 1**:
- `"我要做 supply-chain-dashboard 的需求分析"`
- Complete requirements gathering
- `"記錄這次會議"`

**Day 2** (After stakeholder review):
- `"生成 BRD for supply-chain-dashboard"`
- Review BRD with stakeholders
- `"生成 Report Spec for supply-chain-dashboard"`
- `"進入 Phase 5"`

**Result**: Iterative approach with stakeholder checkpoints

---

### Use Case 3: Emergency Bug Fix (Interrupted Workflow)

**Scenario**: Started workflow, but urgent bug interrupted

**Approach**: Checkpoint Recovery

**Session 1** (Interrupted):
- Started workflow
- Completed Phase 1 ✅
- Completed Phase 2 ✅
- Phase 3 started but interrupted ❌

**Session 2** (After bug fixed):
- `"繼續需求工作流程"`
- System resumes from Phase 3
- Completes all remaining phases

**Result**: No work lost, seamless continuation

---

## Troubleshooting

### Problem: Phase 2 didn't trigger

**Symptom**: Meeting documentation not created after Phase 1

**Solution**:
```bash
# Check trigger file
ls ~/.config/opencode/.triggers/ba-meetings/

# If missing, manually trigger
"記錄這次會議"
```

### Problem: BRD is incomplete

**Symptom**: BRD < 1KB or missing sections

**Cause**: Missing meeting docs or BA specs

**Solution**:
```bash
# Check inputs
ls ~/.opencode/ba-specs/{project}/
ls ~/.opencode/ba-meetings/

# If BA specs missing:
"重新執行 Phase 1"

# If meeting docs missing:
"記錄這次會議"

# Regenerate BRD
"重新生成 BRD"
```

### Problem: Can't choose spec type in Phase 4

**Symptom**: System doesn't show spec options

**Cause**: BRD not found or invalid

**Solution**:
```bash
# Verify BRD exists
cat ~/.opencode/ba-specs/{project}/brd/BRD.md

# If missing or empty:
"重新執行 Phase 3"

# Then retry Phase 4
"執行 Phase 4"
```

### Problem: Handoff package missing artifacts

**Symptom**: ARTIFACT_INDEX shows missing files

**Cause**: Some phases didn't complete

**Solution**:
```bash
# Check workflow state
cat ~/.opencode/workflow/{project}/state.json

# Identify missing phase
# Re-run missing phase
"重新執行 Phase {N}"

# Regenerate handoff
"重新執行 Phase 5"
```

### Problem: Workflow stuck

**Symptom**: No progress for >5 minutes

**Solution**:
```bash
# Check status
"顯示工作流程狀態"

# Check for errors
"顯示錯誤日誌"

# If skill stuck, restart
"暫停工作流程"
[Fix issue]
"繼續工作流程"
```

---

## Best Practices

### 1. Always Complete Phase 2

**Why**: Meeting docs significantly improve BRD quality
- Captures conversation context
- Preserves decision rationale
- Helps future team members understand "why"

**Recommendation**: Even if it feels redundant, let system document the meeting.

---

### 2. Choose Appropriate Spec Types

**Guidelines**:
- **External Integration** → Interface Spec (always)
- **Complex Business Logic** → Function Spec (always)
- **Reporting/Analytics** → Report Spec (if significant)
- **B2B Product** → PRD (comprehensive alternative)

**Recommendation**: When in doubt, choose Interface + Function.

---

### 3. Review Traceability Matrix

**Why**: Ensures no requirements are orphaned

**How**:
```bash
# After Phase 5
cat ~/.opencode/handoff/{project}/TRACEABILITY_MATRIX.md

# Check coverage
# Look for "Untraced Requirements"
# If any found, update specs accordingly
```

**Recommendation**: Aim for >95% traceability coverage.

---

### 4. Use Checkpoints Wisely

**When to Pause**:
- End of workday
- Before major decision
- Waiting for stakeholder input

**How to Pause**:
```
"暫停工作流程"
```

**How to Resume**:
```
"繼續需求工作流程"
```

**Recommendation**: Checkpoints are free—use them liberally.

---

### 5. Validate Before Handoff

**Checklist**:
- [ ] All phases marked complete
- [ ] BRD has 8 sections
- [ ] All specs passed DoR
- [ ] TRACEABILITY_MATRIX shows >95% coverage
- [ ] HANDOFF_CHECKLIST all items checked

**Command**:
```
cat ~/.opencode/handoff/{project}/HANDOFF_CHECKLIST.md
```

**Recommendation**: Don't handoff incomplete packages.

---

## Advanced Usage

### Custom Workflow Configuration

**File**: `.opencode/workflow/{project}/.config.json`

```json
{
  "workflow_type": "default",
  "auto_proceed": true,
  "skip_phases": [],
  "default_spec_types": ["interface", "function"],
  "require_meeting_docs": false,
  "auto_handoff": true,
  "notification": {
    "on_complete": true,
    "on_error": true
  }
}
```

**Use Cases**:
- Skip Phase 2 always: `"skip_phases": [2]`
- Auto-select specs: `"default_spec_types": ["interface"]`
- Require meeting docs: `"require_meeting_docs": true`

---

### Multi-Project Workflows

**Running Parallel Projects**:
```bash
# Project 1
"啟動需求工作流程 for project-a"
"暫停工作流程"  # After Phase 2

# Project 2
"啟動需求工作流程 for project-b"
"暫停工作流程"  # After Phase 2

# Resume Project 1
"繼續需求工作流程 for project-a"

# Resume Project 2
"繼續需求工作流程 for project-b"
```

**Tip**: Each project has its own `state.json`, so you can safely interleave.

---

### Regenerating Specific Artifacts

```bash
# Regenerate BRD only
"重新生成 BRD for {project}"

# Regenerate specific spec
"重新生成 Interface Spec for {project}"

# Regenerate handoff package
"重新生成交付包 for {project}"
```

**Use Case**: Update after requirements change

---

## Getting Help

### In-Workflow Help

```bash
# General help
"help with workflow"

# Phase-specific help
"help with Phase 3"
"how to choose spec type"

# Command help
"list workflow commands"
"show workflow examples"
```

### Documentation

- **Quick Start**: This document (USAGE_GUIDE.md)
- **Complete Reference**: SKILL.md
- **Phase Details**: phases/01-05 guides
- **Workflow Definition**: workflows/default-workflow.md
- **Integration Test**: INTEGRATION_TEST_REPORT.md

### Support

If issues persist:
1. Check `INTEGRATION_TEST_REPORT.md` troubleshooting section
2. Review `.opencode/workflow/{project}/state.json`
3. Check error logs in metadata/generation-log.md
4. Contact requirements-workflow-skill maintainers

---

## FAQ

**Q: How long does the full workflow take?**
A: 2-3.5 hours typically. Phase 1 is longest (1-2h), others are quick.

**Q: Can I skip phases?**
A: Yes, use manual mode. But Phase 2 improves quality, and Phase 5 creates professional handoff.

**Q: What if I need to change requirements mid-workflow?**
A: Pause, update Phase 1 artifacts, regenerate downstream phases.

**Q: Can multiple people work on the same workflow?**
A: No, workflows are single-user. But handoff packages can be shared.

**Q: Do I need all three skills installed?**
A: Yes: ba-analyst-skill, meeting-ba-skill, brd-writer-skill are required.

**Q: Can I customize the workflow?**
A: Yes, via `.opencode/workflow/{project}/.config.json` or by creating custom workflow definition.

**Q: What if Phase 4 fails to generate specs?**
A: Check BRD exists and is complete, then retry Phase 4. If persists, check error log.

**Q: Can I use this for non-software projects?**
A: Yes! The workflow is generic. Just answer BA questions for your domain.

**Q: How do I know if workflow is complete?**
A: Check `state.json`: `"status": "complete"` and handoff package exists.

**Q: Can I export the handoff package?**
A: Yes, it's just files. Zip `.opencode/handoff/{project}/` and share.

---

## Version History

### v1.0.0 (2026-02-06)
- Initial usage guide
- 3 execution modes documented
- Phase-by-phase guide
- Command reference
- Use cases and examples
- Troubleshooting section
- Best practices

---

*For more details, see SKILL.md and phase guides in the phases/ directory.*

*Questions? Contact: requirements-workflow-skill team*

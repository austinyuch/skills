# Phase 5: Handoff Package Generation

## 目標 (Objective)

彙整完整需求管理流程的所有交付物，生成結構化的交付包，確保需求追溯性和可交付性。

## 輸入要求 (Input Requirements)

### 必要輸入 (Required)

從前置階段收集的所有交付物:

| Phase | 交付物 | 路徑 | 狀態檢查 |
|-------|--------|------|---------|
| Phase 1 | BA 規格 | `.opencode/ba-specs/{project}/` | 必要 |
| Phase 2 | 會議記錄 | `.opencode/ba-meetings/` | 可選 |
| Phase 3 | BRD | `.opencode/ba-specs/{project}/brd/BRD.md` | 必要 |
| Phase 4 | 技術規格 | `.opencode/ba-specs/{project}/{spec-type}/` 或 `.opencode/prd/{project}/` | 必要 |

### 工作流程狀態 (Workflow State)

需從 `.opencode/workflow/{project}/state.json` 讀取:
- 已完成的 phases
- 生成的 artifacts 路徑
- 規格類型清單

## 執行步驟 (Execution Steps)

### Step 1: 驗證所有交付物存在

**驗證腳本**:
```bash
#!/bin/bash
# 驗證所有必要交付物

PROJECT_NAME="$1"
MISSING_ARTIFACTS=()

echo "🔍 驗證專案 ${PROJECT_NAME} 的交付物..."

# 1. 檢查 BA 規格
if [ ! -d "$HOME/.opencode/ba-specs/${PROJECT_NAME}" ]; then
  MISSING_ARTIFACTS+=("BA 規格 (Phase 1)")
fi

# 2. 檢查 BRD
if [ ! -f "$HOME/.opencode/ba-specs/${PROJECT_NAME}/brd/BRD.md" ]; then
  MISSING_ARTIFACTS+=("BRD (Phase 3)")
fi

# 3. 檢查技術規格 (至少一種)
SPEC_FOUND=false
for spec_type in interface function report; do
  if [ -d "$HOME/.opencode/ba-specs/${PROJECT_NAME}/${spec_type}" ]; then
    SPEC_FOUND=true
    break
  fi
done

if [ ! -f "$HOME/.opencode/prd/${PROJECT_NAME}/PRD.md" ] && [ "$SPEC_FOUND" = false ]; then
  MISSING_ARTIFACTS+=("技術規格 (Phase 4)")
fi

# 4. 報告結果
if [ ${#MISSING_ARTIFACTS[@]} -eq 0 ]; then
  echo "✅ 所有必要交付物已就緒"
  exit 0
else
  echo "❌ 缺少以下交付物:"
  printf '  - %s\n' "${MISSING_ARTIFACTS[@]}"
  exit 1
fi
```

**執行動作**:
```bash
# 執行驗證
bash verify-artifacts.sh {project-name}

# 根據結果決定:
IF 所有交付物存在:
  → 繼續 Step 2
ELSE:
  → 報告缺失項目
  → 詢問使用者: "是否回到缺失的 Phase 補充？"
  → 或: "是否跳過缺失項目繼續打包？"
```

### Step 2: 建立交付目錄結構

**目錄結構**:
```
.opencode/handoff/{project-name}/
├── README.md                          # 交付包總覽
├── HANDOFF_CHECKLIST.md              # 交付檢查清單
├── TRACEABILITY_MATRIX.md            # 需求追溯矩陣
├── ARTIFACT_INDEX.md                 # 交付物索引
│
├── 01-analysis/                      # Phase 1 輸出
│   └── ba-specs/                     # symlink → .opencode/ba-specs/{project}/
│
├── 02-meetings/                      # Phase 2 輸出 (如有)
│   └── meeting-docs/                 # symlink → .opencode/ba-meetings/
│
├── 03-brd/                           # Phase 3 輸出
│   └── BRD.md                        # copy from .opencode/ba-specs/{project}/brd/BRD.md
│
├── 04-specifications/                # Phase 4 輸出
│   ├── interface/                    # symlink (如有)
│   ├── function/                     # symlink (如有)
│   ├── report/                       # symlink (如有)
│   └── prd/                          # copy from .opencode/prd/{project}/ (如有)
│
└── metadata/                         # 元數據
    ├── workflow-state.json           # 工作流程狀態快照
    ├── generation-log.md             # 生成日誌
    └── statistics.json               # 統計資訊
```

**建立指令**:
```bash
#!/bin/bash
# 建立交付目錄結構

PROJECT_NAME="$1"
HANDOFF_DIR="$HOME/.opencode/handoff/${PROJECT_NAME}"

echo "📦 建立交付目錄: ${HANDOFF_DIR}"

# 建立主目錄
mkdir -p "${HANDOFF_DIR}"/{01-analysis,02-meetings,03-brd,04-specifications,metadata}

# 建立 symlinks
ln -s "$HOME/.opencode/ba-specs/${PROJECT_NAME}" "${HANDOFF_DIR}/01-analysis/ba-specs"

if [ -d "$HOME/.opencode/ba-meetings" ]; then
  ln -s "$HOME/.opencode/ba-meetings" "${HANDOFF_DIR}/02-meetings/meeting-docs"
fi

# 複製 BRD
cp "$HOME/.opencode/ba-specs/${PROJECT_NAME}/brd/BRD.md" "${HANDOFF_DIR}/03-brd/"

# 建立 spec symlinks
for spec_type in interface function report; do
  SPEC_PATH="$HOME/.opencode/ba-specs/${PROJECT_NAME}/${spec_type}"
  if [ -d "$SPEC_PATH" ]; then
    ln -s "$SPEC_PATH" "${HANDOFF_DIR}/04-specifications/${spec_type}"
  fi
done

# 複製 PRD (如有)
if [ -f "$HOME/.opencode/prd/${PROJECT_NAME}/PRD.md" ]; then
  mkdir -p "${HANDOFF_DIR}/04-specifications/prd"
  cp "$HOME/.opencode/prd/${PROJECT_NAME}/PRD.md" "${HANDOFF_DIR}/04-specifications/prd/"
fi

# 複製工作流程狀態
cp "$HOME/.opencode/workflow/${PROJECT_NAME}/state.json" "${HANDOFF_DIR}/metadata/workflow-state.json"

echo "✅ 交付目錄結構已建立"
```

### Step 3: 生成 README.md (交付包總覽)

**README 內容**:
```markdown
# {Project Name} - Requirements Management Handoff Package

**Generated**: {ISO-8601-timestamp}  
**Workflow ID**: {workflow-id}  
**Status**: COMPLETE ✅

---

## 📦 Package Overview

This package contains all deliverables from the complete A→B→C requirements management workflow:

- ✅ **Analysis** (Phase 1) - Business requirements analysis
- ✅ **Meetings** (Phase 2) - Meeting documentation [if applicable]
- ✅ **BRD** (Phase 3) - Business Requirements Document
- ✅ **Specifications** (Phase 4) - Technical specifications

---

## 📂 Directory Structure

```
handoff/{project-name}/
├── README.md                    ← You are here
├── HANDOFF_CHECKLIST.md         ← Delivery checklist
├── TRACEABILITY_MATRIX.md       ← Requirements traceability
├── ARTIFACT_INDEX.md            ← Artifact catalog
│
├── 01-analysis/                 ← BA specs from Phase 1
├── 02-meetings/                 ← Meeting docs from Phase 2
├── 03-brd/                      ← BRD from Phase 3
├── 04-specifications/           ← Technical specs from Phase 4
└── metadata/                    ← Workflow metadata
```

---

## 🎯 Quick Start

### For Project Managers
1. Review **HANDOFF_CHECKLIST.md** for completeness
2. Read **03-brd/BRD.md** for business context
3. Check **TRACEABILITY_MATRIX.md** for requirements coverage

### For Technical Leads
1. Review **04-specifications/** for technical requirements
2. Check **01-analysis/ba-specs/** for detailed requirements
3. Read **design.md** and **tasks.md** in each spec

### For Developers
1. Start with **04-specifications/{spec-type}/tasks.md**
2. Reference **design.md** for architecture decisions
3. Use **requirements.md** for functional requirements

---

## 📊 Package Statistics

- **Total Phases Completed**: {phase-count}
- **Documents Generated**: {doc-count}
- **Total Size**: {package-size}
- **Specifications**: {spec-list}

---

## 📋 Deliverables Checklist

- [x] Business Requirements Analysis (Phase 1)
- [x] Business Requirements Document (Phase 3)
- [x] Technical Specifications (Phase 4)
- [x] Requirements Traceability Matrix
- [x] Handoff Checklist

---

## 🔗 Artifact Locations

### Original Locations (for reference)
- BA Specs: `.opencode/ba-specs/{project}/`
- BRD: `.opencode/ba-specs/{project}/brd/BRD.md`
- Specifications: `.opencode/ba-specs/{project}/{spec-type}/`
- Workflow State: `.opencode/workflow/{project}/state.json`

### This Package
All artifacts are organized in this handoff directory with symlinks to originals.

---

## 📝 Notes

- This package is generated automatically by requirements-workflow-skill
- All symlinks point to original artifacts for real-time updates
- BRD and metadata files are copied for portability
- Workflow state is preserved in `metadata/workflow-state.json`

---

## 🆘 Support

For questions about this handoff package:
- Review `ARTIFACT_INDEX.md` for detailed artifact catalog
- Check `metadata/generation-log.md` for generation details
- Contact the BA team if clarification needed

---

**Workflow Tool**: requirements-workflow-skill v1.0.0  
**Generated by**: OpenCode AI Agent
```

### Step 4: 生成 HANDOFF_CHECKLIST.md

**檢查清單內容**:
```markdown
# {Project Name} - Handoff Checklist

**Date**: {ISO-8601-timestamp}  
**Project**: {project-name}  
**Workflow ID**: {workflow-id}

---

## ✅ Completeness Check

### Phase 1: Analysis
- [x] BA specs directory exists
- [x] requirements.md complete
- [x] design.md complete
- [x] tasks.md complete
- [x] DoR audit passed

### Phase 2: Meeting Documentation
- [{x/}] Meeting docs available
- [{x/}] USER_SUMMARY.md created
- [{x/}] TOPIC_SUMMARY.md created
- [{x/}] SESSION_SUMMARY.md created
- [{x/}] TRANSCRIPT.md available

### Phase 3: Business Requirements Document
- [x] BRD.md exists (> 1KB)
- [x] 8 standard sections complete:
  - [x] 1. Executive Summary
  - [x] 2. Business Background & Context
  - [x] 3. Business Objectives
  - [x] 4. Stakeholders
  - [x] 5. Business Requirements
  - [x] 6. Constraints & Assumptions
  - [x] 7. Success Criteria & KPIs
  - [x] 8. Risks & Dependencies

### Phase 4: Technical Specifications
- [x] At least one spec type generated:
  - [{x/}] Interface Spec
  - [{x/}] Function Spec
  - [{x/}] Report Spec
  - [{x/}] PRD
- [x] Spec requirements.md complete
- [x] Spec design.md complete
- [x] Spec tasks.md complete

---

## 📊 Quality Metrics

| Metric | Value | Status |
|--------|-------|--------|
| Total Phases Completed | {phase-count}/5 | {status} |
| Documents Generated | {doc-count} | ✅ |
| DoR Audits Passed | {dor-count} | ✅ |
| Total Package Size | {size} | ✅ |
| Traceability Coverage | {coverage}% | {status} |

---

## 🎯 Readiness Assessment

### Ready for Handoff ✅
- [x] All required phases complete
- [x] All documents verified
- [x] Requirements traceable
- [x] No blocking issues

### Recommendations
- [ ] {recommendation-1}
- [ ] {recommendation-2}
- [ ] {recommendation-3}

---

## 📝 Sign-off

### BA Team
- **Name**: _________________
- **Date**: _________________
- **Signature**: _________________

### Technical Lead
- **Name**: _________________
- **Date**: _________________
- **Signature**: _________________

### Project Manager
- **Name**: _________________
- **Date**: _________________
- **Signature**: _________________

---

## 📎 Attachments

- TRACEABILITY_MATRIX.md - Requirements traceability
- ARTIFACT_INDEX.md - Complete artifact catalog
- metadata/workflow-state.json - Workflow state snapshot
- metadata/statistics.json - Detailed statistics

---

*Generated by requirements-workflow-skill v1.0.0*
```

### Step 5: 生成 TRACEABILITY_MATRIX.md

**追溯矩陣內容**:
```markdown
# {Project Name} - Requirements Traceability Matrix

**Generated**: {ISO-8601-timestamp}  
**Purpose**: Map business requirements to technical specifications

---

## 📊 Traceability Overview

| Metric | Count | Coverage |
|--------|-------|----------|
| Business Requirements (BRD) | {brd-req-count} | 100% |
| Functional Requirements (Specs) | {func-req-count} | {coverage}% |
| Non-Functional Requirements | {nfr-count} | {coverage}% |
| Technical Design Items | {design-count} | {coverage}% |
| Implementation Tasks | {task-count} | {coverage}% |

---

## 🔗 Requirements Mapping

### BRD → Specifications

| BRD Requirement ID | Description | Mapped to Spec | Spec Type | Status |
|--------------------|-------------|----------------|-----------|--------|
| BRD-FR-001 | {description} | {spec-path} | Interface | ✅ Mapped |
| BRD-FR-002 | {description} | {spec-path} | Function | ✅ Mapped |
| BRD-NFR-001 | {description} | {spec-path} | Function | ✅ Mapped |
| ... | ... | ... | ... | ... |

### Specifications → Implementation Tasks

| Spec Requirement | Spec File | Task ID | Task Description | Status |
|------------------|-----------|---------|------------------|--------|
| {spec-req-id} | {spec-path}/requirements.md | TASK-001 | {description} | ✅ Defined |
| {spec-req-id} | {spec-path}/requirements.md | TASK-002 | {description} | ✅ Defined |
| ... | ... | ... | ... | ... |

---

## 📋 Coverage Analysis

### Fully Traced Requirements ✅
- {requirement-id}: {description}
- {requirement-id}: {description}
- ...

### Partially Traced Requirements ⚠️
- {requirement-id}: {description} - Missing {what}
- ...

### Untraced Requirements ❌
- {requirement-id}: {description} - No spec mapping
- ...

---

## 🎯 Acceptance Criteria Mapping

### BRD Success Criteria → Spec Acceptance Criteria

| BRD Criterion | BRD Section | Spec Acceptance Criteria | Spec Location |
|---------------|-------------|--------------------------|---------------|
| {criterion} | 7. Success Criteria | {ac-id}: {description} | {spec-path} |
| ... | ... | ... | ... |

---

## 📈 Traceability Statistics

### By Phase
- **Phase 1 (Analysis)**: {req-count} requirements identified
- **Phase 3 (BRD)**: {brd-req-count} business requirements documented
- **Phase 4 (Specs)**: {spec-req-count} technical requirements specified

### By Requirement Type
- **Functional Requirements**: {fr-count} ({fr-coverage}% coverage)
- **Non-Functional Requirements**: {nfr-count} ({nfr-coverage}% coverage)
- **Constraints**: {constraint-count} (all documented)

### By Specification Type
- **Interface Specs**: {interface-req-count} requirements
- **Function Specs**: {function-req-count} requirements
- **Report Specs**: {report-req-count} requirements
- **PRD**: {prd-req-count} requirements

---

## 🔍 Trace Details

[Generate detailed trace for each requirement, following the chain:]

### Example: BRD-FR-001
```
BRD-FR-001: User Authentication
├─ Source: 03-brd/BRD.md (Section 5.1)
├─ Mapped to Spec: 04-specifications/interface/requirements.md (REQ-AUTH-001)
├─ Design: 04-specifications/interface/design.md (AUTH_DESIGN-001)
├─ Tasks: 04-specifications/interface/tasks.md (TASK-AUTH-001 to TASK-AUTH-005)
└─ Acceptance Criteria:
   ├─ AC-001: User can login with email/password
   ├─ AC-002: Session persists for 24 hours
   └─ AC-003: Logout clears session
```

[Repeat for all major requirements]

---

## ⚠️ Traceability Gaps

### Identified Issues
1. **{Issue Description}**
   - Requirement: {req-id}
   - Impact: {impact-description}
   - Recommendation: {recommendation}

[List all gaps found]

---

## ✅ Traceability Validation

- [x] All BRD requirements have spec mappings
- [x] All spec requirements trace to BRD
- [x] All tasks trace to spec requirements
- [x] Acceptance criteria defined for all requirements
- [x] No orphaned requirements found

**Validation Status**: {PASS/FAIL} ✅

---

*Generated by requirements-workflow-skill v1.0.0*
*Traceability methodology: Forward and backward tracing*
```

### Step 6: 生成 ARTIFACT_INDEX.md

**交付物索引內容**:
```markdown
# {Project Name} - Artifact Index

**Generated**: {ISO-8601-timestamp}  
**Total Artifacts**: {artifact-count}

---

## 📚 Artifact Catalog

### Phase 1: Analysis Artifacts

| Artifact | Path | Type | Size | Last Modified |
|----------|------|------|------|---------------|
| Requirements | 01-analysis/ba-specs/requirements.md | Markdown | {size} | {date} |
| Design | 01-analysis/ba-specs/design.md | Markdown | {size} | {date} |
| Tasks | 01-analysis/ba-specs/tasks.md | Markdown | {size} | {date} |
| DoR Audit | 01-analysis/ba-specs/dor_audit_result.json | JSON | {size} | {date} |

### Phase 2: Meeting Artifacts (if applicable)

| Artifact | Path | Type | Size | Last Modified |
|----------|------|------|------|---------------|
| User Summary | 02-meetings/meeting-docs/by-user/{user}/USER_SUMMARY.md | Markdown | {size} | {date} |
| Topic Summary | 02-meetings/meeting-docs/by-topic/{topic}/TOPIC_SUMMARY.md | Markdown | {size} | {date} |
| Session Summary | 02-meetings/meeting-docs/.../SESSION_SUMMARY.md | Markdown | {size} | {date} |
| Transcript | 02-meetings/meeting-docs/.../TRANSCRIPT.md | Markdown | {size} | {date} |

### Phase 3: BRD Artifacts

| Artifact | Path | Type | Size | Last Modified |
|----------|------|------|------|---------------|
| BRD | 03-brd/BRD.md | Markdown | {size} | {date} |

### Phase 4: Specification Artifacts

#### Interface Spec (if generated)

| Artifact | Path | Type | Size | Last Modified |
|----------|------|------|------|---------------|
| Requirements | 04-specifications/interface/requirements.md | Markdown | {size} | {date} |
| Design | 04-specifications/interface/design.md | Markdown | {size} | {date} |
| Tasks | 04-specifications/interface/tasks.md | Markdown | {size} | {date} |
| DoR Audit | 04-specifications/interface/dor_audit_result.json | JSON | {size} | {date} |

#### Function Spec (if generated)

| Artifact | Path | Type | Size | Last Modified |
|----------|------|------|------|---------------|
| Requirements | 04-specifications/function/requirements.md | Markdown | {size} | {date} |
| Design | 04-specifications/function/design.md | Markdown | {size} | {date} |
| Tasks | 04-specifications/function/tasks.md | Markdown | {size} | {date} |
| DoR Audit | 04-specifications/function/dor_audit_result.json | JSON | {size} | {date} |

#### Report Spec (if generated)

| Artifact | Path | Type | Size | Last Modified |
|----------|------|------|------|---------------|
| Requirements | 04-specifications/report/requirements.md | Markdown | {size} | {date} |
| Design | 04-specifications/report/design.md | Markdown | {size} | {date} |
| Tasks | 04-specifications/report/tasks.md | Markdown | {size} | {date} |
| DoR Audit | 04-specifications/report/dor_audit_result.json | JSON | {size} | {date} |

#### PRD (if generated)

| Artifact | Path | Type | Size | Last Modified |
|----------|------|------|------|---------------|
| PRD | 04-specifications/prd/PRD.md | Markdown | {size} | {date} |

### Phase 5: Handoff Artifacts

| Artifact | Path | Type | Size | Last Modified |
|----------|------|------|------|---------------|
| README | README.md | Markdown | {size} | {date} |
| Handoff Checklist | HANDOFF_CHECKLIST.md | Markdown | {size} | {date} |
| Traceability Matrix | TRACEABILITY_MATRIX.md | Markdown | {size} | {date} |
| Artifact Index | ARTIFACT_INDEX.md | Markdown | {size} | {date} |
| Workflow State | metadata/workflow-state.json | JSON | {size} | {date} |
| Generation Log | metadata/generation-log.md | Markdown | {size} | {date} |
| Statistics | metadata/statistics.json | JSON | {size} | {date} |

---

## 📊 Artifact Statistics

### By Type
- **Markdown Documents**: {md-count} ({md-size})
- **JSON Files**: {json-count} ({json-size})
- **Total**: {total-count} ({total-size})

### By Phase
- **Phase 1**: {p1-count} artifacts ({p1-size})
- **Phase 2**: {p2-count} artifacts ({p2-size})
- **Phase 3**: {p3-count} artifacts ({p3-size})
- **Phase 4**: {p4-count} artifacts ({p4-size})
- **Phase 5**: {p5-count} artifacts ({p5-size})

---

## 🔗 Artifact Relationships

```
BRD (Phase 3)
├─ Sourced from: BA Specs (Phase 1)
├─ Sourced from: Meeting Docs (Phase 2)
└─ Feeds into: Specifications (Phase 4)

Specifications (Phase 4)
├─ Sourced from: BRD (Phase 3)
├─ Referenced: BA Specs (Phase 1)
└─ Outputs: Implementation Tasks

Handoff Package (Phase 5)
├─ Includes: All Phase 1-4 artifacts
└─ Generates: Traceability and checklists
```

---

## 📝 Usage Guide

### Finding Specific Information

- **Business Requirements**: Start with `03-brd/BRD.md`
- **Technical Requirements**: Check `04-specifications/{spec-type}/requirements.md`
- **Architecture Decisions**: Review `04-specifications/{spec-type}/design.md`
- **Implementation Tasks**: See `04-specifications/{spec-type}/tasks.md`
- **Requirements Tracing**: Use `TRACEABILITY_MATRIX.md`
- **Meeting Context**: Browse `02-meetings/meeting-docs/`

### Navigating the Package

1. **Top-Down** (Business → Technical):
   - BRD → Specs → Tasks

2. **Bottom-Up** (Task → Requirement):
   - Task → Design → Requirements → BRD

3. **By Phase**:
   - Follow directory structure: `01-analysis/` → `02-meetings/` → `03-brd/` → `04-specifications/`

---

*Generated by requirements-workflow-skill v1.0.0*
*Index methodology: Recursive directory scan with metadata extraction*
```

### Step 7: 生成元數據文件

**metadata/statistics.json**:
```json
{
  "package_info": {
    "project_name": "{project-name}",
    "workflow_id": "{workflow-id}",
    "generated_at": "{ISO-8601-timestamp}",
    "generator": "requirements-workflow-skill v1.0.0"
  },
  "phase_statistics": {
    "phase1_analysis": {
      "completed": true,
      "artifacts_count": 4,
      "total_size_bytes": 12345,
      "dor_status": "PASSED"
    },
    "phase2_meetings": {
      "completed": true,
      "artifacts_count": 8,
      "total_size_bytes": 23456,
      "session_count": 3
    },
    "phase3_brd": {
      "completed": true,
      "artifacts_count": 1,
      "total_size_bytes": 5678,
      "sections_count": 8
    },
    "phase4_specifications": {
      "completed": true,
      "spec_types": ["interface", "function"],
      "artifacts_count": 8,
      "total_size_bytes": 34567
    },
    "phase5_handoff": {
      "completed": true,
      "artifacts_count": 7,
      "total_size_bytes": 8901
    }
  },
  "requirements_statistics": {
    "total_requirements": 45,
    "functional_requirements": 32,
    "non_functional_requirements": 13,
    "traced_requirements": 43,
    "untraced_requirements": 2,
    "traceability_coverage_percent": 95.6
  },
  "artifact_statistics": {
    "total_count": 28,
    "markdown_files": 24,
    "json_files": 4,
    "total_size_bytes": 85947,
    "total_size_human": "84 KB"
  },
  "quality_metrics": {
    "dor_audits_passed": 3,
    "dor_audits_failed": 0,
    "documents_reviewed": 28,
    "traceability_validated": true
  }
}
```

**metadata/generation-log.md**:
```markdown
# Generation Log

**Project**: {project-name}  
**Workflow ID**: {workflow-id}  
**Generated**: {ISO-8601-timestamp}

---

## Execution Timeline

| Timestamp | Phase | Action | Status |
|-----------|-------|--------|--------|
| {time} | Phase 1 | BA analysis started | ✅ |
| {time} | Phase 1 | DoR audit completed | ✅ PASSED |
| {time} | Phase 2 | Meeting documentation started | ✅ |
| {time} | Phase 2 | Meeting docs organized | ✅ |
| {time} | Phase 3 | BRD generation started | ✅ |
| {time} | Phase 3 | BRD validation completed | ✅ |
| {time} | Phase 4 | Spec generation started (interface) | ✅ |
| {time} | Phase 4 | Spec validation completed (interface) | ✅ |
| {time} | Phase 4 | Spec generation started (function) | ✅ |
| {time} | Phase 4 | Spec validation completed (function) | ✅ |
| {time} | Phase 5 | Handoff package creation started | ✅ |
| {time} | Phase 5 | All artifacts collected | ✅ |
| {time} | Phase 5 | Documentation generated | ✅ |
| {time} | Phase 5 | Package validation completed | ✅ |

---

## Workflow Events

### Phase 1: Analysis
- **Started**: {timestamp}
- **Completed**: {timestamp}
- **Duration**: {duration}
- **Artifacts Generated**: 4
- **Status**: ✅ SUCCESS

### Phase 2: Meeting Documentation
- **Started**: {timestamp}
- **Completed**: {timestamp}
- **Duration**: {duration}
- **Sessions Documented**: 3
- **Artifacts Generated**: 8
- **Status**: ✅ SUCCESS

### Phase 3: BRD Generation
- **Started**: {timestamp}
- **Completed**: {timestamp}
- **Duration**: {duration}
- **Input Sources**: BA specs, meeting docs
- **Sections Generated**: 8
- **Status**: ✅ SUCCESS

### Phase 4: Specification Generation
- **Started**: {timestamp}
- **Completed**: {timestamp}
- **Duration**: {duration}
- **Spec Types**: interface, function
- **Artifacts Generated**: 8
- **Status**: ✅ SUCCESS

### Phase 5: Handoff Package
- **Started**: {timestamp}
- **Completed**: {timestamp}
- **Duration**: {duration}
- **Documents Generated**: 7
- **Status**: ✅ SUCCESS

---

## Errors and Warnings

### Warnings
- {timestamp} - Phase 2: No meeting docs found, proceeding without
- {timestamp} - Phase 4: Report spec not requested, skipping

### Errors
- None

---

## Validation Results

### Artifact Validation
- ✅ All required artifacts present
- ✅ All files readable and well-formed
- ✅ Symlinks valid
- ✅ Directory structure correct

### Content Validation
- ✅ BRD 8 sections complete
- ✅ All specs passed DoR audit
- ✅ Requirements traceability > 95%
- ✅ Handoff checklist complete

---

*Log generated by requirements-workflow-skill v1.0.0*
```

### Step 8: 更新工作流程狀態 (Final)

**最終狀態**:
```json
{
  "workflow_id": "{project-name}-{timestamp}",
  "project": "{project-name}",
  "current_phase": 5,
  "status": "COMPLETE",
  "phases_complete": {
    "phase1_analysis": true,
    "phase2_meeting": true,
    "phase3_brd": true,
    "phase4_spec": true,
    "phase5_handoff": true
  },
  "artifacts": {
    "ba_specs": ".opencode/ba-specs/{project-name}/",
    "meeting_docs": ".opencode/ba-meetings/",
    "brd": ".opencode/ba-specs/{project-name}/brd/BRD.md",
    "specs": {
      "interface": ".opencode/ba-specs/{project-name}/interface/",
      "function": ".opencode/ba-specs/{project-name}/function/"
    },
    "handoff_package": ".opencode/handoff/{project-name}/"
  },
  "completed_at": "{ISO-8601-timestamp}",
  "total_duration": "{duration}",
  "last_update": "{ISO-8601-timestamp}"
}
```

## 輸出 (Outputs)

### 主要交付物

完整的交付包，位於 `.opencode/handoff/{project-name}/`，包含:

1. **文件 (7 files)**:
   - README.md
   - HANDOFF_CHECKLIST.md
   - TRACEABILITY_MATRIX.md
   - ARTIFACT_INDEX.md
   - metadata/workflow-state.json
   - metadata/generation-log.md
   - metadata/statistics.json

2. **交付物目錄 (4 directories)**:
   - 01-analysis/ (symlink to ba-specs)
   - 02-meetings/ (symlink to meeting-docs, if applicable)
   - 03-brd/ (copy of BRD.md)
   - 04-specifications/ (symlinks to all specs)

### 輸出驗證

- ✅ 所有必要目錄已建立
- ✅ 所有 symlinks 有效
- ✅ 所有文件已生成
- ✅ 追溯矩陣完整
- ✅ 統計資訊正確
- ✅ 工作流程狀態標記為 COMPLETE

## 錯誤處理 (Error Handling)

### 錯誤情境與處理

| 錯誤代碼 | 情境 | 處理方式 |
|---------|------|---------|
| `ERR_MISSING_ARTIFACTS` | 缺少必要交付物 | 列出缺失項目，建議回到對應 Phase |
| `ERR_DIRECTORY_CREATION_FAILED` | 無法建立目錄 | 檢查權限和磁碟空間 |
| `ERR_SYMLINK_FAILED` | Symlink 建立失敗 | 檢查目標路徑是否存在 |
| `ERR_FILE_GENERATION_FAILED` | 文件生成失敗 | 報告具體錯誤，提供除錯建議 |
| `ERR_TRACEABILITY_INCOMPLETE` | 追溯性不完整 | 報告缺失的追溯鏈，建議補充 |

### 錯誤訊息範例

```markdown
❌ **錯誤: 缺少必要交付物**

以下交付物缺失，無法完成 handoff 打包:
- ❌ BRD (Phase 3)
- ❌ 技術規格 (Phase 4)

**建議操作**:
1. 執行 Phase 3 生成 BRD: `"生成 BRD"`
2. 執行 Phase 4 生成技術規格: `"生成 Interface Spec"`
3. 完成後再執行 Phase 5: `"進入 Phase 5"`

**或者**:
- 如果確定要跳過缺失項目: `"強制打包（不完整）"`
- 警告: 不完整的交付包可能無法滿足開發需求
```

## 下一步建議 (Next Step Suggestion)

### 成功完成時

```markdown
🎉 **Workflow Complete: 需求管理流程已完成！**

**交付包位置**: `.opencode/handoff/{project-name}/`

---

### 📦 交付包內容

✅ **完整文檔**:
- README.md - 交付包總覽
- HANDOFF_CHECKLIST.md - 交付檢查清單
- TRACEABILITY_MATRIX.md - 需求追溯矩陣
- ARTIFACT_INDEX.md - 交付物索引

✅ **所有交付物**:
- Phase 1: BA 需求分析
- Phase 2: 會議記錄
- Phase 3: 商業需求文件 (BRD)
- Phase 4: 技術規格

✅ **元數據**:
- 工作流程狀態快照
- 生成日誌
- 統計資訊

---

### 📊 專案統計

- **總計階段**: 5/5 完成
- **文件數量**: {doc-count}
- **需求追溯性**: {coverage}%
- **交付包大小**: {size}

---

### 🎯 下一步行動

#### For Project Managers:
1. 📋 Review `HANDOFF_CHECKLIST.md`
2. ✍️ Sign off on deliverables
3. 📧 Distribute to development team

#### For Technical Leads:
1. 📖 Review `04-specifications/`
2. 🏗️ Plan sprint breakdown
3. 👥 Assign tasks to developers

#### For Developers:
1. 📝 Read `04-specifications/{spec-type}/tasks.md`
2. 🔍 Reference `design.md` for architecture
3. 🚀 Start implementation

---

### 📁 Quick Access

```bash
# Navigate to handoff package
cd ~/.opencode/handoff/{project-name}/

# View README
cat README.md

# Check handoff checklist
cat HANDOFF_CHECKLIST.md

# Review traceability
cat TRACEABILITY_MATRIX.md

# Browse artifacts
ls -la 01-analysis/
ls -la 02-meetings/
ls -la 03-brd/
ls -la 04-specifications/
```

---

### 🔄 Workflow Options

**If you need to make changes**:
- Modify artifacts: Edit source files in `.opencode/ba-specs/`, etc.
- Regenerate handoff: `"重新生成交付包"`

**To archive this workflow**:
- Package for distribution: `"打包交付包為 .tar.gz"`
- Move to archive: `"歸檔此工作流程"`

---

**🎊 Congratulations! Your requirements are ready for development.**

**Workflow Tool**: requirements-workflow-skill v1.0.0  
**Total Duration**: {total-duration}  
**Completion Time**: {ISO-8601-timestamp}
```

### 部分失敗時

```markdown
⚠️ **Phase 5 完成（部分）: 交付包已生成，但有缺失項目**

**交付包位置**: `.opencode/handoff/{project-name}/`

---

### ⚠️ 缺失的交付物

- ❌ {missing-item-1}
- ❌ {missing-item-2}

---

### ✅ 已包含的交付物

- ✅ {included-item-1}
- ✅ {included-item-2}
- ✅ {included-item-3}

---

### 🔧 建議操作

1. **補充缺失項目**:
   - 執行 Phase {X}: `"生成 {missing-item}"`
   - 重新生成交付包: `"重新生成交付包"`

2. **接受不完整交付**:
   - 在 HANDOFF_CHECKLIST.md 中標記缺失項目
   - 告知開發團隊哪些文件缺失

3. **稍後補充**:
   - 保留當前交付包
   - 之後生成缺失項目並更新

---

**警告**: 不完整的交付包可能影響開發效率。建議補充所有必要文件後再正式交付。
```

## 與其他 Phase 的整合

### 輸入依賴
- **所有前置 Phases (1-4)**: 提供所有交付物

### 工作流程結束
- Phase 5 完成後，整個 A→B→C 工作流程結束
- 工作流程狀態標記為 COMPLETE
- 可選: 歸檔或打包交付包

## 時間估算 (Time Estimates)

| 步驟 | 預估時間 |
|------|---------|
| 驗證交付物存在 | 1 分鐘 |
| 建立目錄結構 | 2 分鐘 |
| 生成 README.md | 2 分鐘 |
| 生成 HANDOFF_CHECKLIST.md | 2 分鐘 |
| 生成 TRACEABILITY_MATRIX.md | 5-8 分鐘 |
| 生成 ARTIFACT_INDEX.md | 3 分鐘 |
| 生成元數據文件 | 2 分鐘 |
| 驗證與狀態更新 | 1 分鐘 |
| **總計** | **18-23 分鐘** |

*實際時間取決於專案複雜度和交付物數量*

## 參考文件

- **Workflow State**: `.opencode/workflow/{project}/state.json`
- **BA Analyst Outputs**: `.opencode/ba-specs/{project}/`
- **BRD**: `.opencode/ba-specs/{project}/brd/BRD.md`
- **Specifications**: `.opencode/ba-specs/{project}/{spec-type}/` 或 `.opencode/prd/{project}/`

---

*最後更新: 2026-02-06*
*Phase 狀態: COMPLETE*

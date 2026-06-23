# NAELT Evidence Labeling Guide

**Status:** PROVISIONAL - Framework for mixed-mode CIS documentation

---

## Overview

This document explains the evidence labeling system used throughout NAELT's provisional Corporate Identity System (CIS). The mixed-mode approach acknowledges that not all brand guidance has equal evidentiary support.

---

## Label Definitions

### CONFIRMED

**Meaning:** Directly verifiable from organizational seed data, configuration files, or documented decisions.

**Characteristics:**
- Has clear, traceable source in repository
- Can be independently verified
- No interpretation or inference required
- Represents explicit organizational decisions

**Examples:**
- Organization name and founding year
- Mission statement text
- Core values and their definitions
- Service categories and descriptions
- Legislative appeals content
- Color hex values in config files
- Typography font family specifications

**Usage Confidence:** High - Safe to apply as organizational fact

**Documentation Requirement:**
- Cite specific source file and field/line
- Include direct quote or value when helpful
- Note date of confirmation if relevant

---

### DERIVED

**Meaning:** Logically inferred from multiple consistent evidence sources.

**Characteristics:**
- Based on interpretation of confirmed data
- Multiple evidence points converge on conclusion
- Reasonable professional judgment applied
- Consistent with organizational identity

**Examples:**
- Organizational culture characteristics
- Tone of voice guidelines
- Stakeholder communication principles
- Service visual identity codes
- Advocacy messaging framework
- UI pattern applications
- Typography hierarchy sizing

**Usage Confidence:** Medium-High - Reasonable working guidance

**Documentation Requirement:**
- List source evidence files
- Explain inference logic
- Note any assumptions made
- Indicate where validation may be needed

---

### PROVISIONAL

**Meaning:** Reasonable working assumption pending formal source material.

**Characteristics:**
- Based on general best practices or partial evidence
- Lacks complete organizational source documentation
- Provides functional guidance for immediate use
- May change when formal sources obtained

**Examples:**
- Social media posting frequency
- Email marketing schedules
- Channel-specific best practices
- Content calendar recommendations
- Metrics and KPI targets
- Cross-channel consistency rules

**Usage Confidence:** Medium - Functional but requires validation

**Documentation Requirement:**
- Label clearly as provisional
- Note what formal source material would be needed
- Indicate confidence level
- Suggest review timeframe

---

### UNAVAILABLE

**Meaning:** Formal rules exist but source material not accessible.

**Characteristics:**
- Topic is relevant to brand governance
- Organization likely has or needs formal standards
- Current evidence insufficient for guidance
- Requires external source material

**Examples:**
- Print color specifications (CMYK/PMS)
- Logo clear space and minimum size rules
- Official master logo files
- Formal brand governance protocols
- Trademark usage guidelines
- Print production specifications

**Usage Confidence:** N/A - Cannot provide guidance without sources

**Documentation Requirement:**
- Clearly state what is unavailable
- Explain why it's needed
- Specify what source material would satisfy requirement
- Provide interim guidance if safe to do so

---

## Label Application Guidelines

### When to Use Each Label

| Situation | Label | Rationale |
|-----------|-------|-----------|
| Direct quote from config file | CONFIRMED | Unambiguous source |
| Logical inference from multiple facts | DERIVED | Reasoned conclusion |
| Industry best practice applied to NAELT | PROVISIONAL | Functional assumption |
| Known to exist but no access | UNAVAILABLE | Source gap identified |

### Mixed Label Scenarios

Documents may contain multiple labels when different sections have different evidentiary bases:

**Example:** Service Framework document
- Service descriptions: CONFIRMED (from services.json)
- Visual identity notes: DERIVED (from cross-referencing)

**Example:** Digital Expression document
- Color hex values: CONFIRMED (from manifest.json)
- Typography hierarchy: DERIVED (from application patterns)
- Component patterns: DERIVED (from CSS analysis)

---

## Evidence Hierarchy

### Primary Sources (Highest Confidence)

1. **Seed Data Files**
   - `organization-info.json`
   - `services.json`
   - `core-appeals.json`
   - `events.json`

2. **Configuration Files**
   - `site.json`
   - `manifest.json`

3. **Verified Assets**
   - Logo SVG files
   - Favicon SVG files

### Secondary Sources (Supporting Evidence)

1. **Implementation Files**
   - Theme CSS files
   - Component styles
   - Layout templates

2. **Documentation**
   - Training guides
   - Process documentation
   - Design specifications

### Tertiary Sources (Contextual)

1. **General Best Practices**
   - Industry standards
   - WCAG guidelines
   - Design principles

2. **Professional Judgment**
   - Cross-reference synthesis
   - Logical inference
   - Pattern recognition

---

## Working with Mixed Evidence

### For Brand Practitioners

**When Applying CONFIRMED Rules:**
- Apply directly as organizational fact
- Reference sources when questioned
- Safe for all applications

**When Applying DERIVED Rules:**
- Apply as reasonable guidance
- Note that they represent professional interpretation
- Acceptable for most applications
- Review if organizational context changes significantly

**When Applying PROVISIONAL Rules:**
- Apply as working assumptions
- Validate with stakeholders when possible
- Note limitations in formal communications
- Update when formal guidance obtained

**When Encountering UNAVAILABLE Items:**
- Request formal source material
- Use professional judgment for interim solutions
- Clearly mark as unofficial
- Escalate for formal decisions

### For Stakeholders Reviewing This CIS

**Questions to Ask:**
1. Does this guidance align with organizational intent?
2. Are CONFIRMED facts accurate?
3. Are DERIVED inferences reasonable?
4. Should PROVISIONAL assumptions be formalized?
5. Can UNAVAILABLE items be sourced?

**Feedback Priority:**
1. **High:** CONFIRMED facts that appear incorrect
2. **High:** DERIVED inferences that seem off-brand
3. **Medium:** PROVISIONAL rules that need adjustment
4. **Medium:** Providing UNAVAILABLE source material

---

## Documentation Standards

### Required for Each Reference Document

**Header Information:**
```
# Document Title

**Status:** [LABEL] (from source files)
```

**Source Citations:**
```
**Source:** `filename.json` [CONFIRMED] - Specific field
```

**Inference Explanations:**
```
**Rationale [DERIVED]:** Based on [evidence A] + [evidence B], 
reasonable conclusion is [conclusion].
```

**Provisional Notes:**
```
**Note [PROVISIONAL]:** Based on industry best practices. 
Formal organizational guidance would strengthen this recommendation.
```

**Unavailable Acknowledgments:**
```
**Status [UNAVAILABLE]:** Formal specifications not accessible. 
Source needed: [specific material needed]
```

---

## Updating Evidence Labels

### Promotion Pathways

```
PROVISIONAL → DERIVED → CONFIRMED
     ↑              ↑
  (validation)  (formal source found)

UNAVAILABLE → CONFIRMED
       ↑
(formal source obtained)
```

### When to Revisit Labels

| Trigger | Action |
|---------|--------|
| New source material obtained | Re-evaluate related labels |
| Organizational changes | Review affected guidance |
| Stakeholder feedback | Assess label appropriateness |
| Periodic review (annual) | Validate all PROVISIONAL items |

---

## Quality Assurance

### Self-Check Questions

Before finalizing any guidance:

1. **Source Traceability:** Can every claim be traced to evidence?
2. **Label Accuracy:** Is the label appropriate for the evidence strength?
3. **Transparency:** Would users understand the basis for guidance?
4. **Consistency:** Are similar items labeled consistently?
5. **Completeness:** Are UNAVAILABLE gaps clearly identified?

### Review Checklist

- [ ] All CONFIRMED items have specific source citations
- [ ] All DERIVED items explain inference logic
- [ ] All PROVISIONAL items note validation needs
- [ ] All UNAVAILABLE items specify required sources
- [ ] Mixed documents clearly indicate label boundaries
- [ ] No claims without appropriate labels

---

## Communication to Users

### Standard Disclaimers

**For Documents with Mixed Labels:**
> "This document contains guidance with varying levels of evidentiary support. Items labeled CONFIRMED are directly verifiable from organizational data. Items labeled DERIVED are reasonable inferences. Items labeled PROVISIONAL are working assumptions. Items labeled UNAVAILABLE require formal source material."

**For Documents with PROVISIONAL Content:**
> "This document provides provisional guidance based on current evidence and best practices. Formal organizational validation is recommended for compliance-critical applications."

**For UNAVAILABLE Items:**
> "[Specific item] requires formal source material not currently accessible. Please obtain official [specifications/guidelines/assets] from [appropriate source] before proceeding."

---

## Evidence Sources

This labeling framework itself is:

- **Structure:** PROVISIONAL - Based on documentation best practices
- **Definitions:** PROVISIONAL - Professional judgment framework
- **Application:** Derived from actual evidence analysis in this CIS

---

**Document Version:** 1.0.0
**Status:** PROVISIONAL framework for mixed-mode CIS documentation
**Last Updated:** 2026-03-25

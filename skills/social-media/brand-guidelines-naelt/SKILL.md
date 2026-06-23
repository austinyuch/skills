---
name: brand-guidelines-naelt
description: Provisional organization-level CIS for NAELT (National Association for Equal Life Treatment / 生命權平等協會). Provides mixed-mode brand guidance covering mission/values, stakeholder positioning, advocacy posture, service identity, and digital expression. When users mention "NAELT brand", "NAELT CIS", "生命權平等協會品牌", or request brand-aligned outputs for this victim-rights advocacy NGO. NOT a formal official brand manual; clearly labels CONFIRMED, DERIVED, PROVISIONAL, and UNAVAILABLE rules.
---

# NAELT Provisional Organization-Level CIS

## Status Declaration

This document provides **provisional organization-level brand guidance** for NAELT (生命權平等協會 / National Association for Equal Life Treatment). It is built from current repository evidence, user-provided materials, and organizational context, **not** a formal official brand manual approved by governing bodies.

**Evidence boundary note:** within this skill, `CONFIRMED` means confirmed inside the current repository or directly supplied workspace materials. It does **not** mean formally ratified by NAELT governing bodies unless explicitly stated. In this session, the justice-emblem logo supplied at `temp/naelt-logo.jpg` has been explicitly confirmed by the user as the **official primary logo**.

**Mixed-Mode Evidence Labels:**

| Label | Meaning | Usage |
|-------|---------|-------|
| **CONFIRMED** | Directly verifiable from organizational seed data, config files, or documented decisions | Core identity elements like mission, values, service categories |
| **DERIVED** | Logically inferred from multiple consistent evidence sources | Visual patterns, tone of voice, advocacy positioning |
| **PROVISIONAL** | Reasonable working assumption pending formal source material | Channel-specific adaptations, stakeholder messaging tiers |
| **UNAVAILABLE** | Formal rules exist but source material not accessible | Print specifications, official logo variants, governance protocols |

---

## 1. Organizational Identity

### 1.1 Core Identity [CONFIRMED]

| Element | Value | Evidence Source |
|---------|-------|-----------------|
| **Organization Name (Chinese)** | 生命權平等協會 | `organization-info.json` |
| **Organization Name (English)** | National Association for Equal Life Treatment (NAELT) | `organization-info.json` |
| **Legal Form** | Non-profit organization (NPO) | `organization-info.json` context |
| **Founded** | 2015 | `organization-info.json` history |
| **Mission Focus** | Victims' rights advocacy, judicial reform, victim support services | `organization-info.json` mission statement |

### 1.2 Mission Statement [CONFIRMED]

> NAELT is committed to:
> - Advocating for the rights and dignity of crime victims and their families
> - Promoting comprehensive victim protection legislation
> - Providing holistic support services for victims
> - Raising societal awareness and understanding of victim issues
> - Building a victim-friendly social environment

**Source:** `organization-info.json` mission field

### 1.3 Vision [CONFIRMED]

NAELT envisions a society where:
- Every crime victim receives fair treatment
- Victim rights are protected by comprehensive legal frameworks
- The public understands and respects victims
- Victims receive complete support to rebuild their lives

**Source:** `organization-info.json` vision field

### 1.4 Core Values [CONFIRMED]

| Value | Chinese | Definition | Icon Reference |
|-------|---------|------------|----------------|
| **Respect** | 尊重 | Respecting each victim's dignity, feelings, and choices; victim-centered service approach | heart |
| **Justice** | 公義 | Pursuing judicial justice and advocating for fair treatment and reasonable compensation for victims | scale |
| **Empathy** | 同理 | Understanding victims' circumstances with empathy; providing warm yet professional support | hands-helping |
| **Professionalism** | 專業 | Serving victims with professional knowledge and skills; continuously improving service quality | certificate |
| **Advocacy** | 倡議 | Actively advocating for victim rights; promoting institutional reform and social progress | bullhorn |

**Source:** `organization-info.json` coreValues array

---

## 2. Stakeholder & Audience Framework

### 2.1 Primary Stakeholders [DERIVED]

| Stakeholder Group | Description | Relationship Priority |
|-------------------|-------------|----------------------|
| **Direct Beneficiaries** | Crime victims and their families (spouses, direct relatives, legal guardians) | Primary service recipients |
| **Legal Professionals** | Lawyers, prosecutors, judges engaged in victim rights work | Collaboration and referral partners |
| **Social Workers & Counselors** | Frontline support professionals | Service delivery partners |
| **Policy Makers** | Legislators, government officials in justice and social welfare departments | Advocacy targets |
| **General Public** | Citizens interested in judicial reform and victim rights | Awareness and support base |
| **Volunteers** | Individuals committed to victim support work | Operational capacity |
| **Donors** | Individual and institutional supporters | Financial sustainability |

### 2.2 Stakeholder Communication Principles [PROVISIONAL]

**Tone Guidelines by Stakeholder:**

| Stakeholder | Tone | Key Messages |
|-------------|------|--------------|
| Victims/Families | Warm, respectful, empowering | "You are not alone"; "Your voice matters" |
| Legal/Professional | Precise, evidence-based, collaborative | Legal frameworks, best practices, partnership |
| Policy Makers | Policy-focused, solution-oriented | Legislative priorities, implementation pathways |
| Public Supporters | Accessible, educational, action-oriented | "Learn more"; "Join us"; "Make a difference" |

---

## 3. Advocacy Posture & Positioning

### 3.1 Core Advocacy Areas [CONFIRMED]

NAELT's "Nine Major Legislative Appeals" (九大修法訴求) include:

1. Strengthening victim participation rights in litigation
2. Establishing victim protection order system
3. Improving victim compensation mechanisms
4. Strengthening victim privacy protection
5. Building comprehensive victim support service networks
6. Promoting restorative justice systems
7. Enhancing economic security for victims
8. Strengthening psychological support services
9. Raising awareness of victim rights

**Source:** `core-appeals.json`

### 3.2 Advocacy Voice Characteristics [DERIVED]

| Characteristic | Expression | Avoid |
|----------------|------------|-------|
| **Resolute but not aggressive** | Clear position statements with professional backing | Emotional manipulation, inflammatory language |
| **Evidence-based** | Reference to legal frameworks, comparative law, statistics | Unsupported claims, purely emotional appeals |
| **Victim-centered** | Elevate victim voices and experiences | Speaking for victims without their input |
| **Solution-oriented** | Concrete proposals, implementation pathways | Problem-only statements without alternatives |
| **Collaborative** | Acknowledge partners, invite dialogue | Us-vs-them framing, blanket criticism |

### 3.3 Legislative Reference Framework [CONFIRMED]

Key laws referenced in advocacy:
- Criminal Procedure Law (刑事訴訟法)
- Crime Victim Protection Law (犯罪被害人保護法)
- Domestic Violence Prevention Act (家庭暴力防治法)
- Sexual Assault Prevention Act (性侵害犯罪防治法)
- Juvenile Incident Handling Act (少年事件處理法)

**Source:** `core-appeals.json` relatedLaws fields

---

## 4. Service Positioning

### 4.1 Service Categories [CONFIRMED]

NAELT provides six core service categories:

| Service | Category | Key Features |
|---------|----------|--------------|
| Legal Consultation | Legal Support | Free legal advice, rights education, procedure guidance |
| Psychological Counseling | Psychological Support | Trauma-informed therapy, professional clinical psychologists |
| Financial Assistance | Financial Aid | Emergency living support, medical expense aid, education subsidies |
| Court Accompaniment | Legal Support | Professional accompaniment, emotional support during proceedings |
| Support Groups | Community | Peer support circles, facilitated by professionals |
| Rights Advocacy | Advocacy | Individual case advocacy, policy reform, public awareness |

**Source:** `services.json`

### 4.2 Service Identity Principles [DERIVED]

**Visual Cues for Service Communication:**
- Legal services: Use formal, structured layouts with primary red emphasis
- Psychological services: Use softer layouts with warm accent colors
- Community services: Use inclusive imagery, group-oriented compositions
- Financial services: Use clear, transparent layouts emphasizing dignity

**Tone Across Services:**
- Professional but accessible
- Dignity-preserving (avoiding pity or sensationalism)
- Empowerment-focused

---

## 5. Digital Expression Guidelines

### 5.1 Digital Brand Presence [DERIVED]

NAELT maintains digital presence across:
- **Website**: Primary information and service portal
- **Facebook**: Community engagement, event announcements
- **Instagram**: Visual storytelling, awareness campaigns
- **YouTube**: Educational content, event recordings
- **LINE**: Direct communication, quick updates

**Source:** `organization-info.json` socialMedia field

### 5.2 Visual Identity System [CONFIRMED + DERIVED]

#### Color System

| Role | Entry Colors | UI Scale | Status |
|------|--------------|----------|--------|
| Primary | `#C53030` | 500: #E53E3E, 600: #B02A2A | **CONFIRMED** via config |
| Secondary | `#4A5568` | 600: #4A5568, 800: #1A202C | **CONFIRMED** via config |
| Accent | `#DD6B20` | 500: #DD6B20, 400: #ED8936 | **CONFIRMED** via config |

**Color Usage Principles [DERIVED]:**
- Primary red: Logo, main headlines, primary CTAs, advocacy visuals
- Secondary gray: Body text, stable backgrounds, secondary information
- Accent orange: Auxiliary highlights, warmth signals, supplementary CTAs
- Hero sections: Red-to-orange gradient for advocacy impact
- Cards/Content: White or light gray backgrounds for readability

**Source:** `site.json`, `manifest.json`, theme CSS files

#### Typography

| Role | Font | Status |
|------|------|--------|
| Sans/Body | Noto Sans TC | **CONFIRMED** via manifest |
| Serif/Headlines | Noto Serif TC | **CONFIRMED** via manifest |
| Mono/Technical | Fira Code | **CONFIRMED** via manifest |

**Typography Principles [DERIVED]:**
- Default to Noto Sans TC for body text and UI
- Use Noto Serif TC for main headlines, advocacy headers, and weighty passages
- Reserve Fira Code for technical content only
- Maintain WCAG AA contrast ratios

#### Logo Assets [CONFIRMED]

| Asset | Format | Status | Usage |
|-------|--------|--------|-------|
| Official Primary Logo | JPG / PNG / WebP | **CONFIRMED via user confirmation in current session** | Primary organizational logo |
| Website Lockup | SVG | **OBSERVED SECONDARY DIGITAL LOCKUP** | Secondary digital lockup for current website implementation |
| Favicon Mark | SVG | **OBSERVED DIGITAL SMALL MARK** | Small-scale identification |

**Logo Composition:**
- Circular justice emblem / medallion form
- Central balance scales of justice
- Dove above the scales
- Supporting hands below the scales
- Botanical / laurel-like framing elements

**Logo Status Note:** The justice emblem sourced from `temp/naelt-logo.jpg` is the official primary logo based on direct user confirmation in this session. The current website lockup (`logo.svg`) should be treated as a secondary digital lockup from the existing web implementation, not as the primary organizational mark.

**Source:** `temp/naelt-logo.jpg` (user-confirmed official primary logo), `logo.svg`, `favicon.svg`

### 5.3 UI/Component Patterns [DERIVED]

**Web-Specific Patterns (for digital outputs):**

| Component | Pattern | Usage |
|-----------|---------|-------|
| Hero Section | Red-orange gradient, white text | Homepage, major landing pages |
| CTA Section | Red gradient, strong contrast | Donation, volunteer signup |
| Primary Button | Red gradient, white text, subtle shadow | Main actions |
| Card | White bg, light border, soft shadow, hover lift | Content display |
| Navigation | White bg, red active states | Site navigation |
| Footer | Dark gray bg, white text | Site footer |

**Accessibility Requirements [CONFIRMED]:**
- WCAG 2.1 AA compliance
- Minimum 44px touch targets
- Clear focus indicators

**Source:** `config/site.json` accessibility.wcagLevel, theme CSS

---

## 6. Channel-Specific Guidelines

### 6.1 Website [CONFIRMED within current repo evidence]

- **Observed Domain in current config**: www.naelt.org
- **Supported Locales**: zh-TW (primary), en
- **Key Features**: Donation, volunteer registration, newsletter, search
- **Legal Info**: Organization number and tax ID exist in config; rendered footer placement not verified

**Source:** `site.json`

### 6.2 Social Media [PROVISIONAL]

**Facebook:**
- Post frequency: 2-3 times per week
- Best times: Weekdays 12:00-14:00, 19:00-21:00
- Content: Event announcements, appeal updates, news sharing

**Instagram:**
- Post frequency: 3-4 times per week
- Stories: 1-2 times daily
- Best times: Daily 12:00-13:00, 20:00-22:00
- Content: Visual appeals, event photos, quote graphics

**YouTube:**
- Content: Educational videos, event recordings, interviews

### 6.3 Print & Events [UNAVAILABLE]

The following require formal source material:
- Poster specifications (A3 sizes mentioned in specs but not formally approved)
- Print color specifications (CMYK/PMS)
- Official event banner templates
- Printed brochure layouts

---

## 7. Content & Messaging

### 7.1 Key Messaging Pillars [DERIVED]

| Pillar | Key Message | Supporting Points |
|--------|-------------|-------------------|
| **Justice** | Every victim deserves fair treatment | Legal reform, rights protection, judicial participation |
| **Support** | No victim should face this alone | Comprehensive services, professional help, peer support |
| **Change** | Together we can build a better system | Legislative advocacy, policy reform, public awareness |
| **Dignity** | Victims' voices matter | Respect, empowerment, centering victim experiences |

### 7.2 Language Guidelines [PROVISIONAL]

**Preferred Terms:**
- "犯罪被害人" (crime victim) - standard legal term
- "家屬" (family members) - inclusive of various family structures
- "權益" (rights and interests) - emphasizing legal standing
- "倡議" (advocacy) - proactive stance for change

**Terms to Avoid:**
- Sensationalizing language about victims
- Victim-blaming implications
- Overly clinical or detached language when discussing trauma
- Partisan political framing

---

## 8. Usage Workflows

### 8.1 Creating Brand-Aligned Outputs

**Step 1: Determine Output Type**
- Digital (web/UI) → Use full UI patterns from Section 5.3
- Print/documents → Use entry colors, typography hierarchy from Section 5.2
- Presentations → Use brand colors, logo, messaging pillars

**Step 2: Apply Evidence-Based Rules**
- Check status label (CONFIRMED/DERIVED/PROVISIONAL/UNAVAILABLE)
- For PROVISIONAL rules, note they may need validation
- For UNAVAILABLE items, request formal source material

**Step 3: Maintain Brand Voice**
- Review tone guidelines for target stakeholder (Section 2.2)
- Align with core values (Section 1.4)
- Check against messaging pillars (Section 7.1)

### 8.2 When to Request Formal Brand Manual

Request official brand guidelines when:
- Requirements include logo clear space, minimum sizes, safe areas
- Need for CMYK/PMS color specifications for professional printing
- Need for official white/monochrome logo variants
- External supplier/vendor needs official brand assets
- Large-scale production (conference materials, merchandise)
- Legal/compliance brand review requirements

---

## 9. Reference Documents

| Document | Purpose | Status |
|----------|---------|--------|
| `references/naelt-organizational-identity.md` | Detailed mission, values, history | **DERIVED** from seed data |
| `references/naelt-service-framework.md` | Service descriptions and positioning | **CONFIRMED** from services.json |
| `references/naelt-advocacy-positioning.md` | Legislative appeals and advocacy stance | **CONFIRMED** from core-appeals.json |
| `references/naelt-digital-expression.md` | Colors, typography, UI patterns | **CONFIRMED/DERIVED** from theme files |
| `references/naelt-channel-guidelines.md` | Channel-specific usage guidelines | **PROVISIONAL** |
| `references/evidence-labeling-guide.md` | How to apply and interpret status labels | **PROVISIONAL** |

---

## 10. Final Checklist

Before completing brand-aligned outputs:

- [ ] Output type determined and appropriate guidelines applied
- [ ] Status labels reviewed (CONFIRMED/DERIVED/PROVISIONAL/UNAVAILABLE)
- [ ] Colors use verified values from Section 5.2
- [ ] Typography follows hierarchy from Section 5.2
- [ ] Logo uses correct observed assets (Section 5.2)
- [ ] Tone matches stakeholder guidelines (Section 2.2)
- [ ] Messaging aligns with pillars (Section 7.1)
- [ ] No unsupported formal-brand claims made
- [ ] Users informed when UNAVAILABLE items are encountered

---

**Document Version:** 2.0.0 (Organization-Level Provisional CIS)
**Last Updated:** 2026-03-25
**Status:** Provisional - Mixed-mode evidence boundaries applied
**Evidence Base:** Repository analysis of NAELT site implementation

**Important Note:** This is a provisional guidance document built from digital evidence, not a formal official brand manual. For compliance-critical or large-scale production needs, obtain formal brand documentation from NAELT governing bodies.

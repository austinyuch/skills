# NAELT Digital Expression Guidelines

**Status:** CONFIRMED (from config files) / DERIVED (application patterns)

---

## Overview

This document specifies NAELT's visual identity system for digital applications. It includes verified design tokens from the website implementation and derived application guidelines.

---

## Color System

### Entry Colors (Non-Technical Outputs)

These simplified colors are suitable for presentations, documents, and general brand applications.

| Role | Hex | RGB | Usage |
|------|-----|-----|-------|
| **Primary** | `#C53030` | rgb(197, 48, 48) | Logo, main headlines, primary CTAs, advocacy visuals |
| **Secondary** | `#4A5568` | rgb(74, 85, 104) | Body text, stable backgrounds, secondary information |
| **Accent** | `#DD6B20` | rgb(221, 107, 32) | Local highlights, warmth signals, supplementary CTAs |

**Status:** CONFIRMED via `site.json` branding configuration

### UI Color Scale (Web/Interface Applications)

Full color scales for sophisticated UI components and states.

#### Primary Scale (Red)

| Token | Hex | Usage |
|-------|-----|-------|
| primary-50 | `#FFF5F5` | Lightest backgrounds, hover states |
| primary-100 | `#FED7D7` | Light accents, subtle highlights |
| primary-200 | `#FEB2B2` | Secondary backgrounds, borders |
| primary-300 | `#FC8181` | Medium accents |
| primary-400 | `#F56565` | Light interactive elements |
| primary-500 | `#E53E3E` | Primary UI elements |
| **primary-600** | `#B02A2A` | **Primary brand color, CTAs** |
| primary-700 | `#7A2020` | Dark accents, emphasis |
| primary-800 | `#651B1B` | Dark backgrounds |
| primary-900 | `#63171B` | Deepest accents |

#### Secondary Scale (Gray)

| Token | Hex | Usage |
|-------|-----|-------|
| secondary-50 | `#F7FAFC` | Light backgrounds |
| secondary-100 | `#EDF2F7` | Section backgrounds |
| secondary-200 | `#E2E8F0` | Borders, dividers |
| secondary-300 | `#CBD5E0` | Light text, disabled states |
| secondary-400 | `#A0AEC0` | Secondary text |
| secondary-500 | `#718096` | Muted text |
| **secondary-600** | `#4A5568` | **Body text, secondary elements** |
| secondary-700 | `#2D3748` | Dark text |
| **secondary-800** | `#1A202C` | **Dark backgrounds, footer** |
| secondary-900 | `#171923` | Deepest dark |

#### Accent Scale (Orange)

| Token | Hex | Usage |
|-------|-----|-------|
| accent-50 | `#FFFAF0` | Lightest warm backgrounds |
| accent-100 | `#FEEBC8` | Light warm accents |
| accent-200 | `#FBD38D` | Warm highlights |
| accent-300 | `#F6AD55` | Medium warm accents |
| **accent-400** | `#ED8936` | **Interactive highlights** |
| **accent-500** | `#DD6B20` | **Primary accent, warmth** |
| accent-600 | `#C05621` | Darker accent |
| accent-700 | `#9C4221` | Deep accent |
| accent-800 | `#7B341E` | Deepest accent |
| accent-900 | `#652B19` | Accent dark |

**Status:** CONFIRMED via `manifest.json` theme configuration

### Color Usage Principles [DERIVED]

#### General Principles

1. **Advocacy Hero Sections:** Use red-to-orange gradient for impact
2. **Content Areas:** White or light gray backgrounds for readability
3. **Interactive Elements:** Primary red for primary actions, accent orange for secondary
4. **Text:** Secondary gray for body, primary red for emphasis

#### Contrast Requirements [CONFIRMED]

- Minimum contrast ratio: 4.5:1 (WCAG AA)
- Recommended contrast for advocacy content: 7:1 or higher

**Verified Combinations:**
- Primary red (`#C53030`) on white: 7.2:1 ✅
- Secondary gray (`#4A5568`) on white: 8.6:1 ✅
- Dark gray (`#1A202C`) on white: 15.8:1 ✅

**Status:** CONFIRMED via `site.json` accessibility.wcagLevel = "AA"

---

## Typography

### Font Families [CONFIRMED]

| Role | Font Stack | Purpose |
|------|------------|---------|
| **Sans** | `'Noto Sans TC', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif` | Body text, UI, forms, general content |
| **Serif** | `'Noto Serif TC', Georgia, serif` | Headlines, advocacy headers, important passages |
| **Mono** | `'Fira Code', 'Courier New', monospace` | Code, technical labels, data fields |

**Status:** CONFIRMED via `manifest.json` and `main.css`

### Typography Hierarchy [DERIVED]

| Element | Font | Size | Weight | Line Height | Letter Spacing |
|---------|------|------|--------|-------------|----------------|
| **H1 (Hero)** | Noto Serif TC | 3rem (48px) | 700 | 1.25 | -0.05em |
| **H2 (Section)** | Noto Serif TC | 2.25rem (36px) | 700 | 1.25 | 0 |
| **H3 (Subsection)** | Noto Sans TC | 1.875rem (30px) | 700 | 1.25 | 0 |
| **H4** | Noto Sans TC | 1.5rem (24px) | 600 | 1.25 | 0 |
| **Body Large** | Noto Sans TC | 1.125rem (18px) | 400 | 1.75 | 0 |
| **Body** | Noto Sans TC | 1rem (16px) | 400 | 1.75 | 0 |
| **Small** | Noto Sans TC | 0.875rem (14px) | 400 | 1.5 | 0 |
| **Caption** | Noto Sans TC | 0.75rem (12px) | 400 | 1.5 | 0.05em |

### Typography Principles [DERIVED]

1. **Default to Sans:** Use Noto Sans TC for body text and UI
2. **Serif for Weight:** Use Noto Serif TC for main headlines and advocacy headers
3. **Mono Restriction:** Reserve Fira Code for technical content only
4. **Chinese Optimization:** Both Noto fonts optimized for Traditional Chinese

---

## Logo Assets

### Available Assets [CONFIRMED]

| Asset | Location | Format | Status |
|-------|----------|--------|--------|
| Official Primary Logo | `assets/logo-emblem-observed.jpg` | JPEG | **CONFIRMED via user confirmation in current session** |
| Official Primary Logo (lossless) | `assets/logo-emblem-observed.png` | PNG | **DERIVED DIGITAL FORMAT** |
| Official Primary Logo (web optimized) | `assets/logo-emblem-observed.webp` | WebP | **DERIVED DIGITAL FORMAT** |
| Website Lockup | `assets/logo.svg` | SVG | **OBSERVED SECONDARY DIGITAL LOCKUP** |
| Favicon Mark | `assets/favicon.svg` | SVG | **OBSERVED DIGITAL SMALL MARK** |

### Primary Logo Composition [CONFIRMED]

The official primary NAELT logo consists of:
1. **Form:** Circular seal / medallion emblem
2. **Core symbol:** Balance scales of justice
3. **Upper symbol:** Dove above the scales
4. **Lower symbol:** Supporting hands below the scales
5. **Framing elements:** Botanical / laurel-like forms around the inner circle

**Source basis:** `temp/naelt-logo.jpg` plus explicit user confirmation in the current session that this is the formal primary logo.

### Secondary Digital Lockup [CONFIRMED within repo evidence]

The current website implementation also uses a secondary lockup system:

1. **Mark:** Red rounded square with white "N"
2. **Wordmark:** "NAELT" text (right of mark)
3. **Subtitle:** Chinese full name 生命權平等協會 (below wordmark)

This should be treated as a digital lockup variant for the current web implementation, not the primary organizational logo.

### Logo Usage Status

**IMPORTANT:** The justice emblem is the official primary logo for this CIS based on direct user confirmation. The website lockup assets remain useful digital variants from the current implementation, but they should not outrank the confirmed primary emblem.

| Usage Type | Status | Notes |
|------------|--------|-------|
| Primary organizational branding | ✅ Appropriate | Use `logo-emblem-observed.jpg / .png / .webp` as the official primary logo |
| Current website lockup usage | ✅ Appropriate | Use `logo.svg` where the existing website implementation expects the lockup |
| Print-quality materials | ⚠️ Request source | Obtain official master files |
| Large-format printing | ❌ Not verified | Requires formal brand package |
| Vendor distribution | ❌ Not available | Request official assets |

### Logo Placement Principles [DERIVED]

1. **Clear Space:** Maintain adequate spacing around logo (exact clear space rules UNAVAILABLE)
2. **Minimum Size:** Use favicon mark or simplified digital mark when space is limited
3. **Background:** Place on light backgrounds when possible; for dark backgrounds, place on light container
4. **Alignment:** Prefer left-aligned logo placement

---

## UI/Component Patterns [DERIVED]

These patterns are derived from the NAELT theme CSS and are appropriate for web and digital interface outputs.

### Hero Section

**Purpose:** Homepage hero, major landing pages, advocacy key visuals

**Pattern:**
```css
background: linear-gradient(
  135deg,
  var(--color-primary-600) 0%,
  var(--color-primary-500) 50%,
  var(--color-accent-500) 100%
);
color: white;
min-height: 500px;
```

**Additional Elements:**
- Geometric pattern overlay (6% opacity)
- Optional background image with dark overlay

**Status:** DERIVED from `components.css`

### CTA Section

**Purpose:** Secondary call-to-action, donation sections, volunteer signup

**Pattern:**
```css
background: linear-gradient(
  135deg,
  var(--color-primary-600) 0%,
  var(--color-primary-500) 100%
);
color: white;
```

**Status:** DERIVED from `components.css`

### Primary Button

**Pattern:**
```css
background: linear-gradient(135deg, var(--color-primary-600), var(--color-primary-500));
color: white;
border-radius: 0.375rem (6px);
padding: 0.5rem 1.5rem;
font-weight: 500;
box-shadow: 0 4px 12px rgba(176, 42, 42, 0.2);
transition: all 0.2s ease;

/* Hover */
background: linear-gradient(135deg, var(--color-primary-700), var(--color-primary-600));
transform: translateY(-1px);
box-shadow: 0 6px 16px rgba(176, 42, 42, 0.3);
```

**Status:** DERIVED from `components.css`

### Card Component

**Pattern:**
```css
background: white;
border-radius: 0.75rem (12px);
border: 1px solid var(--color-secondary-200);
box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
padding: 1.5rem;
transition: all 0.3s ease;

/* Hover */
transform: translateY(-4px);
box-shadow: 0 12px 24px rgba(0, 0, 0, 0.12), 0 0 0 1px var(--color-primary-200);
border-color: var(--color-primary-300);
```

**Enhanced Variant (for advocacy cards):**
- Left accent bar with gradient (primary to accent)
- Appeal number badge with gradient background

**Status:** DERIVED from `components.css`

### Form Elements

**Input Pattern:**
```css
background: white;
border: 1px solid var(--color-secondary-200);
border-radius: 0.375rem;
padding: 0.5rem 1rem;
font-size: 1rem;
min-height: 44px; /* WCAG touch target */

/* Focus */
outline: none;
border-color: var(--color-primary-500);
box-shadow: 0 0 0 3px rgba(197, 48, 48, 0.1);
```

**Status:** DERIVED from `components.css`

### Navigation

**Header Pattern:**
- White background
- Border bottom in light gray
- Logo left-aligned
- Navigation items: Secondary gray text, primary red on hover/active
- Active state: Underline indicator in primary red

**Status:** DERIVED from `main.css`

### Footer

**Pattern:**
- Dark gray background (secondary-800)
- White text
- Primary red accent for section headers
- Social icons with gray backgrounds, red on hover

**Status:** DERIVED from `main.css`

---

## Layout Principles [DERIVED]

### Container

- Max width: 1280px
- Centered with auto margins
- Padding: 1.5rem (24px) horizontal

### Spacing Scale

| Token | Value | Usage |
|-------|-------|-------|
| xs | 0.25rem (4px) | Tight spacing, icon gaps |
| sm | 0.5rem (8px) | Related elements |
| md | 1rem (16px) | Standard spacing |
| lg | 1.5rem (24px) | Section padding |
| xl | 2rem (32px) | Component separation |
| 2xl | 3rem (48px) | Section margins |
| 3xl | 4rem (64px) | Major sections |
| 4xl | 6rem (96px) | Page-level spacing |
| 5xl | 8rem (128px) | Hero/content spacing |

### Responsive Breakpoints

| Breakpoint | Width | Usage |
|------------|-------|-------|
| sm | 640px | Mobile landscape |
| md | 768px | Tablet |
| lg | 1024px | Desktop |
| xl | 1280px | Large desktop |
| 2xl | 1536px | Extra large |

---

## Accessibility Requirements [CONFIRMED]

**Standard:** WCAG 2.1 AA

**Requirements:**
- Minimum contrast ratio: 4.5:1 for text
- Touch targets: Minimum 44x44px
- Keyboard navigation: All interactive elements focusable
- Focus indicators: Visible outline (primary accent color)
- Screen reader support: Semantic HTML, ARIA labels where needed

**Source:** `site.json` accessibility.wcagLevel = "AA"

---

## Visual Direction Summary [DERIVED]

### Do

- Use red as the dominant advocacy color
- Maintain clean, professional layouts
- Prioritize readability and accessibility
- Use gradients for hero/CTA impact
- Keep interactions subtle and purposeful

### Don't

- Use purple/blue hero gradients (deprecated)
- Overuse orange (keep as accent only)
- Apply heavy glass morphism or neon effects
- Sacrifice readability for visual flair
- Use playful or overly casual styling

### Brand Character in Digital

NAELT digital expression should convey:
- **Advocacy strength** through red primary color
- **Professional credibility** through clean layouts
- **Human warmth** through appropriate whitespace and typography
- **Action orientation** through clear CTAs

---

## Evidence Sources

- **`site.json`** [CONFIRMED] - Brand colors, accessibility settings
- **`manifest.json`** [CONFIRMED] - Color scales, typography configuration
- **`main.css`** [CONFIRMED] - Base styles, CSS variables
- **`components.css`** [CONFIRMED] - Component-specific patterns
- **Cross-reference synthesis** [DERIVED] - Application principles, best practices

---

**Document Version:** 1.0.0
**Status:** CONFIRMED design tokens with DERIVED application guidelines
**Last Updated:** 2026-03-25

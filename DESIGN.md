---
name: AI Web Vulnerability Scanner
description: A high-precision security assessment platform with AI-driven insights.
colors:
  primary: "#a855f7"
  primary-bright: "#c084fc"
  primary-dark: "#7c3aed"
  neutral-bg: "#0d0d0d"
  surface-card: "#1e1e1e"
  surface-sidebar: "#1a1a1a"
  success: "#10b981"
  danger: "#ef4444"
  warning: "#f59e0b"
  text-primary: "#ffffff"
  text-muted: "#a3a3a3"
typography:
  body:
    fontFamily: "Inter, -apple-system, BlinkMacSystemFont, sans-serif"
    fontSize: "16px"
    fontWeight: 400
    lineHeight: 1.6
  mono:
    fontFamily: "Geist Mono, JetBrains Mono, Fira Code, monospace"
    fontSize: "14px"
    fontWeight: 400
rounded:
  sm: "6px"
  md: "10px"
  lg: "16px"
  xl: "24px"
spacing:
  sidebar: "280px"
  header: "72px"
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.text-primary}"
    rounded: "{rounded.md}"
    padding: "14px 28px"
  card-feature:
    backgroundColor: "{colors.surface-card}"
    rounded: "{rounded.lg}"
    padding: "28px"
---

# Design System: AI Web Vulnerability Scanner

## 1. Overview

**Creative North Star: "The Sentinel's Ledger"**

The Sentinel's Ledger represents a design philosophy where security assessment is treated with the gravity and precision of a master record. The interface is not just a tool but a definitive source of truth, organized with scientific rigor and presented with unshakeable confidence. It rejects the over-the-top "hacker" tropes in favor of an atmosphere that feels like a high-end research instrument.

This system is built on the contrast between deep, stable surfaces and vibrant, focused insights. It prioritizes the readability of complex data while using the "Electric Amethyst" accent as a beacon of discovery.

**Key Characteristics:**
- **Refined Darkness:** Depth is conveyed through subtle tonal shifts in the "Midnight Carbon" scale, never relying on pure blacks or harsh borders.
- **Electric Precision:** Color is used as a functional signal, never as mere decoration.
- **Typographic Authority:** Clear hierarchy between the functional Inter body and the analytical Geist Mono data.
- **Satisfying Tactility:** Every interaction responds with a calculated, smooth transition that reinforces the system's reliability.

## 2. Colors

The palette is anchored in a sophisticated dark theme, utilizing a rich purple accent to draw the eye to critical actions and AI findings.

### Primary: Electric Amethyst
- **Electric Amethyst** (#a855f7): The primary brand color. Used for call-to-actions, active navigation states, and the scanner's primary pulse. It represents the "spark" of AI intelligence.
- **Amethyst Glow** (rgba(168, 85, 247, 0.25)): Used for ambient shadows and subtle backgrounds behind icons.

### Status
- **Secure Green** (#10b981): Used for verified safe endpoints and completed scan states.
- **Vulnerable Red** (#ef4444): Used for confirmed vulnerabilities and critical errors.
- **Caution Amber** (#f59e0b): Used for suspicious findings and pending states.

### Neutral: Midnight Carbon
- **Midnight Carbon** (#0d0d0d): The foundation of the ledger. Provides a restful, focused backdrop for long scanning sessions.
- **Steel Surface** (#1e1e1e): Used for cards and elevated panels to create structural depth.

**The Rare Accent Rule.** The primary "Electric Amethyst" color should be used on ≤10% of any given screen. Its rarity preserves its power as a signal of intent and action.

## 3. Typography

**Display/Body Font:** Inter
**Data/Mono Font:** Geist Mono

### Hierarchy
- **Headline** (600, 24px, 1.2): Used for page titles and major sections.
- **Body** (400, 16px, 1.6): The workhorse of the interface. High readability for scan logs and descriptions.
- **Mono Data** (400, 14px, 1.5): Used for URLs, code snippets, payload data, and AI raw classification output.

**The Clarity Rule.** Never use a font size smaller than 12px for critical security data. If the data is too dense to fit, re-evaluate the layout rather than shrinking the type.

## 4. Elevation

The Sentinel's Ledger uses a layered approach to depth. Surfaces are stacked based on their importance, with the deepest layer being the page body and the highest being active modals or critical alerts.

### Shadow Vocabulary
- **Ambient Glow** (0 8px 32px var(--accent-glow)): A diffuse, purple-tinted shadow used under primary buttons and featured cards to give them an "energized" presence.
- **Structural Depth** (0 8px 32px rgba(0, 0, 0, 0.6)): Used for cards to separate them from the background.

## 5. Components

### Buttons
- **Shape:** Softened rectangular (10px radius).
- **Primary:** Gradient-filled (7c3aed to a855f7) with white text.
- **Satisfying Click:** On hover, the button lifts slightly (-2px translateY) and the glow intensifies.

### Cards
- **Structure:** 16px corner radius, 1px border (#2a2a2a).
- **Interaction:** On hover, the border shifts to the primary accent color, indicating the card is a clickable entry point.

### Inputs
- **Style:** Deep background with a 2px stroke.
- **Focus State:** A 3px glow of "Amethyst Glow" surrounds the field, signaling the system is ready to receive target data.

## 6. Do's and Don'ts

### Do:
- **Do** use Geist Mono for all technical strings and AI-classified responses to differentiate them from UI labels.
- **Do** maintain a minimum padding of 24px within all major content containers to maintain the feeling of "Refined Darkness".
- **Do** use OKLCH for dynamic color tints to ensure perceptual uniformity in the dark theme.

### Don't:
- **Don't** use neon-green or "Matrix" style fonts. It violates the "No Hollywood hacker" principle from PRODUCT.md.
- **Don't** use pure #000000 for backgrounds. Use Midnight Carbon (#0d0d0d) to keep the shadows "soft" and professional.
- **Don't** use side-stripe borders as color accents on cards. Use full borders or background tints.

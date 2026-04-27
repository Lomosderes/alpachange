# Alpachange - DESIGN.md

## Color Strategy
**Register:** product
**Strategy:** Committed
**Theme:** Light (Institutional & Trustworthy)

### Tokens (OKLCH)
- **Primary (Institutional):** `oklch(25% 0.05 250)` — Equivalent to #102636. Used for headers, footers, and deep branding.
- **Accent (Action):** `oklch(60% 0.20 45)` — Equivalent to #ea6119. Used for primary buttons and urgent actions.
- **Success (Teal):** `oklch(68% 0.16 175)` — Equivalent to #0eba95. Used for positive states and support badges.
- **Surface (Background):** `oklch(99% 0.005 250)` — Off-white with a very subtle blue tint to maintain focus.
- **Text-Base:** `oklch(22% 0.04 250)` — Deep charcoal/blue (#102636 variant) for maximum readability.
- **Text-Muted:** `oklch(45% 0.03 250)` — Medium contrast for secondary information.

## Typography
- **Scale:** 1.25 (Major Third)
- **Hierarchy:**
  - `h1`: Bold, tight tracking, 2.441rem.
  - `h2`: Bold, 1.953rem.
  - `h3`: Semibold, 1.563rem.
  - `body`: 1rem, line-height 1.6, max-width 70ch.

## Components
- **Cards:** 
  - Radius: `1.25rem` (20px).
  - Shadow: `0 4px 20px -4px oklch(25% 0.1 255 / 0.08)`.
  - Border: `1px solid oklch(90% 0.02 255)`.
- **Buttons:** 
  - Radius: `0.75rem` (12px).
  - Motion: `0.2s ease-out-expo` for hover states.
- **Navigation:** 
  - Clean, white background with a subtle bottom border instead of solid primary color.

## Motion
- Transitions: `cubic-bezier(0.16, 1, 0.3, 1)` (ease-out-expo) for all visual states.
- Entrance: Subtle fade-in + slide-up for petition cards.

# Design System Strategy: JOC
**Vision Statement: The Sentinel Engine**

## 1. Overview & Creative North Star: "Kinetic Command"
The creative North Star for JOC is **Kinetic Command**. We are moving away from the static, "dashboard-in-a-box" aesthetic and toward a high-fidelity, tactical interface that feels alive. This system interprets "The Sentinel Engine" as a living organism of data—precise, watchful, and authoritative. 

By leveraging **Space Grotesk** for high-impact display and **Inter** for dense utility, we create a tension between "Human" and "Machine." To break the "template" look, we utilize **intentional asymmetry**: large-scale display type is often justified to the left with significant negative space to the right, while interactive elements are clustered in tactical "control pods" to emphasize the Sentinel theme.

## 2. Colors: The Deep-Space Spectrum
The palette is anchored in `#0d0e12` (Surface), providing a void-like depth that allows the electric blue accents (`#81ecff`) to feel like light sources rather than mere UI elements.

### The "No-Line" Rule
**Borders are a failure of hierarchy.** In this design system, 1px solid strokes for sectioning are strictly prohibited. Boundaries are defined exclusively through:
*   **Tonal Shifts:** Placing a `surface-container-low` section against a `surface` background.
*   **Physicality:** Using nested surface tiers to denote parent-child relationships.

### Surface Hierarchy & Nesting
Treat the UI as a series of physical layers—like stacked sheets of obsidian and frosted glass.
*   **Level 0 (Background):** `surface` (#0d0e12) – The base canvas.
*   **Level 1 (Sections):** `surface-container-low` (#121318) – Large content blocks.
*   **Level 2 (Interaction):** `surface-container` (#18191e) – Primary interactive zones.
*   **Level 3 (Floating):** `surface-container-high` (#1e1f25) – Overlays and active cards.

### The "Glass & Gradient" Rule
To achieve the premium "Sentinel" feel, floating elements must utilize **Glassmorphism**. Apply `surface-container-highest` at 60% opacity with a `24px` backdrop blur. Main CTAs should not be flat; use a subtle linear gradient from `primary` (#81ecff) to `primary-container` (#00e3fd) at a 135-degree angle to simulate glowing energy.

## 3. Typography: Tactical Editorial
The typography scale is designed to feel like a high-end technical journal.

*   **Display (Space Grotesk):** Set with tight letter-spacing (-0.04em). These are your "Sentinel" moments. Use `display-lg` to break the grid, overlapping background containers to create depth.
*   **Headlines (Space Grotesk):** Authoritative and geometric. Used for primary module titles.
*   **Body (Inter):** Chosen for its neutrality and high legibility at small sizes. Used for all data-heavy sections and descriptions.
*   **Labels (Space Grotesk):** All-caps, with increased letter-spacing (+0.1em). These are used for "Micro-Data" (e.g., timestamps, status indicators) to maintain the "Engine" aesthetic.

## 4. Elevation & Depth: Tonal Layering
Traditional drop shadows are too "soft" for JOC. We use **Atmospheric Depth**.

*   **The Layering Principle:** Instead of a shadow, a "lifted" card is simply one tier higher in the `surface-container` scale.
*   **Ambient Shadows:** If an element must float (e.g., a Modal), use a shadow color tinted with `surface-tint` (#81ecff) at 5% opacity, with a massive `64px` blur. It should look like a glow, not a shadow.
*   **The "Ghost Border" Fallback:** If accessibility requires a stroke, use `outline-variant` (#47484c) at **15% opacity**. It should be felt, not seen.

## 5. Components: The Sentinel Primitives

### Buttons
*   **Primary:** Gradient fill (`primary` to `primary-container`), black text (`on-primary`), `md` (0.375rem) roundedness.
*   **Secondary:** Glass-morphic background, `outline` at 20% opacity, `primary` colored text.
*   **Tertiary:** No background. `label-md` typography with a `primary` underline that only appears on hover.

### Cards & Lists
**Forbid the use of divider lines.** Use `1.5rem` to `2rem` of vertical white space to separate items. If a list is dense, alternate the background between `surface-container-low` and `surface-container-lowest`.

### Inputs
*   **Text Fields:** Use `surface-container-highest` for the track. Instead of a full border, use a 2px bottom-border of `primary` that animates from the center outward upon focus.

### Additional Component: "The Pulse"
A custom status indicator for JOC. A small `primary` dot with two concentric, animating rings of `primary-dim` that fade out. Use this next to active "Sentinel Engine" processes.

## 6. Do's and Don'ts

### Do
*   **Do** use extreme scale. Pair a `display-lg` headline with `body-sm` metadata for an editorial look.
*   **Do** use `primary` sparingly. It is an "Electric" accent; if everything is blue, nothing is blue.
*   **Do** embrace negative space. The Sentinel Engine needs room to breathe to feel powerful.

### Don't
*   **Don't** use `#000000` for backgrounds. It kills the depth of the `surface` tokens.
*   **Don't** use standard "Material" shadows. They feel dated and "out-of-the-box."
*   **Don't** use center alignment for large text blocks. Keep it tactical and left-aligned or asymmetric.
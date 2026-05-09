# Invoice Quick-Capture Redesign Spec

**Date:** 2026-05-06
**Status:** Approved
**Aesthetic:** Bold & Modern

## Design Vision

A bold, modern dark-themed invoice capture experience with high-contrast accents, brutalist typography, and snap/impact micro-interactions. Optimized for quick capture workflow.

## Visual Foundation

### Color Palette
```css
--bg-primary: #0D0D0D;        /* Deep charcoal black */
--bg-secondary: #1A1A1A;         /* Card backgrounds */
--bg-tertiary: #262626;          /* Elevated surfaces */
--accent-primary: #CCFF00;      /* Electric lime - main CTA */
--accent-secondary: #00FF94;       /* Neon mint - secondary */
--text-primary: #FFFFFF;        /* White for headlines */
--text-secondary: #A0A0A0;      /* Muted gray for body */
--text-tertiary: #666666;        /* Disabled/hints */
--border: #333333;               /* Subtle borders */
--error: #FF4757;               /* Bold red */
--success: #2ED573;             /* Clear green */
```

### Typography
- **Display Font:** 'Outfit' (Google Fonts) - Bold weight for headlines
- **Mono Font:** 'JetBrains Mono' - For amounts, numbers, data
- **Body Font:** 'Outfit' - Regular weight for labels

### Spacing System
```css
--space-xs: 0.25rem;
--space-sm: 0.5rem;
--space-md: 1rem;
--space-lg: 1.5rem;
--space-xl: 2rem;
--space-2xl: 3rem;
```

### Effects
- Hard shadows (no blur): `box-shadow: 4px 4px 0px var(--accent-primary)`
- Border radius: 0px for brutalist edge, 8px for subtle
- Pulse animation on primary CTA
- Slide-up panel transitions (200ms ease-out)

---

## Screen by Screen

### 1. Main Capture Screen

**Layout:**
- Full-bleed dark background
- Minimal header: small logo text + settings icon
- Large camera capture area (80% viewport)
- Floating capture button (center-bottom)

**Capture Button:**
- Large circular (64px)
- Accent color fill
- Subtle pulse animation (scale 1.0 → 1.05, infinite)
- On tap: quick scale-down feedback (0.95)

**States:**
- Empty: Dashed border preview area with icon
- Has image: Full preview with subtle vignette
- Processing: Chunked progress bars (not spinner)

### 2. Processing State

- Horizontal progress bars (4 bars)
- Accent color fills left-to-right
- Bold text status: "EXTRACTING..."
- No spinner — just this animated indicator

### 3. Verification Panel (Slide-up)

- Bottom sheet with backdrop blur
- Card for image thumbnail (left)
- Data fields in bold monospace
- Two buttons: "SAVE" (primary accent) + "EDIT" (ghost)
- Swipe down to dismiss

### 4. Form (Edit Mode)

- Dark card container
- Fields with bottom-border-only style
- Bold monospace values
- Accent-colored focus states
- Keyboard-friendly (full-width inputs)

### 5. Success Toast

- Slide in from top
- Accent background
- Bold checkmark icon
- Auto-dismiss after 2s

---

## Components

### ImageInput
- Hidden file input
- Custom capture button with pulse
- Drag-drop zone overlay
- Bold loading state

### InvoiceForm
- Section headers (uppercase, small)
- Input: bottom-border style
- Line items: horizontal card layout
- Summary: accent border-left box

### ImagePreview
- Aspect-ratio container
- Subtle vignette overlay
- Corner fold effect (CSS)

### Auth (minimal)
- Single "Connect Google" button
- Accent outline style
- Loading state with accent spinner

### SaveButton
- Full-width primary CTA
- Hard shadow accent
- Bold uppercase text

---

## Animations

| Element | Animation | Duration | Easing |
|---------|-----------|----------|--------|
| Capture button pulse | scale 1.0 → 1.05 | 1.5s | ease-in-out |
| Button tap | scale 1.0 → 0.95 → 1.0 | 100ms | ease-out |
| Progress bars | width 0% → 100% (staggered) | 800ms | ease-out |
| Panel slide-up | transform translateY | 200ms | ease-out |
| Toast slide | transform translateY + opacity | 300ms | ease-out |

---

## Success Criteria

1. ✅ Dark theme with electric lime accent
2. ✅ Quick capture flow (select → process → verify → save)
3. ✅ Bold typography with mono for data
4. ✅ Impact micro-interactions
5. ✅ Minimal unnecessary UI elements
6. ✅ Responsive (mobile-first)
7. ✅ Processing indicator: chunked bars (not spinner)
8. ✅ Success/error states have accent colors
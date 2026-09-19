# Design System & UI Specification — VisionAI

This document defines the visual hierarchy, color palette, design tokens, and user experience standards for VisionAI.

---

## 1. Design Philosophy
- **Human-Designed & Intentional**: Avoid generic AI template aesthetics, excessive gradients, or floating blur cards.
- **Dark-First Elegance**: High contrast, minimal eye strain, subtle dividers, and purposeful accents.
- **Information Density**: Deliver actionable metrics (confidence scores, inference latency, coordinates) with clear visual hierarchy.

---

## 2. Color Palette & Design Tokens

```css
:root {
  /* Backgrounds */
  --bg:        #0B0F14;  /* Root dark canvas */
  --surface:   #111820;  /* Card & sidebar background */
  --surface2:  #151D26;  /* Secondary surface / table row hover */
  
  /* Borders */
  --border:    #1E2A38;  /* Primary subtle divider */
  --border2:   #28384A;  /* Emphasized border / active ring */
  
  /* Accents */
  --accent:    #7C3AED;  /* Deep purple primary action */
  --accent-h:  #6D28D9;  /* Accent hover state */
  --accent-lo: rgba(124, 58, 237, 0.12); /* Subtle accent tint */
  
  /* Typography */
  --text:      #F0F4F9;  /* High contrast primary body */
  --text2:     #7E8FA3;  /* Secondary label / description */
  --text3:     #4A5A6E;  /* Tertiary muted captions / icons */
  
  /* Semantic Status */
  --ok:        #22C55E;  /* Success green */
  --ok-lo:     rgba(34, 197, 94, 0.12);
  --warn:      #F59E0B;  /* Warning amber */
  --warn-lo:   rgba(245, 158, 11, 0.12);
  --err:       #EF4444;  /* Danger red */
  --err-lo:    rgba(239, 68, 68, 0.12);
  
  /* Sizing & Radius */
  --side:      228px;    /* Sidebar width */
  --hdr:       56px;     /* Header bar height */
  --r:         6px;      /* Standard component border radius */
}
```

---

## 3. Typography
- **Primary Font**: `Inter`, system-ui, sans-serif.
- **Page Titles**: 22px, `font-weight: 700`, letter-spacing `-0.4px`.
- **Section Headings**: 14px–15px, `font-weight: 600`.
- **Body & Controls**: 13.5px–14px, `font-weight: 400` / `500`.
- **Metadata & Badges**: 11px–12px, `font-weight: 600`.

---

## 4. UI Components

### Buttons
- **Primary (`.btn-primary`)**: Filled with `--accent`, white text, 7px 14px padding. Used for primary execution (e.g. Start Camera, Start Detecting).
- **Ghost / Secondary (`.btn-ghost`)**: Transparent background with `--border`, text `--text2`. Used for secondary actions (Download, Run Again, Clear).
- **Danger (`.btn-danger`)**: Light red background `--err-lo`, border with `--err`. Used for Stop Camera.

### Cards & Stats Strip
- No bulky floating cards with giant drop shadows.
- **Stats Row**: Borderless strip with 1px divider gap, combining Total Runs, Objects, Confidence, and Model into a cohesive KPI bar.

### Upload Zone
- Dashed border with subtle hover background transition (`--accent-lo`).
- Clear format badges: `JPG`, `PNG`, `WEBP`, `BMP`, `Max 15 MB`.

### Live Camera Viewport
- Dark 4:3 aspect container with border `--border`.
- **HUD Badges**: Frosted glass pills displaying LIVE status with pulse animation, real-time FPS counter, inference latency, and detected object count.
- Canvas absolutely positioned to prevent shifting idle states.

---

## 5. Mandatory UX States

1. **Empty States**:
   - Clean SVG line icon + concise title + action button (e.g. "No detections yet" -> "Start Detecting").
2. **Processing States**:
   - Multi-step progress list:
     - `✓ Image uploaded`
     - `✓ Preprocessing`
     - `◉ Running object detection` (animated spinner)
     - `○ Generating results`
3. **Error Handling**:
   - User-friendly error banners (no raw stack traces).
   - Dismissible alerts with explanatory guidance.
4. **Toast Notifications**:
   - Bottom-right unobtrusive feedback pills with checkmarks for completion events (3.5s auto-dismiss).

---

## 6. Responsive Breakpoints
- **Desktop (> 860px)**: Fixed sidebar (`228px`), two-column workspace (image on left, detections table on right).
- **Tablet & Mobile (≤ 860px)**: Sidebar converts to an off-canvas drawer with toggle button; results stack into a single column.

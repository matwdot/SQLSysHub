---
name: Fluent SQL Core
colors:
  surface: '#fcf9f8'
  surface-dim: '#dcd9d9'
  surface-bright: '#fcf9f8'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f6f3f2'
  surface-container: '#f0eded'
  surface-container-high: '#eae7e7'
  surface-container-highest: '#e5e2e1'
  on-surface: '#1b1b1b'
  on-surface-variant: '#3d4949'
  inverse-surface: '#313030'
  inverse-on-surface: '#f3f0ef'
  outline: '#6d7979'
  outline-variant: '#bcc9c8'
  surface-tint: '#006a6a'
  primary: '#006767'
  on-primary: '#ffffff'
  primary-container: '#008282'
  on-primary-container: '#f3fffe'
  inverse-primary: '#6fd7d6'
  secondary: '#5d5f5f'
  on-secondary: '#ffffff'
  secondary-container: '#dcdddd'
  on-secondary-container: '#5f6161'
  tertiary: '#5b5c5c'
  on-tertiary: '#ffffff'
  tertiary-container: '#737575'
  on-tertiary-container: '#fdfcfc'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#8cf3f3'
  primary-fixed-dim: '#6fd7d6'
  on-primary-fixed: '#002020'
  on-primary-fixed-variant: '#004f4f'
  secondary-fixed: '#e2e2e2'
  secondary-fixed-dim: '#c6c6c7'
  on-secondary-fixed: '#1a1c1c'
  on-secondary-fixed-variant: '#454747'
  tertiary-fixed: '#e2e2e2'
  tertiary-fixed-dim: '#c6c6c6'
  on-tertiary-fixed: '#1a1c1c'
  on-tertiary-fixed-variant: '#454747'
  background: '#fcf9f8'
  on-background: '#1b1b1b'
  surface-variant: '#e5e2e1'
typography:
  display-lg:
    fontFamily: Inter
    fontSize: 28px
    fontWeight: '600'
    lineHeight: 36px
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Inter
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
  title-sm:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '600'
    lineHeight: 22px
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  body-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 16px
  label-bold:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '700'
    lineHeight: 16px
  code-mono:
    fontFamily: jetbrainsMono
    fontSize: 13px
    fontWeight: '400'
    lineHeight: 20px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  space-xs: 4px
  space-sm: 8px
  space-md: 16px
  space-lg: 24px
  sidebar-width: 280px
  gutter: 12px
---

## Brand & Style
This design system is built for a technical, high-productivity environment. It targets database administrators and developers who require a modern, desktop-class experience that feels native to high-performance operating systems. 

The aesthetic is **Corporate / Modern** with a strong infusion of **Glassmorphism**, specifically drawing from Microsoft's "Mica" material philosophy. The UI emphasizes clarity, functional hierarchy, and a sense of depth through semi-transparent surfaces and layered containers. The goal is to create a workspace that feels light and responsive while maintaining the serious, professional tone required for data management. 

Key attributes:
- **Native Precision:** Elements feel integrated into the desktop environment.
- **Layered Clarity:** Use of translucency to provide context without clutter.
- **Intentional Focus:** High-contrast text and a singular primary brand color to guide user action.

## Colors
The palette is centered around **Deep Teal (#008B8B)**, used exclusively for primary actions and state indicators to ensure high visibility against the neutral workspace. 

The background system utilizes a hierarchy of light greys and whites. The base layer uses a "Mica" effect—a semi-transparent, subtle grey that picks up hints of the user's wallpaper. Surfaces atop this base are solid white or very light grey to create a clear "card" metaphor for different tool panels. High-contrast neutrals (near-black) are used for typography to ensure maximum legibility during long sessions of code review or data analysis.

## Typography
We use **Inter** as the primary typeface for its exceptional legibility on digital screens and its neutral, professional character. For the SQL editor and data grids, **JetBrains Mono** is utilized to provide the necessary character alignment for technical tasks.

Hierarchy is established through weight rather than dramatic size shifts. This maintains a compact "information-dense" layout suitable for desktop applications. All Portuguese text should respect standard casing rules, with "Label-bold" used sparingly for section headers within sidebars.

## Layout & Spacing
The design system employs a **Fixed Sidebar / Fluid Content** layout model. This is standard for desktop productivity tools. 

- **Sidebars:** Fixed at 280px, containing navigation and configuration forms.
- **Main Canvas:** A fluid area that expands to fill the remaining viewport, typically housing the SQL editor and result grids.
- **Rhythm:** A 4px baseline grid governs all spacing. 12px is the standard gutter between major UI panels to provide breathing room without sacrificing screen real estate. 
- **Density:** High density is preferred. Padding within input fields and list items should be tight (8px vertical) to maximize the amount of data visible at once.

## Elevation & Depth
Elevation is achieved through a combination of **Tonal Layers** and **Mica Translucency**:

1.  **Level 0 (App Background):** The Mica material. A semi-transparent layer that provides the foundation.
2.  **Level 1 (Sidebar/Secondary Panels):** A solid #F3F3F3 background with a 1px interior border (#E5E5E5) to define edges. No shadows.
3.  **Level 2 (Active Canvas/Cards):** Pure white (#FFFFFF) with a very soft, subtle ambient shadow (4px blur, 5% opacity) to signify the primary work area.
4.  **Level 3 (Popovers/Tooltips):** Solid white with a 1px border and a more pronounced shadow (12px blur, 15% opacity) to float above the workspace.

## Shapes
The shape language follows the modern Windows standard. 
- **Standard Elements:** Buttons, Input fields, and Checkboxes use a **8px (rounded)** radius.
- **Containers:** Side panels and main content cards use a **12px (rounded-lg)** radius to create a softer, more modern windowing feel.
- **Inner Selection:** Selection highlights within lists use a **4px** radius to remain tucked within their containers.

## Components
### Buttons
- **Primary:** Solid #008B8B with white text. Subtle 1px top-light border for a tactile feel.
- **Secondary:** Transparent background with #008B8B border and text.
- **Ghost:** No border or background unless hovered. Used for utility icons (e.g., Refresh, Settings).

### Input Fields
- White background with a 1px bottom-heavy border.
- On focus, the bottom border thickens and changes to the primary Teal color.
- Labels are positioned directly above the input in `body-sm` bold.

### Data Grids (Results)
- Header row uses a subtle #F3F3F3 background with `label-bold` text.
- Row hover state: #F9F9F9.
- Cell borders: 1px solid #EDEDED.

### Side Navigation
- Icons are 20px, centered in a 40px square.
- Active state is indicated by a 3px vertical "pill" of Teal color on the left edge of the navigation item.

### Toggle & Checkbox
- Checkboxes use the primary Teal when checked.
- Toggles (Switches) follow the Fluent style: a rounded pill shape where the "thumb" slides horizontally.
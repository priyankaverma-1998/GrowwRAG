---
name: Precision Fintech
colors:
  surface: '#f7fafc'
  surface-dim: '#d7dadc'
  surface-bright: '#f7fafc'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f1f4f6'
  surface-container: '#ebeef0'
  surface-container-high: '#e5e9eb'
  surface-container-highest: '#e0e3e5'
  on-surface: '#181c1e'
  on-surface-variant: '#3c4a43'
  inverse-surface: '#2d3133'
  inverse-on-surface: '#eef1f3'
  outline: '#6b7b72'
  outline-variant: '#bacac1'
  surface-tint: '#006c4f'
  primary: '#006c4f'
  on-primary: '#ffffff'
  primary-container: '#00d09c'
  on-primary-container: '#00533c'
  inverse-primary: '#2fe0aa'
  secondary: '#595f68'
  on-secondary: '#ffffff'
  secondary-container: '#dde3ee'
  on-secondary-container: '#5f656e'
  tertiary: '#5b5e66'
  on-tertiary: '#ffffff'
  tertiary-container: '#b5b7bf'
  on-tertiary-container: '#45484f'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#59fdc5'
  primary-fixed-dim: '#2fe0aa'
  on-primary-fixed: '#002116'
  on-primary-fixed-variant: '#00513b'
  secondary-fixed: '#dde3ee'
  secondary-fixed-dim: '#c1c7d2'
  on-secondary-fixed: '#161c24'
  on-secondary-fixed-variant: '#414750'
  tertiary-fixed: '#e0e2eb'
  tertiary-fixed-dim: '#c4c6cf'
  on-tertiary-fixed: '#181c22'
  on-tertiary-fixed-variant: '#44474e'
  background: '#f7fafc'
  on-background: '#181c1e'
  surface-variant: '#e0e3e5'
typography:
  display:
    fontFamily: Inter
    fontSize: 40px
    fontWeight: '700'
    lineHeight: 48px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.01em
  headline-lg-mobile:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  headline-md:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-sm:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  label-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '600'
    lineHeight: 20px
  label-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  base: 8px
  xs: 4px
  sm: 12px
  md: 24px
  lg: 48px
  xl: 80px
  container-max: 1200px
  gutter: 24px
---

## Brand & Style
The design system is built on the pillars of transparency, efficiency, and clarity. It targets a modern demographic of retail investors who value speed and data-driven insights. The aesthetic is a refined **Corporate Modern** style—utilizing high-performance interfaces that feel light yet authoritative. 

The emotional response should be one of "effortless control." By leveraging generous whitespace and a restricted, high-contrast palette, the UI eliminates cognitive load, allowing the Mutual Fund FAQ Assistant to present complex financial data as simple, actionable information. The design avoids unnecessary decoration, focusing instead on crisp alignment and functional color application.

## Colors
The palette is dominated by **Groww Green** (#00D09C), used strategically for primary actions and positive data indicators to reinforce brand recognition and growth. **Deep Charcoal** (#1B2129) provides the grounding for typography and high-level containers, ensuring maximum legibility.

Backgrounds utilize a soft neutral off-white to reduce eye strain during long reading sessions. Semantic colors for Info, Error, and Warning states are calibrated for high visibility against the neutral backdrop while maintaining a professional, non-alarmist tone.

## Typography
This design system utilizes **Inter** exclusively to achieve a systematic, utilitarian aesthetic that excels in data-heavy environments. Headlines use a tighter letter-spacing and heavier weights to create a strong visual anchor. 

Body text is optimized for readability with a generous 1.5x line-height. Label styles are used for metadata, such as fund categories or risk levels, often appearing in all-caps to differentiate from conversational assistant text. Mobile overrides are essential for the primary display and large headline levels to prevent awkward text wrapping on small devices.

## Layout & Spacing
The layout follows a **Fixed Grid** model on desktop, centering the FAQ Assistant within a 1200px max-width container to maintain focus. A strictly linear 8px scaling system governs all margins and padding.

- **Desktop:** 12-column grid with 24px gutters.
- **Tablet:** 8-column grid with 20px gutters.
- **Mobile:** 4-column grid with 16px gutters and 16px side margins.

Horizontal spacing between the assistant's message and user input should be maximized to create a clear conversational flow. Group related FAQ items using `md` (24px) spacing, while distinct sections are separated by `lg` (48px) blocks.

## Elevation & Depth
Elevation in this design system is handled through **Tonal Layers** and extremely subtle **Ambient Shadows**. This approach keeps the UI feeling flat and modern while providing enough depth to signify interactivity.

- **Level 0 (Base):** The main background using the neutral hex.
- **Level 1 (Cards):** Pure white surfaces with a 1px border (#E2E8F0) and a very soft, diffused shadow (0px 4px 12px, 4% opacity of the secondary color).
- **Level 2 (Dropdowns/Modals):** Increased shadow depth (0px 12px 24px, 8% opacity) to suggest they are floating above the main interface.

Avoid heavy blurs or colorful glows; depth should feel structural rather than decorative.

## Shapes
The shape language is consistently **Rounded**, using an 8px (0.5rem) base radius. This strikes a balance between the precision of a professional financial tool and the approachability of a helpful assistant.

Interactive elements like buttons and input fields use the base 8px radius. Larger containers, such as fund detail cards or FAQ info banners, should scale up to 16px (`rounded-lg`) to soften the overall appearance of the layout.

## Components
### Buttons
- **Primary:** Groww Green background, white text, bold weight. No gradient.
- **Secondary:** Transparent background, Deep Charcoal border (1px), Deep Charcoal text.
- **Interaction:** On hover, primary buttons darken by 10%; on click, they scale down slightly (0.98x).

### Info Banners (st.info)
- Soft Groww Green tint background (10% opacity).
- Left-hand accent border (4px solid #00D09C).
- Iconography matching the primary color.

### Error & Warning States
- **Error (st.error):** Pale red background with bold red text. Used for failed API calls or invalid investment amounts.
- **Warning (st.warning):** Pale amber background. Used for high-risk fund disclaimers.

### Cards
- Use for individual FAQ results.
- White background, 1px neutral border, 16px padding.
- Include a "Was this helpful?" micro-interaction at the bottom right.

### Input Fields
- Subtle gray border (#D1D5DB).
- Transitions to a 2px Groww Green border on focus.
- Placeholder text in tertiary gray.

### Chips/Tags
- Used for fund categories (e.g., "Equity", "Debt").
- Pill-shaped with a neutral gray background and small font size.
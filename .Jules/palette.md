## 2024-03-21 - Accessible Hidden Inputs for Custom Switches
**Learning:** In this application, custom UI toggles (like the theme switch) frequently used `display: none` for the underlying checkbox, which entirely removes the element from the accessibility tree, breaking both screen reader announcements and keyboard navigation.
**Action:** Always replace `display: none` with a 'visually hidden' pattern (`opacity: 0`, `position: absolute`, `width: 0`, `height: 0`) for functional inputs, and ensure they have a `:focus-visible` outline mapped to their adjacent visible label/UI elements.

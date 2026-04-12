## 2024-06-03 - Accessible Custom Toggles
**Learning:** Using `display: none` on native inputs for custom toggles completely removes them from the accessibility tree and prevents keyboard navigation.
**Action:** Always use the "visually hidden" CSS pattern (opacity: 0, width: 0, height: 0, absolute position) instead of `display: none` for the native input, and ensure a `:focus-visible` outline is added to the adjacent visible element (like the slider) to preserve keyboard accessibility and screen reader support.

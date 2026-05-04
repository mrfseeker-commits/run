## 2024-05-14 - Custom Checkbox Accessibility
**Learning:** Using `display: none` for custom toggle switch inputs completely removes them from the accessibility tree, making keyboard navigation impossible.
**Action:** Replace `display: none` with the "visually hidden" CSS pattern (opacity: 0, absolute position) and add adjacent `:focus-visible` styles to ensure screen reader compatibility and keyboard focus rings.

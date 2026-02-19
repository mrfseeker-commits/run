## 2024-05-22 - [Accessibility] Hidden Inputs
**Learning:** Using `display: none` on inputs completely removes them from the accessibility tree, making them inaccessible to screen readers and keyboard users.
**Action:** Always use the "visually hidden" pattern (opacity: 0, width: 0, height: 0, position: absolute) for inputs that are visually replaced by custom UI but need to remain interactive.

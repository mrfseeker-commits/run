## 2024-05-16 - Accessible Custom Hidden Inputs
**Learning:** Using `display: none` for custom toggle switch inputs completely removes them from the accessibility tree, breaking screen reader functionality and preventing keyboard navigation (Tab focus).
**Action:** Always use a 'visually hidden' CSS pattern (`opacity: 0; width: 0; height: 0; position: absolute;`) instead of `display: none`, and ensure there is a `:focus-visible` outline mapped to adjacent visible elements (like `.slider`) for keyboard accessibility.

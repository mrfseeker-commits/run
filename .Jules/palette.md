## 2026-05-23 - Accessible Custom Checkboxes
**Learning:** Setting `display: none` on native inputs powering custom toggles breaks keyboard navigation and screen reader access.
**Action:** Use a visually hidden pattern (`opacity: 0; width: 0; position: absolute;`) and apply `:focus-visible` styles to the adjacent custom element.
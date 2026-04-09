## 2024-05-18 - Accessible Custom Toggles
**Learning:** `display: none` on checkbox inputs removes them from the accessibility tree, making custom toggle switches invisible to screen readers and keyboard navigation.
**Action:** Use visually hidden styles (`opacity: 0; position: absolute;`) instead, add `role="switch"`, `aria-label`, and implement `:focus-visible` on the adjacent visual element.

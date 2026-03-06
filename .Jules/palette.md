
## 2025-02-28 - Custom Toggle Switch Accessibility
**Learning:** Avoid using `display: none` for inputs representing custom toggle switches (`.theme-switch input`). This completely hides the element from screen readers and makes it unreachable via keyboard navigation (Tab).
**Action:** Use the visually hidden pattern (`opacity: 0`, `position: absolute`, `width: 0`, `height: 0`) and always pair it with a `:focus-visible` state on a sibling element (like `.slider`) to ensure keyboard users have a visible focus indicator. Add appropriate ARIA `role="switch"` and `aria-label` attributes to the input.

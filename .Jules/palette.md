## 2024-05-24 - Accessible Theme Toggle
**Learning:** The previous theme toggle used `display: none` on the input checkbox, making it completely hidden from screen readers and breaking keyboard navigation since hidden elements cannot receive focus.
**Action:** Applied the "visually hidden" pattern (opacity 0, absolute position) and added `role="switch"` along with `aria-label` to ensure the element remains focusable and semantically correct for screen reader users while keeping the custom styling intact.

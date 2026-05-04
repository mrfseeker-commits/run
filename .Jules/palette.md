## 2024-05-18 - Fix custom toggle switch accessibility
**Learning:** Using `display: none` on native inputs like checkboxes to create custom toggle switches hides them from screen readers and prevents keyboard focus, breaking accessibility.
**Action:** Always use the "visually hidden" pattern (`opacity: 0; width: 0; height: 0; position: absolute;`) for the native input instead, and use the `:focus-visible` pseudo-class on the adjacent custom styling element (e.g., `input:focus-visible + .slider`) to provide clear visual focus indicators for keyboard users.

## 2024-05-20 - Custom Toggle Switch Accessibility
**Learning:** Using `display: none` on a checkbox for a custom toggle switch completely removes it from the accessibility tree, making it impossible for keyboard users to focus or screen readers to interact with it.
**Action:** Always use the visually hidden pattern (`opacity: 0`, `width: 0`, `height: 0`, `position: absolute`) for custom inputs and add `:focus-visible` outline to the adjacent visible element to ensure keyboard and screen reader accessibility.


## 2024-05-15 - [Theme Toggle Accessibility]
**Learning:** [Using `display: none` on inputs, like checkboxes for custom toggles, removes them from the accessibility tree, making them invisible to screen readers and unable to receive keyboard focus. A visually hidden pattern (`opacity: 0`, `width: 0`, `height: 0`, `position: absolute`) is required to maintain accessibility.]
**Action:** [When styling custom toggles or hidden inputs, always use a visually hidden approach instead of `display: none`, and ensure to add appropriate ARIA attributes like `role="switch"` and `aria-label`.]

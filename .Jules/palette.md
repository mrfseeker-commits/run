## 2024-05-18 - [Accessible Hidden Inputs]
**Learning:** When hiding custom checkboxes (like a theme toggle), using `display: none` removes the element from the accessibility tree, making it invisible to screen readers and keyboard navigation. Using a visually hidden pattern (`opacity: 0`, `width: 0`, `height: 0`, `position: absolute`) keeps the input accessible.
**Action:** Use visually hidden patterns instead of `display: none` for custom inputs, and ensure there is a visible focus indicator (e.g., `outline` on adjacent elements using `:focus-visible`) for keyboard users.

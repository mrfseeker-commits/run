## 2024-03-04 - Accessible Custom Checkboxes
**Learning:** Using `display: none` on custom checkboxes (like toggle switches) completely removes them from the accessibility tree, making them invisible to screen readers and impossible to focus via keyboard.
**Action:** Use the "visually hidden" pattern instead (`opacity: 0`, `width: 0`, `height: 0`, `position: absolute`) and add a `:focus-visible` outline to the adjacent visible element to ensure keyboard users can see when the toggle is focused.

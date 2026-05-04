## 2026-04-01 - [Visually Hidden Inputs for Toggle Switches]
**Learning:** Using `display: none` on custom checkbox inputs hides them from screen readers and removes them from the tab order, breaking keyboard accessibility. Accessible hidden inputs must use the 'visually hidden' CSS pattern (opacity: 0, width: 0, height: 0, absolute position).
**Action:** Use visually hidden styles with `:focus-visible` outlines on adjacent sibling elements to ensure proper keyboard navigation and screen reader support for custom switch components.

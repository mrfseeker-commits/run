
## 2026-05-03 - Theme Toggle Accessible Hiding
**Learning:** Using `display: none` on inputs breaks screen reader and keyboard accessibility, preventing focus. This is a common issue with custom CSS toggles where the real input is hidden and a styled `div` acts as the slider.
**Action:** Use the visually hidden pattern (`opacity: 0`, `width: 0`, `height: 0`, `position: absolute`) instead, and always add an explicit `:focus-visible` outline to the adjacent styling element to ensure keyboard users can tell when the toggle is focused. Also, add `role="switch"` and `aria-label` to the real input to properly convey its state and purpose to screen readers.

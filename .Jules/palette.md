## 2024-05-22 - [Keyboard Traps in Custom Controls]
**Learning:** Using `display: none` on input elements to create custom toggle switches completely removes them from the accessibility tree, making them impossible to focus or operate with a keyboard.
**Action:** Always use the "visually-hidden" CSS pattern (opacity: 0, absolute position, small size) for inputs that need to be hidden but remain functional. Add `:focus-visible` styles to the visible proxy element (e.g., the slider) to indicate focus state.

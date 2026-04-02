## 2024-05-18 - Accessible Hidden Inputs for Custom Toggles
**Learning:** Using `display: none` for custom checkbox/radio inputs breaks keyboard navigation and screen reader accessibility completely because it removes the element from the accessibility tree and focus order.
**Action:** Always use the "visually hidden" CSS pattern (`opacity: 0; width: 0; height: 0; position: absolute;`) for accessible hidden inputs and add an adjacent `:focus-visible` rule to provide visual feedback for keyboard users.

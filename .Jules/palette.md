## 2024-05-18 - [Accessible Custom Toggle Switch]
**Learning:** Using `display: none` on native inputs for custom toggles completely removes them from the accessibility tree and prevents keyboard navigation.
**Action:** Always use the 'visually hidden' CSS pattern (`opacity: 0; width: 0; height: 0; position: absolute;`) for custom toggle inputs and map the `:focus-visible` state to an adjacent visible element to ensure keyboard accessibility.

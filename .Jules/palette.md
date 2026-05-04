## 2024-03-22 - Theme Toggle Accessibility Improvement
**Learning:** Using `display: none` on custom checkbox inputs (like toggle switches) breaks keyboard accessibility entirely because the element is removed from the focus order, making it impossible for screen readers or keyboard-only users to reach.
**Action:** Always use the "visually hidden" CSS pattern (`opacity: 0; width: 0; height: 0; position: absolute;`) instead of `display: none` for hidden inputs, and ensure there is a clear `:focus-visible` outline on adjacent visible elements to provide feedback during keyboard navigation.

## 2024-05-24 - Accessible Toggle Switches
**Learning:** Using `display: none` on hidden checkbox inputs (like toggle switches) prevents screen readers from announcing them and keyboard users from focusing them.
**Action:** Use a "visually hidden" pattern (`opacity: 0; width: 0; height: 0; position: absolute;`) on the input, and use the `:focus-visible` pseudo-class on the hidden input combined with an adjacent sibling selector (e.g., `input:focus-visible + .slider`) to style a visible focus ring for keyboard users.

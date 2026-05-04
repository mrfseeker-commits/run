## 2025-02-23 - Accessible Custom Toggle Switch
**Learning:** Using `display: none` on custom `<input type="checkbox">` elements (like theme switches) completely removes them from the accessibility tree and prevents keyboard navigation (`Tab` targeting).
**Action:** Always use the "visually hidden" CSS pattern (`opacity: 0; width: 0; height: 0; position: absolute;`) instead of `display: none`. This keeps the input accessible for screen readers and focusable via keyboard, allowing you to use `:focus-visible` on the adjacent visual element (like the slider) to show a custom focus ring.

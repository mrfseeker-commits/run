## 2024-05-21 - Accessible Checkbox Toggle
**Learning:** Using `display: none` on `<input type="checkbox">` completely removes it from the accessibility tree and keyboard navigation flow, making custom toggles inaccessible to many users.
**Action:** Use the "visually hidden" CSS pattern (`opacity: 0; width: 0; height: 0; position: absolute;`) for the input element to keep it focusable and readable by screen readers while hiding it visually.

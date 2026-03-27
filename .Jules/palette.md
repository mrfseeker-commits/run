## 2026-02-17 - [Hidden Checkbox Accessibility]
**Learning:** `display: none` on `<input type="checkbox">` removes it from the accessibility tree, making it unfocusable and unusable for keyboard and screen reader users.
**Action:** Use `opacity: 0; width: 0; height: 0; position: absolute;` instead of `display: none` to hide the input visually while keeping it accessible.

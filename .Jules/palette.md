## 2024-10-25 - [Accessibility]
**Learning:** Hidden inputs (e.g., custom checkboxes) with `display: none` are inaccessible to screen readers and keyboard users because they are removed from the accessibility tree.
**Action:** Replace `display: none` with a visually-hidden CSS pattern (e.g., `opacity: 0; width: 0; height: 0; position: absolute`) to ensure they remain focusable and accessible.

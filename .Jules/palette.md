## 2025-02-09 - [The `display: none` Trap]
**Learning:** Using `display: none` on inputs (like checkboxes for custom toggles) removes them from the accessibility tree and keyboard navigation.
**Action:** Always use the `.sr-only` pattern (visually hidden but accessible) for inputs that are styled with custom UI.

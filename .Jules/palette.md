## 2024-05-23 - Accessible Custom Checkboxes
**Learning:** The codebase used `display: none` for custom toggle switches, removing them from the accessibility tree and keyboard navigation.
**Action:** Replace `display: none` with visually hidden styles (`opacity: 0; width: 0; height: 0; position: absolute;`) to maintain focusability while hiding the default input.

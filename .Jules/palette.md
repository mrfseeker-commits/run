## 2024-05-23 - Accessibility First for Dashboards
**Learning:** Even simple toggle switches need accessible names. Screen readers announce "checkbox" without context, leaving users guessing. Also, dynamic content updates (like weather recommendations) are invisible to screen readers without `aria-live`.
**Action:** Always verify form controls have associated labels (visible or via aria-label) and wrap dynamic updates in live regions.

## 2024-05-27 - Keyboard Navigable Custom Checkboxes
**Learning:** Using `display: none` on custom `<input type="checkbox">` elements removes them from the tab order, breaking keyboard accessibility for toggles and switches. Screen reader users can't find them, and keyboard users can't interact with them.
**Action:** Always use a "visually hidden" CSS pattern (e.g., `opacity: 0; width: 0; height: 0; position: absolute;`) for custom checkboxes to ensure they remain in the focus order, and always provide a `:focus-visible` outline on adjacent visual elements (like a slider).

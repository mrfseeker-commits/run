## 2024-05-23 - Accessibility First for Dashboards
**Learning:** Even simple toggle switches need accessible names. Screen readers announce "checkbox" without context, leaving users guessing. Also, dynamic content updates (like weather recommendations) are invisible to screen readers without `aria-live`.
**Action:** Always verify form controls have associated labels (visible or via aria-label) and wrap dynamic updates in live regions.

## 2024-05-27 - Keyboard Navigable Custom Checkboxes
**Learning:** Using `display: none` on custom `<input type="checkbox">` elements removes them from the tab order, breaking keyboard accessibility for toggles and switches. Screen reader users can't find them, and keyboard users can't interact with them.
**Action:** Always use a "visually hidden" CSS pattern (e.g., `opacity: 0; width: 0; height: 0; position: absolute;`) for custom checkboxes to ensure they remain in the focus order, and always provide a `:focus-visible` outline on adjacent visual elements (like a slider).

## 2026-05-28 - ARIA Switch Role Behavior
**Learning:** When applying `role='switch'` to native `<input type='checkbox'>` elements, the `aria-checked` attribute is implicitly handled by the browser based on the `checked` state, so it does not need to be manually updated via JavaScript.
**Action:** Use `role='switch'` on theme toggles and custom toggle checkboxes for better screen reader announcements without adding redundant state management code.

## 2026-05-29 - Semantic Landmarks and Decorative Emojis
**Learning:** Using basic generic `<div>` tags for page headers and wrappers prevents screen readers from understanding page structure. Also, emojis used merely as visual icons in dashboards are read aloud, creating redundant noise when text labels are already present.
**Action:** Always use semantic HTML tags like `<main>`, `<h1>`, `<h2>` for major sections. Apply `aria-hidden="true"` to purely decorative emojis/icons to silence redundant screen reader announcements.

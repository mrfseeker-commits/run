## 2024-05-23 - Accessibility First for Dashboards
**Learning:** Even simple toggle switches need accessible names. Screen readers announce "checkbox" without context, leaving users guessing. Also, dynamic content updates (like weather recommendations) are invisible to screen readers without `aria-live`.
**Action:** Always verify form controls have associated labels (visible or via aria-label) and wrap dynamic updates in live regions.

## 2024-05-27 - Keyboard Navigable Custom Checkboxes
**Learning:** Using `display: none` on custom `<input type="checkbox">` elements removes them from the tab order, breaking keyboard accessibility for toggles and switches. Screen reader users can't find them, and keyboard users can't interact with them.
**Action:** Always use a "visually hidden" CSS pattern (e.g., `opacity: 0; width: 0; height: 0; position: absolute;`) for custom checkboxes to ensure they remain in the focus order, and always provide a `:focus-visible` outline on adjacent visual elements (like a slider).

## 2026-05-28 - ARIA Switch Role Behavior
**Learning:** When applying `role='switch'` to native `<input type='checkbox'>` elements, the `aria-checked` attribute is implicitly handled by the browser based on the `checked` state, so it does not need to be manually updated via JavaScript.
**Action:** Use `role='switch'` on theme toggles and custom toggle checkboxes for better screen reader announcements without adding redundant state management code.

## 2026-06-07 - Semantic Landmarks and Structural Margins
**Learning:** Replacing structural `<div>` elements with semantic heading elements (`<h1>`, `<h2>`) or landmarks (`<main>`) is crucial for screen reader navigation, but it can introduce layout shifts due to the browser's default user-agent stylesheets (e.g., `margin-top` on headings). Furthermore, purely decorative emojis or icons must be hidden from screen readers using `aria-hidden="true"` to prevent redundant and confusing announcements.
**Action:** When converting structural `<div>` elements to headings to improve the document outline, always inspect and reset default browser margins (e.g., `margin-top: 0;`) in the CSS to preserve the intended layout. Always apply `aria-hidden="true"` to decorative icons that do not provide functional or meaningful information beyond what is already conveyed by adjacent text.

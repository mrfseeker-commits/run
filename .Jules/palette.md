## 2024-05-23 - Accessibility First for Dashboards
**Learning:** Even simple toggle switches need accessible names. Screen readers announce "checkbox" without context, leaving users guessing. Also, dynamic content updates (like weather recommendations) are invisible to screen readers without `aria-live`.
**Action:** Always verify form controls have associated labels (visible or via aria-label) and wrap dynamic updates in live regions.

## 2024-05-27 - Keyboard Navigable Custom Checkboxes
**Learning:** Using `display: none` on custom `<input type="checkbox">` elements removes them from the tab order, breaking keyboard accessibility for toggles and switches. Screen reader users can't find them, and keyboard users can't interact with them.
**Action:** Always use a "visually hidden" CSS pattern (e.g., `opacity: 0; width: 0; height: 0; position: absolute;`) for custom checkboxes to ensure they remain in the focus order, and always provide a `:focus-visible` outline on adjacent visual elements (like a slider).

## 2026-05-28 - ARIA Switch Role Behavior
**Learning:** When applying `role='switch'` to native `<input type='checkbox'>` elements, the `aria-checked` attribute is implicitly handled by the browser based on the `checked` state, so it does not need to be manually updated via JavaScript.
**Action:** Use `role='switch'` on theme toggles and custom toggle checkboxes for better screen reader announcements without adding redundant state management code.
## 2026-06-01 - Semantic Landmarks and Hidden Emojis
**Learning:** Relying solely on `<div>` tags for major UI sections creates a flat outline for screen readers, making navigation difficult. Additionally, decorative emojis used purely for visual flair alongside visible text can create redundant or confusing audio clutter if not explicitly hidden from the accessibility tree.
**Action:** Use semantic HTML elements like `<header>`, `<main>`, and heading tags (`<h1>`, `<h2>`) to define structural landmarks. When converting `<div>` tags to headings, actively monitor and reset default browser margins (e.g., `margin-top: 0`) to prevent layout shifts. Always apply `aria-hidden="true"` to decorative visual elements that do not provide unique functional context.

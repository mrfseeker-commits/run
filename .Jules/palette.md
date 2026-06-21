## 2024-05-23 - Accessibility First for Dashboards
**Learning:** Even simple toggle switches need accessible names. Screen readers announce "checkbox" without context, leaving users guessing. Also, dynamic content updates (like weather recommendations) are invisible to screen readers without `aria-live`.
**Action:** Always verify form controls have associated labels (visible or via aria-label) and wrap dynamic updates in live regions.

## 2024-05-27 - Keyboard Navigable Custom Checkboxes
**Learning:** Using `display: none` on custom `<input type="checkbox">` elements removes them from the tab order, breaking keyboard accessibility for toggles and switches. Screen reader users can't find them, and keyboard users can't interact with them.
**Action:** Always use a "visually hidden" CSS pattern (e.g., `opacity: 0; width: 0; height: 0; position: absolute;`) for custom checkboxes to ensure they remain in the focus order, and always provide a `:focus-visible` outline on adjacent visual elements (like a slider).

## 2026-05-28 - ARIA Switch Role Behavior
**Learning:** When applying `role='switch'` to native `<input type='checkbox'>` elements, the `aria-checked` attribute is implicitly handled by the browser based on the `checked` state, so it does not need to be manually updated via JavaScript.
**Action:** Use `role='switch'` on theme toggles and custom toggle checkboxes for better screen reader announcements without adding redundant state management code.

## 2024-05-18 - Semantic Landmarks and Decorative Emojis
**Learning:** Purely visual structural `<div>` elements hinder screen reader navigation and should be replaced with semantic landmarks like `<header>`, `<main>`, `<h1>`, and `<h2>` for better accessibility. Additionally, purely decorative emojis within icons or inline text cause redundant audio announcements for screen readers and should be hidden using `aria-hidden="true"`. Note that changing `<div>` tags to heading elements can cause layout shifts due to default margins, requiring resets like `margin-top: 0`.
**Action:** When inspecting structural markup, look for generic containers functioning as headers or main content areas and convert them to semantic tags. Also scan for decorative emojis used as icons and apply `aria-hidden="true"` to them to declutter the accessibility tree. Always test layout after adding headings to catch unexpected default margin shifts.

## 2024-06-21 - Decorative Emojis in JavaScript Strings
**Learning:** Emojis used purely for decoration in dynamic text strings (like alerts or weather info) can cause verbose, redundant audio announcements for screen reader users. When injected via JavaScript, they often lack proper accessibility semantics.
**Action:** Always wrap decorative emojis in `<span aria-hidden="true">` within template literals, and ensure you use `.innerHTML` rather than `.innerText` to inject them so the HTML tags are parsed correctly.

## 2024-04-23 - Theme Toggle Accessibility Update
**Learning:** In KAIST Track Weather, custom toggle switches using `display: none` on inputs break keyboard navigation and screen reader accessibility. Visually hiding elements (opacity: 0, width: 0, height: 0) while keeping them focusable is essential.
**Action:** When creating custom checkbox-based toggles, always use visually hidden CSS patterns, add `:focus-visible` styles on adjacent elements for keyboard users, and include `role="switch"` and `aria-label` to provide context for screen readers.

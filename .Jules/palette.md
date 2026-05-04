## 2026-04-10 - Custom Toggle Switch Accessibility
**Learning:** Using `display: none` on inputs for custom toggle switches completely removes them from the accessibility tree and breaks keyboard navigation (tabbing).
**Action:** Always use the visually hidden pattern (`position: absolute; opacity: 0; width: 0; height: 0;`) for custom inputs and add `:focus-visible` styles to their visual counterparts to preserve screen reader and keyboard accessibility.

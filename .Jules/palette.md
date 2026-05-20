## 2026-05-20 - Accessible Theme Toggle Switch
**Learning:** Custom toggle switches using `display: none` on the underlying checkbox completely remove the element from the accessibility tree, making it impossible to navigate to via keyboard or interact with via screen readers.
**Action:** Use the visually hidden pattern (`opacity: 0; width: 0; position: absolute;`) instead of `display: none` for underlying inputs. Always pair with `:focus-visible` on the adjacent visible element (like a slider) to provide a clear focus ring, and add `role="switch"` with a descriptive `aria-label`.

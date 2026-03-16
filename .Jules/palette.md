## 2026-03-16 - Custom Toggle Switch Accessibility
**Learning:** Custom toggle switches using `display: none` on inputs remove them from the accessibility tree and keyboard focus order entirely, making them completely unusable for keyboard and screen reader users.
**Action:** Always use the "visually hidden" pattern (`position: absolute; width: 0; height: 0; opacity: 0;`) for custom inputs instead of `display: none`, and ensure focus is delegated visually to the adjacent visible element (e.g., using `:focus-visible + .slider`).


## 2026-04-21 - Accessible visually hidden inputs
**Learning:** Accessible hidden inputs (e.g., custom checkboxes for a switch) must use the 'visually hidden' CSS pattern (opacity: 0, width: 0, height: 0, absolute position) instead of `display: none`, and should include a `:focus-visible` outline on adjacent elements to ensure accessibility for screen readers and keyboard navigation.
**Action:** Always use visually hidden patterns over `display: none` and implement focus styles for adjacent pseudo-elements when creating custom accessible inputs.

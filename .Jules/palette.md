## 2026-05-04 - Accessible Hidden Inputs
**Learning:** Accessible hidden inputs (e.g., custom checkboxes) must use the 'visually hidden' CSS pattern (opacity: 0, width: 0, height: 0, absolute position) instead of display: none, and should include a :focus-visible outline on adjacent elements to ensure accessibility for screen readers and keyboard navigation.
**Action:** Always check display:none usages on interactive elements and use the visually hidden pattern with focus-visible instead.

## 2026-03-07 - Custom Form Input Keyboard Accessibility
**Learning:** Using `display: none` on custom form inputs (like toggle switches) completely breaks keyboard accessibility and screen reader support, as the element is removed from the accessibility tree.
**Action:** Always use the "visually hidden" CSS pattern (`position: absolute; opacity: 0; width: 0; height: 0;`) along with a `:focus-visible` outline on the adjacent visual element to ensure interactive custom UI components are fully accessible via keyboard navigation.

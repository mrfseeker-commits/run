## 2025-04-25 - [Make hidden inputs accessible]
**Learning:** Using `display: none` for custom inputs like toggle switches completely hides them from screen readers and keyboard navigation, breaking accessibility.
**Action:** When implementing custom visual inputs (like sliders), use the "visually hidden" pattern on the native input element (`position: absolute`, `opacity: 0`, `width: 0`, `height: 0`) and apply a `:focus-visible` outline to the adjacent visible element to ensure keyboard and screen reader accessibility.

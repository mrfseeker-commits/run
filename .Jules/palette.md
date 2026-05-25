## 2026-05-25 - Custom Checkbox A11y
**Learning:** Using `display: none` on native checkboxes inside custom toggle switches completely breaks keyboard navigation and screen reader support, as focus is lost and element becomes un-tabbable.
**Action:** Always use the visually hidden CSS pattern (`position: absolute; opacity: 0; width: 0; height: 0;`) for the native checkbox input and implement a `:focus-visible` outline on an adjacent sibling (like the slider/toggle track) to ensure focus visibility while maintaining custom UI design.

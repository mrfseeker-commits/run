## 2024-05-24 - Accessible Hidden Inputs
**Learning:** Using `display: none` completely removes elements from the accessibility tree, making custom inputs invisible to screen readers and impossible to focus with a keyboard.
**Action:** Accessible hidden inputs must use the "visually hidden" CSS pattern (opacity: 0, width: 0, height: 0, absolute position) instead of `display: none`, and include a `:focus-visible` outline on adjacent elements (like custom sliders) to ensure full accessibility for screen readers and keyboard navigation.

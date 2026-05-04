## 2024-05-14 - Custom Checkbox Accessibility
**Learning:** Custom checkboxes built using the `display: none` technique are completely hidden from screen readers and cannot receive keyboard focus, destroying accessibility.
**Action:** Always use the 'visually hidden' pattern (`opacity: 0; width: 0; height: 0; position: absolute;`) combined with `:focus-visible` styling on adjacent visible elements to ensure keyboard navigability while maintaining custom visual designs.

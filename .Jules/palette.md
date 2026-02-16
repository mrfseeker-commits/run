## 2024-05-21 - [Theme Switch Accessibility]
**Learning:** Custom toggle switches using `display: none` on inputs completely block keyboard navigation.
**Action:** Use the visually-hidden pattern (`opacity: 0; width: 0; height: 0`) and ensure `:focus-visible` styles are applied to the visible slider element.

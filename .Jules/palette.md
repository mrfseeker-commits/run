
## 2024-05-15 - [Theme Toggle Keyboard Accessibility]
**Learning:** Custom toggle inputs created with `display: none` completely break keyboard accessibility and are ignored by screen readers.
**Action:** Always use the "visually hidden" pattern (`opacity: 0`, `position: absolute`, `width: 0`, `height: 0`) for the actual `<input>` element instead of `display: none`, and style its sibling (e.g., `.slider`) based on the input's `:focus-visible` state.

# Palette's UX Journal

## 2026-03-14 - [Accessible Custom Checkboxes and Keyboard Focus]
**Learning:** `display: none` completely removes an input element from the accessibility tree, preventing screen readers from announcing it and keyboard users from focusing it. When creating custom toggle switches or styled checkboxes, using a visually hidden approach (`opacity: 0`, `width: 0`, `height: 0`, `position: absolute`) ensures the input remains accessible. Furthermore, targeting `.input:focus-visible + .slider` to add a visible outline is critical for providing clear focus feedback to keyboard users on elements where the underlying input is visually hidden.

**Action:** When restyling default inputs into custom components, use the visually hidden pattern instead of `display: none`. Always ensure a visible focus indicator exists on the customized visual component (e.g., the `.slider`) via `:focus-visible` when the visually hidden input receives keyboard focus.
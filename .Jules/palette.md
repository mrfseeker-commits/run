
## 2024-05-23 - Accessible Hidden Inputs for Theme Toggles
**Learning:** Using `display: none` on `<input type="checkbox">` for toggle switches completely removes them from the accessibility tree, making them un-focusable via keyboard and invisible to screen readers.
**Action:** Always use the "visually hidden" CSS pattern (`opacity: 0`, `width: 0`, `height: 0`, `position: absolute`) instead of `display: none` for custom styled inputs. Additionally, apply `:focus-visible` outlines to adjacent elements (like the `.slider`) to provide clear visual feedback during keyboard navigation.

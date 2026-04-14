## 2024-05-24 - Accessible Toggle Switches
**Learning:** Custom toggle switches using `display: none` on the input element become inaccessible to keyboard navigation and screen readers. Playwright tests (`page.wait_for_selector`) also fail on visually hidden elements.
**Action:** Use the visually hidden CSS pattern (`opacity: 0`, `width: 0`, `height: 0`, `position: absolute`) instead of `display: none`. Apply `:focus-visible` to an adjacent visible element to ensure focus rings appear during keyboard navigation, and rely on other wait conditions in tests.

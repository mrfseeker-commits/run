## 2024-05-19 - Accessible Hidden Pattern for Toggle Switches
**Learning:** In this application, custom toggle switches were previously implemented using `display: none` for the underlying checkbox input, completely hiding them from screen readers and making keyboard navigation impossible.
**Action:** Always use the "visually hidden" pattern (`opacity: 0`, `width: 0`, `height: 0`, `position: absolute`) instead of `display: none` for accessible hidden inputs. Add a `:focus-visible` outline to the adjacent visible element (`.slider`) to provide a clear focus indicator for keyboard users.

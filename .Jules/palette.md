## 2025-02-12 - Keyboard Accessibility in Custom Toggles
**Learning:** Hiding checkbox inputs with `display: none` completely removes them from the accessibility tree, preventing keyboard users from interacting with custom toggles.
**Action:** Always use the "visually hidden" pattern (opacity: 0, width: 0, height: 0, absolute position) for custom inputs to maintain keyboard focusability while customizing the UI.

## 2024-01-01 - Initial Setup\n**Learning:** Accessibility and UX are crucial for this application.\n**Action:** Ensure all interactive elements have proper ARIA attributes and focus states.

## 2024-05-15 - Accessible Custom Checkboxes
**Learning:** Using `display: none` on custom checkboxes (like toggle switches) completely removes them from the accessibility tree, preventing screen reader announcements and keyboard navigation. Custom focus states cannot be triggered.
**Action:** Use the "visually hidden" pattern (`position: absolute; opacity: 0; width: 0; height: 0;`) instead, and use `:focus-visible` on adjacent visible elements to provide clear keyboard focus rings.

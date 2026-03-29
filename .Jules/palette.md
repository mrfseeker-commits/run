## 2026-02-21 - [Hidden Input Accessibility]
**Learning:** Custom checkboxes using `display: none` remove elements from the accessibility tree, making them inaccessible to keyboard/screen reader users.
**Action:** Use `.visually-hidden` class (clip/size 1px) to keep them focusable but hidden.

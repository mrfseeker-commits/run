## 2024-05-22 - Accessible Toggle Switches
**Learning:** This app uses checkbox inputs for toggle switches but lacks accessible names and roles. A pattern of `role="switch"` + `aria-label` is needed.
**Action:** When encountering custom toggle switches (checkboxes with sliders), always add `role="switch"` and a descriptive `aria-label`. Consider adding visual icons (like emojis via CSS `content`) to the slider knob for immediate state recognition without extra assets.

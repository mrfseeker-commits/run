## 2024-05-31 - [Semantic HTML for Layouts]
**Learning:** Generic `div` elements were used for major layout areas (header, main, footer) which reduces screen reader comprehension of the document structure.
**Action:** Replaced `div.header-container` with `<header>`, `div.main-wrapper` with `<main>`, and `div.footer-email` with `<footer>` to improve a11y via semantic HTML landmarks.

## 2024-05-31 - [ARIA Hidden and aria-label interaction]
**Learning:** Adding `aria-hidden="true"` to an element with `role="img"` and `aria-label` completely removes it from the accessibility tree, hiding the label.
**Action:** Do not use `aria-hidden="true"` on elements that provide essential screen reader information via `aria-label`. Only use it on purely decorative elements.

from playwright.sync_api import sync_playwright
import os

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Load the local index.html file
        file_path = os.path.abspath("index.html")
        page.goto(f"file://{file_path}")

        # 1. Verify aria-label on the checkbox
        checkbox = page.locator("input[type='checkbox']")
        aria_label = checkbox.get_attribute("aria-label")
        print(f"Checkbox aria-label: {aria_label}")
        if aria_label != "다크 모드 전환":
            print("FAIL: aria-label mismatch")
        else:
            print("PASS: aria-label is correct")

        # 2. Verify semantic landmarks
        header = page.locator("header.header-container")
        main = page.locator("main.main-wrapper")
        footer = page.locator("footer.footer-email")

        if header.count() == 1 and main.count() == 1 and footer.count() == 1:
            print("PASS: Semantic landmarks found")
        else:
            print("FAIL: Semantic landmarks missing")
            print(f"Header: {header.count()}, Main: {main.count()}, Footer: {footer.count()}")

        # 3. Verify weather icons have role="img"
        # Wait for data to load (mock data loads fast but let's be safe)
        page.wait_for_selector(".ts-icon")
        icons = page.locator(".ts-icon span[role='img']")
        count = icons.count()
        if count > 0:
            print(f"PASS: Found {count} icons with role='img'")
        else:
            print("FAIL: No icons with role='img' found")

        # 4. Verify Focus State
        # Focus the checkbox
        checkbox.focus()
        page.screenshot(path="verification/focus_state.png")
        print("Screenshot taken: verification/focus_state.png")

        browser.close()

if __name__ == "__main__":
    run()

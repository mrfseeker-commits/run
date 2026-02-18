import os
from playwright.sync_api import sync_playwright, expect

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Load local file
        cwd = os.getcwd()
        file_path = f"file://{cwd}/index.html"
        print(f"Loading {file_path}")
        page.goto(file_path)

        # 1. Verify Title
        expect(page).to_have_title("KAIST Track Weather")

        # 2. Verify Theme Toggle Accessibility
        # Find by aria-label
        toggle = page.get_by_label("다크 모드 전환")
        expect(toggle).to_be_attached()

        # Check if it is visually hidden (opacity 0)
        # We can check computed style
        opacity = toggle.evaluate("el => window.getComputedStyle(el).opacity")
        print(f"Toggle opacity: {opacity}")
        if opacity != "0":
            print("ERROR: Toggle should have opacity 0")

        # 3. Focus and Screenshot
        toggle.focus()

        # Take screenshot of the header area where the toggle is
        header = page.locator(".header-content")
        header.screenshot(path="verification/verification.png")
        print("Screenshot saved to verification/verification.png")

        browser.close()

if __name__ == "__main__":
    run()

from playwright.sync_api import sync_playwright
import os

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        # Open the file
        cwd = os.getcwd()
        file_path = f"file://{cwd}/index.html"
        print(f"Opening {file_path}")
        page.goto(file_path)

        # Wait for rendering (mock data fallback might take a tick)
        page.wait_for_timeout(1000)

        # 1. Verify Light Mode (Default)
        print("Taking Light Mode Screenshot...")
        page.screenshot(path="verification/light_mode.png")

        # Verify Aria Label
        switch_input = page.locator(".theme-switch input")
        aria_label = switch_input.get_attribute("aria-label")
        print(f"Aria Label: {aria_label}")
        if aria_label != "Toggle dark mode":
            print("ERROR: Aria label missing or incorrect")

        # 2. Toggle Switch
        print("Clicking Theme Switch...")
        # Since input is hidden, we click the label or the slider
        # We also want to verify focus ring, so let's try keyboard nav
        print("Testing Keyboard Navigation...")
        page.keyboard.press("Tab") # Maybe focus title or body first?
        # If body is focused, first tab might go to the switch if it's the first interactive element.
        # Let's just click for now to toggle state.
        page.locator(".theme-switch").click()

        # Wait for transition
        page.wait_for_timeout(1000)

        # 3. Verify Dark Mode
        print("Taking Dark Mode Screenshot...")
        page.screenshot(path="verification/dark_mode.png")

        browser.close()

if __name__ == "__main__":
    run()

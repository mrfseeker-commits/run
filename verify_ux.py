import os
from playwright.sync_api import sync_playwright

def verify_ux():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        # Load the local HTML file
        page.goto(f"file://{os.getcwd()}/index.html")

        # Select the theme switch
        checkbox = page.locator("#checkbox")

        # Check ARIA label
        aria_label = checkbox.get_attribute("aria-label")
        print(f"ARIA Label: {aria_label}")

        # Take a screenshot of the theme switch area
        # We target the label which wraps the input and the slider
        theme_switch = page.locator(".theme-switch")
        theme_switch.screenshot(path="theme_toggle_state.png")

        browser.close()

if __name__ == "__main__":
    verify_ux()

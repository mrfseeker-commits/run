import time
from playwright.sync_api import sync_playwright

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    page.on('console', lambda msg: print(f"CONSOLE: {msg.text}"))
    page.on('pageerror', lambda err: print(f"ERROR: {err}"))

    print("Navigating to index.html...")
    page.goto('file:///app/index.html')
    time.sleep(1) # wait for initial load

    mock_data = [
        {"time": "04:00", "temp": -22, "sky": "Clear", "wind": 12, "pop": 0, "pty": 0},
    ]

    print("Injecting mock data...")
    page.evaluate("(data) => render(data)", mock_data)
    time.sleep(1) # wait for render

    print("Checking for sunrise aria-hidden element...")
    sunrise_element = page.locator("#sunrise-info span[aria-hidden='true']")
    if sunrise_element.count() > 0:
        print("✅ Sunrise emoji aria-hidden span found.")
        print(f"Sunrise HTML: {page.locator('#sunrise-info').inner_html()}")
    else:
        print("❌ Sunrise emoji aria-hidden span NOT found.")

    print("Checking for warning aria-hidden element...")
    warning_element = page.locator("#rec-text span[aria-hidden='true']")
    if warning_element.count() > 0:
        print("✅ Warning emoji aria-hidden span found.")
        print(f"Warning HTML: {page.locator('#rec-text').inner_html()}")
    else:
        print("❌ Warning emoji aria-hidden span NOT found.")

    context.close()
    browser.close()

with sync_playwright() as playwright:
    run(playwright)

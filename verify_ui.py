import time
from playwright.sync_api import sync_playwright

def run_cuj(page):
    page.goto('file:///app/index.html')
    time.sleep(1) # wait for initial load

    mock_data = [
        {"time": "04:00", "temp": -22, "sky": "Clear", "wind": 12, "pop": 0, "pty": 0},
    ]

    page.evaluate("(data) => render(data)", mock_data)
    time.sleep(1) # wait for render

    page.screenshot(path="/app/verification/verification.png")
    time.sleep(1)

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            record_video_dir="/app/verification"
        )
        page = context.new_page()
        try:
            run_cuj(page)
        finally:
            context.close()
            browser.close()
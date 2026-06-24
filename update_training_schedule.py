"""Fetch the latest weekly training image from Naver Cafe and OCR it."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from io import BytesIO
from pathlib import Path
from zoneinfo import ZoneInfo

import pytesseract
import requests
from bs4 import BeautifulSoup
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
from playwright.sync_api import sync_playwright


CAFE_ID = "30488045"
MENU_ID = "13"
MENU_URL = f"https://cafe.naver.com/f-e/cafes/{CAFE_ID}/menus/{MENU_ID}"
OUTPUT_PATH = Path(__file__).with_name("training_schedule.json")
TARGET_DAYS = {"화", "목", "토", "일"}
KST = ZoneInfo("Asia/Seoul")
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"
)


def normalize_text(text: str) -> str:
    text = text.replace("×", "x").replace("X", "x")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def find_latest_article() -> dict:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(
            user_agent=USER_AGENT,
            locale="ko-KR",
            timezone_id="Asia/Seoul",
        )
        page.goto(MENU_URL, wait_until="domcontentloaded", timeout=60_000)
        page.wait_for_selector('a[href*="/articles/"]', timeout=30_000)

        links = page.locator('a[href*="/articles/"]').evaluate_all(
            """elements => elements.map(a => ({
                title: (a.innerText || '').trim(),
                href: a.href
            }))"""
        )
        browser.close()

    seen = set()
    candidates = []
    for link in links:
        title = normalize_text(link["title"])
        match = re.search(r"/articles/(\d+)", link["href"])
        if not match or not title or "댓글수" in title:
            continue
        article_id = int(match.group(1))
        if article_id in seen:
            continue
        seen.add(article_id)
        if re.search(r"\d+월\s*\d+주", title) and re.search(r"일정|훈련", title):
            candidates.append(
                {"article_id": article_id, "title": title, "url": link["href"]}
            )

    if not candidates:
        raise RuntimeError("주간 훈련 일정 게시물을 찾지 못했습니다.")
    return candidates[0]


def find_schedule_images(article: dict) -> list[str]:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(
            user_agent=USER_AGENT,
            locale="ko-KR",
            timezone_id="Asia/Seoul",
        )
        page.goto(article["url"], wait_until="domcontentloaded", timeout=60_000)
        frame = page.frame_locator('iframe[title="카페 메인"]')
        frame.locator("img.se-image-resource").first.wait_for(
            state="attached", timeout=30_000
        )
        urls = frame.locator("img.se-image-resource").evaluate_all(
            "elements => elements.map(img => img.currentSrc || img.src)"
        )
        browser.close()
    return list(dict.fromkeys(urls))


def download_image(url: str) -> Image.Image:
    response = requests.get(
        url,
        headers={"User-Agent": USER_AGENT, "Referer": "https://cafe.naver.com/"},
        timeout=30,
    )
    response.raise_for_status()
    return Image.open(BytesIO(response.content)).convert("RGB")


def preprocess(image: Image.Image) -> Image.Image:
    scale = max(2, 1800 // max(image.width, 1))
    image = image.resize(
        (image.width * scale, image.height * scale), Image.Resampling.LANCZOS
    )
    image = ImageOps.grayscale(image)
    image = ImageEnhance.Contrast(image).enhance(1.8)
    return image.filter(ImageFilter.SHARPEN)


def run_ocr(image: Image.Image) -> list[str]:
    processed = preprocess(image)
    outputs = []
    for psm in (6, 4, 11):
        outputs.append(
            pytesseract.image_to_string(
                processed,
                lang="kor+eng",
                config=f"--oem 3 --psm {psm}",
            )
        )
    return outputs


def parse_week_label(title: str, ocr_text: str) -> str:
    match = re.search(r"(\d{1,2})월\s*(\d)주", f"{title}\n{ocr_text}")
    return f"{match.group(1)}월 {match.group(2)}주" if match else "주간 훈련"


def infer_year(month: int, day: int, now: datetime) -> int:
    year = now.year
    if now.month == 12 and month == 1:
        year += 1
    elif now.month == 1 and month == 12:
        year -= 1
    return year


def parse_rows(text: str, now: datetime) -> list[dict]:
    cleaned = text.replace("|", " ").replace("（", "(").replace("）", ")")
    cleaned = re.sub(r"(?<=\d)[Il](?=\d)", "1", cleaned)
    lines = [normalize_text(line) for line in cleaned.splitlines() if line.strip()]
    rows = []

    for index, line in enumerate(lines):
        match = re.search(
            r"(?<!\d)(\d{1,2})\s*[\(\[\{]?\s*([월화수목금토일])\s*[\)\]\}]?",
            line,
        )
        if not match:
            continue

        day_number = int(match.group(1))
        weekday = match.group(2)
        if weekday not in TARGET_DAYS:
            continue

        training = line[match.end() :].strip(" :-")
        if len(training) < 2 and index + 1 < len(lines):
            training = lines[index + 1].strip(" :-")
        training = normalize_text(training)
        if not training or training in {"일", "훈련내용"}:
            continue

        rows.append(
            {
                "day_number": day_number,
                "day": weekday,
                "training": training,
            }
        )

    unique = {}
    for row in rows:
        unique[(row["day_number"], row["day"])] = row
    return list(unique.values())


def build_schedule(article: dict, image_url: str, ocr_text: str) -> dict:
    now = datetime.now(KST)
    week_label = parse_week_label(article["title"], ocr_text)
    month_match = re.search(r"(\d{1,2})월", week_label)
    if not month_match:
        raise RuntimeError("일정의 월을 인식하지 못했습니다.")
    month = int(month_match.group(1))

    rows = parse_rows(ocr_text, now)
    if len(rows) < 3:
        raise RuntimeError(f"필요한 일정 행을 충분히 인식하지 못했습니다: {rows}")

    schedule = []
    for row in rows:
        year = infer_year(month, row["day_number"], now)
        date = datetime(year, month, row["day_number"]).date()
        schedule.append(
            {
                "date": date.isoformat(),
                "day": row["day"],
                "training": row["training"],
            }
        )
    schedule.sort(key=lambda item: item["date"])

    return {
        "article_id": article["article_id"],
        "article_title": article["title"],
        "week_label": week_label,
        "source_url": article["url"],
        "source_image_url": image_url,
        "published_at": None,
        "updated_at": now.isoformat(timespec="seconds"),
        "schedule": schedule,
    }


def load_existing() -> dict:
    if not OUTPUT_PATH.exists():
        return {}
    return json.loads(OUTPUT_PATH.read_text(encoding="utf-8"))


def update_from_cafe() -> bool:
    article = find_latest_article()
    existing = load_existing()
    if existing.get("article_id") == article["article_id"]:
        print(f"이미 반영된 게시물입니다: {article['title']}")
        return False

    image_urls = find_schedule_images(article)
    if not image_urls:
        raise RuntimeError("게시물에서 일정 이미지를 찾지 못했습니다.")

    best = None
    errors = []
    for image_url in image_urls:
        image = download_image(image_url)
        for ocr_text in run_ocr(image):
            try:
                candidate = build_schedule(article, image_url, ocr_text)
                if best is None or len(candidate["schedule"]) > len(best["schedule"]):
                    best = candidate
            except Exception as error:  # try the next image/configuration
                errors.append(str(error))

    if best is None:
        raise RuntimeError("OCR 일정 분석에 실패했습니다: " + " | ".join(errors[-5:]))

    OUTPUT_PATH.write_text(
        json.dumps(best, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"{best['week_label']} 일정 {len(best['schedule'])}건을 저장했습니다.")
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", type=Path, help="로컬 이미지 OCR 테스트")
    args = parser.parse_args()

    if args.image:
        image = Image.open(args.image).convert("RGB")
        now = datetime.now(KST)
        for text in run_ocr(image):
            rows = parse_rows(text, now)
            if rows:
                print(json.dumps(rows, ensure_ascii=False, indent=2))
                return 0
        return 1

    try:
        update_from_cafe()
        return 0
    except Exception as error:
        print(f"일정 업데이트 실패: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

"""Fetch and publish the latest weekly Naver Cafe training table without OCR."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timedelta
from io import BytesIO
from pathlib import Path
from zoneinfo import ZoneInfo

import requests
from PIL import Image
from playwright.sync_api import sync_playwright


CAFE_ID = "30488045"
MENU_ID = "13"
MENU_URL = f"https://cafe.naver.com/f-e/cafes/{CAFE_ID}/menus/{MENU_ID}"
OUTPUT_PATH = Path(__file__).with_name("training_schedule.json")
IMAGE_DIR = Path(__file__).with_name("assets") / "training" / "current"
TARGET_ROW_INDEXES = {
    0: "월",
    1: "화",
    2: "수",
    3: "목",
    4: "금",
    5: "토",
    6: "일",
}
DAY_IMAGE_NAMES = {
    "월": "monday.webp",
    "화": "tuesday.webp",
    "수": "wednesday.webp",
    "목": "thursday.webp",
    "금": "friday.webp",
    "토": "saturday.webp",
    "일": "sunday.webp",
}
WEEKDAY_NUMBER = {"월": 0, "화": 1, "수": 2, "목": 3, "금": 4, "토": 5, "일": 6}
KST = ZoneInfo("Asia/Seoul")
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"
)


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


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


def find_horizontal_grid_lines(image: Image.Image) -> list[int]:
    pixels = image.convert("RGB").load()
    minimum_dark_pixels = int(image.width * 0.72)
    candidates = []
    for y in range(image.height):
        dark_pixels = sum(
            1
            for x in range(image.width)
            if max(pixels[x, y]) < 230 and max(pixels[x, y]) - min(pixels[x, y]) < 12
        )
        if dark_pixels >= minimum_dark_pixels:
            candidates.append(y)

    groups = []
    for y in candidates:
        if not groups or y > groups[-1][-1] + 1:
            groups.append([y])
        else:
            groups[-1].append(y)
    return [round(sum(group) / len(group)) for group in groups]


def find_schedule_header_bottom(image: Image.Image) -> int:
    pixels = image.convert("RGB").load()
    minimum_green_pixels = int(image.width * 0.55)
    green_rows = []
    for y in range(image.height):
        green_pixels = sum(
            1
            for x in range(image.width)
            if (
                pixels[x, y][1] >= 145
                and pixels[x, y][1] >= pixels[x, y][0] + 25
                and pixels[x, y][1] >= pixels[x, y][2] + 45
            )
        )
        if green_pixels >= minimum_green_pixels:
            green_rows.append(y)

    if not green_rows:
        raise RuntimeError("훈련 일정 표의 초록색 머리글을 찾지 못했습니다.")

    groups = []
    for y in green_rows:
        if not groups or y > groups[-1][-1] + 1:
            groups.append([y])
        else:
            groups[-1].append(y)
    header = max(groups, key=len)
    if len(header) < max(4, int(image.height * 0.025)):
        raise RuntimeError("훈련 일정 표의 초록색 머리글 영역이 너무 작습니다.")
    return header[-1] + 1


def find_training_column_start(image: Image.Image, top: int, bottom: int) -> int:
    pixels = image.convert("RGB").load()
    minimum_dark_pixels = int((bottom - top) * 0.72)
    candidates = []
    for x in range(1, image.width - 1):
        dark_pixels = sum(
            1
            for y in range(top, bottom + 1)
            if max(pixels[x, y]) < 230 and max(pixels[x, y]) - min(pixels[x, y]) < 12
        )
        if dark_pixels >= minimum_dark_pixels:
            candidates.append(x)

    interior = [x for x in candidates if image.width * 0.12 < x < image.width * 0.42]
    if not interior:
        raise RuntimeError("훈련 일정 표의 날짜/내용 구분선을 찾지 못했습니다.")
    return round(sum(interior) / len(interior))


def schedule_row_boundaries(image: Image.Image) -> list[int]:
    header_bottom = find_schedule_header_bottom(image)
    lines = find_horizontal_grid_lines(image)
    row_ends = [line for line in lines if line > header_bottom + 2][:7]
    if len(row_ends) < 7:
        raise RuntimeError(
            f"훈련 일정 표의 월~일 구분선을 충분히 찾지 못했습니다: {lines}"
        )
    return [header_bottom, *row_ends]


def validate_schedule_table(image: Image.Image) -> list[int]:
    boundaries = schedule_row_boundaries(image)
    find_training_column_start(image, boundaries[0], boundaries[-1])
    return boundaries


def split_schedule_rows(image: Image.Image) -> list[Image.Image]:
    boundaries = validate_schedule_table(image)
    rows = [
        image.crop((1, top + 1, image.width - 1, bottom))
        for top, bottom in zip(boundaries, boundaries[1:])
    ]
    if len(rows) != 7:
        raise RuntimeError(f"훈련 일정 7개 행을 분리하지 못했습니다: {len(rows)}")
    return rows


def write_schedule_images(image: Image.Image, data: dict) -> None:
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    original_path = IMAGE_DIR / "original.webp"
    image.save(original_path, format="WEBP", lossless=True, method=6)
    data["source_image_path"] = original_path.relative_to(OUTPUT_PATH.parent).as_posix()

    rows = split_schedule_rows(image)
    schedule_by_day = {item["day"]: item for item in data["schedule"]}
    for row_index, weekday in TARGET_ROW_INDEXES.items():
        row_path = IMAGE_DIR / DAY_IMAGE_NAMES[weekday]
        rows[row_index].save(row_path, format="WEBP", lossless=True, method=6)
        schedule_by_day[weekday]["image_path"] = row_path.relative_to(
            OUTPUT_PATH.parent
        ).as_posix()


def parse_week_label(title: str) -> str:
    match = re.search(r"(\d{1,2})월\s*(\d)주", title)
    return f"{match.group(1)}월 {match.group(2)}주" if match else "주간 훈련"


def schedule_dates_for_run(now: datetime) -> list:
    """Return this week's dates; a Sunday update prepares the next week."""
    today = now.date()
    monday_offset = 1 if today.weekday() == 6 else -today.weekday()
    monday = today + timedelta(days=monday_offset)
    return [monday + timedelta(days=offset) for offset in range(7)]


def validate_schedule(schedule: list[dict]) -> None:
    if len(schedule) != len(TARGET_ROW_INDEXES):
        raise RuntimeError(f"월~일 7개 일정을 만들지 못했습니다: {schedule}")
    for item in schedule:
        date = datetime.fromisoformat(item["date"]).date()
        if date.weekday() != WEEKDAY_NUMBER[item["day"]]:
            raise RuntimeError(f"날짜와 요일이 일치하지 않습니다: {item}")


def build_schedule_from_table(article: dict, image_url: str, image: Image.Image) -> dict:
    now = datetime.now(KST)
    week_label = parse_week_label(article["title"])
    match = re.fullmatch(r"(\d{1,2})월 (\d)주", week_label)
    if not match:
        raise RuntimeError("게시물 제목에서 일정 주차를 인식하지 못했습니다.")

    dates = schedule_dates_for_run(now)
    month = int(match.group(1))
    if month not in {date.month for date in dates}:
        raise RuntimeError(
            f"게시물 주차({week_label})가 현재 일정 주간과 일치하지 않습니다."
        )

    validate_schedule_table(image)
    schedule = [
        {
            "date": dates[row_index].isoformat(),
            "day": weekday,
            "training": "",
        }
        for row_index, weekday in TARGET_ROW_INDEXES.items()
    ]
    validate_schedule(schedule)
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


def update_from_cafe(force: bool = False) -> bool:
    article = find_latest_article()
    existing = load_existing()
    if not force and existing.get("article_id") == article["article_id"]:
        print(f"이미 반영된 게시물입니다: {article['title']}")
        return False

    image_urls = find_schedule_images(article)
    if not image_urls:
        raise RuntimeError("게시물에서 일정 이미지를 찾지 못했습니다.")

    candidates = []
    errors = []
    for image_url in image_urls:
        image = download_image(image_url)
        try:
            data = build_schedule_from_table(article, image_url, image)
            candidates.append((image.width * image.height, image, data))
        except Exception as error:
            errors.append(str(error))

    if not candidates:
        raise RuntimeError("훈련 일정 표 분석에 실패했습니다: " + " | ".join(errors[-5:]))

    _, best_image, best = max(candidates, key=lambda item: item[0])
    write_schedule_images(best_image, best)
    OUTPUT_PATH.write_text(
        json.dumps(best, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"{best['week_label']} 원본 일정 이미지 7개 행을 저장했습니다.")
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", type=Path, help="로컬 일정표 이미지 구조 테스트")
    parser.add_argument("--week-label", help="로컬 이미지의 주차, 예: 8월 2주")
    parser.add_argument("--force", action="store_true", help="같은 게시물도 다시 저장")
    args = parser.parse_args()

    if args.image:
        image = Image.open(args.image).convert("RGB")
        article = {
            "article_id": 0,
            "title": args.week_label or args.image.stem,
            "url": args.image.resolve().as_uri(),
        }
        result = build_schedule_from_table(article, article["url"], image)
        print(json.dumps(result["schedule"], ensure_ascii=False, indent=2))
        return 0

    try:
        update_from_cafe(force=args.force)
        return 0
    except Exception as error:
        print(f"일정 업데이트 실패: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

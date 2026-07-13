"""Fetch the latest weekly training image from Naver Cafe and OCR it."""

from __future__ import annotations

import argparse
import calendar
import json
import re
import statistics
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
TARGET_ROW_INDEXES = {1: "화", 3: "목", 5: "토", 6: "일"}
WEEKDAY_NUMBER = {"월": 0, "화": 1, "수": 2, "목": 3, "금": 4, "토": 5, "일": 6}
KST = ZoneInfo("Asia/Seoul")
PREVIOUS_MONTH_THRESHOLD = 20
WEEKDAY_ALIASES = {
    "화": "화",
    "와": "화",
    "하": "화",
    "목": "목",
    "묵": "목",
    "토": "토",
    "일": "일",
}
DISTANCE_PATTERN = r"(400|1000|2000|5000)"
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"
)


def normalize_text(text: str) -> str:
    text = text.replace("×", "x").replace("X", "x")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def normalize_training_text(text: str) -> str:
    text = normalize_text(text)
    text = text.replace("회선", "회전").replace("외전", "회전")
    text = re.sub(r"\b4000[7T]?\s*x\s*", "400m x ", text, flags=re.IGNORECASE)
    text = re.sub(r"\b([125])0000\s*x\s*", r"\g<1>000m x ", text)
    text = re.sub(rf"\b{DISTANCE_PATTERN}\s*m?\s*x\s*", r"\1m x ", text)
    text = re.sub(rf"\b{DISTANCE_PATTERN}m\s*x\s*156\b", r"\1m x 1set", text)
    text = re.sub(rf"\b{DISTANCE_PATTERN}m\s*x\s*1\s*56\b", r"\1m x 1set", text)
    text = re.sub(rf"\b{DISTANCE_PATTERN}m\s*x\s*([0-9]+(?:\.[0-9]+)?)\s*(?:5et|set|sct|sel)?\b", r"\1m x \2set", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*x\s*", " × ", text)
    text = re.sub(r"\s+", " ", text).strip()
    interval = re.search(
        rf"\b{DISTANCE_PATTERN}[^×]{{0,12}}×\s*([0-9]+(?:\.[0-9]+)?)",
        text,
    )
    if "카이스트" in text and interval:
        distance = interval.group(1)
        repetitions = interval.group(2)
        if "." not in repetitions and len(repetitions) > 2 and repetitions.endswith("56"):
            repetitions = repetitions[:-2]
        text = f"카이스트 {distance}m × {repetitions}set"
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


def split_training_cells(image: Image.Image) -> list[Image.Image]:
    lines = find_horizontal_grid_lines(image)
    if len(lines) < 7:
        raise RuntimeError(f"훈련 일정 표의 가로선을 충분히 찾지 못했습니다: {lines}")

    row_ends = lines[-7:]
    row_height = round(statistics.median(
        later - earlier for earlier, later in zip(row_ends, row_ends[1:])
    ))
    row_boundaries = [row_ends[0] - row_height, *row_ends]
    column_start = find_training_column_start(image, row_boundaries[0], row_boundaries[-1])
    cells = []
    for top, bottom in zip(row_boundaries, row_boundaries[1:]):
        cells.append(image.crop((column_start + 2, top + 2, image.width - 2, bottom - 2)))
    if len(cells) != 7:
        raise RuntimeError(f"훈련 일정 7개 행을 분리하지 못했습니다: {len(cells)}")
    return cells


def training_candidate_score(text: str) -> int:
    text = normalize_training_text(text)
    score = len(text)
    if "카이스트" in text:
        score += 30
    if "계족산" in text:
        score += 30
    if "빌드업런" in text:
        score += 25
    if re.search(rf"{DISTANCE_PATTERN}m × \d+(?:\.\d+)?set", text):
        score += 35
    if re.search(r"\d+회전", text):
        score += 25
    if re.search(r"4000[7T]?|\b156\b|회선|외전", text):
        score -= 100
    return score


def ocr_training_cell(cell: Image.Image) -> str:
    processed = preprocess(cell)
    variants = [
        processed,
        processed.point(lambda value: 255 if value > 175 else 0),
    ]
    candidates = []
    for variant in variants:
        for language in ("kor+eng", "kor"):
            text = pytesseract.image_to_string(
                variant,
                lang=language,
                config="--oem 3 --psm 7",
            )
            normalized = normalize_training_text(text)
            if normalized:
                candidates.append(normalized)
    if not candidates:
        raise RuntimeError("훈련 내용 셀을 인식하지 못했습니다.")
    return max(candidates, key=training_candidate_score)


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


def week_dates(year: int, month: int, week_number: int) -> list:
    weeks = calendar.Calendar(firstweekday=calendar.MONDAY).monthdatescalendar(year, month)
    if week_number < 1 or week_number > len(weeks):
        raise RuntimeError(f"{month}월 {week_number}주 날짜를 계산하지 못했습니다.")
    return weeks[week_number - 1]


def validate_schedule(schedule: list[dict]) -> None:
    if len(schedule) != len(TARGET_ROW_INDEXES):
        raise RuntimeError(f"화/목/토/일 4개 일정을 모두 인식하지 못했습니다: {schedule}")

    for item in schedule:
        date = datetime.fromisoformat(item["date"]).date()
        expected_weekday = item["day"]
        if date.weekday() != WEEKDAY_NUMBER[expected_weekday]:
            raise RuntimeError(f"날짜와 요일이 일치하지 않습니다: {item}")
        training = item["training"]
        if not is_supported_training_text(training):
            raise RuntimeError(f"OCR 신뢰도가 낮은 훈련 내용입니다: {training}")


def has_suspicious_training_text(training: str) -> bool:
    return bool(
        re.search(r"\b[125]0000\b|\b156\b|\b4000[7T]?\b", training)
        or any(error in training for error in ("회선", "외전"))
    )


def is_supported_training_text(training: str) -> bool:
    patterns = (
        r"카이스트 빌드업런",
        rf"카이스트 {DISTANCE_PATTERN}m × \d+(?:\.\d+)?set",
        r"계족산 \d+회전",
    )
    return any(re.fullmatch(pattern, training) for pattern in patterns)


def build_schedule_from_table(article: dict, image_url: str, image: Image.Image) -> dict:
    now = datetime.now(KST)
    week_label = parse_week_label(article["title"], "")
    match = re.fullmatch(r"(\d{1,2})월 (\d)주", week_label)
    if not match:
        raise RuntimeError("게시물 제목에서 일정 주차를 인식하지 못했습니다.")

    month = int(match.group(1))
    week_number = int(match.group(2))
    year = infer_year(month, 1, now)
    dates = week_dates(year, month, week_number)
    cells = split_training_cells(image)
    schedule = []
    for row_index, weekday in TARGET_ROW_INDEXES.items():
        schedule.append(
            {
                "date": dates[row_index].isoformat(),
                "day": weekday,
                "training": ocr_training_cell(cells[row_index]),
            }
        )
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


def parse_rows(text: str, now: datetime, default_month: int | None = None) -> list[dict]:
    cleaned = text.replace("|", " ").replace("（", "(").replace("）", ")")
    cleaned = re.sub(r"(?<=\d)[Il](?=\d)", "1", cleaned)
    lines = [normalize_text(line) for line in cleaned.splitlines() if line.strip()]
    rows = []

    for index, line in enumerate(lines):
        match = re.search(
            r"(?<!\d)(?:(\d{1,2})\s*/\s*)?(\d{1,2})\s*[\(\[\{]?\s*([월화수목금토일와하묵])\s*[\)\]\}]?",
            line,
        )
        if not match:
            continue

        row_month = int(match.group(1)) if match.group(1) else None
        day_number = int(match.group(2))
        weekday = WEEKDAY_ALIASES.get(match.group(3), match.group(3))
        if weekday not in TARGET_DAYS:
            continue
        if row_month is None and default_month and day_number > PREVIOUS_MONTH_THRESHOLD:
            row_month = default_month - 1 if default_month > 1 else 12

        training = line[match.end() :].strip(" :-")
        if len(training) < 2 and index + 1 < len(lines):
            training = lines[index + 1].strip(" :-")
        training = normalize_training_text(training)
        if not training or training in {"일", "훈련내용"}:
            continue

        rows.append(
            {
                "month": row_month,
                "day_number": day_number,
                "day": weekday,
                "training": training,
            }
        )

    unique = {}
    for row in rows:
        unique[(row["month"], row["day_number"], row["day"])] = row
    return list(unique.values())


def build_schedule(article: dict, image_url: str, ocr_text: str) -> dict:
    now = datetime.now(KST)
    week_label = parse_week_label(article["title"], ocr_text)
    month_match = re.search(r"(\d{1,2})월", week_label)
    if not month_match:
        raise RuntimeError("일정의 월을 인식하지 못했습니다.")
    month = int(month_match.group(1))

    rows = parse_rows(ocr_text, now, month)
    if len(rows) < 3:
        raise RuntimeError(f"필요한 일정 행을 충분히 인식하지 못했습니다: {rows}")

    schedule = []
    for row in rows:
        row_month = row.get("month") or month
        year = infer_year(row_month, row["day_number"], now)
        date = datetime(year, row_month, row["day_number"]).date()
        schedule.append(
            {
                "date": date.isoformat(),
                "day": row["day"],
                "training": row["training"],
            }
        )
    schedule.sort(key=lambda item: item["date"])
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
    if (
        not force
        and existing.get("article_id") == article["article_id"]
        and not has_likely_ocr_errors(existing)
    ):
        print(f"이미 반영된 게시물입니다: {article['title']}")
        return False

    image_urls = find_schedule_images(article)
    if not image_urls:
        raise RuntimeError("게시물에서 일정 이미지를 찾지 못했습니다.")

    best = None
    errors = []
    for image_url in image_urls:
        image = download_image(image_url)
        try:
            candidate = build_schedule_from_table(article, image_url, image)
            if best is None:
                best = candidate
        except Exception as error:
            errors.append(str(error))

    if best is None:
        raise RuntimeError("OCR 일정 분석에 실패했습니다: " + " | ".join(errors[-5:]))

    OUTPUT_PATH.write_text(
        json.dumps(best, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"{best['week_label']} 일정 {len(best['schedule'])}건을 저장했습니다.")
    return True


def has_likely_ocr_errors(data: dict) -> bool:
    for item in data.get("schedule", []):
        training = item.get("training", "")
        date = item.get("date", "")
        if has_suspicious_training_text(training):
            return True
        if data.get("week_label", "").startswith("7월") and date.startswith("2026-07-30"):
            return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", type=Path, help="로컬 이미지 OCR 테스트")
    parser.add_argument("--week-label", help="로컬 이미지의 주차, 예: 7월 3주")
    parser.add_argument("--force", action="store_true", help="같은 게시물도 다시 OCR")
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

import unittest
from unittest.mock import patch

from PIL import Image, ImageDraw

import update_training_schedule as schedule


class TrainingScheduleOcrTests(unittest.TestCase):
    def test_known_interval_ocr_noise_is_canonicalized(self):
        self.assertEqual(
            "카이스트 400m × 10set",
            schedule.normalize_training_text("카이스트 40010 % x 1056"),
        )
        self.assertEqual(
            "카이스트 2000m × 3set",
            schedule.normalize_training_text("카이스트 2000m x 356set"),
        )

    def test_week_dates_use_calendar_rows(self):
        dates = schedule.week_dates(2026, 7, 3)

        self.assertEqual("2026-07-13", dates[0].isoformat())
        self.assertEqual("2026-07-19", dates[6].isoformat())

    def test_fixed_table_is_split_into_seven_training_cells(self):
        image = Image.new("RGB", (532, 337), "white")
        draw = ImageDraw.Draw(image)
        draw.rectangle((0, 37, 531, 74), fill=(146, 208, 80))
        for y in (0, 111, 148, 185, 222, 259, 296, 333):
            draw.line((0, y, 531, y), fill=(212, 212, 212), width=1)
        draw.line((121, 74, 121, 333), fill=(212, 212, 212), width=1)

        cells = schedule.split_training_cells(image)

        self.assertEqual(7, len(cells))
        self.assertTrue(all(cell.size == (407, 33) for cell in cells))

    def test_table_schedule_uses_title_and_row_positions_for_dates(self):
        image = Image.new("RGB", (532, 337), "white")
        draw = ImageDraw.Draw(image)
        for y in (0, 111, 148, 185, 222, 259, 296, 333):
            draw.line((0, y, 531, y), fill=(212, 212, 212), width=1)
        draw.line((121, 74, 121, 333), fill=(212, 212, 212), width=1)
        article = {"article_id": 1, "title": "7월3주 주간 일정", "url": "https://example.com"}
        values = iter([
            "카이스트 빌드업런",
            "카이스트 400m × 10set",
            "카이스트 2000m × 3set",
            "계족산 2회전",
        ])

        with patch.object(schedule, "ocr_training_cell", side_effect=lambda cell: next(values)):
            result = schedule.build_schedule_from_table(article, "image.png", image)

        self.assertEqual(
            ["2026-07-14", "2026-07-16", "2026-07-18", "2026-07-19"],
            [item["date"] for item in result["schedule"]],
        )

    def test_validation_rejects_wrong_weekday(self):
        invalid = [
            {"date": "2026-07-15", "day": "화", "training": "카이스트 빌드업런"},
            {"date": "2026-07-16", "day": "목", "training": "카이스트 400m × 10set"},
            {"date": "2026-07-18", "day": "토", "training": "카이스트 2000m × 3set"},
            {"date": "2026-07-19", "day": "일", "training": "계족산 2회전"},
        ]

        with self.assertRaisesRegex(RuntimeError, "날짜와 요일"):
            schedule.validate_schedule(invalid)

    def test_validation_rejects_unknown_ocr_text(self):
        invalid = [
            {"date": "2026-07-14", "day": "화", "training": "카이스트 빌드업런"},
            {"date": "2026-07-16", "day": "목", "training": "카이스트 40010 % × 1056"},
            {"date": "2026-07-18", "day": "토", "training": "카이스트 2000m × 3set"},
            {"date": "2026-07-19", "day": "일", "training": "계족산 2회전"},
        ]

        with self.assertRaisesRegex(RuntimeError, "OCR 신뢰도"):
            schedule.validate_schedule(invalid)


if __name__ == "__main__":
    unittest.main()

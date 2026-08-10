import unittest
from datetime import date, datetime
from unittest.mock import patch
from zoneinfo import ZoneInfo

from PIL import Image, ImageDraw

import update_training_schedule as schedule


class TrainingScheduleImageTests(unittest.TestCase):
    def test_sunday_update_targets_the_following_week(self):
        now = datetime(2026, 8, 9, 20, tzinfo=ZoneInfo("Asia/Seoul"))
        dates = schedule.schedule_dates_for_run(now)

        self.assertEqual("2026-08-10", dates[0].isoformat())
        self.assertEqual("2026-08-16", dates[6].isoformat())

    def test_midweek_update_keeps_the_current_week(self):
        now = datetime(2026, 8, 12, 9, tzinfo=ZoneInfo("Asia/Seoul"))
        dates = schedule.schedule_dates_for_run(now)

        self.assertEqual("2026-08-10", dates[0].isoformat())
        self.assertEqual("2026-08-16", dates[6].isoformat())

    def test_fixed_table_is_split_into_seven_full_rows(self):
        rows = schedule.split_schedule_rows(self.make_table_image())

        self.assertEqual(7, len(rows))
        self.assertTrue(all(row.width == 530 and row.height > 0 for row in rows))

    def test_fixed_table_supports_a_double_height_event_row(self):
        image = self.make_table_image(
            row_ends=(111, 148, 185, 222, 259, 333, 370), height=374
        )

        rows = schedule.split_schedule_rows(image)

        self.assertEqual(7, len(rows))
        self.assertGreater(rows[5].height, rows[4].height * 1.8)

    def test_non_schedule_spreadsheet_is_rejected(self):
        image = Image.new("RGB", (532, 337), "white")
        draw = ImageDraw.Draw(image)
        for y in range(0, 337, 20):
            draw.line((0, y, 531, y), fill=(212, 212, 212), width=1)

        with self.assertRaisesRegex(RuntimeError, "초록색 머리글"):
            schedule.validate_schedule_table(image)

    def test_table_schedule_uses_title_and_row_positions_for_dates(self):
        article = {
            "article_id": 1,
            "title": "8월2주 주간 일정",
            "url": "https://example.com",
        }
        dates = [date(2026, 8, 10 + offset) for offset in range(7)]

        with patch.object(schedule, "schedule_dates_for_run", return_value=dates):
            result = schedule.build_schedule_from_table(
                article, "image.png", self.make_table_image()
            )

        self.assertEqual(
            [f"2026-08-{day:02d}" for day in range(10, 17)],
            [item["date"] for item in result["schedule"]],
        )
        self.assertEqual(
            ["월", "화", "수", "목", "금", "토", "일"],
            [item["day"] for item in result["schedule"]],
        )
        self.assertTrue(all(item["training"] == "" for item in result["schedule"]))

    def test_validation_rejects_wrong_weekday(self):
        invalid = [
            {"date": "2026-08-11", "day": weekday, "training": ""}
            for weekday in ("월", "화", "수", "목", "금", "토", "일")
        ]

        with self.assertRaisesRegex(RuntimeError, "날짜와 요일"):
            schedule.validate_schedule(invalid)

    @staticmethod
    def make_table_image(row_ends=(111, 148, 185, 222, 259, 296, 333), height=337):
        image = Image.new("RGB", (532, height), "white")
        draw = ImageDraw.Draw(image)
        draw.rectangle((0, 37, 531, 74), fill=(146, 208, 80))
        for y in (0, *row_ends):
            draw.line((0, y, 531, y), fill=(212, 212, 212), width=1)
        draw.line((121, 74, 121, row_ends[-1]), fill=(212, 212, 212), width=1)
        return image


if __name__ == "__main__":
    unittest.main()

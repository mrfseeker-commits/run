import unittest
from datetime import date, datetime
from unittest.mock import patch
from zoneinfo import ZoneInfo

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
        self.assertEqual(
            "카이스트 2000m × 2.5set",
            schedule.normalize_training_text("카이스트 2000m x 2.5656set"),
        )

    def test_candidate_selection_prefers_plausible_repetition(self):
        self.assertEqual(
            "카이스트 2000m × 2.5set",
            schedule.select_training_candidate(
                [
                    "카이스트 2000m × 2.5set",
                    "카이스트 2000m × 2.556set",
                    "카이스트 2000m × 2.5656set",
                ]
            ),
        )
        self.assertEqual(
            "카이스트 1000m × 5set",
            schedule.select_training_candidate(
                [
                    "카이스트 1000m × 5set",
                    "카이스트 1000m × 5set",
                    "카이스트 1000m × 552set",
                ]
            ),
        )

    def test_candidate_selection_rejects_only_implausible_repetitions(self):
        with self.assertRaisesRegex(RuntimeError, "신뢰할 수 있는"):
            schedule.select_training_candidate(
                [
                    "카이스트 2000m × 2.46set",
                    "카이스트 1000m × 552set",
                ]
            )

    def test_sunday_update_targets_the_following_week(self):
        now = datetime(2026, 8, 2, 20, tzinfo=ZoneInfo("Asia/Seoul"))
        dates = schedule.schedule_dates_for_run(now)

        self.assertEqual("2026-08-03", dates[0].isoformat())
        self.assertEqual("2026-08-09", dates[6].isoformat())

    def test_midweek_update_keeps_the_current_week(self):
        now = datetime(2026, 8, 4, 9, tzinfo=ZoneInfo("Asia/Seoul"))
        dates = schedule.schedule_dates_for_run(now)

        self.assertEqual("2026-08-03", dates[0].isoformat())
        self.assertEqual("2026-08-09", dates[6].isoformat())

    def test_fixed_table_is_split_into_seven_training_cells(self):
        image = self.make_table_image()

        cells = schedule.split_training_cells(image)

        self.assertEqual(7, len(cells))
        self.assertTrue(all(cell.width == 407 and cell.height > 0 for cell in cells))

    def test_fixed_table_is_split_into_seven_full_rows(self):
        rows = schedule.split_schedule_rows(self.make_table_image())

        self.assertEqual(7, len(rows))
        self.assertTrue(all(row.width == 530 and row.height > 0 for row in rows))

    def test_table_schedule_uses_title_and_row_positions_for_dates(self):
        article = {
            "article_id": 1,
            "title": "8월1주 주간 일정",
            "url": "https://example.com",
        }
        values = iter(
            [
                "카이스트 2000m × 2.5set",
                "카이스트 1000m × 5set",
                "카이스트 5000m × 1set",
                "계족산 2회전",
            ]
        )
        dates = [date(2026, 8, 3 + offset) for offset in range(7)]

        with (
            patch.object(schedule, "ocr_training_cell", side_effect=lambda cell: next(values)),
            patch.object(schedule, "schedule_dates_for_run", return_value=dates),
        ):
            result = schedule.build_schedule_from_table(
                article, "image.png", self.make_table_image()
            )

        self.assertEqual(
            [f"2026-08-{day:02d}" for day in range(3, 10)],
            [item["date"] for item in result["schedule"]],
        )
        self.assertEqual(
            ["월", "화", "수", "목", "금", "토", "일"],
            [item["day"] for item in result["schedule"]],
        )
        self.assertEqual("", result["schedule"][2]["training"])

    def test_validation_rejects_wrong_weekday(self):
        invalid = [
            {"date": "2026-08-04", "day": weekday, "training": "훈련"}
            for weekday in ("월", "화", "수", "목", "금", "토", "일")
        ]

        with self.assertRaisesRegex(RuntimeError, "날짜와 요일"):
            schedule.validate_schedule(invalid)

    def test_validation_rejects_unknown_ocr_text(self):
        self.assertTrue(
            schedule.has_suspicious_training_text("카이스트 1000m × 552set")
        )

    def test_training_table_scores_higher_than_attendance_table(self):
        attendance = {
            "schedule": [{"training": "김일근 박송욱 김종홍"} for _ in range(7)]
        }
        training = {
            "schedule": [
                {"training": "자율훈련 / 갑천조깅(60분)"},
                {"training": "카이스트 2000m × 2.5set"},
            ]
        }

        self.assertGreater(
            schedule.schedule_candidate_score(training),
            schedule.schedule_candidate_score(attendance),
        )

    @staticmethod
    def make_table_image():
        image = Image.new("RGB", (532, 337), "white")
        draw = ImageDraw.Draw(image)
        draw.rectangle((0, 37, 531, 74), fill=(146, 208, 80))
        for y in (0, 111, 148, 185, 222, 259, 296, 333):
            draw.line((0, y, 531, y), fill=(212, 212, 212), width=1)
        draw.line((121, 74, 121, 333), fill=(212, 212, 212), width=1)
        return image


if __name__ == "__main__":
    unittest.main()

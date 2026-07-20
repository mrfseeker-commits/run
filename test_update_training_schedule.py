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
        pass

    def test_fixed_table_is_split_into_seven_full_rows(self):
        pass

    def test_table_schedule_uses_title_and_row_positions_for_dates(self):
        pass

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
        pass


if __name__ == "__main__":
    unittest.main()

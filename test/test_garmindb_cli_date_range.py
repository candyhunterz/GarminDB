"""Tests for GarminDB CLI download date range calculations."""

import datetime
import importlib.util
from pathlib import Path
from unittest import TestCase, main
from unittest.mock import patch


CLI_PATH = Path(__file__).resolve().parents[1] / "scripts" / "garmindb_cli.py"
spec = importlib.util.spec_from_file_location("garmindb_cli_under_test", CLI_PATH)
assert spec is not None
assert spec.loader is not None
garmindb_cli = importlib.util.module_from_spec(spec)
spec.loader.exec_module(garmindb_cli)


class FixedDate(datetime.date):
    @classmethod
    def today(cls):
        return cls(2026, 6, 8)


class StubConfig:
    def stat_start_date(self, stat_name):
        assert stat_name == "sleep"
        return datetime.date(2026, 6, 6), 30


class StubTable:
    value: datetime.datetime | None = None

    @classmethod
    def latest_time(cls, db, col):
        return cls.value


class TestGarminDbCliDateRange(TestCase):
    def _main(self):
        main_obj = garmindb_cli.GarminDbMain.__new__(garmindb_cli.GarminDbMain)
        main_obj.gc_config = StubConfig()
        return main_obj

    def test_all_download_range_includes_today(self):
        StubTable.value = None
        with patch.object(garmindb_cli.datetime, "date", FixedDate):
            date, days = self._main()._GarminDbMain__get_date_and_days(object(), False, StubTable, object(), "sleep")

        self.assertEqual(date, datetime.date(2026, 6, 6))
        self.assertEqual(days, 3)  # 2026-06-06, 2026-06-07, and 2026-06-08

    def test_latest_download_range_includes_today(self):
        StubTable.value = datetime.datetime(2026, 6, 7)
        with patch.object(garmindb_cli.datetime, "date", FixedDate):
            date, days = self._main()._GarminDbMain__get_date_and_days(object(), True, StubTable, object(), "sleep")

        self.assertEqual(date, datetime.date(2026, 6, 6))
        self.assertEqual(days, 3)  # 2026-06-06, 2026-06-07, and 2026-06-08


if __name__ == "__main__":
    main()

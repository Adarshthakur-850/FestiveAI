import pytest
from datetime import date, datetime, timezone
import pytz
from app.services.calendar_service import CalendarService, FESTIVAL_CATALOG

def test_festival_catalog_astronomical_dates():
    # Verify Diwali dates vary annually across lunisolar cycles
    diwali_entry = next(f for f in FESTIVAL_CATALOG if f["slug"] == "diwali")
    assert diwali_entry["dates"][2025] == date(2025, 10, 20)
    assert diwali_entry["dates"][2026] == date(2026, 11, 8)
    assert diwali_entry["dates"][2027] == date(2027, 10, 29)

    # Verify Holi dates
    holi_entry = next(f for f in FESTIVAL_CATALOG if f["slug"] == "holi")
    assert holi_entry["dates"][2025] == date(2025, 3, 14)
    assert holi_entry["dates"][2026] == date(2026, 3, 4)

    # Verify fixed dates
    xmas = next(f for f in FESTIVAL_CATALOG if f["slug"] == "christmas")
    assert xmas["default_fixed_month"] == 12
    assert xmas["default_fixed_day"] == 25
    assert xmas["dates"][2025] == date(2025, 12, 25)
    assert xmas["dates"][2026] == date(2026, 12, 25)

def test_calculate_publish_datetime_timezone_awareness():
    target_date = date(2026, 11, 8)  # Diwali 2026
    # 09:00:00 Asia/Kolkata is 03:30:00 UTC (IST is UTC+5:30)
    pub_dt = CalendarService.calculate_publish_datetime(
        target_date,
        target_publish_time_str="09:00:00",
        timezone_str="Asia/Kolkata"
    )
    assert pub_dt.tzinfo is not None
    assert pub_dt.hour == 3
    assert pub_dt.minute == 30
    assert pub_dt.year == 2026
    assert pub_dt.month == 11
    assert pub_dt.day == 8

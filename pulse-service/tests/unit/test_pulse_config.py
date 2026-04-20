"""Unit tests for PulseConfig entity — the heart of the check-in system."""
import pytest
from datetime import datetime, timedelta
from app.domain.entities import PulseConfig


class TestPulseConfigValidation:
    def test_valid_config(self):
        config = PulseConfig(user_id="u1", frequency_count=2, frequency_unit="months", grace_hours=48)
        assert config.frequency_in_days() == 60

    def test_weeks_frequency(self):
        config = PulseConfig(user_id="u1", frequency_count=1, frequency_unit="weeks")
        assert config.frequency_in_days() == 7

    def test_frequency_below_1_raises(self):
        with pytest.raises(ValueError, match="at least 1"):
            PulseConfig(user_id="u1", frequency_count=0)

    def test_frequency_above_24_raises(self):
        with pytest.raises(ValueError, match="cannot exceed 24"):
            PulseConfig(user_id="u1", frequency_count=25)

    def test_invalid_unit_raises(self):
        with pytest.raises(ValueError, match="Invalid frequency"):
            PulseConfig(user_id="u1", frequency_unit="days")

    def test_grace_below_minimum_raises(self):
        with pytest.raises(ValueError, match="minimum is 12"):
            PulseConfig(user_id="u1", grace_hours=6)

    def test_grace_above_maximum_raises(self):
        with pytest.raises(ValueError, match="maximum is 72"):
            PulseConfig(user_id="u1", grace_hours=100)


class TestCheckinSchedule:
    def test_next_checkin_date(self):
        config = PulseConfig(user_id="u1", frequency_count=2, frequency_unit="weeks")
        last = datetime(2026, 1, 1)
        assert config.next_checkin_date(last) == datetime(2026, 1, 15)

    def test_grace_deadline(self):
        config = PulseConfig(user_id="u1", frequency_count=1, frequency_unit="months", grace_hours=48)
        last = datetime(2026, 1, 1)
        expected_due = datetime(2026, 1, 31)
        expected_grace = expected_due + timedelta(hours=48)
        assert config.grace_deadline(last) == expected_grace

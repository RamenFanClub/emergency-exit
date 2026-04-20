"""Pulse domain entities — check-in timer and alert scheduling."""
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Optional

FREQUENCY_UNITS = ["weeks", "months"]
ALERT_STATUSES = ["active", "grace_period", "alert_sent", "resolved"]
MIN_GRACE_HOURS = 12
MAX_GRACE_HOURS = 72


@dataclass
class PulseConfig:
    """Configuration for a user's check-in schedule."""
    user_id: str
    frequency_count: int = 2
    frequency_unit: str = "months"
    grace_hours: int = 48
    verification_method: str = "face"
    id: str | None = None

    def __post_init__(self):
        if self.frequency_count < 1:
            raise ValueError("Frequency count must be at least 1")
        if self.frequency_count > 24:
            raise ValueError("Frequency count cannot exceed 24")
        if self.frequency_unit not in FREQUENCY_UNITS:
            raise ValueError(f"Invalid frequency unit: {self.frequency_unit}")
        if self.grace_hours < MIN_GRACE_HOURS:
            raise ValueError(f"Grace period minimum is {MIN_GRACE_HOURS} hours")
        if self.grace_hours > MAX_GRACE_HOURS:
            raise ValueError(f"Grace period maximum is {MAX_GRACE_HOURS} hours")

    def frequency_in_days(self) -> int:
        """Convert the frequency setting to days."""
        if self.frequency_unit == "months":
            return self.frequency_count * 30
        return self.frequency_count * 7

    def next_checkin_date(self, last_checkin: datetime) -> datetime:
        """Calculate when the next check-in is due."""
        return last_checkin + timedelta(days=self.frequency_in_days())

    def grace_deadline(self, last_checkin: datetime) -> datetime:
        """Calculate when the grace period expires and alerts are sent."""
        due = self.next_checkin_date(last_checkin)
        return due + timedelta(hours=self.grace_hours)


@dataclass
class Checkin:
    """A single check-in confirmation."""
    user_id: str
    method: str = "face"
    device: str = ""
    ip_hash: str = ""
    id: str | None = None
    confirmed_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class AlertSchedule:
    """Tracks the alert state for a user."""
    user_id: str
    status: str = "active"
    next_alert_at: Optional[datetime] = None
    pings_sent: int = 0
    kin_notified_at: Optional[datetime] = None
    id: str | None = None

    def __post_init__(self):
        if self.status not in ALERT_STATUSES:
            raise ValueError(f"Invalid alert status: {self.status}")

    def is_overdue(self, now: datetime) -> bool:
        """Check if the user has missed their check-in window."""
        return self.next_alert_at is not None and now >= self.next_alert_at

"""Domain events published by the Guardian service."""
from dataclasses import dataclass
from datetime import datetime

@dataclass
class GuardianAdded:
    user_id: str
    guardian_id: str
    access_level: str
    timestamp: datetime

@dataclass
class AlertSentToKin:
    user_id: str
    guardian_ids: list
    timestamp: datetime

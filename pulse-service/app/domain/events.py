"""Domain events published by the Pulse service."""
from dataclasses import dataclass
from datetime import datetime

@dataclass
class CheckinConfirmed:
    user_id: str
    method: str
    timestamp: datetime

@dataclass
class CheckinOverdue:
    user_id: str
    overdue_since: datetime
    timestamp: datetime

@dataclass
class GracePeriodExpired:
    user_id: str
    timestamp: datetime

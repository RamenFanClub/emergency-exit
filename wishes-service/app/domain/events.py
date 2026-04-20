"""Domain events published by the Wishes service."""
from dataclasses import dataclass
from datetime import datetime

@dataclass
class WishRecorded:
    user_id: str
    wish_id: str
    category: str
    timestamp: datetime

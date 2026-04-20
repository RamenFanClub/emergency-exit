"""Domain events published by the Identity service."""
from dataclasses import dataclass
from datetime import datetime


@dataclass
class UserRegistered:
    user_id: str
    email: str
    timestamp: datetime

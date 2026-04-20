"""Wishes domain entities."""
from datetime import datetime
from dataclasses import dataclass, field

WISH_CATEGORIES = [
    "Funeral & Service", "Medical / end of life care",
    "Guardian for children", "Pet care", "Business succession",
    "Digital accounts", "Personal message", "Charitable giving", "Other",
]

PRIORITIES = ["high", "medium", "low"]


@dataclass
class Wish:
    """Aggregate root for a recorded wish."""
    user_id: str
    title: str
    category: str
    details: str = ""
    priority: str = "medium"
    id: str | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        if not self.title.strip():
            raise ValueError("Wish title cannot be empty")
        if self.category not in WISH_CATEGORIES:
            raise ValueError(f"Invalid category: {self.category}")
        if self.priority not in PRIORITIES:
            raise ValueError(f"Invalid priority: {self.priority}")


@dataclass
class ScheduledMessage:
    """A message to be delivered to a specific person after death."""
    user_id: str
    recipient_name: str
    message: str
    delivery_trigger: str = "on_death"
    id: str | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        if not self.recipient_name.strip():
            raise ValueError("Recipient name cannot be empty")
        if not self.message.strip():
            raise ValueError("Message cannot be empty")

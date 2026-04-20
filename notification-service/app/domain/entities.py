"""Notification types and templates."""
from dataclasses import dataclass
from typing import Optional

CHANNELS = ["email", "sms", "push"]


@dataclass
class Notification:
    """A notification to be sent to a guardian."""
    recipient_email: str
    recipient_phone: str = ""
    channel: str = "email"
    subject: str = ""
    body: str = ""
    user_display_name: str = ""

    def __post_init__(self):
        if self.channel not in CHANNELS:
            raise ValueError(f"Invalid channel: {self.channel}")
        if self.channel == "email" and not self.recipient_email:
            raise ValueError("Email address required for email notifications")
        if self.channel == "sms" and not self.recipient_phone:
            raise ValueError("Phone number required for SMS notifications")

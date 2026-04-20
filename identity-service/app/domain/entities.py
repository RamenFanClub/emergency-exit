"""
Identity domain entities.

These are the core business objects for user management.
They contain validation rules and business logic — no database
or framework dependencies.
"""
import re
from datetime import datetime
from dataclasses import dataclass, field


@dataclass
class User:
    """Aggregate root for user identity."""

    email: str
    hashed_password: str
    display_name: str
    id: str | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    mfa_enabled: bool = False
    is_active: bool = True

    def __post_init__(self):
        self._validate_email()

    def _validate_email(self):
        pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if not re.match(pattern, self.email):
            raise ValueError(f"Invalid email format: {self.email}")

    @staticmethod
    def validate_password_strength(password: str) -> None:
        """Enforce minimum password requirements."""
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not re.search(r"[A-Z]", password):
            raise ValueError("Password must contain an uppercase letter")
        if not re.search(r"[0-9]", password):
            raise ValueError("Password must contain a number")

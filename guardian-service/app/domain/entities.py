"""Guardian domain entities."""
from datetime import datetime
from dataclasses import dataclass, field

ACCESS_LEVELS = ["executor", "full", "wishes"]


@dataclass
class Guardian:
    """Aggregate root for a kin/guardian contact."""
    user_id: str
    first_name: str
    last_name: str = ""
    relationship: str = ""
    email: str = ""
    phone: str = ""
    access_level: str = "full"
    id: str | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    is_verified: bool = False

    def __post_init__(self):
        if not self.first_name.strip():
            raise ValueError("Guardian first name cannot be empty")
        if self.access_level not in ACCESS_LEVELS:
            raise ValueError(f"Invalid access level: {self.access_level}")

    def can_see_account_details(self) -> bool:
        """Only executor-level guardians can see sensitive account details."""
        return self.access_level == "executor"

    def can_see_wishes(self) -> bool:
        """All access levels can see wishes."""
        return True

    def can_see_assets(self) -> bool:
        """Only full and executor can see assets."""
        return self.access_level in ("executor", "full")

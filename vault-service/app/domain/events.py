"""Domain events published by the Vault service."""
from dataclasses import dataclass
from datetime import datetime


@dataclass
class AssetCreated:
    user_id: str
    asset_id: str
    category: str
    timestamp: datetime


@dataclass
class WillRecorded:
    user_id: str
    status: str
    timestamp: datetime

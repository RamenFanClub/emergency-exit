"""
Vault domain entities.

Business objects for assets, Will details, and supplementary documents.
"""
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional


ASSET_CATEGORIES = [
    "Bank account", "Property", "Investment", "Superannuation",
    "Life insurance", "Vehicle", "Cryptocurrency", "Business",
    "Personal item", "Digital account", "Other",
]

WILL_STATUSES = ["signed", "draft", "none"]

SUPP_DOC_TYPES = [
    "Statement of Wishes", "Enduring Power of Attorney",
    "Advance Health Directive", "Guardianship Nomination",
    "Funeral Pre-arrangement", "Business Succession Plan", "Other",
]


@dataclass
class Asset:
    """Aggregate root for a recorded asset."""

    user_id: str
    name: str
    category: str
    value: float = 0.0
    details: str = ""
    beneficiary: str = ""
    notes: str = ""
    id: str | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    version: int = 1

    def __post_init__(self):
        if not self.name.strip():
            raise ValueError("Asset name cannot be empty")
        if self.category not in ASSET_CATEGORIES:
            raise ValueError(f"Invalid category: {self.category}")
        if self.value < 0:
            raise ValueError("Asset value cannot be negative")


@dataclass
class Will:
    """Aggregate root for Will details."""

    user_id: str
    status: str
    date_signed: Optional[str] = None
    solicitor: str = ""
    primary_location: str = ""
    secondary_location: str = ""
    notes: str = ""
    id: str | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        if self.status not in WILL_STATUSES:
            raise ValueError(f"Invalid Will status: {self.status}")


@dataclass
class SupplementaryDoc:
    """A supplementary legal document record."""

    user_id: str
    doc_type: str
    name: str
    location: str = ""
    notes: str = ""
    id: str | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        if not self.name.strip():
            raise ValueError("Document name cannot be empty")
        if self.doc_type not in SUPP_DOC_TYPES:
            raise ValueError(f"Invalid document type: {self.doc_type}")

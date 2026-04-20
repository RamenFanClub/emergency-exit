"""
Unit tests for Asset entity.

TDD: These tests define the business rules for assets.
Run with: pytest tests/unit/ -v
"""
import pytest
from app.domain.entities import Asset


class TestAssetCreation:
    def test_valid_asset(self):
        asset = Asset(user_id="u1", name="ANZ Savings", category="Bank account", value=50000)
        assert asset.name == "ANZ Savings"
        assert asset.version == 1

    def test_empty_name_raises(self):
        with pytest.raises(ValueError, match="cannot be empty"):
            Asset(user_id="u1", name="", category="Bank account")

    def test_whitespace_name_raises(self):
        with pytest.raises(ValueError, match="cannot be empty"):
            Asset(user_id="u1", name="   ", category="Bank account")

    def test_invalid_category_raises(self):
        with pytest.raises(ValueError, match="Invalid category"):
            Asset(user_id="u1", name="Test", category="Made up")

    def test_negative_value_raises(self):
        with pytest.raises(ValueError, match="cannot be negative"):
            Asset(user_id="u1", name="Test", category="Property", value=-100)

    def test_zero_value_is_valid(self):
        asset = Asset(user_id="u1", name="Test", category="Property", value=0)
        assert asset.value == 0

    def test_all_categories_accepted(self):
        from app.domain.entities import ASSET_CATEGORIES
        for cat in ASSET_CATEGORIES:
            asset = Asset(user_id="u1", name="Test", category=cat)
            assert asset.category == cat

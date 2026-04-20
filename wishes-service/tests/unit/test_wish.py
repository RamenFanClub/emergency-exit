"""Unit tests for Wish entity."""
import pytest
from app.domain.entities import Wish, WISH_CATEGORIES


class TestWishCreation:
    def test_valid_wish(self):
        wish = Wish(user_id="u1", title="Cremation", category="Funeral & Service")
        assert wish.priority == "medium"

    def test_empty_title_raises(self):
        with pytest.raises(ValueError, match="cannot be empty"):
            Wish(user_id="u1", title="", category="Funeral & Service")

    def test_invalid_category_raises(self):
        with pytest.raises(ValueError, match="Invalid category"):
            Wish(user_id="u1", title="Test", category="Invalid")

    def test_invalid_priority_raises(self):
        with pytest.raises(ValueError, match="Invalid priority"):
            Wish(user_id="u1", title="Test", category="Other", priority="urgent")

    def test_all_categories_accepted(self):
        for cat in WISH_CATEGORIES:
            wish = Wish(user_id="u1", title="Test", category=cat)
            assert wish.category == cat

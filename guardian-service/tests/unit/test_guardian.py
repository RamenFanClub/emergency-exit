"""Unit tests for Guardian entity."""
import pytest
from app.domain.entities import Guardian


class TestGuardianCreation:
    def test_valid_guardian(self):
        g = Guardian(user_id="u1", first_name="Jane", last_name="Smith", access_level="executor")
        assert g.first_name == "Jane"

    def test_empty_name_raises(self):
        with pytest.raises(ValueError, match="cannot be empty"):
            Guardian(user_id="u1", first_name="")

    def test_invalid_access_level_raises(self):
        with pytest.raises(ValueError, match="Invalid access"):
            Guardian(user_id="u1", first_name="Jane", access_level="admin")


class TestAccessPermissions:
    def test_executor_sees_account_details(self):
        g = Guardian(user_id="u1", first_name="Jane", access_level="executor")
        assert g.can_see_account_details() is True

    def test_full_cannot_see_account_details(self):
        g = Guardian(user_id="u1", first_name="Jane", access_level="full")
        assert g.can_see_account_details() is False

    def test_wishes_only_cannot_see_assets(self):
        g = Guardian(user_id="u1", first_name="Jane", access_level="wishes")
        assert g.can_see_assets() is False

    def test_all_levels_can_see_wishes(self):
        for level in ["executor", "full", "wishes"]:
            g = Guardian(user_id="u1", first_name="Jane", access_level=level)
            assert g.can_see_wishes() is True

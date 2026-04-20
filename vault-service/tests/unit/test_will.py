"""Unit tests for Will entity."""
import pytest
from app.domain.entities import Will


class TestWillCreation:
    def test_valid_signed_will(self):
        will = Will(user_id="u1", status="signed", solicitor="Smith & Co")
        assert will.status == "signed"

    def test_valid_draft_will(self):
        will = Will(user_id="u1", status="draft")
        assert will.status == "draft"

    def test_invalid_status_raises(self):
        with pytest.raises(ValueError, match="Invalid Will status"):
            Will(user_id="u1", status="expired")

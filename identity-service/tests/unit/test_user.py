"""
Unit tests for User entity.

These tests validate business rules in isolation — no database,
no API, no external dependencies. Run with: pytest tests/unit/ -v
"""
import pytest
from app.domain.entities import User


class TestUserCreation:
    def test_valid_user(self):
        user = User(email="test@example.com", hashed_password="x", display_name="Test")
        assert user.email == "test@example.com"
        assert user.is_active is True

    def test_invalid_email_raises(self):
        with pytest.raises(ValueError, match="Invalid email"):
            User(email="not-an-email", hashed_password="x", display_name="Test")

    def test_empty_email_raises(self):
        with pytest.raises(ValueError):
            User(email="", hashed_password="x", display_name="Test")


class TestPasswordStrength:
    def test_short_password_raises(self):
        with pytest.raises(ValueError, match="at least 8"):
            User.validate_password_strength("Short1")

    def test_no_uppercase_raises(self):
        with pytest.raises(ValueError, match="uppercase"):
            User.validate_password_strength("lowercase1")

    def test_no_number_raises(self):
        with pytest.raises(ValueError, match="number"):
            User.validate_password_strength("NoNumberHere")

    def test_valid_password_passes(self):
        User.validate_password_strength("StrongPass1")  # Should not raise

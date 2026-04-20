"""
Shared test fixtures for vault-service.

Uses mongomock-motor for unit/integration tests so no real
MongoDB instance is needed during development.
"""
import pytest
from mongomock_motor import AsyncMongoMockClient


@pytest.fixture
def mongo_client():
    """Provide a mock MongoDB client for testing."""
    return AsyncMongoMockClient()


@pytest.fixture
def db(mongo_client):
    """Provide a mock database for testing."""
    return mongo_client["ee_vault_test"]

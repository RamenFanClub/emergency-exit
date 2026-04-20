"""
Base MongoDB repository pattern.

Each service extends this with its own collection-specific methods.
Uses Motor (async MongoDB driver) for non-blocking I/O with FastAPI.
"""
from typing import Optional
import structlog

logger = structlog.get_logger()


class BaseRepository:
    """Base class for MongoDB repositories."""

    def __init__(self, db, collection_name: str):
        self.collection = db[collection_name]

    async def create(self, document: dict) -> str:
        """Insert a document and return its ID."""
        result = await self.collection.insert_one(document)
        doc_id = str(result.inserted_id)
        logger.info("db.create", collection=self.collection.name, id=doc_id)
        return doc_id

    async def find_by_id(self, doc_id: str) -> Optional[dict]:
        """Find a single document by ID."""
        from bson import ObjectId
        return await self.collection.find_one({"_id": ObjectId(doc_id)})

    async def find_by_user(self, user_id: str) -> list:
        """Find all documents belonging to a user."""
        cursor = self.collection.find({"user_id": user_id})
        return await cursor.to_list(length=100)

    async def update(self, doc_id: str, updates: dict) -> bool:
        """Update a document by ID. Returns True if modified."""
        from bson import ObjectId
        result = await self.collection.update_one(
            {"_id": ObjectId(doc_id)},
            {"$set": updates}
        )
        return result.modified_count > 0

    async def delete(self, doc_id: str) -> bool:
        """Delete a document by ID. Returns True if deleted."""
        from bson import ObjectId
        result = await self.collection.delete_one({"_id": ObjectId(doc_id)})
        return result.deleted_count > 0

    async def count_by_user(self, user_id: str) -> int:
        """Count documents for a user."""
        return await self.collection.count_documents({"user_id": user_id})

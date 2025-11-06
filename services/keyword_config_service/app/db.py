from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING, ReturnDocument
import os

_mongo_client = None

def get_db():
    global _mongo_client
    if _mongo_client is None:
        _mongo_client = AsyncIOMotorClient(os.environ["MONGO_URI"])
    return _mongo_client[os.environ.get("MONGO_DB", "product")]

async def ensure_indexes():
    db = get_db()
    await db.keywords.create_index("seller_id", unique=True)

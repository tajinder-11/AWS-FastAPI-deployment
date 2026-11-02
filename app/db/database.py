from pymongo import AsyncMongoClient
from app.core.config import settings

client = AsyncMongoClient(
    settings.MONGODB_URL
)

database = client[
    settings.DATABASE_NAME
]

users_collection = database["users"]
refresh_tokens_collection = database["refresh_tokens"]

async def create_indexes():
    await users_collection.create_index(
        "email",
        unique=True,
    )
    await refresh_tokens_collection.create_index(
        "jti",
        unique=True,
    )
    await refresh_tokens_collection.create_index(
        "token_hash",
        unique=True,
    )
    await refresh_tokens_collection.create_index(
        "expires_at",
        expiresAfterSeconds=0,
    )
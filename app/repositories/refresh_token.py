from datetime import datetime, timezone

from app.db.database import refresh_tokens_collection


class RefreshTokenRepository:

    async def create(
        self,
        user_id: str,
        jti: str,
        token_hash: str,
        expires_at: datetime,
    ):
        document = {
            "user_id": user_id,
            "jti": jti,
            "token_hash": token_hash,
            "expires_at": expires_at,
            "revoked": False,
            "created_at": datetime.now(timezone.utc),
        }

        result = await refresh_tokens_collection.insert_one(
            document
        )

        return result.inserted_id

    async def get_by_jti(
        self,
        jti: str,
    ):
        return await refresh_tokens_collection.find_one(
            {
                "jti": jti,
            }
        )

    async def revoke(
        self,
        jti: str,
    ):
        return await refresh_tokens_collection.update_one(
            {
                "jti": jti,
                "revoked": False,
            },
            {
                "$set": {
                    "revoked": True,
                    "revoked_at": datetime.now(timezone.utc),
                }
            },
        )
    
    async def revoke_all_for_user(
        self,
        user_id: str,
    ):
        return await refresh_tokens_collection.update_many(
            {
                "user_id": user_id,
                "revoked": False,
            },
            {
                "$set": {
                    "revoked": True,
                    "revoked_at": datetime.now(timezone.utc),
                }
            },
        )
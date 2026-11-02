from app.db.database import users_collection


class UserRepository:

    async def get_by_email(
        self,
        email: str,
    ):
        return await users_collection.find_one(
            {
                "email": email
            }
        )

    async def create(
        self,
        user_data: dict,
    ):
        result = await users_collection.insert_one(
            user_data
        )

        return await users_collection.find_one(
            {
                "_id": result.inserted_id
            }
        )
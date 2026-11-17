from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.db.database import client
from app.api.routes.auth import router as auth_router
from app.api.routes.users import router as users_router

@asynccontextmanager
async def lifespan(app: FastAPI):

    await create_indexes()

    yield

    await client.close()


app = FastAPI(
    title="FastAPI Auth API",
    version="1.0.0",
)


@app.get("/")
async def root():
    return {
        "message": "API is running"
    }


@app.get("/health")
async def health():
    try:
        await client.admin.command("ping")

        return {
            "status": "healthy",
            "database": "connected",
        }

    except Exception as e:
        print("e", e)

        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
        }


app.include_router(
    auth_router,
    prefix="/api/v1/auth",
    tags=["Authentication"],
)

app.include_router(
    users_router,
    prefix="/api/v1/users",
    tags=["Users"],
)
from fastapi import FastAPI

from app.routes import users

app = FastAPI(title="FastAPI demo")
app.include_router(users.router)

@app.get("/")
def read_root():
    return { "message": "Hey backend is running"}
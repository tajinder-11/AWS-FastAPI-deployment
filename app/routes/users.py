from typing import List
from uuid import uuid4

from fastapi import APIRouter, HTTPException

from app.database import load_users, save_users
from app.models import User

router = APIRouter(prefix="/users", tags=["users"])

@router.post("", response_model=User, status_code=201)
def create_user(user: User):
    user.id = str(uuid4())
    users = load_users()
    users.append(user.model_dump())
    save_users(users)
    return user

@router.get("", response_model=List[User])
def list_users():
    return load_users()
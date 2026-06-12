from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_user_service
from app.schemas.common_schema import APIResponse
from app.schemas.user_schema import UserCreate, UserRead
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("", response_model=APIResponse[UserRead], status_code=201)
def create_user(payload: UserCreate, db: Annotated[Session, Depends(get_db)]):
    service: UserService = get_user_service(db)
    user = service.create_user(payload)
    return {"message": "User created successfully.", "data": user}


@router.get("", response_model=APIResponse[list[UserRead]])
def list_users(db: Annotated[Session, Depends(get_db)]):
    service: UserService = get_user_service(db)
    return {"message": "Users retrieved successfully.", "data": service.list_users()}


@router.get("/{user_id}", response_model=APIResponse[UserRead])
def get_user(user_id: int, db: Annotated[Session, Depends(get_db)]):
    service: UserService = get_user_service(db)
    return {"message": "User retrieved successfully.", "data": service.get_user(user_id)}

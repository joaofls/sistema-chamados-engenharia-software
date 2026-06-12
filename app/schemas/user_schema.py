from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.models.enums import UserRole
from app.schemas.common_schema import ORMModel


class UserCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=120)
    email: str
    password: str = Field(..., min_length=6, max_length=128)
    role: UserRole

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        if "@" not in value or value.startswith("@") or value.endswith("@"):
            raise ValueError("Email must contain a valid local part and domain.")
        return value.lower()


class UserRead(ORMModel):
    id: int
    name: str
    email: str
    role: UserRole
    created_at: datetime
    updated_at: datetime

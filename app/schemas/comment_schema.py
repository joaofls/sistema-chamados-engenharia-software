from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common_schema import ORMModel


class CommentCreate(BaseModel):
    user_id: int
    comment: str = Field(..., min_length=1)


class CommentRead(ORMModel):
    id: int
    ticket_id: int
    user_id: int
    comment: str
    created_at: datetime

from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import TicketPriority, TicketStatus
from app.schemas.comment_schema import CommentRead
from app.schemas.common_schema import ORMModel
from app.schemas.status_history_schema import StatusHistoryRead


class TicketCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1)
    priority: TicketPriority
    requester_id: int


class TicketAssign(BaseModel):
    responsible_id: int


class TicketStatusUpdate(BaseModel):
    status: TicketStatus
    changed_by: int


class TicketPriorityUpdate(BaseModel):
    priority: TicketPriority


class TicketRead(ORMModel):
    id: int
    title: str
    description: str
    priority: TicketPriority
    status: TicketStatus
    requester_id: int
    responsible_id: int | None
    created_at: datetime
    updated_at: datetime
    closed_at: datetime | None


class TicketDetail(TicketRead):
    comments: list[CommentRead] = Field(default_factory=list)
    status_history: list[StatusHistoryRead] = Field(default_factory=list)


class TicketFilters(BaseModel):
    status: TicketStatus | None = None
    priority: TicketPriority | None = None
    responsible_id: int | None = None
    requester_id: int | None = None

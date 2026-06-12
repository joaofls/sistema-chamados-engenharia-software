from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_comment_service
from app.schemas.comment_schema import CommentCreate, CommentRead
from app.schemas.common_schema import APIResponse
from app.services.comment_service import CommentService

router = APIRouter(prefix="/tickets", tags=["Comments"])


@router.post("/{ticket_id}/comments", response_model=APIResponse[CommentRead], status_code=201)
def add_comment(ticket_id: int, payload: CommentCreate, db: Annotated[Session, Depends(get_db)]):
    service: CommentService = get_comment_service(db)
    comment = service.add_comment(ticket_id, payload.user_id, payload.comment)
    return {"message": "Comment added successfully.", "data": comment}


@router.get("/{ticket_id}/comments", response_model=APIResponse[list[CommentRead]])
def list_comments(ticket_id: int, db: Annotated[Session, Depends(get_db)]):
    service: CommentService = get_comment_service(db)
    return {"message": "Comments retrieved successfully.", "data": service.list_comments(ticket_id)}

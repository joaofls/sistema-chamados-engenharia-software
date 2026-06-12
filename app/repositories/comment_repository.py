from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.comment import TicketComment


class CommentRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, comment: TicketComment) -> TicketComment:
        self.db.add(comment)
        self.db.commit()
        self.db.refresh(comment)
        return comment

    def list_by_ticket(self, ticket_id: int) -> list[TicketComment]:
        statement = (
            select(TicketComment)
            .where(TicketComment.ticket_id == ticket_id)
            .order_by(TicketComment.created_at.asc())
        )
        return list(self.db.scalars(statement).all())

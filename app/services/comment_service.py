from fastapi import HTTPException, status

from app.models.comment import TicketComment
from app.models.enums import TicketStatus
from app.repositories.comment_repository import CommentRepository
from app.repositories.ticket_repository import TicketRepository
from app.repositories.user_repository import UserRepository


class CommentService:
    def __init__(
        self,
        comment_repository: CommentRepository,
        ticket_repository: TicketRepository,
        user_repository: UserRepository,
    ) -> None:
        self.comment_repository = comment_repository
        self.ticket_repository = ticket_repository
        self.user_repository = user_repository

    def add_comment(self, ticket_id: int, user_id: int, comment_text: str) -> TicketComment:
        ticket = self.ticket_repository.get_by_id(ticket_id)
        if not ticket:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found.")
        if ticket.status == TicketStatus.CLOSED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Closed tickets do not accept comments unless they are reopened.",
            )
        if not self.user_repository.get_by_id(user_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

        return self.comment_repository.create(
            TicketComment(ticket_id=ticket_id, user_id=user_id, comment=comment_text)
        )

    def list_comments(self, ticket_id: int) -> list[TicketComment]:
        ticket = self.ticket_repository.get_by_id(ticket_id)
        if not ticket:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found.")
        return self.comment_repository.list_by_ticket(ticket_id)

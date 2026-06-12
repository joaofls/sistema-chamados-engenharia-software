from sqlalchemy.orm import Session

from app.repositories.comment_repository import CommentRepository
from app.repositories.ticket_repository import TicketRepository
from app.repositories.user_repository import UserRepository
from app.services.comment_service import CommentService
from app.services.ticket_service import TicketService
from app.services.user_service import UserService


def get_user_service(db: Session) -> UserService:
    return UserService(UserRepository(db))


def get_ticket_service(db: Session) -> TicketService:
    return TicketService(TicketRepository(db), UserRepository(db))


def get_comment_service(db: Session) -> CommentService:
    return CommentService(CommentRepository(db), TicketRepository(db), UserRepository(db))

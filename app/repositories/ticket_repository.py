from sqlalchemy import case, func, select
from sqlalchemy.orm import Session, joinedload

from app.models.enums import TicketPriority
from app.models.status_history import TicketStatusHistory
from app.models.ticket import Ticket
from app.models.user import User


class TicketRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, ticket: Ticket) -> Ticket:
        self.db.add(ticket)
        self.db.commit()
        self.db.refresh(ticket)
        return ticket

    def get_by_id(self, ticket_id: int, with_details: bool = False) -> Ticket | None:
        statement = select(Ticket).where(Ticket.id == ticket_id)
        if with_details:
            statement = statement.options(
                joinedload(Ticket.comments),
                joinedload(Ticket.status_history),
            )
            return self.db.execute(statement).unique().scalar_one_or_none()
        return self.db.scalar(statement)

    def list_all(
        self,
        status: str | None = None,
        priority: str | None = None,
        responsible_id: int | None = None,
        requester_id: int | None = None,
    ) -> list[Ticket]:
        priority_order = case(
            (Ticket.priority == TicketPriority.CRITICAL, 0),
            (Ticket.priority == TicketPriority.HIGH, 1),
            (Ticket.priority == TicketPriority.MEDIUM, 2),
            else_=3,
        )

        statement = select(Ticket).order_by(priority_order, Ticket.created_at.desc())
        if status:
            statement = statement.where(Ticket.status == status)
        if priority:
            statement = statement.where(Ticket.priority == priority)
        if responsible_id is not None:
            statement = statement.where(Ticket.responsible_id == responsible_id)
        if requester_id is not None:
            statement = statement.where(Ticket.requester_id == requester_id)

        return list(self.db.scalars(statement).all())

    def update(self, ticket: Ticket) -> Ticket:
        self.db.add(ticket)
        self.db.commit()
        self.db.refresh(ticket)
        return ticket

    def delete(self, ticket: Ticket) -> None:
        self.db.delete(ticket)
        self.db.commit()

    def add_status_history(self, history: TicketStatusHistory) -> TicketStatusHistory:
        self.db.add(history)
        self.db.commit()
        self.db.refresh(history)
        return history

    def report_by_status(self) -> list[tuple[str, int]]:
        statement = select(Ticket.status, func.count(Ticket.id)).group_by(Ticket.status).order_by(Ticket.status)
        return [(row[0].value, row[1]) for row in self.db.execute(statement).all()]

    def report_by_priority(self) -> list[tuple[str, int]]:
        statement = (
            select(Ticket.priority, func.count(Ticket.id))
            .group_by(Ticket.priority)
            .order_by(Ticket.priority)
        )
        return [(row[0].value, row[1]) for row in self.db.execute(statement).all()]

    def report_by_responsible(self) -> list[tuple[str, int]]:
        statement = (
            select(func.coalesce(User.name, "unassigned"), func.count(Ticket.id))
            .select_from(Ticket)
            .join(User, Ticket.responsible_id == User.id, isouter=True)
            .group_by(User.name)
            .order_by(User.name)
        )
        return [(str(row[0]), row[1]) for row in self.db.execute(statement).all()]

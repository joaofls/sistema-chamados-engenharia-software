from datetime import datetime, timezone

from fastapi import HTTPException, status

from app.models.enums import TicketPriority, TicketStatus, UserRole
from app.models.status_history import TicketStatusHistory
from app.models.ticket import Ticket
from app.repositories.ticket_repository import TicketRepository
from app.repositories.user_repository import UserRepository
from app.schemas.report_schema import ReportEntry
from app.schemas.ticket_schema import TicketCreate


class TicketService:
    def __init__(self, ticket_repository: TicketRepository, user_repository: UserRepository) -> None:
        self.ticket_repository = ticket_repository
        self.user_repository = user_repository

    def create_ticket(self, payload: TicketCreate) -> Ticket:
        requester = self.user_repository.get_by_id(payload.requester_id)
        if not requester:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Requester not found.")

        ticket = Ticket(
            title=payload.title,
            description=payload.description,
            priority=payload.priority,
            status=TicketStatus.OPEN,
            requester_id=payload.requester_id,
        )
        return self.ticket_repository.create(ticket)

    def list_tickets(
        self,
        status_filter: TicketStatus | None,
        priority_filter: TicketPriority | None,
        responsible_id: int | None,
        requester_id: int | None,
    ) -> list[Ticket]:
        return self.ticket_repository.list_all(
            status=status_filter.value if status_filter else None,
            priority=priority_filter.value if priority_filter else None,
            responsible_id=responsible_id,
            requester_id=requester_id,
        )

    def get_ticket(self, ticket_id: int, with_details: bool = False) -> Ticket:
        ticket = self.ticket_repository.get_by_id(ticket_id, with_details=with_details)
        if not ticket:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found.")
        return ticket

    def assign_ticket(self, ticket_id: int, responsible_id: int) -> Ticket:
        ticket = self.get_ticket(ticket_id)
        responsible = self.user_repository.get_by_id(responsible_id)
        if not responsible:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Responsible user not found.")
        if responsible.role not in {UserRole.SUPPORT_AGENT, UserRole.ADMIN}:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only support agents or admins can be assigned to tickets.",
            )

        ticket.responsible_id = responsible_id
        return self.ticket_repository.update(ticket)

    def update_ticket_status(self, ticket_id: int, new_status: TicketStatus, changed_by: int) -> Ticket:
        ticket = self.get_ticket(ticket_id)
        author = self.user_repository.get_by_id(changed_by)
        if not author:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User changing status not found.")
        if ticket.status == new_status:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ticket already has this status.")

        old_status = ticket.status
        ticket.status = new_status
        if new_status == TicketStatus.CLOSED:
            ticket.closed_at = datetime.now(timezone.utc)
        elif old_status == TicketStatus.CLOSED and new_status != TicketStatus.CLOSED:
            ticket.closed_at = None

        updated_ticket = self.ticket_repository.update(ticket)
        self.ticket_repository.add_status_history(
            TicketStatusHistory(
                ticket_id=ticket.id,
                old_status=old_status,
                new_status=new_status,
                changed_by=changed_by,
            )
        )
        return updated_ticket

    def update_ticket_priority(self, ticket_id: int, new_priority: TicketPriority) -> Ticket:
        ticket = self.get_ticket(ticket_id)
        ticket.priority = new_priority
        return self.ticket_repository.update(ticket)

    def delete_ticket(self, ticket_id: int) -> None:
        ticket = self.get_ticket(ticket_id)
        self.ticket_repository.delete(ticket)

    def tickets_by_status(self) -> list[ReportEntry]:
        return [ReportEntry(label=label, total=total) for label, total in self.ticket_repository.report_by_status()]

    def tickets_by_priority(self) -> list[ReportEntry]:
        return [ReportEntry(label=label, total=total) for label, total in self.ticket_repository.report_by_priority()]

    def tickets_by_responsible(self) -> list[ReportEntry]:
        return [ReportEntry(label=label, total=total) for label, total in self.ticket_repository.report_by_responsible()]

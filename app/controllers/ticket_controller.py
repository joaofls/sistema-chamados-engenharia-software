from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_ticket_service
from app.models.enums import TicketPriority, TicketStatus
from app.schemas.common_schema import APIResponse
from app.schemas.report_schema import ReportEntry
from app.schemas.ticket_schema import (
    TicketAssign,
    TicketCreate,
    TicketDetail,
    TicketPriorityUpdate,
    TicketRead,
    TicketStatusUpdate,
)
from app.services.ticket_service import TicketService

router = APIRouter(prefix="/tickets", tags=["Tickets"])
reports_router = APIRouter(prefix="/reports", tags=["Reports"])


@router.post("", response_model=APIResponse[TicketRead], status_code=201)
def create_ticket(payload: TicketCreate, db: Annotated[Session, Depends(get_db)]):
    service: TicketService = get_ticket_service(db)
    return {"message": "Ticket created successfully.", "data": service.create_ticket(payload)}


@router.get("", response_model=APIResponse[list[TicketRead]])
def list_tickets(
    db: Annotated[Session, Depends(get_db)],
    status_filter: Annotated[TicketStatus | None, Query(alias="status")] = None,
    priority_filter: Annotated[TicketPriority | None, Query(alias="priority")] = None,
    responsible_id: int | None = None,
    requester_id: int | None = None,
):
    service: TicketService = get_ticket_service(db)
    tickets = service.list_tickets(status_filter, priority_filter, responsible_id, requester_id)
    return {"message": "Tickets retrieved successfully.", "data": tickets}


@router.get("/{ticket_id}", response_model=APIResponse[TicketDetail])
def get_ticket(ticket_id: int, db: Annotated[Session, Depends(get_db)]):
    service: TicketService = get_ticket_service(db)
    return {"message": "Ticket retrieved successfully.", "data": service.get_ticket(ticket_id, with_details=True)}


@router.put("/{ticket_id}/assign", response_model=APIResponse[TicketRead])
def assign_ticket(ticket_id: int, payload: TicketAssign, db: Annotated[Session, Depends(get_db)]):
    service: TicketService = get_ticket_service(db)
    return {
        "message": "Ticket assigned successfully.",
        "data": service.assign_ticket(ticket_id, payload.responsible_id),
    }


@router.put("/{ticket_id}/status", response_model=APIResponse[TicketRead])
def update_ticket_status(
    ticket_id: int,
    payload: TicketStatusUpdate,
    db: Annotated[Session, Depends(get_db)],
):
    service: TicketService = get_ticket_service(db)
    return {
        "message": "Ticket status updated successfully.",
        "data": service.update_ticket_status(ticket_id, payload.status, payload.changed_by),
    }


@router.put("/{ticket_id}/priority", response_model=APIResponse[TicketRead])
def update_ticket_priority(
    ticket_id: int,
    payload: TicketPriorityUpdate,
    db: Annotated[Session, Depends(get_db)],
):
    service: TicketService = get_ticket_service(db)
    return {
        "message": "Ticket priority updated successfully.",
        "data": service.update_ticket_priority(ticket_id, payload.priority),
    }


@router.delete("/{ticket_id}", status_code=204)
def delete_ticket(ticket_id: int, db: Annotated[Session, Depends(get_db)]):
    service: TicketService = get_ticket_service(db)
    service.delete_ticket(ticket_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@reports_router.get("/tickets-by-status", response_model=APIResponse[list[ReportEntry]])
def tickets_by_status(db: Annotated[Session, Depends(get_db)]):
    service: TicketService = get_ticket_service(db)
    return {"message": "Report generated successfully.", "data": service.tickets_by_status()}


@reports_router.get("/tickets-by-priority", response_model=APIResponse[list[ReportEntry]])
def tickets_by_priority(db: Annotated[Session, Depends(get_db)]):
    service: TicketService = get_ticket_service(db)
    return {"message": "Report generated successfully.", "data": service.tickets_by_priority()}


@reports_router.get("/tickets-by-responsible", response_model=APIResponse[list[ReportEntry]])
def tickets_by_responsible(db: Annotated[Session, Depends(get_db)]):
    service: TicketService = get_ticket_service(db)
    return {"message": "Report generated successfully.", "data": service.tickets_by_responsible()}

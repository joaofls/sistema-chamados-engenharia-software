from datetime import datetime

from app.models.enums import TicketStatus
from app.schemas.common_schema import ORMModel


class StatusHistoryRead(ORMModel):
    id: int
    ticket_id: int
    old_status: TicketStatus
    new_status: TicketStatus
    changed_by: int
    created_at: datetime

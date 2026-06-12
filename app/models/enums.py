from enum import Enum


class UserRole(str, Enum):
    REQUESTER = "requester"
    SUPPORT_AGENT = "support_agent"
    ADMIN = "admin"


class TicketPriority(str, Enum):
    LOW = "baixa"
    MEDIUM = "media"
    HIGH = "alta"
    CRITICAL = "critica"


class TicketStatus(str, Enum):
    OPEN = "aberto"
    IN_PROGRESS = "em_andamento"
    WAITING_FOR_USER = "aguardando_usuario"
    RESOLVED = "resolvido"
    CLOSED = "fechado"

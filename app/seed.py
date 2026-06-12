from sqlalchemy import select

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models import Ticket, TicketComment, TicketStatusHistory, User
from app.models.enums import TicketPriority, TicketStatus, UserRole


def run_seed() -> None:
    db = SessionLocal()
    try:
        existing_admin = db.scalar(select(User).where(User.email == "admin@empresa.local"))
        if existing_admin:
            return

        admin = User(
            name="Administrador",
            email="admin@empresa.local",
            password_hash=hash_password("admin123"),
            role=UserRole.ADMIN,
        )
        requester = User(
            name="Solicitante Padrao",
            email="solicitante@empresa.local",
            password_hash=hash_password("request123"),
            role=UserRole.REQUESTER,
        )
        agent = User(
            name="Analista de Suporte",
            email="suporte@empresa.local",
            password_hash=hash_password("support123"),
            role=UserRole.SUPPORT_AGENT,
        )
        db.add_all([admin, requester, agent])
        db.flush()

        ticket_1 = Ticket(
            title="Falha no acesso ao ERP",
            description="Usuario nao consegue autenticar no ERP corporativo.",
            priority=TicketPriority.CRITICAL,
            status=TicketStatus.IN_PROGRESS,
            requester_id=requester.id,
            responsible_id=agent.id,
        )
        ticket_2 = Ticket(
            title="Solicitacao de instalacao de impressora",
            description="Necessidade de mapear impressora no setor financeiro.",
            priority=TicketPriority.MEDIUM,
            status=TicketStatus.OPEN,
            requester_id=requester.id,
        )
        db.add_all([ticket_1, ticket_2])
        db.flush()

        db.add(
            TicketComment(
                ticket_id=ticket_1.id,
                user_id=agent.id,
                comment="Chamado em atendimento. Validando logs de autenticacao.",
            )
        )
        db.add(
            TicketStatusHistory(
                ticket_id=ticket_1.id,
                old_status=TicketStatus.OPEN,
                new_status=TicketStatus.IN_PROGRESS,
                changed_by=agent.id,
            )
        )
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()

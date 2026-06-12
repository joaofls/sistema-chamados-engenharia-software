"""initial schema

Revision ID: 20260519_01
Revises:
Create Date: 2026-05-19 13:20:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260519_01"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


user_role = sa.Enum("requester", "support_agent", "admin", name="user_role", native_enum=False)
ticket_priority = sa.Enum("baixa", "media", "alta", "critica", name="ticket_priority", native_enum=False)
ticket_status = sa.Enum(
    "aberto",
    "em_andamento",
    "aguardando_usuario",
    "resolvido",
    "fechado",
    name="ticket_status",
    native_enum=False,
)


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", user_role, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=False)

    op.create_table(
        "tickets",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("priority", ticket_priority, nullable=False),
        sa.Column("status", ticket_status, nullable=False),
        sa.Column("requester_id", sa.Integer(), nullable=False),
        sa.Column("responsible_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["requester_id"], ["users.id"], name="fk_tickets_requester_id_users"),
        sa.ForeignKeyConstraint(["responsible_id"], ["users.id"], name="fk_tickets_responsible_id_users"),
    )
    op.create_index("ix_tickets_title", "tickets", ["title"], unique=False)
    op.create_index("ix_tickets_priority", "tickets", ["priority"], unique=False)
    op.create_index("ix_tickets_status", "tickets", ["status"], unique=False)
    op.create_index("ix_tickets_requester_id", "tickets", ["requester_id"], unique=False)
    op.create_index("ix_tickets_responsible_id", "tickets", ["responsible_id"], unique=False)

    op.create_table(
        "ticket_comments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("ticket_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("comment", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["ticket_id"], ["tickets.id"], name="fk_ticket_comments_ticket_id_tickets"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_ticket_comments_user_id_users"),
    )
    op.create_index("ix_ticket_comments_ticket_id", "ticket_comments", ["ticket_id"], unique=False)
    op.create_index("ix_ticket_comments_user_id", "ticket_comments", ["user_id"], unique=False)

    op.create_table(
        "ticket_status_history",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("ticket_id", sa.Integer(), nullable=False),
        sa.Column("old_status", ticket_status, nullable=False),
        sa.Column("new_status", ticket_status, nullable=False),
        sa.Column("changed_by", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["ticket_id"], ["tickets.id"], name="fk_ticket_status_history_ticket_id_tickets"),
        sa.ForeignKeyConstraint(["changed_by"], ["users.id"], name="fk_ticket_status_history_changed_by_users"),
    )
    op.create_index("ix_ticket_status_history_ticket_id", "ticket_status_history", ["ticket_id"], unique=False)
    op.create_index("ix_ticket_status_history_changed_by", "ticket_status_history", ["changed_by"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_ticket_status_history_changed_by", table_name="ticket_status_history")
    op.drop_index("ix_ticket_status_history_ticket_id", table_name="ticket_status_history")
    op.drop_table("ticket_status_history")
    op.drop_index("ix_ticket_comments_user_id", table_name="ticket_comments")
    op.drop_index("ix_ticket_comments_ticket_id", table_name="ticket_comments")
    op.drop_table("ticket_comments")
    op.drop_index("ix_tickets_responsible_id", table_name="tickets")
    op.drop_index("ix_tickets_requester_id", table_name="tickets")
    op.drop_index("ix_tickets_status", table_name="tickets")
    op.drop_index("ix_tickets_priority", table_name="tickets")
    op.drop_index("ix_tickets_title", table_name="tickets")
    op.drop_table("tickets")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")

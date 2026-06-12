from collections import Counter
from pathlib import Path
from typing import Annotated
from urllib.parse import quote_plus

from fastapi import APIRouter, Depends, Form, HTTPException, Query, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import hash_password
from app.dependencies import get_comment_service, get_ticket_service, get_user_service
from app.models.enums import TicketPriority, TicketStatus, UserRole
from app.models.user import User
from app.schemas.ticket_schema import TicketCreate
from app.schemas.user_schema import UserCreate

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

router = APIRouter(include_in_schema=False)


def _to_filter_enum(enum_class, raw_value: str | None):
    if not raw_value:
        return None
    return enum_class(raw_value)


def _redirect(path: str) -> RedirectResponse:
    return RedirectResponse(url=path, status_code=303)


def _redirect_error(path: str, detail: str) -> RedirectResponse:
    separator = "&" if "?" in path else "?"
    return _redirect(f"{path}{separator}error={quote_plus(detail)}")


def _redirect_message(path: str, detail: str) -> RedirectResponse:
    separator = "&" if "?" in path else "?"
    return _redirect(f"{path}{separator}message={quote_plus(detail)}")


def _session_user_id(request: Request) -> int | None:
    user_id = request.session.get("user_id")
    return int(user_id) if user_id else None


def _get_logged_user(request: Request, db: Session) -> User | None:
    user_id = _session_user_id(request)
    if not user_id:
        return None
    return get_user_service(db).get_user(user_id)


def _is_support(user: User) -> bool:
    return user.role in {UserRole.SUPPORT_AGENT, UserRole.ADMIN}


def _login_redirect(request: Request, message: str | None = None, error: str | None = None) -> RedirectResponse:
    next_url = request.url.path
    if request.url.query:
        next_url = f"{next_url}?{request.url.query}"
    path = f"/login?next={quote_plus(next_url)}"
    if message:
        path += f"&message={quote_plus(message)}"
    if error:
        path += f"&error={quote_plus(error)}"
    return _redirect(path)


def _redirect_after_login(user: User, next_url: str | None = None) -> RedirectResponse:
    if next_url and next_url.startswith("/") and not next_url.startswith("//"):
        if user.role == UserRole.REQUESTER and next_url.startswith("/admin"):
            return _redirect("/portal")
        if _is_support(user) and next_url.startswith("/portal"):
            return _redirect("/admin")
        return _redirect(next_url)
    if user.role == UserRole.REQUESTER:
        return _redirect("/portal")
    return _redirect("/admin")


def _load_dashboard_data(db: Session, filters: dict[str, str | None]):
    user_service = get_user_service(db)
    ticket_service = get_ticket_service(db)

    users = user_service.list_users()
    tickets = ticket_service.list_tickets(
        _to_filter_enum(TicketStatus, filters["status"]),
        _to_filter_enum(TicketPriority, filters["priority"]),
        int(filters["responsible_id"]) if filters["responsible_id"] else None,
        int(filters["requester_id"]) if filters["requester_id"] else None,
    )

    status_counts = Counter(ticket.status.value for ticket in tickets)
    priority_counts = Counter(ticket.priority.value for ticket in tickets)
    support_users = [user for user in users if user.role in {UserRole.SUPPORT_AGENT, UserRole.ADMIN}]
    requester_users = [user for user in users if user.role == UserRole.REQUESTER]

    return {
        "users": users,
        "tickets": tickets,
        "support_users": support_users,
        "requester_users": requester_users,
        "stats": {
            "total_tickets": len(tickets),
            "open_tickets": status_counts.get(TicketStatus.OPEN.value, 0),
            "in_progress_tickets": status_counts.get(TicketStatus.IN_PROGRESS.value, 0),
            "closed_tickets": status_counts.get(TicketStatus.CLOSED.value, 0),
            "critical_tickets": priority_counts.get(TicketPriority.CRITICAL.value, 0),
        },
    }


def _empty_dashboard_data():
    return {
        "users": [],
        "tickets": [],
        "support_users": [],
        "requester_users": [],
        "stats": {
            "total_tickets": 0,
            "open_tickets": 0,
            "in_progress_tickets": 0,
            "closed_tickets": 0,
            "critical_tickets": 0,
        },
    }


@router.get("/", response_class=HTMLResponse)
def home(request: Request, db: Annotated[Session, Depends(get_db)]):
    current_user = _get_logged_user(request, db)
    if not current_user:
        return _redirect("/login")
    return _redirect_after_login(current_user)


@router.get("/login", response_class=HTMLResponse)
def login_page(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    next: str | None = None,
    message: str | None = None,
    error: str | None = None,
):
    current_user = _get_logged_user(request, db)
    if current_user:
        return _redirect_after_login(current_user, next)
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={
            "request": request,
            "page_title": "Login",
            "message": message,
            "error": error,
            "next": next or "",
            "current_user": None,
        },
    )


@router.post("/login")
def login_action(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    email: Annotated[str, Form()],
    password: Annotated[str, Form()],
    next: Annotated[str | None, Form()] = None,
):
    user = get_user_service(db).repository.get_by_email(email.strip().lower())
    if not user or user.password_hash != hash_password(password):
        return _redirect_error("/login", "E-mail ou senha invalidos.")
    request.session["user_id"] = user.id
    request.session["user_name"] = user.name
    request.session["user_role"] = user.role.value
    return _redirect_after_login(user, next)


@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return _redirect_message("/login", "Voce saiu do sistema.")


@router.get("/admin", response_class=HTMLResponse)
def admin_dashboard(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    status_filter: Annotated[str | None, Query(alias="status")] = None,
    priority_filter: Annotated[str | None, Query(alias="priority")] = None,
    responsible_id: int | None = None,
    requester_id: int | None = None,
    message: str | None = None,
    error: str | None = None,
):
    current_user = _get_logged_user(request, db)
    if not current_user:
        return _login_redirect(request)
    if not _is_support(current_user):
        return _redirect_error("/portal", "Seu perfil nao permite acessar o painel do suporte.")

    filters = {
        "status": status_filter,
        "priority": priority_filter,
        "responsible_id": str(responsible_id) if responsible_id else None,
        "requester_id": str(requester_id) if requester_id else None,
    }
    error_message = error
    try:
        context = _load_dashboard_data(db, filters)
    except SQLAlchemyError:
        context = _empty_dashboard_data()
        error_message = error_message or "Nao foi possivel carregar os dados. Verifique a conexao com o PostgreSQL."
    context.update(
        {
            "request": request,
            "page_title": "Painel do Suporte",
            "message": message,
            "error": error_message,
            "filters": filters,
            "roles": list(UserRole),
            "statuses": list(TicketStatus),
            "priorities": list(TicketPriority),
            "current_user": current_user,
        }
    )
    return templates.TemplateResponse(request=request, name="dashboard.html", context=context)


@router.get("/portal", response_class=HTMLResponse)
def requester_portal(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    message: str | None = None,
    error: str | None = None,
):
    current_user = _get_logged_user(request, db)
    if not current_user:
        return _login_redirect(request)
    if current_user.role != UserRole.REQUESTER:
        return _redirect_error("/admin", "O portal do solicitante e exclusivo para usuarios solicitantes.")

    ticket_service = get_ticket_service(db)
    error_message = error
    try:
        tickets = ticket_service.list_tickets(None, None, None, current_user.id)
    except SQLAlchemyError:
        tickets = []
        error_message = error_message or "Nao foi possivel carregar o portal. Verifique a conexao com o PostgreSQL."

    status_counts = Counter(ticket.status.value for ticket in tickets)

    return templates.TemplateResponse(
        request=request,
        name="portal.html",
        context={
            "request": request,
            "page_title": "Portal do Solicitante",
            "message": message,
            "error": error_message,
            "selected_requester": current_user,
            "current_user": current_user,
            "tickets": tickets,
            "priorities": list(TicketPriority),
            "stats": {
                "total_tickets": len(tickets),
                "open_tickets": status_counts.get(TicketStatus.OPEN.value, 0),
                "in_progress_tickets": status_counts.get(TicketStatus.IN_PROGRESS.value, 0),
                "closed_tickets": status_counts.get(TicketStatus.CLOSED.value, 0),
            },
        },
    )


@router.get("/tickets/{ticket_id}/view", response_class=HTMLResponse)
def ticket_detail_page(
    ticket_id: int,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    message: str | None = None,
    error: str | None = None,
):
    current_user = _get_logged_user(request, db)
    if not current_user:
        return _login_redirect(request)
    if not _is_support(current_user):
        return _redirect_error("/portal", "Seu perfil nao permite acessar esta tela.")

    user_service = get_user_service(db)
    ticket_service = get_ticket_service(db)
    comment_service = get_comment_service(db)
    try:
        users = user_service.list_users()
        support_users = [user for user in users if user.role in {UserRole.SUPPORT_AGENT, UserRole.ADMIN}]
        ticket = ticket_service.get_ticket(ticket_id, with_details=True)
        comments = comment_service.list_comments(ticket_id)
    except SQLAlchemyError:
        return _redirect_error("/admin", "Nao foi possivel carregar o chamado. Verifique a conexao com o PostgreSQL.")

    return templates.TemplateResponse(
        request=request,
        name="ticket_detail.html",
        context={
            "request": request,
            "page_title": f"Chamado #{ticket.id}",
            "ticket": ticket,
            "comments": comments,
            "users": users,
            "support_users": support_users,
            "statuses": list(TicketStatus),
            "priorities": list(TicketPriority),
            "message": message,
            "error": error,
            "current_user": current_user,
        },
    )


@router.get("/portal/tickets/{ticket_id}/view", response_class=HTMLResponse)
def portal_ticket_detail_page(
    ticket_id: int,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    message: str | None = None,
    error: str | None = None,
):
    current_user = _get_logged_user(request, db)
    if not current_user:
        return _login_redirect(request)
    if current_user.role != UserRole.REQUESTER:
        return _redirect_error("/admin", "O portal do solicitante e exclusivo para usuarios solicitantes.")

    ticket_service = get_ticket_service(db)
    comment_service = get_comment_service(db)
    try:
        ticket = ticket_service.get_ticket(ticket_id, with_details=True)
        if ticket.requester_id != current_user.id:
            return _redirect_error("/portal", "Voce nao tem permissao para visualizar este chamado.")
        comments = comment_service.list_comments(ticket_id)
    except SQLAlchemyError:
        return _redirect_error("/portal", "Nao foi possivel carregar o chamado. Verifique a conexao com o PostgreSQL.")

    return templates.TemplateResponse(
        request=request,
        name="portal_ticket_detail.html",
        context={
            "request": request,
            "page_title": f"Meu chamado #{ticket.id}",
            "ticket": ticket,
            "comments": comments,
            "selected_requester": current_user,
            "current_user": current_user,
            "message": message,
            "error": error,
        },
    )


@router.post("/web/users")
def create_user_form(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    name: Annotated[str, Form()],
    email: Annotated[str, Form()],
    password: Annotated[str, Form()],
    role: Annotated[UserRole, Form()],
):
    current_user = _get_logged_user(request, db)
    if not current_user or current_user.role != UserRole.ADMIN:
        return _redirect_error("/admin", "Apenas administrador pode cadastrar usuarios.")

    service = get_user_service(db)
    try:
        service.create_user(UserCreate(name=name, email=email, password=password, role=role))
        return _redirect_message("/admin", "Usuario criado com sucesso.")
    except HTTPException as exc:
        return _redirect_error("/admin", str(exc.detail))
    except ValidationError as exc:
        first_error = exc.errors()[0]["msg"] if exc.errors() else "Dados invalidos."
        return _redirect_error("/admin", first_error)


@router.post("/web/tickets")
def create_ticket_form(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    title: Annotated[str, Form()],
    description: Annotated[str, Form()],
    priority: Annotated[TicketPriority, Form()],
    requester_id: Annotated[int, Form()],
):
    current_user = _get_logged_user(request, db)
    if not current_user or not _is_support(current_user):
        return _redirect_error("/login", "Faca login com perfil de suporte.")

    service = get_ticket_service(db)
    try:
        service.create_ticket(TicketCreate(title=title, description=description, priority=priority, requester_id=requester_id))
        return _redirect_message("/admin", "Chamado aberto em nome do solicitante.")
    except HTTPException as exc:
        return _redirect_error("/admin", str(exc.detail))
    except ValidationError as exc:
        first_error = exc.errors()[0]["msg"] if exc.errors() else "Dados invalidos."
        return _redirect_error("/admin", first_error)


@router.post("/portal/tickets")
def create_portal_ticket_form(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    title: Annotated[str, Form()],
    description: Annotated[str, Form()],
    priority: Annotated[TicketPriority, Form()],
):
    current_user = _get_logged_user(request, db)
    if not current_user:
        return _redirect_error("/login", "Faca login para abrir um chamado.")
    if current_user.role != UserRole.REQUESTER:
        return _redirect_error("/admin", "Apenas solicitantes abrem chamados pelo portal.")

    service = get_ticket_service(db)
    try:
        service.create_ticket(TicketCreate(title=title, description=description, priority=priority, requester_id=current_user.id))
        return _redirect_message("/portal", "Chamado aberto com sucesso.")
    except HTTPException as exc:
        return _redirect_error("/portal", str(exc.detail))
    except ValidationError as exc:
        first_error = exc.errors()[0]["msg"] if exc.errors() else "Dados invalidos."
        return _redirect_error("/portal", first_error)


@router.post("/web/tickets/{ticket_id}/assign")
def assign_ticket_form(
    ticket_id: int,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    responsible_id: Annotated[int, Form()],
):
    current_user = _get_logged_user(request, db)
    if not current_user or not _is_support(current_user):
        return _redirect_error("/login", "Faca login com perfil de suporte.")

    service = get_ticket_service(db)
    try:
        service.assign_ticket(ticket_id, responsible_id)
        return _redirect_message(f"/tickets/{ticket_id}/view", "Responsavel atualizado.")
    except HTTPException as exc:
        return _redirect_error(f"/tickets/{ticket_id}/view", str(exc.detail))


@router.post("/web/tickets/{ticket_id}/status")
def update_status_form(
    ticket_id: int,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    status: Annotated[TicketStatus, Form()],
    changed_by: Annotated[int, Form()],
):
    current_user = _get_logged_user(request, db)
    if not current_user or not _is_support(current_user):
        return _redirect_error("/login", "Faca login com perfil de suporte.")

    service = get_ticket_service(db)
    try:
        service.update_ticket_status(ticket_id, status, changed_by)
        return _redirect_message(f"/tickets/{ticket_id}/view", "Status atualizado.")
    except HTTPException as exc:
        return _redirect_error(f"/tickets/{ticket_id}/view", str(exc.detail))


@router.post("/web/tickets/{ticket_id}/priority")
def update_priority_form(
    ticket_id: int,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    priority: Annotated[TicketPriority, Form()],
):
    current_user = _get_logged_user(request, db)
    if not current_user or not _is_support(current_user):
        return _redirect_error("/login", "Faca login com perfil de suporte.")

    service = get_ticket_service(db)
    try:
        service.update_ticket_priority(ticket_id, priority)
        return _redirect_message(f"/tickets/{ticket_id}/view", "Prioridade atualizada.")
    except HTTPException as exc:
        return _redirect_error(f"/tickets/{ticket_id}/view", str(exc.detail))


@router.post("/web/tickets/{ticket_id}/comments")
def add_comment_form(
    ticket_id: int,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    user_id: Annotated[int, Form()],
    comment: Annotated[str, Form()],
):
    current_user = _get_logged_user(request, db)
    if not current_user or not _is_support(current_user):
        return _redirect_error("/login", "Faca login com perfil de suporte.")

    service = get_comment_service(db)
    try:
        service.add_comment(ticket_id, user_id, comment)
        return _redirect_message(f"/tickets/{ticket_id}/view", "Comentario adicionado.")
    except HTTPException as exc:
        return _redirect_error(f"/tickets/{ticket_id}/view", str(exc.detail))


@router.post("/portal/tickets/{ticket_id}/comments")
def add_portal_comment_form(
    ticket_id: int,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    comment: Annotated[str, Form()],
):
    current_user = _get_logged_user(request, db)
    if not current_user:
        return _redirect_error("/login", "Faca login para comentar.")
    if current_user.role != UserRole.REQUESTER:
        return _redirect_error("/admin", "Apenas solicitantes comentam pelo portal.")

    service = get_comment_service(db)
    ticket_service = get_ticket_service(db)
    portal_ticket_path = f"/portal/tickets/{ticket_id}/view"

    try:
        ticket = ticket_service.get_ticket(ticket_id)
        if ticket.requester_id != current_user.id:
            return _redirect_error("/portal", "Voce nao tem permissao para comentar neste chamado.")
        service.add_comment(ticket_id, current_user.id, comment)
        return _redirect_message(portal_ticket_path, "Comentario adicionado.")
    except HTTPException as exc:
        return _redirect_error(portal_ticket_path, str(exc.detail))

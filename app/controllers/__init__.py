from app.controllers.comment_controller import router as comment_router
from app.controllers.ticket_controller import reports_router, router as ticket_router
from app.controllers.user_controller import router as user_router
from app.controllers.web_controller import router as web_router

__all__ = ["user_router", "ticket_router", "comment_router", "reports_router", "web_router"]

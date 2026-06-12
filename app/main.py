import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.controllers import comment_router, reports_router, ticket_router, user_router, web_router
from app.core.config import get_settings

settings = get_settings()
BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title=settings.app_name,
    description="API REST para gerenciamento de chamados de suporte interno.",
    version="1.0.0",
)

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET", "dev-secret-change-me"),
    same_site="lax",
    https_only=False,
)

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

app.include_router(web_router)
app.include_router(user_router)
app.include_router(ticket_router)
app.include_router(comment_router)
app.include_router(reports_router)

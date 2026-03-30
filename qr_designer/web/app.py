"""FastAPI application factory."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

WEB_DIR = Path(__file__).resolve().parent
STATIC_DIR = WEB_DIR / "static"
TEMPLATE_DIR = WEB_DIR / "templates"


def create_app() -> FastAPI:
    app = FastAPI(
        title="QR Designer",
        description="Customizable QR code designer and print layout generator",
        version="1.0.0",
    )

    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    templates = Jinja2Templates(directory=str(TEMPLATE_DIR))
    app.state.templates = templates

    from .routes.api import router as api_router
    from .routes.designer import router as designer_router
    from .routes.layout import router as layout_router

    app.include_router(designer_router)
    app.include_router(layout_router)
    app.include_router(api_router, prefix="/api")

    return app

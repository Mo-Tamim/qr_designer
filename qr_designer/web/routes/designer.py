"""Designer page routes."""

from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def designer_page(request: Request):
    templates = request.app.state.templates
    return templates.TemplateResponse(request, "designer.html")

"""REST API routes for QR generation, export, and layout."""

from __future__ import annotations

import base64
import io
import os
import uuid

from fastapi import APIRouter, File, UploadFile
from fastapi.responses import JSONResponse, StreamingResponse

from ...core.encoder import encode_content
from ...core.generator import generate_matrix
from ...core.matrix_analyzer import classify_matrix
from ...export.exporter import export_pdf_bytes, export_png_bytes, export_svg_bytes
from ...layout.pdf_generator import generate_grid_pdf
from ...logo.embedder import embed_logo
from ...renderer.pillow_renderer import PillowRenderer
from ...renderer.svg_renderer import SVGRenderer
from ...styles.config import QRStyleConfig
from ...styles.presets import PRESETS
from ..models import (
    ExportRequest,
    LayoutExportRequest,
    LayoutPreviewRequest,
    PreviewRequest,
    PresetListItem,
)

router = APIRouter()

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

pillow_renderer = PillowRenderer()
svg_renderer = SVGRenderer()


def _generate_qr_image(style: QRStyleConfig, size_override: int | None = None):
    data = encode_content(style.content_type, **style.content_data)
    matrix = generate_matrix(data, error_correction=style.error_correction, border=0)
    classified = classify_matrix(matrix)

    if size_override:
        render_style = style.model_copy(update={"size_px": size_override})
    else:
        render_style = style

    img = pillow_renderer.render(matrix, classified, render_style)

    if style.logo and style.logo.image_path and os.path.isfile(style.logo.image_path):
        img = embed_logo(
            img,
            style.logo.image_path,
            size_ratio=style.logo.size_ratio,
            padding=style.logo.padding,
            margin=style.logo.margin,
            frame_shape=style.logo.frame_shape,
            frame_color=style.logo.frame_color,
            logo_shape=style.logo.logo_shape,
            border_width=style.logo.border_width,
            border_color=style.logo.border_color,
            shadow=style.logo.shadow,
            shadow_color=style.logo.shadow_color,
            shadow_offset=style.logo.shadow_offset,
            shadow_blur=style.logo.shadow_blur,
            bg_opacity=style.logo.bg_opacity,
            text=style.logo.text,
            text_color=style.logo.text_color,
            text_font_size=style.logo.text_font_size,
        )

    return img, matrix, classified


def _generate_qr_svg(style: QRStyleConfig) -> str:
    data = encode_content(style.content_type, **style.content_data)
    matrix = generate_matrix(data, error_correction=style.error_correction, border=0)
    classified = classify_matrix(matrix)
    return svg_renderer.render(matrix, classified, style)


@router.post("/preview")
async def preview(req: PreviewRequest):
    img, _, _ = _generate_qr_image(req.style, size_override=req.preview_size)
    png_bytes = export_png_bytes(img, dpi=72)
    b64 = base64.b64encode(png_bytes).decode("ascii")
    return JSONResponse({"image": f"data:image/png;base64,{b64}"})


@router.post("/export")
async def export_qr(req: ExportRequest):
    if req.format == "svg":
        svg_str = _generate_qr_svg(req.style)
        svg_bytes = export_svg_bytes(svg_str)
        return StreamingResponse(
            io.BytesIO(svg_bytes),
            media_type="image/svg+xml",
            headers={"Content-Disposition": "attachment; filename=qr_code.svg"},
        )
    elif req.format == "pdf":
        img, _, _ = _generate_qr_image(req.style)
        pdf_bytes = export_pdf_bytes(
            img, width_mm=req.width_mm, height_mm=req.height_mm, dpi=req.style.dpi
        )
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=qr_code.pdf"},
        )
    else:
        img, _, _ = _generate_qr_image(req.style)
        png_bytes = export_png_bytes(img, dpi=req.style.dpi)
        return StreamingResponse(
            io.BytesIO(png_bytes),
            media_type="image/png",
            headers={"Content-Disposition": "attachment; filename=qr_code.png"},
        )


@router.post("/upload-logo")
async def upload_logo(file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename or "logo.png")[1]
    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    content = await file.read()
    with open(filepath, "wb") as f:
        f.write(content)
    return JSONResponse({"path": filepath, "filename": filename})


@router.get("/presets")
async def list_presets():
    items = [PresetListItem(name=k, label=k.replace("_", " ").title()) for k in PRESETS]
    return items


@router.get("/presets/{name}")
async def get_preset(name: str):
    factory = PRESETS.get(name)
    if factory is None:
        return JSONResponse({"error": "Preset not found"}, status_code=404)
    return factory().model_dump()


@router.post("/layout/preview")
async def layout_preview(req: LayoutPreviewRequest):
    img, _, _ = _generate_qr_image(req.style, size_override=400)
    pdf_bytes = generate_grid_pdf(img, req.grid)
    b64 = base64.b64encode(pdf_bytes).decode("ascii")
    return JSONResponse({"pdf": f"data:application/pdf;base64,{b64}"})


@router.post("/layout/export")
async def layout_export(req: LayoutExportRequest):
    img, _, _ = _generate_qr_image(req.style)
    pdf_bytes = generate_grid_pdf(img, req.grid)
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=qr_grid.pdf"},
    )

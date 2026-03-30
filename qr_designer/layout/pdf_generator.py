"""Generate print-ready PDF grid layouts of QR codes."""

from __future__ import annotations

import io

from PIL import Image
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas as pdf_canvas

from .grid import GridConfig
from .page import get_page_size


def generate_grid_pdf(
    qr_image: Image.Image,
    config: GridConfig,
    output: str | io.BytesIO | None = None,
) -> bytes:
    """Render a PDF with a grid of QR code cells.

    Each cell contains the QR image, optional top text, and optional bottom text.
    Returns the PDF bytes.
    """
    if config.page_width_mm and config.page_height_mm:
        page_w = config.page_width_mm * mm
        page_h = config.page_height_mm * mm
    else:
        ps = get_page_size(config.page_size)
        page_w = ps.width_mm * mm
        page_h = ps.height_mm * mm

    buf = io.BytesIO() if output is None else (output if isinstance(output, io.BytesIO) else None)
    file_path = output if isinstance(output, str) else None

    if file_path:
        c = pdf_canvas.Canvas(file_path, pagesize=(page_w, page_h))
    else:
        if buf is None:
            buf = io.BytesIO()
        c = pdf_canvas.Canvas(buf, pagesize=(page_w, page_h))

    cell_w = config.cell_width_mm * mm
    cell_h = config.cell_height_mm * mm
    h_space = config.h_spacing_mm * mm
    v_space = config.v_spacing_mm * mm
    margin_left = config.margin_left_mm * mm + config.offset_x_mm * mm
    margin_top = config.margin_top_mm * mm + config.offset_y_mm * mm

    # Prepare QR image for embedding
    qr_buf = io.BytesIO()
    qr_image.save(qr_buf, "PNG")
    qr_buf.seek(0)
    qr_reader = ImageReader(qr_buf)

    text_margin = 2 * mm

    top_font = (
        config.top_font_size_pt or config.font_size_pt
    )
    bottom_font = (
        config.bottom_font_size_pt or config.font_size_pt
    )

    top_lines = (
        [ln for ln in config.top_text.split("\n") if ln.strip()]
        if config.top_text
        else []
    )
    bottom_lines = (
        [ln for ln in config.bottom_text.split("\n") if ln.strip()]
        if config.bottom_text
        else []
    )

    top_lh = top_font * 1.3
    bottom_lh = bottom_font * 1.3
    top_text_h = top_lh * len(top_lines) if top_lines else 0
    btm_text_h = bottom_lh * len(bottom_lines) if bottom_lines else 0

    for row in range(config.rows):
        for col in range(config.cols):
            x = margin_left + col * (cell_w + h_space)
            y = page_h - margin_top - (row + 1) * cell_h - row * v_space

            if config.show_borders:
                c.setStrokeColorRGB(0.8, 0.8, 0.8)
                c.setLineWidth(0.5)
                c.rect(x, y, cell_w, cell_h, stroke=1, fill=0)

            qr_area_top = (
                top_text_h + text_margin if top_lines else 0
            )
            qr_area_bottom = (
                btm_text_h + text_margin if bottom_lines else 0
            )
            available_h = cell_h - qr_area_top - qr_area_bottom
            qr_size = min(cell_w - 2 * text_margin, available_h)
            qr_x = x + (cell_w - qr_size) / 2
            qr_y = y + qr_area_bottom + (available_h - qr_size) / 2

            c.drawImage(
                qr_reader, qr_x, qr_y,
                width=qr_size, height=qr_size,
                mask="auto",
            )

            if top_lines:
                c.setFont("Helvetica", top_font)
                c.setFillColorRGB(0, 0, 0)
                tx = x + cell_w / 2
                for i, line in enumerate(top_lines):
                    ty = y + cell_h - top_lh * (i + 1)
                    c.drawCentredString(tx, ty, line)

            if bottom_lines:
                c.setFont("Helvetica", bottom_font)
                c.setFillColorRGB(0, 0, 0)
                tx = x + cell_w / 2
                for i, line in enumerate(reversed(bottom_lines)):
                    ty = y + text_margin + bottom_lh * i
                    c.drawCentredString(tx, ty, line)

    # Alignment guides
    if config.show_guides:
        c.setStrokeColorRGB(0.5, 0.5, 1.0)
        c.setLineWidth(0.25)
        c.setDash(2, 2)
        # Horizontal guides
        for row in range(config.rows + 1):
            gy = page_h - margin_top - row * (cell_h + v_space)
            c.line(0, gy, page_w, gy)
        # Vertical guides
        for col in range(config.cols + 1):
            gx = margin_left + col * (cell_w + h_space)
            c.line(gx, 0, gx, page_h)

    c.save()

    if buf is not None:
        return buf.getvalue()
    if file_path:
        with open(file_path, "rb") as f:
            return f.read()
    return b""

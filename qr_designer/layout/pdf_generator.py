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
    top_text_height = (config.font_size_pt * 1.2) if config.top_text else 0
    bottom_text_height = (config.font_size_pt * 1.2) if config.bottom_text else 0

    for row in range(config.rows):
        for col in range(config.cols):
            x = margin_left + col * (cell_w + h_space)
            # ReportLab Y starts from bottom
            y = page_h - margin_top - (row + 1) * cell_h - row * v_space

            if config.show_borders:
                c.setStrokeColorRGB(0.8, 0.8, 0.8)
                c.setLineWidth(0.5)
                c.rect(x, y, cell_w, cell_h, stroke=1, fill=0)

            # Calculate QR image area within cell
            qr_area_top = top_text_height + text_margin if config.top_text else 0
            qr_area_bottom = bottom_text_height + text_margin if config.bottom_text else 0
            available_h = cell_h - qr_area_top - qr_area_bottom
            qr_size = min(cell_w - 2 * text_margin, available_h)
            qr_x = x + (cell_w - qr_size) / 2
            qr_y = y + qr_area_bottom + (available_h - qr_size) / 2

            c.drawImage(qr_reader, qr_x, qr_y, width=qr_size, height=qr_size, mask="auto")

            # Top text
            if config.top_text:
                c.setFont("Helvetica", config.font_size_pt)
                c.setFillColorRGB(0, 0, 0)
                text_x = x + cell_w / 2
                text_y = y + cell_h - top_text_height
                c.drawCentredString(text_x, text_y, config.top_text)

            # Bottom text
            if config.bottom_text:
                c.setFont("Helvetica", config.font_size_pt)
                c.setFillColorRGB(0, 0, 0)
                text_x = x + cell_w / 2
                text_y = y + text_margin
                c.drawCentredString(text_x, text_y, config.bottom_text)

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

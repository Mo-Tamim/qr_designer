"""Unified export interface for PNG, SVG, and PDF."""

from __future__ import annotations

import io
from pathlib import Path

from PIL import Image
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas as pdf_canvas


def export_png(
    image: Image.Image,
    output: str | Path | io.BytesIO,
    dpi: int = 300,
) -> None:
    if isinstance(output, (str, Path)):
        image.save(str(output), "PNG", dpi=(dpi, dpi))
    else:
        image.save(output, "PNG", dpi=(dpi, dpi))


def export_png_bytes(image: Image.Image, dpi: int = 300) -> bytes:
    buf = io.BytesIO()
    export_png(image, buf, dpi=dpi)
    return buf.getvalue()


def export_svg(svg_string: str, output: str | Path | io.BytesIO) -> None:
    data = svg_string.encode("utf-8")
    if isinstance(output, (str, Path)):
        Path(output).write_bytes(data)
    else:
        output.write(data)


def export_svg_bytes(svg_string: str) -> bytes:
    return svg_string.encode("utf-8")


def export_pdf(
    image: Image.Image,
    output: str | Path | io.BytesIO,
    width_mm: float = 50.0,
    height_mm: float = 50.0,
    dpi: int = 300,
) -> None:
    """Export a single QR code as a PDF page."""
    buf = io.BytesIO()
    export_png(image, buf, dpi=dpi)
    buf.seek(0)

    page_w = width_mm * mm
    page_h = height_mm * mm

    if isinstance(output, (str, Path)):
        c = pdf_canvas.Canvas(str(output), pagesize=(page_w, page_h))
    else:
        c = pdf_canvas.Canvas(output, pagesize=(page_w, page_h))

    from reportlab.lib.utils import ImageReader

    img_reader = ImageReader(buf)
    c.drawImage(img_reader, 0, 0, width=page_w, height=page_h, mask="auto")
    c.save()


def export_pdf_bytes(
    image: Image.Image,
    width_mm: float = 50.0,
    height_mm: float = 50.0,
    dpi: int = 300,
) -> bytes:
    buf = io.BytesIO()
    export_pdf(image, buf, width_mm=width_mm, height_mm=height_mm, dpi=dpi)
    return buf.getvalue()

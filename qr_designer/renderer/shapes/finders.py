"""Finder pattern (eye) renderers for Pillow."""

from __future__ import annotations

from PIL import ImageDraw, ImageFilter, Image


def draw_finder_pattern(
    img: Image.Image,
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    cell_size: int,
    outer_shape: str = "square",
    inner_shape: str = "square",
    outer_color: str | tuple = "#000000",
    inner_color: str | tuple = "#000000",
    bg_color: str | tuple = "#FFFFFF",
    shadow: bool = False,
    emboss: bool = False,
) -> None:
    """Draw a complete 7x7 finder pattern at pixel position (x, y).

    The pattern is: outer ring (7x7) -> white gap (5x5) -> inner block (3x3).
    """
    s7 = cell_size * 7
    s5 = cell_size * 5
    s3 = cell_size * 3
    offset1 = cell_size
    offset2 = cell_size * 2

    if shadow:
        shadow_offset = max(2, cell_size // 5)
        _draw_shape(draw, x + shadow_offset, y + shadow_offset, s7, outer_shape, "#00000040")

    _draw_shape(draw, x, y, s7, outer_shape, outer_color)
    _draw_shape(draw, x + offset1, y + offset1, s5, outer_shape, bg_color)
    _draw_shape(draw, x + offset2, y + offset2, s3, inner_shape, inner_color)


def _draw_shape(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    size: int,
    shape: str,
    color: str | tuple,
) -> None:
    box = [x, y, x + size - 1, y + size - 1]
    if shape == "circle":
        draw.ellipse(box, fill=color)
    elif shape == "rounded":
        radius = size // 4
        draw.rounded_rectangle(box, radius=radius, fill=color)
    elif shape == "diamond":
        cx = x + size // 2
        cy = y + size // 2
        half = size // 2
        draw.polygon([(cx, y), (x + size, cy), (cx, y + size), (x, cy)], fill=color)
    else:
        draw.rectangle(box, fill=color)

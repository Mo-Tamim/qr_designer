"""Alignment pattern renderers for Pillow."""

from __future__ import annotations

from PIL import ImageDraw


def draw_alignment_pattern(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    cell_size: int,
    shape: str = "square",
    outer_color: str | tuple = "#000000",
    inner_color: str | tuple = "#000000",
    bg_color: str | tuple = "#FFFFFF",
) -> None:
    """Draw a 5x5 alignment pattern centered at the given module position.

    ``x``, ``y`` is the top-left pixel of the 5x5 block.
    """
    s5 = cell_size * 5
    s3 = cell_size * 3
    s1 = cell_size

    _draw_shape(draw, x, y, s5, shape, outer_color)
    _draw_shape(draw, x + cell_size, y + cell_size, s3, shape, bg_color)
    _draw_shape(draw, x + cell_size * 2, y + cell_size * 2, s1, shape, inner_color)


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
        radius = max(1, size // 4)
        draw.rounded_rectangle(box, radius=radius, fill=color)
    else:
        draw.rectangle(box, fill=color)

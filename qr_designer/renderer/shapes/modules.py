"""Module (pixel) shape drawers for Pillow rendering."""

from __future__ import annotations

import math
from abc import ABC, abstractmethod

from PIL import ImageDraw


class ModuleDrawer(ABC):
    """Draws a single QR module at the given cell position."""

    @abstractmethod
    def draw(
        self,
        draw: ImageDraw.ImageDraw,
        x: int,
        y: int,
        size: int,
        color: str | tuple,
    ) -> None: ...


class SquareDrawer(ModuleDrawer):
    def draw(self, draw: ImageDraw.ImageDraw, x: int, y: int, size: int, color: str | tuple) -> None:
        draw.rectangle([x, y, x + size - 1, y + size - 1], fill=color)


class CircleDrawer(ModuleDrawer):
    def draw(self, draw: ImageDraw.ImageDraw, x: int, y: int, size: int, color: str | tuple) -> None:
        margin = max(1, size // 10)
        draw.ellipse(
            [x + margin, y + margin, x + size - 1 - margin, y + size - 1 - margin],
            fill=color,
        )


class RoundedDrawer(ModuleDrawer):
    def __init__(self, radius_ratio: float = 0.3):
        self.radius_ratio = radius_ratio

    def draw(self, draw: ImageDraw.ImageDraw, x: int, y: int, size: int, color: str | tuple) -> None:
        radius = int(size * self.radius_ratio)
        draw.rounded_rectangle(
            [x, y, x + size - 1, y + size - 1],
            radius=radius,
            fill=color,
        )


class DiamondDrawer(ModuleDrawer):
    def draw(self, draw: ImageDraw.ImageDraw, x: int, y: int, size: int, color: str | tuple) -> None:
        cx = x + size // 2
        cy = y + size // 2
        half = size // 2 - 1
        points = [
            (cx, cy - half),
            (cx + half, cy),
            (cx, cy + half),
            (cx - half, cy),
        ]
        draw.polygon(points, fill=color)


class HexagonDrawer(ModuleDrawer):
    def draw(self, draw: ImageDraw.ImageDraw, x: int, y: int, size: int, color: str | tuple) -> None:
        cx = x + size / 2
        cy = y + size / 2
        r = size / 2 - 1
        points = []
        for i in range(6):
            angle = math.radians(60 * i - 30)
            px = cx + r * math.cos(angle)
            py = cy + r * math.sin(angle)
            points.append((px, py))
        draw.polygon(points, fill=color)


class StarDrawer(ModuleDrawer):
    def draw(self, draw: ImageDraw.ImageDraw, x: int, y: int, size: int, color: str | tuple) -> None:
        cx = x + size / 2
        cy = y + size / 2
        outer_r = size / 2 - 1
        inner_r = outer_r * 0.4
        points = []
        for i in range(10):
            angle = math.radians(36 * i - 90)
            r = outer_r if i % 2 == 0 else inner_r
            points.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
        draw.polygon(points, fill=color)


DRAWERS: dict[str, ModuleDrawer] = {
    "square": SquareDrawer(),
    "circle": CircleDrawer(),
    "rounded": RoundedDrawer(),
    "diamond": DiamondDrawer(),
    "hexagon": HexagonDrawer(),
    "star": StarDrawer(),
}


def get_drawer(name: str) -> ModuleDrawer:
    drawer = DRAWERS.get(name)
    if drawer is None:
        return DRAWERS["square"]
    return drawer

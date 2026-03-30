"""Raster rendering engine using Pillow."""

from __future__ import annotations

import math
from typing import Any

from PIL import Image, ImageDraw, ImageFilter

from ..core.matrix_analyzer import ModuleType
from ..styles.color import BackgroundType, ColorSpec, GradientSpec, GradientType
from ..styles.config import QRStyleConfig
from .base import BaseRenderer
from .shapes.alignment import draw_alignment_pattern
from .shapes.finders import draw_finder_pattern
from .shapes.modules import get_drawer


def _parse_color(color_str: str) -> tuple[int, ...]:
    c = color_str.lstrip("#")
    if len(c) == 6:
        return tuple(int(c[i : i + 2], 16) for i in (0, 2, 4))
    if len(c) == 8:
        return tuple(int(c[i : i + 2], 16) for i in (0, 2, 4, 6))
    return (0, 0, 0)


def _create_gradient(
    width: int, height: int, gradient: GradientSpec
) -> Image.Image:
    img = Image.new("RGBA", (width, height))
    pixels = img.load()

    stops = sorted(gradient.stops, key=lambda s: s.position)
    if len(stops) < 2:
        col = _parse_color(stops[0].color if stops else "#000000")
        for y in range(height):
            for x in range(width):
                pixels[x, y] = col + (255,)
        return img

    colors = [_parse_color(s.color) for s in stops]
    positions = [s.position for s in stops]

    for py in range(height):
        for px in range(width):
            if gradient.type == GradientType.RADIAL:
                cx, cy = width / 2, height / 2
                dist = math.sqrt((px - cx) ** 2 + (py - cy) ** 2)
                max_dist = math.sqrt(cx**2 + cy**2)
                t = min(dist / max_dist, 1.0) if max_dist > 0 else 0
            else:
                angle_rad = math.radians(gradient.angle)
                cos_a = math.cos(angle_rad)
                sin_a = math.sin(angle_rad)
                proj = (px * cos_a + py * sin_a)
                max_proj = abs(width * cos_a) + abs(height * sin_a)
                t = (proj / max_proj + 0.5) if max_proj > 0 else 0
                t = max(0.0, min(1.0, t))

            # Interpolate between stops
            seg = 0
            for i in range(len(positions) - 1):
                if t <= positions[i + 1]:
                    seg = i
                    break
            else:
                seg = len(positions) - 2

            p0, p1 = positions[seg], positions[seg + 1]
            local_t = (t - p0) / (p1 - p0) if p1 != p0 else 0
            c0, c1 = colors[seg], colors[seg + 1]
            r = int(c0[0] + (c1[0] - c0[0]) * local_t)
            g = int(c0[1] + (c1[1] - c0[1]) * local_t)
            b = int(c0[2] + (c1[2] - c0[2]) * local_t)
            pixels[px, py] = (r, g, b, 255)

    return img


def _resolve_module_color(
    color_spec: ColorSpec,
    px: int,
    py: int,
    total_w: int,
    total_h: int,
    gradient_cache: dict | None = None,
) -> tuple[int, ...]:
    """Return an RGBA tuple for the given module position."""
    if color_spec.use_gradient and color_spec.gradient:
        key = id(color_spec)
        if gradient_cache is not None and key in gradient_cache:
            grad_img = gradient_cache[key]
        else:
            grad_img = _create_gradient(total_w, total_h, color_spec.gradient)
            if gradient_cache is not None:
                gradient_cache[key] = grad_img
        gx = min(px, grad_img.width - 1)
        gy = min(py, grad_img.height - 1)
        return grad_img.getpixel((gx, gy))
    return _parse_color(color_spec.solid) + (255,)


class PillowRenderer(BaseRenderer):
    def render(
        self,
        matrix: list[list[bool]],
        classified: list[list[ModuleType]],
        style: QRStyleConfig,
    ) -> Image.Image:
        module_count = len(matrix)
        cell_size = style.size_px // module_count
        img_size = cell_size * module_count

        bg_color = self._make_background(img_size, style)
        img = bg_color
        draw = ImageDraw.Draw(img)
        grad_cache: dict[int, Image.Image] = {}

        finder_origins = self._finder_origins(module_count)
        alignment_origins = self._alignment_origins(classified, module_count)

        # Draw finder patterns as composite shapes
        for r, c in finder_origins:
            resolved_bg = _parse_color(
                style.background.color
                if style.background.type == BackgroundType.SOLID
                else "#FFFFFF"
            )
            draw_finder_pattern(
                img,
                draw,
                c * cell_size,
                r * cell_size,
                cell_size,
                outer_shape=style.finder_outer_shape,
                inner_shape=style.finder_inner_shape,
                outer_color=_resolve_module_color(
                    style.finder_outer_color, c * cell_size, r * cell_size, img_size, img_size, grad_cache
                ),
                inner_color=_resolve_module_color(
                    style.finder_inner_color,
                    (c + 2) * cell_size,
                    (r + 2) * cell_size,
                    img_size,
                    img_size,
                    grad_cache,
                ),
                bg_color=resolved_bg,
                shadow=style.finder_shadow,
                emboss=style.finder_3d,
            )

        # Draw alignment patterns
        for r, c in alignment_origins:
            resolved_bg = _parse_color(
                style.background.color
                if style.background.type == BackgroundType.SOLID
                else "#FFFFFF"
            )
            draw_alignment_pattern(
                draw,
                c * cell_size,
                r * cell_size,
                cell_size,
                shape=style.alignment_shape,
                outer_color=_resolve_module_color(
                    style.alignment_outer_color, c * cell_size, r * cell_size, img_size, img_size, grad_cache
                ),
                inner_color=_resolve_module_color(
                    style.alignment_inner_color,
                    (c + 2) * cell_size,
                    (r + 2) * cell_size,
                    img_size,
                    img_size,
                    grad_cache,
                ),
                bg_color=resolved_bg,
            )

        # Regions handled by composite drawing
        skip_types = {
            ModuleType.FINDER_OUTER,
            ModuleType.FINDER_INNER,
            ModuleType.ALIGNMENT_OUTER,
            ModuleType.ALIGNMENT_INNER,
        }

        drawer = get_drawer(style.data_module_shape)

        for r in range(module_count):
            for c in range(module_count):
                if classified[r][c] in skip_types:
                    continue
                if not matrix[r][c]:
                    continue

                px = c * cell_size
                py = r * cell_size
                color = _resolve_module_color(
                    style.data_module_color, px, py, img_size, img_size, grad_cache
                )
                drawer.draw(draw, px, py, cell_size, color)

        # Apply QR shape mask
        img = self._apply_shape_mask(img, style.qr_shape)

        return img

    def _make_background(self, size: int, style: QRStyleConfig) -> Image.Image:
        bg = style.background
        if bg.type == BackgroundType.TRANSPARENT:
            return Image.new("RGBA", (size, size), (0, 0, 0, 0))
        if bg.type == BackgroundType.GRADIENT and bg.gradient:
            return _create_gradient(size, size, bg.gradient)
        if bg.type == BackgroundType.IMAGE and bg.image_path:
            try:
                bg_img = Image.open(bg.image_path).convert("RGBA")
                bg_img = bg_img.resize((size, size), Image.LANCZOS)
                if bg.opacity < 1.0:
                    alpha = bg_img.split()[3]
                    alpha = alpha.point(lambda p: int(p * bg.opacity))
                    bg_img.putalpha(alpha)
                white = Image.new("RGBA", (size, size), (255, 255, 255, 255))
                white.paste(bg_img, (0, 0), bg_img)
                return white
            except Exception:
                pass
        color = _parse_color(bg.color)
        return Image.new("RGBA", (size, size), color + (255,))

    def _finder_origins(self, module_count: int) -> list[tuple[int, int]]:
        return [
            (0, 0),
            (0, module_count - 7),
            (module_count - 7, 0),
        ]

    def _alignment_origins(
        self, classified: list[list[ModuleType]], module_count: int
    ) -> list[tuple[int, int]]:
        """Find top-left corners of alignment patterns from the classified matrix."""
        origins: list[tuple[int, int]] = []
        visited: set[tuple[int, int]] = set()
        for r in range(module_count):
            for c in range(module_count):
                if classified[r][c] == ModuleType.ALIGNMENT_OUTER and (r, c) not in visited:
                    # Walk to find the top-left of the 5x5 block
                    # The center is at (r+2, c+2) from top-left
                    top_r, top_c = r, c
                    # Ensure we haven't already tracked this alignment
                    center = (top_r + 2, top_c + 2)
                    if center not in visited:
                        origins.append((top_r, top_c))
                        for dr in range(5):
                            for dc in range(5):
                                visited.add((top_r + dr, top_c + dc))
        return origins

    def _apply_shape_mask(self, img: Image.Image, shape: str) -> Image.Image:
        if shape == "square":
            return img
        w, h = img.size
        mask = Image.new("L", (w, h), 0)
        mask_draw = ImageDraw.Draw(mask)
        if shape == "circle":
            mask_draw.ellipse([0, 0, w - 1, h - 1], fill=255)
        elif shape == "rounded":
            radius = w // 10
            mask_draw.rounded_rectangle([0, 0, w - 1, h - 1], radius=radius, fill=255)
        else:
            return img

        result = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        result.paste(img, (0, 0), mask)
        return result

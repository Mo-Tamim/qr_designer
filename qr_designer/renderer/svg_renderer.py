"""Vector rendering engine producing SVG output."""

from __future__ import annotations

import math
from typing import Any
from xml.etree.ElementTree import Element, SubElement, tostring

from ..core.matrix_analyzer import ModuleType
from ..styles.color import BackgroundType, ColorSpec, GradientSpec, GradientType
from ..styles.config import QRStyleConfig
from .base import BaseRenderer


def _gradient_id(prefix: str, idx: int) -> str:
    return f"{prefix}_{idx}"


class SVGRenderer(BaseRenderer):
    def render(
        self,
        matrix: list[list[bool]],
        classified: list[list[ModuleType]],
        style: QRStyleConfig,
    ) -> str:
        module_count = len(matrix)
        cell_size = style.size_px / module_count
        img_size = style.size_px

        svg = Element(
            "svg",
            xmlns="http://www.w3.org/2000/svg",
            width=str(img_size),
            height=str(img_size),
            viewBox=f"0 0 {img_size} {img_size}",
        )

        defs = SubElement(svg, "defs")
        grad_counter = [0]

        # Background
        self._add_background(svg, defs, img_size, style, grad_counter)

        # Clip path for QR shape
        if style.qr_shape != "square":
            clip_id = "qr_clip"
            clip_path = SubElement(defs, "clipPath", id=clip_id)
            if style.qr_shape == "circle":
                SubElement(
                    clip_path,
                    "circle",
                    cx=str(img_size / 2),
                    cy=str(img_size / 2),
                    r=str(img_size / 2),
                )
            elif style.qr_shape == "rounded":
                SubElement(
                    clip_path,
                    "rect",
                    x="0",
                    y="0",
                    width=str(img_size),
                    height=str(img_size),
                    rx=str(img_size // 10),
                    ry=str(img_size // 10),
                )
            group = SubElement(svg, "g", **{"clip-path": f"url(#{clip_id})"})
        else:
            group = SubElement(svg, "g")

        finder_origins = [(0, 0), (0, module_count - 7), (module_count - 7, 0)]
        finder_cells: set[tuple[int, int]] = set()
        for fr, fc in finder_origins:
            for dr in range(7):
                for dc in range(7):
                    finder_cells.add((fr + dr, fc + dc))

        alignment_cells: set[tuple[int, int]] = set()
        alignment_centers: list[tuple[int, int]] = []
        for r in range(module_count):
            for c in range(module_count):
                if classified[r][c] in (ModuleType.ALIGNMENT_OUTER, ModuleType.ALIGNMENT_INNER):
                    alignment_cells.add((r, c))

        visited_align: set[tuple[int, int]] = set()
        for r in range(module_count):
            for c in range(module_count):
                if classified[r][c] == ModuleType.ALIGNMENT_OUTER and (r, c) not in visited_align:
                    alignment_centers.append((r, c))
                    for dr in range(5):
                        for dc in range(5):
                            visited_align.add((r + dr, c + dc))

        # Draw finder patterns
        for fr, fc in finder_origins:
            self._draw_svg_finder(
                group, defs, fr, fc, cell_size, style, grad_counter, img_size
            )

        # Draw alignment patterns
        for ar, ac in alignment_centers:
            self._draw_svg_alignment(
                group, defs, ar, ac, cell_size, style, grad_counter, img_size
            )

        # Draw data modules
        data_fill = self._resolve_fill(
            defs, style.data_module_color, grad_counter, img_size
        )
        for r in range(module_count):
            for c in range(module_count):
                if (r, c) in finder_cells or (r, c) in alignment_cells:
                    continue
                if not matrix[r][c]:
                    continue
                px = c * cell_size
                py = r * cell_size
                self._draw_module_svg(
                    group, px, py, cell_size, style.data_module_shape, data_fill
                )

        return tostring(svg, encoding="unicode")

    def _add_background(
        self,
        svg: Element,
        defs: Element,
        size: int,
        style: QRStyleConfig,
        counter: list[int],
    ) -> None:
        bg = style.background
        if bg.type == BackgroundType.TRANSPARENT:
            return
        if bg.type == BackgroundType.GRADIENT and bg.gradient:
            fill = self._create_gradient_def(defs, bg.gradient, counter, size)
        else:
            fill = bg.color
        SubElement(
            svg,
            "rect",
            x="0",
            y="0",
            width=str(size),
            height=str(size),
            fill=fill,
        )

    def _resolve_fill(
        self,
        defs: Element,
        color_spec: ColorSpec,
        counter: list[int],
        size: int,
    ) -> str:
        if color_spec.use_gradient and color_spec.gradient:
            return self._create_gradient_def(defs, color_spec.gradient, counter, size)
        return color_spec.solid

    def _create_gradient_def(
        self,
        defs: Element,
        gradient: GradientSpec,
        counter: list[int],
        size: int,
    ) -> str:
        gid = _gradient_id("grad", counter[0])
        counter[0] += 1

        if gradient.type == GradientType.RADIAL:
            g = SubElement(
                defs,
                "radialGradient",
                id=gid,
                cx="50%",
                cy="50%",
                r="70.7%",
            )
        else:
            angle = math.radians(gradient.angle)
            x1 = 50 - 50 * math.cos(angle)
            y1 = 50 - 50 * math.sin(angle)
            x2 = 50 + 50 * math.cos(angle)
            y2 = 50 + 50 * math.sin(angle)
            g = SubElement(
                defs,
                "linearGradient",
                id=gid,
                x1=f"{x1}%",
                y1=f"{y1}%",
                x2=f"{x2}%",
                y2=f"{y2}%",
            )

        for stop in sorted(gradient.stops, key=lambda s: s.position):
            SubElement(
                g,
                "stop",
                offset=f"{stop.position * 100}%",
                **{"stop-color": stop.color},
            )

        return f"url(#{gid})"

    def _draw_module_svg(
        self,
        parent: Element,
        x: float,
        y: float,
        size: float,
        shape: str,
        fill: str,
    ) -> None:
        if shape == "circle":
            margin = max(0.5, size * 0.1)
            r = (size - 2 * margin) / 2
            SubElement(
                parent,
                "circle",
                cx=str(x + size / 2),
                cy=str(y + size / 2),
                r=str(r),
                fill=fill,
            )
        elif shape == "rounded":
            radius = size * 0.3
            SubElement(
                parent,
                "rect",
                x=str(x),
                y=str(y),
                width=str(size),
                height=str(size),
                rx=str(radius),
                ry=str(radius),
                fill=fill,
            )
        elif shape == "diamond":
            cx = x + size / 2
            cy = y + size / 2
            half = size / 2 - 0.5
            points = f"{cx},{cy - half} {cx + half},{cy} {cx},{cy + half} {cx - half},{cy}"
            SubElement(parent, "polygon", points=points, fill=fill)
        elif shape == "hexagon":
            cx = x + size / 2
            cy = y + size / 2
            r = size / 2 - 0.5
            pts = []
            for i in range(6):
                a = math.radians(60 * i - 30)
                pts.append(f"{cx + r * math.cos(a)},{cy + r * math.sin(a)}")
            SubElement(parent, "polygon", points=" ".join(pts), fill=fill)
        elif shape == "star":
            cx = x + size / 2
            cy = y + size / 2
            outer_r = size / 2 - 0.5
            inner_r = outer_r * 0.4
            pts = []
            for i in range(10):
                a = math.radians(36 * i - 90)
                r = outer_r if i % 2 == 0 else inner_r
                pts.append(f"{cx + r * math.cos(a)},{cy + r * math.sin(a)}")
            SubElement(parent, "polygon", points=" ".join(pts), fill=fill)
        else:
            SubElement(
                parent,
                "rect",
                x=str(x),
                y=str(y),
                width=str(size),
                height=str(size),
                fill=fill,
            )

    def _draw_svg_finder(
        self,
        parent: Element,
        defs: Element,
        row: int,
        col: int,
        cell_size: float,
        style: QRStyleConfig,
        counter: list[int],
        img_size: int,
    ) -> None:
        x = col * cell_size
        y = row * cell_size
        s7 = cell_size * 7
        s5 = cell_size * 5
        s3 = cell_size * 3

        outer_fill = self._resolve_fill(defs, style.finder_outer_color, counter, img_size)
        inner_fill = self._resolve_fill(defs, style.finder_inner_color, counter, img_size)
        bg_fill = style.background.color if style.background.type == BackgroundType.SOLID else "#FFFFFF"

        self._draw_shape_svg(parent, x, y, s7, style.finder_outer_shape, outer_fill)
        self._draw_shape_svg(parent, x + cell_size, y + cell_size, s5, style.finder_outer_shape, bg_fill)
        self._draw_shape_svg(parent, x + cell_size * 2, y + cell_size * 2, s3, style.finder_inner_shape, inner_fill)

    def _draw_svg_alignment(
        self,
        parent: Element,
        defs: Element,
        row: int,
        col: int,
        cell_size: float,
        style: QRStyleConfig,
        counter: list[int],
        img_size: int,
    ) -> None:
        x = col * cell_size
        y = row * cell_size
        s5 = cell_size * 5
        s3 = cell_size * 3
        s1 = cell_size

        outer_fill = self._resolve_fill(defs, style.alignment_outer_color, counter, img_size)
        inner_fill = self._resolve_fill(defs, style.alignment_inner_color, counter, img_size)
        bg_fill = style.background.color if style.background.type == BackgroundType.SOLID else "#FFFFFF"

        self._draw_shape_svg(parent, x, y, s5, style.alignment_shape, outer_fill)
        self._draw_shape_svg(parent, x + cell_size, y + cell_size, s3, style.alignment_shape, bg_fill)
        self._draw_shape_svg(parent, x + cell_size * 2, y + cell_size * 2, s1, style.alignment_shape, inner_fill)

    def _draw_shape_svg(
        self,
        parent: Element,
        x: float,
        y: float,
        size: float,
        shape: str,
        fill: str,
    ) -> None:
        if shape == "circle":
            SubElement(
                parent,
                "circle",
                cx=str(x + size / 2),
                cy=str(y + size / 2),
                r=str(size / 2),
                fill=fill,
            )
        elif shape == "rounded":
            radius = size / 4
            SubElement(
                parent,
                "rect",
                x=str(x),
                y=str(y),
                width=str(size),
                height=str(size),
                rx=str(radius),
                ry=str(radius),
                fill=fill,
            )
        else:
            SubElement(
                parent,
                "rect",
                x=str(x),
                y=str(y),
                width=str(size),
                height=str(size),
                fill=fill,
            )

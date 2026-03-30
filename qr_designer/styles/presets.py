"""Built-in style presets."""

from __future__ import annotations

from .color import (
    BackgroundSpec,
    BackgroundType,
    ColorSpec,
    GradientSpec,
    GradientStop,
    GradientType,
)
from .config import QRStyleConfig


def classic() -> QRStyleConfig:
    return QRStyleConfig()


def rounded_dots() -> QRStyleConfig:
    return QRStyleConfig(
        data_module_shape="circle",
        finder_outer_shape="rounded",
        finder_inner_shape="circle",
    )


def ocean_gradient() -> QRStyleConfig:
    grad = GradientSpec(
        type=GradientType.LINEAR,
        angle=135.0,
        stops=[
            GradientStop(color="#0077B6", position=0.0),
            GradientStop(color="#00B4D8", position=0.5),
            GradientStop(color="#90E0EF", position=1.0),
        ],
    )
    return QRStyleConfig(
        data_module_shape="rounded",
        data_module_color=ColorSpec(use_gradient=True, gradient=grad),
        finder_outer_shape="rounded",
        finder_inner_shape="rounded",
        finder_outer_color=ColorSpec(solid="#0077B6"),
        finder_inner_color=ColorSpec(solid="#023E8A"),
    )


def sunset() -> QRStyleConfig:
    grad = GradientSpec(
        type=GradientType.RADIAL,
        stops=[
            GradientStop(color="#FF6B6B", position=0.0),
            GradientStop(color="#FFA500", position=0.5),
            GradientStop(color="#FFD93D", position=1.0),
        ],
    )
    return QRStyleConfig(
        data_module_shape="diamond",
        data_module_color=ColorSpec(use_gradient=True, gradient=grad),
        finder_outer_shape="rounded",
        finder_inner_shape="circle",
        finder_outer_color=ColorSpec(solid="#FF6B6B"),
        finder_inner_color=ColorSpec(solid="#CC0000"),
    )


def minimal() -> QRStyleConfig:
    return QRStyleConfig(
        data_module_shape="square",
        data_module_color=ColorSpec(solid="#333333"),
        finder_outer_color=ColorSpec(solid="#333333"),
        finder_inner_color=ColorSpec(solid="#333333"),
        background=BackgroundSpec(type=BackgroundType.SOLID, color="#F5F5F5"),
    )


def neon() -> QRStyleConfig:
    return QRStyleConfig(
        data_module_shape="circle",
        data_module_color=ColorSpec(solid="#39FF14"),
        finder_outer_shape="circle",
        finder_inner_shape="circle",
        finder_outer_color=ColorSpec(solid="#39FF14"),
        finder_inner_color=ColorSpec(solid="#00FF41"),
        background=BackgroundSpec(type=BackgroundType.SOLID, color="#0D0D0D"),
    )


PRESETS: dict[str, callable] = {
    "classic": classic,
    "rounded_dots": rounded_dots,
    "ocean_gradient": ocean_gradient,
    "sunset": sunset,
    "minimal": minimal,
    "neon": neon,
}

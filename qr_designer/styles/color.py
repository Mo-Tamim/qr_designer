"""Color specification types for the rendering engine."""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class GradientType(str, Enum):
    LINEAR = "linear"
    RADIAL = "radial"


class GradientStop(BaseModel):
    color: str = "#000000"
    position: float = Field(0.0, ge=0.0, le=1.0)


class GradientSpec(BaseModel):
    type: GradientType = GradientType.LINEAR
    angle: float = 0.0
    stops: list[GradientStop] = Field(
        default_factory=lambda: [
            GradientStop(color="#000000", position=0.0),
            GradientStop(color="#000000", position=1.0),
        ]
    )


class BackgroundType(str, Enum):
    SOLID = "solid"
    GRADIENT = "gradient"
    IMAGE = "image"
    TRANSPARENT = "transparent"


class ColorSpec(BaseModel):
    """Flexible color specification: solid hex or gradient."""

    solid: str = "#000000"
    gradient: Optional[GradientSpec] = None
    use_gradient: bool = False

    def resolve_solid(self) -> str:
        return self.solid


class BackgroundSpec(BaseModel):
    type: BackgroundType = BackgroundType.SOLID
    color: str = "#FFFFFF"
    gradient: Optional[GradientSpec] = None
    image_path: Optional[str] = None
    opacity: float = Field(1.0, ge=0.0, le=1.0)

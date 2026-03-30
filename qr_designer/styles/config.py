"""Central style configuration model."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field

from .color import BackgroundSpec, ColorSpec


class LogoConfig(BaseModel):
    image_path: str = ""
    size_ratio: float = Field(0.2, ge=0.05, le=0.35)
    padding: int = Field(5, ge=0, le=40)
    margin: int = Field(0, ge=0, le=20)
    frame_shape: str = "none"  # "none", "circle", "square", "rounded"
    frame_color: str = "#FFFFFF"
    logo_shape: str = "original"  # "original", "circle", "rounded_square"
    border_width: int = Field(0, ge=0, le=10)
    border_color: str = "#000000"
    shadow: bool = False
    shadow_color: str = "#00000066"
    shadow_offset: int = Field(3, ge=0, le=10)
    shadow_blur: int = Field(8, ge=0, le=20)
    bg_opacity: int = Field(100, ge=0, le=100)
    text: str = ""
    text_color: str = "#000000"
    text_font_size: int = Field(14, ge=8, le=32)


class QRStyleConfig(BaseModel):
    # Content
    content_type: str = "url"
    content_data: dict = Field(default_factory=lambda: {"url": "https://example.com"})

    # Module styling
    data_module_shape: str = "square"
    data_module_color: ColorSpec = Field(default_factory=ColorSpec)

    # Finder pattern styling
    finder_outer_shape: str = "square"
    finder_inner_shape: str = "square"
    finder_outer_color: ColorSpec = Field(default_factory=ColorSpec)
    finder_inner_color: ColorSpec = Field(default_factory=lambda: ColorSpec(solid="#000000"))

    # Alignment pattern styling
    alignment_shape: str = "square"
    alignment_outer_color: ColorSpec = Field(default_factory=ColorSpec)
    alignment_inner_color: ColorSpec = Field(default_factory=lambda: ColorSpec(solid="#000000"))

    # Background
    background: BackgroundSpec = Field(default_factory=BackgroundSpec)

    # Logo
    logo: Optional[LogoConfig] = None

    # QR code outer shape
    qr_shape: str = "square"  # "square", "rounded", "circle"

    # Error correction
    error_correction: str = "H"

    # Export settings
    size_px: int = Field(800, ge=100, le=4096)
    dpi: int = Field(300, ge=72, le=1200)

    # Finder effects
    finder_shadow: bool = False
    finder_3d: bool = False

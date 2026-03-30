"""Pydantic request/response models for the API."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field

from ..layout.grid import GridConfig
from ..styles.color import BackgroundSpec, ColorSpec
from ..styles.config import LogoConfig, QRStyleConfig


class PreviewRequest(BaseModel):
    style: QRStyleConfig = Field(default_factory=QRStyleConfig)
    preview_size: int = Field(400, ge=100, le=1024)


class ExportRequest(BaseModel):
    style: QRStyleConfig = Field(default_factory=QRStyleConfig)
    format: str = "png"  # "png", "svg", "pdf"
    width_mm: float = 50.0
    height_mm: float = 50.0


class LayoutPreviewRequest(BaseModel):
    style: QRStyleConfig = Field(default_factory=QRStyleConfig)
    grid: GridConfig = Field(default_factory=GridConfig)


class LayoutExportRequest(BaseModel):
    style: QRStyleConfig = Field(default_factory=QRStyleConfig)
    grid: GridConfig = Field(default_factory=GridConfig)


class PresetListItem(BaseModel):
    name: str
    label: str

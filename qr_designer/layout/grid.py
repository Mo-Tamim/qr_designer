"""Grid layout configuration for print sheets."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class GridConfig(BaseModel):
    rows: int = Field(5, ge=1, le=20)
    cols: int = Field(4, ge=1, le=20)

    cell_width_mm: float = Field(40.0, ge=10.0)
    cell_height_mm: float = Field(50.0, ge=10.0)

    h_spacing_mm: float = Field(5.0, ge=0.0)
    v_spacing_mm: float = Field(5.0, ge=0.0)

    margin_top_mm: float = Field(10.0, ge=0.0)
    margin_bottom_mm: float = Field(10.0, ge=0.0)
    margin_left_mm: float = Field(10.0, ge=0.0)
    margin_right_mm: float = Field(10.0, ge=0.0)

    # Fine-tune offsets for sticker sheet alignment
    offset_x_mm: float = 0.0
    offset_y_mm: float = 0.0

    # Text labels (newline-separated for multi-line)
    top_text: str = ""
    bottom_text: str = ""
    font_size_pt: float = Field(8.0, ge=4.0, le=24.0)
    top_font_size_pt: float | None = None
    bottom_font_size_pt: float | None = None

    # Visual aids
    show_guides: bool = False
    show_borders: bool = False

    page_size: str = "a4"
    page_width_mm: Optional[float] = None
    page_height_mm: Optional[float] = None

"""Page size definitions for print layouts."""

from __future__ import annotations

from pydantic import BaseModel, Field


class PageSize(BaseModel):
    width_mm: float
    height_mm: float
    name: str = "Custom"


# Common page sizes
A4 = PageSize(width_mm=210.0, height_mm=297.0, name="A4")
A3 = PageSize(width_mm=297.0, height_mm=420.0, name="A3")
LETTER = PageSize(width_mm=215.9, height_mm=279.4, name="Letter")
LEGAL = PageSize(width_mm=215.9, height_mm=355.6, name="Legal")

PAGE_SIZES: dict[str, PageSize] = {
    "a4": A4,
    "a3": A3,
    "letter": LETTER,
    "legal": LEGAL,
}


def get_page_size(name: str) -> PageSize:
    return PAGE_SIZES.get(name.lower(), A4)

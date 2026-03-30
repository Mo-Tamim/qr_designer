"""Abstract base for QR renderers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from ..styles.config import QRStyleConfig


class BaseRenderer(ABC):
    """Renders a classified QR matrix according to a style config."""

    @abstractmethod
    def render(
        self,
        matrix: list[list[bool]],
        classified: list[list[Any]],
        style: QRStyleConfig,
    ) -> Any:
        """Return the rendered output (Image, SVG string, etc.)."""
        ...

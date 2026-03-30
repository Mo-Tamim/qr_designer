"""QR matrix generation using the qrcode library."""

from __future__ import annotations

import qrcode
import qrcode.constants

ERROR_CORRECTION_MAP = {
    "L": qrcode.constants.ERROR_CORRECT_L,
    "M": qrcode.constants.ERROR_CORRECT_M,
    "Q": qrcode.constants.ERROR_CORRECT_Q,
    "H": qrcode.constants.ERROR_CORRECT_H,
}


def recommend_error_correction(has_logo: bool, style_complexity: int = 0) -> str:
    """Suggest error correction level based on styling choices.

    ``style_complexity`` ranges from 0 (no styling) to 3 (heavy
    customization).  A logo always bumps to at least Q.
    """
    if has_logo:
        return "H"
    if style_complexity >= 2:
        return "Q"
    if style_complexity >= 1:
        return "M"
    return "L"


def generate_matrix(
    data: str,
    error_correction: str = "H",
    version: int | None = None,
    box_size: int = 1,
    border: int = 0,
) -> list[list[bool]]:
    """Generate a boolean matrix for the given data.

    Returns a 2-D list where ``True`` = dark module.
    """
    ec = ERROR_CORRECTION_MAP.get(error_correction.upper(), qrcode.constants.ERROR_CORRECT_H)
    qr = qrcode.QRCode(
        version=version,
        error_correction=ec,
        box_size=box_size,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)

    modules = qr.get_matrix()
    return [[bool(cell) for cell in row] for row in modules]


def get_qr_version(
    data: str,
    error_correction: str = "H",
) -> int:
    """Return the QR version that would be chosen for the given data."""
    ec = ERROR_CORRECTION_MAP.get(error_correction.upper(), qrcode.constants.ERROR_CORRECT_H)
    qr = qrcode.QRCode(error_correction=ec, box_size=1, border=0)
    qr.add_data(data)
    qr.make(fit=True)
    return qr.version  # type: ignore[return-value]

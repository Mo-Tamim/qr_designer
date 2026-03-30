"""Logo embedding into QR code images."""

from __future__ import annotations

from PIL import Image, ImageDraw


def embed_logo(
    qr_image: Image.Image,
    logo_path: str,
    size_ratio: float = 0.2,
    padding: int = 5,
    frame_shape: str = "none",
    frame_color: str = "#FFFFFF",
) -> Image.Image:
    """Embed a logo at the center of the QR code image.

    Returns a new image with the logo composited.
    """
    logo = Image.open(logo_path).convert("RGBA")

    qr_w, qr_h = qr_image.size
    logo_max = int(min(qr_w, qr_h) * size_ratio)
    logo.thumbnail((logo_max, logo_max), Image.LANCZOS)
    logo_w, logo_h = logo.size

    total_w = logo_w + padding * 2
    total_h = logo_h + padding * 2

    result = qr_image.copy()

    # Draw frame / background behind logo
    if frame_shape != "none":
        frame_img = Image.new("RGBA", (total_w, total_h), (0, 0, 0, 0))
        frame_draw = ImageDraw.Draw(frame_img)
        fc = _parse_color(frame_color)

        if frame_shape == "circle":
            frame_draw.ellipse([0, 0, total_w - 1, total_h - 1], fill=fc)
        elif frame_shape == "rounded":
            r = min(total_w, total_h) // 4
            frame_draw.rounded_rectangle(
                [0, 0, total_w - 1, total_h - 1], radius=r, fill=fc
            )
        else:
            frame_draw.rectangle([0, 0, total_w - 1, total_h - 1], fill=fc)

        # Paste frame centered
        fx = (qr_w - total_w) // 2
        fy = (qr_h - total_h) // 2
        result.paste(frame_img, (fx, fy), frame_img)

    # Paste logo centered
    lx = (qr_w - logo_w) // 2
    ly = (qr_h - logo_h) // 2
    result.paste(logo, (lx, ly), logo)

    return result


def _parse_color(color_str: str) -> tuple[int, ...]:
    c = color_str.lstrip("#")
    if len(c) == 8:
        return tuple(int(c[i : i + 2], 16) for i in (0, 2, 4, 6))
    if len(c) == 6:
        return tuple(int(c[i : i + 2], 16) for i in (0, 2, 4)) + (255,)
    return (255, 255, 255, 255)

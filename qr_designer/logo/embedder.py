"""Logo embedding into QR code images."""

from __future__ import annotations

from PIL import Image, ImageDraw, ImageFilter, ImageFont


def embed_logo(
    qr_image: Image.Image,
    logo_path: str,
    size_ratio: float = 0.2,
    padding: int = 5,
    margin: int = 0,
    frame_shape: str = "none",
    frame_color: str = "#FFFFFF",
    logo_shape: str = "original",
    border_width: int = 0,
    border_color: str = "#000000",
    shadow: bool = False,
    shadow_color: str = "#00000066",
    shadow_offset: int = 3,
    shadow_blur: int = 8,
    bg_opacity: int = 100,
    text: str = "",
    text_color: str = "#000000",
    text_font_size: int = 14,
) -> Image.Image:
    """Embed a logo at the center of the QR code image.

    Returns a new image with the logo composited.
    """
    logo = Image.open(logo_path).convert("RGBA")

    qr_w, qr_h = qr_image.size
    logo_max = int(min(qr_w, qr_h) * size_ratio)
    logo.thumbnail((logo_max, logo_max), Image.LANCZOS)

    if logo_shape != "original":
        logo = _crop_logo_shape(logo, logo_shape)

    logo_w, logo_h = logo.size

    text_height = 0
    if text.strip():
        font = _get_font(text_font_size)
        bbox = font.getbbox(text)
        text_height = bbox[3] - bbox[1] + 6

    content_w = logo_w
    content_h = logo_h + (text_height if text.strip() else 0)

    total_w = content_w + padding * 2 + border_width * 2 + margin * 2
    total_h = content_h + padding * 2 + border_width * 2 + margin * 2

    result = qr_image.copy()

    cx = (qr_w - total_w) // 2
    cy = (qr_h - total_h) // 2

    if frame_shape != "none":
        frame_area_w = content_w + padding * 2 + border_width * 2
        frame_area_h = content_h + padding * 2 + border_width * 2

        if shadow:
            _draw_shadow(
                result, frame_shape, frame_area_w, frame_area_h,
                cx + margin, cy + margin,
                shadow_color, shadow_offset, shadow_blur,
            )

        _draw_frame(
            result, frame_shape, frame_area_w, frame_area_h,
            cx + margin, cy + margin,
            frame_color, bg_opacity, border_width, border_color,
        )
    else:
        _draw_clear_zone(result, total_w, total_h, cx, cy, qr_image)

    lx = (qr_w - logo_w) // 2
    ly = (qr_h - content_h) // 2
    result.paste(logo, (lx, ly), logo)

    if text.strip():
        _draw_text(result, text, lx + logo_w // 2, ly + logo_h + 2,
                   text_color, font)

    return result


def _crop_logo_shape(logo: Image.Image, shape: str) -> Image.Image:
    """Crop logo to a circle or rounded square using an alpha mask."""
    w, h = logo.size
    mask = Image.new("L", (w, h), 0)
    draw = ImageDraw.Draw(mask)

    if shape == "circle":
        draw.ellipse([0, 0, w - 1, h - 1], fill=255)
    elif shape == "rounded_square":
        r = min(w, h) // 5
        draw.rounded_rectangle([0, 0, w - 1, h - 1], radius=r, fill=255)

    result = logo.copy()
    result.putalpha(mask)
    if logo.mode == "RGBA":
        orig_alpha = logo.split()[3]
        combined = Image.new("L", (w, h), 0)
        combined.paste(orig_alpha, mask=mask)
        result.putalpha(combined)

    return result


def _draw_shadow(
    target: Image.Image,
    shape: str,
    w: int, h: int,
    x: int, y: int,
    color: str,
    offset: int,
    blur_radius: int,
) -> None:
    """Draw a blurred shadow behind the frame."""
    pad = blur_radius * 2
    shadow_img = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    draw = ImageDraw.Draw(shadow_img)
    sc = _parse_color(color)

    sx, sy = pad, pad
    if shape == "circle":
        draw.ellipse([sx, sy, sx + w - 1, sy + h - 1], fill=sc)
    elif shape == "rounded":
        r = min(w, h) // 4
        draw.rounded_rectangle(
            [sx, sy, sx + w - 1, sy + h - 1],
            radius=r, fill=sc,
        )
    else:
        draw.rectangle(
            [sx, sy, sx + w - 1, sy + h - 1], fill=sc,
        )

    shadow_img = shadow_img.filter(
        ImageFilter.GaussianBlur(radius=blur_radius)
    )

    paste_x = x + offset - pad
    paste_y = y + offset - pad
    target.paste(shadow_img, (paste_x, paste_y), shadow_img)


def _draw_frame(
    target: Image.Image,
    shape: str,
    w: int, h: int,
    x: int, y: int,
    fill_color: str,
    bg_opacity: int,
    border_width: int,
    border_color: str,
) -> None:
    """Draw the frame background with optional border stroke."""
    frame_img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(frame_img)

    fc = _parse_color(fill_color)
    alpha = int(255 * bg_opacity / 100)
    fc = fc[:3] + (alpha,)

    bc = _parse_color(border_color) if border_width > 0 else None
    bw = border_width if border_width > 0 else 0

    if shape == "circle":
        if bw > 0:
            draw.ellipse([0, 0, w - 1, h - 1], fill=fc, outline=bc, width=bw)
        else:
            draw.ellipse([0, 0, w - 1, h - 1], fill=fc)
    elif shape == "rounded":
        r = min(w, h) // 4
        if bw > 0:
            draw.rounded_rectangle(
                [0, 0, w - 1, h - 1], radius=r, fill=fc, outline=bc, width=bw
            )
        else:
            draw.rounded_rectangle([0, 0, w - 1, h - 1], radius=r, fill=fc)
    else:
        if bw > 0:
            draw.rectangle([0, 0, w - 1, h - 1], fill=fc, outline=bc, width=bw)
        else:
            draw.rectangle([0, 0, w - 1, h - 1], fill=fc)

    target.paste(frame_img, (x, y), frame_img)


def _draw_clear_zone(
    target: Image.Image,
    w: int, h: int,
    x: int, y: int,
    qr_image: Image.Image,
) -> None:
    """Clear the area behind the logo with the QR bg color."""
    bg_sample = qr_image.getpixel((0, 0))
    if isinstance(bg_sample, int):
        bg_sample = (bg_sample, bg_sample, bg_sample, 255)
    elif len(bg_sample) == 3:
        bg_sample = bg_sample + (255,)
    clear = Image.new("RGBA", (w, h), bg_sample)
    target.paste(clear, (x, y), clear)


def _draw_text(
    target: Image.Image,
    text: str,
    center_x: int,
    top_y: int,
    color: str,
    font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
) -> None:
    """Draw centered text below the logo."""
    draw = ImageDraw.Draw(target)
    tc = _parse_color(color)
    bbox = font.getbbox(text)
    tw = bbox[2] - bbox[0]
    tx = center_x - tw // 2
    draw.text((tx, top_y), text, fill=tc, font=font)


def _get_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Load a TrueType font, falling back to the default bitmap font."""
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
        "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/arial.ttf",
    ]
    for path in font_paths:
        try:
            return ImageFont.truetype(path, size)
        except (IOError, OSError):
            continue
    try:
        return ImageFont.truetype("arial.ttf", size)
    except (IOError, OSError):
        return ImageFont.load_default()


def _parse_color(color_str: str) -> tuple[int, ...]:
    c = color_str.lstrip("#")
    if len(c) == 8:
        return tuple(
            int(c[i:i + 2], 16) for i in (0, 2, 4, 6)
        )
    if len(c) == 6:
        return tuple(
            int(c[i:i + 2], 16) for i in (0, 2, 4)
        ) + (255,)
    return (255, 255, 255, 255)

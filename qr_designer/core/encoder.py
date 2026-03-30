"""Content encoders for various QR code data types."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime


class ContentEncoder(ABC):
    @abstractmethod
    def encode(self, **kwargs: object) -> str: ...


class URLEncoder(ContentEncoder):
    def encode(self, *, url: str, **_: object) -> str:
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        return url


class PlainTextEncoder(ContentEncoder):
    def encode(self, *, text: str, **_: object) -> str:
        return text


class VCardEncoder(ContentEncoder):
    def encode(
        self,
        *,
        first_name: str = "",
        last_name: str = "",
        org: str = "",
        title: str = "",
        phone: str = "",
        email: str = "",
        url: str = "",
        address: str = "",
        **_: object,
    ) -> str:
        lines = [
            "BEGIN:VCARD",
            "VERSION:3.0",
            f"N:{last_name};{first_name};;;",
            f"FN:{first_name} {last_name}".strip(),
        ]
        if org:
            lines.append(f"ORG:{org}")
        if title:
            lines.append(f"TITLE:{title}")
        if phone:
            lines.append(f"TEL:{phone}")
        if email:
            lines.append(f"EMAIL:{email}")
        if url:
            lines.append(f"URL:{url}")
        if address:
            lines.append(f"ADR:{address}")
        lines.append("END:VCARD")
        return "\r\n".join(lines)


class WiFiEncoder(ContentEncoder):
    def encode(
        self,
        *,
        ssid: str,
        password: str = "",
        encryption: str = "WPA",
        hidden: bool = False,
        **_: object,
    ) -> str:
        hidden_str = "true" if hidden else "false"
        return f"WIFI:T:{encryption};S:{ssid};P:{password};H:{hidden_str};;"


class CalendarEventEncoder(ContentEncoder):
    def encode(
        self,
        *,
        summary: str,
        start: str,
        end: str = "",
        location: str = "",
        description: str = "",
        **_: object,
    ) -> str:
        def _fmt(dt_str: str) -> str:
            try:
                dt = datetime.fromisoformat(dt_str)
                return dt.strftime("%Y%m%dT%H%M%S")
            except ValueError:
                return dt_str

        lines = [
            "BEGIN:VEVENT",
            f"SUMMARY:{summary}",
            f"DTSTART:{_fmt(start)}",
        ]
        if end:
            lines.append(f"DTEND:{_fmt(end)}")
        if location:
            lines.append(f"LOCATION:{location}")
        if description:
            lines.append(f"DESCRIPTION:{description}")
        lines.append("END:VEVENT")
        return "\r\n".join(lines)


class PaymentLinkEncoder(ContentEncoder):
    """Encodes payment URIs (e.g. Bitcoin, UPI, or generic payment URLs)."""

    def encode(self, *, url: str, **_: object) -> str:
        return url


class AppDeepLinkEncoder(ContentEncoder):
    """Encodes app deep links (custom URI schemes or universal links)."""

    def encode(self, *, url: str, **_: object) -> str:
        return url


ENCODERS: dict[str, ContentEncoder] = {
    "url": URLEncoder(),
    "text": PlainTextEncoder(),
    "vcard": VCardEncoder(),
    "wifi": WiFiEncoder(),
    "calendar": CalendarEventEncoder(),
    "payment": PaymentLinkEncoder(),
    "deeplink": AppDeepLinkEncoder(),
}


def encode_content(content_type: str, **kwargs: object) -> str:
    encoder = ENCODERS.get(content_type)
    if encoder is None:
        raise ValueError(f"Unknown content type: {content_type}")
    return encoder.encode(**kwargs)

"""Resolve the browser-facing workbook origin for an API request.

The TLS frontend serves the workbook from a dedicated ``:8443`` origin so the
framed wiki keeps its own storage without being able to read the SPA's token.
When the admin has not set ``wiki_origin``, nginx announces that split with
``X-OCR-Wiki-Split-Origin``. A fresh HTTPS deployment therefore gets the split
without an operator remembering the setting. HTTP-only deployments (dev mode,
or a TLS-terminating tunnel with no 8443 route) send no header and keep the
same-origin fallback.

The header is trusted only when it is an https origin on the documented wiki
port whose hostname matches the request host; a client-supplied value cannot
point the frame at another site.
"""

from __future__ import annotations

from urllib.parse import urlsplit

SPLIT_ORIGIN_HEADER = "x-ocr-wiki-split-origin"
WIKI_ORIGIN_PORT = 8443


def _first_header(request, name: str) -> str:
    value = request.headers.get(name) or ""
    return value.split(",")[0].strip()


def _request_host(request) -> str:
    return _first_header(request, "x-forwarded-host") or _first_header(request, "host")


def _request_scheme(request) -> str:
    forwarded = _first_header(request, "x-forwarded-proto")
    return forwarded or (request.url.scheme or "").lower()


def normalize_origin(value: str) -> str:
    """Return a canonical https origin, or '' when the value is not one."""
    raw = (value or "").strip()
    if not raw:
        return ""
    try:
        parsed = urlsplit(raw)
        port = parsed.port
    except ValueError:
        return ""
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.username
        or parsed.password
        or parsed.path not in ("", "/")
        or parsed.query
        or parsed.fragment
    ):
        return ""
    host = parsed.hostname
    if ":" in host:  # IPv6 literal
        host = f"[{host}]"
    netloc = host if port in (None, 443) else f"{host}:{port}"
    return f"https://{netloc}"


def split_origin(request) -> str:
    """The nginx-declared workbook origin, when it belongs to this host."""
    if _request_scheme(request) != "https":
        return ""
    origin = normalize_origin(_first_header(request, SPLIT_ORIGIN_HEADER))
    if not origin:
        return ""
    parsed = urlsplit(origin)
    host_header = _request_host(request)
    if not host_header:
        return ""
    try:
        request_hostname = urlsplit(f"//{host_header}").hostname
    except ValueError:
        return ""
    if parsed.port != WIKI_ORIGIN_PORT or parsed.hostname != request_hostname:
        return ""
    return origin


def app_origin(request) -> str:
    """The browser-facing SPA origin for this request, when it is HTTPS."""
    if _request_scheme(request) != "https":
        return ""
    host = _request_host(request)
    if not host:
        return ""
    return normalize_origin(f"https://{host}")

"""Public community calendar ingestion.

The SWOCTS Hub publishes a public Google Calendar. The platform shows those
events beside its own competitions so learners get one calendar. The feed is
public, unauthenticated, and read-only; nothing here writes to the source.

The calendar is fetched server-side for three reasons: the browser avoids a
third-party origin and its CSP, one process can cache the feed for every
visitor, and a network failure degrades to the cached copy instead of an empty
page.
"""

from __future__ import annotations

import html
import ipaddress
import logging
import os
import re
import threading
import time
from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qsl, quote, urlencode, urlsplit, urlunsplit
from zoneinfo import ZoneInfo

import requests
from dateutil import rrule

logger = logging.getLogger(__name__)

SWOCTS_CALENDAR_ID = os.environ.get(
    "OCR_SWOCTS_CALENDAR_ID",
    "dcf7ff998803e31e8f5c679f57807d35ef54e763391071aa3a0fe28b48082035"
    "@group.calendar.google.com",
)
SWOCTS_CALENDAR_URL = "https://www.swocts.com/calendar"
SWOCTS_EVENTS_URL = "https://www.swocts.com/events"
SWOCTS_SOURCE_NAME = "SWOCTS Hub"
SWOCTS_ICS_URL = (
    "https://calendar.google.com/calendar/ical/"
    f"{quote(SWOCTS_CALENDAR_ID, safe='')}/public/basic.ics"
)

CACHE_SECONDS = 15 * 60
FAILURE_BACKOFF_SECONDS = 60
STALE_MAX_SECONDS = 24 * 60 * 60
PAST_WINDOW_DAYS = 45
FUTURE_WINDOW_DAYS = 730
REQUEST_TIMEOUT = 15
MAX_FEED_BYTES = 5 * 1024 * 1024
MAX_EVENTS = 1500
MAX_OCCURRENCES_PER_EVENT = 250
ALLOWED_FREQUENCIES = {"DAILY", "WEEKLY", "MONTHLY", "YEARLY"}
TITLE_LIMIT = 200
LOCATION_LIMIT = 300
URL_LIMIT = 2000

# Calendar descriptions and locations often contain the only usable event
# link. Prefer recognised event platforms over arbitrary links (tracking
# pixels, social profiles) when a description contains more than one URL.
PREFERRED_EVENT_HOSTS = tuple(
    host.strip().lower()
    for host in os.environ.get(
        "OCR_COMMUNITY_EVENT_HOSTS",
        "eventbrite.ca,eventbrite.com,eventbrite.co.uk,eventbrite.ie,"
        "gdg.community.dev,discord.gg,swocts.com",
    ).split(",")
    if host.strip()
)
TRACKING_QUERY_KEYS = {
    "aff",
    "fbclid",
    "gclid",
    "igshid",
    "mc_cid",
    "mc_eid",
    "ref",
}
_URL_RE = re.compile(r"https?://[^\s<>\"']+", re.IGNORECASE)
_CONTROL_RE = re.compile(r"[\x00-\x1f\x7f]")

_CACHE: dict = {"at": 0.0, "failure_at": 0.0, "payload": None}
_CACHE_LOCK = threading.Lock()

_TAG = re.compile(r"<[^>]+>")
_SPACE = re.compile(r"\s+")
DESCRIPTION_LIMIT = 600


def source_payload() -> dict:
    return {
        "key": "swocts-hub",
        "name": SWOCTS_SOURCE_NAME,
        "url": SWOCTS_EVENTS_URL,
        "calendar_url": SWOCTS_CALENDAR_URL,
        "location": "Southwestern Ontario",
    }


def get_community_events(force: bool = False) -> dict:
    """Return normalized SWOCTS Hub events, using a short in-process cache."""
    now = time.monotonic()
    with _CACHE_LOCK:
        cached = _CACHE["payload"]
        if cached and not force and now - _CACHE["at"] < CACHE_SECONDS:
            return {**cached, "cached": True, "stale": False}
        if (
            not force
            and _CACHE["failure_at"]
            and now - _CACHE["failure_at"] < FAILURE_BACKOFF_SECONDS
        ):
            return _unavailable()
        try:
            text = _download_ics()
            events = parse_ics(text)
            payload = {
                "events": events,
                "source": source_payload(),
                "available": True,
                "fetched_at": datetime.now(timezone.utc).isoformat(),
                "cached": False,
                "stale": False,
            }
            _CACHE["payload"] = payload
            _CACHE["at"] = now
            _CACHE["failure_at"] = 0.0
            return payload
        except Exception as exc:  # noqa: BLE001 - the page must still render
            logger.warning("SWOCTS calendar fetch failed: %s", exc)
            _CACHE["failure_at"] = now
            if cached and now - _CACHE["at"] <= STALE_MAX_SECONDS:
                return {**cached, "cached": True, "stale": True}
            return _unavailable()


def _unavailable() -> dict:
    return {
        "events": [],
        "source": source_payload(),
        "available": False,
        "fetched_at": None,
        "cached": False,
        "stale": False,
        "error": "The community calendar is temporarily unavailable.",
    }


def _download_ics() -> str:
    chunks: list[bytes] = []
    size = 0
    with requests.get(
        SWOCTS_ICS_URL,
        timeout=REQUEST_TIMEOUT,
        headers={"User-Agent": "OpenCyberRange community calendar/1.0"},
        stream=True,
    ) as response:
        response.raise_for_status()
        for chunk in response.iter_content(chunk_size=65536):
            size += len(chunk)
            if size > MAX_FEED_BYTES:
                raise ValueError("The community calendar feed is too large")
            chunks.append(chunk)
    text = b"".join(chunks).decode("utf-8", errors="replace").lstrip("\ufeff")
    if "BEGIN:VCALENDAR" not in text or "BEGIN:VEVENT" not in text:
        raise ValueError("The calendar response was not an iCalendar feed")
    return text


def _unfold(text: str) -> list[str]:
    lines: list[str] = []
    for raw in text.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
        if raw.startswith((" ", "\t")) and lines:
            lines[-1] += raw[1:]
        else:
            lines.append(raw)
    return lines


def _split_property(line: str) -> tuple[str, dict[str, str], str] | None:
    left, separator, value = line.partition(":")
    if not separator:
        return None
    parts = left.split(";")
    name = parts[0].strip().upper()
    params: dict[str, str] = {}
    for part in parts[1:]:
        key, _, raw = part.partition("=")
        params[key.strip().upper()] = raw.strip().strip('"')
    return name, params, value


def _text(value: str) -> str:
    value = re.sub(r"\\[nN]", "\n", value)
    value = value.replace("\\,", ",").replace("\\;", ";").replace("\\\\", "\\")
    value = html.unescape(value)
    if "<" in value and ">" in value:
        value = _TAG.sub(" ", value)
    return _SPACE.sub(" ", value).strip()


def _shorten(value: str, limit: int = DESCRIPTION_LIMIT) -> str:
    if len(value) <= limit:
        return value
    clipped = value[:limit].rsplit(" ", 1)[0].rstrip(" ,.;:")
    return f"{clipped}…"


def _zone(name: str | None):
    if not name:
        return timezone.utc
    try:
        return ZoneInfo(name)
    except Exception:  # noqa: BLE001 - a bad TZID must not drop the event
        return timezone.utc


def _parse_datetime(value: str, params: dict[str, str], default_zone):
    value = value.strip()
    if params.get("VALUE", "").upper() == "DATE" or re.fullmatch(r"\d{8}", value):
        return datetime.strptime(value, "%Y%m%d").replace(tzinfo=default_zone), True
    if value.endswith("Z"):
        return datetime.strptime(value, "%Y%m%dT%H%M%SZ").replace(
            tzinfo=timezone.utc
        ), False
    zone = _zone(params.get("TZID")) if params.get("TZID") else default_zone
    return datetime.strptime(value, "%Y%m%dT%H%M%S").replace(tzinfo=zone), False


def _event_id(uid: str, start: datetime, title: str) -> str:
    base = uid or re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return f"{base}:{start.date().isoformat()}"


def parse_ics(
    text: str,
    *,
    now: datetime | None = None,
) -> list[dict]:
    """Parse the public feed and expand recurrences inside a bounded window."""
    now = now or datetime.now(timezone.utc)
    lines = _unfold(text)
    calendar_zone = timezone.utc
    for line in lines:
        if line.upper().startswith("X-WR-TIMEZONE:"):
            calendar_zone = _zone(line.split(":", 1)[1].strip())
            break

    window_start = now - timedelta(days=PAST_WINDOW_DAYS)
    window_end = now + timedelta(days=FUTURE_WINDOW_DAYS)

    events: dict[str, dict] = {}
    current: dict[str, tuple[dict[str, str], str]] | None = None
    for line in lines:
        upper = line.upper()
        if upper == "BEGIN:VEVENT":
            current = {}
            continue
        if upper == "END:VEVENT":
            if current is not None:
                try:
                    _add_event(events, current, calendar_zone, window_start, window_end)
                except Exception as exc:  # noqa: BLE001 - skip one bad event
                    logger.debug("Skipped a malformed calendar event: %s", exc)
            current = None
            continue
        if len(events) >= MAX_EVENTS:
            break
        if current is None:
            continue
        parsed = _split_property(line)
        if parsed:
            name, params, value = parsed
            current[name] = (params, value)

    return sorted(events.values(), key=lambda item: (item["start"], item["title"]))


def _host_is_public(host: str) -> bool:
    """Reject loopback, private, link-local, and internal hostnames."""
    host = (host or "").strip().lower().rstrip(".")
    if not host:
        return False
    try:
        address = ipaddress.ip_address(host)
        return not (
            address.is_private
            or address.is_loopback
            or address.is_link_local
            or address.is_multicast
            or address.is_reserved
            or address.is_unspecified
        )
    except ValueError:
        pass
    return host not in {"localhost", "localhost.localdomain"} and not host.endswith(
        (".local", ".internal", ".localhost", ".home.arpa")
    )


def _sanitize_event_url(value: str) -> str | None:
    """Return a safe public https event URL, or None.

    The calendar is editor-controlled input. Reject plaintext HTTP,
    credentials, control characters, private destinations, and tracking
    parameters before a URL is shown to a learner. This also keeps the link the
    browser sees identical to the link the server validated.
    """
    raw = (value or "").strip().strip("<>\"'")
    if not raw or len(raw) > URL_LIMIT:
        return None
    if _CONTROL_RE.search(raw) or "\\" in raw:
        return None
    try:
        parts = urlsplit(raw)
    except ValueError:
        return None
    if parts.scheme.lower() != "https":
        return None
    if not parts.netloc or not parts.hostname:
        return None
    if parts.username or parts.password:
        return None
    if not _host_is_public(parts.hostname):
        return None
    query = urlencode(
        [
            (key, item)
            for key, item in parse_qsl(parts.query, keep_blank_values=True)
            if key.lower() not in TRACKING_QUERY_KEYS
            and not key.lower().startswith("utm_")
        ],
        doseq=True,
    )
    return urlunsplit(
        (
            parts.scheme.lower(),
            parts.netloc.lower(),
            parts.path or "/",
            query,
            parts.fragment,
        )
    )


def _urls_in_text(value: str) -> list[str]:
    """Extract public http(s) URLs from free-form calendar text."""
    text = html.unescape(value or "")
    urls: list[str] = []
    for match in _URL_RE.finditer(text):
        candidate = match.group(0).rstrip(").,;:!?]}\"'")
        safe = _sanitize_event_url(candidate)
        if safe and safe not in urls:
            urls.append(safe)
    return urls


def _is_preferred_event_host(url: str) -> bool:
    host = (urlsplit(url).hostname or "").lower()
    return any(
        host == allowed or host.endswith("." + allowed)
        for allowed in PREFERRED_EVENT_HOSTS
    )


def _choose_event_url(*candidates: str) -> str | None:
    """Pick a preferred event-platform URL, then any other safe public URL."""
    extracted: list[str] = []
    for candidate in candidates:
        extracted.extend(_urls_in_text(candidate))
    for url in extracted:
        if _is_preferred_event_host(url):
            return url
    return extracted[0] if extracted else None


def _add_event(
    events: dict[str, dict],
    data: dict[str, tuple[dict[str, str], str]],
    calendar_zone,
    window_start: datetime,
    window_end: datetime,
) -> None:
    start_raw = data.get("DTSTART")
    if not start_raw:
        return
    start, all_day = _parse_datetime(start_raw[1], start_raw[0], calendar_zone)

    end = start
    end_raw = data.get("DTEND")
    if end_raw:
        end, end_all_day = _parse_datetime(end_raw[1], end_raw[0], calendar_zone)
        if all_day and end_all_day:
            end -= timedelta(days=1)
    if end < start:
        end = start
    duration = end - start

    title = _shorten(
        _text(data.get("SUMMARY", ({}, "Community event"))[1]),
        TITLE_LIMIT,
    ) or "Community event"
    uid = _text(data.get("UID", ({}, ""))[1])
    raw_location = data.get("LOCATION", ({}, ""))[1]
    location = _shorten(_text(raw_location), LOCATION_LIMIT) or "Southwestern Ontario"
    raw_description = data.get("DESCRIPTION", ({}, ""))[1]
    description = _shorten(_text(raw_description))

    # Google Calendar commonly leaves URL empty and puts the event link in
    # LOCATION or DESCRIPTION. Extract and validate a safe public link so a
    # learner reaches the advertised event instead of the generic calendar.
    url = _choose_event_url(
        _text(data.get("URL", ({}, ""))[1]),
        raw_location,
        raw_description,
    ) or SWOCTS_CALENDAR_URL

    occurrences: list[datetime] = []
    rule_raw = data.get("RRULE")
    if rule_raw:
        frequency = next(
            (
                part.split("=", 1)[1].upper()
                for part in rule_raw[1].split(";")
                if part.upper().startswith("FREQ=")
            ),
            "",
        )
        if frequency in ALLOWED_FREQUENCIES:
            try:
                rule = rrule.rrulestr(f"RRULE:{rule_raw[1]}", dtstart=start)
                occurrences = list(
                    rule.between(window_start, window_end, inc=True)
                )[:MAX_OCCURRENCES_PER_EVENT]
            except Exception:  # noqa: BLE001 - keep the first occurrence
                occurrences = [start] if window_start <= start <= window_end else []
        else:
            occurrences = [start] if window_start <= start <= window_end else []
    elif window_start <= start <= window_end:
        occurrences = [start]

    if not occurrences:
        return

    excluded = set()
    exdate = data.get("EXDATE")
    if exdate:
        params, value = exdate
        for raw in value.split(","):
            try:
                candidate, _ = _parse_datetime(raw.strip(), params, calendar_zone)
                excluded.add(candidate)
            except ValueError:
                continue

    for occurrence in occurrences:
        if occurrence in excluded:
            continue
        if len(events) >= MAX_EVENTS:
            break
        occurrence_end = occurrence + duration
        event_id = _event_id(uid, occurrence, title)
        events[event_id] = {
            "id": event_id,
            "title": title,
            "start": occurrence.isoformat(),
            "end": occurrence_end.isoformat(),
            "all_day": all_day,
            "location": location,
            "description": description,
            "url": url,
            "source": SWOCTS_SOURCE_NAME,
            "source_key": "swocts-hub",
            "calendar_url": SWOCTS_CALENDAR_URL,
            "free": True,
        }

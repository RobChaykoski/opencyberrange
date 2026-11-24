"""Synthetic canary console for the Noise in the Nest lab.

The service records token hits in memory and shows the request metadata the
learner needs for triage. It does not identify people, store secrets, or call
an external service. Everything runs inside the isolated lab network.
"""

from __future__ import annotations

import html
import json
import threading
from datetime import UTC, datetime, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

FLAG = "OCR{c4n4ry_n0ise_tru3}"
CANARY_LABEL = "incident-timeline"
MAX_EVENTS = 200
BOT_MARKERS = (
    "bot",
    "crawler",
    "spider",
    "scanner",
    "nuclei",
    "uptime",
    "monitor",
    "curl/",
    "wget/",
    "python-requests",
)

_EVENTS: list[dict] = []
_LOCK = threading.Lock()

PIXEL = (
    b"GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!"
    b"\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00"
    b"\x00\x02\x02D\x01\x00;"
)


def _iso(value: datetime) -> str:
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z")


def _seed_events() -> None:
    now = datetime.now(UTC)
    seeds = (
        {
            "token": CANARY_LABEL,
            "source": "10.20.0.50",
            "user_agent": (
                "Mozilla/5.0 (compatible; LinkPreviewBot/1.0; "
                "+https://chat.example/bot)"
            ),
            "referer": "https://chat.example/",
            "fetch_mode": "",
            "fetch_dest": "",
            "accept_language": "en",
            "classification": "link preview",
            "created": now - timedelta(minutes=18),
        },
        {
            "token": CANARY_LABEL,
            "source": "10.20.0.51",
            "user_agent": (
                "Mozilla/5.0 (compatible; Nuclei - Open-source project; "
                "https://nuclei.projectdiscovery.io)"
            ),
            "referer": "",
            "fetch_mode": "",
            "fetch_dest": "",
            "accept_language": "en",
            "classification": "scanner",
            "created": now - timedelta(minutes=9),
        },
        {
            "token": CANARY_LABEL,
            "source": "10.20.0.52",
            "user_agent": "UptimeMonitor/2.0 (+https://monitor.example/)",
            "referer": "",
            "fetch_mode": "",
            "fetch_dest": "",
            "accept_language": "en",
            "classification": "uptime monitor",
            "created": now - timedelta(minutes=3),
        },
    )
    _EVENTS.extend(seeds)


def _browser_candidate(user_agent: str, fetch_mode: str) -> bool:
    agent = (user_agent or "").lower()
    if fetch_mode.strip().lower() != "navigate":
        return False
    if "mozilla/5.0" not in agent:
        return False
    return not any(marker in agent for marker in BOT_MARKERS)


def _record(token: str, headers, source: str) -> dict:
    user_agent = headers.get("User-Agent", "")
    fetch_mode = headers.get("Sec-Fetch-Mode", "")
    event = {
        "token": token,
        "source": source,
        "user_agent": user_agent,
        "referer": headers.get("Referer", ""),
        "fetch_mode": fetch_mode,
        "fetch_dest": headers.get("Sec-Fetch-Dest", ""),
        "accept_language": headers.get("Accept-Language", ""),
        "classification": (
            "browser-class candidate"
            if _browser_candidate(user_agent, fetch_mode)
            else "automated or unknown"
        ),
        "human_candidate": _browser_candidate(user_agent, fetch_mode),
        "created": datetime.now(UTC),
    }
    with _LOCK:
        _EVENTS.append(event)
        if len(_EVENTS) > MAX_EVENTS:
            del _EVENTS[: len(_EVENTS) - MAX_EVENTS]
    return event


def _snapshot() -> list[dict]:
    with _LOCK:
        return list(reversed(_EVENTS[-MAX_EVENTS:]))


def _unlocked(events: list[dict]) -> bool:
    return any(event.get("human_candidate") for event in events)


def _payload(events: list[dict]) -> dict:
    return {
        "token": CANARY_LABEL,
        "flag": FLAG if _unlocked(events) else None,
        "events": [
            {**event, "created": _iso(event["created"])} for event in events
        ],
    }


def _console_html(events: list[dict]) -> str:
    unlocked = _unlocked(events)
    rows = []
    for event in events:
        rows.append(
            "<tr>"
            f"<td>{html.escape(_iso(event['created']))}</td>"
            f"<td>{html.escape(event['token'])}</td>"
            f"<td>{html.escape(event['classification'])}</td>"
            f"<td>{html.escape(event['source'])}</td>"
            f"<td class=\"ua\">{html.escape(event['user_agent'])}</td>"
            f"<td class=\"ua\">{html.escape(event['referer'])}</td>"
            f"<td>{html.escape(event['fetch_mode'])}</td>"
            f"<td>{html.escape(event['fetch_dest'])}</td>"
            "</tr>"
        )
    flag_box = (
        f"<div class='flag'><strong>Browser-class hit observed.</strong>"
        f"<p>Lab flag: <code>{html.escape(FLAG)}</code></p></div>"
        if unlocked
        else (
            "<div class='flag flag--locked'><strong>No browser-class hit yet.</strong>"
            "<p>Open the incident timeline link from <code>http://portal.lab/</code>"
            " in the lab browser, then reload this console.</p></div>"
        )
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Northwind Freight - Canary Console</title>
  <style>
    body {{ font-family: system-ui, -apple-system, Segoe UI, sans-serif; margin: 0; background: #0f172a; color: #e2e8f0; }}
    main {{ max-width: 1180px; margin: 2rem auto; padding: 0 1rem 3rem; }}
    h1 {{ margin: 0 0 .25rem; font-size: 1.7rem; }}
    .meta {{ color: #94a3b8; margin-bottom: 1.5rem; }}
    .flag {{ border: 1px solid #22c55e; background: #052e1a; padding: 1rem 1.25rem; border-radius: .6rem; margin: 1.25rem 0; }}
    .flag--locked {{ border-color: #f59e0b; background: #2a1d04; }}
    .flag p {{ margin: .4rem 0 0; }}
    code {{ background: #1e293b; padding: .15rem .35rem; border-radius: .25rem; }}
    table {{ width: 100%; border-collapse: collapse; background: #111c33; border-radius: .6rem; overflow: hidden; }}
    th, td {{ text-align: left; padding: .65rem .7rem; border-bottom: 1px solid #243352; vertical-align: top; font-size: .82rem; }}
    th {{ background: #16233d; color: #cbd5e1; }}
    .ua {{ max-width: 280px; word-break: break-word; }}
    .note {{ color: #94a3b8; font-size: .9rem; margin-top: 1rem; }}
  </style>
</head>
<body>
  <main>
    <h1>Northwind Freight canary console</h1>
    <p class="meta">Token <code>{html.escape(CANARY_LABEL)}</code> &middot; in-memory synthetic events &middot; no external service</p>
    {flag_box}
    <table>
      <thead>
        <tr>
          <th>Time (UTC)</th><th>Token</th><th>Classification</th><th>Source</th>
          <th>User-Agent</th><th>Referer</th><th>Sec-Fetch-Mode</th><th>Sec-Fetch-Dest</th>
        </tr>
      </thead>
      <tbody>
        {''.join(rows)}
      </tbody>
    </table>
    <p class="note">
      A hit records access, not identity or intent. Compare the user agent,
      referer, and fetch headers before escalating. Link-preview bots, scanners,
      and uptime monitors are common noise.
    </p>
  </main>
</body>
</html>"""


class Handler(BaseHTTPRequestHandler):
    server_version = "NorthwindCanary/1.0"

    def _send(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path
        headers = self.headers

        if path == "/health":
            self._send(200, b'{"status":"ok"}', "application/json")
            return

        if path in ("/", "/console", "/console/"):
            events = _snapshot()
            self._send(
                200,
                _console_html(events).encode(),
                "text/html; charset=utf-8",
            )
            return

        if path == "/console/api/events":
            events = _snapshot()
            body = json.dumps(_payload(events), indent=2).encode()
            self._send(200, body, "application/json")
            return

        if path.startswith("/t/"):
            token = path.removeprefix("/t/") or "unknown"
            event = _record(token, headers, self.client_address[0])
            query = parse_qs(parsed.query)
            wants_pixel = path.endswith(".gif") or query.get("img", ["0"])[0] == "1"
            if wants_pixel:
                self._send(200, PIXEL, "image/gif")
            else:
                body = (
                    "<!DOCTYPE html><html lang='en'><head><meta charset='utf-8'>"
                    "<title>Document withdrawn</title></head><body>"
                    "<h1>This document is no longer available</h1>"
                    "<p>The publisher has withdrawn this file. Contact the "
                    "communications desk for an accessible copy.</p>"
                    f"<p>Token: {html.escape(event['token'])}</p>"
                    "</body></html>"
                ).encode()
                self._send(200, body, "text/html; charset=utf-8")
            return

        self._send(404, b"Not found", "text/plain; charset=utf-8")

    def log_message(self, format: str, *args) -> None:
        return


def main() -> None:
    _seed_events()
    server = ThreadingHTTPServer(("0.0.0.0", 80), Handler)
    server.daemon_threads = True
    server.serve_forever()


if __name__ == "__main__":
    main()

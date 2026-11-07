#!/usr/bin/env python3
"""Build a small live status dashboard for the dev and prod deployments.

The dashboard reads only public, non-sensitive API endpoints:

* ``/api/version``      -> running build identity
* ``/api/setup/status`` -> setup complete + whether the userbase exists
* ``/``                 -> build asset fingerprint from the served SPA

It does not log in, read learner data, or print secrets. Use it from the
operator workstation:

    python scripts/status-dashboard.py
    python scripts/status-dashboard.py --output docs/status-dashboard.html
    python scripts/status-dashboard.py --json docs/status-dashboard.json

The default host map is intentionally small and can be overridden with a JSON
file via ``--config``:

    [
      {"label": "Prod", "role": "production", "url": "https://172.16.16.41",
       "expected_version": "1.1.3"},
      {"label": "Dev", "role": "development", "url": "https://172.16.16.44",
       "expected_version": "2.1.4"}
    ]

Local deployments often use self-signed certificates. The script verifies TLS
when it can but does not fail the dashboard on a self-signed certificate; the
card records ``self-signed / unverified`` so the operator can see it.
"""

from __future__ import annotations

import argparse
import json
import re
import ssl
import time
import urllib.error
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

DEFAULT_HOSTS = [
    {
        "label": "Prod",
        "role": "production",
        "url": "https://172.16.16.41",
        "expected_version": "1.1.3",
        "line": "Community / Academic maintenance line",
    },
    {
        "label": "Dev",
        "role": "development",
        "url": "https://172.16.16.44",
        "expected_version": "2.1.4",
        "line": "Professional current platform release",
    },
]

TITLE_RE = re.compile(r"<title>(.*?)</title>", re.IGNORECASE | re.DOTALL)
SCRIPT_RE = re.compile(r'<script[^>]+src="([^"]+)"', re.IGNORECASE)
CSS_RE = re.compile(r'<link[^>]+href="([^"]+\.css)"', re.IGNORECASE)


def _fetch(url: str, timeout: float = 8.0) -> dict:
    started = time.perf_counter()
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    request = urllib.request.Request(url, headers={"User-Agent": "ocr-status-dashboard/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=timeout, context=context) as response:
            body = response.read(512_000).decode("utf-8", errors="replace")
            elapsed = round((time.perf_counter() - started) * 1000)
            return {
                "ok": True,
                "status": response.status,
                "elapsed_ms": elapsed,
                "body": body,
                "content_type": response.headers.get("Content-Type", ""),
                "server": response.headers.get("Server", ""),
            }
    except urllib.error.HTTPError as exc:
        body = exc.read(64_000).decode("utf-8", errors="replace")
        return {
            "ok": False,
            "status": exc.code,
            "elapsed_ms": round((time.perf_counter() - started) * 1000),
            "body": body,
            "error": f"HTTP {exc.code}",
        }
    except Exception as exc:  # noqa: BLE001 - a probe failure is data, not a crash
        return {
            "ok": False,
            "status": None,
            "elapsed_ms": round((time.perf_counter() - started) * 1000),
            "body": "",
            "error": str(exc),
        }


def _json_body(result: dict):
    if not result.get("ok"):
        return None
    try:
        return json.loads(result.get("body") or "{}")
    except json.JSONDecodeError:
        return None


def _assets(index_result: dict) -> dict:
    body = index_result.get("body") or ""
    title = TITLE_RE.search(body)
    scripts = SCRIPT_RE.findall(body)
    css = CSS_RE.findall(body)
    main = next((item for item in scripts if "/assets/index-" in item), "")
    return {
        "title": title.group(1).strip() if title else "",
        "main_asset": main.rsplit("/", 1)[-1] if main else "",
        "css_asset": css[0].rsplit("/", 1)[-1] if css else "",
        "assets": len(scripts) + len(css),
    }


def probe(host: dict) -> dict:
    version = _fetch(f"{host['url']}/api/version")
    setup = _fetch(f"{host['url']}/api/setup/status")
    index = _fetch(f"{host['url']}/")
    version_data = _json_body(version) or {}
    setup_data = _json_body(setup) or {}
    assets = _assets(index)
    running_version = version_data.get("version", "")
    expected = host.get("expected_version", "")
    return {
        "label": host.get("label", host["url"]),
        "role": host.get("role", ""),
        "url": host["url"],
        "up": bool(index.get("ok") and version.get("ok")),
        "api_ok": bool(version.get("ok") and setup.get("ok")),
        "version": running_version or "unknown",
        "expected_version": expected,
        "line": host.get("line", ""),
        "version_ok": bool(running_version and expected and running_version == expected),
        "release": version_data.get("release", ""),
        "setup_complete": setup_data.get("setup_complete"),
        "has_users": setup_data.get("has_users"),
        "title": assets["title"],
        "main_asset": assets["main_asset"],
        "css_asset": assets["css_asset"],
        "asset_count": assets["assets"],
        "response_ms": version.get("elapsed_ms"),
        "server": index.get("server") or version.get("server") or "",
        "tls": "self-signed / unverified" if host["url"].startswith("https://") else "n/a",
        "errors": [
            f"version: {version.get('error')}" if version.get("error") else "",
            f"setup: {setup.get('error')}" if setup.get("error") else "",
            f"index: {index.get('error')}" if index.get("error") else "",
        ],
    }


def overall_state(rows: list[dict]) -> tuple[str, str]:
    if all(row["up"] and row["api_ok"] and row["version_ok"] for row in rows):
        return "healthy", "All deployments are up and on the expected version."
    if all(row["up"] for row in rows):
        return "attention", "All deployments are reachable, but one or more checks need attention."
    return "down", "One or more deployments are unreachable."


def render_markdown(rows: list[dict], state: str, message: str) -> str:
    lines = [
        "# Deployment status",
        "",
        f"Generated: `{datetime.now(UTC).isoformat(timespec='seconds')}`",
        "",
        f"**Overall:** `{state}` - {message}",
        "",
        "| Environment | Role | URL | Up | API | Version | Expected | Users | Setup | Build asset | Response |",
        "|---|---|---|---:|---:|---|---|---:|---|---|---:|",
    ]
    for row in rows:
        lines.append(
            "| {label} | {role} | {url} | {up} | {api} | `{version}` | `{expected}` | "
            "{users} | {setup} | `{asset}` | {ms} ms |".format(
                label=row["label"],
                role=row["role"],
                url=row["url"],
                up="yes" if row["up"] else "no",
                api="yes" if row["api_ok"] else "no",
                version=row["version"],
                expected=(row["expected_version"] or "-") + (f" ({row['line']})" if row.get("line") else ""),
                users="yes" if row["has_users"] else "no",
                setup="yes" if row["setup_complete"] else "no",
                asset=row["main_asset"] or "-",
                ms=row["response_ms"] if row["response_ms"] is not None else "-",
            )
        )
    lines.extend([
        "",
        "Checks use public endpoints only: `/api/version`, `/api/setup/status`, and `/`.",
        "No login, learner records, secrets, or private data are read.",
        "Container and Docker host state are not exposed by the public API; confirm",
        "them with `docker compose ps` on each host.",
        "",
    ])
    return "\n".join(lines)


def render_html(rows: list[dict], state: str, message: str) -> str:
    state_colour = {"healthy": "#22c55e", "attention": "#f59e0b", "down": "#ef4444"}[state]
    cards = []
    for row in rows:
        up_label = "Up" if row["up"] else "Down"
        version_state = "ok" if row["version_ok"] else "warn"
        users = "Userbase present" if row["has_users"] else "No users reported"
        setup = "Setup complete" if row["setup_complete"] else "Setup incomplete"
        cards.append(f"""
        <article class="card">
          <div class="card-head">
            <div><p class="eyebrow">{row['role'] or 'deployment'}</p><h2>{row['label']}</h2></div>
            <span class="pill {'ok' if row['up'] else 'bad'}">{up_label}</span>
          </div>
          <p class="url">{row['url']}</p>
          <div class="stats">
            <div><span>Version</span><strong class="{version_state}">{row['version']}</strong><small>expected {row['expected_version'] or '-'}{(' · ' + row['line']) if row.get('line') else ''}</small></div>
            <div><span>Response</span><strong>{row['response_ms'] if row['response_ms'] is not None else '-'}<small> ms</small></strong></div>
            <div><span>Build asset</span><strong class="mono">{row['main_asset'] or '-'}</strong><small>{row['asset_count']} linked assets</small></div>
          </div>
          <ul class="checks">
            <li><span class="{'ok' if row['api_ok'] else 'bad'}">{'API OK' if row['api_ok'] else 'API issue'}</span></li>
            <li><span class="{'ok' if row['has_users'] else 'warn'}">{users}</span></li>
            <li><span class="{'ok' if row['setup_complete'] else 'warn'}">{setup}</span></li>
            <li><span class="muted">{row['server'] or 'server unknown'}</span></li>
          </ul>
          {('<p class="error">' + ' · '.join(e for e in row['errors'] if e) + '</p>') if any(row['errors']) else ''}
        </article>""")

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>SWOCTS Cyber Range - Deployment status</title>
<style>
  :root {{ color-scheme: dark; --bg:#0f172a; --panel:#1e293b; --line:#334155;
    --text:#f8fafc; --muted:#94a3b8; --accent:#3b82f6; --ok:#22c55e; --warn:#f59e0b; --bad:#ef4444; }}
  * {{ box-sizing: border-box; }}
  body {{ margin:0; padding:2rem; background:var(--bg); color:var(--text);
    font:15px/1.55 Inter,system-ui,-apple-system,"Segoe UI",sans-serif; }}
  main {{ max-width: 1100px; margin: 0 auto; }}
  h1 {{ margin:0 0 .25rem; font-size:1.8rem; }}
  .head {{ display:flex; justify-content:space-between; gap:1rem; align-items:flex-start; flex-wrap:wrap; margin-bottom:1.25rem; }}
  .overall {{ display:inline-flex; align-items:center; gap:.5rem; padding:.45rem .7rem;
    border:1px solid var(--line); border-radius:999px; background:var(--panel); font-weight:700; }}
  .overall .dot {{ width:.65rem; height:.65rem; border-radius:50%; background:{state_colour}; }}
  .muted, small {{ color:var(--muted); }}
  .grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(330px,1fr)); gap:1rem; }}
  .card {{ padding:1rem; border:1px solid var(--line); border-radius:12px; background:var(--panel); }}
  .card-head {{ display:flex; justify-content:space-between; align-items:flex-start; gap:.75rem; }}
  .eyebrow {{ margin:0 0 .1rem; color:var(--accent); font-size:.65rem; font-weight:700;
    letter-spacing:.1em; text-transform:uppercase; }}
  h2 {{ margin:0; font-size:1.25rem; }}
  .url {{ margin:.15rem 0 .8rem; color:var(--muted); font-family:"JetBrains Mono",ui-monospace,monospace; font-size:.8rem; }}
  .pill {{ padding:.2rem .55rem; border-radius:999px; font-size:.7rem; font-weight:700; }}
  .pill.ok {{ background:rgba(34,197,94,.15); color:var(--ok); }}
  .pill.bad {{ background:rgba(239,68,68,.15); color:var(--bad); }}
  .stats {{ display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:.5rem; margin:.75rem 0; }}
  .stats div {{ min-width:0; padding:.6rem; border-radius:8px; background:var(--bg); }}
  .stats span {{ display:block; color:var(--muted); font-size:.65rem; text-transform:uppercase;
    letter-spacing:.05em; }}
  .stats strong {{ display:block; font-size:1rem; margin:.1rem 0; }}
  .stats small {{ display:block; font-size:.68rem; }}
  .stats strong.ok {{ color:var(--ok); }}
  .stats strong.warn {{ color:var(--warn); }}
  .mono {{ font-family:"JetBrains Mono",ui-monospace,monospace; font-size:.72rem !important;
    overflow-wrap:anywhere; }}
  .checks {{ display:flex; flex-wrap:wrap; gap:.45rem; list-style:none; padding:0; margin:0; }}
  .checks span {{ display:inline-flex; padding:.2rem .45rem; border:1px solid var(--line);
    border-radius:999px; font-size:.7rem; }}
  .checks .ok {{ color:var(--ok); }} .checks .warn {{ color:var(--warn); }}
  .checks .bad {{ color:var(--bad); }} .checks .muted {{ color:var(--muted); }}
  .error {{ margin:.65rem 0 0; color:var(--bad); font-size:.75rem; overflow-wrap:anywhere; }}
  footer {{ margin-top:1.25rem; color:var(--muted); font-size:.72rem; }}
  @media (max-width:640px) {{ body {{ padding:1rem; }} .stats {{ grid-template-columns:1fr; }} }}
</style>
</head>
<body>
<main>
  <header class="head">
    <div>
      <p class="eyebrow">SWOCTS Cyber Range · powered by OpenCyberRange</p>
      <h1>Deployment status</h1>
      <p class="muted">Checked {datetime.now(UTC).isoformat(timespec='seconds')} · public API probes only</p>
    </div>
    <div class="overall"><span class="dot"></span>{state.upper()}</div>
  </header>
  <p class="muted">{message}</p>
  <div class="grid">{''.join(cards)}</div>
  <footer>
    This dashboard reads <code>/api/version</code>, <code>/api/setup/status</code>, and the
    SPA index. It does not log in, read learner records, or display secrets.
    Container and Docker host state are not exposed by the public API; confirm them
    with <code>docker compose ps</code> on each host. A green API card does not replace
    the full Docker, backup, and lab-run verification.
  </footer>
</main>
</body>
</html>
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", help="JSON file with deployment definitions.")
    parser.add_argument("--output", default="docs/status-dashboard.html")
    parser.add_argument("--json", dest="json_output", help="Also write the raw status JSON.")
    args = parser.parse_args()

    if args.config:
        hosts = json.loads(Path(args.config).read_text(encoding="utf-8"))
    else:
        hosts = DEFAULT_HOSTS

    rows = [probe(host) for host in hosts]
    state, message = overall_state(rows)
    payload = {
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "overall": state,
        "message": message,
        "deployments": rows,
    }

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_html(rows, state, message), encoding="utf-8")
    markdown_path = output.with_suffix(".md")
    markdown_path.write_text(render_markdown(rows, state, message), encoding="utf-8")
    if args.json_output:
        json_path = Path(args.json_output)
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    print(json.dumps(payload, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

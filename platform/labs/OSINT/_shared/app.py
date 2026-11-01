#!/usr/bin/env python3
"""Kestrel Connect - a small, safe OSINT training target.

The service is deliberately dependency-free and self-contained. Each OSINT
lab selects a mode with LAB_MODE and supplies its own FLAG:

    public_profile  - robots.txt points at a "restricted" notes page whose HTML
                      source contains the flag.
    image_intel     - the profile badge image carries a flag in its blue-channel
                      least-significant bits.
    code_intel      - /static/app.js contains a leftover developer comment with
                      the flag.

Nothing here reaches the internet, calls a real service, or stores state.
"""
import html
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

MODE = os.environ.get("LAB_MODE", "public_profile")
FLAG = os.environ.get("FLAG", "OCR{osint_flag_not_set}")
COMPANY = os.environ.get("COMPANY", "Kestrel Ridge")
PORT = int(os.environ.get("PORT", "8080"))

HERE = Path(__file__).resolve().parent
ASSETS = HERE / "assets"
TOOLS = HERE / "tools"

PEOPLE = [
    {
        "slug": "dana.whitfield",
        "name": "Dana Whitfield",
        "role": "Threat Intelligence Analyst",
        "team": "Fusion Center",
        "location": "Building C / Remote",
        "initials": "DW",
        "badge": "KR-0421",
        "bio": (
            "Dana correlates vendor advisories, incident notes, and public "
            "reporting into the weekly threat picture. She joined Kestrel Ridge "
            "after six years in a regional SOC and still keeps a paper notebook."
        ),
        "kudos": [
            "Spotted the supplier-phishing wave before it reached the help desk.",
            "Rebuilt the weekly intelligence brief after the tooling outage.",
            "Walked the new analysts through the badge-photo archive.",
        ],
    },
    {
        "slug": "marcus.lee",
        "name": "Marcus Lee",
        "role": "Detection Engineer",
        "team": "Fusion Center",
        "location": "Building A",
        "initials": "ML",
        "badge": "KR-0318",
        "bio": "Turns incident findings into detections that survive the next quarter.",
        "kudos": ["Cut the noisy DNS alert volume by half."],
    },
    {
        "slug": "priya.nair",
        "name": "Priya Nair",
        "role": "Security Awareness Lead",
        "team": "People Security",
        "location": "Building B",
        "initials": "PN",
        "badge": "KR-0287",
        "bio": "Runs the phishing simulations and writes the plain-language recaps.",
        "kudos": ["Made the quarterly awareness report readable in one sitting."],
    },
    {
        "slug": "owen.brooks",
        "name": "Owen Brooks",
        "role": "Infrastructure Engineer",
        "team": "Platform",
        "location": "Building A",
        "initials": "OB",
        "badge": "KR-0154",
        "bio": "Keeps the intranet, VPN, and build pipeline out of the incident queue.",
        "kudos": ["Moved the badge-photo service off the legacy host."],
    },
]

PEOPLE_BY_SLUG = {person["slug"]: person for person in PEOPLE}

ANNOUNCEMENTS = [
    "Badge photos are being refreshed this week. Please review yours in the directory.",
    "The Q3 intelligence retrospective is in the Fusion Center wiki.",
    "Reminder: do not post customer names or incident details in public channels.",
]

KUDOS = [
    ("Dana Whitfield", "Clean Sweep", "Closed every assigned review before the audit window."),
    ("Marcus Lee", "First Blood", "Caught the first sample in the supplier-phishing wave."),
    ("Priya Nair", "Self-Reliant", "Finished the awareness rebuild without opening a hint."),
]


def _esc(value) -> str:
    return html.escape(str(value or ""), quote=True)


def _shell(title: str, body: str, active: str = "") -> str:
    nav = [
        ("home", "/", "Dashboard"),
        ("people", "/people", "People"),
        ("kudos", "/kudos", "Kudos"),
        ("announcements", "/announcements", "Announcements"),
    ]
    links = "".join(
        f'<a class="nav-link{" nav-link--active" if key == active else ""}" href="{href}">{label}</a>'
        for key, href, label in nav
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{_esc(title)} · Kestrel Connect</title>
  <style>
    :root {{
      --ink: #e8eef5;
      --muted: #93a4b8;
      --panel: #141f2c;
      --panel-2: #1b2a3a;
      --line: #2b3d50;
      --accent: #5eead4;
      --gold: #f5c76a;
      --danger: #fb7185;
      --bg: #0a121b;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      min-height: 100vh;
      background:
        radial-gradient(circle at 8% 0%, rgba(94, 234, 212, 0.10), transparent 34rem),
        radial-gradient(circle at 92% 4%, rgba(245, 199, 106, 0.08), transparent 30rem),
        var(--bg);
      color: var(--ink);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif;
      line-height: 1.55;
    }}
    a {{ color: var(--accent); text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    .topbar {{
      display: flex;
      align-items: center;
      gap: 1.25rem;
      padding: 0.85rem clamp(1rem, 4vw, 3rem);
      border-bottom: 1px solid var(--line);
      background: rgba(10, 18, 27, 0.82);
      backdrop-filter: blur(10px);
      position: sticky;
      top: 0;
      z-index: 5;
    }}
    .brand {{
      display: inline-flex;
      align-items: baseline;
      gap: 0.4rem;
      color: var(--ink);
      font-weight: 800;
      letter-spacing: 0.16em;
      font-size: 0.8rem;
      text-decoration: none;
      white-space: nowrap;
    }}
    .brand span {{ color: var(--gold); }}
    .nav {{ display: flex; flex-wrap: wrap; gap: 0.2rem; flex: 1; }}
    .nav-link {{
      padding: 0.35rem 0.65rem;
      border-radius: 999px;
      color: var(--muted);
      font-size: 0.78rem;
      font-weight: 600;
    }}
    .nav-link:hover {{ color: var(--ink); background: var(--panel-2); text-decoration: none; }}
    .nav-link--active {{ color: var(--bg); background: var(--accent); }}
    .top-avatar {{
      display: grid;
      place-items: center;
      width: 34px;
      height: 34px;
      border-radius: 50%;
      background: var(--panel-2);
      border: 1px solid var(--line);
      color: var(--gold);
      font-size: 0.7rem;
      font-weight: 800;
    }}
    main {{
      width: min(1080px, 92vw);
      margin: 0 auto;
      padding: 2rem 0 3rem;
    }}
    .eyebrow {{
      margin: 0 0 0.35rem;
      color: var(--gold);
      font-size: 0.68rem;
      font-weight: 800;
      letter-spacing: 0.16em;
      text-transform: uppercase;
    }}
    h1 {{ margin: 0 0 0.45rem; font-size: clamp(1.7rem, 4vw, 2.5rem); line-height: 1.1; }}
    h2 {{ margin: 0 0 0.75rem; font-size: 0.74rem; letter-spacing: 0.1em; text-transform: uppercase; color: var(--muted); }}
    p {{ margin: 0.35rem 0; }}
    .muted {{ color: var(--muted); }}
    .hero {{
      padding: 1.6rem;
      border: 1px solid var(--line);
      border-radius: 16px;
      background:
        linear-gradient(125deg, rgba(94, 234, 212, 0.08), transparent 45%),
        linear-gradient(315deg, rgba(245, 199, 106, 0.08), transparent 42%),
        var(--panel);
      margin-bottom: 1rem;
    }}
    .hero p {{ max-width: 62ch; color: var(--muted); }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 1rem;
    }}
    .card {{
      padding: 1.15rem;
      border: 1px solid var(--line);
      border-radius: 14px;
      background: var(--panel);
    }}
    .card--wide {{ grid-column: 1 / -1; }}
    .people-list, .kudos-list, .announcement-list {{ margin: 0; padding: 0; list-style: none; }}
    .people-list li, .kudos-list li, .announcement-list li {{
      padding: 0.55rem 0;
      border-top: 1px solid var(--line);
    }}
    .people-list li:first-child, .kudos-list li:first-child, .announcement-list li:first-child {{ border-top: 0; }}
    .person {{
      display: flex;
      align-items: center;
      gap: 0.65rem;
    }}
    .avatar {{
      display: grid;
      place-items: center;
      width: 36px;
      height: 36px;
      flex-shrink: 0;
      border-radius: 50%;
      background: var(--panel-2);
      border: 1px solid var(--line);
      color: var(--accent);
      font-size: 0.68rem;
      font-weight: 800;
    }}
    .person strong {{ display: block; font-size: 0.84rem; }}
    .person small {{ color: var(--muted); }}
    .kudos li {{ font-size: 0.82rem; }}
    .kudos b {{ color: var(--gold); }}
    .kudos span {{ color: var(--muted); }}
    .profile-head {{
      display: flex;
      gap: 1rem;
      align-items: center;
      flex-wrap: wrap;
      margin-bottom: 1rem;
    }}
    .avatar--large {{
      width: 82px;
      height: 82px;
      font-size: 1.25rem;
      border-color: rgba(94, 234, 212, 0.45);
    }}
    .profile-meta {{ color: var(--muted); font-size: 0.8rem; }}
    .badge-photo {{
      width: 100%;
      max-width: 420px;
      display: block;
      border-radius: 12px;
      border: 1px solid var(--line);
      background: var(--panel-2);
    }}
    .tag {{
      display: inline-block;
      padding: 0.18rem 0.5rem;
      margin-right: 0.3rem;
      border-radius: 999px;
      border: 1px solid var(--line);
      color: var(--muted);
      font-size: 0.68rem;
      font-weight: 600;
    }}
    .back {{ display: inline-block; margin-bottom: 0.75rem; font-size: 0.78rem; }}
    .warning {{
      border-left: 3px solid var(--danger);
      padding: 0.8rem 0.95rem;
      background: rgba(251, 113, 133, 0.08);
      border-radius: 0 10px 10px 0;
      color: var(--ink);
      font-size: 0.82rem;
      margin: 1rem 0;
    }}
    .code {{
      font-family: "JetBrains Mono", ui-monospace, SFMono-Regular, Menlo, monospace;
      font-size: 0.78rem;
      background: #081019;
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 0.55rem 0.7rem;
      overflow-x: auto;
    }}
    footer {{
      padding: 1.2rem clamp(1rem, 4vw, 3rem) 2rem;
      color: var(--muted);
      font-size: 0.68rem;
      text-align: center;
      border-top: 1px solid var(--line);
    }}
    @media (max-width: 760px) {{
      .grid {{ grid-template-columns: 1fr; }}
      .topbar {{ flex-wrap: wrap; }}
      .nav {{ order: 3; flex-basis: 100%; }}
    }}
  </style>
</head>
<body>
  <header class="topbar">
    <a class="brand" href="/">KESTREL<span>RIDGE</span></a>
    <nav class="nav">{links}</nav>
    <div class="top-avatar" aria-hidden="true">AK</div>
  </header>
  <main>
    {body}
  </main>
  <footer>
    Kestrel Connect · Internal use only · Build 2026.10.31 · {_esc(COMPANY)}
  </footer>
  <script src="/static/app.js"></script>
</body>
</html>"""


def _dashboard() -> str:
    people = "".join(
        f'<li><a class="person" href="/people/{person["slug"]}">'
        f'<span class="avatar">{person["initials"]}</span>'
        f'<span><strong>{_esc(person["name"])}</strong>'
        f'<small>{_esc(person["role"])} · {_esc(person["team"])}</small></span></a></li>'
        for person in PEOPLE
    )
    kudos = "".join(
        f'<li><b>{_esc(name)}</b> earned <b>{_esc(badge)}</b><br><span>{_esc(text)}</span></li>'
        for name, badge, text in KUDOS
    )
    announcements = "".join(f"<li>{_esc(item)}</li>" for item in ANNOUNCEMENTS)
    body = f"""
    <section class="hero">
      <p class="eyebrow">Fusion Center / Internal</p>
      <h1>Good morning, analyst.</h1>
      <p>Track the people, projects, and wins across Kestrel Ridge. The weekly
      intelligence brief is in review; the badge-photo refresh is still open.</p>
    </section>
    <div class="grid">
      <section class="card">
        <h2>People directory</h2>
        <ul class="people-list">{people}</ul>
      </section>
      <section class="card">
        <h2>Kudos wall</h2>
        <ul class="kudos-list">{kudos}</ul>
      </section>
      <section class="card card--wide">
        <h2>Announcements</h2>
        <ul class="announcement-list">{announcements}</ul>
      </section>
    </div>"""
    return _shell("Dashboard", body, active="home")


def _people() -> str:
    rows = "".join(
        f'<li><a class="person" href="/people/{person["slug"]}">'
        f'<span class="avatar">{person["initials"]}</span>'
        f'<span><strong>{_esc(person["name"])}</strong>'
        f'<small>{_esc(person["role"])} · {_esc(person["team"])} · {_esc(person["badge"])}</small></span></a></li>'
        for person in PEOPLE
    )
    body = f"""
    <p class="eyebrow">Directory</p>
    <h1>People at Kestrel Ridge</h1>
    <p class="muted">Profiles are visible to everyone on the intranet. Badge photos
    are maintained by People Security.</p>
    <section class="card" style="margin-top:1rem">
      <ul class="people-list">{rows}</ul>
    </section>"""
    return _shell("People", body, active="people")


def _profile(person: dict) -> str:
    kudos = "".join(f"<li>{_esc(item)}</li>" for item in person["kudos"])
    body = f"""
    <a class="back" href="/people">← People directory</a>
    <section class="hero">
      <div class="profile-head">
        <span class="avatar avatar--large">{person["initials"]}</span>
        <div>
          <p class="eyebrow">Employee profile</p>
          <h1>{_esc(person["name"])}</h1>
          <p class="profile-meta">{_esc(person["role"])} · {_esc(person["team"])}</p>
          <p class="profile-meta">{_esc(person["location"])} · Badge {_esc(person["badge"])}</p>
          <p style="margin-top:0.5rem">
            <span class="tag">intranet</span>
            <span class="tag">badge photo</span>
            <span class="tag">fusion center</span>
          </p>
        </div>
      </div>
      <p>{_esc(person["bio"])}</p>
    </section>
    <div class="grid">
      <section class="card">
        <h2>Badge photo</h2>
        <img class="badge-photo" src="/assets/badge.png" alt="Employee badge photo for {_esc(person['name'])}">
        <p class="muted" style="font-size:0.72rem">Last refreshed 2026-10-12 · Photo booth v2.1</p>
      </section>
      <section class="card">
        <h2>Recent kudos</h2>
        <ul class="kudos-list">{kudos}</ul>
        <p class="muted" style="margin-top:0.8rem;font-size:0.72rem">
          Kudos are mirrored from the weekly celebration digest.
        </p>
      </section>
    </div>"""
    return _shell(person["name"], body, active="people")


def _notes() -> str:
    audit_note = FLAG if MODE == "public_profile" else "redacted in this build"
    body = f"""
    <a class="back" href="/people/dana.whitfield">← Dana Whitfield</a>
    <p class="eyebrow">Restricted · People Security</p>
    <h1>Dana Whitfield · internal notes</h1>
    <div class="warning">
      This page is not linked from the directory. It is retained for the current
      access review and should be removed when the review closes.
    </div>
    <section class="card">
      <h2>Access review</h2>
      <p>Badge reissue is pending. The photo booth export still carries the old
      barcode and should be replaced before the next audit.</p>
      <p>Requested transfer to the Fusion Center was approved by the team lead.</p>
      <p class="muted">Review owner: People Security · Last touched 2026-10-30</p>
    </section>
    <!-- audit-note: {_esc(audit_note)} -->"""
    return _shell("Internal notes", body, active="people")


def _kudos() -> str:
    items = "".join(
        f'<li><b>{_esc(name)}</b> earned <b>{_esc(badge)}</b><br><span>{_esc(text)}</span></li>'
        for name, badge, text in KUDOS
    )
    body = f"""
    <p class="eyebrow">Celebration digest</p>
    <h1>Kudos wall</h1>
    <p class="muted">A running record of wins from across the Fusion Center and
    People Security teams.</p>
    <section class="card" style="margin-top:1rem"><ul class="kudos-list">{items}</ul></section>"""
    return _shell("Kudos", body, active="kudos")


def _announcements() -> str:
    items = "".join(f"<li>{_esc(item)}</li>" for item in ANNOUNCEMENTS)
    body = f"""
    <p class="eyebrow">Company notices</p>
    <h1>Announcements</h1>
    <section class="card" style="margin-top:1rem"><ul class="announcement-list">{items}</ul></section>"""
    return _shell("Announcements", body, active="announcements")


def _robots() -> str:
    return """# Kestrel Connect staging build
# Do not index internal review pages.
User-agent: *
Disallow: /people/dana.whitfield/notes
Disallow: /static/staging/
Disallow: /api/internal/

# Legacy photo booth export
# /assets/badge.png
"""


def _app_js() -> str:
    code_flag = ""
    if MODE == "code_intel":
        code_flag = f"""
/* TODO(KR-0421): remove the staging token before the next deploy.
   token = "{FLAG}"
*/
"""
    return f"""/* Kestrel Connect - small intranet helpers. */
(function () {{
  const search = document.querySelector("[data-people-search]");
  if (search) {{
    const rows = Array.from(document.querySelectorAll("[data-person]"));
    search.addEventListener("input", () => {{
      const needle = search.value.trim().toLowerCase();
      rows.forEach((row) => {{
        row.hidden = needle !== "" && !row.textContent.toLowerCase().includes(needle);
      }});
    }});
  }}

  document.querySelectorAll("[data-year]").forEach((el) => {{
    el.textContent = new Date().getFullYear();
  }});
}})();
{code_flag}
"""


def _extract_script() -> str:
    path = TOOLS / "extract_lsb.py"
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return "# extractor not available\n"


def _swocts_mirror() -> str:
    """Offline mirror of the public SWOCTS homepage for the source-code lab.

    The real target is https://www.swocts.com. This mirror repeats the same
    meta tag so the exercise can be validated without outbound internet.
    """
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>SWOCTS Hub</title>
  <meta name="description" content="Southwestern Ontario Cybersecurity Hub - Uniting professionals through events, workshops, and community.">
  <meta name="x-swocts-osint" content="{_esc(FLAG)}">
  <!-- Local mirror for the OpenCyberRange OSINT exercise. Live target: https://www.swocts.com -->
  <style>
    :root {{ color-scheme: dark; }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      min-height: 100vh;
      display: grid;
      place-items: center;
      padding: 2rem;
      background:
        radial-gradient(circle at 18% 10%, rgba(56, 189, 248, 0.22), transparent 34rem),
        radial-gradient(circle at 82% 84%, rgba(45, 212, 191, 0.18), transparent 32rem),
        #07111c;
      color: #e8eef5;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif;
    }}
    main {{
      width: min(780px, 100%);
      padding: clamp(1.5rem, 5vw, 3rem);
      border: 1px solid #27435a;
      border-radius: 20px;
      background: rgba(13, 28, 43, 0.88);
      box-shadow: 0 24px 80px rgba(0, 0, 0, 0.35);
    }}
    .eyebrow {{
      margin: 0 0 0.5rem;
      color: #5eead4;
      font-size: 0.7rem;
      font-weight: 800;
      letter-spacing: 0.18em;
      text-transform: uppercase;
    }}
    h1 {{ margin: 0 0 0.75rem; font-size: clamp(2rem, 6vw, 3.5rem); line-height: 1.02; letter-spacing: -0.04em; }}
    p {{ color: #9fb3c8; line-height: 1.65; }}
    .pill {{
      display: inline-block;
      margin-top: 1rem;
      padding: 0.35rem 0.7rem;
      border: 1px solid #27435a;
      border-radius: 999px;
      color: #5eead4;
      font-size: 0.72rem;
      font-weight: 700;
    }}
    code {{ color: #f5c76a; }}
  </style>
</head>
<body>
  <main>
    <p class="eyebrow">Southwestern Ontario Cybersecurity Hub</p>
    <h1>SWOCTS Hub</h1>
    <p>Uniting cybersecurity professionals through free, open-source events,
    workshops, and community collaboration.</p>
    <p>This is a local mirror of the public homepage used for an OSINT
    exercise. The live target is <code>https://www.swocts.com</code>.</p>
    <span class="pill">View the page source</span>
  </main>
</body>
</html>"""


class Handler(BaseHTTPRequestHandler):
    server_version = "KestrelConnect/1.0"

    def log_message(self, fmt, *args):  # keep container logs quiet
        pass

    def _send(self, status: int, body: bytes, content_type: str):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _html(self, body: str, status: int = 200):
        self._send(status, body.encode("utf-8"), "text/html; charset=utf-8")

    def _json(self, payload: dict, status: int = 200):
        self._send(status, json.dumps(payload).encode("utf-8"), "application/json")

    def do_GET(self):
        path = urlparse(self.path).path

        if MODE == "public_site":
            if path == "/health":
                self._send(200, b"ok\n", "text/plain; charset=utf-8")
            elif path in ("/", "/index.html"):
                self._html(_swocts_mirror())
            elif path == "/robots.txt":
                self._send(
                    200,
                    b"User-agent: *\nAllow: /\n",
                    "text/plain; charset=utf-8",
                )
            else:
                self._html(_shell("Not found", "<h1>Not found</h1>"), 404)
            return

        if path == "/health":
            self._send(200, b"ok\n", "text/plain; charset=utf-8")
        elif path == "/":
            self._html(_dashboard())
        elif path == "/people":
            self._html(_people())
        elif path == "/people/dana.whitfield":
            self._html(_profile(PEOPLE_BY_SLUG["dana.whitfield"]))
        elif path == "/people/dana.whitfield/notes":
            self._html(_notes())
        elif path == "/kudos":
            self._html(_kudos())
        elif path == "/announcements":
            self._html(_announcements())
        elif path == "/robots.txt":
            self._send(
                200, _robots().encode("utf-8"), "text/plain; charset=utf-8"
            )
        elif path == "/static/app.js":
            self._send(
                200, _app_js().encode("utf-8"), "application/javascript; charset=utf-8"
            )
        elif path == "/tools/extract_lsb.py":
            self._send(
                200,
                _extract_script().encode("utf-8"),
                "text/x-python; charset=utf-8",
            )
        elif path == "/assets/badge.png":
            image = "badge_stego.png" if MODE == "image_intel" else "badge_clean.png"
            try:
                self._send(200, (ASSETS / image).read_bytes(), "image/png")
            except OSError:
                self._send(404, b"badge photo unavailable\n", "text/plain")
        elif path == "/api/directory":
            self._json({
                "people": [
                    {"slug": p["slug"], "name": p["name"], "role": p["role"]}
                    for p in PEOPLE
                ]
            })
        elif path.startswith("/people/") and path.count("/") == 2:
            slug = path.rsplit("/", 1)[-1]
            person = PEOPLE_BY_SLUG.get(slug)
            if person:
                self._html(_profile(person))
            else:
                self._html(_shell("Not found", "<h1>Profile not found</h1>"), 404)
        else:
            self._html(
                _shell(
                    "Not found",
                    "<p class=\"eyebrow\">404</p><h1>That page is not on the intranet.</h1>"
                    "<p class=\"muted\">Try the <a href=\"/people\">people directory</a>.</p>",
                ),
                404,
            )


def main():
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print(f"Kestrel Connect listening on :{PORT} (mode={MODE})", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()

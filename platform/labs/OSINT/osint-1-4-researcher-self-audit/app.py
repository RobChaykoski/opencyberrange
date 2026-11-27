#!/usr/bin/env python3
"""A safe, offline OSINT self-audit target for the OSINT track.

The portal is a synthetic "mirror" of one fictional researcher's public
footprint. Learners search for the researcher, compare the public profile with
a breach record and photo metadata, and write a remediation plan. Every person,
organisation, address, credential, and record is invented. Nothing here reaches
the internet and no input is stored.
"""

from __future__ import annotations

import html
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

FLAG = os.environ.get("FLAG", "OCR{4ud1t_b3f0r3_y0u_publ1sh}")
PORT = int(os.environ.get("PORT", "8080"))

RESEARCHER = {
    "name": "Dr. Maya Chen",
    "slug": "maya-chen",
    "role": "Postdoctoral Researcher",
    "org": "Fictional Institute for Coastal Resilience",
    "email": "maya.chen.research@example.edu",
    "handle": "@mayachen_lab",
    "office": "Building C, Room 214",
    "orcid": "0000-0000-0000-0000",
    "github": "mayachen-lab",
    "conference": "Coastal Data Summit, 12-14 May 2027, Harbour City",
    "bio": (
        "Maya studies storm-surge exposure in small coastal communities. She "
        "publishes open notebooks, teaches a summer mapping workshop, and is "
        "the person everyone asks when a dataset needs a map."
    ),
}

FICTION_NOTICE = (
    "Fictional teaching data. Every person, organisation, address, credential, "
    "and record on this page is invented for the exercise. Do not use these "
    "details against a real person or service."
)

STYLE = """
:root {
  color-scheme: dark;
  --ink: #eef4f8;
  --muted: #9fb2c4;
  --panel: #14202c;
  --panel-2: #1b2b3a;
  --line: #2c4256;
  --accent: #67e8f9;
  --gold: #f6c96b;
  --danger: #fda4af;
  --ok: #86efac;
  --bg: #08111a;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  min-height: 100vh;
  background:
    radial-gradient(circle at 8% 0%, rgba(103, 232, 249, 0.12), transparent 32rem),
    radial-gradient(circle at 92% 4%, rgba(246, 201, 107, 0.08), transparent 30rem),
    var(--bg);
  color: var(--ink);
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif;
  line-height: 1.55;
}
a { color: var(--accent); text-decoration: none; }
a:hover { text-decoration: underline; }
.topbar {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.8rem clamp(1rem, 4vw, 3rem);
  border-bottom: 1px solid var(--line);
  background: rgba(8, 17, 26, 0.88);
  backdrop-filter: blur(10px);
  position: sticky;
  top: 0;
  z-index: 5;
}
.brand { display: inline-flex; flex-direction: column; line-height: 1.05; }
.brand strong { font-size: 0.82rem; letter-spacing: 0.14em; text-transform: uppercase; }
.brand span { color: var(--gold); font-size: 0.66rem; letter-spacing: 0.05em; }
.nav { display: flex; flex-wrap: wrap; gap: 0.2rem; flex: 1; }
.nav a {
  padding: 0.35rem 0.65rem;
  border-radius: 999px;
  color: var(--muted);
  font-size: 0.78rem;
  font-weight: 600;
}
.nav a:hover { color: var(--ink); background: var(--panel-2); text-decoration: none; }
.nav a.active { color: var(--bg); background: var(--accent); }
.pill {
  padding: 0.28rem 0.6rem;
  border: 1px solid var(--line);
  border-radius: 999px;
  color: var(--gold);
  font-size: 0.64rem;
  font-weight: 700;
  white-space: nowrap;
}
main { width: min(1060px, 92vw); margin: 0 auto; padding: 2rem 0 3rem; }
.eyebrow {
  margin: 0 0 0.35rem;
  color: var(--gold);
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}
h1 { margin: 0 0 0.5rem; font-size: clamp(1.6rem, 3vw, 2.35rem); line-height: 1.15; }
h2 { margin: 0 0 0.55rem; font-size: 1.15rem; }
p { margin: 0 0 0.8rem; }
.lead { max-width: 58rem; color: var(--muted); font-size: 1.02rem; }
.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem; }
.card {
  padding: 1rem 1.1rem;
  border: 1px solid var(--line);
  border-radius: 12px;
  background: linear-gradient(180deg, var(--panel), rgba(16, 28, 40, 0.7));
}
.card h2 { color: var(--accent); }
.muted { color: var(--muted); }
.notice {
  margin: 1rem 0;
  padding: 0.8rem 0.95rem;
  border: 1px solid rgba(246, 201, 107, 0.45);
  border-radius: 10px;
  background: rgba(246, 201, 107, 0.08);
  color: #f8dfa6;
  font-size: 0.84rem;
}
.badges { display: flex; flex-wrap: wrap; gap: 0.4rem; margin: 0.7rem 0 0; }
.badge {
  padding: 0.22rem 0.55rem;
  border: 1px solid var(--line);
  border-radius: 999px;
  color: var(--muted);
  font-size: 0.7rem;
}
.badge.danger { color: var(--danger); border-color: rgba(253, 164, 175, 0.4); }
.badge.ok { color: var(--ok); border-color: rgba(134, 239, 172, 0.35); }
table { width: 100%; border-collapse: collapse; }
th, td { padding: 0.5rem 0.55rem; border-bottom: 1px solid var(--line); text-align: left; vertical-align: top; }
th { color: var(--muted); font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.06em; }
code, pre { font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }
code { color: #bae6fd; }
pre {
  overflow-x: auto;
  padding: 0.8rem;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: #0b1621;
  color: #d7e6f4;
  font-size: 0.8rem;
}
input[type="search"], input[type="text"] {
  width: min(100%, 32rem);
  padding: 0.55rem 0.7rem;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: var(--panel);
  color: var(--ink);
  font: inherit;
}
button {
  padding: 0.55rem 0.8rem;
  border: 1px solid var(--accent);
  border-radius: 8px;
  background: var(--accent);
  color: var(--bg);
  font: inherit;
  font-weight: 700;
  cursor: pointer;
}
.result { padding: 0.75rem 0; border-bottom: 1px solid var(--line); }
.result:last-child { border-bottom: 0; }
.result a { font-weight: 700; }
.result .url { color: var(--ok); font-size: 0.78rem; }
.result .snippet { color: var(--muted); font-size: 0.86rem; }
ul { margin: 0.4rem 0 0.9rem; padding-left: 1.2rem; }
li { margin-bottom: 0.35rem; }
.fiction { margin-top: 2rem; color: var(--muted); font-size: 0.75rem; }
"""


def esc(value) -> str:
    return html.escape(str(value or ""), quote=True)


def shell(title: str, body: str, active: str = "") -> str:
    nav = [
        ("home", "/", "Overview"),
        ("search", "/search", "Search"),
        ("profile", f"/profile/{RESEARCHER['slug']}", "Profile"),
        ("breach", "/breach", "Breach record"),
        ("photo", "/photo", "Photo metadata"),
    ]
    links = "".join(
        f'<a class="{"active" if key == active else ""}" href="{href}">{label}</a>'
        for key, href, label in nav
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)} | Researcher Self-Audit Mirror</title>
  <style>{STYLE}</style>
</head>
<body>
  <div class="topbar">
    <div class="brand">
      <strong>Researcher Self-Audit</strong>
      <span>offline synthetic mirror</span>
    </div>
    <nav class="nav">{links}</nav>
    <span class="pill">TRAINING DATA</span>
  </div>
  <main>
    {body}
    <p class="fiction">{esc(FICTION_NOTICE)}</p>
  </main>
</body>
</html>"""


def home() -> str:
    return shell(
        "Overview",
        f"""
        <p class="eyebrow">Researcher self-audit</p>
        <h1>What does a stranger learn about Dr. Maya Chen?</h1>
        <p class="lead">
          Maya is a fictional coastal-resilience researcher preparing for a
          conference. She asked for a pre-trip privacy review. Use the mirror
          the way an outsider would: start with a search, compare the public
          profile with other records, and decide what should be removed,
          separated, or monitored.
        </p>
        <div class="notice">
          This is a safe simulation. The portal contains no real person, no real
          breach data, no live social-media target, and no writable state.
        </div>
        <div class="grid">
          <section class="card">
            <h2>1. Search the name and handles</h2>
            <p class="muted">Try the name, the lab handle, and the public email. Search engines are mirrors too.</p>
            <a href="/search">Open the search mirror</a>
          </section>
          <section class="card">
            <h2>2. Compare the public profile</h2>
            <p class="muted">Public profiles often carry contact details, location, travel, and account names.</p>
            <a href="/profile/{esc(RESEARCHER['slug'])}">Open Maya's profile</a>
          </section>
          <section class="card">
            <h2>3. Check the other records</h2>
            <p class="muted">A breach record and a badge photo can confirm identifiers the profile already exposed.</p>
            <a href="/breach">Breach record</a> &middot; <a href="/photo">Photo metadata</a>
          </section>
          <section class="card">
            <h2>4. Write the remediation plan</h2>
            <p class="muted">Name the exposure, the action, and the owner. A finding without an action is only trivia.</p>
            <span class="badge ok">Workbook step</span>
          </section>
        </div>
        """,
    )


def search_page(query: str) -> str:
    q = query.strip()
    body = f"""
    <p class="eyebrow">Search mirror</p>
    <h1>Search the public footprint</h1>
    <p class="lead">
      This simulates the result page for a name, handle, or email. The results
      are fixed teaching records, not live search results.
    </p>
    <form method="get" action="/search">
      <input type="search" name="q" value="{esc(q)}" placeholder="Try: Maya Chen, @mayachen_lab, or the email" aria-label="Search query">
      <button type="submit">Search</button>
    </form>
    """
    if not q:
        body += """
        <div class="notice">
          Start with the name, then try the lab handle and the public email.
          Reusing the same handle across sites links records together.
        </div>
        """
        return shell("Search", body, "search")

    results = [
        (
            "Maya Chen | Fictional Institute for Coastal Resilience",
            f"/profile/{RESEARCHER['slug']}",
            "Profile page — role, public email, office, conference travel, ORCID, GitHub handle.",
        ),
        (
            "Maya Chen — Lakeside Community School",
            "/search?q=maya-chen-school",
            "Different person — a school staff page with the same common name. No research affiliation; do not merge this record.",
        ),
        (
            "Coastal Data Summit 2027 — speaker list",
            "/search?q=coastal-data-summit",
            "Conference listing — name, talk title, and travel dates.",
        ),
        (
            "mayachen_lab on Example Forum",
            "/search?q=mayachen_lab",
            "Forum profile — same handle, old posts, and a link to a personal blog.",
        ),
        (
            "Maya Chen | Fictional Institute for Coastal Resilience (cached)",
            f"/profile/{RESEARCHER['slug']}",
            "Duplicate profile — a cached copy of the same page. Confirm the canonical URL before recording it.",
        ),
        (
            "Have I Been Exposed? (synthetic record)",
            "/breach",
            "Breach record — public email and a reused username.",
        ),
    ]
    rows = "".join(
        f"""
        <div class="result">
          <a href="{href}">{esc(title)}</a>
          <div class="url">mirror.example.edu{href}</div>
          <div class="snippet">{esc(snippet)}</div>
        </div>
        """
        for title, href, snippet in results
    )
    body += f"""
    <h2 style="margin-top:1.4rem;">Results for “{esc(q)}”</h2>
    {rows}
    <div class="notice">
      A search result is a lead, not proof. Confirm the identifier on the page
      itself and record where you found it.
    </div>
    """
    return shell("Search results", body, "search")


def profile_page() -> str:
    r = RESEARCHER
    body = f"""
    <!-- reviewer note: the exposure review ticket is /review/OSINT-SELF-001 -->
    <p class="eyebrow">Public profile</p>
    <h1>{esc(r['name'])}</h1>
    <p class="lead">{esc(r['role'])}, {esc(r['org'])}</p>
    <div class="grid">
      <section class="card">
        <h2>About</h2>
        <p>{esc(r['bio'])}</p>
        <p class="muted">Open notebooks, reproducible maps, and community workshops.</p>
      </section>
      <section class="card">
        <h2>Contact and accounts</h2>
        <table>
          <tr><th>Public email</th><td><code>{esc(r['email'])}</code></td></tr>
          <tr><th>Lab handle</th><td><code>{esc(r['handle'])}</code></td></tr>
          <tr><th>Office</th><td>{esc(r['office'])}</td></tr>
          <tr><th>ORCID</th><td><code>{esc(r['orcid'])}</code></td></tr>
          <tr><th>GitHub</th><td><code>{esc(r['github'])}</code></td></tr>
        </table>
      </section>
    </div>
    <section class="card" style="margin-top:1rem;">
      <h2>Upcoming</h2>
      <p>{esc(r['conference'])}</p>
      <p class="muted">Two workshop sessions and a poster. Travel dates are in the conference listing.</p>
    </section>
    <div class="notice">
      Ask yourself which fields a stranger needs in order to contact Maya
      professionally, and which fields only help someone correlate accounts,
      track travel, or target a password reset.
    </div>
    """
    return shell("Profile", body, "profile")


def breach_page() -> str:
    r = RESEARCHER
    body = f"""
    <p class="eyebrow">Synthetic breach record</p>
    <h1>Exposure history</h1>
    <p class="lead">
      This record is invented for the exercise. It is not a live breach lookup
      and it does not contain a real password or credential.
    </p>
    <table>
      <tr><th>Email</th><td><code>{esc(r['email'])}</code></td></tr>
      <tr><th>Username</th><td><code>{esc(r['handle'])}</code></td></tr>
      <tr><th>Source</th><td>Example Forum (fictional) — 2024 archive</td></tr>
      <tr><th>Exposed fields</th><td>Email address, username, salted password hash, last login IP</td></tr>
      <tr><th>Reuse risk</th><td>High — the same handle appears on the profile and the old forum</td></tr>
    </table>
    <div class="notice">
      A breach record turns a username into a verification lead. The defensive
      response is not “change one password”; it is unique credentials, MFA,
      session review, and a check for other accounts that share the identifier.
    </div>
    <h2 style="margin-top:1.2rem;">What a reviewer should record</h2>
    <ul>
      <li>The exposed identifier and where it was confirmed.</li>
      <li>Whether the identifier links to other public accounts.</li>
      <li>The remediation owner and the date the change was verified.</li>
    </ul>
    """
    return shell("Breach record", body, "breach")


def photo_page() -> str:
    body = """
    <p class="eyebrow">Synthetic photo metadata</p>
    <h1>Badge photo record</h1>
    <p class="lead">
      This is a text-only metadata record, not a real photograph. It exists to
      show what a published image can reveal after the picture is forgotten.
    </p>
    <table>
      <tr><th>Camera</th><td>ExampleCam X100 (fictional)</td></tr>
      <tr><th>Captured</th><td>2027-03-14 09:12:44</td></tr>
      <tr><th>GPS</th><td><code>12.345678, 98.765432</code> (synthetic placeholder, not a real place)</td></tr>
      <tr><th>Software</th><td>PhotoEditor 5.2</td></tr>
      <tr><th>Comment</th><td>“Maya — Building C loading dock”</td></tr>
      <tr><th>Original filename</th><td><code>IMG_0412_badge_original.jpg</code></td></tr>
    </table>
    <div class="notice">
      The metadata names a device, a time, a location, and an internal place.
      Stripping metadata before publishing is a one-step control; keeping the
      original file out of the public share is the stronger one.
    </div>
    """
    return shell("Photo metadata", body, "photo")


def review_page() -> str:
    body = f"""
    <!-- Self-audit review ticket. Flag: {esc(FLAG)} -->
    <p class="eyebrow">Review ticket OSINT-SELF-001</p>
    <h1>Self-audit findings and remediation</h1>
    <p class="lead">
      This ticket is the reviewer's working copy. It is not linked from the
      profile navigation, but the profile source points here. Finding the
      ticket is the last step; the flag is in the page source.
    </p>
    <h2>Findings</h2>
    <p class="muted">Risk: Low means limited context; Medium means useful for correlation; High means direct location, contact, or account-recovery exposure.</p>
    <table>
      <tr><th>Exposure</th><th>Risk</th><th>Why it matters</th><th>Action</th></tr>
      <tr><td>Public email</td><td>Low</td><td>Needed for professional contact, but useful for phishing and account discovery</td><td>Use a role address; keep the personal address off the public page</td></tr>
      <tr><td>Handle reuse</td><td>High</td><td>Links a professional identity to a forum account and a breach record</td><td>Separate the personal handle; check account recovery paths</td></tr>
      <tr><td>Office and travel dates</td><td>Medium</td><td>Reveals physical location and absence windows</td><td>Publish only the conference city or a “remote” status</td></tr>
      <tr><td>Photo metadata</td><td>High</td><td>Confirms device, time, and an internal building</td><td>Strip metadata; publish a re-encoded copy</td></tr>
      <tr><td>Stale forum profile</td><td>Medium</td><td>Keeps an old identifier and personal blog discoverable</td><td>Retire or update the profile; remove the old link</td></tr>
    </table>
    <h2 style="margin-top:1.2rem;">Exposure score</h2>
    <p class="muted">Use the score to order remediation. It supports the risk rating; it does not replace it.</p>
    <table>
      <tr><th>Signal</th><th>Weight</th><th>Present?</th><th>Score</th></tr>
      <tr><td>Public email</td><td>+2</td><td>Yes</td><td>2</td></tr>
      <tr><td>Handle reuse</td><td>+3</td><td>Yes</td><td>3</td></tr>
      <tr><td>Travel schedule</td><td>+3</td><td>Yes</td><td>3</td></tr>
      <tr><td>Photo metadata</td><td>+4</td><td>Yes</td><td>4</td></tr>
      <tr><th>Total</th><th></th><th></th><th>12</th></tr>
    </table>
    <h2 style="margin-top:1.2rem;">Remediation checklist</h2>
    <table>
      <tr><th>Action</th><th>Owner</th><th>Due date</th><th>Verification date</th></tr>
      <tr><td>Remove the public personal email; keep a role address</td><td>Maya Chen</td><td>2027-04-15</td><td>2027-04-18</td></tr>
      <tr><td>Stop reusing the lab handle for non-professional accounts</td><td>Maya Chen</td><td>2027-04-20</td><td>2027-04-22</td></tr>
      <tr><td>Strip EXIF and GPS before publishing images</td><td>Comms team</td><td>2027-04-10</td><td>2027-04-11</td></tr>
      <tr><td>Remove office room numbers and precise travel dates</td><td>Web team</td><td>2027-04-12</td><td>2027-04-14</td></tr>
      <tr><td>Retire stale profiles and old links</td><td>Maya Chen</td><td>2027-04-30</td><td>Pending</td></tr>
      <tr><td>Enable MFA and review active sessions after any breach notice</td><td>IT support</td><td>2027-04-08</td><td>2027-04-09</td></tr>
    </table>
    <div class="notice">
      A complete finding names the exposure, the evidence, the risk, the action,
      the owner, and the verification date. “Be more careful online” is not a
      remediation plan. A pending verification is still an open finding.
    </div>
    """
    return shell("Review ticket", body, "")


def robots() -> str:
    return """# Researcher self-audit mirror
# The review ticket is not linked from the profile navigation.
User-agent: *
Disallow: /review/
Disallow: /breach/
"""


class Handler(BaseHTTPRequestHandler):
    server_version = "ResearcherSelfAudit/1.0"

    def _send(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def _html(self, body: str, status: int = 200) -> None:
        self._send(status, body.encode("utf-8"), "text/html; charset=utf-8")

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path
        if path == "/health":
            self._send(200, b"ok\n", "text/plain; charset=utf-8")
            return
        if path in ("/", "/index.html"):
            self._html(home())
            return
        if path == "/search":
            query = parse_qs(parsed.query).get("q", [""])[0]
            self._html(search_page(query))
            return
        if path == f"/profile/{RESEARCHER['slug']}":
            self._html(profile_page())
            return
        if path == "/breach":
            self._html(breach_page())
            return
        if path == "/photo":
            self._html(photo_page())
            return
        if path == "/review/OSINT-SELF-001":
            self._html(review_page())
            return
        if path == "/robots.txt":
            self._send(200, robots().encode("utf-8"), "text/plain; charset=utf-8")
            return
        self._html(
            shell(
                "Not found",
                """
                <p class="eyebrow">404</p>
                <h1>That page is not on the mirror</h1>
                <p class="lead">Return to the overview and follow the audit trail.</p>
                <a href="/">Back to the overview</a>
                """,
            ),
            404,
        )

    def do_HEAD(self) -> None:
        self.do_GET()

    def log_message(self, fmt: str, *args) -> None:
        return


def main() -> None:
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print(f"researcher self-audit mirror listening on :{PORT}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()

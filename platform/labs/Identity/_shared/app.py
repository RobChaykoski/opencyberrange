#!/usr/bin/env python3
"""Identity & Access training targets.

Each lab selects a mode with LAB_MODE and supplies its own FLAG:

    authweak   - a staff portal with a forgeable session cookie and weak hashing
    oauth      - a mock OIDC client that trusts any redirect URI and skips state
    lifecycle  - an access review with a stale leaver account and an admin token

The targets are deliberately vulnerable in the taught area. They are isolated,
read-only, and dependency-free. They never call the internet or store state.
"""
import base64
import html
import json
import os
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

MODE = os.environ.get("LAB_MODE", "authweak")
FLAG = os.environ.get("FLAG", "OCR{identity_flag_not_set}")
TITLE = os.environ.get("TITLE", "Identity & Access")
PORT = int(os.environ.get("PORT", "8080"))

DEMO_USER = "amara"
DEMO_PASSWORD = "Library2026!"
OAUTH_CODE = "AUTH-CODE-7f3a"
ACCESS_TOKEN = "ACCESS-TOKEN-amara-7f3a"
VICTIM = "amara"

ACCOUNTS = [
    {
        "user": "amara",
        "role": "staff",
        "status": "active",
        "last_login": "2026-11-10",
        "token": "tok_amara_staff_2b7c",
        "scope": "reports:read",
    },
    {
        "user": "rowan",
        "role": "reports-admin",
        "status": "active",
        "last_login": "2025-09-14",
        "token": "tok_rowan_9f2c",
        "scope": "reports:admin",
    },
    {
        "user": "svc-reports",
        "role": "service",
        "status": "active",
        "last_login": "2026-11-10",
        "token": "tok_svc_reports_4d1a",
        "scope": "reports:read",
    },
]
REPORT_ADMIN_TOKEN = "tok_rowan_9f2c"
REPORT_READ_TOKENS = {"tok_amara_staff_2b7c", "tok_svc_reports_4d1a"}

STYLE = """
:root {
  --ink: #e8eef5;
  --muted: #9aa9bb;
  --panel: #152232;
  --panel-2: #1c2d40;
  --line: #30465e;
  --accent: #6ee7d8;
  --gold: #f5c76a;
  --danger: #fca5a5;
  --bg: #0a121b;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  min-height: 100vh;
  background:
    radial-gradient(circle at 8% 0%, rgba(110, 231, 216, 0.10), transparent 34rem),
    radial-gradient(circle at 92% 4%, rgba(245, 199, 106, 0.08), transparent 30rem),
    var(--bg);
  color: var(--ink);
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif;
  line-height: 1.6;
}
a { color: var(--accent); }
a:hover { text-decoration: underline; }
.wrap { width: min(920px, 92vw); margin: 0 auto; padding: 2rem 0 3rem; }
.topbar {
  display: flex; align-items: center; gap: 1rem;
  padding: 0.8rem clamp(1rem, 4vw, 3rem);
  border-bottom: 1px solid var(--line);
  background: rgba(10, 18, 27, 0.85);
  position: sticky; top: 0; z-index: 5;
}
.brand { font-weight: 800; letter-spacing: 0.14em; font-size: 0.78rem; white-space: nowrap; }
.brand span { color: var(--gold); }
.pill {
  display: inline-block; padding: 0.15rem 0.55rem; border-radius: 999px;
  background: var(--panel-2); border: 1px solid var(--line);
  color: var(--muted); font-size: 0.72rem; font-weight: 700;
}
h1 { font-size: clamp(1.9rem, 4vw, 3rem); line-height: 1.1; margin: 1.4rem 0 0.6rem; }
h2 { margin-top: 2rem; font-size: 1.2rem; }
p, li { color: var(--muted); }
.lede { font-size: 1.05rem; max-width: 62ch; }
.card {
  background: var(--panel); border: 1px solid var(--line);
  border-radius: 14px; padding: 1.2rem 1.35rem; margin: 1.2rem 0;
}
.card h2 { margin-top: 0; color: var(--ink); }
.card p:last-child { margin-bottom: 0; }
code, pre {
  font-family: "JetBrains Mono", ui-monospace, SFMono-Regular, Consolas, monospace;
  font-size: 0.88rem;
}
code { background: var(--panel-2); padding: 0.1rem 0.35rem; border-radius: 5px; color: var(--ink); }
pre {
  background: #07101a; border: 1px solid var(--line); border-radius: 10px;
  padding: 0.9rem 1rem; overflow-x: auto; color: #cfe3f5;
}
.button {
  display: inline-block; margin-top: 0.4rem; padding: 0.6rem 0.9rem;
  border-radius: 8px; background: var(--accent); color: #04121a;
  font-weight: 800; text-decoration: none;
}
button.button { border: 0; cursor: pointer; font: inherit; }
.button:hover { text-decoration: none; filter: brightness(1.05); }
.steps li { margin-bottom: 0.45rem; }
.note { border-left: 3px solid var(--gold); padding-left: 0.8rem; }
.danger { border-left: 3px solid var(--danger); padding-left: 0.8rem; }
.footer { margin-top: 2.5rem; color: #6f8297; font-size: 0.8rem; }
table { width: 100%; border-collapse: collapse; margin: 0.8rem 0; font-size: 0.9rem; }
th, td { text-align: left; padding: 0.5rem 0.6rem; border-bottom: 1px solid var(--line); vertical-align: top; }
th { color: var(--ink); }
label { display: block; margin: 0.6rem 0 0.2rem; color: var(--muted); font-weight: 600; }
input {
  width: 100%; padding: 0.55rem 0.7rem; border-radius: 8px;
  border: 1px solid var(--line); background: var(--panel-2);
  color: var(--ink); font: inherit;
}
.form-row { margin: 0.6rem 0; }
"""


def page(title: str, body: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)} - {html.escape(TITLE)}</title>
  <style>{STYLE}</style>
</head>
<body>
  <header class="topbar">
    <div class="brand">OPEN<span>CYBER</span>RANGE</div>
    <span class="pill">Identity &amp; Access</span>
  </header>
  <main class="wrap">
    {body}
    <p class="footer">A safe, fictional training target. Nothing here is real data.</p>
  </main>
</body>
</html>
"""


def _session_token(user: str, role: str) -> str:
    return base64.b64encode(f"{user}:{role}".encode("utf-8")).decode("ascii")


def _parse_session(value: str):
    if not value:
        return None, None
    try:
        decoded = base64.b64decode(value, validate=True).decode("utf-8")
        user, role = decoded.split(":", 1)
    except (ValueError, UnicodeDecodeError):
        return None, None
    if not user or role not in ("staff", "admin"):
        return None, None
    return user, role


def auth_home_body() -> str:
    return f"""
      <!-- Debug build: session tokens are base64(user:role). -->
      <span class="pill">Authentication</span>
      <h1>Community centre staff portal</h1>
      <p class="lede">A small staff portal lets volunteers check schedules and
      reports. The developer shipped a debug session format and enabled MFA only
      for the administrator account.</p>
      <div class="card">
        <h2>Sign in</h2>
        <form method="post" action="/login">
          <div class="form-row">
            <label for="user">Username</label>
            <input id="user" name="user" autocomplete="username" required>
          </div>
          <div class="form-row">
            <label for="password">Password</label>
            <input id="password" name="password" type="password"
                   autocomplete="current-password" required>
          </div>
          <button class="button" type="submit">Sign in</button>
        </form>
        <p class="note" style="margin-top:1rem">Demo staff account:
        <code>{DEMO_USER}</code> / <code>{DEMO_PASSWORD}</code>. Admin accounts
        require a second factor.</p>
      </div>
      <div class="card">
        <h2>Your goal</h2>
        <p>Sign in as the demo staff user, inspect the session cookie, and see
        whether you can reach the admin console. Recover the training token and
        explain the session fix.</p>
        <p>If you are already signed in, open <a href="/dashboard">your
        dashboard</a>.</p>
      </div>
      <div class="card note">
        <h2>Password storage</h2>
        <p>The portal's user table stores passwords with a fast hash. That is a
        separate problem from the session cookie. The workbook asks you to
        explain both.</p>
      </div>
    """


def auth_login_body(error: str = "") -> str:
    message = f'<p class="danger">{html.escape(error)}</p>' if error else ""
    return f"""
      <span class="pill">Authentication</span>
      <h1>Sign in</h1>
      {message}
      <div class="card">
        <form method="post" action="/login">
          <div class="form-row">
            <label for="user">Username</label>
            <input id="user" name="user" autocomplete="username" required>
          </div>
          <div class="form-row">
            <label for="password">Password</label>
            <input id="password" name="password" type="password"
                   autocomplete="current-password" required>
          </div>
          <button class="button" type="submit">Sign in</button>
        </form>
        <p class="note" style="margin-top:1rem">Demo staff account:
        <code>{DEMO_USER}</code> / <code>{DEMO_PASSWORD}</code>.</p>
      </div>
      <p><a href="/">Back to the portal</a></p>
    """


def auth_dashboard_body(user: str, role: str, cookie: str) -> str:
    return f"""
      <span class="pill">Signed in</span>
      <h1>Dashboard</h1>
      <div class="card">
        <h2>Session</h2>
        <p>Signed in as <strong>{html.escape(user)}</strong> with role
        <strong>{html.escape(role)}</strong>.</p>
        <p>Your session cookie is:</p>
        <pre>session={html.escape(cookie)}</pre>
        <p>The server reads the role from this cookie. It does not keep a
        server-side session record.</p>
      </div>
      <div class="card">
        <h2>Next step</h2>
        <p>The admin console checks the role in the same cookie. If your role is
        <code>staff</code>, the console will refuse you.</p>
        <p><a class="button" href="/admin">Open admin console</a></p>
      </div>
      <p><a href="/">Back to the portal</a></p>
    """


def auth_admin_body(user: str) -> str:
    return f"""
      <span class="pill">Admin console</span>
      <h1>Administration</h1>
      <div class="card">
        <h2>Access granted</h2>
        <p>Signed in as <strong>{html.escape(user)}</strong> with role
        <strong>admin</strong>.</p>
        <p>MFA was verified when this account signed in. The server trusted the
        session cookie and did not check a server-side session record.</p>
        <p>Training token: <code>{html.escape(FLAG)}</code></p>
      </div>
      <div class="card note">
        <h2>Why this worked</h2>
        <p>The cookie is base64 of <code>user:role</code>. Changing the role and
        re-encoding the cookie is enough to become an administrator. A real
        session should use a random, opaque identifier stored on the server, and
        the server should check the role on every request.</p>
      </div>
      <p><a href="/dashboard">Back to the dashboard</a></p>
    """


def oauth_home_body() -> str:
    authorize = (
        "/authorize?client_id=community-portal"
        "&amp;redirect_uri=http://oauth.lab:8080/callback"
        "&amp;response_type=code&amp;state=demo-state"
    )
    return f"""
      <span class="pill">Federation</span>
      <h1>Community ID</h1>
      <p class="lede">A new community portal uses Community ID to sign volunteers
      in. The client registration was created in a hurry.</p>
      <div class="card">
        <h2>Sign in with Community ID</h2>
        <p><a class="button" href="{authorize}">Continue</a></p>
        <p>The provider redirects back to the portal with an authorization code.</p>
      </div>
      <div class="card">
        <h2>Client configuration (debug)</h2>
        <pre>client_id: community-portal
redirect_uri: any value accepted
state: not required
pkce: not used
token audience: not checked</pre>
        <p>This is a training client. The debug panel shows the controls that are
        missing so you can test the flow.</p>
      </div>
      <div class="card note">
        <h2>Your goal</h2>
        <p>See whether the authorization code can be delivered somewhere other
        than the portal's callback. Then exchange the code and read the victim's
        profile.</p>
      </div>
    """


def oauth_callback_body(code: str) -> str:
    return f"""
      <span class="pill">Portal callback</span>
      <h1>Sign-in complete</h1>
      <div class="card">
        <h2>Authorization code received</h2>
        <pre>{html.escape(code)}</pre>
        <p>The client would exchange this code for an access token.</p>
        <p><a class="button"
        href="/token?code={urllib.parse.quote(code)}&amp;client_id=community-portal">Exchange
        code</a></p>
      </div>
      <p><a href="/">Back to Community ID</a></p>
    """


def oauth_attacker_body(code: str) -> str:
    return f"""
      <span class="pill">Attacker callback</span>
      <h1>The code went to the wrong place</h1>
      <div class="card">
        <h2>Stolen authorization code</h2>
        <pre>{html.escape(code)}</pre>
        <p>The provider accepted this callback because the client does not
        enforce an exact redirect URI allowlist. The client also did not send or
        verify a <code>state</code> value.</p>
        <p><a class="button"
        href="/token?code={urllib.parse.quote(code)}&amp;client_id=community-portal">Exchange
        the code</a></p>
        <p>After the exchange, copy the <code>access_token</code> into
        <code>/me?access_token=...</code>.</p>
      </div>
      <p><a href="/">Back to Community ID</a></p>
    """


def oauth_me_body() -> str:
    return f"""
      <span class="pill">Victim profile</span>
      <h1>Community ID profile</h1>
      <div class="card">
        <h2>{VICTIM}</h2>
        <p>Role: community volunteer</p>
        <p>Email: {VICTIM}@communitycentre.example</p>
        <p>Training token: <code>{html.escape(FLAG)}</code></p>
      </div>
      <div class="card note">
        <h2>What was missing</h2>
        <p>An exact redirect URI allowlist, a per-request <code>state</code>
        value, PKCE for public clients, short-lived one-time codes, and token
        audience checks. The provider should also bind the code to the client
        that requested it.</p>
      </div>
    """


def lifecycle_home_body() -> str:
    return f"""
      <span class="pill">Access review</span>
      <h1>Quarterly access review</h1>
      <p class="lede">A community centre is reviewing who can still reach its
      reporting system. The volunteer coordinator left 14 months ago, but the
      review was never completed.</p>
      <div class="card">
        <h2>Your goal</h2>
        <p>Open the directory, identify the account that should have been
        disabled, and use its API token to reach the reporting export. Then write
        the offboarding fixes.</p>
        <p><a class="button" href="/directory">Open the directory</a></p>
      </div>
      <div class="card">
        <h2>Test an API token</h2>
        <form method="get" action="/api/reports">
          <div class="form-row">
            <label for="token">API token</label>
            <input id="token" name="token" autocomplete="off"
                   placeholder="tok_...">
          </div>
          <button class="button" type="submit">Check reports access</button>
        </form>
      </div>
      <div class="card note">
        <h2>Offboarding checklist</h2>
        <p>Disable the account, revoke tokens and sessions, transfer files and
        ownership, remove shared-drive access, and record the review.</p>
      </div>
    """


def lifecycle_directory_body() -> str:
    rows = "".join(
        "<tr>"
        f"<td>{html.escape(account['user'])}</td>"
        f"<td>{html.escape(account['role'])}</td>"
        f"<td>{html.escape(account['status'])}</td>"
        f"<td>{html.escape(account['last_login'])}</td>"
        f"<td><code>{html.escape(account['token'])}</code></td>"
        f"<td>{html.escape(account['scope'])}</td>"
        "</tr>"
        for account in ACCOUNTS
    )
    return f"""
      <span class="pill">Directory</span>
      <h1>Accounts and tokens</h1>
      <p class="lede">These are the active accounts in the community centre
      directory. Status and last login are part of the review.</p>
      <table>
        <thead>
          <tr><th>User</th><th>Role</th><th>Status</th><th>Last login</th>
          <th>API token</th><th>Scope</th></tr>
        </thead>
        <tbody>{rows}</tbody>
      </table>
      <div class="card note">
        <h2>Review question</h2>
        <p>Which account has not signed in for more than a year but still has an
        active token? What access does that token grant?</p>
      </div>
      <p><a href="/">Back to the access review</a></p>
    """


def lifecycle_reports_body() -> str:
    return f"""
      <span class="pill">Reports</span>
      <h1>Reporting export</h1>
      <div class="card">
        <h2>Access granted</h2>
        <p>This endpoint requires the <code>reports:admin</code> scope.</p>
        <p>Training token: <code>{html.escape(FLAG)}</code></p>
      </div>
      <div class="card note">
        <h2>Least privilege</h2>
        <p>The account that reached this page should have been disabled when the
        person left. The token was never revoked, and the account held more
        access than the role needed.</p>
      </div>
      <p><a href="/directory">Back to the directory</a></p>
    """


class Handler(BaseHTTPRequestHandler):
    server_version = "IdentityAccess/1.0"

    def log_message(self, format, *args):
        return

    def _cookie(self, name: str) -> str:
        raw = self.headers.get("Cookie", "")
        for part in raw.split(";"):
            key, _, value = part.strip().partition("=")
            if key == name:
                return value
        return ""

    def _read_body(self) -> str:
        length = int(self.headers.get("Content-Length", "0") or 0)
        if length <= 0:
            return ""
        return self.rfile.read(length).decode("utf-8", "replace")

    def _send(self, status, body, content_type="text/html; charset=utf-8", extra_headers=None):
        data = body.encode("utf-8") if isinstance(body, str) else body
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'none'; style-src 'unsafe-inline'; img-src data:; "
            "base-uri 'none'; form-action 'self'; frame-ancestors 'none'",
        )
        self.send_header("Cache-Control", "no-store")
        for key, value in (extra_headers or {}).items():
            self.send_header(key, value)
        self.end_headers()
        if not getattr(self, "_head_only", False):
            self.wfile.write(data)

    def do_HEAD(self):
        self._head_only = True
        self.do_GET()

    def do_POST(self):
        path = self.path.split("?", 1)[0]
        if MODE == "authweak" and path == "/login":
            params = urllib.parse.parse_qs(self._read_body())
            user = (params.get("user") or [""])[0]
            password = (params.get("password") or [""])[0]
            if user == DEMO_USER and password == DEMO_PASSWORD:
                token = _session_token(user, "staff")
                self._send(
                    302,
                    "",
                    "text/plain; charset=utf-8",
                    {
                        "Location": "/dashboard",
                        # Intentionally missing HttpOnly, Secure, and SameSite.
                        "Set-Cookie": f"session={token}; Path=/",
                    },
                )
                return
            self._send(
                401,
                page("Sign in", auth_login_body("Invalid username or password.")),
            )
            return
        self._send(405, page("Method not allowed", "<h1>Method not allowed</h1>"))

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)

        if MODE == "authweak":
            if path in ("/", "/index.html"):
                body = page("Staff portal", auth_home_body())
            elif path == "/login":
                body = page("Sign in", auth_login_body())
            elif path == "/dashboard":
                user, role = _parse_session(self._cookie("session"))
                if not user:
                    self._send(401, page("Sign in required", auth_login_body("Sign in first.")))
                    return
                body = page("Dashboard", auth_dashboard_body(user, role, self._cookie("session")))
            elif path == "/admin":
                user, role = _parse_session(self._cookie("session"))
                if not user:
                    self._send(401, page("Sign in required", auth_login_body("Sign in first.")))
                    return
                if role != "admin":
                    self._send(
                        403,
                        page(
                            "Forbidden",
                            "<h1>Admin access required</h1>"
                            "<p>Your session role is <code>staff</code>. "
                            "The admin console requires <code>admin</code>.</p>"
                            "<p><a href='/dashboard'>Back to the dashboard</a></p>",
                        ),
                    )
                    return
                body = page("Admin console", auth_admin_body(user))
            else:
                self._send(404, page("Not found", "<h1>Not found</h1>"))
                return

        elif MODE == "oauth":
            if path in ("/", "/index.html"):
                body = page("Community ID", oauth_home_body())
            elif path == "/authorize":
                redirect_uri = (params.get("redirect_uri") or [""])[0]
                state = (params.get("state") or [""])[0]
                if not redirect_uri:
                    self._send(
                        400,
                        page("Bad request", "<h1>Missing redirect_uri</h1>"),
                    )
                    return
                separator = "&" if "?" in redirect_uri else "?"
                location = f"{redirect_uri}{separator}code={OAUTH_CODE}"
                if state:
                    location += f"&state={urllib.parse.quote(state)}"
                self._send(
                    302,
                    "",
                    "text/plain; charset=utf-8",
                    {"Location": location},
                )
                return
            elif path == "/callback":
                code = (params.get("code") or [""])[0]
                body = page("Portal callback", oauth_callback_body(code))
            elif path == "/attacker":
                code = (params.get("code") or [""])[0]
                body = page("Attacker callback", oauth_attacker_body(code))
            elif path == "/token":
                code = (params.get("code") or [""])[0]
                if code != OAUTH_CODE:
                    self._send(
                        400,
                        json.dumps({"error": "invalid_grant"}),
                        "application/json",
                    )
                    return
                self._send(
                    200,
                    json.dumps(
                        {
                            "access_token": ACCESS_TOKEN,
                            "token_type": "Bearer",
                            "expires_in": 3600,
                            "scope": "profile",
                        }
                    ),
                    "application/json",
                )
                return
            elif path == "/me":
                token = (params.get("access_token") or [""])[0]
                authorization = self.headers.get("Authorization", "")
                if not token and authorization.lower().startswith("bearer "):
                    token = authorization[7:].strip()
                if token != ACCESS_TOKEN:
                    self._send(
                        401,
                        page(
                            "Unauthorized",
                            "<h1>Unauthorized</h1>"
                            "<p>A valid access token is required.</p>",
                        ),
                    )
                    return
                body = page("Profile", oauth_me_body())
            else:
                self._send(404, page("Not found", "<h1>Not found</h1>"))
                return

        elif MODE == "lifecycle":
            if path in ("/", "/index.html"):
                body = page("Access review", lifecycle_home_body())
            elif path == "/directory":
                body = page("Directory", lifecycle_directory_body())
            elif path == "/api/reports":
                token = (params.get("token") or [""])[0]
                if not token:
                    token = self.headers.get("X-API-Token", "")
                if token == REPORT_ADMIN_TOKEN:
                    body = page("Reporting export", lifecycle_reports_body())
                elif token in REPORT_READ_TOKENS:
                    self._send(
                        403,
                        page(
                            "Forbidden",
                            "<h1>Insufficient scope</h1>"
                            "<p>This token has <code>reports:read</code>. "
                            "The export endpoint requires "
                            "<code>reports:admin</code>.</p>"
                            "<p><a href='/directory'>Back to the directory</a></p>",
                        ),
                    )
                    return
                else:
                    self._send(
                        401,
                        page(
                            "Unauthorized",
                            "<h1>Missing or invalid API token</h1>"
                            "<p>Provide an API token from the directory.</p>",
                        ),
                    )
                    return
            else:
                self._send(404, page("Not found", "<h1>Not found</h1>"))
                return

        else:
            self._send(500, page("Configuration error", "<h1>Unknown LAB_MODE</h1>"))
            return

        self._send(200, body)


if __name__ == "__main__":
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    server.serve_forever()

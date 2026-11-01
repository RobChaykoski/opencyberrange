#!/usr/bin/env python3
"""Shared browser-first target for the Software Security starter labs.

Two modes:

  code_review         A fictional DevFest speaker portal. The shipped JavaScript
                      contains a temporary export route and token; the route
                      returns the flag only when the token is supplied. The
                      lesson is that client-side code is public and a hidden
                      route is not access control.

  command_injection   A network diagnostics form that passes a hostname to a
                      shell. The learner can add a shell separator and read the
                      flag from /tmp/flag. The container is isolated, read-only,
                      and drops all capabilities; the shell is the exercise.

Dependency-free on purpose. Run with LAB_MODE and FLAG set by the lab compose
file. Nothing here contacts a real service.
"""
import html
import os
import subprocess
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

MODE = os.environ.get("LAB_MODE", "code_review")
FLAG = os.environ.get("FLAG", "OCR{software_security_flag_not_set}")
COMPANY = os.environ.get("COMPANY", "DevFest Windsor-Essex")
PORT = int(os.environ.get("PORT", "8080"))
FLAG_PATH = Path(os.environ.get("FLAG_PATH", "/tmp/flag"))
EXPORT_TOKEN = os.environ.get("EXPORT_TOKEN", "devfest-export-2026")

if MODE == "command_injection":
    try:
        FLAG_PATH.write_text(FLAG + "\n", encoding="utf-8")
    except OSError:
        pass


def page(title: str, body: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)} | {html.escape(COMPANY)}</title>
  <style>
    :root {{ color-scheme: dark; }}
    body {{ margin: 0; font: 16px/1.55 system-ui, sans-serif; background: #0f172a; color: #e2e8f0; }}
    main {{ max-width: 760px; margin: 0 auto; padding: 2rem 1.25rem 4rem; }}
    header {{ border-bottom: 1px solid #334155; padding-bottom: 1rem; margin-bottom: 1.5rem; }}
    h1 {{ margin: 0 0 .25rem; font-size: 1.5rem; }}
    h2 {{ margin-top: 2rem; font-size: 1.15rem; }}
    p, li {{ color: #cbd5e1; }}
    a {{ color: #60a5fa; }}
    code, pre {{ font-family: ui-monospace, monospace; }}
    pre {{ background: #111827; border: 1px solid #334155; border-radius: 8px; padding: 1rem; overflow-x: auto; white-space: pre-wrap; }}
    input {{ background: #111827; color: #e2e8f0; border: 1px solid #475569; border-radius: 6px; padding: .55rem .7rem; font: inherit; }}
    button {{ background: #2563eb; color: white; border: 0; border-radius: 6px; padding: .6rem .9rem; font: inherit; cursor: pointer; }}
    .muted {{ color: #94a3b8; font-size: .9rem; }}
    .card {{ background: #1e293b; border: 1px solid #334155; border-radius: 10px; padding: 1rem 1.25rem; }}
  </style>
</head>
<body>
<main>
  <header>
    <h1>{html.escape(COMPANY)}</h1>
    <p class="muted">Fictional training portal. No real people or attendee data.</p>
  </header>
  {body}
</main>
</body>
</html>"""


def code_review_home() -> str:
    return page(
        "Speaker Portal",
        """
        <h2>Community speaker portal</h2>
        <p>Welcome to the DevFest volunteer portal. The community track keeps
        speaker exports and handoff notes here.</p>
        <div class="card">
          <p><strong>Ada Mercer</strong><br>Community track speaker</p>
          <p class="muted">The speaker export link is being moved to the new
          admin console. The old route still exists in the portal code.</p>
        </div>
        <h2>Portal resources</h2>
        <ul>
          <li><a href="/static/app.js">Open the portal JavaScript</a></li>
          <li><a href="/robots.txt">robots.txt</a></li>
        </ul>
        <p class="muted">Viewing the source is allowed. This is a training app.</p>
        """,
    )


def diagnostics_home() -> str:
    return page(
        "Network Diagnostics",
        """
        <h2>Host lookup</h2>
        <p>Enter a hostname or IP address to check that the DevFest network can
        resolve it.</p>
        <form action="/lookup" method="get">
          <label for="host">Hostname or IP</label><br>
          <input id="host" name="host" value="127.0.0.1" autocomplete="off">
          <button type="submit">Look up</button>
        </form>
        <p class="muted">The diagnostics service is intentionally small. It is
        not connected to the public internet.</p>
        """,
    )


def lookup(host: str) -> str:
    # Deliberately vulnerable: untrusted input is passed to a shell. The lab
    # container is isolated; the exercise is to notice and exploit this.
    try:
        completed = subprocess.run(
            ["sh", "-c", f"getent hosts {host}"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        output = (completed.stdout or "") + (completed.stderr or "")
    except subprocess.TimeoutExpired:
        output = "Lookup timed out after 5 seconds."
    return output.strip() or "No result."


class Handler(BaseHTTPRequestHandler):
    server_version = "OCRSoftwareSecurity/1.0"

    def _send(self, status: int, body: str, content_type: str = "text/html; charset=utf-8") -> None:
        data = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:  # noqa: N802 - stdlib handler name
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        if path == "/healthz":
            self._send(200, "ok", "text/plain; charset=utf-8")
            return

        if MODE == "code_review":
            if path == "/":
                self._send(200, code_review_home())
                return
            if path == "/static/app.js":
                script = (
                    "/* DevFest speaker portal bootstrap.\n"
                    " * TODO(ada): remove the temporary export route before launch.\n"
                    f" * Export route: /admin/export?token={EXPORT_TOKEN}\n"
                    " */\n"
                    "console.log('portal ready');\n"
                )
                self._send(200, script, "application/javascript; charset=utf-8")
                return
            if path == "/admin/export":
                token = (query.get("token") or [""])[0]
                if token != EXPORT_TOKEN:
                    self._send(403, page("Export denied", "<h2>Export denied</h2><p>The organiser token is required.</p>"))
                    return
                self._send(
                    200,
                    page(
                        "Speaker Export",
                        f"""
                        <h2>Speaker export</h2>
                        <p>Community track handoff token:</p>
                        <pre>{html.escape(FLAG)}</pre>
                        <p class="muted">This route was left in the shipped
                        JavaScript. Treat client-side code as public.</p>
                        """,
                    ),
                )
                return
            if path == "/robots.txt":
                self._send(200, "User-agent: *\nDisallow: /admin/\n", "text/plain; charset=utf-8")
                return
        elif MODE == "command_injection":
            if path == "/":
                self._send(200, diagnostics_home())
                return
            if path == "/lookup":
                host = (query.get("host") or [""])[0].strip()
                if not host:
                    self._send(400, page("Missing host", "<h2>Missing host</h2><p>Enter a hostname or IP.</p>"))
                    return
                output = lookup(host)
                self._send(
                    200,
                    page(
                        "Lookup result",
                        f"""
                        <h2>Lookup result</h2>
                        <p>Host: <code>{html.escape(host)}</code></p>
                        <pre>{html.escape(output)}</pre>
                        <p><a href="/">Run another lookup</a></p>
                        """,
                    ),
                )
                return

        self._send(404, page("Not found", "<h2>Not found</h2><p>That route does not exist.</p>"))

    def log_message(self, fmt: str, *args) -> None:
        # Do not log request lines: query strings can contain a learner's
        # payload and do not need to be retained by the platform.
        return


if __name__ == "__main__":
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print(f"software-security target mode={MODE} port={PORT}", flush=True)
    server.serve_forever()

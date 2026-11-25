"""Northshore Community Arts practice app for the ZAP baseline lab.

This is a deliberately imperfect, synthetic target. It has a directory listing,
missing security headers, an over-sharing cookie, and a reflected search field.
It contains no real data and makes no outbound calls.
"""

from __future__ import annotations

import os
from pathlib import Path

from flask import Flask, Response, request, send_from_directory

app = Flask(__name__)
FILES = Path(__file__).resolve().parent / "files"

LANDING = """<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>Northshore Community Arts</title></head>
<body>
  <h1>Northshore Community Arts</h1>
  <p>Workshops, exhibitions, and a shared studio calendar for the 2026 season.</p>
  <p>This is a synthetic practice site for the ZAP baseline exercise. It contains
  no real member, donor, or event data.</p>
  <h2>Quick links</h2>
  <ul>
    <li><a href="/files/">Shared files</a></li>
    <li><a href="/search">Search the site</a></li>
    <li><a href="/robots.txt">robots.txt</a></li>
  </ul>
  <form action="/search" method="get">
    <label for="q">Search</label>
    <input id="q" name="q" value="">
    <button type="submit">Go</button>
  </form>
</body>
</html>
"""


@app.after_request
def add_practice_headers(response: Response) -> Response:
    # Deliberately over-shares server and framework details. ZAP reports this as
    # information disclosure; the lab asks the learner to confirm and remove it.
    response.headers["X-Powered-By"] = "Flask practice app"
    response.headers["Server"] = "nginx/1.18.0"
    return response


@app.route("/")
def index() -> Response:
    response = Response(LANDING, mimetype="text/html")
    # Deliberately missing HttpOnly and Secure. The lab asks the learner to
    # notice the cookie flags in the report and in the browser.
    response.set_cookie("arts_session", "demo-session", httponly=False, secure=False, samesite=None)
    return response


@app.route("/files/")
def file_index() -> str:
    if not FILES.is_dir():
        return "<h1>Index of /files</h1><p>No files.</p>"
    entries = sorted(path.name for path in FILES.iterdir() if path.is_file())
    links = "\n".join(
        f'<li><a href="/files/{name}">{name}</a></li>' for name in entries
    )
    return f"""<!doctype html>
<html lang="en"><head><title>Index of /files</title></head>
<body><h1>Index of /files</h1><ul>{links}</ul>
<p>Shared studio exports. Remove this directory from the public site before launch.</p>
</body></html>"""


@app.route("/files/<path:name>")
def file(name: str):
    return send_from_directory(FILES, name)


@app.route("/search")
def search() -> str:
    # Deliberately reflects the query without escaping. A full ZAP scan reports
    # this as reflected cross-site scripting; the baseline lab only needs the
    # passive findings, but the comparison is part of the analysis questions.
    query = request.args.get("q", "")
    return f"""<!doctype html>
<html lang="en"><head><title>Search</title></head>
<body><h1>Search results</h1><p>Results for {query}</p>
<p><a href="/">Back to the home page</a></p></body></html>"""


@app.route("/robots.txt")
def robots() -> Response:
    return Response(
        "User-agent: *\nDisallow: /files/\n",
        mimetype="text/plain",
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "80")))

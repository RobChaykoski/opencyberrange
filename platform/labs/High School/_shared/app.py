#!/usr/bin/env python3
"""RangeBox Basics - a small, safe, dependency-free training target.

Each lab selects a mode with LAB_MODE and supplies its own FLAG:

    welcome   - a welcome page and a downloadable text file
    filehunt  - a small evidence archive with one flag file among decoys
    network   - a status endpoint and a token in the response headers
    browser   - a page whose HTML source contains the flag
    logs      - a synthetic web access log with a suspicious request
    linkcheck - a message with a lookalike link and an encoded token
    filetype  - a shared folder where one file's extension is wrong
    capstone  - a forwarded notice that combines link and file checks
    emailmeta - a raw email with routing, authentication, and custom headers
    mfa_recovery - a staff portal with MFA and a weak recovery question
    provenance   - a newsroom archive with synthetic-media provenance records
    rugpull      - a simulated token dashboard and transaction ledger

Nothing here reaches the internet, calls a real service, or stores state.
"""
import base64
import codecs
import hashlib
import html
import io
import json
import os
import zipfile
from urllib.parse import parse_qs, quote
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

MODE = os.environ.get("LAB_MODE", "welcome")
FLAG = os.environ.get("FLAG", "OCR{rangebox_flag_not_set}")
TITLE = os.environ.get("TITLE", "RangeBox Basics")
PORT = int(os.environ.get("PORT", "8080"))

DECOY_FLAG = "OCR{d3c0y_n0t_th3_r34l_fl4g}"

STYLE = """
:root {
  --ink: #e8eef5;
  --muted: #9aa9bb;
  --panel: #152232;
  --panel-2: #1c2d40;
  --line: #30465e;
  --accent: #6ee7d8;
  --gold: #f5c76a;
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
.wrap { width: min(900px, 92vw); margin: 0 auto; padding: 2rem 0 3rem; }
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
.button:hover { text-decoration: none; filter: brightness(1.05); }
.steps li { margin-bottom: 0.45rem; }
.note { border-left: 3px solid var(--gold); padding-left: 0.8rem; }
.footer { margin-top: 2.5rem; color: #6f8297; font-size: 0.8rem; }
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
    <span class="pill">RangeBox basics</span>
  </header>
  <main class="wrap">
    {body}
    <p class="footer">A safe, fictional training target. Nothing here is real data.</p>
  </main>
</body>
</html>
"""


def welcome_body() -> str:
    return f"""
      <span class="pill">Start here</span>
      <h1>Welcome to your first RangeBox session</h1>
      <p class="lede">This page is a practice target. You cannot break it, and you can
      use hints at any time.</p>
      <div class="card">
        <h2>Your goal</h2>
        <p>Find the training token in the welcome file, then submit it as the flag.</p>
        <a class="button" href="/welcome.txt">Open welcome.txt</a>
      </div>
      <div class="card">
        <h2>Two ways to get there</h2>
        <ol class="steps">
          <li>Open RangeBox, start the <strong>Kali</strong> desktop, and open a terminal.
              Run <code>curl http://{html.escape(os.environ.get("HOST_LABEL", "rangebox.lab"))}:8080/welcome.txt</code>.</li>
          <li>Or use the browser inside RangeBox and click the button above.</li>
        </ol>
      </div>
      <div class="card note">
        <h2>Feeling stuck?</h2>
        <p>Open the hints panel. Hints are part of the lesson, not a penalty.</p>
      </div>
    """


def filehunt_body() -> str:
    return """
      <span class="pill">File hunt</span>
      <h1>Find the one useful file</h1>
      <p class="lede">A well-meaning teammate zipped up a shared folder before a
      cleanup. Most of it is noise. One file holds the training token.</p>
      <div class="card">
        <h2>Your goal</h2>
        <p>Download the archive, unpack it, and use <code>find</code> and
        <code>grep</code> to locate the token.</p>
        <a class="button" href="/evidence.zip">Download evidence.zip</a>
      </div>
      <div class="card">
        <h2>Suggested path</h2>
        <pre>curl -O http://files.lab:8080/evidence.zip
unzip evidence.zip
find evidence -type f
grep -R "OCR{" evidence</pre>
      </div>
      <div class="card note">
        <h2>Read before you grep</h2>
        <p>The archive contains a decoy token on purpose. The real file is the
        one described by the notes in the archive.</p>
      </div>
    """


def network_body() -> str:
    return f"""
      <span class="pill">Network basics</span>
      <h1>Ask a service how it is doing</h1>
      <p class="lede">Every web request has a request and a response. Response
      headers often carry information the page itself does not show.</p>
      <div class="card">
        <h2>Your goal</h2>
        <p>Request the status endpoint and read the response headers. The
        training token is in a header named <code>X-OCR-Token</code>.</p>
        <pre>curl -i http://network.lab:8080/status.json</pre>
      </div>
      <div class="card">
        <h2>What to notice</h2>
        <ul>
          <li>The status line, such as <code>HTTP/1.1 200 OK</code></li>
          <li>The response headers, one per line</li>
          <li>The JSON body after the blank line</li>
        </ul>
      </div>
      <div class="card note">
        <h2>No terminal?</h2>
        <p>Open the lab browser and visit
        <code>http://network.lab:8080/status.json</code>. Browser developer tools
        show the same response headers under the Network tab.</p>
      </div>
    """


def browser_body() -> str:
    return f"""
      <span class="pill">Browser basics</span>
      <h1>The page is not the whole story</h1>
      <p class="lede">A web page is delivered as text. The browser turns that text
      into what you see. Viewing the source shows the parts that are easy to miss.</p>
      <div class="card">
        <h2>Your goal</h2>
        <p>Open the staff notes page and view its source. The training token is in
        an HTML comment.</p>
        <a class="button" href="/staff-notes.html">Open staff-notes.html</a>
        <p style="margin-top:0.8rem">Then right-click the page and choose
        <strong>View Page Source</strong>, or press <code>Ctrl+U</code>.</p>
      </div>
      <div class="card">
        <h2>Try the terminal too</h2>
        <pre>curl http://web.lab:8080/staff-notes.html</pre>
      </div>
      <div class="card note">
        <h2>Defensive habit</h2>
        <p>Comments in source code can leak notes, internal paths, and test data.
        Remove them before publishing a page.</p>
      </div>
    """


def logs_body() -> str:
    return """
      <span class="pill">Defensive security</span>
      <h1>Read the web server log</h1>
      <p class="lede">A log is a record of what a service saw. Most lines are
      ordinary. A few can tell you that someone was probing the server.</p>
      <div class="card">
        <h2>Your goal</h2>
        <p>Download the access log, find the suspicious requests, and recover the
        training token from the request that should never have succeeded.</p>
        <a class="button" href="/access.log">Open access.log</a>
      </div>
      <div class="card">
        <h2>Try the terminal too</h2>
        <pre>curl http://logs.lab:8080/access.log
grep " 404 " access.log
grep "OCR{" access.log</pre>
      </div>
      <div class="card note">
        <h2>Think like a defender</h2>
        <p>One source address is making repeated failed requests, then a request
        with an unusual query string. That pattern is worth explaining in a short
        incident note.</p>
      </div>
    """


def cyberchef_body(kind: str) -> str:
    """Instructions for a beginner-friendly CyberChef decoding exercise."""
    if kind == "cyberchef_b64":
        lesson = (
            "The message is <strong>Base64 encoded</strong>. Base64 is an encoding, "
            "not encryption: it changes how text is represented so it can travel "
            "safely through systems that expect plain text. It does not keep a "
            "secret."
        )
        recipe = (
            "Open <strong>CyberChef</strong> from the platform menu, drag "
            "<strong>From Base64</strong> into the Recipe column, paste the message "
            "into the Input column, and read the Output."
        )
    elif kind == "cyberchef_caesar":
        lesson = (
            "The message uses a <strong>Caesar shift</strong>, a simple cipher that "
            "moves each letter a fixed number of places through the alphabet. "
            "ROT13 is a shift of 13 and is its own inverse."
        )
        recipe = (
            "Open <strong>CyberChef</strong> from the platform menu, drag "
            "<strong>ROT13</strong> (or <strong>Caesar Brute Force</strong>) into "
            "the Recipe column, paste the message, and read the Output."
        )
    else:
        lesson = (
            "This message has <strong>two layers</strong>: a Base64 layer and a "
            "Caesar shift. Decode the outer layer first, then look at what remains."
        )
        recipe = (
            "Open <strong>CyberChef</strong> from the platform menu. Add "
            "<strong>From Base64</strong>, then add <strong>ROT13</strong>, paste "
            "the message, and read the Output."
        )
    return f"""
      <span class="pill">CyberChef practice</span>
      <h1>Read the message without guessing</h1>
      <p class="lede">A community library received a short note from a partner
      organisation. The note is encoded, and the librarian needs the training token
      inside it. You will use CyberChef to turn the encoded message back into
      readable text.</p>
      <div class="card">
        <h2>Your goal</h2>
        <p>Download the message, decode it with CyberChef, and submit the
        <code>OCR{...}</code> training token as the flag.</p>
        <a class="button" href="/message.txt">Open message.txt</a>
      </div>
      <div class="card">
        <h2>What you are looking at</h2>
        <p>{lesson}</p>
      </div>
      <div class="card">
        <h2>Use CyberChef</h2>
        <p>{recipe}</p>
        <p class="note">CyberChef is a free, client-side tool from GCHQ. Use only the
        fictional message in this lab. Do not paste real passwords, personal data,
        or anything from a real system.</p>
      </div>
      <div class="card note">
        <h2>If you get stuck</h2>
        <p>Check that you used the right operation direction: <strong>From Base64</strong>,
        not <strong>To Base64</strong>. For the shift cipher, try ROT13 first. If the
        output still looks unreadable, read the hints panel and try one operation at a
        time.</p>
      </div>
    """


def _cyberchef_message(kind: str) -> str:
    """Return the encoded practice message for a CyberChef lab."""
    plain = f"Training token: {FLAG}\n"
    if kind == "cyberchef_b64":
        return base64.b64encode(plain.encode("utf-8")).decode("ascii")
    if kind == "cyberchef_caesar":
        return codecs.encode(plain, "rot_13")
    return base64.b64encode(codecs.encode(plain, "rot_13").encode("utf-8")).decode("ascii")


def _linkcheck_message() -> str:
    """A fictional message whose link hides the real host and an encoded token."""
    encoded_flag = quote(FLAG, safe="")
    return (
        "From: Windsor Community Library <updates@windsorlibrary.example>\n"
        "Subject: Your library account needs one quick check\n\n"
        "Hello,\n\n"
        "We are updating our catalogue. Please confirm your account within 24 hours:\n\n"
        "https://windsorlibrary.example@windosrlibrary-secure.example/verify"
        f"?next=%2Faccount%2Ftoken%2F{encoded_flag}\n\n"
        "If you did not request this, ignore this message.\n\n"
        "Thank you,\n"
        "Library Services\n\n"
        "Practice note: the .example domain is reserved for training.\n"
        "Do not click the link. Copy it as text.\n"
    )


def linkcheck_body() -> str:
    message = html.escape(_linkcheck_message())
    return f"""
      <span class="pill">Digital safety</span>
      <h1>Read the link before you click</h1>
      <p class="lede">A patron at the community library received this message.
      The link looks close to the library's real address, but close is not the
      same as correct. You do not need to open it to find out where it goes.</p>
      <div class="card">
        <h2>The message</h2>
        <pre>{message}</pre>
      </div>
      <div class="card">
        <h2>Your goal</h2>
        <p>Do not click the link. Copy it into CyberChef, decode the
        <code>next</code> value, and recover the training token.</p>
        <a class="button" href="/message.txt">Open message.txt</a>
      </div>
      <div class="card">
        <h2>How to read a URL</h2>
        <p>Read from the scheme to the right:</p>
        <pre>scheme://userinfo@host:port/path?query#fragment</pre>
        <p>The <strong>host</strong> is the part after the <code>@</code> and
        before the next <code>/</code>. Text before the <code>@</code> is a
        username, not the site. Percent-encoding such as <code>%2F</code> hides
        characters until you decode them.</p>
      </div>
      <div class="card note">
        <h2>Stay safe</h2>
        <p>The link uses reserved <code>.example</code> domains and a fictional
        practice target, so it cannot reach a real service. Never click a
        suspicious link in real life, even to "see what happens".</p>
      </div>
    """


FILE_DECOYS = {
    "budget.pdf": (
        "Community centre budget (draft)\n"
        "Event supplies: $240\n"
        "Room booking: $0 (donated)\n"
        f"Training token: {DECOY_FLAG}\n"
    ),
    "agenda.txt": (
        "Volunteer event agenda\n"
        "09:00 Welcome\n"
        "09:30 Accessibility walkthrough\n"
        "11:00 Lunch\n"
        "12:00 Close\n"
    ),
    "README.txt": (
        "Community centre shared folder\n"
        "==============================\n"
        "event-photo.png  Group photo from the volunteer event\n"
        "budget.pdf       Approved budget for the event\n"
        "agenda.txt       Event agenda\n\n"
        "If a file does not open the way you expect, do not force it.\n"
        "Ask the coordinator for a fresh copy.\n"
    ),
}

FILE_NAMES = ["event-photo.png", "budget.pdf", "agenda.txt", "README.txt"]


def _disguised_zip(token: str, note: str) -> bytes:
    """Return a ZIP archive that is deliberately served under a misleading name."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("token.txt", f"Training token: {token}\n")
        archive.writestr("notes.txt", note + "\n")
    return buffer.getvalue()


def filetype_body() -> str:
    return """
      <span class="pill">Digital safety</span>
      <h1>Know the file before you open it</h1>
      <p class="lede">A community centre volunteer downloaded files from a
      shared event folder. One of them is not what its name says. A file
      extension is a label, not proof of what is inside.</p>
      <div class="card">
        <h2>The shared folder</h2>
        <ul>
          <li><a href="/downloads/event-photo.png">event-photo.png</a> &mdash; group photo</li>
          <li><a href="/downloads/budget.pdf">budget.pdf</a> &mdash; approved budget</li>
          <li><a href="/downloads/agenda.txt">agenda.txt</a> &mdash; event agenda</li>
          <li><a href="/downloads/README.txt">README.txt</a> &mdash; folder notes</li>
        </ul>
      </div>
      <div class="card">
        <h2>Your goal</h2>
        <p>Download the files, identify their real types, and recover the
        training token. Do not double-click or execute an unknown file.</p>
        <pre>curl -O http://filesafe.lab:8080/downloads/event-photo.png
curl -O http://filesafe.lab:8080/downloads/budget.pdf
file event-photo.png budget.pdf</pre>
      </div>
      <div class="card">
        <h2>What to notice</h2>
        <p><code>file</code> reads the first bytes of a file and reports what
        they indicate. It does not open or run the file. A ZIP archive starts
        with the letters <code>PK</code>. A text file usually reports
        <code>ASCII text</code> or <code>Unicode text</code>.</p>
      </div>
      <div class="card note">
        <h2>If you are not sure</h2>
        <p>Stop and ask. A suspicious file can be reported without opening it.
        Never disable a security warning just to see what a file does.</p>
      </div>
    """


def filetype_listing() -> str:
    items = "".join(
        f'<li><a href="/downloads/{html.escape(name)}">{html.escape(name)}</a></li>'
        for name in FILE_NAMES
    )
    return f"""
      <span class="pill">Shared folder</span>
      <h1>Community centre downloads</h1>
      <p class="lede">These are the files from the volunteer event folder.</p>
      <ul>{items}</ul>
      <p><a href="/">Back to the exercise</a></p>
    """


def _capstone_notice() -> str:
    encoded_path = quote("/files/grant-pack.png", safe="")
    return (
        "From: Community Grants Office <grants@communitycentre.example>\n"
        "Subject: Grant application review - action required\n\n"
        "Your application has moved to review. Open the shared folder to confirm\n"
        "the documents:\n\n"
        "https://communitycentre.example@grant-portal-secure.example/review"
        f"?next={encoded_path}\n\n"
        "The practice mirror is at http://capstone.lab:8080. Decode the link to\n"
        "find the file path, then request that path on the mirror.\n\n"
        "Thank you,\n"
        "Grants Office\n\n"
        "Practice note: the .example domain is reserved for training.\n"
        "Do not click the link. Copy it as text.\n"
    )


def capstone_body() -> str:
    notice = html.escape(_capstone_notice())
    return f"""
      <span class="pill">Capstone</span>
      <h1>Put the evidence together</h1>
      <p class="lede">A volunteer forwarded a grant notice. The link looks
      official, and the attachment is not the file it claims to be. Use the link
      and file skills from the last two exercises to decide what to trust.</p>
      <div class="card">
        <h2>The forwarded notice</h2>
        <pre>{notice}</pre>
      </div>
      <div class="card">
        <h2>Your goal</h2>
        <p>Decode the link, find the file path, request that path from the
        practice mirror, identify the real file type, and recover the training
        token.</p>
      </div>
      <div class="card">
        <h2>Work in order</h2>
        <ol class="steps">
          <li>Do not click the link. Copy it into CyberChef.</li>
          <li>Use <strong>URL Decode</strong> to read the <code>next</code> value.</li>
          <li>Request the decoded path on <code>http://capstone.lab:8080</code>.</li>
          <li>Check the downloaded file&rsquo;s real type before opening it.</li>
          <li>Extract the archive and submit the token.</li>
        </ol>
      </div>
      <div class="card note">
        <h2>Explain your decision</h2>
        <p>The flag is only part of the task. Be ready to say which evidence
        made the message suspicious and what you would tell the volunteer to do
        next.</p>
      </div>
    """


def _email_message() -> str:
    """A fictional raw email with realistic routing and authentication metadata."""
    return (
        "Return-Path: <bounce@mailer-relay.example>\n"
        "Received: from mx.communitycentre.example (mx.communitycentre.example [198.51.100.25])\n"
        "        by inbox.communitycentre.example (Postfix) with ESMTPS id 4Xy7Q2\n"
        "        for <volunteer@communitycentre.example>; Tue, 10 Nov 2026 13:15:07 +0000\n"
        "Received: from smtp.mailer-relay.example (smtp.mailer-relay.example [203.0.113.66])\n"
        "        by mx.communitycentre.example (Postfix) with ESMTP id 3Ab9K1\n"
        "        for <volunteer@communitycentre.example>; Tue, 10 Nov 2026 13:15:05 +0000\n"
        "Received: from grant-portal-secure.example (grant-portal-secure.example [203.0.113.66])\n"
        "        by smtp.mailer-relay.example (Exim 4.96) with ESMTPS id 1Qz4M8\n"
        "        for <volunteer@communitycentre.example>; Tue, 10 Nov 2026 13:15:04 +0000\n"
        "Authentication-Results: mx.communitycentre.example;\n"
        "        spf=fail (sender IP is 203.0.113.66) smtp.mailfrom=mailer-relay.example;\n"
        "        dkim=none (message not signed) header.d=none;\n"
        "        dmarc=fail action=none header.from=communitycentre.example\n"
        "Received-SPF: fail (domain of transitioning bounce@mailer-relay.example does not\n"
        "        designate 203.0.113.66 as a permitted sender)\n"
        "X-Originating-IP: [203.0.113.66]\n"
        "X-Mailer: PHPMailer 6.8.1 (https://github.com/PHPMailer/PHPMailer)\n"
        "X-Spam-Status: No, score=-0.1 required=5.0 tests=BAYES_00,HTML_MESSAGE\n"
        f"X-OCR-Case-Token: {FLAG}\n"
        'From: "Community Grants Office" <grants@communitycentre.example>\n'
        "Reply-To: grants-review@communitycentre-support.example\n"
        "To: volunteer@communitycentre.example\n"
        "Subject: Grant application review - action required\n"
        "Date: Tue, 10 Nov 2026 09:15:02 -0400\n"
        "Message-ID: <20261110131502.4f2a1c@mailer-relay.example>\n"
        "MIME-Version: 1.0\n"
        'Content-Type: text/plain; charset="utf-8"\n'
        "Content-Transfer-Encoding: 7bit\n"
        "\n"
        "Hello,\n\n"
        "Your grant application has moved to review. Please confirm the documents by\n"
        "opening the shared folder:\n\n"
        "https://communitycentre.example@grant-portal-secure.example/review"
        "?next=%2Ffiles%2Fgrant-pack.png\n\n"
        f"Reference: {DECOY_FLAG}\n\n"
        "Thank you,\n"
        "Grants Office\n\n"
        "---\n"
        "This is a fictional training message produced for the OpenCyberRange lab.\n"
        "Do not click the link.\n"
    )


def emailmeta_body() -> str:
    return """
      <span class="pill">Email metadata</span>
      <h1>Dissect the reported email</h1>
      <p class="lede">A volunteer forwarded a grant review message. The rendered
      message looks ordinary, but the raw headers tell a different story.</p>
      <div class="card">
        <h2>Your goal</h2>
        <p>Download the raw email, read its headers, and recover the training
        token from the case metadata. Do not click any link in the message.</p>
        <a class="button" href="/email.eml">Download reported-email.eml</a>
      </div>
      <div class="card">
        <h2>Read it as text</h2>
        <pre>curl -O http://emailmeta.lab:8080/email.eml
less email.eml</pre>
        <p>If <code>less</code> is unfamiliar, use <code>cat</code> or open the
        file in a text editor. The headers are above the blank line; the body is
        below it.</p>
      </div>
      <div class="card">
        <h2>What to look for</h2>
        <ul>
          <li>Who the message claims to be from, and who it actually came from</li>
          <li>The <code>Received</code> chain and the originating address</li>
          <li><code>Authentication-Results</code> for SPF, DKIM, and DMARC</li>
          <li>Custom <code>X-</code> headers that carry routing or case identifiers</li>
        </ul>
      </div>
      <div class="card note">
        <h2>Stay safe</h2>
        <p>The addresses use reserved <code>.example</code> domains and the
        links are not real. Never open an unexpected attachment or click a link
        to test it.</p>
      </div>
    """


MFA_USER = "amara"
MFA_PASSWORD = "Library2026!"
MFA_ANSWER = "The Lantern Keeper"


def mfa_home_body() -> str:
    return f"""
      <span class="pill">Identity</span>
      <h1>MFA and the lost phone</h1>
      <p class="lede">A community centre volunteer lost their phone. The account
      is protected by a password and an authenticator app. The volunteer needs
      to get back in before the Tuesday reading circle.</p>
      <div class="card">
        <h2>Your goal</h2>
        <p>Sign in, see what the MFA prompt asks for, and find the recovery path.
        Recover the training token and explain why the recovery path was weaker
        than the second factor.</p>
        <p><a class="button" href="/login">Open the staff sign-in</a></p>
      </div>
      <div class="card">
        <h2>Also available</h2>
        <p><a href="/staff">Staff directory</a> &mdash; public profiles for the
        community centre team.</p>
      </div>
      <div class="card note">
        <h2>Stay safe</h2>
        <p>This is a fictional account. Never use a real password, recovery
        answer, or authenticator code in a training lab.</p>
      </div>
    """


def mfa_login_body(error: str = "") -> str:
    message = f'<p class="danger">{html.escape(error)}</p>' if error else ""
    return f"""
      <span class="pill">Sign in</span>
      <h1>Staff sign-in</h1>
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
        <code>{MFA_USER}</code> / <code>{MFA_PASSWORD}</code>. The account also
        requires an authenticator code.</p>
        <p><a href="/recover">Lost your phone?</a></p>
      </div>
      <p><a href="/">Back to the portal</a></p>
    """


def mfa_mfa_body() -> str:
    return f"""
      <span class="pill">Second factor</span>
      <h1>Enter your authenticator code</h1>
      <div class="card">
        <h2>MFA required</h2>
        <p>The password was correct. The account now asks for a six-digit code
        from the authenticator app on the volunteer's phone.</p>
        <p>The phone is lost. There is no code to enter here.</p>
        <p><a class="button" href="/recover">Use account recovery</a></p>
      </div>
      <div class="card note">
        <h2>Think like a defender</h2>
        <p>MFA is only as strong as its recovery path. A recovery question that
        anyone can answer from a public profile turns the second factor into a
        formality.</p>
      </div>
      <p><a href="/">Back to the portal</a></p>
    """


def mfa_staff_body() -> str:
    return f"""
      <span class="pill">Directory</span>
      <h1>Community centre staff</h1>
      <p class="lede">These public profiles help visitors put a name to a role.
      They are not meant to be a source of account-recovery answers.</p>
      <div class="card">
        <ul>
          <li><a href="/staff/amara">Amara &mdash; volunteer coordinator</a></li>
          <li><a href="/staff/rowan">Rowan &mdash; communications volunteer</a></li>
        </ul>
      </div>
      <p><a href="/">Back to the portal</a></p>
    """


def mfa_profile_body(name: str, role: str, book: str, bio: str) -> str:
    return f"""
      <span class="pill">Staff profile</span>
      <h1>{html.escape(name)}</h1>
      <div class="card">
        <h2>{html.escape(role)}</h2>
        <p>{html.escape(bio)}</p>
        <p><strong>Favourite book:</strong> {html.escape(book)}</p>
      </div>
      <p><a href="/staff">Back to the directory</a></p>
    """


def mfa_recover_body(error: str = "") -> str:
    message = f'<p class="danger">{html.escape(error)}</p>' if error else ""
    return f"""
      <span class="pill">Recovery</span>
      <h1>Recover the account</h1>
      {message}
      <div class="card">
        <p>The recovery flow asks one security question. It does not require the
        authenticator code.</p>
        <form method="post" action="/recover">
          <div class="form-row">
            <label for="user">Username</label>
            <input id="user" name="user" autocomplete="username" required>
          </div>
          <div class="form-row">
            <label for="answer">What is your favourite book?</label>
            <input id="answer" name="answer" autocomplete="off" required>
          </div>
          <button class="button" type="submit">Recover account</button>
        </form>
      </div>
      <p><a href="/login">Back to sign-in</a></p>
    """


def mfa_success_body() -> str:
    return f"""
      <span class="pill">Recovered</span>
      <h1>Recovery complete</h1>
      <div class="card">
        <h2>Account access restored</h2>
        <p>The MFA requirement was reset by answering a question whose answer is
        published on the staff directory.</p>
        <p>Training token: <code>{html.escape(FLAG)}</code></p>
      </div>
      <div class="card note">
        <h2>The fix</h2>
        <p>Use pre-generated recovery codes or a second enrolled authenticator,
        store them offline, and never use a fact that is public or guessable.
        Rotate recovery codes after use and notify the account owner.</p>
      </div>
      <p><a href="/">Back to the portal</a></p>
    """


PROVENANCE_ITEMS = {
    "river-cleanup": {
        "title": "River cleanup volunteers",
        "caption": "Staff photo from the riverside cleanup.",
        "source": "Community centre staff page",
        "source_url": "/sources/river-cleanup",
        "uploaded_at": "2026-11-09 16:10",
        "camera": "Pixel 8",
        "software": "Camera 9.2",
        "gps": "42.31, -83.02",
        "corroboration": "Venue log and a second photographer",
        "claim": "The cleanup happened on 9 November.",
        "synthetic": False,
    },
    "lantern-festival": {
        "title": "Lantern festival at the park",
        "caption": "A lantern festival photo submitted anonymously.",
        "source": "Anonymous upload",
        "source_url": "/sources/lantern-festival",
        "uploaded_at": "2026-11-09 18:42",
        "camera": "Not recorded",
        "software": "synthetic-media-studio 2.1",
        "gps": "Not recorded",
        "corroboration": "None found",
        "claim": "The festival happened on 9 November.",
        "synthetic": True,
    },
}

PROVENANCE_SVGS = {
    "river-cleanup": """<svg xmlns="http://www.w3.org/2000/svg" width="640" height="360" viewBox="0 0 640 360">
<rect width="640" height="360" fill="#dbeafe"/>
<circle cx="540" cy="70" r="34" fill="#fde68a"/>
<rect y="230" width="640" height="130" fill="#3b82f6"/>
<path d="M0 230 Q160 190 320 230 T640 230 L640 260 Q480 220 320 260 T0 260 Z" fill="#22c55e"/>
<rect x="70" y="150" width="18" height="90" fill="#92400e"/>
<circle cx="79" cy="145" r="38" fill="#15803d"/>
<rect x="150" y="165" width="14" height="75" fill="#92400e"/>
<circle cx="157" cy="160" r="30" fill="#166534"/>
<rect x="470" y="245" width="110" height="46" rx="6" fill="#f8fafc" stroke="#334155" stroke-width="3"/>
<text x="525" y="274" font-family="sans-serif" font-size="15" text-anchor="middle" fill="#0f172a">RIVER CLEANUP</text>
<text x="320" y="338" font-family="sans-serif" font-size="14" text-anchor="middle" fill="#e0f2fe">Staff photo · 9 November</text>
</svg>""",
    "lantern-festival": """<svg xmlns="http://www.w3.org/2000/svg" width="640" height="360" viewBox="0 0 640 360">
<rect width="640" height="360" fill="#0f172a"/>
<circle cx="90" cy="60" r="24" fill="#fef3c7" opacity="0.8"/>
<circle cx="560" cy="90" r="18" fill="#fef3c7" opacity="0.6"/>
<rect x="250" y="70" width="34" height="46" rx="8" fill="#f59e0b"/>
<rect x="430" y="110" width="34" height="46" rx="8" fill="#f59e0b"/>
<rect x="160" y="160" width="34" height="46" rx="8" fill="#f59e0b"/>
<rect x="300" y="210" width="34" height="46" rx="8" fill="#fbbf24"/>
<path d="M267 116 L267 150" stroke="#fde68a" stroke-width="3"/>
<path d="M447 156 L447 190" stroke="#fde68a" stroke-width="3"/>
<path d="M177 206 L177 240" stroke="#fde68a" stroke-width="3"/>
<text x="320" y="320" font-family="sans-serif" font-size="16" text-anchor="middle" fill="#fef3c7">LANTERN FESTIVAL</text>
<text x="400" y="286" font-family="sans-serif" font-size="11" fill="#94a3b8">submitted anonymously</text>
</svg>""",
}

PROVENANCE_REAL_ID = "river-cleanup"
PROVENANCE_SYNTHETIC_ID = "lantern-festival"


def provenance_records() -> list[dict]:
    records = []
    for item_id, item in PROVENANCE_ITEMS.items():
        record = dict(item)
        record["id"] = item_id
        record["media_url"] = f"/media/{item_id}"
        record["sha256"] = hashlib.sha256(
            PROVENANCE_SVGS[item_id].encode("utf-8")
        ).hexdigest()
        records.append(record)
    return records


def provenance_home_body() -> str:
    return """
      <span class="pill">Verification desk</span>
      <h1>Community newsroom verification desk</h1>
      <p class="lede">Two images were submitted for the same weekend. One is a
      staff photo. The other arrived anonymously with a dramatic caption.</p>
      <div class="card">
        <h2>Your goal</h2>
        <p>Use the archive, provenance records, and source notes to decide which
        item is supported by independent evidence. Then request a verification
        token for that item.</p>
        <p><a class="button" href="/archive">Open the archive</a></p>
      </div>
      <div class="card note">
        <h2>Check in order</h2>
        <p>Source, provenance, corroboration, clues. Metadata is often stripped
        on upload, and a visual artefact is not proof on its own.</p>
      </div>
    """


def provenance_archive_body() -> str:
    cards = "".join(
        f"""
        <div class="card">
          <h2>{html.escape(item['title'])}</h2>
          <img src="{html.escape(item['media_url'])}"
               alt="{html.escape(item['caption'])}"
               style="width:100%;max-width:640px;border-radius:10px;border:1px solid var(--line)">
          <p>{html.escape(item['caption'])}</p>
          <p><a href="/provenance/{html.escape(item['id'])}">Provenance record</a>
          &middot; <a href="{html.escape(item['source_url'])}">Source note</a></p>
        </div>
        """
        for item in provenance_records()
    )
    return f"""
      <span class="pill">Archive</span>
      <h1>Two submissions</h1>
      <p class="lede">The newsroom has not published either item. Compare the
      provenance before you trust the claim.</p>
      {cards}
      <p><a href="/provenance.json">Raw provenance data</a></p>
      <p><a href="/">Back to the verification desk</a></p>
    """


def provenance_detail_body(item: dict) -> str:
    return f"""
      <span class="pill">Provenance</span>
      <h1>{html.escape(item['title'])}</h1>
      <div class="card">
        <img src="{html.escape(item['media_url'])}"
             alt="{html.escape(item['caption'])}"
             style="width:100%;max-width:640px;border-radius:10px;border:1px solid var(--line)">
      </div>
      <table>
        <tr><th>Claim</th><td>{html.escape(item['claim'])}</td></tr>
        <tr><th>Source</th><td>{html.escape(item['source'])}</td></tr>
        <tr><th>Uploaded</th><td>{html.escape(item['uploaded_at'])}</td></tr>
        <tr><th>Camera</th><td>{html.escape(item['camera'])}</td></tr>
        <tr><th>Software</th><td>{html.escape(item['software'])}</td></tr>
        <tr><th>GPS</th><td>{html.escape(item['gps'])}</td></tr>
        <tr><th>Corroboration</th><td>{html.escape(item['corroboration'])}</td></tr>
        <tr><th>SHA-256</th><td><code>{html.escape(item['sha256'])}</code></td></tr>
      </table>
      <div class="card note">
        <h2>Metadata is not a verdict</h2>
        <p>Camera and GPS fields can be edited or stripped. The source and
        independent corroboration carry more weight than one metadata field.</p>
      </div>
      <p><a href="/archive">Back to the archive</a></p>
    """


def provenance_source_body(item: dict) -> str:
    if item["synthetic"]:
        note = (
            "First seen on an anonymous repost account. No original upload, no "
            "camera record, and no independent report of the event. The only "
            "source is the account that posted it."
        )
    else:
        note = (
            "First seen on the community centre staff page. A venue log records "
            "the cleanup, and a second photographer submitted a matching frame "
            "from a different angle."
        )
    return f"""
      <span class="pill">Source note</span>
      <h1>{html.escape(item['title'])}</h1>
      <div class="card">
        <p>{html.escape(note)}</p>
        <p><strong>Source:</strong> {html.escape(item['source'])}</p>
        <p><strong>Corroboration:</strong> {html.escape(item['corroboration'])}</p>
      </div>
      <p><a href="/archive">Back to the archive</a></p>
    """


def provenance_success_body() -> str:
    return f"""
      <span class="pill">Verified</span>
      <h1>Provenance check passed</h1>
      <div class="card">
        <h2>The staff photo is supported</h2>
        <p>The source, venue log, second photographer, and metadata are
        consistent. The anonymous lantern image has no independent support.</p>
        <p>Training token: <code>{html.escape(FLAG)}</code></p>
      </div>
      <div class="card note">
        <h2>What the evidence does not prove</h2>
        <p>It does not prove that every detail in the staff photo is true. It
        supports the specific claim that the cleanup happened and that this
        image came from a known photographer.</p>
      </div>
      <p><a href="/">Back to the verification desk</a></p>
    """


RUGPULL_TREASURY = "0x4b8e2d6f1a3c5e7b9d0f2a4c6e8b1d3f5a7c9e2b"
RUGPULL_COMMUNITY = "0x7a1c3e5b9d2f4a6c8e0b1d3f5a7c9e2b4d6f8a0c"
RUGPULL_DRAINED = "0x9f2c4a7b1e5d8c3f6a2b9d0e4c7f1a8b3d6e9c2f"
RUGPULL_OFFSHORE = "0x3d6e9c2f4a7b1e5d8c3f6a2b9d0e4c7f1a8b3d6"
RUGPULL_EXCHANGE = "0x5a7c9e2b4d6f8a0c1e3b5d7f9a2c4e6b8d0f1a3c"


def rugpull_ledger() -> list[dict]:
    return [
        {
            "id": "tx-001",
            "from": RUGPULL_TREASURY,
            "to": RUGPULL_COMMUNITY,
            "amount": 1000000,
            "asset": "MILK",
            "memo": "initial liquidity",
        },
        {
            "id": "tx-002",
            "from": RUGPULL_COMMUNITY,
            "to": RUGPULL_DRAINED,
            "amount": 950000,
            "asset": "MILK",
            "memo": "liquidity removal",
        },
        {
            "id": "tx-003",
            "from": RUGPULL_DRAINED,
            "to": RUGPULL_OFFSHORE,
            "amount": 940000,
            "asset": "MILK",
            "memo": "bridge to external wallet",
        },
        {
            "id": "tx-004",
            "from": RUGPULL_DRAINED,
            "to": RUGPULL_EXCHANGE,
            "amount": 10000,
            "asset": "MILK",
            "memo": "swap",
        },
    ]


def rugpull_home_body() -> str:
    return """
      <span class="pill">Money</span>
      <h1>$MILK: the community token</h1>
      <p class="lede">A polished token site says it will fund youth programmes.
      The offer has a countdown, a guaranteed return, and an anonymous team.</p>
      <div class="card">
        <h2>Guaranteed 12% weekly returns</h2>
        <p>Airdrop ends in <strong>00:14:59</strong>. Connect your wallet to
        claim your share of the community pool.</p>
        <p><a class="button" href="/claim">Connect wallet</a></p>
      </div>
      <div class="card">
        <h2>Built by the community</h2>
        <p>Team: <code>@milkdev</code> and <code>@anon_ops</code>. Audit
        pending. Whitepaper coming soon.</p>
        <p>Influencer quote: &ldquo;I put my community's savings in $MILK.&rdquo;</p>
      </div>
      <div class="card">
        <h2>Investigate</h2>
        <p><a href="/ledger.json">View the public ledger</a> &middot;
        <a href="/team">Team page</a> &middot;
        <a href="/report">Report a scam</a></p>
      </div>
      <div class="card note">
        <h2>Defensive only</h2>
        <p>This is a simulation. There is no real token, wallet, or money. Never
        connect a real wallet to an unknown site, and never share a seed phrase.</p>
      </div>
    """


def rugpull_team_body() -> str:
    return """
      <span class="pill">Team</span>
      <h1>The $MILK team</h1>
      <div class="card">
        <p><code>@milkdev</code> &mdash; anonymous founder</p>
        <p><code>@anon_ops</code> &mdash; anonymous operations</p>
        <p>No company name, no registered address, no independent audit, and no
        named advisors.</p>
      </div>
      <p><a href="/">Back to the token page</a></p>
    """


def rugpull_claim_body() -> str:
    return """
      <span class="pill">Simulation</span>
      <h1>Wallet connection is disabled</h1>
      <div class="card">
        <p>This training page never connects to a wallet. The real red flag is
        the request: a &ldquo;free airdrop&rdquo; that asks you to connect a
        wallet can drain the wallet's approvals.</p>
        <p>Never enter a seed phrase on a website. A legitimate airdrop does not
        need it.</p>
      </div>
      <p><a href="/">Back to the token page</a></p>
    """


def rugpull_report_body() -> str:
    return """
      <span class="pill">Report</span>
      <h1>What to do next</h1>
      <div class="card">
        <h2>Red-flag card</h2>
        <ul>
          <li>Guaranteed returns</li>
          <li>Urgency or a countdown timer</li>
          <li>&ldquo;Free airdrop&rdquo; that asks you to connect a wallet</li>
          <li>Anonymous team and no audit</li>
          <li>Credibility from one influencer only</li>
          <li>No paper trail or regulatory protection</li>
        </ul>
        <p>Any two of these is a reason to walk away.</p>
      </div>
      <div class="card note">
        <h2>If money is already gone</h2>
        <p>Stop paying. Do not use a &ldquo;recovery agent&rdquo; who asks for a
        fee; that is often a second-layer scam. Report to a trusted adult, your
        bank, and the appropriate consumer-protection or police channel.</p>
      </div>
      <p><a href="/">Back to the token page</a></p>
    """


def rugpull_case_body() -> str:
    return f"""
      <span class="pill">Case file</span>
      <h1>The liquidity trail</h1>
      <div class="card">
        <h2>Drained wallet identified</h2>
        <p>The wallet <code>{html.escape(RUGPULL_DRAINED)}</code> received the
        community liquidity and forwarded almost all of it to an external
        wallet. The small remainder was swapped.</p>
        <p>Training token: <code>{html.escape(FLAG)}</code></p>
      </div>
      <div class="card note">
        <h2>Scam anatomy</h2>
        <p>Hook, trust builders, the ask, the exit, and who profited. The
        &ldquo;recovery agent&rdquo; offer is the second layer: it targets people
        who have already lost money.</p>
      </div>
      <p><a href="/">Back to the token page</a></p>
    """


def access_log() -> str:
    lines = [
        '10.0.40.15 - - [18/Mar/2026:09:01:12 +0000] "GET / HTTP/1.1" 200 512 "-" "Mozilla/5.0"',
        '10.0.40.22 - - [18/Mar/2026:09:02:45 +0000] "GET /schedule HTTP/1.1" 200 1203 "-" "Mozilla/5.0"',
        '10.0.40.31 - - [18/Mar/2026:09:04:03 +0000] "GET /health HTTP/1.1" 200 32 "-" "curl/8.5.0"',
        '10.0.40.15 - - [18/Mar/2026:09:06:20 +0000] "GET /?debug=' + DECOY_FLAG + ' HTTP/1.1" 200 512 "-" "Mozilla/5.0"',
        '203.0.113.66 - - [18/Mar/2026:09:12:10 +0000] "GET /admin HTTP/1.1" 404 189 "-" "sqlmap/1.8"',
        '203.0.113.66 - - [18/Mar/2026:09:12:13 +0000] "GET /wp-login.php HTTP/1.1" 404 189 "-" "sqlmap/1.8"',
        '203.0.113.66 - - [18/Mar/2026:09:12:17 +0000] "GET /backup.sql HTTP/1.1" 404 189 "-" "sqlmap/1.8"',
        '203.0.113.66 - - [18/Mar/2026:09:12:22 +0000] "GET /admin?token=' + FLAG + ' HTTP/1.1" 200 512 "-" "sqlmap/1.8"',
        '10.0.40.22 - - [18/Mar/2026:09:14:51 +0000] "GET /schedule HTTP/1.1" 200 1203 "-" "Mozilla/5.0"',
        '10.0.40.31 - - [18/Mar/2026:09:16:08 +0000] "GET /health HTTP/1.1" 200 32 "-" "curl/8.5.0"',
        '10.0.40.15 - - [18/Mar/2026:09:18:33 +0000] "GET / HTTP/1.1" 200 512 "-" "Mozilla/5.0"',
    ]
    return "\n".join(lines) + "\n"


def evidence_zip() -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        files = {
            "evidence/README.txt": (
                "Shared folder export\n"
                "====================\n\n"
                "This archive was created during a classroom cleanup.\n"
                "The useful training token is in archive/old/flag.txt.\n"
                "The other files are decoys kept for practice.\n"
            ),
            "evidence/notes/team.txt": "Team: RangeBox practice group\n",
            "evidence/notes/schedule.txt": "Monday: accounts\nTuesday: files\n",
            "evidence/archive/old/flag.txt": f"Training token: {FLAG}\n",
            "evidence/archive/old/notes.txt": "Old notes. Nothing important here.\n",
            "evidence/archive/old/decoy.txt": f"Decoy token: {DECOY_FLAG}\n",
            "evidence/photos/readme.txt": "No photos in this training archive.\n",
        }
        for name, content in files.items():
            archive.writestr(name, content)
    return buffer.getvalue()


class Handler(BaseHTTPRequestHandler):
    server_version = "RangeBoxBasics/1.0"

    def log_message(self, format, *args):
        return

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
            "default-src 'none'; style-src 'unsafe-inline'; "
            "img-src 'self' data:; base-uri 'none'; form-action 'self'; "
            "frame-ancestors 'none'",
        )
        if MODE == "network":
            self.send_header("X-OCR-Token", FLAG)
        self.send_header("Cache-Control", "no-store")
        for key, value in (extra_headers or {}).items():
            self.send_header(key, value)
        self.end_headers()
        if not getattr(self, "_head_only", False):
            self.wfile.write(data)

    def _read_body(self) -> str:
        length = int(self.headers.get("Content-Length", "0") or 0)
        if length <= 0:
            return ""
        return self.rfile.read(length).decode("utf-8", "replace")

    def do_POST(self):
        path = self.path.split("?", 1)[0]
        if MODE == "mfa_recovery" and path in ("/login", "/recover"):
            form = parse_qs(self._read_body())
            user = (form.get("user") or [""])[0].strip()
            if path == "/login":
                password = (form.get("password") or [""])[0]
                if user == MFA_USER and password == MFA_PASSWORD:
                    self._send(200, page("MFA required", mfa_mfa_body()))
                else:
                    self._send(
                        401,
                        page("Sign in", mfa_login_body("Invalid username or password.")),
                    )
                return
            answer = (form.get("answer") or [""])[0].strip()
            if user == MFA_USER and answer == MFA_ANSWER:
                self._send(200, page("Recovered", mfa_success_body()))
            else:
                self._send(
                    403,
                    page(
                        "Recovery failed",
                        mfa_recover_body("That answer did not match the account."),
                    ),
                )
            return
        self._send(405, page("Method not allowed", "<h1>Method not allowed</h1>"))

    def do_HEAD(self):
        self._head_only = True
        self.do_GET()

    def do_GET(self):
        path = self.path.split("?", 1)[0]

        if MODE == "welcome":
            if path in ("/", "/index.html"):
                body = page("Welcome", welcome_body())
            elif path == "/welcome.txt":
                self._send(200, f"RangeBox first steps\n\nTraining token: {FLAG}\n", "text/plain; charset=utf-8")
                return
            else:
                self._send(404, page("Not found", "<h1>Not found</h1>"))
                return

        elif MODE == "filehunt":
            if path in ("/", "/index.html"):
                body = page("File hunt", filehunt_body())
            elif path == "/evidence.zip":
                self._send(200, evidence_zip(), "application/zip", {"Content-Disposition": 'attachment; filename="evidence.zip"'})
                return
            else:
                self._send(404, page("Not found", "<h1>Not found</h1>"))
                return

        elif MODE == "network":
            if path in ("/", "/index.html"):
                body = page("Network basics", network_body())
            elif path == "/status.json":
                payload = {
                    "service": "rangebox-basics",
                    "status": "ok",
                    "lesson": "Read the X-OCR-Token response header.",
                }
                self._send(200, json.dumps(payload), "application/json")
                return
            else:
                self._send(404, page("Not found", "<h1>Not found</h1>"))
                return

        elif MODE == "logs":
            if path in ("/", "/index.html"):
                body = page("Log detective", logs_body())
            elif path == "/access.log":
                self._send(200, access_log(), "text/plain; charset=utf-8")
                return
            else:
                self._send(404, page("Not found", "<h1>Not found</h1>"))
                return

        elif MODE in ("cyberchef_b64", "cyberchef_caesar", "cyberchef_layers"):
            if path in ("/", "/index.html"):
                body = page("CyberChef practice", cyberchef_body(MODE))
            elif path == "/message.txt":
                self._send(
                    200,
                    _cyberchef_message(MODE) + "\n",
                    "text/plain; charset=utf-8",
                )
                return
            else:
                self._send(404, page("Not found", "<h1>Not found</h1>"))
                return

        elif MODE == "linkcheck":
            if path in ("/", "/index.html"):
                body = page("Read the link", linkcheck_body())
            elif path == "/message.txt":
                self._send(200, _linkcheck_message(), "text/plain; charset=utf-8")
                return
            else:
                self._send(404, page("Not found", "<h1>Not found</h1>"))
                return

        elif MODE == "filetype":
            if path in ("/", "/index.html"):
                body = page("File safety", filetype_body())
            elif path == "/downloads/":
                self._send(200, page("Shared folder", filetype_listing()))
                return
            elif path == "/downloads/event-photo.png":
                self._send(
                    200,
                    _disguised_zip(
                        FLAG,
                        "This archive was renamed to look like a photo. "
                        "The extension is a label, not evidence.",
                    ),
                    "application/octet-stream",
                    {"Content-Disposition": 'attachment; filename="event-photo.png"'},
                )
                return
            elif path.startswith("/downloads/"):
                name = path[len("/downloads/"):]
                content = FILE_DECOYS.get(name)
                if content is None:
                    self._send(404, page("Not found", "<h1>Not found</h1>"))
                    return
                self._send(
                    200,
                    content,
                    "text/plain; charset=utf-8",
                    {"Content-Disposition": f'attachment; filename="{name}"'},
                )
                return
            else:
                self._send(404, page("Not found", "<h1>Not found</h1>"))
                return

        elif MODE == "capstone":
            if path in ("/", "/index.html"):
                body = page("Forwarded message", capstone_body())
            elif path == "/notice.txt":
                self._send(200, _capstone_notice(), "text/plain; charset=utf-8")
                return
            elif path == "/files/grant-pack.png":
                self._send(
                    200,
                    _disguised_zip(
                        FLAG,
                        "The grant pack was renamed to look like a PNG image. "
                        "Check the real file type before opening it.",
                    ),
                    "application/octet-stream",
                    {"Content-Disposition": 'attachment; filename="grant-pack.png"'},
                )
                return
            elif path == "/files/README.txt":
                self._send(
                    200,
                    "Practice mirror for the grant review exercise.\n"
                    "Use the decoded file path from the forwarded notice.\n",
                    "text/plain; charset=utf-8",
                )
                return
            else:
                self._send(404, page("Not found", "<h1>Not found</h1>"))
                return

        elif MODE == "emailmeta":
            if path in ("/", "/index.html"):
                body = page("Email metadata", emailmeta_body())
            elif path == "/email.eml":
                self._send(
                    200,
                    _email_message(),
                    "message/rfc822; charset=utf-8",
                    {"Content-Disposition": 'attachment; filename="reported-email.eml"'},
                )
                return
            else:
                self._send(404, page("Not found", "<h1>Not found</h1>"))
                return

        elif MODE == "mfa_recovery":
            if path in ("/", "/index.html"):
                body = page("MFA recovery", mfa_home_body())
            elif path == "/login":
                body = page("Staff sign-in", mfa_login_body())
            elif path == "/mfa":
                body = page("MFA required", mfa_mfa_body())
            elif path == "/staff":
                body = page("Staff directory", mfa_staff_body())
            elif path == "/staff/amara":
                body = page(
                    "Amara",
                    mfa_profile_body(
                        "Amara",
                        "Volunteer coordinator",
                        "The Lantern Keeper",
                        "Amara runs the Tuesday reading circle and the summer "
                        "book drive.",
                    ),
                )
            elif path == "/staff/rowan":
                body = page(
                    "Rowan",
                    mfa_profile_body(
                        "Rowan",
                        "Communications volunteer",
                        "North of the River",
                        "Rowan looks after the newsletter and the community "
                        "calendar.",
                    ),
                )
            elif path == "/recover":
                body = page("Recover the account", mfa_recover_body())
            else:
                self._send(404, page("Not found", "<h1>Not found</h1>"))
                return

        elif MODE == "provenance":
            if path in ("/", "/index.html"):
                body = page("Verification desk", provenance_home_body())
            elif path == "/archive":
                body = page("Archive", provenance_archive_body())
            elif path == "/provenance.json":
                self._send(
                    200,
                    json.dumps(provenance_records(), indent=2),
                    "application/json",
                )
                return
            elif path.startswith("/provenance/"):
                item_id = path[len("/provenance/"):]
                item = PROVENANCE_ITEMS.get(item_id)
                if not item:
                    self._send(404, page("Not found", "<h1>Not found</h1>"))
                    return
                record = next(
                    r for r in provenance_records() if r["id"] == item_id
                )
                body = page("Provenance record", provenance_detail_body(record))
            elif path.startswith("/sources/"):
                item_id = path[len("/sources/"):]
                item = PROVENANCE_ITEMS.get(item_id)
                if not item:
                    self._send(404, page("Not found", "<h1>Not found</h1>"))
                    return
                body = page("Source note", provenance_source_body(item))
            elif path.startswith("/media/"):
                item_id = path[len("/media/"):]
                svg = PROVENANCE_SVGS.get(item_id)
                if not svg:
                    self._send(404, page("Not found", "<h1>Not found</h1>"))
                    return
                self._send(200, svg, "image/svg+xml")
                return
            elif path == "/verify":
                query = self.path.split("?", 1)[1] if "?" in self.path else ""
                params = parse_qs(query)
                item_id = (params.get("id") or [""])[0]
                if item_id == PROVENANCE_REAL_ID:
                    body = page("Verified", provenance_success_body())
                elif item_id == PROVENANCE_SYNTHETIC_ID:
                    self._send(
                        403,
                        page(
                            "Synthetic media",
                            "<h1>Verification declined</h1>"
                            "<p>This item is synthetic. It has no independent "
                            "provenance token.</p>"
                            "<p><a href='/archive'>Back to the archive</a></p>",
                        ),
                    )
                    return
                else:
                    self._send(
                        404,
                        page("Not found", "<h1>Unknown media item</h1>"),
                    )
                    return
            else:
                self._send(404, page("Not found", "<h1>Not found</h1>"))
                return

        elif MODE == "rugpull":
            if path in ("/", "/index.html"):
                body = page("$MILK", rugpull_home_body())
            elif path == "/ledger.json":
                self._send(
                    200,
                    json.dumps(rugpull_ledger(), indent=2),
                    "application/json",
                )
                return
            elif path == "/team":
                body = page("Team", rugpull_team_body())
            elif path == "/claim":
                body = page("Wallet connection", rugpull_claim_body())
            elif path == "/report":
                body = page("Report a scam", rugpull_report_body())
            elif path == "/case":
                query = self.path.split("?", 1)[1] if "?" in self.path else ""
                params = parse_qs(query)
                wallet = (params.get("wallet") or [""])[0].strip().lower()
                if wallet == RUGPULL_DRAINED.lower():
                    body = page("Case file", rugpull_case_body())
                else:
                    self._send(
                        404,
                        page(
                            "No case file",
                            "<h1>No case file for that wallet</h1>"
                            "<p>Trace the ledger and use the wallet that "
                            "received the community liquidity.</p>"
                            "<p><a href='/ledger.json'>Open the ledger</a></p>",
                        ),
                    )
                    return
            else:
                self._send(404, page("Not found", "<h1>Not found</h1>"))
                return

        elif MODE == "browser":
            if path in ("/", "/index.html"):
                body = page("Browser basics", browser_body())
            elif path == "/staff-notes.html":
                body = page(
                    "Staff notes",
                    f"<h1>Staff notes</h1><p>This page is mostly empty on purpose.</p>"
                    f"<!-- Training token: {FLAG} -->",
                )
            elif path == "/robots.txt":
                self._send(200, "User-agent: *\nDisallow: /staff-notes.html\n", "text/plain; charset=utf-8")
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

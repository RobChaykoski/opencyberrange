#!/usr/bin/env python3
"""Convert the release review markdown files to print-ready HTML.

The HTML is rendered to PDF by Chromium (see scripts/html-to-pdf.mjs). Keeping
the source as markdown and the styling in CSS gives clean page breaks, tables,
and headings without a heavyweight PDF toolchain.
"""

from __future__ import annotations

import html
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCES = [
    (ROOT / "docs" / "reviews" / "TECHNICAL-DEBT-REVIEW-2026-11.md", "Technical debt review - 2.7.x"),
    (ROOT / "docs" / "reviews" / "DATA-ANALYST-SIGNOFF-2026-11.md", "Data analyst review and sign-off - 2.7.x"),
    (ROOT / "docs" / "reviews" / "ADMIN-SETTINGS-REVIEW-2026-11.md", "System administrator review - server settings"),
    (ROOT / "docs" / "PROD-DEPLOYMENT-VALIDATION-MATRIX.md", "Production deployment validation matrix"),
]

CSS = """
@page { size: A4; margin: 18mm 16mm; }
* { box-sizing: border-box; }
body { font-family: -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
       font-size: 10.5pt; line-height: 1.45; color: #111827; margin: 0; }
h1 { font-size: 22pt; margin: 0 0 4mm; color: #0f172a; border-bottom: 2px solid #2563eb; padding-bottom: 3mm; }
h2 { font-size: 14pt; margin: 7mm 0 2mm; color: #1e293b; }
h3 { font-size: 11.5pt; margin: 5mm 0 1.5mm; color: #334155; }
p { margin: 0 0 2.5mm; }
ul, ol { margin: 0 0 3mm 5mm; padding: 0; }
li { margin-bottom: 1.2mm; }
table { width: 100%; border-collapse: collapse; margin: 2mm 0 4mm; font-size: 8.8pt; page-break-inside: auto; }
thead { display: table-header-group; }
tr { page-break-inside: avoid; }
th, td { border: 1px solid #cbd5e1; padding: 1.5mm 2mm; vertical-align: top; text-align: left; }
th { background: #f1f5f9; font-weight: 700; }
code { background: #f1f5f9; padding: 0 1mm; border-radius: 2px; font-size: 9pt; }
a { color: #1d4ed8; text-decoration: none; }
strong { color: #0f172a; }
.meta { color: #64748b; font-size: 9pt; margin-bottom: 5mm; }
"""


def inline(text: str) -> str:
    text = html.escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
    return text


def convert(markdown: str, title: str) -> str:
    out: list[str] = [f"<h1>{html.escape(title)}</h1>"]
    lines = markdown.splitlines()
    i = 0
    in_list: str | None = None

    def close_list():
        nonlocal in_list
        if in_list:
            out.append(f"</{in_list}>")
            in_list = None

    while i < len(lines):
        line = lines[i].rstrip()
        if not line.strip():
            close_list()
            i += 1
            continue

        if line.startswith("|"):
            close_list()
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                cells = [c.strip() for c in lines[i].strip("|").split("|")]
                if not all(set(c) <= {"-", ":", " "} for c in cells):
                    rows.append(cells)
                i += 1
            if rows:
                out.append("<table><thead><tr>")
                out.extend(f"<th>{inline(c)}</th>" for c in rows[0])
                out.append("</tr></thead><tbody>")
                for row in rows[1:]:
                    out.append("<tr>")
                    out.extend(f"<td>{inline(c)}</td>" for c in row)
                    out.append("</tr>")
                out.append("</tbody></table>")
            continue

        if line.startswith("# "):
            close_list()
            out.append(f"<h1>{inline(line[2:])}</h1>")
        elif line.startswith("## "):
            close_list()
            out.append(f"<h2>{inline(line[3:])}</h2>")
        elif line.startswith("### "):
            close_list()
            out.append(f"<h3>{inline(line[4:])}</h3>")
        elif line.startswith("- "):
            if in_list != "ul":
                close_list()
                out.append("<ul>")
                in_list = "ul"
            out.append(f"<li>{inline(line[2:])}</li>")
        elif re.match(r"^\d+\. ", line):
            if in_list != "ol":
                close_list()
                out.append("<ol>")
                in_list = "ol"
            item_text = re.sub(r"^\d+\. ", "", line)
            out.append(f"<li>{inline(item_text)}</li>")
        else:
            close_list()
            out.append(f"<p>{inline(line)}</p>")
        i += 1

    close_list()
    body = "\n".join(out)
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>{html.escape(title)}</title>
<style>{CSS}</style>
</head><body>{body}</body></html>"""


def main() -> int:
    for source, title in SOURCES:
        if not source.exists():
            raise SystemExit(f"missing source: {source}")
        target = source.with_suffix(".html")
        target.write_text(convert(source.read_text(encoding="utf-8"), title), encoding="utf-8")
        print(f"wrote {target.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

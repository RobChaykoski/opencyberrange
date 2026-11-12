#!/usr/bin/env python3
"""Render the release review markdown files to PDF.

Simple, dependency-light renderer: headings, bullets, tables, and paragraphs.
The PDFs are the offline copies; the markdown files remain the source.
"""

from __future__ import annotations

import pathlib
import re

from fpdf import FPDF

ROOT = pathlib.Path(__file__).resolve().parents[1]
REVIEWS = [
    ("TECHNICAL-DEBT-REVIEW-2026-11.md", "Technical debt review - 2.7.x"),
    ("DATA-ANALYST-SIGNOFF-2026-11.md", "Data analyst review and sign-off - 2.7.x"),
    ("ADMIN-SETTINGS-REVIEW-2026-11.md", "System administrator review - server settings"),
]
MATRIX = ROOT / "docs" / "PROD-DEPLOYMENT-VALIDATION-MATRIX.md"


def clean(text: str) -> str:
    text = text.replace("**", "").replace("`", "")
    text = text.replace("\u2014", "-").replace("\u2013", "-")
    text = text.replace("\u2019", "'").replace("\u201c", '"').replace("\u201d", '"')
    text = text.replace("\u2192", "->")
    return text.encode("latin-1", "replace").decode("latin-1")


def prepare(text: str) -> str:
    """Wrap very long unbroken tokens so fpdf can lay them out.

    The matrix evidence column can contain long paths and URLs. fpdf's
    character wrapping can stall on a token wider than the cell, so insert
    break opportunities before rendering.
    """
    parts = []
    for part in text.split(" "):
        if len(part) <= 90:
            parts.append(part)
        else:
            parts.extend(part[i:i + 90] for i in range(0, len(part), 90))
    return clean(" ".join(parts))


class ReviewPDF(FPDF):
    def __init__(self, title: str):
        super().__init__(format="A4")
        self.title_text = clean(title)
        self.set_auto_page_break(auto=True, margin=18)
        self.set_margins(18, 18, 18)

    def header(self):
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(90, 90, 90)
        self.cell(0, 6, "OpenCyberRange - release review", align="L")
        self.ln(8)
        self.set_text_color(0, 0, 0)

    def footer(self):
        self.set_y(-14)
        self.set_font("Helvetica", "", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 6, f"{self.title_text}  |  page {self.page_no()}", align="C")


def render(markdown_path: pathlib.Path, title: str, out_path: pathlib.Path) -> None:
    pdf = ReviewPDF(title)
    pdf.add_page()
    lines = markdown_path.read_text(encoding="utf-8").splitlines()
    in_table = False

    def write_line(text: str, height: float) -> None:
        text = prepare(text)
        if not text:
            pdf.ln(height)
            return
        # fpdf can stall when a single token is wider than the cell. Chunking
        # keeps every cell short enough to render and preserves the text.
        for start in range(0, len(text), 110):
            pdf.cell(0, height, text[start:start + 110])
            pdf.ln(height)

    for raw in lines:
        line = raw.rstrip()
        if not line.strip():
            if in_table:
                in_table = False
                pdf.ln(2)
            else:
                pdf.ln(1.5)
            continue

        if line.startswith("|"):
            cells = [c.strip() for c in line.strip("|").split("|")]
            if all(set(c) <= {"-", ":", " "} for c in cells):
                continue
            in_table = True
            pdf.set_font("Helvetica", "", 7.5)
            write_line(" | ".join(c for c in cells if c), 4.2)
            continue

        if in_table:
            in_table = False
            pdf.ln(2)

        if line.startswith("# "):
            pdf.set_font("Helvetica", "B", 18)
            write_line(line[2:], 9)
            pdf.ln(2)
        elif line.startswith("## "):
            pdf.ln(2)
            pdf.set_font("Helvetica", "B", 13)
            write_line(line[3:], 7)
            pdf.ln(1)
        elif line.startswith("### "):
            pdf.set_font("Helvetica", "B", 11)
            write_line(line[4:], 6)
        elif line.startswith("- "):
            pdf.set_font("Helvetica", "", 9.5)
            write_line("  - " + line[2:], 5)
        elif re.match(r"^\d+\. ", line):
            pdf.set_font("Helvetica", "", 9.5)
            write_line(line, 5)
        else:
            pdf.set_font("Helvetica", "", 9.5)
            write_line(line, 5)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(out_path))
    print(f"wrote {out_path.relative_to(ROOT)}")


def main() -> int:
    for name, title in REVIEWS:
        source = ROOT / "docs" / "reviews" / name
        render(source, title, source.with_suffix(".pdf"))
    render(MATRIX, "Production deployment validation matrix", ROOT / "docs" / "reviews" / "PROD-VALIDATION-MATRIX-2026-11.pdf")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


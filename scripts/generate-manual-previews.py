"""Generate preview images for the Career Atlas and Momentum manual pages.

These are deterministic design previews, not captures of a live deployment.
They keep the manual readable and the documentation asset check green until the
real screenshots are captured from the development host with
``scripts/ui-manual-screenshots.mjs``.

Usage:
    python scripts/generate-manual-previews.py

Outputs:
    Manual-Lite/02_Student_Guide/img/profile-momentum.png
    Manual-Lite/02_Student_Guide/img/profile-careers.png
    Manual-Lite/04_Admin_Guide/img/admin-settings-features.png
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
STUDENT_IMG = ROOT / "Manual-Lite" / "02_Student_Guide" / "img"
ADMIN_IMG = ROOT / "Manual-Lite" / "04_Admin_Guide" / "img"

# The same semantic roles as the frontend tokens. These are previews, so the
# values are copied here rather than importing a browser stylesheet.
BG = "#0f172a"
PANEL = "#1e293b"
PANEL_ALT = "#172033"
BORDER = "#334155"
TEXT = "#f8fafc"
SECONDARY = "#94a3b8"
MUTED = "#64748b"
ACCENT = "#2563eb"
ACCENT_TEXT = "#60a5fa"
ACCENT_BG = "#1e3a5f"
SUCCESS = "#22c55e"
WARNING = "#f59e0b"
PURPLE = "#8b5cf6"

FONT_DIR = Path(__file__).resolve().parents[1] / ".venv" / "Lib" / "site-packages" / "matplotlib" / "mpl-data" / "fonts" / "ttf"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    candidate = FONT_DIR / name
    if candidate.exists():
        return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def rounded(draw: ImageDraw.ImageDraw, box, radius=10, fill=PANEL, outline=BORDER, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def label(draw: ImageDraw.ImageDraw, xy, value: str, size=14, color=SECONDARY, bold=False, anchor="la"):
    draw.text(xy, value, font=font(size, bold), fill=color, anchor=anchor)


def wrap_text(draw: ImageDraw.ImageDraw, value: str, size: int, max_width: int) -> list[str]:
    """Wrap a sentence into lines that fit the preview column."""
    words = value.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if draw.textlength(candidate, font=font(size)) <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def paragraph(draw: ImageDraw.ImageDraw, xy, value: str, size: int, color: str, max_width: int, line_height: int):
    x, y = xy
    for line in wrap_text(draw, value, size, max_width):
        label(draw, (x, y), line, size, color)
        y += line_height


def pill(draw: ImageDraw.ImageDraw, xy, value: str, *, fill=PANEL, color=SECONDARY, size=12, pad=8):
    x, y = xy
    f = font(size, True)
    width = int(draw.textlength(value, font=f)) + pad * 2
    height = size + pad
    draw.rounded_rectangle((x, y, x + width, y + height), radius=999, fill=fill, outline=BORDER)
    draw.text((x + pad, y + height / 2), value, font=f, fill=color, anchor="lm")
    return width


def progress(draw: ImageDraw.ImageDraw, box, pct: float, color=ACCENT, track=PANEL_ALT):
    x1, y1, x2, y2 = box
    draw.rounded_rectangle(box, radius=999, fill=track)
    width = max(0, min(1, pct / 100)) * (x2 - x1)
    if width:
        draw.rounded_rectangle((x1, y1, x1 + width, y2), radius=999, fill=color)


def sidebar(draw: ImageDraw.ImageDraw, height: int, active: str):
    draw.rectangle((0, 0, 230, height), fill="#0b1220")
    draw.line((230, 0, 230, height), fill=BORDER)
    label(draw, (24, 26), "SWOCTS", 18, TEXT, True)
    label(draw, (24, 50), "CYBER RANGE", 10, ACCENT_TEXT, True)
    items = ["Ops Center", "Academy", "Instructor", "Admin", "Profile"]
    y = 110
    for item in items:
        if item == active:
            draw.rounded_rectangle((14, y - 8, 216, y + 28), radius=8, fill=ACCENT_BG)
            label(draw, (30, y), item, 14, ACCENT_TEXT, True)
        else:
            label(draw, (30, y), item, 14, SECONDARY)
        y += 48


def page_title(draw: ImageDraw.ImageDraw, title: str, subtitle: str, *, x=270, y=34, width=1100):
    label(draw, (x, y), title, 28, TEXT, True)
    label(draw, (x, y + 42), subtitle, 14, SECONDARY)
    draw.line((x, y + 76, x + width, y + 76), fill=BORDER)


def stat_card(draw: ImageDraw.ImageDraw, box, title: str, value: str, detail: str, color=TEXT):
    rounded(draw, box)
    x1, y1, x2, y2 = box
    label(draw, (x1 + 18, y1 + 16), title.upper(), 10, MUTED, True)
    label(draw, (x1 + 18, y1 + 36), value, 28, color, True)
    label(draw, (x1 + 18, y1 + 76), detail, 11, SECONDARY)


def branch_card(draw: ImageDraw.ImageDraw, box, name: str, status: str, pct: int, color: str, numbers: str):
    rounded(draw, box)
    x1, y1, x2, y2 = box
    draw.rectangle((x1, y1, x1 + 4, y2), fill=color)
    label(draw, (x1 + 16, y1 + 12), name, 13, TEXT, True)
    label(draw, (x2 - 16, y1 + 12), status.upper(), 10, color, True, "ra")
    progress(draw, (x1 + 16, y1 + 38, x2 - 16, y1 + 44), pct, color)
    label(draw, (x1 + 16, y1 + 54), numbers, 10, MUTED)


def draw_momentum() -> Path:
    width, height = 1400, 1120
    image = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(image)
    sidebar(draw, height, "Profile")
    page_title(draw, "Profile", "Momentum, Cyber DNA, and career practice evidence")

    x = 270
    y = 130
    label(draw, (x, y), "MOMENTUM AND FRICTION", 11, MUTED, True)
    label(draw, (x, y + 22), "Where practice is moving", 22, TEXT, True)
    label(
        draw,
        (x, y + 56),
        "Recent half of completed exercises compared with the earlier half. Friction uses hints, reattempts, time over estimate, and unfinished exercises.",
        12,
        SECONDARY,
    )
    pill(draw, (1180, y), "v2026.1", fill=PANEL, color=MUTED, size=11)

    stats = [
        ("Completed", "18", "22 started"),
        ("Clean solves", "61%", "11 of 18"),
        ("Active branches", "5/6", "practice breadth"),
        ("Friction branches", "2", "2 gaining"),
    ]
    sx = x
    for title, value, detail in stats:
        stat_card(draw, (sx, y + 90, sx + 250, y + 180), title, value, detail)
        sx += 265

    cards = [
        ("Gaining", SUCCESS, "Defender", "Clean-solve rate moved from 33% to 67%."),
        ("Friction", WARNING, "Tester", "58% hint use, 42% first-attempt, 2 unfinished."),
        ("Next move", ACCENT_TEXT, "Next move", "Retry one Tester exercise with hints closed, then write the step that unlocked it."),
    ]
    cx = x
    for title, color, name, body in cards:
        box = (cx, y + 205, cx + 350, y + 340)
        rounded(draw, box)
        label(draw, (box[0] + 18, box[1] + 16), title, 14, color, True)
        label(draw, (box[0] + 18, box[1] + 44), name, 13, TEXT, True)
        paragraph(draw, (box[0] + 18, box[1] + 70), body, 11, SECONDARY, 310, 16)
        cx += 365

    label(draw, (x, y + 370), "Branch read", 16, TEXT, True)
    label(draw, (x + 140, y + 374), "Recent half compared with the earlier half", 11, MUTED)
    branches = [
        ("Explorer", "Gaining", 22, SUCCESS, "6 done · 17% hints · 83% first try"),
        ("Builder", "Steady", 38, ACCENT, "5 done · 40% hints · 60% first try"),
        ("Tester", "Friction", 64, WARNING, "3 done · 58% hints · 42% first try"),
        ("Defender", "Gaining", 18, SUCCESS, "2 done · 0% hints · 100% first try"),
        ("Investigator", "Steady", 30, ACCENT, "1 done · 0% hints · 100% first try"),
        ("Leader", "No evidence yet", 0, MUTED, "0 done · no evidence yet"),
    ]
    bx, by = x, y + 400
    for index, (name, status, pct, color, numbers) in enumerate(branches):
        col = index % 3
        row = index // 3
        box = (bx + col * 365, by + row * 120, bx + col * 365 + 350, by + row * 120 + 105)
        branch_card(draw, box, name, status, pct, color, numbers)

    label(draw, (x, y + 660), "Where the friction is", 16, TEXT, True)
    stuck = [
        ("Request Smuggling", "Tester", "High hint use — 3 hints on Request Smuggling"),
        ("Traffic Triage", "Defender", "Started but not finished — 2 starts, no completion"),
        ("Memory Analysis", "Investigator", "Took much longer than estimated — 95 min against a 45 min estimate"),
    ]
    sx = x
    for name, branch, body in stuck:
        box = (sx, y + 690, sx + 350, y + 790)
        rounded(draw, box)
        label(draw, (box[0] + 16, box[1] + 14), name, 13, TEXT, True)
        label(draw, (box[0] + 16, box[1] + 36), branch, 10, MUTED, True)
        paragraph(draw, (box[0] + 16, box[1] + 58), body, 10, SECONDARY, 310, 15)
        sx += 365

    label(
        draw,
        (x, y + 830),
        "Momentum and friction are descriptive signals from your own records. They are not grades, a ranking, or a prediction.",
        10,
        MUTED,
    )

    STUDENT_IMG.mkdir(parents=True, exist_ok=True)
    target = STUDENT_IMG / "profile-momentum.png"
    image.save(target, format="PNG", optimize=True)
    return target


def node(draw: ImageDraw.ImageDraw, cx: int, cy: int, pct: int, color: str, unlocked: bool):
    draw.ellipse((cx - 22, cy - 22, cx + 22, cy + 22), fill=PANEL_ALT, outline=BORDER, width=2)
    if pct:
        draw.arc((cx - 18, cy - 18, cx + 18, cy + 18), start=-90, end=-90 + int(360 * pct / 100), fill=color, width=3)
    if unlocked:
        draw.line((cx - 7, cy, cx - 1, cy + 6), fill=color, width=3)
        draw.line((cx - 1, cy + 6, cx + 9, cy - 7), fill=color, width=3)
    else:
        draw.rounded_rectangle((cx - 7, cy - 2, cx + 7, cy + 10), radius=2, outline=MUTED, width=2)
        draw.arc((cx - 6, cy - 10, cx + 6, cy + 2), start=180, end=360, fill=MUTED, width=2)


def lane(draw: ImageDraw.ImageDraw, box, title: str, score: int, nodes):
    rounded(draw, box)
    x1, y1, x2, y2 = box
    label(draw, (x1 + 16, y1 + 12), title, 13, TEXT, True)
    ring_cx, ring_cy, ring_r = x2 - 28, y1 + 22, 11
    ring_color = SUCCESS if score >= 50 else ACCENT
    draw.ellipse(
        (ring_cx - ring_r, ring_cy - ring_r, ring_cx + ring_r, ring_cy + ring_r),
        outline=BORDER,
        width=2,
    )
    if score:
        draw.arc(
            (ring_cx - ring_r + 2, ring_cy - ring_r + 2, ring_cx + ring_r - 2, ring_cy + ring_r - 2),
            start=-90,
            end=-90 + int(360 * score / 100),
            fill=ring_color,
            width=3,
        )
    label(draw, (ring_cx, ring_cy), str(score), 8, TEXT, True, "mm")
    draw.line((x1 + 16, y1 + 38, x2 - 16, y1 + 38), fill=BORDER)
    cy = y1 + 78
    draw.line((x1 + 42, y1 + 52, x1 + 42, y2 - 22), fill=BORDER)
    for name, pct, color, unlocked, meta in nodes:
        node(draw, x1 + 42, cy, pct, color, unlocked)
        label(draw, (x1 + 78, cy - 20), name, 12, TEXT, True)
        label(draw, (x1 + 78, cy + 2), meta, 10, MUTED)
        cy += 68


def draw_careers() -> Path:
    width, height = 1400, 1660
    image = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(image)
    sidebar(draw, height, "Profile")
    page_title(draw, "Profile", "Cyber DNA, Momentum, and Career Atlas")

    x = 270
    y = 120
    label(draw, (x, y), "CAREER ATLAS", 11, MUTED, True)
    label(draw, (x, y + 22), "Practice evidence, mapped to real work", 24, TEXT, True)
    label(
        draw,
        (x, y + 58),
        "Six practice branches, eleven career families, and the roles inside them. Nodes unlock from the work you have already completed.",
        12,
        SECONDARY,
    )
    pill(draw, (960, y + 12), "Canada  CAD", fill=ACCENT_BG, color=ACCENT_TEXT, size=11)
    pill(draw, (1080, y + 12), "United States  USD", fill=PANEL, color=SECONDARY, size=11)
    pill(draw, (1245, y + 12), "v2026.1", fill=PANEL, color=MUTED, size=11)

    # Legend
    rounded(draw, (x, y + 90, x + 1100, y + 126), fill=PANEL_ALT)
    label(draw, (x + 16, y + 100), "Unlocked", 11, SUCCESS, True)
    label(draw, (x + 120, y + 100), "One step away", 11, WARNING, True)
    label(draw, (x + 250, y + 100), "Locked", 11, MUTED, True)
    label(draw, (x + 860, y + 100), "4 of 11 families unlocked", 11, MUTED)

    # Tree
    rounded(draw, (x, y + 145, x + 1100, y + 760), fill=PANEL_ALT)
    draw.rounded_rectangle((x + 420, y + 165, x + 680, y + 225), radius=999, fill=PANEL, outline=ACCENT)
    draw.ellipse((x + 436, y + 176, x + 470, y + 210), fill=ACCENT_BG, outline=ACCENT)
    label(draw, (x + 456, y + 193), "A", 14, ACCENT_TEXT, True, "mm")
    label(draw, (x + 484, y + 178), "Artificer", 13, TEXT, True)
    label(draw, (x + 484, y + 200), "62/100 · Practitioner", 10, MUTED)

    lanes = [
        ("Explorer", 48, [("Threat Intelligence / OSINT", 64, SUCCESS, True, "64% · 3 roles")]),
        ("Builder", 62, [("AppSec / Product Security", 72, SUCCESS, True, "72% · 3 roles"), ("Cloud Security", 38, WARNING, False, "38% · 3 roles")]),
        ("Tester", 55, [("Offensive Security", 81, SUCCESS, True, "81% · 4 roles")]),
        ("Defender", 44, [("Defensive Security / SOC", 58, SUCCESS, True, "58% · 4 roles"), ("OT / ICS Security", 26, WARNING, False, "26% · 3 roles")]),
        ("Investigator", 51, [("DFIR / Investigation", 67, SUCCESS, True, "67% · 4 roles"), ("AI Security", 22, MUTED, False, "22% · 3 roles")]),
        ("Leader", 30, [("Leadership / Education", 41, WARNING, False, "41% · 4 roles"), ("Governance, Risk & Compliance", 18, MUTED, False, "18% · 3 roles")]),
    ]
    lane_w = 350
    for index, (title, score, nodes) in enumerate(lanes):
        col = index % 3
        row = index // 3
        box = (x + 16 + col * 365, y + 250 + row * 250, x + 16 + col * 365 + lane_w, y + 250 + row * 250 + 230)
        lane(draw, box, title, score, nodes)

    # Detail panel
    dy = y + 790
    rounded(draw, (x, dy, x + 1100, dy + 470), fill=PANEL)
    label(draw, (x + 22, dy + 20), "TESTER BRANCH · UNLOCKED", 10, MUTED, True)
    label(draw, (x + 22, dy + 42), "Offensive Security / Penetration Testing", 20, TEXT, True)
    label(
        draw,
        (x + 22, dy + 74),
        "Authorised testing inside isolated labs: reconnaissance, exploitation, privilege escalation, post-exploitation, and clear reporting.",
        11,
        SECONDARY,
    )
    label(draw, (x + 940, dy + 22), "PRACTICE MATCH", 10, MUTED, True)
    label(draw, (x + 940, dy + 40), "81/100", 24, TEXT, True)
    match_cx, match_cy, match_r = x + 906, dy + 52, 16
    draw.ellipse(
        (match_cx - match_r, match_cy - match_r, match_cx + match_r, match_cy + match_r),
        outline=BORDER,
        width=2,
    )
    draw.arc(
        (match_cx - match_r + 3, match_cy - match_r + 3, match_cx + match_r - 3, match_cy + match_r - 3),
        start=-90,
        end=-90 + int(360 * 0.81),
        fill=SUCCESS,
        width=3,
    )
    progress(draw, (x + 22, dy + 110, x + 1078, dy + 118), 81, SUCCESS)
    label(draw, (x + 22, dy + 128), "Unlocked by your practice evidence", 10, MUTED)

    roles = [
        ("ENTRY", "Junior Penetration Tester", "CA$103,000 median", "CA$62,400 – CA$150,000"),
        ("CORE", "Penetration Tester", "CA$103,000 median", "CA$62,400 – CA$150,000"),
        ("ADVANCED", "Red Team Operator", "CA$103,000 median", "CA$62,400 – CA$150,000"),
        ("ADVANCED", "Offensive Security Consultant", "CA$138,700 median", "CA$91,000 – CA$215,000"),
    ]
    rx = x + 22
    for level, title, median, salary_range in roles:
        box = (rx, dy + 155, rx + 255, dy + 275)
        rounded(draw, box, fill=PANEL_ALT)
        pill(draw, (box[0] + 14, box[1] + 12), level, fill=BG, color=SECONDARY, size=9, pad=6)
        label(draw, (box[0] + 14, box[1] + 38), title, 11, TEXT, True)
        label(draw, (box[0] + 14, box[1] + 62), median, 13, TEXT, True)
        label(draw, (box[0] + 14, box[1] + 84), salary_range, 9, MUTED)
        rx += 268

    # Salary lens
    sy = dy + 300
    rounded(draw, (x + 22, sy, x + 1078, sy + 145), fill=PANEL_ALT)
    label(draw, (x + 40, sy + 16), "SALARY LENS · CANADA (CAD)", 9, MUTED, True)
    label(draw, (x + 40, sy + 34), "Penetration Tester", 14, TEXT, True)
    label(draw, (x + 800, sy + 18), "Cybersecurity specialists (NOC 21220)", 9, MUTED)
    draw.rounded_rectangle((x + 40, sy + 72, x + 1040, sy + 84), radius=999, fill=BG)
    draw.rounded_rectangle((x + 40, sy + 72, x + 1040, sy + 84), radius=999, fill=ACCENT_BG)
    draw.rectangle((x + 40, sy + 66, x + 43, sy + 90), fill=MUTED)
    draw.rectangle((x + 620, sy + 62, x + 624, sy + 94), fill=ACCENT)
    draw.rectangle((x + 1037, sy + 66, x + 1040, sy + 90), fill=MUTED)
    label(draw, (x + 40, sy + 100), "Low 10th  CA$62,400", 9, MUTED)
    label(draw, (x + 540, sy + 100), "Median  CA$103,000", 9, TEXT, True)
    label(draw, (x + 900, sy + 100), "High 90th  CA$150,000", 9, MUTED)
    label(draw, (x + 40, sy + 122), "Canada Job Bank · as of 2025-11-19 · annualised from the national median hourly wage at 2,080 hours", 8, MUTED)

    label(
        draw,
        (x, dy + 500),
        "Career families unlock from practice evidence. They are not a job prediction, a certification, or a ranking. Salary bands are national planning ranges from public labour-market data.",
        10,
        MUTED,
    )

    STUDENT_IMG.mkdir(parents=True, exist_ok=True)
    target = STUDENT_IMG / "profile-careers.png"
    image.save(target, format="PNG", optimize=True)
    return target


def draw_admin_features() -> Path:
    width, height = 1400, 900
    image = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(image)
    sidebar(draw, height, "Admin")
    page_title(draw, "Platform Settings", "Settings apply to this entire deployment")

    tabs = ["General", "Security", "Exercises", "VPN", "Email", "Features"]
    tx = 270
    for tab in tabs:
        f = font(12, True)
        w = int(draw.textlength(tab, font=f)) + 28
        if tab == "Features":
            draw.rounded_rectangle((tx, 140, tx + w, 172), radius=8, fill=ACCENT_BG, outline=ACCENT)
            label(draw, (tx + 14, 149), tab, 12, ACCENT_TEXT, True)
        else:
            label(draw, (tx + 14, 149), tab, 12, SECONDARY, True)
        tx += w + 8

    rounded(draw, (270, 200, 1360, 430), fill=PANEL)
    label(draw, (294, 222), "Advanced DNA Insights", 16, TEXT, True)
    label(
        draw,
        (294, 252),
        "Show the development-only Momentum and Career Atlas surfaces on learner profiles and career dossiers.",
        12,
        SECONDARY,
    )
    label(
        draw,
        (294, 276),
        "Keep this off in production until the review in docs/CAREER-ATLAS-AND-MOMENTUM.md is signed off.",
        11,
        MUTED,
    )
    draw.rounded_rectangle((1160, 230, 1330, 272), radius=999, fill=SUCCESS)
    label(draw, (1245, 251), "Enabled", 12, "#052e16", True, "mm")
    label(draw, (294, 310), "advanced_dna_insights_enabled", 10, MUTED)

    rounded(draw, (270, 450, 1360, 560), fill=PANEL_ALT)
    label(draw, (294, 472), "Development preview", 13, WARNING, True)
    label(
        draw,
        (294, 496),
        "The Career Atlas, Momentum panel, and the extended career dossier are gated by this setting. Production keeps the default Off.",
        11,
        SECONDARY,
    )

    rounded(draw, (270, 580, 1360, 680), fill=PANEL_ALT)
    label(draw, (294, 602), "Where the learner sees it", 13, TEXT, True)
    label(
        draw,
        (294, 626),
        "Profile -> Skill tree -> Momentum and friction. Profile -> Careers -> Career Atlas. Career dossier Markdown and printable HTML include both sections when the setting is On.",
        11,
        SECONDARY,
    )

    label(
        draw,
        (270, 720),
        "The toggle is audited like any other platform setting. Turning it off hides the surfaces but does not delete learner records.",
        10,
        MUTED,
    )

    ADMIN_IMG.mkdir(parents=True, exist_ok=True)
    target = ADMIN_IMG / "admin-settings-features.png"
    image.save(target, format="PNG", optimize=True)
    return target


def main() -> None:
    written = [draw_momentum(), draw_careers(), draw_admin_features()]
    for path in written:
        print(path.relative_to(ROOT))


if __name__ == "__main__":
    main()

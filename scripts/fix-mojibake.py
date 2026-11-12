from pathlib import Path

import ftfy

ROOT = Path(__file__).resolve().parents[1]

FILES = [
    "README.md",
    "docs/EDITIONS.md",
    "docs/SUPPORTED-VERSIONS.md",
    "docs/status-dashboard.html",
    "docs/reviews/V2.5.3-RELEASE-EVIDENCE.md",
    "platform/labs/OSINT/osint-1-3-exif-metadata/README.md",
    "platform/labs/Windows/windows-6-2-mssql-version-and-instance-enumeration/README.md",
    "scripts/status-dashboard.py",
    "platform/backend/app/routers/rangebox.py",
]

for relative in FILES:
    path = ROOT / relative
    original = path.read_text(encoding="utf-8")
    fixed = ftfy.fix_text(original, uncurl_quotes=False)
    # A few files had a literal replacement character where an em dash was
    # lost before this cleanup. The surrounding spaces make the intent clear.
    fixed = fixed.replace(" \ufffd ", " \u2014 ")
    fixed = fixed.replace("\ufffd", "\u2014")
    if fixed != original:
        path.write_text(fixed, encoding="utf-8")
        print(f"fixed {relative}")
    else:
        print(f"unchanged {relative}")

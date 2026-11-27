"""Create the small upload fixtures used by the Karate security suite."""
from __future__ import annotations

import io
import zipfile
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "fixtures"
OUT.mkdir(parents=True, exist_ok=True)


def make_zip(name: str, entries: dict[str, bytes]) -> None:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        for path, data in entries.items():
            archive.writestr(path, data)
    (OUT / name).write_bytes(buffer.getvalue())


(OUT / "not-a-zip.zip").write_text("this is not a zip archive\n", encoding="utf-8")

make_zip(
    "non-md.zip",
    {
        "payload.exe": b"MZ\x90\x00not-a-real-executable",
        "readme.txt": b"no markdown here\n",
    },
)

make_zip(
    "valid.zip",
    {
        "00_Introduction.md": b"# Karate upload fixture\n",
        "01_Test.md": b"# Test page\n",
    },
)

make_zip(
    "traversal.zip",
    {
        "../../evil.md": b"# should be sanitized\n",
        "01_Safe.md": b"# safe\n",
    },
)

print(f"wrote fixtures to {OUT}")

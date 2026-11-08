"""Unicode-aware input normalisation for user-supplied text.

The goal is not to strip international text.  Kanji, Arabic, Devanagari,
accented Latin, emoji, and other scripts are valid in names, descriptions, and
comments.  The dangerous cases are the characters that change how text is
interpreted without being visible:

* NUL bytes and C0/C1 control characters (log injection, truncation);
* CR/LF in single-line fields (header and log injection);
* bidirectional overrides and isolates (Trojan Source / display spoofing);
* zero-width spaces, BOMs, and word joiners (identifier spoofing);
* unpaired surrogates and Unicode noncharacters (invalid UTF-8, parser bugs);
* overlong input by code points or UTF-8 bytes.

``normalize_text`` applies NFKC so full-width and compatibility forms compare
predictably, then rejects the dangerous categories.  It deliberately does not
escape SQL, HTML, or shell metacharacters: those are handled at the sink with
parameterised queries and output encoding.  Rejecting ``'`` or ``<`` here would
break ordinary names such as O'Brien and descriptions that contain code.
"""

from __future__ import annotations

import re
import unicodedata

# C0/C1 controls except tab and newline. Newline is allowed only in multiline
# fields; single-line fields reject it rather than silently folding it.
_ALLOWED_CONTROLS = {"\t", "\n"}

# Bidirectional formatting characters and marks. These can reorder the visual
# rendering of an identifier without changing its code points.
_BIDI_CONTROLS = {
    0x061C,  # Arabic letter mark
    0x200E,  # left-to-right mark
    0x200F,  # right-to-left mark
    *range(0x202A, 0x202F),  # LRE, RLE, PDF, LRO, RLO
    *range(0x2066, 0x206A),  # LRI, RLI, FSI, PDI
}

# Invisible characters that are commonly used to spoof identifiers. ZWNJ and
# ZWJ (U+200C/U+200D) are allowed because they are legitimate in several
# scripts and in emoji sequences.
_INVISIBLE_SPOOFING = {
    0x200B,  # zero-width space
    0x2060,  # word joiner
    0xFEFF,  # zero-width no-break space / BOM
    0x180E,  # Mongolian vowel separator
}

_NONCHARACTER_RANGES = (
    (0xFDD0, 0xFDEF),
    (0xFFFE, 0xFFFF),
    (0x1FFFE, 0x1FFFF),
    (0x2FFFE, 0x2FFFF),
    (0x3FFFE, 0x3FFFF),
    (0x4FFFE, 0x4FFFF),
    (0x5FFFE, 0x5FFFF),
    (0x6FFFE, 0x6FFFF),
    (0x7FFFE, 0x7FFFF),
    (0x8FFFE, 0x8FFFF),
    (0x9FFFE, 0x9FFFF),
    (0xAFFFE, 0xAFFFF),
    (0xBFFFE, 0xBFFFF),
    (0xCFFFE, 0xCFFFF),
    (0xDFFFE, 0xDFFFF),
    (0xEFFFE, 0xEFFFF),
    (0xFFFFE, 0xFFFFF),
    (0x10FFFE, 0x10FFFF),
)


def _is_noncharacter(codepoint: int) -> bool:
    return any(start <= codepoint <= end for start, end in _NONCHARACTER_RANGES)


def _reject(field: str, reason: str) -> None:
    raise ValueError(f"{field} contains {reason}")


def normalize_text(
    value: str,
    *,
    field: str = "value",
    allow_newlines: bool = False,
    collapse_whitespace: bool = True,
    strip: bool = True,
    max_length: int | None = None,
    max_bytes: int | None = None,
) -> str:
    """Normalise and validate one user-supplied string.

    Raises ``ValueError`` with a field-specific message when the value contains
    a dangerous character or exceeds a limit.  The caller (usually a Pydantic
    validator) turns that into a 422 response.
    """
    if not isinstance(value, str):
        raise ValueError(f"{field} must be text")
    if "\x00" in value:
        _reject(field, "a null byte")

    # Normalise line endings before checking, so CRLF is handled consistently.
    value = value.replace("\r\n", "\n").replace("\r", "\n")

    for char in value:
        codepoint = ord(char)
        if char == "\n":
            if not allow_newlines:
                _reject(field, "a line break")
            continue
        if char == "\t":
            continue
        if codepoint in _BIDI_CONTROLS:
            _reject(field, "a bidirectional control character")
        if codepoint in _INVISIBLE_SPOOFING:
            _reject(field, "an invisible formatting character")
        if _is_noncharacter(codepoint):
            _reject(field, "a Unicode noncharacter")
        category = unicodedata.category(char)
        if category in {"Cc", "Cs"}:
            _reject(field, "a control character or unpaired surrogate")

    # NFKC folds full-width Latin, compatibility ideographs, and similar forms
    # to a predictable representation. It does not remove kanji or emoji.
    value = unicodedata.normalize("NFKC", value)

    if collapse_whitespace:
        value = re.sub(r"[ \t]+", " ", value)
        if allow_newlines:
            value = re.sub(r"\n{3,}", "\n\n", value)
    if strip:
        value = value.strip()

    if max_length is not None and len(value) > max_length:
        raise ValueError(f"{field} must be at most {max_length} characters")
    if max_bytes is not None and len(value.encode("utf-8")) > max_bytes:
        raise ValueError(f"{field} is too large")
    return value


def normalize_identifier(
    value: str,
    *,
    field: str = "value",
    pattern: str | None = None,
    max_length: int = 100,
) -> str:
    """Normalise a machine identifier and require an ASCII-only shape.

    Identifiers (slugs, invite codes, certificate IDs, usernames) must not use
    homoglyphs, full-width forms, or Unicode digits. NFKC runs first so a
    canonical ASCII value still passes, then the ASCII allowlist rejects
    everything else.
    """
    cleaned = normalize_text(
        value,
        field=field,
        allow_newlines=False,
        max_length=max_length,
    )
    if not cleaned.isascii():
        _reject(field, "non-ASCII characters")
    if pattern and not re.fullmatch(pattern, cleaned):
        raise ValueError(f"{field} has an invalid format")
    return cleaned


def is_safe_text(value: str, *, allow_newlines: bool = True) -> bool:
    """Return True when ``normalize_text`` would accept ``value``."""
    try:
        normalize_text(value, allow_newlines=allow_newlines)
    except ValueError:
        return False
    return True

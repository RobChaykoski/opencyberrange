"""Spreadsheet export safety.

CSV cells are data, but spreadsheet applications interpret a leading ``=``,
``+``, ``-``, or ``@`` as a formula. A learner-controlled name, course title,
comment, or activity label could therefore become an executable formula when
an instructor opens an export.

``neutralize_cell`` prefixes only values that look like formulas with an
apostrophe, the standard spreadsheet text marker. Numeric values (including
negative numbers) and plain numeric strings are left alone so legitimate
academic data is not silently changed. The original text follows the marker.
"""

from __future__ import annotations

import re
from decimal import Decimal
from typing import Any

# Leading ASCII formula characters plus their full-width compatibility forms.
_DANGEROUS_PREFIXES = ("=", "+", "-", "@", "\t", "\r", "\n", "\uff1d", "\uff0b", "\uff0d", "\uff20")
# A plain number is data, not a formula, even when it starts with + or -.
_NUMERIC = re.compile(r"^[+-]?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?$")
# A lone marker is a placeholder, not an executable expression.
_LONE_MARKERS = {"-", "+", "@"}


def neutralize_cell(value: Any) -> Any:
    """Return a CSV-safe cell value without changing ordinary text.

    Numbers and booleans are returned unchanged. Strings that begin with a
    formula marker are prefixed with an apostrophe; plain numbers and lone
    punctuation markers are left alone.
    """
    if value is None:
        return ""
    if isinstance(value, (bool, int, float, Decimal)):
        return value
    text = str(value)
    if not text:
        return text

    stripped = text.lstrip(" \t\r\n")
    if not stripped:
        return text
    if stripped in _LONE_MARKERS:
        return text
    if stripped[0] in _DANGEROUS_PREFIXES and not _NUMERIC.fullmatch(stripped):
        return "'" + text
    return text


def neutralize_row(values) -> list:
    """Apply :func:`neutralize_cell` to every cell in a row."""
    return [neutralize_cell(value) for value in values]

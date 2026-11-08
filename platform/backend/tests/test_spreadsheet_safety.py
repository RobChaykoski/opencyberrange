"""CSV/Excel exports must neutralise spreadsheet formulas without altering data."""

import pytest

from app.services.spreadsheet_safety import neutralize_cell, neutralize_row

MALICIOUS = [
    '=HYPERLINK("https://example.invalid","Open")',
    "@SUM(1+1)",
    "+cmd|' /C calc'!A0",
    "-2+3",
    "=1+1",
    "\t=SUM(A1:A2)",
    "\r\n=SUM(A1:A2)",
    "\uff1dSUM(1,1)",
]

SAFE = [
    "O'Brien",
    "Negative five: -5",
    "-5",
    "+1.5",
    "1e-3",
    "A normal title",
    "漢字のコース",
    "Emoji 🙂",
    "-",
    "+",
    "@",
]


@pytest.mark.parametrize("value", MALICIOUS)
def test_formula_like_values_are_prefixed(value):
    result = neutralize_cell(value)
    assert isinstance(result, str)
    assert result.startswith("'")
    assert result[1:] == value


@pytest.mark.parametrize("value", SAFE)
def test_ordinary_values_are_unchanged(value):
    assert neutralize_cell(value) == value


def test_numbers_are_never_changed():
    assert neutralize_cell(-5) == -5
    assert neutralize_cell(1.5) == 1.5
    assert neutralize_cell(True) is True


def test_none_becomes_empty_cell():
    assert neutralize_cell(None) == ""


def test_row_neutralises_each_cell():
    row = neutralize_row(["=SUM(1+1)", "safe", -3])
    assert row == ["'=SUM(1+1)", "safe", -3]

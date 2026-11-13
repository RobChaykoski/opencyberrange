"""Shared learning-metadata helpers for catalogue cards.

Track and course cards are built from different tables, but both need a
consistent, honest difficulty label and a short level summary. Keeping the
rules here means the Exercises hub and the Courses workspace cannot drift.
"""
from __future__ import annotations

from typing import Iterable, Sequence

DIFFICULTY_RANK = {"beginner": 1, "intermediate": 2, "advanced": 3}


def aggregate_difficulty(values: Iterable[str | None]) -> tuple[str, int]:
    """Return the typical difficulty for a set of labs.

    The mode is used rather than the maximum: one advanced capstone should not
    label an otherwise beginner course as advanced. Ties break toward the
    easier level so the catalogue stays approachable.
    """
    counts = {"beginner": 0, "intermediate": 0, "advanced": 0}
    for value in values:
        key = (value or "beginner").strip().lower()
        if key in counts:
            counts[key] += 1
    if not any(counts.values()):
        return "beginner", DIFFICULTY_RANK["beginner"]
    difficulty, _ = max(
        counts.items(),
        key=lambda item: (item[1], -DIFFICULTY_RANK[item[0]]),
    )
    return difficulty, DIFFICULTY_RANK[difficulty]


def level_label_for_numbers(level_numbers: Sequence[int | None]) -> str:
    """Short label for the levels represented by a set of labs."""
    numbers = sorted({n for n in level_numbers if n is not None})
    if not numbers:
        return ""
    if len(numbers) == 1:
        number = numbers[0]
        return "Foundations" if number == 0 else f"Level {number}"
    if numbers == list(range(numbers[0], numbers[-1] + 1)):
        if numbers[0] == 0:
            return f"Foundations–Level {numbers[-1]}"
        return f"Levels {numbers[0]}–{numbers[-1]}"
    return f"{len(numbers)} levels"

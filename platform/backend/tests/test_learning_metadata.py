"""Difficulty and level summaries shared by course and exercise cards."""

from app.services.learning_metadata import (
    aggregate_difficulty,
    level_label_for_numbers,
    percent_complete,
)


def test_mode_wins_over_a_single_advanced_capstone():
    assert aggregate_difficulty(["beginner", "beginner", "advanced"]) == ("beginner", 1)
    assert aggregate_difficulty(["beginner", "advanced", "advanced"]) == ("advanced", 3)


def test_ties_break_toward_the_easier_level():
    assert aggregate_difficulty(["beginner", "advanced"]) == ("beginner", 1)
    assert aggregate_difficulty([]) == ("beginner", 1)


def test_level_labels_cover_foundations_contiguous_and_mixed_sets():
    assert level_label_for_numbers([0]) == "Foundations"
    assert level_label_for_numbers([2]) == "Level 2"
    assert level_label_for_numbers([0, 1, 2]) == "Foundations–Level 2"
    assert level_label_for_numbers([1, 2, 3]) == "Levels 1–3"
    assert level_label_for_numbers([1, 3, 9]) == "3 levels"
    assert level_label_for_numbers([]) == ""


def test_percent_is_half_up_to_match_the_frontend():
    assert percent_complete(1, 8) == 13
    assert percent_complete(17, 139) == 12
    assert percent_complete(0, 8) == 0
    assert percent_complete(8, 8) == 100
    assert percent_complete(0, 0) == 0

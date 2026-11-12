"""Achievement catalogue: tiers, difficulty values, and grouping."""

from __future__ import annotations

from types import SimpleNamespace

from app.services.achievement_catalogue import (
    BUILTIN_METADATA,
    DIFFICULTIES,
    GROUPS,
    TIERS,
    build_catalogue,
    points_for,
    serialize_custom_achievement,
)
from app.services.achievements import ACHIEVEMENT_LABELS, HIDDEN_ACHIEVEMENT_TYPES


def test_points_increase_with_tier_and_difficulty():
    assert points_for("bronze", "starter") < points_for("bronze", "standard")
    assert points_for("bronze", "standard") < points_for("silver", "standard")
    assert points_for("silver", "standard") < points_for("gold", "advanced")
    assert points_for("gold", "advanced") < points_for("platinum", "expert")
    assert points_for("platinum", "expert") == 200


def test_points_round_to_whole_values_and_never_zero():
    for tier in TIERS:
        for difficulty in DIFFICULTIES:
            value = points_for(tier["key"], difficulty["key"])
            assert value >= 5
            assert isinstance(value, int)


def test_every_builtin_label_has_metadata():
    missing = [key for key in ACHIEVEMENT_LABELS if key not in BUILTIN_METADATA]
    assert missing == []


def test_hidden_achievements_are_flagged_hidden():
    for achievement_type in HIDDEN_ACHIEVEMENT_TYPES:
        assert achievement_type in BUILTIN_METADATA


def test_quiz_platinum_exists_and_is_platinum():
    group, tier, difficulty = BUILTIN_METADATA["quiz_platinum"]
    assert group == "quiz"
    assert tier == "platinum"
    assert points_for(tier, difficulty) >= 100


def test_custom_achievement_serialization_includes_value_metadata():
    row = SimpleNamespace(
        id=7,
        name="Night Owl",
        description="Finish three exercises after midnight",
        icon="\U0001F319",
        trigger="night_labs",
        threshold=3,
        group_key="custom",
        tier="gold",
        difficulty="advanced",
        points=points_for("gold", "advanced"),
        is_active=True,
        created_at=None,
    )
    payload = serialize_custom_achievement(row)
    assert payload["id"] == "custom:7"
    assert payload["source"] == "custom"
    assert payload["editable"] is True
    assert payload["points"] == 75
    assert payload["group_label"] == "Custom"


def test_catalogue_groups_are_declared():
    keys = {group["key"] for group in GROUPS}
    assert keys == {
        "foundations",
        "consistency",
        "quiz",
        "tracks",
        "hidden",
        "custom",
    }


class _FakeQuery:
    def order_by(self, *args, **kwargs):
        return self

    def all(self):
        return []


class _FakeSession:
    def query(self, *args, **kwargs):
        return _FakeQuery()


def test_catalogue_summary_counts_builtins():
    catalogue = build_catalogue(_FakeSession())
    assert catalogue["summary"]["builtin"] == len(ACHIEVEMENT_LABELS)
    assert catalogue["summary"]["custom"] == 0
    assert catalogue["summary"]["total"] == len(ACHIEVEMENT_LABELS)
    assert catalogue["summary"]["total_points"] > 0
    assert all(row["points"] > 0 for row in catalogue["achievements"])

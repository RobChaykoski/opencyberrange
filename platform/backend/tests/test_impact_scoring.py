"""Pure impact scoring checks. No database required."""

from __future__ import annotations

from datetime import datetime, timedelta

from app.models.impact import ImpactContribution
from app.services import impact


def _contrib(**overrides) -> ImpactContribution:
    values = dict(
        user_id=1,
        dimension="build",
        kind="lab",
        title="A reviewed lab",
        status="verified",
        base_points=50,
        reach_count=1000,
        quality_rating=5.0,
        validation_level="instructor",
        originality="original",
        occurred_at=datetime(2026, 1, 1),
        last_used_at=datetime(2026, 1, 1),
    )
    values.update(overrides)
    return ImpactContribution(**values)


def test_reach_is_sublinear_and_capped():
    assert impact.reach_multiplier(0) == 1.0
    assert impact.reach_multiplier(1) == 1.0
    assert impact.reach_multiplier(10) == 2.0
    assert impact.reach_multiplier(1000) == 4.0
    assert impact.reach_multiplier(10000) == 5.0
    assert impact.reach_multiplier(10_000_000) == 5.0


def test_quality_floor_excludes_low_ratings():
    assert impact.quality_multiplier(None) is None
    assert impact.quality_multiplier(2.9) is None
    assert impact.quality_multiplier(3.0) == 0.75
    assert impact.quality_multiplier(4.0) == 1.0
    assert impact.quality_multiplier(4.6) == 1.15
    assert impact.quality_multiplier(5.0) == 1.25


def test_repeat_weight_diminishes_and_floors():
    assert impact.repeat_weight(1) == 1.0
    assert impact.repeat_weight(2) == 0.6667
    assert impact.repeat_weight(3) == 0.5
    assert impact.repeat_weight(5) == 0.3333
    assert impact.repeat_weight(50) == 0.1


def test_longevity_only_applies_to_long_running_work():
    now = datetime(2026, 6, 1)
    assert (
        impact.longevity_multiplier(
            "build", now - timedelta(days=10), now=now
        )
        == 0.5
    )
    assert (
        impact.longevity_multiplier(
            "build", now - timedelta(days=60), now=now
        )
        == 1.0
    )
    assert (
        impact.longevity_multiplier(
            "build", now - timedelta(days=200), now=now
        )
        == 1.5
    )
    assert (
        impact.longevity_multiplier(
            "build", now - timedelta(days=900), now=now
        )
        == 2.0
    )
    assert (
        impact.longevity_multiplier(
            "teach", now - timedelta(days=900), now=now
        )
        == 1.0
    )


def test_decay_only_after_two_unused_years():
    now = datetime(2026, 6, 1)
    assert (
        impact.decay_multiplier("build", now - timedelta(days=700), now=now)
        == 1.0
    )
    assert (
        impact.decay_multiplier("build", now - timedelta(days=365 * 3 + 1), now=now)
        == 0.8
    )
    assert (
        impact.decay_multiplier("build", now - timedelta(days=365 * 20), now=now)
        == impact.DECAY_FLOOR
    )
    assert impact.decay_multiplier("teach", now - timedelta(days=365 * 20)) == 1.0


def test_score_is_bounded_by_the_coefficients():
    now = datetime(2026, 1, 1)
    row = _contrib(
        base_points=50,
        reach_count=1000,
        quality_rating=4.6,
        validation_level="instructor",
        last_used_at=datetime(2025, 1, 2),
    )
    score = impact.score_contribution(row, ordinal=1, now=now)
    # 50 * 4 * 1.15 * 1.5 * 1.2 * 1.0 * 1.0 * 1.0
    assert score["points"] == 414
    assert score["factors"]["reach"] == 4.0
    assert score["factors"]["quality"] == 1.15
    assert score["factors"]["longevity"] == 1.5
    assert score["factors"]["validation"] == 1.2


def test_unverified_work_is_preview_only():
    row = _contrib(status="submitted", validation_level="self")
    score = impact.score_contribution(row)
    assert score["points"] == 0
    assert score["counted"] is False
    assert score["preview_points"] > 0
    assert score["excluded"] == "not_verified"


def test_low_rating_scores_zero():
    row = _contrib(quality_rating=2.0)
    score = impact.score_contribution(row)
    assert score["points"] == 0
    assert score["excluded"] == "quality_threshold"


def test_ordinals_are_per_learner_and_per_kind():
    base = datetime(2026, 1, 1)
    rows = [
        _contrib(id=1, user_id=1, occurred_at=base),
        _contrib(id=2, user_id=1, occurred_at=base + timedelta(days=10)),
        _contrib(id=3, user_id=2, occurred_at=base + timedelta(days=20)),
        _contrib(
            id=4,
            user_id=1,
            kind="tool",
            occurred_at=base + timedelta(days=30),
        ),
        _contrib(
            id=5,
            user_id=1,
            occurred_at=base + timedelta(days=400),
        ),
    ]
    ordinals = impact._verify_ordinals(rows)
    assert ordinals == {1: 1, 2: 2, 3: 1, 4: 1, 5: 1}


def test_stewardship_starts_at_one_hundred_and_is_capped():
    class Event:
        def __init__(self, delta):
            self.points_delta = delta

    assert impact.stewardship_points([]) == 100
    assert impact.stewardship_points([Event(-30)]) == 70
    assert impact.stewardship_points([Event(-500)]) == 0
    assert impact.stewardship_points([Event(200)]) == impact.STEWARDSHIP_MAX
    assert impact.stewardship_band(92) == "Trusted"
    assert impact.stewardship_band(75) == "Established"
    assert impact.stewardship_band(55) == "Watch"
    assert impact.stewardship_band(10) == "Restricted"


def test_meaning_index_uses_verified_work_only():
    now = datetime(2026, 11, 24)
    rows = [
        _contrib(dimension="protect", kind="assessment", reach_count=1),
        _contrib(dimension="protect", kind="policy", reach_count=1),
        _contrib(dimension="teach", kind="mentoring", reach_count=10),
        _contrib(dimension="teach", kind="workshop", reach_count=100),
        _contrib(dimension="build", kind="tool", reach_count=2000),
        _contrib(dimension="serve", kind="community_event", reach_count=50),
        _contrib(
            dimension="build",
            kind="lab",
            reach_count=99999,
            status="submitted",
        ),
    ]
    index = impact.meaning_index(rows, now=now)
    assert index["organizations_protected"] == 2
    assert index["learners_mentored"] == 10
    assert index["people_taught"] == 100
    assert index["open_source_users"] == 2000
    assert index["communities_supported"] == 1
    # 2*5 + 10*2 + 100 + 2000*0.1 + 1*10 + years*25
    assert index["total"] == 340


def test_legacy_class_is_a_self_view():
    assert impact.legacy_class({}, "Trusted", False) == "Unclassified"
    assert (
        impact.legacy_class(
            {"build": 200, "protect": 10, "teach": 10, "serve": 10},
            "Trusted",
            True,
        )
        == "Builder"
    )
    assert (
        impact.legacy_class(
            {"build": 50, "protect": 50, "teach": 50, "serve": 50},
            "Trusted",
            True,
        )
        == "Steward"
    )
    assert (
        impact.legacy_class(
            {"build": 0, "protect": 0, "teach": 0, "serve": 100},
            "Established",
            True,
        )
        == "Community Champion"
    )
    assert (
        impact.legacy_class(
            {"build": 100, "protect": 20, "teach": 0, "serve": 0},
            "Trusted",
            True,
            innovative_build=80,
        )
        == "Pathfinder"
    )
    assert (
        impact.legacy_class(
            {"build": 40, "protect": 30, "teach": 20, "serve": 10},
            "Watch",
            True,
        )
        == "Contributor"
    )

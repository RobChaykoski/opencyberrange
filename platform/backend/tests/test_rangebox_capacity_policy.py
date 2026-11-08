"""The RangeBox live cap is a configurable percentage of the physical maximum."""

import pytest

from app.services import rangebox_capacity


@pytest.fixture(autouse=True)
def _clear_capacity_cache():
    rangebox_capacity.invalidate_cache()
    yield
    rangebox_capacity.invalidate_cache()


@pytest.mark.parametrize(
    "value,expected",
    [
        ("75", 75),
        (75, 75),
        ("100", 100),
        ("10", 10),
        ("0", rangebox_capacity.MIN_PERCENT),
        ("101", rangebox_capacity.MAX_PERCENT),
        ("not-a-number", rangebox_capacity.DEFAULT_PERCENT),
        (None, rangebox_capacity.DEFAULT_PERCENT),
    ],
)
def test_clamp_percent(value, expected):
    assert rangebox_capacity.clamp_percent(value) == expected


@pytest.mark.parametrize(
    "computed,percent,stress_max,expected",
    [
        (27, 75, 0, 20),
        (27, 75, 24, 18),
        (12, 75, 0, 9),
        (11, 75, 0, 8),
        (2, 75, 0, 1),
        (1, 75, 0, 1),
        (0, 75, 0, 0),
        (27, 100, 0, 27),
        (27, 50, 0, 13),
        (27, 75, 30, 20),  # a stale ceiling cannot exceed the computed maximum
    ],
)
def test_effective_max(computed, percent, stress_max, expected):
    assert rangebox_capacity.effective_max(computed, percent, stress_max) == expected


def test_get_capacity_percent_reads_the_setting(monkeypatch):
    monkeypatch.setattr(
        "app.services.settings_service.get_setting",
        lambda db, key, default=None: "60",
    )

    assert rangebox_capacity.get_capacity_percent(db=object()) == 60


def test_get_capacity_policy_reads_both_values(monkeypatch):
    def _setting(db, key, default=None):
        return {"rangebox_capacity_percent": "80", "rangebox_stress_max": "18"}.get(
            key, default
        )

    monkeypatch.setattr("app.services.settings_service.get_setting", _setting)

    assert rangebox_capacity.get_capacity_policy(db=object()) == (80, 18)


def test_get_capacity_percent_falls_back_on_error(monkeypatch):
    def _boom(db, key, default=None):
        raise RuntimeError("database unavailable")

    monkeypatch.setattr("app.services.settings_service.get_setting", _boom)

    assert rangebox_capacity.get_capacity_percent(db=object()) == 75


def test_record_stress_ceiling_is_clamped(monkeypatch):
    stored = {}

    def _set(db, key, value):
        stored[key] = value

    monkeypatch.setattr("app.services.settings_service.set_setting", _set)

    assert rangebox_capacity.record_stress_ceiling(30, 27, db=object()) == 27
    assert stored["rangebox_stress_max"] == "27"
    assert "rangebox_stress_tested_at" in stored


def test_record_stress_ceiling_ignores_zero(monkeypatch):
    stored = {}
    monkeypatch.setattr(
        "app.services.settings_service.set_setting",
        lambda db, key, value: stored.setdefault(key, value),
    )

    assert rangebox_capacity.record_stress_ceiling(0, 27, db=object()) == 0
    assert stored == {}

"""Accommodation bounds and serialization."""

from types import SimpleNamespace

import pytest

from app.services import accommodations


class _StubQuery:
    def __init__(self, record):
        self.record = record

    def filter(self, *args, **kwargs):
        return self

    def first(self):
        return self.record


class _StubDB:
    def __init__(self, record):
        self.record = record

    def query(self, *args, **kwargs):
        return _StubQuery(self.record)


def test_no_record_keeps_global_defaults():
    db = _StubDB(None)
    assert accommodations.effective_multiplier(db, 7) == 1.0
    assert accommodations.extension_days(db, 7) == 0
    assert accommodations.effective_multiplier(db, None) == 1.0


def test_record_multiplier_and_extension_apply():
    db = _StubDB(
        SimpleNamespace(time_multiplier=1.5, due_date_extension_days=3)
    )
    assert accommodations.effective_multiplier(db, 7) == 1.5
    assert accommodations.effective_percent(db, 7) == 150
    assert accommodations.extension_days(db, 7) == 3


def test_multiplier_is_clamped_to_supported_range():
    db = _StubDB(
        SimpleNamespace(time_multiplier=9.0, due_date_extension_days=900)
    )
    assert accommodations.effective_multiplier(db, 7) == 3.0
    assert accommodations.effective_percent(db, 7) == 300
    assert accommodations.extension_days(db, 7) == 365


def test_set_rejects_out_of_range_values():
    db = _StubDB(None)
    with pytest.raises(ValueError):
        accommodations.set_accommodation(
            db,
            user_id=1,
            actor_id=2,
            time_multiplier=0.5,
            due_date_extension_days=0,
        )
    with pytest.raises(ValueError):
        accommodations.set_accommodation(
            db,
            user_id=1,
            actor_id=2,
            time_multiplier=1.5,
            due_date_extension_days=400,
        )


def test_serialize_defaults():
    assert accommodations.serialize(None) == {
        "time_multiplier": 1.0,
        "due_date_extension_days": 0,
        "notes": None,
        "updated_at": None,
    }

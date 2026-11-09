"""Timed-exercise accommodation: session length and extension scaling."""

from datetime import timedelta

import pytest

from app.routers import labs


def _settings(monkeypatch, **values):
    monkeypatch.setattr(
        labs.settings_service,
        "get_setting",
        lambda db, key, default=None: values.get(key, default),
    )


def test_defaults_are_unscaled(monkeypatch):
    _settings(monkeypatch)
    assert labs._accommodation_percent(None) == 100
    assert labs._session_duration(None) == timedelta(hours=2)
    assert labs._session_extension(None) == timedelta(hours=1)


def test_one_hundred_and_fifty_percent_adds_half_the_time(monkeypatch):
    _settings(
        monkeypatch,
        session_accommodation_percent="150",
        default_session_hours="2",
    )
    assert labs._session_duration(None) == timedelta(minutes=180)
    assert labs._session_extension(None) == timedelta(minutes=90)


def test_accommodation_is_clamped_to_supported_range(monkeypatch):
    _settings(
        monkeypatch,
        session_accommodation_percent="999",
        default_session_hours="2",
    )
    assert labs._accommodation_percent(None) == 300
    assert labs._session_duration(None) == timedelta(hours=6)
    assert labs._session_extension(None) == timedelta(hours=3)


def test_invalid_setting_falls_back_to_no_change(monkeypatch):
    _settings(monkeypatch, session_accommodation_percent="not-a-number")
    assert labs._accommodation_percent(None) == 100
    assert labs._session_duration(None) == timedelta(hours=2)


def test_custom_session_length_is_scaled(monkeypatch):
    _settings(
        monkeypatch,
        session_accommodation_percent="125",
        default_session_hours="3",
    )
    assert labs._session_duration(None) == timedelta(minutes=225)
    assert labs._session_extension(None) == timedelta(minutes=75)

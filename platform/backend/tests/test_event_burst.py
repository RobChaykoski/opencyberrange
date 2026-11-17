from datetime import datetime, timedelta

from app.services import event_burst


def _window():
    start = datetime(2026, 11, 21, 14, 0, 0)
    end = datetime(2026, 11, 21, 22, 0, 0)
    return start, end


def test_window_includes_the_pre_and_post_buffer():
    start, end = _window()
    assert event_burst.within_event_window(
        start - timedelta(minutes=30), start, end, 30
    )
    assert not event_burst.within_event_window(
        start - timedelta(minutes=31), start, end, 30
    )
    assert event_burst.within_event_window(start, start, end, 30)
    assert event_burst.within_event_window(end, start, end, 30)
    assert event_burst.within_event_window(
        end + timedelta(minutes=30), start, end, 30
    )
    assert not event_burst.within_event_window(
        end + timedelta(minutes=31), start, end, 30
    )


def test_limits_switch_with_the_window(monkeypatch):
    monkeypatch.setattr(event_burst, "event_window_active", lambda now=None: True)
    assert event_burst.login_rate_limit() == event_burst.LOGIN_BURST
    assert event_burst.registration_rate_limit() == event_burst.REGISTRATION_BURST

    monkeypatch.setattr(event_burst, "event_window_active", lambda now=None: False)
    assert event_burst.login_rate_limit() == event_burst.LOGIN_STRICT
    assert event_burst.registration_rate_limit() == event_burst.REGISTRATION_STRICT


def test_database_failure_falls_back_to_strict(monkeypatch):
    def boom(_now):
        raise RuntimeError("database unavailable")

    monkeypatch.setattr(event_burst, "_competition_is_live", boom)
    assert event_burst.event_window_active(datetime(2026, 11, 21, 14, 0, 0)) is False

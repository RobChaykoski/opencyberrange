"""The stress-test run store must survive across workers and process restarts."""

from app.routers import admin


def test_stress_state_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setattr(admin, "_STRESS_DIR", str(tmp_path))
    monkeypatch.setattr(admin, "_stress_cancel_flags", {})

    admin._stress_write_state("run1", {"status": "running", "users": 10})
    assert admin._stress_read_state("run1") == {"status": "running", "users": 10}

    admin._stress_append_event("run1", {"type": "line", "message": "one"})
    admin._stress_append_event("run1", {"type": "line", "message": "two"})
    assert admin._stress_count_events("run1") == 2
    assert admin._stress_read_events("run1") == [
        {"type": "line", "message": "one"},
        {"type": "line", "message": "two"},
    ]
    assert admin._stress_read_events("run1", after=1) == [
        {"type": "line", "message": "two"},
    ]

    run_id, state = admin._stress_find_active()
    assert run_id == "run1"
    assert state["users"] == 10

    admin._stress_write_state("run1", {"status": "completed", "users": 10})
    assert admin._stress_find_active() == (None, {})

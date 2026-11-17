"""The stress-test run store must survive across workers and process restarts."""

import threading
import time

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


def test_last_completed_stress_state_returns_results(tmp_path, monkeypatch):
    monkeypatch.setattr(admin, "_STRESS_DIR", str(tmp_path))
    admin._stress_write_state("run2", {
        "status": "completed",
        "level": 4,
        "users": 20,
        "results": {"prespawn_succeeded": 20, "all_thresholds_passed": True},
    })

    state = admin._last_completed_stress_state()
    assert state["run_id"] == "run2"
    assert state["results"]["prespawn_succeeded"] == 20


def test_last_completed_stress_state_ignores_running_runs(tmp_path, monkeypatch):
    monkeypatch.setattr(admin, "_STRESS_DIR", str(tmp_path))
    admin._stress_write_state("run3", {
        "status": "running",
        "level": 4,
        "users": 20,
        "results": None,
    })

    assert admin._last_completed_stress_state() is None


def test_stress_cleanup_reports_its_messages(tmp_path, monkeypatch):
    monkeypatch.setattr(admin, "_STRESS_DIR", str(tmp_path))
    import stress_test

    def fake_cleanup(emit=None):
        if emit:
            emit("Cleanup complete: removed 5 test users")

    monkeypatch.setattr(stress_test, "cleanup_test_data", fake_cleanup)

    admin._stress_cleanup_users("cleanup-ok")

    messages = [event["message"] for event in admin._stress_read_events("cleanup-ok")]
    assert "Removing stress-test users..." in messages
    assert "Cleanup complete: removed 5 test users" in messages


def test_stress_cleanup_failure_is_reported(tmp_path, monkeypatch):
    monkeypatch.setattr(admin, "_STRESS_DIR", str(tmp_path))
    import stress_test

    def broken_cleanup(emit=None):
        raise RuntimeError("database unavailable")

    monkeypatch.setattr(stress_test, "cleanup_test_data", broken_cleanup)

    admin._stress_cleanup_users("cleanup-error")

    events = admin._stress_read_events("cleanup-error")
    assert any(
        event["level"] == "error" and "database unavailable" in event["message"]
        for event in events
    )


def test_app_stress_run_cleans_users_before_finishing(tmp_path, monkeypatch):
    monkeypatch.setattr(admin, "_STRESS_DIR", str(tmp_path))
    monkeypatch.setattr(admin, "_stress_cancel_flags", {})
    import stress_test

    cleaned = threading.Event()

    def fake_run(**kwargs):
        kwargs["event_callback"]({
            "type": "complete",
            "results": {"cancelled": False, "endpoints": []},
        })
        return {"cancelled": False, "endpoints": []}

    def fake_cleanup(emit=None):
        cleaned.set()

    monkeypatch.setattr(stress_test, "run_stress_test", fake_run)
    monkeypatch.setattr(stress_test, "cleanup_test_data", fake_cleanup)

    run = admin._start_stress_test_run(level=1, num_users=1)
    assert cleaned.wait(2), "cleanup did not run"

    deadline = time.monotonic() + 2
    while time.monotonic() < deadline:
        state = admin._stress_read_state(run["run_id"])
        if state.get("status") == "completed":
            break
        time.sleep(0.01)

    assert admin._stress_read_state(run["run_id"])["status"] == "completed"

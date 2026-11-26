"""Read-only HA status snapshot and attention entries."""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta

import pytest

from app.services import ha_status


@pytest.fixture(autouse=True)
def _clear_cache():
    ha_status.reset_cache()
    yield
    ha_status.reset_cache()


def _iso(seconds_ago: int = 0) -> str:
    value = datetime.now(UTC) - timedelta(seconds=seconds_ago)
    return value.isoformat().replace("+00:00", "Z")


def _write(
    tmp_path,
    monkeypatch,
    *,
    checked_at: str | None = None,
    role: str = "standby",
    state: str = "streaming",
    lag_bytes: int = 0,
    witness_contact: int = 0,
    witness_prod: str = "up",
    witness_dev: str = "up",
    last_failover=None,
    document: str | None = None,
):
    role_path = tmp_path / "role"
    role_path.write_text(role, encoding="utf-8")
    status_path = tmp_path / "status.json"
    if document is not None:
        status_path.write_text(document, encoding="utf-8")
    else:
        status_path.write_text(
            json.dumps(
                {
                    "checked_at": checked_at or _iso(),
                    "preferred": "prod",
                    "prod": {"app": "up", "db": "primary"},
                    "dev": {"app": "up", "db": "standby"},
                    "replication": {
                        "state": state,
                        "lag_bytes": lag_bytes,
                        "last_replay": "0/1",
                    },
                    "redis": {"master": "up", "sentinels": "2/2"},
                    "witness": {
                        "last_contact": _iso(witness_contact),
                        "prod": witness_prod,
                        "dev": witness_dev,
                    },
                    "last_failover": last_failover,
                }
            ),
            encoding="utf-8",
        )
    monkeypatch.setenv("OCR_HA_STATUS_PATH", str(status_path))
    monkeypatch.setenv("OCR_HA_ROLE_PATH", str(role_path))
    return status_path


def test_missing_snapshot_means_ha_is_not_configured(tmp_path, monkeypatch):
    monkeypatch.setenv("OCR_HA_STATUS_PATH", str(tmp_path / "missing.json"))
    monkeypatch.setenv("OCR_HA_ROLE_PATH", str(tmp_path / "missing-role"))

    snap = ha_status.snapshot()

    assert snap["available"] is False
    assert snap["verdict"] == "unknown"
    assert snap["role"] == "unknown"
    assert ha_status.attention_items() == []


def test_fresh_snapshot_is_ok(tmp_path, monkeypatch):
    _write(tmp_path, monkeypatch)

    snap = ha_status.snapshot()

    assert snap["available"] is True
    assert snap["stale"] is False
    assert snap["role"] == "standby"
    assert snap["preferred"] == "prod"
    assert snap["verdict"] == "ok"
    assert snap["age_seconds"] is not None and snap["age_seconds"] < 5
    assert snap["replication"]["state"] == "streaming"
    assert ha_status.attention_items() == []


def test_stale_snapshot_is_unknown(tmp_path, monkeypatch):
    _write(tmp_path, monkeypatch, checked_at=_iso(120))

    snap = ha_status.snapshot()

    assert snap["stale"] is True
    assert snap["verdict"] == "unknown"
    items = ha_status.attention_items()
    assert items[0]["name"] == "HA status"
    assert items[0]["status"] == "warning"


def test_not_streaming_is_an_error(tmp_path, monkeypatch):
    _write(tmp_path, monkeypatch, state="stopped")

    snap = ha_status.snapshot()

    assert snap["verdict"] == "error"
    items = ha_status.attention_items()
    assert items[0]["name"] == "HA replication"
    assert items[0]["status"] == "error"


def test_lag_warns(tmp_path, monkeypatch):
    _write(tmp_path, monkeypatch, lag_bytes=65 * 1024 * 1024)

    snap = ha_status.snapshot()

    assert snap["verdict"] == "warning"
    items = ha_status.attention_items()
    assert items[0]["name"] == "HA replication"
    assert items[0]["status"] == "warning"


def test_witness_silence_warns(tmp_path, monkeypatch):
    _write(tmp_path, monkeypatch, witness_contact=600)

    snap = ha_status.snapshot()

    assert snap["verdict"] == "warning"
    items = ha_status.attention_items()
    assert items[0]["name"] == "HA witness"
    assert items[0]["status"] == "warning"


def test_witness_down_warns(tmp_path, monkeypatch):
    _write(tmp_path, monkeypatch, witness_prod="down")

    snap = ha_status.snapshot()

    assert snap["verdict"] == "warning"
    items = ha_status.attention_items()
    assert items[0]["name"] == "HA witness"


def test_unverified_failover_warns(tmp_path, monkeypatch):
    _write(
        tmp_path,
        monkeypatch,
        last_failover={"at": _iso(60), "from": "prod", "to": "dev", "verified": False},
    )

    snap = ha_status.snapshot()

    assert snap["verdict"] == "warning"
    assert snap["last_failover"]["verified"] is False


def test_malformed_snapshot_is_unknown_not_an_exception(tmp_path, monkeypatch):
    _write(tmp_path, monkeypatch, document="{not-json")

    snap = ha_status.snapshot()

    assert snap["available"] is True
    assert snap["verdict"] == "unknown"
    items = ha_status.attention_items()
    assert items[0]["name"] == "HA status"


def test_unknown_fields_are_dropped(tmp_path, monkeypatch):
    document = {
        "checked_at": _iso(),
        "preferred": "prod",
        "replication": {"state": "streaming", "lag_bytes": 0},
        "witness": {"last_contact": _iso(), "prod": "up", "dev": "up"},
        "path": "/etc/passwd",
        "address": "192.0.2.10",
    }
    _write(tmp_path, monkeypatch, document=json.dumps(document))

    snap = ha_status.snapshot()

    assert "path" not in snap
    assert "address" not in snap
    assert "192.0.2.10" not in json.dumps(snap)


def test_role_marker_is_validated(tmp_path, monkeypatch):
    _write(tmp_path, monkeypatch, role="primary")
    assert ha_status.snapshot()["role"] == "primary"

    ha_status.reset_cache()
    _write(tmp_path, monkeypatch, role="not-a-role")
    assert ha_status.snapshot()["role"] == "unknown"

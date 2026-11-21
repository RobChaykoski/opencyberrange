"""Pre-flight checks for labs whose images were never pre-built."""

from __future__ import annotations

import json

import docker
import pytest

from app.models import ActivityEvent, LabSession
from app.services import lab_preflight
from app.services.activity import EventTypes
from app.services.docker_manager import DockerManager

BUILD_COMPOSE = """
services:
  target:
    build:
      context: ./containers/target
"""

IMAGE_ONLY_COMPOSE = """
services:
  target:
    image: alpine:3.20
"""


class _FakeImages:
    def __init__(self, tags):
        self.tags = set(tags)

    def get(self, tag):
        if tag in self.tags:
            return object()
        raise docker.errors.ImageNotFound(tag)


class _FakeClient:
    def __init__(self, tags):
        self.images = _FakeImages(tags)


def test_prebuild_command_is_exact():
    assert (
        lab_preflight.prebuild_command("network-0-1-ping-basics")
        == "scripts/prebuild-labs.sh --lab network-0-1-ping-basics"
    )


def test_missing_build_service_is_detected():
    missing = lab_preflight.missing_built_services(
        "demo-lab", BUILD_COMPOSE, _FakeClient(set())
    )
    assert missing == ["target"]


def test_prebuilt_ocr_lab_tag_satisfies_check():
    missing = lab_preflight.missing_built_services(
        "demo-lab",
        BUILD_COMPOSE,
        _FakeClient({"ocr-lab/demo-lab-target:latest"}),
    )
    assert missing == []


def test_explicit_compose_image_tag_satisfies_check():
    compose = """
services:
  target:
    build: .
    image: registry.example/ocr/demo:1.2.3
"""
    missing = lab_preflight.missing_built_services(
        "demo-lab",
        compose,
        _FakeClient({"registry.example/ocr/demo:1.2.3"}),
    )
    assert missing == []


def test_image_only_services_are_not_gated():
    missing = lab_preflight.missing_built_services(
        "demo-lab", IMAGE_ONLY_COMPOSE, _FakeClient(set())
    )
    assert missing == []


def test_lab_without_services_is_not_gated():
    missing = lab_preflight.missing_built_services(
        "demo-lab", "services: {}\n", _FakeClient(set())
    )
    assert missing == []


def test_unavailable_docker_fails_open():
    assert lab_preflight.missing_built_services("demo-lab", BUILD_COMPOSE, None) is None


@pytest.mark.db
def test_refused_launch_records_exact_command(db_session, test_lab, test_user, monkeypatch):
    monkeypatch.setattr(DockerManager, "ALLOW_ON_DEMAND_BUILD", False)
    db_session.query(ActivityEvent).filter(
        ActivityEvent.event_type == EventTypes.LAB_PREBUILD_REQUIRED,
        ActivityEvent.target_id == test_lab.id,
    ).delete()
    db_session.commit()

    lab_preflight.record_prebuild_required(db_session, test_lab, test_user.id)

    event = db_session.query(ActivityEvent).filter(
        ActivityEvent.event_type == EventTypes.LAB_PREBUILD_REQUIRED,
        ActivityEvent.target_id == test_lab.id,
    ).one()
    detail = json.loads(event.detail)
    assert detail["command"] == f"scripts/prebuild-labs.sh --lab {test_lab.slug}"

    # A second click within the hour is deduplicated.
    lab_preflight.record_prebuild_required(db_session, test_lab, test_user.id)
    count = db_session.query(ActivityEvent).filter(
        ActivityEvent.event_type == EventTypes.LAB_PREBUILD_REQUIRED,
        ActivityEvent.target_id == test_lab.id,
    ).count()
    assert count == 1

    db_session.query(ActivityEvent).filter(
        ActivityEvent.event_type == EventTypes.LAB_PREBUILD_REQUIRED,
        ActivityEvent.target_id == test_lab.id,
    ).delete()
    db_session.commit()


@pytest.mark.db
def test_health_warns_with_command_until_image_is_built(
    db_session, test_lab, test_user, monkeypatch
):
    monkeypatch.setattr(DockerManager, "ALLOW_ON_DEMAND_BUILD", False)
    lab_preflight.record_prebuild_required(db_session, test_lab, test_user.id)

    monkeypatch.setattr(
        lab_preflight, "missing_built_services", lambda *args, **kwargs: ["target"]
    )
    item = lab_preflight.prebuild_health(db_session, object())
    assert item is not None
    assert item["status"] == "warning"
    assert item["commands"] == [
        f"scripts/prebuild-labs.sh --lab {test_lab.slug}"
    ]

    # Once the image exists the warning clears without an admin dismissing it.
    monkeypatch.setattr(
        lab_preflight, "missing_built_services", lambda *args, **kwargs: []
    )
    item = lab_preflight.prebuild_health(db_session, object())
    assert item["status"] == "ok"
    assert item["commands"] == []

    db_session.query(ActivityEvent).filter(
        ActivityEvent.event_type == EventTypes.LAB_PREBUILD_REQUIRED,
        ActivityEvent.target_id == test_lab.id,
    ).delete()
    db_session.commit()


@pytest.mark.db
def test_spawn_returns_friendly_message_for_unbuilt_lab(
    client, db_session, test_lab, test_user, auth_headers, monkeypatch
):
    monkeypatch.setattr(DockerManager, "ALLOW_ON_DEMAND_BUILD", False)
    monkeypatch.setattr(
        lab_preflight, "missing_built_services", lambda *args, **kwargs: ["target"]
    )

    response = client.post(
        f"/api/labs/spawn/{test_lab.slug}",
        headers=auth_headers,
        json={"rangebox": False},
    )

    assert response.status_code == 409
    assert "still being prepared by your instructor" in response.json()["detail"]

    # The refusal happens before a session row is created, so the student is
    # not left with a phantom active session they must clear.
    assert (
        db_session.query(LabSession)
        .filter(LabSession.user_id == test_user.id)
        .count()
        == 0
    )

    event = db_session.query(ActivityEvent).filter(
        ActivityEvent.event_type == EventTypes.LAB_PREBUILD_REQUIRED,
        ActivityEvent.target_id == test_lab.id,
    ).one()
    assert json.loads(event.detail)["lab_slug"] == test_lab.slug

    db_session.query(ActivityEvent).filter(
        ActivityEvent.event_type == EventTypes.LAB_PREBUILD_REQUIRED,
        ActivityEvent.target_id == test_lab.id,
    ).delete()
    db_session.commit()


def test_health_is_silent_when_on_demand_builds_are_allowed(monkeypatch, db_session):
    monkeypatch.setattr(DockerManager, "ALLOW_ON_DEMAND_BUILD", True)
    assert lab_preflight.prebuild_health(db_session, None) is None

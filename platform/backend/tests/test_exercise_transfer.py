"""Exercise export/import: reusable ZIP round trip and draft safety."""

from __future__ import annotations

import hashlib
import io
import json
import string
import uuid
import zipfile

import pytest
import yaml

from app.auth import get_password_hash
from app.models import Lab, Level, Track, User
from app.services import exercise_transfer, lab_upload

# Test-only login credential; security-delta: allow credential-like assignment
PASSWORD = "Exercise#Pass123"
pytestmark = pytest.mark.db


def _make_user(db_session, role="admin"):
    suffix = uuid.uuid4().hex[:8]
    user = User(
        username=f"transfer_{role}_{suffix}",
        email=f"transfer_{role}_{suffix}@example.org",
        hashed_password=get_password_hash(PASSWORD),
        is_active=True,
        is_approved=True,
        is_admin=role == "admin",
        role=role,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def _headers(client, user):
    response = client.post(
        "/api/auth/login",
        data={"username": user.username, "password": PASSWORD},
    )
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def _track_level(db_session):
    suffix = "".join(string.ascii_lowercase[int(ch, 16)] for ch in uuid.uuid4().hex[:8])
    track = Track(
        name=f"Transfer Track {suffix}",
        slug=f"transfer{suffix}",
        is_active=True,
    )
    db_session.add(track)
    db_session.flush()
    level = Level(
        track_id=track.id,
        level_number=1,
        name="Transfer Level",
    )
    db_session.add(level)
    db_session.commit()
    db_session.refresh(track)
    db_session.refresh(level)
    return track, level


def _lab(db_session, track, level):
    suffix = uuid.uuid4().hex[:8]
    lab = Lab(
        name=f"Transfer Lab {suffix}",
        slug=f"{track.slug}-1-1-transfer-{suffix}",
        description="Export me",
        compose_file="services: {}\n",
        is_active=True,
        visibility="public",
        level_id=level.id,
        difficulty="beginner",
        category="network",
        duration_minutes=30,
        mapped_skills=json.dumps(["network_systems"]),
        assessment_criteria=json.dumps(["Submit the flag."]),
        prerequisites="[]",
        objectives=json.dumps(["Do the thing"]),
        mitre_attack=json.dumps(
            [
                {
                    "tactic": "Discovery",
                    "technique": "T1046",
                    "technique_name": "Network Service Discovery",
                    "detection": "Monitor scan traffic.",
                }
            ]
        ),
    )
    db_session.add(lab)
    db_session.commit()
    db_session.refresh(lab)
    return lab


def _write_lab_dir(root, lab, flag="OCR{original_flag}"):
    lab_dir = root / "Linux" / lab.slug
    (lab_dir / "containers" / "target").mkdir(parents=True)
    (lab_dir / "__pycache__").mkdir()
    (lab_dir / "__pycache__" / "ignored.pyc").write_bytes(b"noise")
    (lab_dir / "lab.yaml").write_text(
        "title: Transfer Lab\n"
        "category: network\n"
        "difficulty: beginner\n"
        "estimated_time: 30\n"
        "prerequisites: []\n"
        "learning_outcomes:\n"
        "  - Do the thing\n"
        "mapped_skills:\n"
        "  - network_systems\n"
        "assessment_criteria:\n"
        "  - Submit the flag.\n"
        "mitre_attack:\n"
        "  - tactic: Discovery\n"
        "    technique: T1046\n"
        "    technique_name: Network Service Discovery\n"
        "    detection: Monitor scan traffic.\n"
        f"flag: \"{flag}\"\n"
        "description: A reusable exercise.\n",
        encoding="utf-8",
    )
    (lab_dir / "docker-compose.yml").write_text(
        "services:\n  target:\n    image: demo\n", encoding="utf-8"
    )
    (lab_dir / "containers" / "target" / "Dockerfile").write_text(
        "FROM alpine\n", encoding="utf-8"
    )
    return lab_dir


def _source_zip(flag="OCR{original_flag}", wrapper="reuse/"):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(
            f"{wrapper}lab.yaml",
            yaml.safe_dump(
                {
                    "title": "Imported Reuse Lab",
                    "category": "network",
                    "difficulty": "beginner",
                    "estimated_time": 30,
                    "prerequisites": [],
                    "learning_outcomes": ["Do the thing"],
                    "mapped_skills": ["network_systems"],
                    "assessment_criteria": ["Submit the flag."],
                    "mitre_attack": [
                        {
                            "tactic": "Discovery",
                            "technique": "T1046",
                            "technique_name": "Network Service Discovery",
                            "detection": "Monitor scan traffic.",
                        }
                    ],
                    "flag": flag,
                    "description": "A reusable exercise.",
                },
                sort_keys=False,
            ),
        )
        archive.writestr(
            f"{wrapper}docker-compose.yml",
            "services:\n  target:\n    image: demo\n",
        )
        archive.writestr(
            f"{wrapper}containers/target/Dockerfile", "FROM alpine\n"
        )
    return buffer.getvalue()


def _zip_names(contents):
    with zipfile.ZipFile(io.BytesIO(contents)) as archive:
        return set(archive.namelist())


def test_export_scrubs_flag_and_keeps_source_files(tmp_path, db_session, monkeypatch):
    track, level = _track_level(db_session)
    lab = _lab(db_session, track, level)
    try:
        _write_lab_dir(tmp_path, lab)
        monkeypatch.setattr(exercise_transfer, "_labs_roots", lambda: [str(tmp_path)])

        contents, filename = exercise_transfer.export_lab_zip(
            db_session, lab, include_flag=False
        )
        names = _zip_names(contents)
        assert "lab.yaml" in names
        assert "docker-compose.yml" in names
        assert "containers/target/Dockerfile" in names
        assert "export-manifest.json" in names
        assert "EXPORT-README.md" in names
        assert not any("__pycache__" in name for name in names)
        assert filename.endswith("-export.zip")

        with zipfile.ZipFile(io.BytesIO(contents)) as archive:
            data = yaml.safe_load(archive.read("lab.yaml"))
            manifest = json.loads(archive.read("export-manifest.json"))
        assert data["flag"] == exercise_transfer.PLACEHOLDER_FLAG
        assert data["mapped_skills"] == ["network_systems"]
        assert manifest["format"] == exercise_transfer.FORMAT
        assert manifest["flag_included"] is False
    finally:
        cleanup_lab(db_session, lab)


def test_export_can_include_flag_for_trusted_backup(tmp_path, db_session, monkeypatch):
    track, level = _track_level(db_session)
    lab = _lab(db_session, track, level)
    try:
        _write_lab_dir(tmp_path, lab, flag="OCR{backup_flag}")
        monkeypatch.setattr(exercise_transfer, "_labs_roots", lambda: [str(tmp_path)])

        contents, _filename = exercise_transfer.export_lab_zip(
            db_session, lab, include_flag=True
        )
        with zipfile.ZipFile(io.BytesIO(contents)) as archive:
            data = yaml.safe_load(archive.read("lab.yaml"))
            manifest = json.loads(archive.read("export-manifest.json"))
        assert data["flag"] == "OCR{backup_flag}"
        assert manifest["flag_included"] is True
    finally:
        cleanup_lab(db_session, lab)


def test_import_creates_a_draft_with_a_new_flag(tmp_path, db_session, monkeypatch):
    track, level = _track_level(db_session)
    admin = _make_user(db_session)
    monkeypatch.setattr(lab_upload, "LABS_ROOT", str(tmp_path))
    monkeypatch.setattr(
        exercise_transfer, "get_track_directory_name", lambda slug: "Linux"
    )
    try:
        result = exercise_transfer.import_lab_zip(
            db_session,
            user_id=admin.id,
            contents=_source_zip(),
            track_slug=track.slug,
            level_id=level.id,
        )
        assert result["visibility"] == "draft"
        assert result["flag_generated"] is True
        assert result["generated_flag"].startswith("OCR{")
        lab = db_session.query(Lab).filter(Lab.id == result["id"]).one()
        assert lab.created_by == admin.id
        assert lab.level_id == level.id
        assert lab.slug.startswith(f"{track.slug}-1-1-")
        assert lab.mapped_skills == json.dumps(["network_systems"])
        assert lab.mitre_attack and "T1046" in lab.mitre_attack
        assert lab.flag_hash is not None
        extracted = tmp_path / "Linux" / lab.slug / "lab.yaml"
        assert result["generated_flag"] in extracted.read_text(encoding="utf-8")
    finally:
        cleanup_track(db_session, track)


def test_import_accepts_a_provided_flag_and_reuses_exported_flag(
    tmp_path, db_session, monkeypatch
):
    track, level = _track_level(db_session)
    admin = _make_user(db_session)
    monkeypatch.setattr(lab_upload, "LABS_ROOT", str(tmp_path))
    monkeypatch.setattr(
        exercise_transfer, "get_track_directory_name", lambda slug: "Linux"
    )
    try:
        provided = exercise_transfer.import_lab_zip(
            db_session,
            user_id=admin.id,
            contents=_source_zip(),
            track_slug=track.slug,
            level_id=level.id,
            name_override="Provided Flag Lab",
            flag="OCR{provided_flag}",
        )
        lab = db_session.query(Lab).filter(Lab.id == provided["id"]).one()
        assert lab.flag_hash == hashlib.sha256(
            b"OCR{provided_flag}"
        ).hexdigest()
        assert provided["flag_generated"] is False

        reused = exercise_transfer.import_lab_zip(
            db_session,
            user_id=admin.id,
            contents=_source_zip(flag="OCR{exported_flag}"),
            track_slug=track.slug,
            level_id=level.id,
            name_override="Reused Flag Lab",
            reuse_flag=True,
        )
        lab = db_session.query(Lab).filter(Lab.id == reused["id"]).one()
        assert lab.flag_hash == hashlib.sha256(
            b"OCR{exported_flag}"
        ).hexdigest()
        assert reused["flag_generated"] is False
    finally:
        cleanup_track(db_session, track)


def test_import_rejects_missing_lab_yaml(tmp_path, db_session, monkeypatch):
    track, level = _track_level(db_session)
    admin = _make_user(db_session)
    monkeypatch.setattr(lab_upload, "LABS_ROOT", str(tmp_path))
    try:
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as archive:
            archive.writestr("docker-compose.yml", "services: {}\n")
        with pytest.raises(exercise_transfer.ExerciseTransferError) as exc:
            exercise_transfer.import_lab_zip(
                db_session,
                user_id=admin.id,
                contents=buffer.getvalue(),
                track_slug=track.slug,
                level_id=level.id,
            )
        assert "lab.yaml" in str(exc.value)
    finally:
        cleanup_track(db_session, track)


def test_admin_and_instructor_export_and_admin_import(
    client, db_session, tmp_path, monkeypatch
):
    track, level = _track_level(db_session)
    lab = _lab(db_session, track, level)
    admin = _make_user(db_session)
    instructor = _make_user(db_session, "instructor")
    student = _make_user(db_session, "student")
    monkeypatch.setattr(lab_upload, "LABS_ROOT", str(tmp_path))
    monkeypatch.setattr(
        exercise_transfer, "get_track_directory_name", lambda slug: "Linux"
    )
    try:
        _write_lab_dir(tmp_path, lab)
        monkeypatch.setattr(exercise_transfer, "_labs_roots", lambda: [str(tmp_path)])

        admin_headers = _headers(client, admin)
        instructor_headers = _headers(client, instructor)
        student_headers = _headers(client, student)

        denied = client.get(
            f"/api/admin/labs/{lab.id}/export", headers=student_headers
        )
        assert denied.status_code == 403

        exported = client.get(
            f"/api/admin/labs/{lab.id}/export", headers=admin_headers
        )
        assert exported.status_code == 200, exported.text
        assert exported.content.startswith(b"PK")
        assert exported.headers["content-type"].startswith("application/zip")
        assert "attachment" in exported.headers["content-disposition"]

        instructor_export = client.get(
            f"/api/instructor/labs/{lab.id}/export", headers=instructor_headers
        )
        assert instructor_export.status_code == 200, instructor_export.text
        assert instructor_export.content.startswith(b"PK")

        imported = client.post(
            "/api/admin/labs/import",
            files={"file": ("reuse.zip", _source_zip(), "application/zip")},
            data={
                "track": track.slug,
                "level_id": str(level.id),
                "name": "API Imported Lab",
                "flag": "OCR{api_import_flag}",
            },
            headers=admin_headers,
        )
        assert imported.status_code == 201, imported.text
        body = imported.json()
        assert body["visibility"] == "draft"
        assert body["file_count"] >= 3
        imported_lab = db_session.query(Lab).filter(Lab.id == body["id"]).one()
        assert imported_lab.created_by == admin.id
        assert imported_lab.flag_hash == hashlib.sha256(
            b"OCR{api_import_flag}"
        ).hexdigest()
    finally:
        cleanup_track(db_session, track)


def cleanup_lab(db_session, lab):
    db_session.query(Lab).filter(Lab.id == lab.id).delete()
    db_session.commit()


def cleanup_track(db_session, track):
    level_ids = [level.id for level in track.levels]
    for lab in db_session.query(Lab).filter(Lab.level_id.in_(level_ids)).all():
        db_session.delete(lab)
    db_session.commit()
    for level in list(track.levels):
        db_session.delete(level)
    db_session.commit()
    db_session.delete(track)
    db_session.commit()

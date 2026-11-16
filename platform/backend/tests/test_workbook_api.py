"""Workbook APIs: instructor-only upload/build/delete with safe paths.

The workbook router is a dev-tool module mounted at ``/api/admin/workbook``.
Filesystem work is stubbed so the tests cover the HTTP contract without
touching the real ``Workbook`` volume.
"""

import io
import uuid
import zipfile
from datetime import datetime, timedelta, timezone

import pytest

from app.auth import get_password_hash
from app.models import Course, User
from app.routers import workbook as workbook_router
from app.services import workbook_builder

# Test-only login credential; security-delta: allow credential-like assignment
PASSWORD = "Workbook#Pass123"
pytestmark = pytest.mark.db


def _make_user(db_session, role):
    suffix = uuid.uuid4().hex[:8]
    user = User(
        username=f"workbook_{role}_{suffix}",
        email=f"workbook_{role}_{suffix}@example.org",
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


def _zip_bytes(name="notes.md", content="# Week 1"):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr(name, content)
    return buffer.getvalue()


def _failing_build():
    raise RuntimeError("mkdocs missing")


def _course(db_session, instructor):
    suffix = uuid.uuid4().hex[:8]
    now = datetime.now(timezone.utc)
    course = Course(
        name=f"Workbook Course {suffix}",
        code=f"WB{suffix[:5].upper()}",
        semester="Fall",
        invite_code=f"WB-{suffix}",
        instructor_id=instructor.id,
        start_date=now - timedelta(days=1),
        end_date=now + timedelta(days=30),
        is_active=True,
        wiki_slug=f"course-{suffix}",
    )
    db_session.add(course)
    db_session.commit()
    db_session.refresh(course)
    return course


def test_workbook_requires_instructor(client, db_session):
    student = _make_user(db_session, "student")
    headers = _headers(client, student)

    assert client.get("/api/admin/workbook/chapters").status_code == 401
    assert (
        client.get("/api/admin/workbook/chapters", headers=headers).status_code
        == 403
    )
    assert (
        client.post("/api/admin/workbook/build", headers=headers).status_code
        == 403
    )
    upload = client.post(
        "/api/admin/workbook/upload",
        files={"file": ("chapter.zip", _zip_bytes(), "application/zip")},
        data={"chapter_dir": "CH_TEST"},
        headers=headers,
    )
    assert upload.status_code == 403
    assert (
        client.delete(
            "/api/admin/workbook/chapter/CH_TEST", headers=headers
        ).status_code
        == 403
    )


def test_workbook_chapters_build_and_course_wikis(client, db_session, monkeypatch):
    instructor = _make_user(db_session, "instructor")
    headers = _headers(client, instructor)

    monkeypatch.setattr(
        workbook_builder,
        "list_chapters",
        lambda: [{"dir": "CH01", "files": ["01_intro.md"]}],
    )
    chapters = client.get("/api/admin/workbook/chapters", headers=headers)
    assert chapters.status_code == 200, chapters.text
    assert chapters.json()[0]["dir"] == "CH01"

    monkeypatch.setattr(workbook_builder, "build_wiki", lambda: {"success": True})
    build = client.post("/api/admin/workbook/build", headers=headers)
    assert build.status_code == 200, build.text
    assert build.json() == {"success": True}

    monkeypatch.setattr(workbook_builder, "build_wiki", _failing_build)
    failed = client.post("/api/admin/workbook/build", headers=headers)
    assert failed.status_code == 500
    assert "wiki build failed" in failed.json()["detail"]

    course = _course(db_session, instructor)
    monkeypatch.setattr(
        workbook_router,
        "rebuild_course_wiki",
        lambda db, row: {"success": True},
    )
    built = client.post("/api/admin/workbook/build-all-course-wikis", headers=headers)
    assert built.status_code == 200, built.text
    body = built.json()
    assert any(row["slug"] == course.wiki_slug for row in body["results"])
    assert body["courses_built"] >= 1


def test_workbook_upload_reporting(client, db_session, monkeypatch):
    instructor = _make_user(db_session, "instructor")
    headers = _headers(client, instructor)

    not_zip = client.post(
        "/api/admin/workbook/upload",
        files={"file": ("notes.md", b"# nope", "text/markdown")},
        data={"chapter_dir": "CH_UPLOAD"},
        headers=headers,
    )
    assert not_zip.status_code == 400
    assert "zip" in not_zip.json()["detail"]

    monkeypatch.setattr(
        workbook_builder,
        "extract_upload",
        lambda data, name: {"files_extracted": 0},
    )
    empty = client.post(
        "/api/admin/workbook/upload",
        files={"file": ("chapter.zip", _zip_bytes(), "application/zip")},
        data={"chapter_dir": "CH_UPLOAD"},
        headers=headers,
    )
    assert empty.status_code == 400
    assert "No .md files" in empty.json()["detail"]

    monkeypatch.setattr(
        workbook_builder,
        "extract_upload",
        lambda data, name: {"files_extracted": 2, "chapter_dir": name},
    )
    monkeypatch.setattr(workbook_builder, "build_wiki", lambda: {"success": True})
    monkeypatch.setattr(
        workbook_router,
        "rebuild_affected_course_wikis",
        lambda db, name: [{"ok": True}],
    )

    uploaded = client.post(
        "/api/admin/workbook/upload",
        files={"file": ("chapter.zip", _zip_bytes(), "application/zip")},
        data={"chapter_dir": "CH_UPLOAD"},
        headers=headers,
    )
    assert uploaded.status_code == 200, uploaded.text
    body = uploaded.json()
    assert body["files_extracted"] == 2
    assert body["build"] == {"success": True}
    assert body["course_wikis_rebuilt"] == 1

    monkeypatch.setattr(workbook_builder, "build_wiki", _failing_build)
    warned = client.post(
        "/api/admin/workbook/upload",
        files={"file": ("chapter.zip", _zip_bytes(), "application/zip")},
        data={"chapter_dir": "CH_UPLOAD"},
        headers=headers,
    )
    assert warned.status_code == 200, warned.text
    assert "build_warning" in warned.json()
    assert "build" not in warned.json()

    def failing_extract(data, name):
        raise RuntimeError("bad archive")

    monkeypatch.setattr(workbook_builder, "extract_upload", failing_extract)
    broken = client.post(
        "/api/admin/workbook/upload",
        files={"file": ("chapter.zip", _zip_bytes(), "application/zip")},
        data={"chapter_dir": "CH_UPLOAD"},
        headers=headers,
    )
    assert broken.status_code == 400
    assert "could not be extracted" in broken.json()["detail"]


def test_workbook_delete_only_removes_listed_chapters(
    client, db_session, monkeypatch, tmp_path
):
    instructor = _make_user(db_session, "instructor")
    headers = _headers(client, instructor)

    docs = tmp_path / "docs"
    chapter = docs / "CH_KEEP"
    chapter.mkdir(parents=True)
    (chapter / "01.md").write_text("# one", encoding="utf-8")
    outside = tmp_path / "outside.txt"
    outside.write_text("keep", encoding="utf-8")

    monkeypatch.setattr(workbook_builder, "DOCS_DIR", str(docs))
    monkeypatch.setattr(workbook_builder, "build_wiki", lambda: {"success": True})
    monkeypatch.setattr(
        workbook_router,
        "rebuild_affected_course_wikis",
        lambda db, name: [],
    )

    traversal = client.delete(
        "/api/admin/workbook/chapter/outside.txt", headers=headers
    )
    assert traversal.status_code == 404
    assert outside.exists()

    missing = client.delete(
        "/api/admin/workbook/chapter/CH_MISSING", headers=headers
    )
    assert missing.status_code == 404

    deleted = client.delete("/api/admin/workbook/chapter/CH_KEEP", headers=headers)
    assert deleted.status_code == 200, deleted.text
    assert deleted.json()["deleted"] == "CH_KEEP"
    assert deleted.json()["build"] == {"success": True}
    assert not chapter.exists()

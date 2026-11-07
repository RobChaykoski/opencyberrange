"""Career dossier rendering and access safeguards."""

from app.routers.profile import _safe_export_name
from app.services.career_profile import render_html, render_markdown


def _dossier():
    return {
        "generated_at": "2026-11-07T00:00:00+00:00",
        "identity": {
            "username": "test_learner",
            "display_name": "Test Learner",
            "email": "test@example.invalid",
            "organization": "Test School",
            "member_since": "2026-01-01T00:00:00",
        },
        "headline": "A practice snapshot, not a job label.",
        "cyber_dna": {
            "formula_version": "2026.11",
            "overall": 42,
            "tier": "Apprentice",
            "class": {
                "key": "investigator",
                "label": "Investigator",
                "class_name": "Seeker",
                "certification_key": "forensics",
                "certification_focus": "DFIR",
            },
            "dimensions": [
                {
                    "key": "investigator",
                    "label": "Investigator",
                    "class_name": "Seeker",
                    "tier": "Apprentice",
                    "score": 42,
                    "evidence": "2 analysis labs",
                }
            ],
            "affinities": [
                {
                    "key": "investigative",
                    "label": "DFIR / Investigation",
                    "summary": "Evidence work.",
                    "roles": ["DFIR analyst"],
                    "evidence_level": "early",
                    "evidence": "2 analysis labs",
                    "next_step": "Try a timeline exercise.",
                    "recommended": True,
                }
            ],
            "equipped_title": "Seeker",
        },
        "learning": {
            "completed_exercises": 2,
            "started_exercises": 3,
            "learning_minutes": 60,
            "learning_hours": 1.0,
            "clean_solves": 1,
            "hint_free_rate": 50.0,
            "first_attempt_rate": 50.0,
            "advanced_exercises": 0,
        },
        "courses": [{"code": "TST101", "name": "Test Course", "semester": "2026F"}],
        "achievements": ["First Blood"],
        "recommended_next_steps": [
            {"title": "DFIR", "action": "Try a timeline exercise.", "why": "2 analysis labs"}
        ],
        "external_resources": [
            {
                "label": "Example",
                "url": "https://example.invalid/",
                "use": "Reference only.",
            }
        ],
        "reflection_questions": ["What felt energising?"],
        "privacy_note": "Not for hiring or ranking.",
    }


def test_career_html_escapes_identity_fields():
    dossier = _dossier()
    dossier["identity"]["display_name"] = '<script>alert("x")</script>'
    dossier["identity"]["organization"] = "<img src=x onerror=alert(1)>"

    html = render_html(dossier)

    assert "<script>" not in html
    assert "<img src=x" not in html
    assert "&lt;script&gt;" in html
    assert "&lt;img src=x" in html


def test_career_markdown_contains_privacy_note_and_resources():
    markdown = render_markdown(_dossier())
    assert "# Career profile: Test Learner" in markdown
    assert "Not for hiring or ranking." in markdown
    assert "[Example](" in markdown
    assert "Reference only." in markdown


def test_career_export_filename_is_sanitised():
    assert _safe_export_name('normal_user') == 'normal_user'
    assert _safe_export_name('bad"name\r\nX-Test: 1') == 'badnameX-Test1'
    assert _safe_export_name('') == 'learner'


def test_career_endpoints_require_authentication(client):
    for path in (
        "/api/profile/career-dossier",
        "/api/profile/career-dossier.md",
        "/api/profile/career-dossier.html",
    ):
        response = client.get(path)
        assert response.status_code == 401, (path, response.text)

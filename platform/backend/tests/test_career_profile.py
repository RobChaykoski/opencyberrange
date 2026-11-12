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
            "formula_version": "2026.12",
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


def _advanced_dossier():
    dossier = _dossier()
    dossier["momentum"] = {
        "version": "2026.1",
        "window": "Recent half compared with the earlier half.",
        "summary": {
            "completed": 4,
            "started": 5,
            "clean_solves": 2,
            "clean_rate": 50.0,
            "active_branches": 2,
            "gaining_branches": 1,
            "friction_branches": 0,
        },
        "branches": [
            {
                "key": "tester",
                "label": "Tester",
                "status": "steady",
                "status_label": "Steady",
                "completed": 2,
                "hint_rate": 50.0,
                "first_attempt_rate": 50.0,
                "friction_score": 30,
                "movement": {"label": "Steady", "delta": 0},
            }
        ],
        "gaining": [],
        "friction": [],
        "stuck_points": [],
        "next_move": "Try one more Tester exercise.",
        "disclaimer": "Descriptive signals, not grades.",
    }
    salary = {
        "low": 62400,
        "median": 103000,
        "high": 150000,
        "currency": "CAD",
        "occupation": "Cybersecurity specialists (NOC 21220)",
        "source_label": "Canada Job Bank",
        "as_of": "2025-11-19",
        "basis": "Annualised at 2,080 hours.",
    }
    dossier["career_atlas"] = {
        "version": "2026.1",
        "regions": [{"key": "ca", "label": "Canada", "currency": "CAD"}],
        "sources": [
            {
                "key": "ca_jobbank",
                "label": "Canada Job Bank",
                "detail": "Statistics Canada Labour Force Survey.",
                "basis": "Annualised at 2,080 hours.",
                "url": "https://example.invalid/jobbank",
            }
        ],
        "summary": {"families": 1, "unlocked": 1, "next": 0, "locked": 0},
        "branches": [],
        "families": [
            {
                "key": "offensive",
                "label": "Offensive Security",
                "summary": "Authorised testing.",
                "branch_label": "Tester",
                "unlock_state": "unlocked",
                "unlock_hint": "Unlocked by practice evidence.",
                "match_score": 81,
                "recommended": True,
                "next_step": "Write a finding.",
                "roles": [
                    {
                        "title": "Penetration Tester",
                        "level": "core",
                        "salary": {"ca": salary, "us": {**salary, "currency": "USD"}},
                    }
                ],
            }
        ],
        "recommended_family_key": "offensive",
        "disclaimer": "Not a job prediction.",
        "salary_note": "Not an offer.",
    }
    return dossier


def test_career_markdown_includes_momentum_and_career_atlas():
    markdown = render_markdown(_advanced_dossier())
    assert "## Momentum and friction" in markdown
    assert "## Career atlas" in markdown
    assert "Penetration Tester" in markdown
    assert "Canada Job Bank" in markdown


def test_career_html_includes_and_escapes_advanced_sections():
    dossier = _advanced_dossier()
    dossier["career_atlas"]["families"][0]["label"] = "<script>alert(1)</script>"
    html = render_html(dossier)
    assert "Momentum and friction" in html
    assert "Career atlas" in html
    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;" in html


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

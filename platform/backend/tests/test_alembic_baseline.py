"""Alembic baseline and revision graph checks."""

from __future__ import annotations

from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory

BACKEND = Path(__file__).resolve().parents[1]


def _script() -> ScriptDirectory:
    cfg = Config(str(BACKEND / "alembic.ini"))
    cfg.set_main_option("script_location", str(BACKEND / "alembic"))
    return ScriptDirectory.from_config(cfg)


def test_alembic_head_is_the_metadata_revision():
    script = _script()
    heads = script.get_heads()
    assert heads == ["0026_impersonation_sessions"]


def test_revision_graph_is_linear():
    script = _script()
    revisions = list(script.walk_revisions())
    assert revisions
    # walk_revisions yields head first; each row's down_revision must match the
    # next row's revision id.
    for current, previous in zip(revisions, revisions[1:], strict=False):
        assert current.down_revision == previous.revision


def test_baseline_revision_exists():
    versions = BACKEND / "alembic" / "versions"
    names = {path.name for path in versions.glob("*.py")}
    assert "0001_baseline.py" in names
    assert "0013_achievement_event_metadata.py" in names
    assert "0014_performance_indexes.py" in names
    assert "0015_lti_platforms.py" in names
    assert "0016_lti_links_scores.py" in names
    assert "0017_lti_nrps.py" in names
    assert "0018_lti_roster.py" in names
    assert "0019_lti_deep_link.py" in names
    assert "0020_lti_dl_multiple.py" in names
    assert "0021_accommodations.py" in names
    assert "0022_lab_pause.py" in names
    assert "0023_minor_consent.py" in names
    assert "0024_retention.py" in names
    assert "0026_impersonation_sessions.py" in names


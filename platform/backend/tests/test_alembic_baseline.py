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
    assert heads == ["0047_lab_nice_metadata"]


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
    assert "0030_cohort_strict.py" in names
    assert "0031_learner_snapshots.py" in names
    assert "0032_cyber_dna.py" in names
    assert "0033_consent_revocation.py" in names
    assert "0034_security_events_rbac.py" in names
    assert "0035_tenant_rls.py" in names
    assert "0036_service_identities.py" in names
    assert "0037_auth_lifecycle.py" in names
    assert "0038_security_version.py" in names
    assert "0039_db_invariants.py" in names
    assert "0040_settings_change_control.py" in names
    assert "0041_tenant_rls_legacy.py" in names






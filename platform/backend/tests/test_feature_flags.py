"""Feature-gate contracts for development-only surfaces."""

from app.services import feature_flags


def test_setting_enabled_accepts_truthy_values(monkeypatch):
    for value in ("1", "true", "TRUE", "yes", "on", "enabled"):
        monkeypatch.setattr(
            feature_flags,
            "get_setting_fresh",
            lambda db, key, default, value=value: value,
        )
        assert feature_flags.setting_enabled(object(), "test_flag") is True


def test_setting_enabled_rejects_other_values(monkeypatch):
    for value in ("0", "false", "off", "", None, "no"):
        monkeypatch.setattr(
            feature_flags,
            "get_setting_fresh",
            lambda db, key, default, value=value: value,
        )
        assert feature_flags.setting_enabled(object(), "test_flag") is False


def test_advanced_dna_insights_uses_the_expected_key(monkeypatch):
    seen = {}

    def fake_get(db, key, default):
        seen["key"] = key
        seen["default"] = default
        return "false"

    monkeypatch.setattr(feature_flags, "get_setting_fresh", fake_get)
    assert feature_flags.advanced_dna_insights_enabled(object()) is False
    assert seen == {
        "key": feature_flags.ADVANCED_DNA_INSIGHTS,
        "default": "false",
    }

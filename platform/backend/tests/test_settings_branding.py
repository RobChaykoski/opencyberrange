"""The SWOCTS Cyber Range rename migrates only the old seeded default."""

from app.models import PlatformSetting
from app.services import settings_service


def _set_from_name(db_session, value):
    db_session.query(PlatformSetting).filter(
        PlatformSetting.key == "mail_from_name"
    ).delete()
    db_session.add(
        PlatformSetting(
            key="mail_from_name",
            value=value,
            category="email",
            description="Display name for the From address",
            is_secret=False,
        )
    )
    db_session.commit()


def test_seed_defaults_migrates_old_brand_name(db_session):
    _set_from_name(db_session, "OpenCyberRange")

    settings_service.seed_defaults(db_session)

    db_session.expire_all()
    row = db_session.query(PlatformSetting).filter(
        PlatformSetting.key == "mail_from_name"
    ).one()
    assert row.value == "SWOCTS Cyber Range"


def test_seed_defaults_preserves_custom_from_name(db_session):
    _set_from_name(db_session, "Example University Range")

    settings_service.seed_defaults(db_session)

    db_session.expire_all()
    row = db_session.query(PlatformSetting).filter(
        PlatformSetting.key == "mail_from_name"
    ).one()
    assert row.value == "Example University Range"


def test_seed_defaults_creates_admin_privacy_default(db_session):
    db_session.query(PlatformSetting).filter(
        PlatformSetting.key == "privacy_default_on"
    ).delete()
    db_session.commit()

    settings_service.seed_defaults(db_session)

    db_session.expire_all()
    row = db_session.query(PlatformSetting).filter(
        PlatformSetting.key == "privacy_default_on"
    ).one()
    assert row.value == "true"
    assert row.category == "security"

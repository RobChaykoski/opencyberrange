"""Password-policy regression tests.

The policy must reject the common shortcut of taking a dictionary word and
bolting a number or symbol onto it, not just check character classes.
"""
import pytest
from pydantic import ValidationError

from app.auth import validate_privileged_password
from app.schemas import CreateUserRequest, _password_policy_error


@pytest.mark.parametrize(
    "password",
    [
        "Password1",
        "Password1!",
        "P@ssw0rd!",
        "P@ssw0rd1!",
        "P@ssw0rd2026!",
        "Welcome123!",
        "Qwerty123!",
        "Summer2026!",
        "Admin123!",
        "Iloveyou1!",
        "Changeme1!",
        "Student123!",
    ],
)
def test_common_base_with_number_or_symbol_is_rejected(password):
    error = _password_policy_error(password)
    assert error
    assert "common" in error.lower()


@pytest.mark.parametrize(
    "password",
    [
        "Aaaaaaa1",
        "Abcabc1!",
        "Abcd1234!",
        "Qwer1234!",
        "4321Abcd!",
    ],
)
def test_repeated_and_sequential_patterns_are_rejected(password):
    error = _password_policy_error(password)
    assert error
    assert "repeat" in error.lower() or "sequence" in error.lower()


@pytest.mark.parametrize(
    ("password", "context"),
    [
        ("Alice2026!", {"username": "alice"}),
        ("Smith2026!", {"email": "alice.smith@example.com"}),
        ("Wonderland-Alice-2026!", {"first_name": "Alice"}),
        ("2026-Builder!", {"last_name": "Builder"}),
    ],
)
def test_account_context_words_are_rejected(password, context):
    error = _password_policy_error(password, **context)
    assert error
    assert "username" in error.lower()


def test_account_context_does_not_overmatch_inside_a_word():
    # "rob" is inside "Correct" but must not reject an unrelated passphrase.
    assert _password_policy_error(
        "Correct#Horse7Battery",
        username="rob",
        email="rob@example.com",
    ) is None


@pytest.mark.parametrize(
    "password",
    [
        "Correct#Horse7Battery",
        "Purple-Otter-Coffee-42",
        "Tr0ub4dor3-Correct",
        "Kestrel!Mango!Quartz-91",
    ],
)
def test_strong_passphrases_are_accepted(password):
    assert _password_policy_error(password) is None


@pytest.mark.parametrize(
    ("password", "message"),
    [
        ("short1A", "at least 8"),
        ("alllowercase1", "uppercase"),
        ("ALLUPPERCASE1", "lowercase"),
        ("NoNumberHere!", "number"),
    ],
)
def test_existing_complexity_checks_still_apply(password, message):
    error = _password_policy_error(password)
    assert error
    assert message in error.lower()


def test_create_user_schema_rejects_username_in_password():
    with pytest.raises(ValidationError) as exc:
        CreateUserRequest(
            username="alice",
            email="alice@example.com",
            first_name="Alice",
            password="Alice2026!",
        )
    assert "username, email, or name" in str(exc.value)


def test_privileged_policy_rejects_long_common_password():
    error = validate_privileged_password("Password123456!")
    assert error
    assert "common" in error.lower()


def test_privileged_policy_accepts_long_strong_password():
    assert validate_privileged_password("Kestrel!Mango!Quartz-91") is None

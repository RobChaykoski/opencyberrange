"""
Pydantic schemas for request/response validation
"""

from pydantic import BaseModel, model_validator
from typing import Optional, ClassVar
import re
import unicodedata

from app.services.input_safety import normalize_text


# Common bases are matched after the password is normalised (case-folded,
# reduced to letters/digits, and stripped of trailing counters/years). That
# catches the real-world habit of taking a dictionary word and appending a
# digit or symbol: Password1, P@ssw0rd!, Summer2026!.
_COMMON_PASSWORD_BASES = frozenset({
    "password", "passw0rd", "passwd", "pass", "qwerty", "qwertyuiop",
    "azerty", "abc123", "123456", "1234567", "12345678", "123456789",
    "1234567890", "111111", "000000", "letmein", "welcome", "admin",
    "administrator", "root", "toor", "login", "iloveyou", "monkey",
    "dragon", "master", "sunshine", "princess", "football", "baseball",
    "shadow", "superman", "batman", "trustno1", "starwars", "whatever",
    "freedom", "hello", "secret", "changeme", "changeit", "default",
    "guest", "user", "test", "testing", "student", "teacher", "instructor",
    "school", "college", "university", "cyber", "security", "range",
    "rangebox", "opencyberrange", "ocr", "kali", "ubuntu", "remnux",
    "linux", "windows", "summer", "winter", "spring", "autumn", "fall",
    "january", "february", "march", "april", "may", "june", "july",
    "august", "september", "october", "november", "december", "monday",
    "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday",
    "northwind", "swocts", "academy", "course", "lab", "flag",
})

# Fold common substitutions back to the base word. Symbols are folded first,
# then trailing counters/years are removed, then digit substitutions. That order
# turns P@ssw0rd1! into "password" without turning Password1 into
# "passwordl".
_SYMBOL_TRANSLATION = str.maketrans({
    "@": "a", "$": "s", "+": "t",
})
_DIGIT_TRANSLATION = str.maketrans({
    "0": "o", "1": "l", "3": "e", "4": "a", "5": "s", "7": "t", "8": "b",
})

_SEQUENCES = (
    "0123456789",
    "abcdefghijklmnopqrstuvwxyz",
    "qwertyuiop",
    "asdfghjkl",
    "zxcvbnm",
)


def _password_normalise(value: str) -> str:
    """Case-fold and reduce a password to letters/digits for comparison."""
    return "".join(
        ch for ch in unicodedata.normalize("NFKC", value).casefold()
        if ch.isalnum()
    )


def _password_base(value: str) -> str:
    """Return the dictionary-like base of a password, ignoring suffixes."""
    folded = unicodedata.normalize("NFKC", value).casefold()
    folded = folded.translate(_SYMBOL_TRANSLATION)
    normalised = "".join(ch for ch in folded if ch.isalnum())
    without_counter = normalised.rstrip("0123456789")
    translated = (without_counter or normalised).translate(_DIGIT_TRANSLATION)
    return translated


def _has_sequential_run(value: str, run_length: int = 4) -> bool:
    """True when value contains an obvious ascending/descending/keyboard run."""
    if len(value) < run_length:
        return False
    for start in range(len(value) - run_length + 1):
        chunk = value[start:start + run_length]
        if not chunk.isalnum():
            continue
        deltas = [
            ord(chunk[i + 1]) - ord(chunk[i])
            for i in range(len(chunk) - 1)
        ]
        if all(delta == 1 for delta in deltas) or all(delta == -1 for delta in deltas):
            return True
    for sequence in _SEQUENCES:
        for start in range(len(sequence) - run_length + 1):
            if sequence[start:start + run_length] in value:
                return True
    return False


def _is_repeated_pattern(value: str) -> bool:
    if len(value) >= 4 and len(set(value)) == 1:
        return True
    return re.fullmatch(r"(.+?)\1+", value) is not None


def _password_context_tokens(
    username: Optional[str] = None,
    email: Optional[str] = None,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
) -> set[str]:
    tokens = set()
    for value in (username, first_name, last_name):
        if value:
            tokens.add(unicodedata.normalize("NFKC", str(value)).casefold())
    if email:
        local = str(email).split("@", 1)[0].casefold()
        tokens.add(local)
        tokens.update(part for part in re.split(r"[^a-z0-9]+", local) if part)
    # One- and two-character names would reject far too much ordinary text.
    return {token for token in tokens if len(token) >= 3}


def _contains_context_token(value: str, token: str) -> bool:
    """Match a username/name only as a word or with a numeric/symbol suffix."""
    escaped = re.escape(token)
    return bool(
        re.fullmatch(rf"{escaped}[0-9\W_]*", value)
        or re.fullmatch(rf"[0-9\W_]*{escaped}", value)
        or re.search(rf"(?<![a-z0-9]){escaped}(?![a-z0-9])", value)
    )


def _password_policy_error(
    v: str,
    *,
    username: Optional[str] = None,
    email: Optional[str] = None,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
) -> Optional[str]:
    """Return the first password-policy error, or None when the password is ok.

    Uses Unicode-aware character classes so kanji, full-width letters, and
    other scripts are not silently treated as symbols. The policy is about
    categories, not the Latin alphabet: an uppercase letter, lowercase letter,
    and digit may come from any script.

    Complexity alone is not enough: this also rejects common bases with a
    number/symbol bolted on, account-specific words, repeated patterns, and
    simple sequences.
    """
    if len(v) < 8:
        return "Password must be at least 8 characters"
    if len(v) > 128:
        return "Password must be at most 128 characters"
    if any(unicodedata.category(ch) == "Cc" for ch in v):
        return "Password must not contain control characters"
    if not any(ch.isupper() for ch in v):
        return "Password must contain at least one uppercase letter"
    if not any(ch.islower() for ch in v):
        return "Password must contain at least one lowercase letter"
    if not any(ch.isdigit() for ch in v):
        return "Password must contain at least one number"

    normalised = _password_normalise(v)
    base = _password_base(v)
    if base in _COMMON_PASSWORD_BASES:
        return (
            "Password is too common. Choose a longer phrase that is not a "
            "common word, name, or simple pattern."
        )

    lower_value = unicodedata.normalize("NFKC", v).casefold()
    for token in _password_context_tokens(
        username=username,
        email=email,
        first_name=first_name,
        last_name=last_name,
    ):
        if _contains_context_token(lower_value, token):
            return "Password must not contain your username, email, or name."

    if _is_repeated_pattern(normalised.rstrip("0123456789")):
        return "Password must not repeat the same character or pattern."
    if _has_sequential_run(normalised):
        return (
            "Password must not contain a simple sequence such as 1234, "
            "abcd, or qwerty."
        )
    return None


def _validate_password(
    v: str,
    *,
    username: Optional[str] = None,
    email: Optional[str] = None,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
) -> str:
    """Shared password check used by all schemas that accept passwords."""
    error = _password_policy_error(
        v,
        username=username,
        email=email,
        first_name=first_name,
        last_name=last_name,
    )
    if error:
        raise ValueError(error)
    return v


class SafeTextModel(BaseModel):
    """Base model that normalises declared human-text fields.

    Subclasses list fields in ``__safe_text_fields__`` with ``"short"`` for
    single-line values and ``"multiline"`` for descriptions and comments.
    Passwords, slugs, flags, code/YAML, and other machine values are not listed
    and are therefore never normalised here.
    """

    __safe_text_fields__: ClassVar[dict[str, str]] = {}

    @model_validator(mode="before")
    @classmethod
    def _normalize_safe_text_fields(cls, data):
        fields = cls.__safe_text_fields__
        if not fields or not isinstance(data, dict):
            return data
        cleaned = dict(data)
        for name, mode in fields.items():
            if name not in cleaned:
                continue
            value = cleaned[name]
            if value is None or not isinstance(value, str):
                continue
            cleaned[name] = normalize_text(
                value,
                field=name.replace("_", " "),
                allow_newlines=(mode == "multiline"),
            )
        return cleaned


# ==================== User Schemas ====================

"""Flag feedback should point at common typing mistakes without leaking answers."""
import hashlib

from app.routers.curriculum import _wrong_flag_hint


def _hash(flag: str) -> str:
    return hashlib.sha256(flag.encode()).hexdigest()


def test_lookalike_digit_hint_for_leetspeak_miss():
    expected = _hash("OCR{test_1nj3ct10n_syst3m_l34k}")
    hint = _wrong_flag_hint("OCR{test_1nj3cti0n_syst3m_l34k}", expected)

    assert "look-alike" in hint.lower()
    assert "1 for" in hint


def test_lookalike_hint_when_public_is_typed_with_a_letter():
    expected = _hash("OCR{test_s3cr3ts_4r3_publ1c}")
    hint = _wrong_flag_hint("OCR{test_s3cr3ts_4r3_public}", expected)

    assert "look-alike" in hint.lower()


def test_case_hint_is_kept():
    expected = _hash("OCR{Mixed_Case}")
    hint = _wrong_flag_hint("ocr{mixed_case}", expected)

    assert "case" in hint.lower()


def test_wrapper_hint_is_kept():
    expected = _hash("OCR{wrapped}")
    hint = _wrong_flag_hint("wrapped", expected)

    assert "OCR{...}" in hint


def test_unrelated_flag_gets_generic_format_hint():
    expected = _hash("OCR{real_flag}")
    hint = _wrong_flag_hint("whoami", expected)

    assert "case-sensitive" in hint.lower()
    assert "real_flag" not in hint

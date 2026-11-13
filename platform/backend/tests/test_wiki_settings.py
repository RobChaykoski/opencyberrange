"""Wiki origin settings must reject values that cannot be a safe origin."""

import pytest
from fastapi import HTTPException

from app.routers.settings import _validate_wiki_setting


def test_wiki_origin_accepts_https_origin():
    _validate_wiki_setting("wiki_origin", "https://wiki.example.edu")
    _validate_wiki_setting("wiki_origin", "")


@pytest.mark.parametrize(
    "value",
    [
        "http://wiki.example.edu",
        "https://wiki.example.edu/path",
        "https://wiki.example.edu?x=1",
        "javascript:alert(1)",
        "wiki.example.edu",
    ],
)
def test_wiki_origin_rejects_non_origins(value):
    with pytest.raises(HTTPException):
        _validate_wiki_setting("wiki_origin", value)


def test_wiki_frame_ancestor_accepts_multiple_origins():
    _validate_wiki_setting(
        "wiki_frame_ancestor",
        "https://app.example.edu https://range.example.edu",
    )


def test_wiki_cookie_domain_requires_parent_domain():
    _validate_wiki_setting("wiki_cookie_domain", ".example.edu")
    _validate_wiki_setting("wiki_cookie_domain", "example.edu")
    for value in ("example", ".example", "https://example.edu", ".example..edu"):
        with pytest.raises(HTTPException):
            _validate_wiki_setting("wiki_cookie_domain", value)

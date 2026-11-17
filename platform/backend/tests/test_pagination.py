"""Pagination helpers used by admin list endpoints."""

from app.pagination import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE, normalize_page, page_meta


def test_page_values_are_clamped():
    assert normalize_page(None, None) == (1, DEFAULT_PAGE_SIZE)
    assert normalize_page(0, 0) == (1, DEFAULT_PAGE_SIZE)
    assert normalize_page(2, 1000) == (2, MAX_PAGE_SIZE)


def test_page_meta_reports_total_and_pages():
    assert page_meta(0, 1, 50) == {
        "total": 0,
        "page": 1,
        "per_page": 50,
        "pages": 1,
    }
    assert page_meta(101, 2, 50) == {
        "total": 101,
        "page": 2,
        "per_page": 50,
        "pages": 3,
    }

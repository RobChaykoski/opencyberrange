"""Small, shared pagination helpers for admin list endpoints."""

from __future__ import annotations

from typing import Any

DEFAULT_PAGE_SIZE = 50
MAX_PAGE_SIZE = 200


def normalize_page(page: int | None, per_page: int | None) -> tuple[int, int]:
    """Clamp a requested page and page size to safe values."""
    page = max(1, int(page or 1))
    per_page = int(per_page or DEFAULT_PAGE_SIZE)
    return page, min(max(1, per_page), MAX_PAGE_SIZE)


def paginate(query, page: int, per_page: int) -> tuple[list[Any], int]:
    """Return one page of ORM rows and the unpaginated total."""
    total = query.count()
    rows = query.offset((page - 1) * per_page).limit(per_page).all()
    return rows, total


def page_meta(total: int, page: int, per_page: int) -> dict[str, int]:
    return {
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": max(1, (total + per_page - 1) // per_page),
    }

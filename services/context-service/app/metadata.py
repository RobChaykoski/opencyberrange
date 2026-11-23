from __future__ import annotations

import json
import time
from pathlib import Path

import httpx

from .models import ResourceMetadata


class MetadataUnavailable(Exception):
    pass


class FixtureMetadataStore:
    """Local policy view for development and tests.

    The fixture is intentionally small. In integration, the same contract is
    populated by the OpenMetadata adapter and refreshed into this cache.
    """

    def __init__(self, path: str | Path, cache_seconds: int = 60):
        self.path = Path(path)
        self.cache_seconds = cache_seconds
        self._loaded_at = 0.0
        self._rows: dict[str, ResourceMetadata] = {}

    def _load(self) -> None:
        if self._rows and (time.monotonic() - self._loaded_at) < self.cache_seconds:
            return
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise MetadataUnavailable(f"could not read metadata fixture: {exc}") from exc
        rows = {}
        for key, value in raw.items():
            rows[key] = ResourceMetadata(id=key, **value)
        self._rows = rows
        self._loaded_at = time.monotonic()

    def lookup(self, resource_id: str) -> ResourceMetadata | None:
        self._load()
        return self._rows.get(resource_id)


class HttpMetadataStore:
    """Adapter for a normalized metadata lookup endpoint.

    The production adapter maps OpenMetadata entities, tags, glossary terms, and
    custom properties into the contract returned by this endpoint. Keeping the
    adapter behind a narrow HTTP contract prevents the policy path from
    depending on OpenMetadata's API shape.
    """

    def __init__(self, lookup_url: str, cache_seconds: int = 60):
        self.lookup_url = lookup_url.rstrip("/")
        self.cache_seconds = cache_seconds
        self._cache: dict[str, tuple[float, ResourceMetadata]] = {}

    def lookup(self, resource_id: str) -> ResourceMetadata | None:
        now = time.monotonic()
        cached = self._cache.get(resource_id)
        if cached and now - cached[0] < self.cache_seconds:
            return cached[1]
        try:
            response = httpx.get(
                f"{self.lookup_url}/{resource_id}",
                timeout=3.0,
                headers={"Accept": "application/json"},
            )
            if response.status_code == 404:
                return None
            response.raise_for_status()
            metadata = ResourceMetadata(**response.json())
        except (httpx.HTTPError, ValueError) as exc:
            raise MetadataUnavailable(str(exc)) from exc
        self._cache[resource_id] = (now, metadata)
        return metadata


def build_metadata_store(mode: str, fixture_path: str, lookup_url: str):
    if mode == "http":
        if not lookup_url:
            raise ValueError("METADATA_LOOKUP_URL is required when METADATA_MODE=http")
        return HttpMetadataStore(lookup_url)
    return FixtureMetadataStore(fixture_path)

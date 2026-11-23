"""Read-only competency coverage for the admin quality view.

The source of truth is the generated contract file. This service does not score
learners; it reports whether the curriculum model is ready for Release 6.
"""

from __future__ import annotations

from collections import defaultdict

from app.services.competency_contract import load_contracts
from app.services.rubrics import load_rubrics


def coverage_summary() -> dict:
    contracts = load_contracts().get("labs") or {}
    tracks: dict[str, dict[str, int]] = defaultdict(lambda: {"total": 0, "reviewed": 0, "pending": 0})
    pending: list[dict] = []

    for slug, contract in sorted(contracts.items()):
        if not isinstance(contract, dict):
            continue
        track = str(contract.get("track") or "Unknown")
        status = str(contract.get("review_status") or "unknown")
        reviewed = status == "reviewed"
        tracks[track]["total"] += 1
        tracks[track]["reviewed" if reviewed else "pending"] += 1
        if not reviewed:
            pending.append(
                {
                    "slug": slug,
                    "track": track,
                    "difficulty": contract.get("difficulty"),
                    "status": status,
                }
            )

    total = len(contracts)
    reviewed = sum(1 for contract in contracts.values() if isinstance(contract, dict) and contract.get("review_status") == "reviewed")
    return {
        "total": total,
        "reviewed": reviewed,
        "pending": total - reviewed,
        "coverage_percent": round((reviewed / total) * 100, 1) if total else 0.0,
        "rubrics": len(load_rubrics()),
        "tracks": [
            {"track": track, **counts}
            for track, counts in sorted(tracks.items(), key=lambda item: (-item[1]["pending"], item[0]))
        ],
        "pending_labs": pending[:25],
    }

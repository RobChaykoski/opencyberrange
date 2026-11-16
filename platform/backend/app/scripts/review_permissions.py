"""Release review for the permission catalog.

Run in CI or before a release:

    python -m app.scripts.review_permissions --check

The check is intentionally about dangerous drift, not a fixed count. It fails
when private data becomes role-grantable, when high-sensitivity permissions are
missing review metadata, or when faculty roles accumulate learner-private
signals such as career affinity or recommendations.
"""

from __future__ import annotations

import argparse
import sys

from app.security.permissions import (
    BREAK_GLASS_PERMISSIONS,
    HIGH_SENSITIVITY_PERMISSIONS,
    PERMISSION_META,
    ROLE_PERMISSIONS,
    SENSITIVE_PRIVATE_PERMISSIONS,
    validate_catalog,
)

_FACULTY_ROLES = ("instructor", "teaching_assistant", "mentor")
_PRIVATE_SIGNALS = {
    "career_affinity.view.self",
    "recommendation.view.self",
    "coach.transcript.view",
    "dna.view.private",
    "gps.view.private",
}


def issues() -> list[str]:
    found = list(validate_catalog())
    for role in _FACULTY_ROLES:
        leaked = ROLE_PERMISSIONS.get(role, frozenset()) & _PRIVATE_SIGNALS
        if leaked:
            found.append(f"{role} has private learner signals: {sorted(leaked)}")
    for permission in sorted(HIGH_SENSITIVITY_PERMISSIONS):
        meta = PERMISSION_META.get(permission, {})
        if not meta.get("category"):
            found.append(f"{permission} has no review category")
        if not meta.get("sensitivity"):
            found.append(f"{permission} has no sensitivity label")
    for permission in sorted(BREAK_GLASS_PERMISSIONS):
        meta = PERMISSION_META.get(permission, {})
        if meta.get("sensitivity") not in {"high", "critical", "restricted"}:
            found.append(
                f"{permission} is break-glass eligible but only "
                f"{meta.get('sensitivity')} sensitivity"
            )
    for permission in sorted(SENSITIVE_PRIVATE_PERMISSIONS):
        granted = [
            role
            for role, permissions in ROLE_PERMISSIONS.items()
            if permission in permissions
        ]
        if granted:
            found.append(f"{permission} is granted to {granted}")
    return found


def summarize() -> None:
    print(f"Permissions: {len(PERMISSION_META)}")
    print(f"Roles: {len(ROLE_PERMISSIONS)}")
    print(f"High/critical/restricted: {len(HIGH_SENSITIVITY_PERMISSIONS)}")
    print(f"Break-glass eligible: {len(BREAK_GLASS_PERMISSIONS)}")
    print("Private (must stay ungranted):")
    for permission in sorted(SENSITIVE_PRIVATE_PERMISSIONS):
        print(f"  - {permission}")
    print("\nRole grants:")
    for role, permissions in sorted(ROLE_PERMISSIONS.items()):
        print(f"  {role:<20} {len(permissions):>3} permissions")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail on review issues")
    args = parser.parse_args(argv)
    summarize()
    found = issues()
    if found:
        print("\nReview issues:", file=sys.stderr)
        for item in found:
            print(f"  - {item}", file=sys.stderr)
        return 1 if args.check else 0
    print("\nNo permission-review issues found.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

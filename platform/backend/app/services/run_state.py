"""Service-owned directory for cross-worker ephemeral state.

The backend runs as the unprivileged ``ocr`` user and owns ``/app``. ``/tmp`` is
shared and world-writable, so predictable state files there are a local
tampering surface. Use one directory with a tight mode instead.
"""

from __future__ import annotations

import os
import tempfile


def _default_run_state_dir() -> str:
    # The container owns /app. Local development and tests do not, so use a
    # private directory under the OS temp root there.
    if os.path.isdir("/app"):
        return "/app/run-state"
    return os.path.join(tempfile.gettempdir(), "ocr-run-state")


DEFAULT_RUN_STATE_DIR = _default_run_state_dir()


def run_state_dir() -> str:
    """Return the shared state directory, creating it when missing."""
    path = os.environ.get("OCR_RUN_STATE_DIR", DEFAULT_RUN_STATE_DIR)
    os.makedirs(path, mode=0o750, exist_ok=True)
    try:
        os.chmod(path, 0o750)
    except OSError:
        # A read-only or pre-provisioned mount may already be correct.
        pass
    return path

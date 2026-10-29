"""
Cross-platform advisory file locking.

Production runs in a Linux container, where ``fcntl.flock`` provides the
worker-safe locking the admin impersonation store relies on. ``fcntl`` does
not exist on Windows, so local development and the test suite need an
equivalent: Windows uses ``msvcrt.locking`` over the same one-byte region.

Use :func:`open_locked` as a context manager; the lock is released and the
file closed when the block exits.
"""

import os
from contextlib import contextmanager

if os.name == "nt":  # pragma: no cover - exercised only on Windows
    import msvcrt

    def _lock(handle, exclusive):
        # msvcrt locks a byte range starting at the current position. Seek to
        # the start so every caller contends for the same byte.
        handle.seek(0)
        mode = msvcrt.LK_LOCK if exclusive else msvcrt.LK_RLCK
        msvcrt.locking(handle.fileno(), mode, 1)

    def _unlock(handle):
        handle.seek(0)
        msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)

else:
    import fcntl

    def _lock(handle, exclusive):
        fcntl.flock(handle, fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH)

    def _unlock(handle):
        fcntl.flock(handle, fcntl.LOCK_UN)


@contextmanager
def open_locked(path, mode="r", encoding="utf-8"):
    """Open ``path`` and hold an advisory lock until the block exits.

    Modes that write (``w``, ``a``, ``+``) take an exclusive lock; read-only
    modes take a shared lock. Raises the same ``OSError`` subclasses as
    :func:`open` when the file is missing or unreadable.
    """
    exclusive = any(flag in mode for flag in "wa+")
    handle = open(path, mode, encoding=encoding)
    try:
        _lock(handle, exclusive)
        try:
            yield handle
        finally:
            _unlock(handle)
    finally:
        handle.close()

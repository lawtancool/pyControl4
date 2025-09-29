"""Compatibility utilities for differing dependency versions.

Currently provides an async-timeout wrapper that works with both
async-timeout >= 4.x (async context manager) and < 4.x (sync context manager).
"""

import typing as _t

try:
    import async_timeout as _async_timeout
except Exception:  # pragma: no cover
    _async_timeout = None  # type: ignore


class _AsyncifyContextManager:
    def __init__(self, sync_cm: _t.Any) -> None:
        self._sync_cm = sync_cm

    async def __aenter__(self) -> _t.Any:
        return self._sync_cm.__enter__()

    async def __aexit__(self, exc_type, exc, tb) -> _t.Optional[bool]:
        return self._sync_cm.__exit__(exc_type, exc, tb)


def timeout_ctx(seconds: float):
    """Return an async-compatible context manager for timeouts.

    Works whether async-timeout returns an async or sync context manager.
    """
    if _async_timeout is None:
        raise RuntimeError("async_timeout is required for timeout_ctx")

    cm = _async_timeout.timeout(seconds)
    # If async context manager is supported, use directly
    if hasattr(cm, "__aenter__") and hasattr(cm, "__aexit__"):
        return cm
    # Fallback: wrap sync context manager for async `async with` usage
    return _AsyncifyContextManager(cm)

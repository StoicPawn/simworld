from __future__ import annotations

from contextvars import ContextVar


_counters: ContextVar[dict[str, int] | None] = ContextVar("simworld_id_counters", default=None)


def reset_id_scope() -> None:
    """Start a fresh deterministic identifier scope for one simulation run.

    The scope is context-local, so independent execution contexts do not share counters.
    IDs encode creation order only; they must never be used as a source of randomness or
    historical significance.
    """
    _counters.set({})


def next_id(prefix: str) -> str:
    counters = _counters.get()
    if counters is None:
        counters = {}
        _counters.set(counters)
    value = counters.get(prefix, 0) + 1
    counters[prefix] = value
    return f"{prefix}_{value:010d}"

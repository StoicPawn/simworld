from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from random import Random


def derive_seed(root_seed: int, *parts: object) -> int:
    """Derive a stable integer seed from a root seed and semantic coordinates.

    The derivation is independent of Python's process-randomized hash() and of call
    order. The same root seed + semantic path therefore produces the same stream on
    every compatible run.
    """

    payload = "\x1f".join((str(root_seed), *(str(part) for part in parts))).encode("utf-8")
    digest = hashlib.blake2b(payload, digest_size=16, person=b"simworld-rng-v1").digest()
    return int.from_bytes(digest, "big", signed=False)


@dataclass(slots=True)
class RandomStreams:
    """Registry of independent deterministic pseudo-random streams.

    Domains should use semantic keys such as ("demography", settlement_id) or
    ("encounter", actor_id, year). Adding a new unrelated stream must not advance or
    perturb an existing stream.
    """

    root_seed: int
    _streams: dict[tuple[str, ...], Random] = field(default_factory=dict)

    def seed_for(self, *parts: object) -> int:
        if not parts:
            raise ValueError("at least one stream coordinate is required")
        return derive_seed(self.root_seed, *parts)

    def stream(self, *parts: object) -> Random:
        if not parts:
            raise ValueError("at least one stream coordinate is required")
        key = tuple(str(part) for part in parts)
        stream = self._streams.get(key)
        if stream is None:
            stream = Random(self.seed_for(*key))
            self._streams[key] = stream
        return stream

    def ephemeral(self, *parts: object) -> Random:
        """Return a fresh reproducible stream without retaining mutable state."""
        return Random(self.seed_for(*parts))

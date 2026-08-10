from __future__ import annotations

from dataclasses import dataclass
from hashlib import blake2b
import json
from random import Random
from typing import Any

import numpy as np


def _canonical_key(value: Any) -> Any:
    """Return a JSON-stable representation for semantic RNG keys.

    Python's built-in hash() is intentionally never used because it is process-randomized.
    Only simple semantic values should be used as RNG keys. Containers are normalized
    recursively; mappings are sorted by their string key representation.
    """

    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, bytes):
        return {"bytes": value.hex()}
    if isinstance(value, tuple):
        return {"tuple": [_canonical_key(item) for item in value]}
    if isinstance(value, list):
        return {"list": [_canonical_key(item) for item in value]}
    if isinstance(value, dict):
        return {
            "dict": [
                [_canonical_key(key), _canonical_key(value[key])]
                for key in sorted(value, key=lambda item: str(item))
            ]
        }
    raise TypeError(f"unsupported deterministic RNG key type: {type(value).__name__}")


@dataclass(frozen=True, slots=True)
class SeedStreams:
    """Derive independent deterministic pseudo-random streams from semantic keys.

    A stream is a pure function of the root seed, namespace and keys. Drawing from one
    stream therefore cannot advance or perturb another. Callers should include the
    causal scope needed for uniqueness, e.g. ("demography", year) or
    ("residence", household_id, year, "move").
    """

    root_seed: int
    namespace: str = "simworld-v1"

    def seed(self, *keys: Any) -> int:
        payload = json.dumps(
            {
                "root_seed": int(self.root_seed),
                "namespace": self.namespace,
                "keys": [_canonical_key(key) for key in keys],
            },
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
        digest = blake2b(payload, digest_size=16, person=b"simworld-rng-v1").digest()
        return int.from_bytes(digest, "big", signed=False)

    def python(self, *keys: Any) -> Random:
        return Random(self.seed(*keys))

    def numpy(self, *keys: Any) -> np.random.Generator:
        return np.random.default_rng(self.seed(*keys))

    def scoped(self, *prefix: Any) -> "ScopedSeedStreams":
        return ScopedSeedStreams(self, tuple(prefix))


@dataclass(frozen=True, slots=True)
class ScopedSeedStreams:
    parent: SeedStreams
    prefix: tuple[Any, ...]

    def seed(self, *keys: Any) -> int:
        return self.parent.seed(*self.prefix, *keys)

    def python(self, *keys: Any) -> Random:
        return self.parent.python(*self.prefix, *keys)

    def numpy(self, *keys: Any) -> np.random.Generator:
        return self.parent.numpy(*self.prefix, *keys)

from __future__ import annotations

from dataclasses import fields, is_dataclass
from enum import Enum
from hashlib import sha256
import json
import math
from typing import Any, Mapping


def _stable_key(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def normalize(value: Any) -> Any:
    """Convert supported values to a deterministic JSON-compatible tree."""
    if isinstance(value, Enum):
        return normalize(value.value)
    if is_dataclass(value) and not isinstance(value, type):
        return {field.name: normalize(getattr(value, field.name)) for field in fields(value)}
    if isinstance(value, Mapping):
        out: dict[str, Any] = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise TypeError("canonical mappings require string keys")
            out[key] = normalize(item)
        return {key: out[key] for key in sorted(out)}
    if isinstance(value, (set, frozenset)):
        items = [normalize(item) for item in value]
        return sorted(items, key=_stable_key)
    if isinstance(value, (tuple, list)):
        return [normalize(item) for item in value]
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("non-finite floats are not canonicalizable")
        return 0.0 if value == 0.0 else value
    if value is None or isinstance(value, (str, int, bool)):
        return value
    raise TypeError(f"unsupported canonical value: {type(value)!r}")


def canonical_json(value: Any) -> str:
    return json.dumps(
        normalize(value),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def content_digest(value: Any) -> str:
    payload = canonical_json(value).encode("utf-8")
    return "sha256:" + sha256(payload).hexdigest()


def verify_digest(value: Any, expected: str) -> None:
    actual = content_digest(value)
    if actual != expected:
        raise ValueError(f"content digest mismatch: expected {expected}, got {actual}")

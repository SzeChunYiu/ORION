from __future__ import annotations

import hashlib
import json
from dataclasses import fields, is_dataclass
from enum import Enum
from typing import Any, Mapping

HASH_EXCLUDED_FIELDS = frozenset(
    {"content_hash", "snapshot_hash", "authority_reasons", "final_state"}
)


def jsonable(value: Any, *, exclude: frozenset[str] = frozenset()) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, Mapping):
        return {str(key): jsonable(item, exclude=exclude) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [jsonable(item, exclude=exclude) for item in value]
    if is_dataclass(value):
        payload = {}
        for field in fields(value):
            if field.name in exclude:
                continue
            payload[field.name] = jsonable(getattr(value, field.name), exclude=exclude)
        return payload
    raise TypeError(f"cannot canonicalize {type(value)!r}")


def canonical_json(value: Any, *, exclude: frozenset[str] = frozenset()) -> str:
    return json.dumps(jsonable(value, exclude=exclude), sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def sha256_canonical(value: Any, *, exclude: frozenset[str] | None = None) -> str:
    skipped = HASH_EXCLUDED_FIELDS if exclude is None else exclude
    return hashlib.sha256(canonical_json(value, exclude=skipped).encode("utf-8")).hexdigest()

"""Shared result type for the local theorem suite."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any


@dataclass(frozen=True)
class TheoremResult:
    theorem_id: str
    statement: str
    status: str
    assumptions: tuple[str, ...]
    detail: str
    witness: dict[str, Any] | None = None

    @property
    def passed(self) -> bool:
        return self.status == "LOCAL_PROVED"

    def as_json(self) -> dict[str, Any]:
        def jsonable(value: Any) -> Any:
            if isinstance(value, Enum):
                return value.value
            if isinstance(value, tuple):
                return [jsonable(item) for item in value]
            if isinstance(value, list):
                return [jsonable(item) for item in value]
            if isinstance(value, dict):
                return {str(key): jsonable(item) for key, item in value.items()}
            return value

        return jsonable(asdict(self))

"""Shared deterministic report machinery for the P6--P8 hostile review."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable, Mapping


class Status(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    COUNTEREXAMPLE_CONFIRMED = "COUNTEREXAMPLE_CONFIRMED"


@dataclass(frozen=True)
class ReviewResult:
    paper: str
    finding: str
    status: Status
    cases: int
    summary: str
    reviewed_snapshot: str
    witness: Mapping[str, Any] | None = None
    scope: str = "bounded deterministic hostile review"

    def as_json(self) -> dict[str, Any]:
        raw = asdict(self)
        raw["status"] = self.status.value
        return raw


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def write_report(
    path: Path,
    results: Iterable[ReviewResult],
    metadata: Mapping[str, Any],
) -> str:
    payload = {
        "schema": "orion.p6_p8.hostile_formal_review.v1",
        "metadata": dict(metadata),
        "results": [result.as_json() for result in results],
    }
    payload["report_sha256"] = sha256_text(canonical_json(payload))
    rendered = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(rendered, encoding="utf-8")
    return sha256_text(rendered)

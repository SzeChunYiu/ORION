#!/usr/bin/env python3
"""Derive the R7A acquisition frame before any source or candidate outcome."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import runpy
from typing import Any

BASE_QUERY_FRAME = Path(__file__).resolve().parents[1] / "gpt_r7" / "query_frame.py"
PRIMARY_SAMPLE_SEED = 2026082302
REPLICATION_SAMPLE_SEED = 2026082303


def canonical_json(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def build_query_frame() -> dict[str, Any]:
    base = runpy.run_path(str(BASE_QUERY_FRAME))["build_query_frame"]()
    frame = dict(base)
    frame["schema_version"] = "orion.p1.r7a.acquisition-query-frame.v2"
    frame["successor_of_query_frame"] = "orion.p1.r7.acquisition-query-frame.v1"
    frame["reason_for_amendment"] = "double every family-domain source-pair quota after outcome-blind nine-comparator max-T power audit"
    sampling = dict(frame["sampling"])
    sampling["primary_seed"] = PRIMARY_SAMPLE_SEED
    sampling["replication_seed"] = REPLICATION_SAMPLE_SEED
    sampling["pairs_per_family_domain_cell"] = 12
    frame["sampling"] = sampling
    return frame


def frame_digest(frame: dict[str, Any] | None = None) -> str:
    payload = frame if frame is not None else build_query_frame()
    return "sha256:" + hashlib.sha256(canonical_json(payload)).hexdigest()


def main() -> None:
    frame = build_query_frame()
    print(json.dumps({"query_frame_digest": frame_digest(frame), **frame}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

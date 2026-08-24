#!/usr/bin/env python3
"""Enumerate the frozen two-world stage-composition countermodel."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


LANE = Path(__file__).resolve().parent


def canonical_sha(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest()


def main() -> None:
    worlds = [
        {
            "world": "omega_0",
            "observation": "same_local_artifacts",
            "local_gates": {"source": 1, "rights": 1, "parser": 1, "entrypoint": 1},
            "stage_1_artifact": "fixed_A",
            "stage_2_artifact": "fixed_B",
            "unobserved_cross_stage_identity": 0,
            "global_query": 0,
        },
        {
            "world": "omega_1",
            "observation": "same_local_artifacts",
            "local_gates": {"source": 1, "rights": 1, "parser": 1, "entrypoint": 1},
            "stage_1_artifact": "fixed_A",
            "stage_2_artifact": "fixed_B",
            "unobserved_cross_stage_identity": 1,
            "global_query": 1,
        },
    ]
    observed_signatures = {
        (
            w["observation"],
            tuple(sorted(w["local_gates"].items())),
            w["stage_1_artifact"],
            w["stage_2_artifact"],
        )
        for w in worlds
    }
    identified_set = sorted({w["global_query"] for w in worlds})
    result = {
        "schema_version": "orion.p3.authority-composition.countermodel.v7t",
        "world_count": len(worlds),
        "observed_signature_count": len(observed_signatures),
        "all_local_gates_true": all(all(w["local_gates"].values()) for w in worlds),
        "all_local_artifacts_fixed": len(observed_signatures) == 1,
        "global_query_identified_set": identified_set,
        "global_query_point_identified": len(identified_set) == 1,
        "terminal": "LOCAL_STAGE_READINESS_PASS__GLOBAL_COMPOSITION_QUERY_NOT_IDENTIFIED",
        "worlds": worlds,
    }
    result["canonical_content_sha256"] = canonical_sha(result)
    (LANE / "FINITE_COUNTERMODEL_RESULT_V7T.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n"
    )


if __name__ == "__main__":
    main()

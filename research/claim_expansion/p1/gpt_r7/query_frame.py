#!/usr/bin/env python3
"""Deterministically enumerate the pre-outcome R7 acquisition query frame."""

from __future__ import annotations

import hashlib
import json
from typing import Any

YEAR_MIN = 2019
YEAR_MAX = 2025
MAX_RANK_PER_QUERY = 100
PRIMARY_SAMPLE_SEED = 20260822
REPLICATION_SAMPLE_SEED = 20260823

DOMAINS = {
    "BIOMEDICAL_CLINICAL": "biomedical clinical",
    "EARTH_ENVIRONMENTAL": "earth environmental science",
    "COMPUTATIONAL_SCIENTIFIC_SOFTWARE": "computational scientific software",
    "PHYSICAL_ENGINEERING": "physical engineering experiment",
}

FAMILIES = {
    "LATENT_OBJECTIVE": "proxy objective versus protected target outcome",
    "CONTRADICTORY_OBJECTIVES": "conflicting objectives tradeoff versus stale evidence",
    "WRONG_MEASUREMENT": "uncalibrated measurement versus validated reference measurement",
    "WRONG_REPRESENTATION": "raw representation versus transformed representation",
    "WRONG_PROBLEM_BOUNDARY": "restricted system boundary versus expanded boundary",
    "IMPLEMENTATION_OR_HARNESS_FAILURE": "software implementation error versus corrected implementation",
    "EVIDENCE_SCARCITY": "limited evidence versus additional observations",
    "NO_REFORMULATION_CONTROL": "same scientific objective lower-level repair versus objective change",
}

PAIR_QUERY_VARIANTS = (
    "primary comparative study",
    "controlled comparison",
    "replication benchmark",
    "official artifact case study",
)

UNRESOLVED_NOTIONS = (
    "competing models observationally indistinguishable",
    "nonidentifiable parameters multiple mechanisms",
    "equifinality under available observations",
    "insufficient evidence distinguish scientific hypotheses",
)

UNRESOLVED_VARIANTS = (
    "primary study",
    "controlled analysis",
)


def canonical_json(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def build_query_frame() -> dict[str, Any]:
    pair_queries: list[dict[str, Any]] = []
    for family, family_terms in FAMILIES.items():
        for domain, domain_terms in DOMAINS.items():
            for index, variant in enumerate(PAIR_QUERY_VARIANTS, start=1):
                pair_queries.append(
                    {
                        "query_id": f"PAIR-{family}-{domain}-Q{index}",
                        "family": family,
                        "domain": domain,
                        "query": f"{domain_terms} {family_terms} {variant}",
                    }
                )

    unresolved_queries: list[dict[str, Any]] = []
    for domain, domain_terms in DOMAINS.items():
        query_index = 0
        for notion in UNRESOLVED_NOTIONS:
            for variant in UNRESOLVED_VARIANTS:
                query_index += 1
                unresolved_queries.append(
                    {
                        "query_id": f"UNRESOLVED-{domain}-Q{query_index}",
                        "domain": domain,
                        "query": f"{domain_terms} {notion} {variant}",
                    }
                )

    frame: dict[str, Any] = {
        "schema_version": "orion.p1.r7.acquisition-query-frame.v1",
        "publication_year_min": YEAR_MIN,
        "publication_year_max": YEAR_MAX,
        "max_rank_per_query": MAX_RANK_PER_QUERY,
        "source_priority": [
            "primary_paper",
            "publisher_record",
            "official_artifact_repository",
        ],
        "pair_queries": pair_queries,
        "unresolved_queries": unresolved_queries,
        "sampling": {
            "eligible_pool_is_frozen_before_sampling": True,
            "primary_seed": PRIMARY_SAMPLE_SEED,
            "replication_seed": REPLICATION_SAMPLE_SEED,
            "pairs_per_family_domain_cell": 6,
            "unresolved_per_domain": 16,
            "replication_excludes_every_primary_and_p1_x_r1_r6_source_family": True,
            "outcome_access_during_search_eligibility_or_sampling": False,
        },
    }
    return frame


def frame_digest(frame: dict[str, Any] | None = None) -> str:
    payload = frame if frame is not None else build_query_frame()
    return "sha256:" + hashlib.sha256(canonical_json(payload)).hexdigest()


def main() -> int:
    frame = build_query_frame()
    print(json.dumps({"query_frame_digest": frame_digest(frame), **frame}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


#!/usr/bin/env python3
"""Count outcome-free metadata signals for P4 natural-pair mechanisms.

Keyword and version-history hits are discovery signals only.  They do not
establish linked objects, reuse rights, natural-pair eligibility, claim
resolution, or adjudicated terminals.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def signal_text(row: dict[str, Any]) -> str:
    parts = (
        row.get("title", ""),
        row.get("abstract", ""),
        row.get("comments", ""),
        row.get("journal_ref", ""),
    )
    return " ".join(str(value or "") for value in parts).lower()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--pool", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    protocol = json.loads(args.protocol.read_text(encoding="utf-8"))
    rows = [json.loads(line) for line in args.pool.read_text(encoding="utf-8").splitlines() if line]
    lexicon = protocol["feasibility_signal_lexicon"]
    domains = [item["domain_id"] for item in protocol["domains"]]
    mechanisms = [item["mechanism_id"] for item in protocol["natural_pair_mechanisms"]]
    counts = {domain: Counter() for domain in domains}
    combination_counts: Counter[tuple[str, ...]] = Counter()

    for row in rows:
        domain = row["domain_id"]
        text = signal_text(row)
        hits = ["M1_ABSTRACT_TO_FULLTEXT"]
        if len(row.get("version_history") or []) > 1:
            hits.append("M2_EARLIER_TO_LATER_VERSION")
        for mechanism, terms in lexicon.items():
            if mechanism == "M2_EARLIER_TO_LATER_VERSION":
                continue
            if any(term.lower() in text for term in terms):
                hits.append(mechanism)
        for mechanism in hits:
            counts[domain][mechanism] += 1
        combination_counts[tuple(sorted(hits))] += 1

    minimum = int(protocol["panel_allocation"]["minimum_screening_reserve_per_cell"])
    primary = int(protocol["panel_allocation"]["primary_clusters_per_cell"])
    replication = int(protocol["panel_allocation"]["source_disjoint_replication_clusters_per_cell"])
    required_signal_count = minimum + primary + replication
    table = {
        domain: {
            mechanism: {
                "metadata_signal_rows": int(counts[domain][mechanism]),
                "at_least_nominal_48_candidate_signal_rows": counts[domain][mechanism] >= required_signal_count,
                "eligible_natural_pairs": None,
                "rights_bound_pairs": None,
            }
            for mechanism in mechanisms
        }
        for domain in domains
    }
    result = {
        "schema_version": "orion.p4.natural-pair-metadata-feasibility.v1",
        "date": "2026-08-23",
        "authority": "OUTCOME_FREE_METADATA_SIGNAL_CENSUS_ONLY__NOT_CASE_ELIGIBILITY_OR_SCIENTIFIC_RESULT",
        "protocol_sha256": file_sha256(args.protocol),
        "pool_sha256": file_sha256(args.pool),
        "pool_rows": len(rows),
        "domains": domains,
        "mechanisms": mechanisms,
        "nominal_rows_needed_per_cell": required_signal_count,
        "signal_table": table,
        "lowest_signal_count_by_mechanism": {
            mechanism: min(counts[domain][mechanism] for domain in domains)
            for mechanism in mechanisms
        },
        "highest_signal_count_by_mechanism": {
            mechanism: max(counts[domain][mechanism] for domain in domains)
            for mechanism in mechanisms
        },
        "signal_overlap_patterns": [
            {"mechanisms": list(pattern), "rows": count}
            for pattern, count in sorted(
                combination_counts.items(), key=lambda item: (-item[1], item[0])
            )
        ],
        "binding_findings": {
            "M1_ABSTRACT_TO_FULLTEXT": "all rows expose provider-native abstract and exact article-version identities; full-text bytes and eligibility remain unbound",
            "M2_EARLIER_TO_LATER_VERSION": "version-history signals exist, but earlier-version licence and content bytes are not inherited from the latest version",
            "M3_TO_M8": "keyword signals do not prove a linked object, identity match, separate reuse permission, natural information-state pair, or resolving evidence",
        },
        "current_terminal": "P4_NATURAL_PAIR_METADATA_SIGNALS_COUNTED__32_CELL_ELIGIBILITY_CANNOT_CHECK",
    }
    args.out.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Fail-closed consistency checks; this is not an empirical or test-suite run."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def check_manifest(path: Path, base: Path) -> int:
    count = 0
    for line in path.read_text().splitlines():
        expected, relative = line.split("  ", 1)
        observed = hashlib.sha256((base / relative).read_bytes()).hexdigest()
        assert observed == expected, (relative, expected, observed)
        count += 1
    return count


def main() -> None:
    online = json.loads((HERE / "ONLINE_EVIDENCE_RECEIPTS.json").read_text())
    bindings = json.loads((HERE / "PUBLIC_SOURCE_BINDINGS.json").read_text())
    sampling = json.loads((HERE / "MINIMAL_SAMPLING_MANIFESTS.json").read_text())
    receipt = json.loads((HERE / "AUDIT_RECEIPT.json").read_text())

    assert [row["paper_id"] for row in bindings["paper_bindings"]] == ["P1", "P2", "P3", "P5"]
    assert bindings["excluded_papers"] == ["P4"]
    assert bindings["dataset_rows_accessed"] == 0
    assert online["dataset_rows_accessed"] == 0
    assert sampling["dataset_rows_accessed"] == 0
    assert sampling["label_values_accessed"] == 0
    assert not online["protected_outcome_bytes_accessed"]
    assert not sampling["protected_outcome_bytes_accessed"]
    assert all(not row["paper_level_blocker_closed"] for row in bindings["paper_bindings"])
    assert bindings["closure_summary"]["paper_level_empirical_blockers_closed"] == 0
    assert bindings["closure_summary"]["paper_level_empirical_blockers_still_open"] == 4
    assert len(sampling["manifests"]) == 4
    assert all(not manifest["row_ids_materialized"] for manifest in sampling["manifests"])
    assert all(item["http_status"] in {200, 404} for item in online["http_receipts"])
    missing_urls = {
        item["url"] for item in online["http_receipts"] if item["http_status"] == 404
    }
    assert missing_urls == {
        "https://raw.githubusercontent.com/allenai/PeerRead/9bb37751781a900cee9e74ec3105997732c8e8e5/LICENSE",
        "https://raw.githubusercontent.com/soarsmu/BugsInPy/11c5f1eea954a42132cfd06bf257766a7963e0fd/LICENSE",
    }
    assert receipt["papers_audited"] == ["P1", "P2", "P3", "P5"]
    assert receipt["papers_excluded"] == ["P4"]
    assert receipt["data_candidate_mapping_count"] == 14
    assert receipt["comparator_candidate_count"] == 4
    assert receipt["dataset_rows_accessed"] == 0
    assert receipt["label_values_accessed"] == 0
    assert not receipt["protected_outcome_bytes_accessed"]
    assert not receipt["empirical_execution_run"]
    assert not receipt["pytest_run"]
    assert not receipt["ci_run"]
    assert not receipt["manuscripts_modified_by_lane"]

    source_count = check_manifest(HERE / "SOURCE_REQUIREMENTS_SHA256SUMS", ROOT)
    artifact_count = check_manifest(HERE / "SHA256SUMS", HERE)
    print(
        json.dumps(
            {
                "status": "PASS",
                "papers": receipt["papers_audited"],
                "data_candidate_mappings": receipt["data_candidate_mapping_count"],
                "comparator_candidates": receipt["comparator_candidate_count"],
                "official_http_receipts": receipt["official_http_receipt_count"],
                "sampling_manifests": receipt["sampling_manifest_count"],
                "dataset_rows_accessed": 0,
                "protected_outcome_bytes_accessed": False,
                "paper_level_empirical_blockers_closed": 0,
                "source_manifest_entries": source_count,
                "artifact_manifest_entries": artifact_count,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()

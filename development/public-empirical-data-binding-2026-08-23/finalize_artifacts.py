#!/usr/bin/env python3
"""Create local-source and artifact integrity manifests plus audit receipt."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE_PATHS = [
    "research/claim_expansion/p1/gpt_r7/R7A_MAXT_POWER_AMENDMENT_V2.json",
    "papers/orion-12-open-world-scientific-discovery/protocol/P2_TASK_WORLD_SUCCESSOR_V2.json",
    "papers/orion-13-global-knowledge-portrait/protocol/P3_PARTIAL_IDENTIFICATION_SUCCESSOR_V1.json",
    "papers/orion-15-self-orion/protocol/P5_WIDE_REVISION_LEVEL_SUCCESSOR_V1.json",
]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    online = json.loads((HERE / "ONLINE_EVIDENCE_RECEIPTS.json").read_text())
    bindings = json.loads((HERE / "PUBLIC_SOURCE_BINDINGS.json").read_text())
    sampling = json.loads((HERE / "MINIMAL_SAMPLING_MANIFESTS.json").read_text())

    (HERE / "SOURCE_REQUIREMENTS_SHA256SUMS").write_text(
        "".join(f"{digest(ROOT / rel)}  {rel}\n" for rel in SOURCE_PATHS)
    )

    statuses = Counter(item["http_status"] for item in online["http_receipts"])
    paper_rows = bindings["paper_bindings"]
    receipt = {
        "schema_version": "orion.public-empirical-data-binding.audit-receipt.v1",
        "captured_at_utc": online["captured_at_utc"],
        "authority": "PUBLIC_METADATA_DATASET_CARD_LICENCE_AND_FILE_IDENTITY_PREFLIGHT_ONLY",
        "papers_audited": [row["paper_id"] for row in paper_rows],
        "papers_excluded": bindings["excluded_papers"],
        "data_candidate_mapping_count": sum(len(row["candidate_bindings"]) for row in paper_rows),
        "comparator_candidate_count": sum("comparator_candidate" in row for row in paper_rows),
        "official_http_receipt_count": len(online["http_receipts"]),
        "official_http_status_counts": {str(key): value for key, value in sorted(statuses.items())},
        "github_repository_count": len(online["github"]),
        "hugging_face_dataset_count": len(online["hugging_face"]),
        "zenodo_record_count": len(online["zenodo"]),
        "dataverse_version_count": 1,
        "sampling_manifest_count": len(sampling["manifests"]),
        "selected_file_or_revision_identity_count": sum(
            len(manifest["selected_objects"]) for manifest in sampling["manifests"]
        ),
        "dataset_rows_accessed": online["dataset_rows_accessed"],
        "label_values_accessed": sampling["label_values_accessed"],
        "protected_outcome_bytes_accessed": online["protected_outcome_bytes_accessed"],
        "empirical_execution_run": False,
        "pytest_run": False,
        "ci_run": False,
        "manuscripts_modified_by_lane": False,
        "paper_level_empirical_blockers_closed": bindings["closure_summary"][
            "paper_level_empirical_blockers_closed"
        ],
        "paper_level_empirical_blockers_still_open": bindings["closure_summary"][
            "paper_level_empirical_blockers_still_open"
        ],
        "scientific_terminal": bindings["closure_summary"]["scientific_terminal"],
    }
    (HERE / "AUDIT_RECEIPT.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    )

    entries = []
    for path in sorted(
        item for item in HERE.iterdir() if item.is_file() and item.name != "SHA256SUMS"
    ):
        entries.append(f"{digest(path)}  {path.name}\n")
    (HERE / "SHA256SUMS").write_text("".join(entries))


if __name__ == "__main__":
    main()

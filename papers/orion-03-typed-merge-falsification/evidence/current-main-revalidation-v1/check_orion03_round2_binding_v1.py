#!/usr/bin/env python3
"""Current-main, toolchain-free revalidation of ORION-03 Round-2 evidence.

This checker does not rerun OpenSSL. It verifies the committed evidence remains
byte-bound and internally/independently consistent at the authority level the
publication freeze actually claims.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

EXPECTED_TASKS = 1962
EXPECTED_HYBRIDS = 46
EXPECTED_BOUND_DIGESTS = 269


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / ".git").exists() or (parent / "papers").is_dir() and (parent / "packages").is_dir():
            return parent
    raise SystemExit("cannot locate ORION repository root")


def verify_source_binding(r2: Path) -> dict[str, int]:
    binding = load(r2 / "SOURCE_BINDING_V2.json")
    third_party = r2 / "third_party" / "openssl-3.6.4-testcerts"
    groups = (
        ("vendored_files", third_party),
        ("vendored_recipe", third_party),
        ("excluded_list", third_party),
        ("frozen_artifacts", r2),
        ("results_artifacts", r2),
    )
    ok = 0
    mismatches = []
    for group, root in groups:
        entries = binding[group]
        for rel, expected in entries.items():
            path = root / rel
            if not path.is_file():
                mismatches.append({"group": group, "path": rel, "error": "MISSING"})
                continue
            actual = sha256(path)
            if actual != expected:
                mismatches.append(
                    {"group": group, "path": rel, "expected": expected, "actual": actual}
                )
            else:
                ok += 1
    assert not mismatches, mismatches[:10]
    assert ok == EXPECTED_BOUND_DIGESTS, (ok, EXPECTED_BOUND_DIGESTS)
    return {"verified": ok, "mismatches": 0}


def verify_duplicate_receipts(r2: Path) -> dict[str, bool]:
    names = ("ROUND2_RESULTS_V2", "INDEPENDENT_REPRO_R2", "COST_ROUND2_V2")
    result = {}
    for name in names:
        a = r2 / f"{name}.json"
        b = r2 / f"{name}.run2.json"
        result[name] = a.read_bytes() == b.read_bytes()
    assert all(result.values()), result
    return result


def verify_round2_invariants(r2: Path) -> dict:
    result = load(r2 / "ROUND2_RESULTS_V2.json")
    independent = load(r2 / "INDEPENDENT_REPRO_R2.json")

    assert result["total_tasks"] == EXPECTED_TASKS
    assert result["engine_hybrids_total"] == EXPECTED_HYBRIDS
    assert result["obstruction_detection"]["engine_hybrids"] == EXPECTED_HYBRIDS
    assert result["obstruction_detection"]["m5_flagged"] == EXPECTED_HYBRIDS
    assert result["obstruction_detection"]["false_flags_on_single_origin_complete"] == 0
    assert result["obstruction_detection"]["precision"] == 1.0
    assert result["obstruction_detection"]["recall"] == 1.0
    assert result["terminal"] == "D_R2_REAL_AUTHORITY_PROMOTION_ERROR_PREVENTED"

    family_tasks = sum(family["tasks"] for family in result["families"].values())
    family_hybrids = sum(family["engine_hybrids"] for family in result["families"].values())
    assert family_tasks == EXPECTED_TASKS
    assert family_hybrids == EXPECTED_HYBRIDS

    assert independent["task_counts"]["total"] == EXPECTED_TASKS
    assert independent["hybrid_tasks"]["count"] == EXPECTED_HYBRIDS
    assert len(independent["hybrid_tasks"]["task_ids"]) == EXPECTED_HYBRIDS
    assert len(set(independent["hybrid_tasks"]["task_ids"])) == EXPECTED_HYBRIDS
    assert independent["methods"]["overall"]["M1_flat_union"]["unsafe_merges"] == EXPECTED_HYBRIDS
    assert independent["methods"]["overall"]["M5_typed_origin_witness"]["unsafe_merges"] == 0
    assert independent["methods"]["overall"]["M5_typed_origin_witness"]["allows"] == independent["authorization_totals"]["parent_authorized"]
    assert independent["external_peer_review_claimed"] is False
    assert independent["journal_authority"] is False
    assert independent["submission_authority"] is False
    assert "excludes C1-C6 and structural localization" in independent["scope"]

    return {
        "tasks": EXPECTED_TASKS,
        "hybrids": EXPECTED_HYBRIDS,
        "terminal": result["terminal"],
        "independent_scope": independent["scope"],
    }


def verify_publication_boundary(root: Path) -> dict[str, bool]:
    paper = root / "papers" / "orion-03-typed-merge-falsification"
    freeze = (paper / "PUBLICATION_FREEZE_ADDENDUM_V1.md").read_text(encoding="utf-8")
    manuscript = (paper / "MANUSCRIPT_V2.md").read_text(encoding="utf-8")
    checks = {
        "freeze_status_preserved": "CURRENT_EARNED_CEILING_FROZEN__EXTERNAL_POLICY_VALIDATION_SUCCESSOR_ONLY" in freeze,
        "external_validation_not_claimed": "external-domain validation" in freeze,
        "analytic_empirical_boundary_present": "empirical" in manuscript.lower() and "analytic" in manuscript.lower(),
    }
    assert all(checks.values()), checks
    return checks


def main() -> int:
    root = repo_root()
    r2 = root / "papers" / "orion-03-typed-merge-falsification" / "evidence" / "round2-x509-truststore"
    out = {
        "status": "PASS",
        "source_binding": verify_source_binding(r2),
        "duplicate_receipts": verify_duplicate_receipts(r2),
        "round2": verify_round2_invariants(r2),
        "publication_boundary": verify_publication_boundary(root),
        "authority": "BOUNDED_R2_EVIDENCE_REMAINS_BOUND__NO_NATIVE_ENGINE_RERUN",
        "scientific_authority_delta": "NONE",
    }
    print(json.dumps(out, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

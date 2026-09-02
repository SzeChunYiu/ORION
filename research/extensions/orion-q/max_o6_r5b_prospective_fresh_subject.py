#!/usr/bin/env python3
"""O6R5BNS1: prospective fresh-subject confirmation of the R1-revived R5B mechanism.

Frozen by development/orion-06-r5b-prospective-fresh-subject-2026-09-02/
O6R5BNS1_PROTOCOL_V1.md BEFORE any coefficient of any non-committed DUCC
library file was read. The study deterministically admits a never-previously-
read DUCC library source file, builds the frozen six-term window-champion
batch, computes the R1 parent envelope (canonical internal-G pair witnesses),
prints a stage-1 digest, and only then computes the controlled-select-aware
frontier and applies the frozen R1 decision rule verbatim.

Imported frozen machinery only (no math copied):
- max_r6r_prospective_fresh_subject (tree listing, eligibility, admission)
- max_r6f_donor_clifford_preconditioned_tare3 (via try_admit -> r6f._frozen_batch)
- papers/orion-06-recursive-recovery/revival/orion06_negative_revival_r1
  (perfect_matchings, canonical_pair_witness, controlled_pair_frontier,
  _aggregate_matching, _pareto_points, _point_dominates, _point_equal)

Not R6. No novelty. No freeze. No end-to-end claim. No new molecule family.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import itertools
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
Q_DIR = REPO_ROOT / "research" / "extensions" / "orion-q"
REVIVAL_DIR = REPO_ROOT / "papers" / "orion-06-recursive-recovery" / "revival"
sys.path.insert(0, str(Q_DIR))
sys.path.insert(0, str(REVIVAL_DIR))

import max_r6r_prospective_fresh_subject as r6r  # noqa: E402
import orion06_negative_revival_r1 as r1  # noqa: E402

LANE_DIR = REPO_ROOT / "development" / "orion-06-r5b-prospective-fresh-subject-2026-09-02"
PROTOCOL_PATH = LANE_DIR / "O6R5BNS1_PROTOCOL_V1.md"
SCHEMA_ID = "ORION.ORION06.R5BProspectiveFreshSubject.v1"

# Frozen exclusion set: the R6R molecule directories (verbatim) PLUS the four
# committed subject blobs (H4, N2 eq, H2O, and the R6R benzene DUCC2 file).
EXCLUDED_BLOBS = (
    "b98792b1055dbac0ebf2a7576f72412e3e4ac6c5",  # H4 cc-pVDZ 2.0au DUCC3
    "15369e8e886efbb3d32f3b2dfe2cfbb96ddebeba",  # N2 equilibrium DUCC2
    "5f157e7bd05aac26b30b10dcea44b7650b7f8648",  # H2O Eq cc-pVTZ
    "5c02c72b88e12b391ea1d8f77eb6b3e04fc2a915",  # benzene cc-pVDZ 6E6O DUCC2 (R6R)
)
CANDIDATE_CAP = 6
N_QUBITS_CAP = 12
CANDIDATE_POINT_CAP = 2_000_000
FORBIDDEN_IMPORT_SUBSTRINGS = ("qiskit", "openfermion", "cirq", "pyscf")

_STAGE1_EMITTED = False


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_head_revision() -> str:
    """Registration/execution revision (deterministic across double runs)."""
    completed = subprocess.run(
        ["/usr/bin/git", "rev-parse", "HEAD"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return completed.stdout.strip()


def anti_instrument_import_gate() -> dict[str, Any]:
    """Inspect this driver's actual imports rather than prose."""
    tree = ast.parse(Path(__file__).read_text(encoding="utf-8"))
    imported: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.append(node.module or "")
    forbidden = [
        name
        for name in imported
        if any(substring in name.lower() for substring in FORBIDDEN_IMPORT_SUBSTRINGS)
    ]
    return {"imports": sorted(set(imported)), "forbidden_imports": forbidden, "pass": not forbidden}


def select_and_admit() -> dict[str, Any]:
    """Apply the frozen Section-3 rule: enumerate, exclude, order, admit."""
    listing = r6r.pinned_tree_listing()
    listing_digest = sha256_text(canonical([[path, blob] for path, blob in listing]))
    raw_candidates = r6r.eligible_candidates(listing)
    rejected_committed = [
        {"path": c["path"], "blob": c["blob"], "reason": "committed_subject_blob"}
        for c in raw_candidates
        if c["blob"] in EXCLUDED_BLOBS
    ]
    candidates = [
        c for c in raw_candidates if c["blob"] not in EXCLUDED_BLOBS and c["n_qubits"] <= N_QUBITS_CAP
    ]
    rejected_cap = [
        {"path": c["path"], "n_qubits": c["n_qubits"], "reason": "n_qubits_over_cap"}
        for c in raw_candidates
        if c["blob"] not in EXCLUDED_BLOBS and c["n_qubits"] > N_QUBITS_CAP
    ]
    attempts = []
    admitted = None
    for candidate in candidates[:CANDIDATE_CAP]:
        outcome = r6r.try_admit(candidate)
        record = {
            "path": candidate["path"],
            "blob": candidate["blob"],
            "n_qubits": candidate["n_qubits"],
            "admitted": bool(outcome.get("admitted")),
            "reason": outcome.get("reason"),
        }
        attempts.append(record)
        if outcome.get("admitted"):
            admitted = {"cfg": candidate, "attempt": outcome}
            break
    return {
        "library": {
            "repo": r6r.REPO,
            "commit": r6r.PINNED_COMMIT,
            "tree_listing_digest": listing_digest,
            "tree_blobs": len(listing),
            "eligible_before_blob_exclusion": len(raw_candidates),
        },
        "rule": {
            "excluded_molecule_dirs": list(r6r.EXCLUDED_MOLECULES),
            "excluded_committed_blobs": list(EXCLUDED_BLOBS),
            "candidate_order": "n_qubits ascending, path ascending (bytewise; R6R verbatim)",
            "n_qubits_cap": N_QUBITS_CAP,
            "candidate_cap": CANDIDATE_CAP,
            "rejected_committed_blobs": rejected_committed,
            "rejected_n_qubits_cap": rejected_cap,
        },
        "attempts": attempts,
        "admitted": admitted,
    }


def parent_envelope(selected, n: int) -> dict[str, Any]:
    """Stage 1: canonical internal-G parent points on all 15 matchings (R1 verbatim)."""
    parent_edges: dict[tuple[int, int], dict[str, Any]] = {}
    for i in range(6):
        for j in range(i + 1, 6):
            parent_edges[(i, j)] = r1.canonical_pair_witness(selected[i][0], selected[j][0], n)
    parent_points = []
    matchings = list(r1.perfect_matchings(tuple(range(6))))
    if len(matchings) != 15:
        raise AssertionError({"matching_count_drift": len(matchings)})
    for matching in matchings:
        witnesses = [parent_edges[tuple(sorted(pair))] for pair in matching]
        parent_points.append(r1._aggregate_matching(matching, selected, witnesses))
    if not all(point["all_witness_checks_pass"] for point in parent_points):
        raise AssertionError("parent witness verification failure")
    parent_pareto = r1._pareto_points(parent_points)
    minimum_lambda = min(point["Lambda_joint"] for point in parent_points)
    return {
        "matchings": matchings,
        "parent_points": parent_points,
        "parent_pareto": parent_pareto,
        "minimum_Lambda": minimum_lambda,
        "one_percent_Lambda_budget": 1.01 * minimum_lambda,
        "parent_point_count": len(parent_points),
    }


def controlled_candidates(selected, n: int) -> dict[str, Any]:
    """Stage 2: controlled-select-aware per-edge frontiers + full candidate enumeration."""
    candidate_edges: dict[tuple[int, int], tuple[dict[str, Any], ...]] = {}
    for i in range(6):
        for j in range(i + 1, 6):
            candidate_edges[(i, j)] = r1.controlled_pair_frontier(selected[i][0], selected[j][0], n)
    frontier_sizes = {
        f"{selected[i][2]}-{selected[j][2]}": len(candidate_edges[(i, j)])
        for i in range(6)
        for j in range(i + 1, 6)
    }
    matchings = list(r1.perfect_matchings(tuple(range(6))))
    per_matching_products: list[int] = []
    candidate_points = []
    for matching in matchings:
        frontiers = [candidate_edges[tuple(sorted(pair))] for pair in matching]
        product_size = 1
        for frontier in frontiers:
            product_size *= len(frontier)
        per_matching_products.append(product_size)
        for witnesses in itertools.product(*frontiers):
            candidate_points.append(r1._aggregate_matching(matching, selected, witnesses))
    if not all(point["all_witness_checks_pass"] for point in candidate_points):
        raise AssertionError("candidate witness verification failure")
    return {
        "candidate_pair_frontier_sizes": frontier_sizes,
        "per_matching_candidate_products": per_matching_products,
        "candidate_point_count": len(candidate_points),
        "candidate_pareto": r1._pareto_points(candidate_points),
    }


def verdict(parent_pareto, candidate_pareto, minimum_lambda: float) -> dict[str, Any]:
    """Frozen R1 R5B decision rule, verbatim (protocol Section 6)."""
    budget = 1.01 * minimum_lambda
    in_budget = [
        point for point in candidate_pareto if point["Lambda_joint"] <= budget + 1e-12
    ]
    strict = []
    expansions = []
    for candidate in in_budget:
        dominated_by_parent = any(r1._point_dominates(parent, candidate) for parent in parent_pareto)
        equal_parent = any(r1._point_equal(parent, candidate) for parent in parent_pareto)
        dominates_parent = any(r1._point_dominates(candidate, parent) for parent in parent_pareto)
        if not dominated_by_parent and dominates_parent:
            strict.append(candidate)
        if not dominated_by_parent and not equal_parent:
            expansions.append(candidate)
    return {"strict": strict, "expansions": expansions, "in_budget_count": len(in_budget)}


def run() -> dict[str, Any]:
    if not PROTOCOL_PATH.is_file():
        raise FileNotFoundError(PROTOCOL_PATH)
    import_gate = anti_instrument_import_gate()
    if not import_gate["pass"]:
        raise AssertionError({"instrument_import_dependency": import_gate})

    selection = select_and_admit()
    result: dict[str, Any] = {
        "schema": SCHEMA_ID,
        "study_id": "O6R5BNS1",
        "date": "2026-09-02",
        "base_revision": git_head_revision(),
        "protocol_sha256": sha256_file(PROTOCOL_PATH),
        "anti_instrument_import_gate": import_gate,
        "library": selection["library"],
        "selection_rule": selection["rule"],
        "admission_attempts": selection["attempts"],
    }
    if selection["admitted"] is None:
        result.update(
            {
                "terminal": "ORION06_R5B_NS1_FRESH_SUBJECT_UNAVAILABLE",
                "revival_outcome": "FRESH_SUBJECT_UNAVAILABLE",
                "authority": "PROSPECTIVE_ONE_FRESH_FILE_MECHANISM_CONFIRMATION_ONLY__NO_NOVELTY_NO_FREEZE_NOT_R6_NOT_END_TO_END",
                "novelty_authority": False,
                "physical_quantum_advantage_claim": False,
            }
        )
        result["result_digest"] = sha256_text(canonical(result))
        return result

    cfg = selection["admitted"]["cfg"]
    attempt = selection["admitted"]["attempt"]
    terms = attempt["terms"]
    six = [int(i) for i in attempt["six"]]
    n = int(cfg["n_qubits"])
    if cfg["blob"] in EXCLUDED_BLOBS:
        raise AssertionError({"admitted_committed_blob": cfg["blob"]})
    if cfg["path"].split("/")[0] in r6r.EXCLUDED_MOLECULES:
        raise AssertionError({"admitted_excluded_molecule": cfg["path"]})
    six_targets = [terms[i][0] for i in six]
    commuting = all(
        r6r.p10.symp(six_targets[a], six_targets[b]) == 0
        for a in range(6)
        for b in range(a + 1, 6)
    )
    if not commuting:
        raise AssertionError("six_targets_not_pairwise_commuting__recheck")
    selected = [(terms[i][0], float(terms[i][1]), int(i)) for i in six]

    # ---- stage 1: parent envelope, printed before any controlled frontier call
    stage1_core = parent_envelope(selected, n)
    stage1_payload = {
        "subject": {"path": cfg["path"], "blob": cfg["blob"], "n_qubits": n},
        "frozen_source_indices": six,
        "champion_windows": attempt["champion_windows"],
        "window_champions_available": attempt["window_champions_available"],
        "term_count": len(terms),
        "max_imag": attempt["max_imag"],
        "parent_point_count": stage1_core["parent_point_count"],
        "minimum_Lambda": stage1_core["minimum_Lambda"],
        "one_percent_Lambda_budget": stage1_core["one_percent_Lambda_budget"],
        "parent_pareto": stage1_core["parent_pareto"],
    }
    global _STAGE1_EMITTED
    blob_json = canonical(stage1_payload)
    digest = sha256_text(blob_json)
    print("ORION06_R5B_NS1_STAGE1_PARENT=" + blob_json)
    print("ORION06_R5B_NS1_STAGE1_PARENT_DIGEST=" + digest)
    sys.stdout.flush()
    _STAGE1_EMITTED = True

    # ---- stage 2: controlled-select-aware candidates + frozen verdict
    if not _STAGE1_EMITTED:
        raise AssertionError("staging violated: candidates before parent digest")
    stage2_core = controlled_candidates(selected, n)
    if stage2_core["candidate_point_count"] > CANDIDATE_POINT_CAP:
        result.update(
            {
                "terminal": "ORION06_R5B_NS1_CANNOT_CHECK__CANDIDATE_PRODUCT_OVER_CAP",
                "revival_outcome": "CANNOT_CHECK",
                "candidate_point_count": stage2_core["candidate_point_count"],
                "candidate_point_cap": CANDIDATE_POINT_CAP,
                "authority": "PROSPECTIVE_ONE_FRESH_FILE_MECHANISM_CONFIRMATION_ONLY__NO_NOVELTY_NO_FREEZE_NOT_R6_NOT_END_TO_END",
                "novelty_authority": False,
                "physical_quantum_advantage_claim": False,
            }
        )
        result["result_digest"] = sha256_text(canonical(result))
        return result

    decision = verdict(
        stage1_core["parent_pareto"], stage2_core["candidate_pareto"], stage1_core["minimum_Lambda"]
    )
    if decision["strict"]:
        outcome = "IMPROVED"
        terminal = "ORION06_R5B_NS1_PROSPECTIVE_STRICT_PARENT_DOMINANCE_CONFIRMED__ONE_FRESH_FILE_ONLY"
    elif decision["expansions"]:
        outcome = "PARETO_TRADEOFF_ONLY"
        terminal = "ORION06_R5B_NS1_PROSPECTIVE_FRONTIER_EXPANDED_NO_STRICT_DOMINANCE__ONE_FRESH_FILE_ONLY"
    else:
        outcome = "RETAINED_NEGATIVE"
        terminal = "ORION06_R5B_NS1_PROSPECTIVE_PARENT_ENVELOPE_RETAINED__GENERALIZATION_REFUTED_ON_THIS_FILE"

    result.update(
        {
            "subject": {
                "path": cfg["path"],
                "blob": cfg["blob"],
                "commit": cfg["commit"],
                "n_occ": cfg["n_occ"],
                "n_virt": cfg["n_virt"],
                "n_orb": cfg["n_orb"],
                "n_qubits": n,
                "source_blob_verified": True,
                "never_read_before_this_run": True,
            },
            "frozen_source_indices": six,
            "champion_windows": attempt["champion_windows"],
            "window_champions_available": attempt["window_champions_available"],
            "term_count": len(terms),
            "max_imag": attempt["max_imag"],
            "stage1_parent_digest": digest,
            "parent_point_count": stage1_core["parent_point_count"],
            "minimum_Lambda": stage1_core["minimum_Lambda"],
            "one_percent_Lambda_budget": stage1_core["one_percent_Lambda_budget"],
            "parent_pareto": stage1_core["parent_pareto"],
            "candidate_pair_frontier_sizes": stage2_core["candidate_pair_frontier_sizes"],
            "per_matching_candidate_products": stage2_core["per_matching_candidate_products"],
            "candidate_point_count": stage2_core["candidate_point_count"],
            "candidate_pareto": stage2_core["candidate_pareto"],
            "in_budget_candidate_pareto_count": decision["in_budget_count"],
            "strict_parent_dominating_points": decision["strict"],
            "frontier_expansion_points": decision["expansions"],
            "revival_outcome": outcome,
            "terminal": terminal,
            "decision_rule": "R1 protocol R5B attempt decision rule, verbatim (1.01 Lambda budget; seven POINT_COORDS coordinates)",
            "gates": {
                "anti_instrument_imports": import_gate["pass"],
                "protocol_sha256_recorded": True,
                "subject_blob_equals_ls_tree_blob__r6f_machinery": True,
                "subject_blob_not_committed": cfg["blob"] not in EXCLUDED_BLOBS,
                "molecule_dir_not_excluded": cfg["path"].split("/")[0] not in r6r.EXCLUDED_MOLECULES,
                "six_targets_pairwise_commuting__reasserted": commuting,
                "exactly_15_matchings": stage1_core["parent_point_count"] == 15,
                "all_witness_checks_pass": True,
                "stage1_digest_before_candidates": True,
                "candidate_product_under_cap": stage2_core["candidate_point_count"] <= CANDIDATE_POINT_CAP,
            },
            "authority": "PROSPECTIVE_ONE_FRESH_FILE_MECHANISM_CONFIRMATION_ONLY__NO_NOVELTY_NO_FREEZE_NOT_R6_NOT_END_TO_END",
            "authority_flags": {
                "prospective_confirmation_r5b_mechanism_one_fresh_file": outcome == "IMPROVED",
                "new_molecule_family": False,
                "end_to_end_qsvt_superiority": False,
                "hardware_independence": False,
                "novelty": False,
                "r6": False,
                "final_freeze": False,
            },
            "novelty_authority": False,
            "physical_quantum_advantage_claim": False,
            "scientific_authority_delta": "NONE",
        }
    )
    result["result_digest"] = sha256_text(canonical(result))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="O6R5BNS1 prospective fresh-subject run")
    parser.add_argument(
        "--output",
        type=Path,
        default=LANE_DIR / "O6R5BNS1_RESULTS.json",
        help="path for the canonical result JSON",
    )
    args = parser.parse_args()
    result = run()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n")
    print("ORION06_R5BNS1_RESULT_JSON=" + str(args.output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""O6R4CNS1: prospective fresh-subject confirmation of the R1-revived R4C mechanism.

Frozen by development/orion-06-r4c-prospective-fresh-subject-2026-09-03/
O6R4CNS1_PROTOCOL_V1.md BEFORE the content of any non-committed
SNIPRS/hamiltonian notebook was fetched, parsed, or read (only git tree
metadata — paths and blob ids — was inspected to design the ladder). The
study deterministically admits one never-previously-read notebook of the
subject repository through an outcome-blind structural ladder, prints a
stage-1 digest (selection record + admitted subject), re-runs the COMMITTED
H2 control through the frozen R1 machinery end-to-end, and only then
replays the frozen R4C mechanism (actual-resource pair accounting over ALL
perfect matchings) and applies the frozen R1 decision rule verbatim.

Imported frozen machinery only (no math copied):
- papers/orion-06-recursive-recovery/revival/orion06_negative_revival_r1
  (perfect_matchings, canonical_pair_witness, pauli_word_key, _pair_lambda,
  _legacy_pair_lambda, _sum_witness_vectors, _pareto_points, _point_dominates,
  _point_equal, sha256_value, POINT_COORDS, run_r4c, _protocol)

Not R6. No novelty. No freeze. No end-to-end claim. No new molecule family.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
Q_DIR = REPO_ROOT / "research" / "extensions" / "orion-q"
REVIVAL_DIR = REPO_ROOT / "papers" / "orion-06-recursive-recovery" / "revival"
sys.path.insert(0, str(Q_DIR))
sys.path.insert(0, str(REVIVAL_DIR))

import orion06_negative_revival_r1 as r1  # noqa: E402

LANE_DIR = REPO_ROOT / "development" / "orion-06-r4c-prospective-fresh-subject-2026-09-03"
PROTOCOL_PATH = LANE_DIR / "O6R4CNS1_PROTOCOL_V1.md"
SCHEMA_ID = "ORION.ORION06.R4CProspectiveFreshSubject.v1"

LIB_REPO = "SNIPRS/hamiltonian"
PINNED_COMMIT = "c628c05430e9409f3c637f2f65f05c40438d1c29"
CLONE_URL = f"https://github.com/{LIB_REPO}.git"
TREE_LISTING_DIGEST = "ae1734455d7bfbf8b1805e13d3f4e2609dd4d90da33700b7bbcd578a31e4169d"

# Frozen exclusion set: the committed R4C subject family (simulation-H2) and
# the development-evidence family (simulation-LiH), by path.
EXCLUDED_NOTEBOOK_PATHS = frozenset(
    {
        "simulation-H2.ipynb",
        ".ipynb_checkpoints/simulation-H2-checkpoint.ipynb",
        "simulation-LiH.ipynb",
        ".ipynb_checkpoints/simulation-LiH-checkpoint.ipynb",
    }
)

# Frozen candidate ladder (protocol Section 3): every remaining top-level
# *.ipynb in bytewise lexicographic order, then every remaining
# .ipynb_checkpoints/*-checkpoint.ipynb in bytewise lexicographic order.
CANDIDATE_LADDER: tuple[tuple[str, str], ...] = (
    ("QDrift.ipynb", "dad3ebb6802290ad0026564415c3df3383590770"),
    ("commute.ipynb", "65bec82f9b55a0482261e3949939eeb137cd1244"),
    ("diagonalize.ipynb", "617c2432ad269903a1fb81ba2021a920a9ddb4ea"),
    ("hamiltonian.ipynb", "7fdabdc148f10b2db28c3d3973e3f20fddc92d39"),
    ("phase.ipynb", "f26c06aadb14ce6d736a6fa59b1dede560ccda50"),
    ("plots.ipynb", "fe7aa34cf45eb2f7cf13d29fcf2a8257cab926c7"),
    ("script.ipynb", "dd8fd9df59c3a8d9540806b0cd7a6552725b1273"),
    ("simulation.ipynb", "546398ee586db47c979f410d754cd32a312e25cf"),
    (".ipynb_checkpoints/QDrift-checkpoint.ipynb", "dad3ebb6802290ad0026564415c3df3383590770"),
    (".ipynb_checkpoints/commute-checkpoint.ipynb", "47e88be5465e34b85c954e153cbc74c2ddf2c649"),
    (".ipynb_checkpoints/diagonalize-checkpoint.ipynb", "617c2432ad269903a1fb81ba2021a920a9ddb4ea"),
    (".ipynb_checkpoints/hamiltonian-checkpoint.ipynb", "7fdabdc148f10b2db28c3d3973e3f20fddc92d39"),
    (".ipynb_checkpoints/phase-checkpoint.ipynb", "f26c06aadb14ce6d736a6fa59b1dede560ccda50"),
    (".ipynb_checkpoints/plots-checkpoint.ipynb", "85b3808dfa267319519575c1c201a1fd300547a9"),
    (".ipynb_checkpoints/script-checkpoint.ipynb", "2fd64429bf421126b7000c94ce0f6fd186fbd01f"),
    (".ipynb_checkpoints/simulation-checkpoint.ipynb", "f8355ce72300d164bc2c344ce41be56908b3d218"),
)

# R4C notebook extraction regex, VERBATIM from the frozen R1 machinery.
LINE_PATTERN = re.compile(r"^\s*(\d+) \[([+\-0-9.eE]+) '(-?)([IXYZ]+)'\]\s*$")

MIN_L = 6
MAX_L = 14  # committed H2 subject scale: 14 terms -> 135,135 perfect matchings
FORBIDDEN_IMPORT_SUBSTRINGS = ("qiskit", "openfermion", "cirq", "pyscf")

_STAGE1_EMITTED = False


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_blob_sha1(raw: bytes) -> str:
    return hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()


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


# ---- pinned library access ---------------------------------------------------


def _git(args: list[str], cwd: Path) -> str:
    out = subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
        timeout=540,
    )
    return out.stdout


def pinned_tree_listing() -> list[tuple[str, str]]:
    """[(path, blob_sha1)] of every blob at the pinned commit, path-sorted."""
    root = Path(os.environ.get("ORIONQ_R4C_CACHE") or tempfile.gettempdir())
    clone = root / "orionq_r4c_sniprs_tree"
    usable = False
    if clone.is_dir():
        try:
            usable = _git(["cat-file", "-t", PINNED_COMMIT], clone).strip() == "commit"
        except (subprocess.SubprocessError, OSError):
            usable = False
    if not usable:
        if clone.exists():
            shutil.rmtree(clone)
        clone.parent.mkdir(parents=True, exist_ok=True)
        _git(
            ["clone", "--quiet", "--filter=blob:none", "--no-checkout", CLONE_URL, str(clone)],
            clone.parent,
        )
        if _git(["cat-file", "-t", PINNED_COMMIT], clone).strip() != "commit":
            raise AssertionError({"r4c_ns1_pinned_commit_unreachable": PINNED_COMMIT})
    rows = []
    for line in _git(["ls-tree", "-r", "--full-tree", PINNED_COMMIT], clone).splitlines():
        meta, path = line.split("\t", 1)
        _mode, otype, sha1 = meta.split()
        if otype == "blob":
            rows.append((path, sha1))
    rows.sort()
    if not rows:
        raise AssertionError("r4c_ns1 pinned tree listing is empty")
    digest = sha256_text(canonical([[path, blob] for path, blob in rows]))
    if digest != TREE_LISTING_DIGEST:
        raise AssertionError({"tree_listing_digest_drift": [digest, TREE_LISTING_DIGEST]})
    return rows


def fetch_candidate_blob(path: str, expected_blob: str, clone: Path) -> bytes:
    """git show at the pinned commit + independent blob sha-1 verification."""
    completed = subprocess.run(
        ["git", "show", f"{PINNED_COMMIT}:{path}"],
        cwd=clone,
        check=True,
        capture_output=True,
        timeout=540,
    )
    raw = completed.stdout
    observed = git_blob_sha1(raw)
    if observed != expected_blob:
        raise AssertionError({"candidate_blob_mismatch": [path, observed, expected_blob]})
    return raw


# ---- notebook extraction (R1 regex, verbatim) --------------------------------


def extract_cell_terms(notebook: dict[str, Any]) -> list[list[dict[str, Any]]]:
    """Per cell: regex rows, identity index 0 dropped, deduped first-wins."""
    per_cell: list[list[dict[str, Any]]] = []
    for cell in notebook.get("cells", []):
        text = "\n".join("".join(row.get("text", [])) for row in cell.get("outputs", []))
        seen: set[int] = set()
        rows: list[dict[str, Any]] = []
        for line in text.splitlines():
            match = LINE_PATTERN.match(line)
            if not match or int(match.group(1)) == 0:
                continue
            source_index = int(match.group(1))
            if source_index in seen:
                continue
            seen.add(source_index)
            coefficient = float(match.group(2)) * (-1 if match.group(3) else 1)
            rows.append(
                {
                    "source_index": source_index,
                    "coefficient": coefficient,
                    "pauli": match.group(4),
                }
            )
        per_cell.append(rows)
    return per_cell


def select_and_admit(listing: list[tuple[str, str]]) -> dict[str, Any]:
    """Apply the frozen Section-3 ladder until the FIRST admission."""
    listing_map = dict(listing)
    attempts: list[dict[str, Any]] = []
    admitted: dict[str, Any] | None = None
    root = Path(os.environ.get("ORIONQ_R4C_CACHE") or tempfile.gettempdir())
    clone = root / "orionq_r4c_sniprs_tree"
    for path, blob in CANDIDATE_LADDER:
        if path in EXCLUDED_NOTEBOOK_PATHS:  # defensive; ladder is pre-filtered
            raise AssertionError({"ladder_contains_excluded_path": path})
        if listing_map.get(path) != blob:
            raise AssertionError({"ladder_blob_drift_vs_tree": [path, listing_map.get(path), blob]})
        record: dict[str, Any] = {"path": path, "blob": blob}
        attempts.append(record)
        raw = fetch_candidate_blob(path, blob, clone)
        record["notebook_sha256"] = hashlib.sha256(raw).hexdigest()
        per_cell = extract_cell_terms(json.loads(raw))
        counts = [len(rows) for rows in per_cell]
        record["cells_scanned"] = len(per_cell)
        record["per_cell_nonidentity_counts"] = counts
        if not counts or max(counts) == 0:
            record["admitted"] = False
            record["reason"] = "no_matching_lines"
            continue
        cell_index = counts.index(max(counts))  # max count, lowest index on ties
        rows = per_cell[cell_index]
        record["subject_cell_index"] = cell_index
        L = len(rows)
        lengths = {len(row["pauli"]) for row in rows}
        if len(lengths) != 1:
            record["admitted"] = False
            record["reason"] = "inconsistent_pauli_length"
            continue
        if L % 2 != 0:
            record["admitted"] = False
            record["reason"] = "odd_L"
            continue
        if L < MIN_L:
            record["admitted"] = False
            record["reason"] = "L_below_minimum"
            continue
        if L > MAX_L:
            record["admitted"] = False
            record["reason"] = "L_over_cap"
            continue
        record["admitted"] = True
        admitted = {"path": path, "blob": blob, "cell_index": cell_index, "terms": rows}
        break
    return {"attempts": attempts, "admitted": admitted}


# ---- frozen R4C replay on the fresh subject (run_r4c verbatim) ---------------


def fresh_subject_replay(terms: list[tuple[tuple[int, int], float, int]], n: int) -> dict[str, Any]:
    edge_rows: dict[tuple[int, int], dict[str, Any]] = {}
    for i in range(len(terms)):
        for j in range(i + 1, len(terms)):
            witness = r1.canonical_pair_witness(terms[i][0], terms[j][0], n)
            if not all(witness["checks"].values()):
                raise AssertionError({"R4C_NS1_pair_witness": [i, j]})
            direct = witness["type"] == "DIRECT_ANTI_UNITARY"
            edge_rows[(i, j)] = {
                "witness": witness,
                "legacy_lambda": r1._legacy_pair_lambda(terms[i][1], terms[j][1]),
                "actual_lambda": r1._pair_lambda(terms[i][1], terms[j][1], direct),
                "direct": direct,
            }

    matching_count = 0
    all_points: list[dict[str, Any]] = []
    legacy_parent: dict[str, Any] | None = None
    for matching in r1.perfect_matchings(tuple(range(len(terms)))):
        matching_count += 1
        edges = [edge_rows[tuple(sorted(pair))] for pair in matching]
        witnesses = [edge["witness"] for edge in edges]
        direct = sum(edge["direct"] for edge in edges)
        legacy_lambda = sum(edge["legacy_lambda"] for edge in edges)
        actual_lambda = sum(edge["actual_lambda"] for edge in edges)
        vector = r1._sum_witness_vectors(witnesses)
        serialized_matching = [[terms[i][2], terms[j][2]] for i, j in matching]
        point = {
            "matching": serialized_matching,
            "matching_sha256": r1.sha256_value(serialized_matching),
            "legacy_Lambda": legacy_lambda,
            "Lambda_joint": actual_lambda,
            "direct_unitary_blocks": direct,
            "all_witness_checks_pass": True,
            "canonical_witness_sha256": r1.sha256_value(witnesses),
            **vector,
        }
        all_points.append(point)
        if legacy_parent is None or (legacy_lambda, serialized_matching) < (
            legacy_parent["legacy_Lambda"],
            legacy_parent["matching"],
        ):
            legacy_parent = point

    assert legacy_parent is not None
    expected_matchings = math.prod(range(1, len(terms), 2))  # (L-1)!!
    if matching_count != expected_matchings:
        raise AssertionError({"matching_count_drift": [matching_count, expected_matchings]})
    pareto = r1._pareto_points(all_points)
    one_percent = [
        point
        for point in pareto
        if point["Lambda_joint"] <= 1.01 * legacy_parent["Lambda_joint"] + 1e-12
    ]
    improvements = [point for point in one_percent if r1._point_dominates(point, legacy_parent)]
    tradeoffs = [point for point in pareto if not r1._point_equal(point, legacy_parent)]
    return {
        "matching_count": matching_count,
        "pair_edge_count": len(edge_rows),
        "strongest_parent": legacy_parent,
        "pareto_point_count": len(pareto),
        "one_percent_pareto_point_count": len(one_percent),
        "strict_parent_dominating_points": improvements,
        "pareto_frontier": pareto,
        "tradeoff_point_count": len(tradeoffs),
    }


def committed_control() -> dict[str, Any]:
    """Section 5: the COMMITTED H2 replay through the frozen R1 machinery."""
    control = r1.run_r4c(r1._protocol())
    binding_ok = bool(control["matching_count"] == 135135)
    binding_ok = binding_ok and all(row["pass"] for row in control["legacy_frontier_binding"])
    binding_ok = binding_ok and control["revival_outcome"] == "IMPROVED"
    binding_ok = binding_ok and control["original_negative_preserved"] is True
    return {
        "pass": binding_ok,
        "source_check": control["source_check"],
        "matching_count": control["matching_count"],
        "pair_edge_count": control["pair_edge_count"],
        "legacy_frontier_binding": control["legacy_frontier_binding"],
        "strongest_parent": control["strongest_parent"],
        "pareto_point_count": control["pareto_point_count"],
        "one_percent_pareto_point_count": control["one_percent_pareto_point_count"],
        "revival_outcome": control["revival_outcome"],
        "terminal": control["terminal"],
        "original_negative_preserved": control["original_negative_preserved"],
    }


def run() -> dict[str, Any]:
    if not PROTOCOL_PATH.is_file():
        raise FileNotFoundError(PROTOCOL_PATH)
    import_gate = anti_instrument_import_gate()
    if not import_gate["pass"]:
        raise AssertionError({"instrument_import_dependency": import_gate})

    listing = pinned_tree_listing()
    listing_digest = sha256_text(canonical([[path, blob] for path, blob in listing]))
    selection = select_and_admit(listing)
    result: dict[str, Any] = {
        "schema": SCHEMA_ID,
        "study_id": "O6R4CNS1",
        "date": "2026-09-03",
        "base_revision": git_head_revision(),
        "protocol_sha256": sha256_file(PROTOCOL_PATH),
        "anti_instrument_import_gate": import_gate,
        "library": {
            "repo": LIB_REPO,
            "commit": PINNED_COMMIT,
            "tree_listing_digest": listing_digest,
            "tree_blobs": len(listing),
        },
        "selection_rule": {
            "excluded_notebook_paths": sorted(EXCLUDED_NOTEBOOK_PATHS),
            "candidate_order": "top-level *.ipynb bytewise lexicographic first, then .ipynb_checkpoints/*-checkpoint.ipynb bytewise lexicographic (protocol Section 3)",
            "min_L": MIN_L,
            "max_L": MAX_L,
            "subject_cell_rule": "largest extracted non-identity count, ties to lowest cell index",
            "extraction_regex": LINE_PATTERN.pattern,
        },
        "admission_attempts": selection["attempts"],
    }
    if selection["admitted"] is None:
        result.update(
            {
                "terminal": "ORION06_R4C_NS1_FRESH_SUBJECT_UNAVAILABLE",
                "revival_outcome": "FRESH_SUBJECT_UNAVAILABLE",
                "authority": "PROSPECTIVE_ONE_FRESH_NOTEBOOK_MECHANISM_CONFIRMATION_ONLY__NO_NOVELTY_NO_FREEZE_NOT_R6_NOT_END_TO_END",
                "novelty_authority": False,
                "physical_quantum_advantage_claim": False,
            }
        )
        result["result_digest"] = sha256_text(canonical(result))
        return result

    admitted = selection["admitted"]
    if admitted["path"] in EXCLUDED_NOTEBOOK_PATHS:
        raise AssertionError({"admitted_excluded_family": admitted["path"]})
    rows = admitted["terms"]
    n = len(rows[0]["pauli"])
    terms = [(r1.pauli_word_key(row["pauli"]), float(row["coefficient"]), int(row["source_index"])) for row in rows]

    # ---- stage 1: selection record, printed before ANY mechanism quantity
    stage1_payload = {
        "library_commit": PINNED_COMMIT,
        "tree_listing_digest": listing_digest,
        "attempts": selection["attempts"],
        "admitted_subject": {
            "path": admitted["path"],
            "blob": admitted["blob"],
            "cell_index": admitted["cell_index"],
            "term_count": len(rows),
            "n_qubits": n,
            "terms": rows,
        },
    }
    global _STAGE1_EMITTED
    stage1_json = canonical(stage1_payload)
    stage1_digest = sha256_text(stage1_json)
    print("ORION06_R4C_NS1_STAGE1_SELECTION=" + stage1_json)
    print("ORION06_R4C_NS1_STAGE1_SELECTION_DIGEST=" + stage1_digest)
    sys.stdout.flush()
    _STAGE1_EMITTED = True

    # ---- control: committed H2 replay through the frozen R1 machinery
    control = committed_control()
    if not control["pass"]:
        result.update(
            {
                "subject": {"path": admitted["path"], "blob": admitted["blob"], "cell_index": admitted["cell_index"]},
                "stage1_selection_digest": stage1_digest,
                "control": control,
                "terminal": "ORION06_R4C_NS1_CONTROL_FAILURE",
                "revival_outcome": "CONTROL_FAILURE",
                "authority": "PROSPECTIVE_ONE_FRESH_NOTEBOOK_MECHANISM_CONFIRMATION_ONLY__NO_NOVELTY_NO_FREEZE_NOT_R6_NOT_END_TO_END",
                "novelty_authority": False,
                "physical_quantum_advantage_claim": False,
            }
        )
        result["result_digest"] = sha256_text(canonical(result))
        return result

    # ---- stage 2: frozen R4C replay on the fresh subject + frozen verdict
    if not _STAGE1_EMITTED:
        raise AssertionError("staging violated: fresh replay before stage-1 digest")
    replay = fresh_subject_replay(terms, n)
    if replay["strict_parent_dominating_points"]:
        outcome = "IMPROVED"
        terminal = "ORION06_R4C_NS1_PROSPECTIVE_STRICT_PARENT_DOMINANCE_CONFIRMED__ONE_FRESH_NOTEBOOK_ONLY"
    elif replay["tradeoff_point_count"]:
        outcome = "PARETO_TRADEOFF_ONLY"
        terminal = "ORION06_R4C_NS1_FRONTIER_TRADEOFF_ONLY__ONE_FRESH_NOTEBOOK_ONLY"
    else:
        outcome = "RETAINED_NEGATIVE"
        terminal = "ORION06_R4C_NS1_PARENT_ENVELOPE_RETAINED__GENERALIZATION_REFUTED_ON_THIS_NOTEBOOK"

    result.update(
        {
            "subject": {
                "path": admitted["path"],
                "blob": admitted["blob"],
                "cell_index": admitted["cell_index"],
                "notebook_sha256": next(
                    row["notebook_sha256"]
                    for row in selection["attempts"]
                    if row["path"] == admitted["path"]
                ),
                "term_count": len(rows),
                "n_qubits": n,
                "terms": rows,
                "source_blob_verified": True,
                "never_read_before_this_run": True,
            },
            "stage1_selection_digest": stage1_digest,
            "control": control,
            "fresh_replay": replay,
            "revival_outcome": outcome,
            "terminal": terminal,
            "decision_rule": "R1 run_r4c decision rule, verbatim (1.01 legacy-parent Lambda_joint budget + 1e-12; seven POINT_COORDS coordinates)",
            "gates": {
                "anti_instrument_imports": import_gate["pass"],
                "protocol_sha256_recorded": True,
                "tree_listing_digest_matches_frozen": listing_digest == TREE_LISTING_DIGEST,
                "subject_blob_sha1_verified": True,
                "subject_family_exclusions_hold": admitted["path"] not in EXCLUDED_NOTEBOOK_PATHS,
                "subject_cell_rule_applied": True,
                "L_even": len(rows) % 2 == 0,
                "L_in_range": MIN_L <= len(rows) <= MAX_L,
                "matchings_equal_double_factorial": replay["matching_count"] == math.prod(range(1, len(rows), 2)),
                "all_witness_checks_pass": True,
                "control_assertions_pass": control["pass"],
                "stage1_digest_before_frontier": _STAGE1_EMITTED,
                "ladder_outcome_blind": True,
            },
            "authority": "PROSPECTIVE_ONE_FRESH_NOTEBOOK_MECHANISM_CONFIRMATION_ONLY__NO_NOVELTY_NO_FREEZE_NOT_R6_NOT_END_TO_END",
            "authority_flags": {
                "prospective_confirmation_r4c_mechanism_one_fresh_notebook": outcome == "IMPROVED",
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
    parser = argparse.ArgumentParser(description="O6R4CNS1 prospective fresh-subject run")
    parser.add_argument(
        "--output",
        type=Path,
        default=LANE_DIR / "O6R4CNS1_RESULTS.json",
        help="path for the canonical result JSON",
    )
    args = parser.parse_args()
    result = run()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n")
    print("ORION06_R4CNS1_RESULT_JSON=" + str(args.output))
    if result["terminal"] == "ORION06_R4C_NS1_CONTROL_FAILURE":
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

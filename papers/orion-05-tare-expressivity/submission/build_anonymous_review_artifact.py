#!/usr/bin/env python3
"""Build the identity-scrubbed review archive for the support-two paper."""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path


HERE = Path(__file__).resolve().parent
PAPER = HERE.parent
ROOT = PAPER.parents[1]
OUT = PAPER / "journal_package" / "support_two_normal_form_review_2026-08-28.zip"
FIXED_ZIP_TIME = (2026, 8, 28, 12, 0, 0)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def canonical_json(value) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def sanitized_direct_solver() -> str:
    text = (PAPER / "orion05_r11_sparse_direct_solver.py").read_text(encoding="utf-8")
    replacements = {
        "Independent sparse exact solver for the frozen six-slot R6M grammar.":
            "Standalone sparse exact solver for the declared six-slot grammar.",
        "not import, call, or reproduce the frozen 512-state production XOR DP.":
            "not import or call the unrestricted dynamic program used in the runtime comparison.",
        "input is the already-established R6S theorem.":
            "input is the support-two theorem proved in the manuscript.",
        "frozen local three-way Restore-factor support objective.":
            "declared local three-way correction-factor support objective.",
        "Local phase-ignored Pauli codes follow the production convention":
            "Local phase-ignored Pauli codes use",
        "Frozen donor-owned three-way local Restore-factor support cost.":
            "Three-way local correction-factor support cost.",
        "the frozen grammar requires exactly three frame pairs":
            "the declared grammar requires exactly three frame pairs",
        "O(n) identity-frame Restore baseline for one ordered six-target tuple.":
            "O(n) identity-frame correction baseline for one ordered six-target tuple.",
        "the frozen grammar requires six ordered targets":
            "the declared grammar requires six ordered targets",
        "Exact baseline-plus-active-union Restore score.":
            "Exact baseline-plus-active-union correction score.",
        "Frozen normalized Uanti support cost (the production raw cost minus 18).":
            "Normalized auxiliary-frame support cost (raw form minus the fixed baseline 18).",
        "frozen grammar produced no feasible sparse witness":
            "declared grammar produced no feasible sparse witness",
        "their complete frozen\n    constant families are optimized.":
            "their complete\n    constant families are optimized.",
        "Reconstruct the frozen exact Restore/common-factor phase witness in O(n).":
            "Reconstruct the exact correction/common-factor phase witness in O(n).",
        "Exact direct optimizer including the frozen constant 15 matchings.":
            "Exact direct optimizer including the declared 15 matchings.",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def sanitized_proof_checker() -> str:
    text = (PAPER / "independent_human_proof_sanity.py").read_text(encoding="utf-8")
    replacements = {
        "Independent sanity checker for Q1's analytic R6S proof.":
            "Standalone sanity checker for the analytic support-two proof.",
        "Deliberately imports no ORION quantum/compiler module.":
            "Deliberately imports no solver or compiler module.",
        "1. changing one Restore slot by zeroing a nonidentity frame letter raises the":
            "1. changing one correction slot by zeroing a nonidentity frame letter raises the",
        "   frozen F3 cost by at most 2;":
            "   declared factor cost by at most 2;",
        "This is a regression/sanity check, not an independent external peer review.":
            "This is a finite sanity check, not an independent external peer review.",
        "# Restore-slot letters u,v arbitrary.  The production 18,432-case sweep":
            "# Correction-slot letters u,v are arbitrary.  A larger implementation sweep",
        "# multiplies this by partner/tag/slot/refund bookkeeping that does not":
            "# adds partner/tag/slot/refund bookkeeping that does not",
        '"schema": "ORION.Q1.IndependentHumanProofSanity.v1"':
            '"schema": "anonymous-review.proof-sanity.v1"',
        '"papers/orion-05-tare-expressivity/independent_human_proof_sanity.py"':
            '"proof_sanity.py"',
        '"orion_quantum_imports": False': '"external_solver_imports": False',
        "standalone no-ORION-import finite-core sanity only; a matching CI ":
            "standalone finite-core sanity only; a matching automated ",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


SHARPNESS = r'''#!/usr/bin/env python3
"""Recompute the displayed paired-instance sharpness result."""

import json
from direct_solver import SparseGrammar, solve_matching, verify_witness


TARGET_PAIRS = (
    ((1, 0), (1, 0)),  # XI, XI
    ((1, 0), (1, 0)),  # XI, XI
    ((0, 1), (0, 2)),  # IX, IY
)


def main() -> None:
    grammar_two = SparseGrammar(2, max_support=2)
    grammar_one = SparseGrammar(2, max_support=1)
    witness_two = solve_matching(TARGET_PAIRS, grammar=grammar_two, max_support=2)
    witness_one = solve_matching(TARGET_PAIRS, grammar=grammar_one, max_support=1)
    checks_two = verify_witness(TARGET_PAIRS, witness_two)
    checks_one = verify_witness(TARGET_PAIRS, witness_one)
    assert witness_two.cost == 5
    assert witness_one.cost == 6
    assert all(checks_two.values()) and all(checks_one.values())
    print(json.dumps({
        "schema": "anonymous-review.sharpness.v1",
        "target_pairs": [["XI", "XI"], ["XI", "XI"], ["IX", "IY"]],
        "support_two_cost": witness_two.cost,
        "support_one_cost": witness_one.cost,
        "support_two_witness": witness_two.as_dict(),
        "support_one_witness": witness_one.as_dict(),
        "support_two_checks": checks_two,
        "support_one_checks": checks_one,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
'''


README = """# Anonymous review materials

This archive accompanies *Support-Two Normal Forms for a Shared-Tag Pauli
Compilation Grammar*.

## Reproduce the finite checks

Use Python 3.11 or newer; no third-party package is required.

```text
python proof_sanity.py
python verify_sharpness.py
```

`proof_sanity.py` exhausts the 192 local correction cases and the odd-parity
class tuples through support eight. `verify_sharpness.py` exhaustively obtains
support-two minimum 5 and support-one minimum 6 for the displayed paired instance.
The latter may take tens of seconds in the reference Python implementation.

`runtime_specification.json` records the pre-measurement design and exact Pauli
subjects in neutral notation. `runtime_attempts.jsonl` contains all 120
sanitized attempt rows, `runtime_environment.json` records the available
environment fields, and `aggregate_runtime.py` deterministically checks the
schedule and regenerates the adverse summary:

```text
python aggregate_runtime.py --check runtime_summary.json
```

The summary retains 108 completions and 12 timeouts, including six
three-qubit and six full-subject direct-solver timeouts. The original
unrestricted measurement stack is not included, so these materials support an
audit of the retained measurements rather than a new timing campaign. The
runtime record is not part of the all-size proof and establishes no performance
improvement.

`literature_boundary.md` records the dated search boundary and a nearest-object
comparison. It supports only the manuscript's bounded positioning and is not a
priority or novelty certificate.

The manuscript source is included under `manuscript_source/`. A standard TeX
installation can build it with:

```text
cd manuscript_source
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

The archive contains no author metadata or protected data.
"""


LITERATURE_BOUNDARY = """# Bounded literature and contribution crosswalk

## Search boundary

The search was refreshed through 28 August 2026 using web and arXiv discovery.
Query families combined Tag-and-Restore encoding, shared labels, Pauli frames,
support-two normal forms, exact expressivity, binary-symplectic compilation,
sharp support thresholds, exact and approximate synthesis, low-ancilla block
encodings, fault-tolerant resource models, and compiler benchmarks. Candidate
records were retained when their title, abstract, or accessible full text
concerned the same scientific object or a nearby support-reduction mechanism.
Metadata-only matches that did not expose an assessable scientific claim were
not treated as evidence. Patents, private manuscripts, unindexed software,
non-English sources not located by these channels, and work after the cutoff
were not assessed.

## Nearest-object comparison

| Source family | Scientific object and guarantee | Difference from this paper |
|---|---|---|
| Schillo, Sturm and Quay, version 4, Section 4, Theorems 1-2 and Remarks 1-2 | Tag-and-Restore block encoding with selectable anticommuting frames, controls and compatible label operators | The present paper fixes one six-target specialization and proves a cost-nonincreasing support-two transformation for its declared normalized objective. |
| Izmaylov and coauthors | Grouping anticommuting Pauli terms for measurement | Different task and optimized quantity; no same-object performance comparison is claimed. |
| Cowtan and coauthors; Amy and coauthors | Phase-gadget synthesis and parity-network sharing | Establish support-local decomposition and sharing ideas, not the declared frame-exchange theorem. |
| van den Berg and Temme; PCOAST; PHOENIX; Symphony | Circuit or Hamiltonian transformation in Pauli and binary-symplectic representations | Different compiler objects and guarantees; no same-problem asymptotic improvement is claimed here. |
| DiVincenzo; Fattal and coauthors | Two-qubit universality and stabilizer normal-form foundations | Remove any claim that two-local building blocks or stabilizer reductions originate here. |
| Hastings; Kempe, Kitaev and Regev | Hamiltonian weight reduction, including encodings with additional degrees of freedom or approximation | Different object and preserved quantity from an exact optimum-preserving frame exchange. |

The search did not locate the complete combination of this fixed grammar, this
objective, the coordinate exchange, the exact support-one obstruction, and the
induced direct bound. That statement is a bounded search observation only. It
does not establish absence, priority, broad novelty, significance, or journal
acceptance.
"""


SUBJECT_KEYS = {
    "H4": {
        "anonymous_name": "subject_a",
        "n_qubits": 8,
        "targets": ((0, 68), (0, 80), (0, 64), (0, 136), (0, 144), (0, 128)),
    },
    "N2": {
        "anonymous_name": "subject_b",
        "n_qubits": 12,
        "targets": ((0, 4), (0, 260), (0, 132), (0, 272), (0, 16), (0, 1024)),
    },
}


def perfect_matchings(indices: tuple[int, ...]) -> tuple[tuple[tuple[int, int], ...], ...]:
    if not indices:
        return ((),)
    first = indices[0]
    rows = []
    for offset in range(1, len(indices)):
        pair = (first, indices[offset])
        remaining = indices[1:offset] + indices[offset + 1 :]
        for tail in perfect_matchings(remaining):
            rows.append((pair,) + tail)
    return tuple(sorted(set(rows)))


def pauli_string(key: tuple[int, int], n_qubits: int) -> str:
    letters = {(0, 0): "I", (1, 0): "X", (1, 1): "Y", (0, 1): "Z"}
    x, z = key
    return "".join(letters[((x >> q) & 1, (z >> q) & 1)] for q in range(n_qubits))


def runtime_specification() -> dict:
    original = json.loads(
        (PAPER / "rounds/r12-production-benchmark/ORION05_R12_PRODUCTION_BENCHMARK_PROTOCOL.json").read_text()
    )
    selected = tuple(original["panel"]["matching_indices"])
    matchings = perfect_matchings(tuple(range(6)))
    subjects = {}
    for source_name, row in SUBJECT_KEYS.items():
        subjects[row["anonymous_name"]] = {
            "n_qubits": row["n_qubits"],
            "targets_qubit_zero_first": [
                pauli_string(key, row["n_qubits"]) for key in row["targets"]
            ],
            "selected_pairings": {
                str(index): [list(pair) for pair in matchings[index]] for index in selected
            },
            "source_name_removed": source_name != row["anonymous_name"],
        }
    return {
        "schema": "anonymous-review.runtime-specification.v1",
        "status": "specified_before_measurement",
        "question": (
            "Does complete support-two enumeration provide measured exact-search value "
            "against the unrestricted dynamic program under the identical declared objective?"
        ),
        "algorithms": {
            "support_two": "complete enumeration of ordered anticommuting support-two frame pairs",
            "unrestricted": "complete arbitrary-frame and shared-operator dynamic program",
        },
        "subjects": subjects,
        "panel": {
            "pairing_indices": selected,
            "projections": [1, 2, 3, "full_subject"],
            "correctness_projections": [1, 2],
            "scale_projections": [3, "full_subject"],
            "completed_cell_repeats": 3,
            "timeout_cell_repeats": 1,
            "per_attempt_timeout_seconds": 120,
            "projection_rule": "retain the least-significant Pauli coordinates",
        },
        "measurements": [
            "exact objective value",
            "witness validity",
            "planned search states",
            "wall and CPU nanoseconds",
            "peak resident set size in KiB",
            "witness-verification nanoseconds",
            "completion or timeout",
        ],
        "execution": {
            "measurement_command_template": (
                "<python> <benchmark-runner> --run --output-dir <new-directory> "
                "--python <python> --workers 16"
            ),
            "aggregation_command": "python aggregate_runtime.py --check runtime_summary.json",
            "fresh_process_per_attempt": True,
            "logical_cpus_per_measured_child": 1,
            "maximum_concurrent_children": 16,
        },
        "decision_rule": {
            "preconditions": [
                "all recorded measurement-source bindings were verified before execution",
                "all subject target reconstructions were consistent before execution",
                "the unrestricted solver completes every full-subject cell",
                "all jointly completed cells have equal exact objectives and valid witnesses",
            ],
            "positive": (
                "support-two enumeration completes every full-subject cell and improves median "
                "wall time, CPU time, or peak memory by at least 25 percent; no other resource "
                "median is more than 10 percent worse, and witness-validation time is no more "
                "than 10 percent worse"
            ),
            "null": (
                "the preconditions hold but the positive rule fails, including any support-two "
                "full-subject timeout"
            ),
            "indeterminate": (
                "a measurement-source or target-reconstruction check fails, the unrestricted "
                "solver times out, an objective mismatch persists on repeated comparison, or a "
                "completed witness fails validation"
            ),
        },
        "sanitization": (
            "scientific fields are preserved; author, site, project, path, source-subject "
            "and process identifiers are removed or replaced"
        ),
        "measurement_stack_included": False,
        "measurement_stack_boundary": (
            "the archive supports deterministic audit of retained rows, not a new timing run"
        ),
    }


def runtime_environment() -> dict:
    source = json.loads(
        (PAPER / "rounds/r12-production-benchmark/result/BENCHMARK_ENVIRONMENT.json").read_text()
    )
    return {
        "schema": "anonymous-review.runtime-environment.v1",
        "site_description": "shared academic Linux CPU cluster",
        "platform": source["platform"],
        "machine": source["machine"],
        "processor_field": source["processor"],
        "cpu_model": "not recorded",
        "logical_cpu_count_visible": source["logical_cpu_count"],
        "allocated_logical_cpus": int(source["slurm"]["SLURM_CPUS_PER_TASK"]),
        "requested_memory_gib": 32,
        "workers": source["workers"],
        "python_version": source["python_version"],
        "numpy_version": source["numpy_version"],
        "thread_limits": source["thread_limits"],
        "fresh_single_process_children": True,
        "one_logical_cpu_per_child": True,
        "sanitized_fields_removed": [
            "checkout revision",
            "executable path",
            "scheduler job identifier",
            "scheduler node name",
            "site account",
        ],
    }


def runtime_rows() -> list[dict]:
    source_path = PAPER / "rounds/r12-production-benchmark/result/RAW_ATTEMPTS.jsonl"
    rows = []
    keep = (
        "n_qubits",
        "planned_states",
        "status",
        "cost",
        "witness_valid",
        "witness_checks",
        "wall_ns",
        "cpu_ns",
        "peak_rss_kib",
        "verification_ns",
        "timeout_seconds",
    )
    for line in source_path.read_text().splitlines():
        raw = json.loads(line)
        subject = SUBJECT_KEYS[raw["subject"]]["anonymous_name"]
        algorithm = "unrestricted" if raw["algorithm"] == "unrestricted_dp" else "support_two"
        projection = "full_subject" if raw["projection"] == "FULL_SUBJECT" else raw["projection"]
        row = {
            "subject": subject,
            "pairing_index": int(raw["matching_index"]),
            "projection": projection,
            "algorithm": algorithm,
            "repeat": int(raw["repeat"]),
            "measurement_sources_verified_before_run": bool(raw["source_bindings_ok"]),
        }
        qlabel = "full" if projection == "full_subject" else str(projection)
        row["attempt_id"] = (
            f"{subject}-pairing{row['pairing_index']:02d}-qubits{qlabel}-{algorithm}-repeat{row['repeat']}"
        )
        for key in keep:
            if key in raw:
                value = raw[key]
                if key == "witness_checks" and isinstance(value, dict):
                    value = dict(value)
                    if "production_internal_checks" in value:
                        value["implementation_consistency_checks"] = value.pop(
                            "production_internal_checks"
                        )
                row[key] = value
        rows.append(row)
    rows.sort(key=lambda row: row["attempt_id"])
    if len(rows) != 120 or len({row["attempt_id"] for row in rows}) != 120:
        raise AssertionError("sanitized runtime row count or identity mismatch")
    return rows


AGGREGATE_RUNTIME = r'''#!/usr/bin/env python3
"""Audit all retained runtime rows and regenerate their adverse summary."""

import argparse
import json
import statistics
from pathlib import Path


HERE = Path(__file__).resolve().parent
METRICS = ("wall_ns", "cpu_ns", "peak_rss_kib", "verification_ns")


def load_rows():
    return [json.loads(line) for line in (HERE / "runtime_attempts.jsonl").read_text().splitlines() if line]


def completed(rows):
    return [row for row in rows if row["status"] == "COMPLETED"]


def medians(rows):
    done = completed(rows)
    return {
        metric: (float(statistics.median(int(row[metric]) for row in done)) if done else None)
        for metric in METRICS
    }


def cell(row):
    return row["subject"], int(row["pairing_index"]), row["projection"]


def expected_attempt_ids(spec, rows):
    panel = spec["panel"]
    repeats = int(panel["completed_cell_repeats"])
    correctness = set(panel["correctness_projections"])
    scale = set(panel["scale_projections"])
    by_id = {row["attempt_id"]: row for row in rows}
    expected = set()
    for subject in sorted(spec["subjects"]):
        for pairing in panel["pairing_indices"]:
            for projection in panel["projections"]:
                qlabel = "full" if projection == "full_subject" else str(projection)
                for algorithm in ("support_two", "unrestricted"):
                    initial_repeats = repeats if projection in correctness or algorithm == "unrestricted" else 1
                    for repeat in range(initial_repeats):
                        expected.add(f"{subject}-pairing{int(pairing):02d}-qubits{qlabel}-{algorithm}-repeat{repeat}")
                    first = f"{subject}-pairing{int(pairing):02d}-qubits{qlabel}-{algorithm}-repeat0"
                    if algorithm == "support_two" and projection in scale and by_id.get(first, {}).get("status") == "COMPLETED":
                        for repeat in range(1, repeats):
                            expected.add(f"{subject}-pairing{int(pairing):02d}-qubits{qlabel}-{algorithm}-repeat{repeat}")
    return expected


def summarize():
    specification_path = HERE / "runtime_specification.json"
    environment_path = HERE / "runtime_environment.json"
    spec = json.loads(specification_path.read_text())
    rows = load_rows()
    ids = [row.get("attempt_id") for row in rows]
    assert None not in ids and len(ids) == len(set(ids))
    assert set(ids) == expected_attempt_ids(spec, rows)
    assert all(row.get("measurement_sources_verified_before_run") is True for row in rows)

    grouped = {}
    for row in rows:
        grouped.setdefault((row["algorithm"], *cell(row)), []).append(row)
    correctness_keys = {
        (subject, int(pairing), projection)
        for subject in spec["subjects"]
        for pairing in spec["panel"]["pairing_indices"]
        for projection in spec["panel"]["correctness_projections"]
    }
    full_keys = {
        (subject, int(pairing), "full_subject")
        for subject in spec["subjects"]
        for pairing in spec["panel"]["pairing_indices"]
    }
    repeats = int(spec["panel"]["completed_cell_repeats"])

    def complete_valid(algorithm, keys):
        return all(
            len(completed(grouped.get((algorithm, *key), []))) >= repeats
            and all(row.get("witness_valid") is True for row in completed(grouped.get((algorithm, *key), [])))
            for key in keys
        )

    cost_rows = []
    equal = True
    all_keys = sorted({cell(row) for row in rows}, key=str)
    for key in all_keys:
        left = completed(grouped.get(("unrestricted", *key), []))
        right = completed(grouped.get(("support_two", *key), []))
        if not left or not right:
            continue
        left_costs = sorted({int(row["cost"]) for row in left})
        right_costs = sorted({int(row["cost"]) for row in right})
        row_equal = len(left_costs) == 1 and left_costs == right_costs
        equal = equal and row_equal
        cost_rows.append({"cell": list(key), "unrestricted_costs": left_costs, "support_two_costs": right_costs, "equal": row_equal})

    full_unrestricted = [row for row in rows if row["algorithm"] == "unrestricted" and row["projection"] == "full_subject"]
    full_support_two = [row for row in rows if row["algorithm"] == "support_two" and row["projection"] == "full_subject"]
    scale_three_unrestricted = [row for row in rows if row["algorithm"] == "unrestricted" and row["projection"] == 3]
    scale_three_support_two = [row for row in rows if row["algorithm"] == "support_two" and row["projection"] == 3]
    unrestricted_medians = medians(full_unrestricted)
    support_two_medians = medians(full_support_two)
    ratios = {
        metric: (
            None if unrestricted_medians[metric] in (None, 0) or support_two_medians[metric] is None
            else float(support_two_medians[metric] / unrestricted_medians[metric])
        )
        for metric in METRICS
    }
    positive = False
    done = completed(rows)
    hard_errors = [row["attempt_id"] for row in rows if row["status"] not in ("COMPLETED", "TIMEOUT")]
    return {
        "schema": "anonymous-review.runtime-summary.v2",
        "attempt_counts": {
            "total": len(rows),
            "completed": len(done),
            "timeouts": sum(row["status"] == "TIMEOUT" for row in rows),
            "errors": len(hard_errors),
        },
        "preconditions": {
            "all_measurement_sources_verified_before_run": True,
            "correctness_panel_complete_with_valid_witnesses": complete_valid("unrestricted", correctness_keys) and complete_valid("support_two", correctness_keys),
            "unrestricted_solver_completes_full_subject_panel": complete_valid("unrestricted", full_keys),
            "all_jointly_completed_costs_equal": equal and bool(cost_rows),
            "all_completed_witnesses_valid": all(row.get("witness_valid") is True for row in done),
            "no_non_timeout_execution_errors": not hard_errors,
        },
        "jointly_completed_cells": cost_rows,
        "three_qubit_scale": {
            "unrestricted_timeouts": sum(row["status"] == "TIMEOUT" for row in scale_three_unrestricted),
            "support_two_timeouts": sum(row["status"] == "TIMEOUT" for row in scale_three_support_two),
        },
        "full_subject": {
            "unrestricted_complete": complete_valid("unrestricted", full_keys),
            "support_two_complete": complete_valid("support_two", full_keys),
            "unrestricted_timeouts": sum(row["status"] == "TIMEOUT" for row in full_unrestricted),
            "support_two_timeouts": sum(row["status"] == "TIMEOUT" for row in full_support_two),
            "unrestricted_medians": unrestricted_medians,
            "support_two_medians": support_two_medians,
            "support_two_over_unrestricted_ratios": ratios,
        },
        "positive_performance_rule_satisfied": positive,
        "supported_interpretation": "no measured runtime or memory improvement; all timeout rows are retained",
        "measurement_stack_included": False,
    }


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--write")
    group.add_argument("--check")
    args = parser.parse_args()
    summary = summarize()
    text = json.dumps(summary, indent=2, sort_keys=True) + "\n"
    if args.write:
        (HERE / args.write).write_text(text)
    elif args.check:
        assert json.loads((HERE / args.check).read_text()) == summary
        print("runtime aggregate: PASS")
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
'''


def populate(stage: Path) -> None:
    write(stage / "README.md", README)
    write(stage / "literature_boundary.md", LITERATURE_BOUNDARY)
    write(stage / "direct_solver.py", sanitized_direct_solver())
    write(stage / "proof_sanity.py", sanitized_proof_checker())
    write(stage / "verify_sharpness.py", SHARPNESS)
    write(stage / "runtime_specification.json", canonical_json(runtime_specification()))
    write(stage / "runtime_environment.json", canonical_json(runtime_environment()))
    rows = runtime_rows()
    write(
        stage / "runtime_attempts.jsonl",
        "".join(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n" for row in rows),
    )
    write(stage / "aggregate_runtime.py", AGGREGATE_RUNTIME)
    subprocess.run(
        [sys.executable, str(stage / "aggregate_runtime.py"), "--write", "runtime_summary.json"],
        cwd=stage,
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        [sys.executable, str(stage / "aggregate_runtime.py"), "--check", "runtime_summary.json"],
        cwd=stage,
        check=True,
        capture_output=True,
        text=True,
    )
    shutil.copy2(ROOT / "LICENSE", stage / "LICENSE-CODE-APACHE-2.0.txt")
    shutil.copy2(ROOT / "LICENSE-PAPERS-CC-BY-4.0.txt", stage / "LICENSE-PAPER-CC-BY-4.0.txt")
    manuscript = stage / "manuscript_source"
    manuscript.mkdir()
    for source in sorted((PAPER / "manuscript").glob("*.tex")):
        shutil.copy2(source, manuscript / source.name)
    shutil.copy2(PAPER / "manuscript/bibliography.bib", manuscript / "bibliography.bib")
    sections = manuscript / "sections"
    sections.mkdir()
    for source in sorted((PAPER / "manuscript/sections").glob("*.tex")):
        shutil.copy2(source, sections / source.name)


def scan_identity(stage: Path) -> None:
    forbidden = (
        rb"sze[ -]?chun[ .-]?yiu",
        rb"/users/",
        rb"github\.com/",
        rb"\borion(?:[-_ ]?\d+)?\b",
        rb"\bqg[-_ ]?[a-z0-9]+\b",
        rb"\b(?:cannot_check|ready_to_submit|scientifically_sound_but_target_mismatch|current_claims_not_established|blocked_by_integrity_or_compliance)\b",
        rb"\b(?:commit|pull request|issue #|workflow|continuous integration|build history)\b",
        rb"\b(?:git|source|development|feature|release) branch\b",
        rb"\b(?:pr|issue)\s*#?\d+\b",
        rb"\bsha(?:-?256)?\b",
        rb"\b(?:hash(?:es|ed|ing)?|digest(?:s|ed|ing)?)\b",
        rb"\b[0-9a-f]{40,64}\b",
        rb"\bauthorized_(?:interpretation|conclusion)\b",
        rb"\bproduction_(?:internal|raw|checks?)\b",
        rb"\b(?:donor[-_ ]owned|donor method|donor construction)\b",
        rb"\b(?:frozen|production|internal) (?:grammar|system|convention|checks?|history|release|raw cost)\b",
    )
    for path in stage.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(stage).as_posix().encode().lower()
        original = path.read_bytes()
        data = original.lower()
        for pattern in forbidden:
            if re.search(pattern, relative) or re.search(pattern, data):
                raise AssertionError({"forbidden_pattern": pattern.decode(), "file": str(path)})
        internal_code = rb"\b(?:P\d{1,2}|Q\d+[A-Z0-9_-]*|R\d+[A-Z0-9_-]*|H\d+[A-Z0-9_-]*|B\d+[A-Z0-9_-]*)\b"
        if re.search(internal_code, original):
            raise AssertionError({"forbidden_pattern": internal_code.decode(), "file": str(path)})


def build_zip(stage: Path) -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(OUT, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(stage.rglob("*")):
            if not path.is_file():
                continue
            info = zipfile.ZipInfo(path.relative_to(stage).as_posix(), FIXED_ZIP_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes(), compresslevel=9)


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="anonymous-review-") as temp:
        stage = Path(temp)
        populate(stage)
        scan_identity(stage)
        build_zip(stage)
    print(
        canonical_json(
            {
                "path": str(OUT.relative_to(ROOT)),
                "sha256": hashlib.sha256(OUT.read_bytes()).hexdigest(),
                "bytes": OUT.stat().st_size,
                "identity_scan": "PASS",
            }
        ),
        end="",
    )


if __name__ == "__main__":
    main()

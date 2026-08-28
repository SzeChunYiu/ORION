#!/usr/bin/env python3
"""Build the identity-scrubbed review archive for the support-two paper."""

from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
import zipfile
from pathlib import Path


HERE = Path(__file__).resolve().parent
PAPER = HERE.parent
ROOT = PAPER.parents[1]
OUT = PAPER / "journal_package" / "orion05_anonymous_review_2026-08-28.zip"
FIXED_ZIP_TIME = (2026, 8, 28, 12, 0, 0)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def canonical_json(value) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def sanitized_direct_solver() -> str:
    text = (PAPER / "orion05_r11_sparse_direct_solver.py").read_text(encoding="utf-8")
    text = text.replace(
        "Independent sparse exact solver for the frozen six-slot R6M grammar.",
        "Standalone sparse exact solver for the declared six-slot grammar.",
    )
    text = text.replace(
        "input is the already-established R6S theorem.",
        "input is the support-two theorem proved in the manuscript.",
    )
    return text


def sanitized_proof_checker() -> str:
    text = (PAPER / "independent_human_proof_sanity.py").read_text(encoding="utf-8")
    replacements = {
        "Independent sanity checker for Q1's analytic R6S proof.":
            "Standalone sanity checker for the analytic support-two proof.",
        "Deliberately imports no ORION quantum/compiler module.":
            "Deliberately imports no project quantum/compiler module.",
        '"schema": "ORION.Q1.IndependentHumanProofSanity.v1"':
            '"schema": "anonymous-review.proof-sanity.v1"',
        '"papers/orion-05-tare-expressivity/independent_human_proof_sanity.py"':
            '"proof_sanity.py"',
        '"orion_quantum_imports": False': '"project_quantum_imports": False',
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
class tuples through support eight. `verify_sharpness.py` recomputes the
displayed paired-instance support-two cost 5 and exhaustive support-one cost 6.
The latter may take tens of seconds in the reference Python implementation.

`exact_comparison_summary.json` reports the bounded comparison against a
separate exact referee. `runtime_summary.json` retains the adverse aggregate:
108 of 120 attempts completed and 12 timed out, including every direct-solver
full-subject attempt. These implementation records are not part of the logical
proof of the all-size theorem and do not establish performance improvement.

The manuscript source is included under `manuscript_source/`. The archive
contains no author identity, development history or protected data.
"""


def comparison_summary() -> dict:
    source = json.loads(
        (PAPER / "ORION05_R11_SPARSE_EQUIVALENCE_RESULTS.json").read_text()
    )
    panels = []
    names = ("stress_case_a", "stress_case_b", "sharpness_case")
    for name, row in zip(names, source["hostile_n2_equivalence"]["panels"]):
        panels.append(
            {
                "name": name,
                "separate_referee_cost": row["production_512_state_dp_cost"],
                "direct_support_two_cost": row["sparse_support_two_cost"],
                "direct_support_one_cost": row["sparse_support_one_cost"],
                "cost_equal_on_support_two": row["exact_cost_equal"],
                "direct_witness_checks": row["sparse_witness_checks"],
                "phase_checks": row["sparse_phase_certificate"]["checks"],
                "separate_referee_checks": row["production_witness_separate_checks"],
            }
        )
    return {
        "schema": "anonymous-review.exact-comparison-summary.v1",
        "scope": "declared six-target three-block shared-label support-count grammar only",
        "constructive_pair_checks": source["constructive_pair_checks"],
        "tag_and_preprocessing_checks": source["tag_and_preprocessing_checks"],
        "complete_one_qubit_domain": source["complete_n1_equivalence"],
        "two_qubit_cases": panels,
        "all_declared_checks_pass": all(source["gates"].values()),
        "authority_boundary": (
            "finite conformance and exact witness checking only; not external peer "
            "review, novelty, physical-resource or production-performance evidence"
        ),
    }


def runtime_summary() -> dict:
    source = json.loads(
        (
            PAPER
            / "rounds/r12-production-benchmark/result/"
            "ORION05_R12_PRODUCTION_BENCHMARK_RESULT.json"
        ).read_text()
    )
    return {
        "schema": "anonymous-review.runtime-summary.v1",
        "design": "attempt schedule, limits and success rule specified before measurement",
        "attempt_counts": source["attempt_counts"],
        "preconditions": source["preconditions"],
        "full_subject": source["full_subject"],
        "positive_performance_rule_satisfied": source["decision"]["positive_rule_satisfied"],
        "authorized_interpretation": (
            "no measured runtime or memory improvement; all timeouts are retained"
        ),
    }


def populate(stage: Path) -> None:
    write(stage / "README.md", README)
    write(stage / "direct_solver.py", sanitized_direct_solver())
    write(stage / "proof_sanity.py", sanitized_proof_checker())
    write(stage / "verify_sharpness.py", SHARPNESS)
    write(stage / "exact_comparison_summary.json", canonical_json(comparison_summary()))
    write(stage / "runtime_summary.json", canonical_json(runtime_summary()))
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
        b"Sze Chun Yiu",
        b"sze-chun.yiu",
        b"SzeChunYiu",
        b"/Users/",
        b"github.com/",
        b"ORION",
    )
    for path in stage.rglob("*"):
        if not path.is_file():
            continue
        data = path.read_bytes()
        for token in forbidden:
            if token.lower() in data.lower():
                raise AssertionError({"identity_token": token.decode(), "file": str(path)})


def write_sums(stage: Path) -> None:
    rows = []
    for path in sorted(stage.rglob("*")):
        if path.is_file() and path.name != "SHA256SUMS":
            rows.append(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.relative_to(stage).as_posix()}")
    write(stage / "SHA256SUMS", "\n".join(rows) + "\n")


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
        write_sums(stage)
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

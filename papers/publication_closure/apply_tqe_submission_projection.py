#!/usr/bin/env python3
"""Verify and apply the result-bound TQE submission projection.

The canonical scientific masters are not edited. The existing quantum source
builder first applies the centrally frozen TQE abstract map. This script verifies
that the prepared abstract exactly matches that authority and, for Q1/ORION-05,
appends the separately executed R11 algorithmic section only after checking the
live result/protocol/solver/checker identities and authority boundary.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PAPER_TO_ID = {"Q1": "ORION-05", "QG1": "ORION-09", "QG2": "ORION-10"}
ABSTRACTS_JSON = ROOT / "papers/publication_closure/tqe/TQE_ABSTRACTS_V1.json"
R11_RESULT = ROOT / "papers/orion-05-tare-expressivity/Q1_R11_SPARSE_DIRECT_EXECUTABLE_RESULT_V1.json"
R11_PROTOCOL = ROOT / "papers/orion-05-tare-expressivity/Q1_R11_SPARSE_DIRECT_EXECUTABLE_PROTOCOL_V1.md"
R11_SOLVER = ROOT / "papers/orion-05-tare-expressivity/q1_r11_sparse_direct_solver.py"
R11_PAIR_CHECKER = ROOT / "papers/orion-05-tare-expressivity/q1_r11_pair_count_independent.py"
R11_ADDENDUM = ROOT / "papers/publication_closure/tqe/ORION-05_R11_ADDENDUM.md"
R11_TERMINAL = "Q1_R11_EXACT_O_N9_DIRECT_SOLVER_THEOREM"
WORD_RE = re.compile(r"\b[\w'-]+\b", re.UNICODE)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fail(message: str) -> int:
    print("TQE_SUBMISSION_PROJECTION=FAIL")
    print(f"- {message}")
    return 1


def load_object(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"not a JSON object: {path}")
    return value


def frozen_abstract(paper: str) -> str:
    payload = load_object(ABSTRACTS_JSON)
    if payload.get("schema") != "ORION.TQEAbstractOverrides.v1":
        raise ValueError("wrong TQE abstract authority schema")
    abstracts = payload.get("abstracts")
    if not isinstance(abstracts, dict) or not isinstance(abstracts.get(paper), str):
        raise ValueError(f"missing TQE abstract authority for {paper}")
    return " ".join(str(abstracts[paper]).split())


def verify_r11() -> tuple[bool, str]:
    required_files = (R11_RESULT, R11_PROTOCOL, R11_SOLVER, R11_PAIR_CHECKER, R11_ADDENDUM)
    if not all(path.is_file() for path in required_files):
        return False, "R11 result/protocol/solver/checker/addendum missing"
    result = load_object(R11_RESULT)
    if result.get("terminal") != R11_TERMINAL:
        return False, f"R11 terminal is not {R11_TERMINAL}"
    authority = result.get("authority")
    if not isinstance(authority, dict):
        return False, "R11 authority object missing"
    required = {
        "algorithmic_theorem": True,
        "novelty_authority": False,
        "physical_quantum_resource_authority": False,
        "production_runtime_value": False,
        "submission_authority": False,
    }
    for key, expected in required.items():
        if authority.get(key) is not expected:
            return False, f"R11 authority drifted: {key}={authority.get(key)!r} expected {expected!r}"
    if authority.get("scope") != "frozen R6M six-slot grammar and declared objective only":
        return False, "R11 scope boundary drifted"

    observed_protocol = sha256(R11_PROTOCOL)
    if result.get("protocol_sha256") != observed_protocol:
        return False, "R11 result no longer binds the live protocol digest"
    if result.get("solver_sha256") != sha256(R11_SOLVER):
        return False, "R11 result no longer binds the live direct solver"
    if result.get("pair_checker_sha256") != sha256(R11_PAIR_CHECKER):
        return False, "R11 result no longer binds the live independent pair checker"

    gates = result.get("gates")
    if not isinstance(gates, dict) or not gates or not all(value is True for value in gates.values()):
        return False, "R11 executable gate set is not uniformly green"
    complete_n1 = result.get("complete_n1")
    if not isinstance(complete_n1, dict) or complete_n1.get("pass") is not True:
        return False, "R11 complete n=1 gate is not green"
    if complete_n1.get("denominator") != 729 or complete_n1.get("expected_denominator") != 729:
        return False, "R11 complete n=1 denominator drifted"
    independent = result.get("independent_pair_checker")
    if not isinstance(independent, dict) or independent.get("pass") is not True or independent.get("terminal_present") is not True:
        return False, "R11 independent pair checker is not green"
    qg7 = result.get("qg7_support2")
    if not isinstance(qg7, dict) or qg7.get("pass") is not True:
        return False, "R11 registered support-two exact panel is not green"
    isolation = result.get("source_isolation")
    if not isinstance(isolation, dict) or isolation.get("pass") is not True:
        return False, "R11 source-isolation gate is not green"

    addendum = R11_ADDENDUM.read_text(encoding="utf-8")
    if R11_TERMINAL not in addendum or observed_protocol not in addendum:
        return False, "R11 submission addendum does not bind terminal/protocol digest"
    return True, observed_protocol


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--paper", choices=sorted(PAPER_TO_ID), required=True)
    ap.add_argument("--prepared-in", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    source = args.prepared_in.read_text(encoding="utf-8")
    marker_a = "abstract: |\n"
    marker_d = "dataavailability: |\n"
    a = source.find(marker_a)
    d = source.find(marker_d)
    if a < 0 or d < 0 or d <= a:
        return fail("prepared source YAML abstract/dataavailability markers missing or reordered")
    abstract_start = a + len(marker_a)
    abstract_block = source[abstract_start:d]
    if not abstract_block.startswith("  "):
        return fail("prepared source abstract is not the expected indented YAML block")
    prepared_abstract = " ".join(line.strip() for line in abstract_block.splitlines())
    try:
        authority_abstract = frozen_abstract(args.paper)
    except ValueError as exc:
        return fail(str(exc))
    if prepared_abstract != authority_abstract:
        return fail("prepared abstract differs from centrally frozen TQE abstract authority")
    count = len(WORD_RE.findall(prepared_abstract))
    if not 150 <= count <= 250:
        return fail(f"TQE abstract word count {count} outside 150..250")

    projected = source
    r11_protocol_sha: str | None = None
    scientific_extension = "NONE"
    if args.paper == "Q1":
        ok, detail = verify_r11()
        if not ok:
            return fail(detail)
        r11_protocol_sha = detail
        addendum = R11_ADDENDUM.read_text(encoding="utf-8").strip()
        projected = projected.rstrip() + "\n\n" + addendum + "\n"
        scientific_extension = "R11_RESULT_BOUND_ALGORITHMIC_SECTION"
    elif projected != source:
        return fail("non-Q1 projection changed scientific body")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(projected, encoding="utf-8")
    print("TQE_SUBMISSION_PROJECTION=PASS")
    print(f"PAPER={PAPER_TO_ID[args.paper]}")
    print(f"ABSTRACT_WORD_COUNT={count}")
    print(f"SCIENTIFIC_EXTENSION={scientific_extension}")
    if r11_protocol_sha:
        print(f"R11_PROTOCOL_SHA256={r11_protocol_sha}")
        print(f"R11_RESULT_SHA256={sha256(R11_RESULT)}")
        print(f"R11_SOLVER_SHA256={sha256(R11_SOLVER)}")
        print(f"R11_PAIR_CHECKER_SHA256={sha256(R11_PAIR_CHECKER)}")
    print("CANONICAL_SCIENTIFIC_MASTER_MUTATED=0")
    return 0


if __name__ == "__main__":
    sys.exit(main())

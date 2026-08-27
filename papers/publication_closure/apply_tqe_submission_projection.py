#!/usr/bin/env python3
"""Apply TQE-only abstract and result-bound projection to a prepared quantum paper.

The canonical scientific masters are not edited. This script operates after the
existing citation-only master generator and the journal-neutral source
preparation step. It may replace only the YAML abstract with a frozen TQE
abstract and, for Q1/ORION-05, append the separately executed R11 algorithmic
section after verifying the live result/protocol authority.
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
ABSTRACTS = {
    "Q1": ROOT / "papers/publication_closure/tqe/ORION-05_ABSTRACT.md",
    "QG1": ROOT / "papers/publication_closure/tqe/ORION-09_ABSTRACT.md",
    "QG2": ROOT / "papers/publication_closure/tqe/ORION-10_ABSTRACT.md",
}
R11_RESULT = ROOT / "papers/orion-05-tare-expressivity/Q1_R11_SPARSE_DIRECT_EXECUTABLE_RESULT_V1.json"
R11_PROTOCOL = ROOT / "papers/orion-05-tare-expressivity/Q1_R11_SPARSE_DIRECT_EXECUTABLE_PROTOCOL_V1.md"
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


def verify_r11() -> tuple[bool, str]:
    if not (R11_RESULT.is_file() and R11_PROTOCOL.is_file() and R11_ADDENDUM.is_file()):
        return False, "R11 result/protocol/addendum missing"
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
    observed_protocol = sha256(R11_PROTOCOL)
    if result.get("protocol_sha256") != observed_protocol:
        return False, "R11 result no longer binds the live protocol digest"
    gates = result.get("gates")
    if not isinstance(gates, dict) or not gates or not all(value is True for value in gates.values()):
        return False, "R11 executable gate set is not uniformly green"
    complete_n1 = result.get("complete_n1")
    if not isinstance(complete_n1, dict) or complete_n1.get("pass") is not True:
        return False, "R11 complete n=1 gate is not green"
    if complete_n1.get("denominator") != complete_n1.get("expected_denominator"):
        return False, "R11 complete n=1 denominator is incomplete"
    independent = result.get("independent_pair_checker")
    if not isinstance(independent, dict) or independent.get("pass") is not True:
        return False, "R11 independent pair checker is not green"
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
    original_abstract_block = source[abstract_start:d]
    if not original_abstract_block.startswith("  "):
        return fail("prepared source abstract is not the expected indented YAML block")

    abstract_path = ABSTRACTS[args.paper]
    if not abstract_path.is_file():
        return fail(f"missing TQE abstract: {abstract_path.relative_to(ROOT)}")
    abstract = " ".join(abstract_path.read_text(encoding="utf-8").split())
    count = len(WORD_RE.findall(abstract))
    if not 150 <= count <= 250:
        return fail(f"TQE abstract word count {count} outside 150..250")
    abstract_block = "  " + abstract.replace("\n", "\n  ") + "\n"
    projected = source[:abstract_start] + abstract_block + source[d:]

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

    # Non-Q1 projections may alter only the abstract block. Q1 may additionally
    # append exactly the frozen R11 addendum after passing the authority checks.
    if args.paper != "Q1":
        expected_delta = len(abstract_block) - len(original_abstract_block)
        if len(projected) - len(source) != expected_delta:
            return fail("non-Q1 projection changed text outside the abstract")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(projected, encoding="utf-8")
    print("TQE_SUBMISSION_PROJECTION=PASS")
    print(f"PAPER={PAPER_TO_ID[args.paper]}")
    print(f"ABSTRACT_WORD_COUNT={count}")
    print(f"SCIENTIFIC_EXTENSION={scientific_extension}")
    if r11_protocol_sha:
        print(f"R11_PROTOCOL_SHA256={r11_protocol_sha}")
        print(f"R11_RESULT_SHA256={sha256(R11_RESULT)}")
    print("CANONICAL_SCIENTIFIC_MASTER_MUTATED=0")
    return 0


if __name__ == "__main__":
    sys.exit(main())

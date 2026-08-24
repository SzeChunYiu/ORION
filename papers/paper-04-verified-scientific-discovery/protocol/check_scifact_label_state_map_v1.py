#!/usr/bin/env python3
"""Validate the frozen SciFact label-to-P4-state adapter.

`SCIFACT_LABEL_STATE_MAP_V1.json` is the only sanctioned adapter from external
SciFact gold labels into P4 semantic-support and authority-terminal states. Its
whole value comes from being frozen *before* any SciFact scoring: a mapping
edited after outcomes are visible is a tuned mapping, whatever it claims. This
checker enforces the structural invariants that make the freeze meaningful:

* totality — every label in the SciFact claim-verdict vocabulary has a mapping
  row, and no row invents a label outside it;
* decisiveness — a gold REFUTE can only produce BLOCK, a NOT_ENOUGH_INFO can
  only produce CANNOT_CHECK, and a gold SUPPORT is never sufficient for BLOCK;
* no-UNRESOLVED — no readable external label may map into the ORION-internal
  UNRESOLVED state;
* Crossref/RW whitelist exactness — the allowed-use set is exactly the three
  coordinate uses and an active retraction forces a revocation BLOCK;
* freeze honesty — the map asserts outcome_accessed=false and no SciFact
  outcome artifact exists under the P4 evidence directory.

Exit codes: 0 conformant, 1 violation found, 2 the map (or evidence tree)
could not be read — distinct from clean, because "could not check" must never
be reported as "checked and fine".
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

PROTOCOL_DIR = Path(__file__).resolve().parent
DEFAULT_MAP = PROTOCOL_DIR / "SCIFACT_LABEL_STATE_MAP_V1.json"
EVIDENCE_DIR = PROTOCOL_DIR.parent / "evidence"

EXPECTED_ALLOWED_USES = {
    "DOI_METADATA_UPDATE",
    "EVALUATION_EPOCH",
    "REVOCATION_CONFORMANCE",
}


def _violations(doc: dict) -> list[str]:
    problems: list[str] = []

    # --- freeze honesty -----------------------------------------------------
    if doc.get("freeze_status") != "FROZEN_BEFORE_ANY_SCIFACT_SCORING":
        problems.append(f"freeze_status is {doc.get('freeze_status')!r}")
    if doc.get("outcome_accessed") is not False:
        problems.append(f"outcome_accessed is {doc.get('outcome_accessed')!r}, not false")
    frozen_utc = doc.get("frozen_utc")
    try:
        datetime.fromisoformat(str(frozen_utc).replace("Z", "+00:00"))
    except (ValueError, TypeError):
        problems.append(f"frozen_utc {frozen_utc!r} is not an ISO-8601 timestamp")

    # --- mapping totality over the declared vocabulary ----------------------
    vocab = doc.get("scifact_label_vocabulary", {})
    verdict_labels = vocab.get("claim_verdict_labels", [])
    rows = doc.get("frozen_mapping", [])
    mapped = {row.get("scifact_label"): row for row in rows}
    if len(mapped) != len(rows):
        problems.append("frozen_mapping contains duplicate scifact_label rows")
    for label in verdict_labels:
        if label not in mapped:
            problems.append(f"no frozen_mapping row for claim-verdict label {label!r}")
    for label in mapped:
        if label not in verdict_labels:
            problems.append(f"frozen_mapping row {label!r} is outside the SciFact vocabulary")

    # --- per-row decisiveness ----------------------------------------------
    semantic_states = doc.get("p4_state_vocabulary", {}).get("semantic_support", [])
    for row in rows:
        label = row.get("scifact_label")
        state = row.get("p4_semantic_support")
        if state not in semantic_states:
            problems.append(f"{label}: semantic support {state!r} outside the P4 vocabulary")
        if state == "UNRESOLVED":
            problems.append(f"{label}: maps to UNRESOLVED (reserved for unreadable labels)")
    refute = mapped.get("REFUTE", {})
    if refute.get("p4_semantic_support") != "CONTRADICTED" or refute.get("terminal") != "BLOCK":
        problems.append("REFUTE must map to CONTRADICTED with decisive terminal BLOCK")
    nei = mapped.get("NOT_ENOUGH_INFO", {})
    if nei.get("p4_semantic_support") != "INSUFFICIENT" or nei.get("terminal") != "CANNOT_CHECK":
        problems.append("NOT_ENOUGH_INFO must map to INSUFFICIENT with terminal CANNOT_CHECK")
    support = mapped.get("SUPPORT", {})
    if support.get("p4_semantic_support") != "SUPPORTED":
        problems.append("SUPPORT must map to SUPPORTED")
    if support.get("terminal_on_all_obligations_discharged") != "PROMOTE":
        problems.append("SUPPORT with all obligations discharged must be PROMOTE")
    if support.get("terminal_on_any_unresolved_obligation") != "CANNOT_CHECK":
        problems.append("SUPPORT with an unresolved obligation must fail closed to CANNOT_CHECK")
    if support.get("never_terminal") != "BLOCK":
        problems.append("a gold SUPPORT alone must never yield BLOCK")
    if not support.get("required_promotion_obligations"):
        problems.append("SUPPORT row lists no promotion obligations (PROMOTE would be unconditional)")

    # --- composition rules ---------------------------------------------------
    composition = doc.get("claim_verdict_composition", {})
    if "contradiction_dominates" not in composition.get("rules", {}):
        problems.append("claim_verdict_composition is missing contradiction_dominates")

    # --- Crossref / Retraction Watch whitelist exactness ---------------------
    rw = doc.get("crossref_retraction_watch_constraint", {})
    allowed = set(rw.get("allowed_uses", []))
    if allowed != EXPECTED_ALLOWED_USES:
        missing = sorted(EXPECTED_ALLOWED_USES - allowed)
        extra = sorted(allowed - EXPECTED_ALLOWED_USES)
        problems.append(
            f"allowed_uses must be exactly {sorted(EXPECTED_ALLOWED_USES)}; "
            f"missing={missing} extra={extra}"
        )
    for use in EXPECTED_ALLOWED_USES:
        if use not in rw.get("allowed_use_definitions", {}):
            problems.append(f"allowed use {use!r} has no definition")
    if not rw.get("forbidden_uses"):
        problems.append("no forbidden_uses recorded for Crossref/RW")
    retraction = rw.get("conformance_rules", {}).get("active_retraction_on_gold_evidence_doi", {})
    if retraction.get("forced_terminal") != "BLOCK" or retraction.get(
        "revocation_nonconformant"
    ) is not True:
        problems.append("an active retraction on gold evidence must force a revocation BLOCK")

    return problems


def _scifact_outcome_artifacts(evidence_dir: Path) -> list[str] | None:
    """SciFact-named files under the P4 evidence tree; None if the tree is unreadable."""

    if not evidence_dir.exists():
        return []
    try:
        return sorted(
            str(path.relative_to(evidence_dir))
            for path in evidence_dir.rglob("*")
            if path.is_file() and "scifact" in path.name.lower()
        )
    except OSError:
        return None


def run(map_path: Path = DEFAULT_MAP) -> int:
    """Entry point usable from tests; returns the process exit code."""

    if not map_path.is_file():
        print(f"CANNOT_CHECK: no label-state map at {map_path}", file=sys.stderr)
        return 2
    try:
        doc = json.loads(map_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as error:
        print(f"CANNOT_CHECK: map could not be read: {error}", file=sys.stderr)
        return 2
    if not isinstance(doc, dict):
        print("CANNOT_CHECK: map root is not a JSON object", file=sys.stderr)
        return 2

    problems = _violations(doc)
    artifacts = _scifact_outcome_artifacts(EVIDENCE_DIR)
    if artifacts is None:
        print(f"CANNOT_CHECK: evidence tree {EVIDENCE_DIR} is unreadable", file=sys.stderr)
        return 2
    if artifacts:
        problems.append(
            f"SciFact outcome artifacts present under evidence/ at check time: {artifacts}"
        )

    if problems:
        print(f"SCIFACT LABEL-STATE MAP: FAIL — {len(problems)} violation(s)")
        for problem in problems:
            print(f"  - {problem}")
        return 1

    print("SCIFACT LABEL-STATE MAP: conformant (total, decisive, fail-closed, pre-scoring)")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--map", type=Path, default=DEFAULT_MAP)
    args = parser.parse_args(argv)
    return run(args.map)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

#!/usr/bin/env python3
"""Fail-closed validator and hostile mutation suite for Paper 2 claims."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
LEDGER_PATH = ROOT / "research/experiments/davenport-c7-frontier/PAPER2_ATOMIC_CLAIM_LEDGER_V1.json"

REQUIRED_STATUSES = {
    "P2.A2.EXACT_OVERLAP_AND_RADIAL": "PROVED_ANALYTIC",
    "P2.A2.EXACT_DEPTH_FIBER_ENVELOPE": "PROVED_ANALYTIC",
    "P2.RANK3.EXACT_OVERLAP_PLANE_COST": "PROVED_ANALYTIC",
    "P2.A3.RANK2_FACE_EMPTY": "PROVED_ANALYTIC_DONOR_DEPENDENT",
    "P2.RANK3.A_GE4.SIMULTANEOUS_OVERLAP_BOUND": "PROVED_ANALYTIC_REDUCTION",
    "P2.RANK3.A_GE4.DOUBLING_BOUNDARY": "PROVED_ANALYTIC_REDUCTION",
    "P2.RANK3.A_GE4.TRIPLE_CENTRAL_BOUNDARY": "PROVED_ANALYTIC_REDUCTION",
    "P2.A2.TOP_OVERLAP_STANDARD_FAMILIES_EMPTY": "PROVED_CONDITIONAL_ANALYTIC",
    "P7.A2.RANK3_SUPPORT4_EQUALITY_EMPTY": "PROVED_EXACT_FINITE",
    "P7.FIRST_CORRIDOR.SUPPORT4_MAXIMAL_PAIR_SUPPORT_GE7": "PROVED_COMPOSITE",
    "P7.SECOND_CORRIDOR.SUPPORT6_COMPLETIONS_PACK_FOUR": "PROVED_EXACT_FINITE",
    "P7.TWO_CORRIDOR.SUPPORT6_MAXIMAL_PAIR_FACE_EXCLUDED": "PROVED_COMPOSITE",
    "P2.ALL_PRIME.FIRST_CORRIDOR_SUPPORT7": "OPEN",
    "P2.RANK2.A1.C_GE5_EMPTY": "OPEN",
    "P2.RANK2.A2.C_GE5_EMPTY": "OPEN",
    "P2.RANK3.A_GE4.EDGE_REGIMES_EMPTY": "OPEN",
    "P2.RANK3.EXCEPTIONAL_A2_A3_EMPTY": "OPEN",
    "P7.MAXIMAL_ATOM.SUPPORT_GE5_CLOSED": "OPEN",
    "P7.SUPPORT8.TYPE_A_EMPTY": "OPEN",
    "P7.D3_EXACT_36": "OPEN",
    "P2.NOVELTY_AND_PRIORITY": "CANNOT_CHECK",
    "P2.TOP_SPECIALIST_SUBMISSION": "DEVELOPMENT_READY",
}

EXPECTED_FLAGS = {
    "exact_D3_C7_proved": False,
    "all_prime_first_corridor_support7_proved": False,
    "all_prime_Dk_formula_proved": False,
    "complete_length37_obstruction_classification_proved": False,
    "novelty_certified": False,
    "priority_certified": False,
    "top_generalist_submission_ready": False,
    "top_specialist_development_track_ready": True,
    "C7_two_corridor_support_growth_proved": True,
}

ANCHORS = {
    "research/experiments/davenport-c7-frontier/A2_EXACT_OVERLAP_AND_RADIAL_STAIRCASE_V1.md": [
        "c_light=2 floor(H/2)",
        "lambda_{2,c}(D)-D=2 ceil(max(D-c-2,0)/2)",
    ],
    "research/experiments/davenport-c7-frontier/A2_EXACT_DEPTH_FIBER_ENVELOPE_V1.md": [
        "Exact fiber-envelope theorem",
        "M_p(w,C)",
    ],
    "research/experiments/davenport-c7-frontier/SUPPORT4_EXACT_OVERLAP_PLANE_LIFTING_COST_V1.md": [
        "nu_a(C,D)",
        "rank-three",
    ],
    "research/experiments/davenport-c7-frontier/A3_LEFT_HALF_BOUNDARY_ELIMINATION_V1.md": [
        "Left-half boundary theorem",
        "Complete type-three rank-two theorem",
    ],
    "research/experiments/davenport-c7-frontier/P7_A2_RANK3_SUPPORT4_EQUALITY_EMPTY_V1.md": [
        "14 ordered parameter pairs",
        "C7 support-seven corollary",
    ],
    "research/experiments/davenport-c7-frontier/SUPPORT6_9919_CLOSURE_V1.md": [
        "1634",
        "26",
    ],
    "research/experiments/davenport-c7-frontier/PAPER2_TOP_SPECIALIST_THEOREM_SPINE_V1.md": [
        "Claim ceiling",
        "D_3(C_7^3)=36",
    ],
}


class LedgerError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise LedgerError(message)


def index_claims(data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    claims = data.get("claims")
    require(isinstance(claims, list), "claims must be a list")
    indexed: dict[str, dict[str, Any]] = {}
    for item in claims:
        require(isinstance(item, dict), "every claim must be an object")
        claim_id = item.get("id")
        require(isinstance(claim_id, str) and claim_id, "claim id must be nonempty")
        require(claim_id not in indexed, f"duplicate claim id: {claim_id}")
        indexed[claim_id] = item
    return indexed


def validate(data: dict[str, Any], *, check_live_files: bool = True) -> dict[str, int]:
    require(data.get("schema") == "ORION.PAPER2_ATOMIC_CLAIM_LEDGER_V1", "wrong schema")
    require(data.get("as_of_date") == "2026-09-04", "wrong as-of date")
    require(data.get("reconciled_integration_parent") == "9229d28be5a643ff7bf30ea6213aba717c48e309", "wrong integration parent")

    allowed = data.get("allowed_statuses")
    require(isinstance(allowed, list), "allowed_statuses must be a list")
    allowed_set = set(allowed)
    require(len(allowed_set) == len(allowed), "allowed_statuses contains duplicates")
    require(set(REQUIRED_STATUSES.values()) <= allowed_set, "required status missing from allow-list")

    flags = data.get("authority_flags")
    require(flags == EXPECTED_FLAGS, "authority flags do not match the frozen claim ceiling")

    scope = data.get("scope")
    require(isinstance(scope, dict), "scope must be an object")
    require(scope.get("primary_bounded_group") == "C_7^3", "bounded group drift")
    require("no exact D_3(C_7^3) value" in scope.get("claim_ceiling", ""), "claim ceiling must withhold exact D3")

    indexed = index_claims(data)
    require(set(indexed) == set(REQUIRED_STATUSES), "claim id set drift")

    counts = {
        "proved": 0,
        "open": 0,
        "cannot_check": 0,
        "development_ready": 0,
        "evidence_paths": 0,
    }

    for claim_id, expected_status in REQUIRED_STATUSES.items():
        claim = indexed[claim_id]
        status = claim.get("status")
        require(status == expected_status, f"status drift for {claim_id}")
        require(status in allowed_set, f"unallowed status for {claim_id}")
        require(isinstance(claim.get("statement"), str) and claim["statement"], f"missing statement for {claim_id}")
        require(isinstance(claim.get("limitations"), str) and claim["limitations"], f"missing limitations for {claim_id}")

        authority = claim.get("theorem_authority")
        require(isinstance(authority, bool), f"theorem_authority must be boolean for {claim_id}")
        if status.startswith("PROVED_"):
            require(authority is True, f"proved claim lacks theorem authority: {claim_id}")
            counts["proved"] += 1
        elif status == "OPEN":
            require(authority is False, f"open claim promoted: {claim_id}")
            counts["open"] += 1
        elif status == "CANNOT_CHECK":
            require(authority is False, f"cannot-check claim promoted: {claim_id}")
            counts["cannot_check"] += 1
        elif status == "DEVELOPMENT_READY":
            require(authority is False, f"development status must not be theorem authority: {claim_id}")
            counts["development_ready"] += 1

        evidence = claim.get("evidence")
        require(isinstance(evidence, list) and evidence, f"missing evidence for {claim_id}")
        require(len(evidence) == len(set(evidence)), f"duplicate evidence path for {claim_id}")
        if status.startswith("PROVED_ANALYTIC") or status in {"PROVED_EXACT_FINITE", "PROVED_COMPOSITE"}:
            require(len(evidence) >= 2, f"proved claim needs at least two evidence paths: {claim_id}")
        for relative in evidence:
            require(isinstance(relative, str) and not relative.startswith("/"), f"bad evidence path in {claim_id}")
            require(".." not in Path(relative).parts, f"path traversal in {claim_id}")
            if check_live_files:
                path = ROOT / relative
                require(path.is_file(), f"missing live evidence file: {relative}")
            counts["evidence_paths"] += 1

    require(counts == {
        "proved": 12,
        "open": 8,
        "cannot_check": 1,
        "development_ready": 1,
        "evidence_paths": 54,
    }, f"frozen census drift: {counts}")

    # Cross-record authority implications.
    require(indexed["P7.D3_EXACT_36"]["status"] == "OPEN", "exact D3 must remain open")
    require(indexed["P2.ALL_PRIME.FIRST_CORRIDOR_SUPPORT7"]["status"] == "OPEN", "all-prime support-seven must remain open")
    require(indexed["P2.NOVELTY_AND_PRIORITY"]["status"] == "CANNOT_CHECK", "priority must remain cannot-check")
    require(indexed["P7.TWO_CORRIDOR.SUPPORT6_MAXIMAL_PAIR_FACE_EXCLUDED"]["status"] == "PROVED_COMPOSITE", "bounded support-growth theorem lost")

    if check_live_files:
        for relative, anchors in ANCHORS.items():
            text = (ROOT / relative).read_text(encoding="utf-8")
            for anchor in anchors:
                require(anchor in text, f"missing anchor {anchor!r} in {relative}")

    return counts


def expect_rejected(mutant: dict[str, Any], label: str) -> None:
    try:
        validate(mutant, check_live_files=False)
    except LedgerError:
        return
    raise AssertionError(f"hostile mutation accepted: {label}")


def hostile_mutations(data: dict[str, Any]) -> int:
    mutants: list[tuple[str, dict[str, Any]]] = []

    mutant = copy.deepcopy(data)
    mutant["authority_flags"]["exact_D3_C7_proved"] = True
    mutants.append(("promote exact D3 flag", mutant))

    mutant = copy.deepcopy(data)
    for claim in mutant["claims"]:
        if claim["id"] == "P7.D3_EXACT_36":
            claim["status"] = "PROVED_ANALYTIC"
            claim["theorem_authority"] = True
    mutants.append(("promote exact D3 claim", mutant))

    mutant = copy.deepcopy(data)
    mutant["authority_flags"]["novelty_certified"] = True
    mutants.append(("grant novelty", mutant))

    mutant = copy.deepcopy(data)
    for claim in mutant["claims"]:
        if claim["id"] == "P2.NOVELTY_AND_PRIORITY":
            claim["status"] = "PROVED_ANALYTIC"
            claim["theorem_authority"] = True
    mutants.append(("promote priority claim", mutant))

    mutant = copy.deepcopy(data)
    mutant["claims"] = [claim for claim in mutant["claims"] if claim["id"] != "P2.RANK3.A_GE4.EDGE_REGIMES_EMPTY"]
    mutants.append(("delete open edge claim", mutant))

    mutant = copy.deepcopy(data)
    mutant["claims"].append(copy.deepcopy(mutant["claims"][0]))
    mutants.append(("duplicate claim id", mutant))

    mutant = copy.deepcopy(data)
    mutant["claims"][0]["evidence"] = []
    mutants.append(("erase analytic evidence", mutant))

    mutant = copy.deepcopy(data)
    mutant["claims"][0]["evidence"][0] = "/tmp/forged.md"
    mutants.append(("absolute forged evidence", mutant))

    mutant = copy.deepcopy(data)
    for claim in mutant["claims"]:
        if claim["id"] == "P2.RANK2.A2.C_GE5_EMPTY":
            claim["theorem_authority"] = True
    mutants.append(("promote open a2 face", mutant))

    mutant = copy.deepcopy(data)
    mutant["allowed_statuses"].remove("OPEN")
    mutants.append(("remove open from allow-list", mutant))

    mutant = copy.deepcopy(data)
    mutant["scope"]["claim_ceiling"] = "D_3(C_7^3)=36"
    mutants.append(("erase exact-value withholding", mutant))

    mutant = copy.deepcopy(data)
    mutant["authority_flags"]["top_generalist_submission_ready"] = True
    mutants.append(("grant top-generalist authority", mutant))

    for label, item in mutants:
        expect_rejected(item, label)
    return len(mutants)


def main() -> None:
    raw = LEDGER_PATH.read_bytes()
    data = json.loads(raw)
    require(isinstance(data, dict), "ledger root must be an object")
    counts = validate(data)
    rejected = hostile_mutations(data)
    canonical = json.dumps(data, sort_keys=True, separators=(",", ":")).encode()
    print(json.dumps({
        "status": "PAPER2_ATOMIC_CLAIM_LEDGER_GREEN",
        "counts": counts,
        "hostile_mutations_rejected": rejected,
        "ledger_bytes_sha256": hashlib.sha256(raw).hexdigest(),
        "canonical_json_sha256": hashlib.sha256(canonical).hexdigest(),
        "authority": "claim-governance validator only; it cannot promote theorem, novelty, priority, or venue authority",
    }, sort_keys=True))


if __name__ == "__main__":
    main()

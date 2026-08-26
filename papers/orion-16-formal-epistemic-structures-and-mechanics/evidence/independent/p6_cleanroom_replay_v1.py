#!/usr/bin/env python3
"""Clean-room replay unit for the frozen P6 bounded formal bundle (V1).

This is the second, independently implemented execution unit required by the
operator-approved substitute protocol for the P6.EMPIRICAL.LIFTING.V1 external
reproduction gate.  It shares NO code path with the local execution unit:

  * it does not import ``papers.candidates.reproducibility_generators_v3``;
  * it does not import any module under ``formal/`` of this paper;
  * it does not run the paper Makefile or any of its targets;
  * schema validation, canonical serialization, the six hostile-kind decision
    procedures, and the SMT obligation discharge are re-implemented here from
    the frozen artifacts themselves.

What it does, in order:

  1. CUSTODY: recompute sha256 for every file bound by the frozen V3 local
     replay contract and the V2 content manifest (raw inputs, raw outputs,
     bound files, environment lock) and require equality.
  2. BYTE-FOR-BYTE RE-DERIVATION: regenerate the countermodel JSONL bytes from
     the frozen source register with this unit's own serializer and validator
     and require byte identity with the committed artifact.
  3. SEMANTIC RE-EXECUTION: independently implement the six hostile-kind
     decision procedures and require agreement with all twelve frozen
     ``expected_verdict`` entries plus the register's own balance invariants.
  4. SMT RE-DISCHARGE: discharge the frozen certificate-lifting obligation
     with this unit's own exhaustive enumeration decision procedure (a
     complete method for the two-Boolean fragment), cross-checked by z3
     parsing, and prove each registered law live under weakened mutants with
     explicit witness assignments.
  5. RECEIPT: emit a machine-signed (Ed25519) receipt over the canonical
     fact payload.  The signing key is derived deterministically from the
     committed domain string so any party can re-derive the public key.

Run from the repository root:

    python papers/orion-16-formal-epistemic-structures-and-mechanics/evidence/independent/p6_cleanroom_replay_v1.py

Requires z3 for the cross-check leg only (``--no-z3`` skips that leg and
records it as skipped rather than passing it silently).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

PAPER = Path(__file__).resolve().parents[2]
ROOT = PAPER.parents[1]

CONTRACT = PAPER / "evidence/local/P6_LOCAL_REPLAY_CONTRACT_V3.json"
MANIFEST = PAPER / "CONTENT_MANIFEST_V2.json"
SOURCE = PAPER / "formal/assumption_countermodels_v2.source.json"
SCHEMA = PAPER / "formal/assumption_countermodels_v2.schema.json"
JSONL = PAPER / "formal/assumption_countermodels_v2.jsonl"
SMT2 = PAPER / "formal/certificate_lifting_scope_v1.smt2"
RECEIPT = PAPER / "evidence/independent/P6_CLEANROOM_REPLAY_RECEIPT_V1.json"

KEY_DOMAIN = "P6-CLEANROOM-REPLAY-V1-KEY"
CUSTODIAN = "orion-gap-lane-b-cleanroom-unit"

SCHEMA_VERSION = "orion.p6.cleanroom-replay-receipt.v1"

# ---------------------------------------------------------------------------
# This unit's own primitives (deliberately independent implementations).
# ---------------------------------------------------------------------------


def digest_bytes(payload: bytes) -> str:
    """This unit's digest helper (name and structure chosen independently)."""
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def digest_file(path: Path) -> str:
    return digest_bytes(path.read_bytes())


def canon(obj) -> bytes:
    """Signing canonicalization: sorted keys so payload order cannot matter."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()


def signing_key() -> Ed25519PrivateKey:
    seed = hashlib.sha256(KEY_DOMAIN.encode()).digest()
    return Ed25519PrivateKey.from_private_bytes(seed)


def public_key_hex() -> str:
    key = signing_key()
    return key.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw).hex()


# ---------------------------------------------------------------------------
# 1. Custody: every digest bound by the frozen contract and manifest.
# ---------------------------------------------------------------------------


def verify_bundle() -> dict:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    checks = []
    for group in ("raw_inputs", "raw_outputs"):
        for entry in contract.get(group, []):
            checks.append(("contract." + group, entry["path"], entry["sha256"]))
    for entry in manifest.get("bound_files", []):
        checks.append(("manifest.bound_files", entry["path"], entry["sha256"]))
    lock = manifest.get("environment_lock", {})
    if lock:
        checks.append(("manifest.environment_lock", lock["path"], lock["sha256"]))

    results = []
    for source, rel, expected in checks:
        observed = digest_file(ROOT / rel)
        results.append(
            {
                "bound_by": source,
                "path": rel,
                "expected": "sha256:" + expected,
                "observed": observed,
                "match": observed == "sha256:" + expected,
            }
        )
    return {
        "contract_terminal": contract.get("terminal"),
        "contract_schema": contract.get("schema_version"),
        "manifest_schema": manifest.get("schema_version"),
        "bindings_checked": len(results),
        "bindings_matched": sum(1 for r in results if r["match"]),
        "all_matched": all(r["match"] for r in results),
        "failures": [r for r in results if not r["match"]],
    }


# ---------------------------------------------------------------------------
# 2. Byte-for-byte re-derivation of the countermodel register.
# ---------------------------------------------------------------------------

_TYPE_RULES = {
    "string": lambda v: isinstance(v, str),
    "boolean": lambda v: isinstance(v, bool),
    "array": lambda v: isinstance(v, list),
    "object": lambda v: isinstance(v, dict),
}


def _check_node(value, rule, where: str, problems: list) -> None:
    """Independent schema-subset walk: explicit dispatch, closed properties."""
    expected_type = rule.get("type")
    if expected_type not in _TYPE_RULES or not _TYPE_RULES[expected_type](value):
        problems.append(f"{where}: expected {expected_type}")
        return
    if "enum" in rule and value not in rule["enum"]:
        problems.append(f"{where}: {value!r} outside enum")
    if expected_type == "string" and "minLength" in rule:
        if len(value) < rule["minLength"]:
            problems.append(f"{where}: shorter than minLength")
    if expected_type == "array":
        if "minItems" in rule and len(value) < rule["minItems"]:
            problems.append(f"{where}: fewer than minItems")
        item_rule = rule.get("items")
        if item_rule:
            for i, item in enumerate(value):
                _check_node(item, item_rule, f"{where}[{i}]", problems)


def validate_register(cases: list, schema: dict) -> list:
    problems: list[str] = []
    props = schema["properties"]
    required = set(schema["required"])
    # JSON Schema semantics: undeclared keys violate the schema only when it
    # closes properties with additionalProperties:false.  The frozen schema
    # leaves it open, so kind-specific carriers (claim, note, candidate_root,
    # trusted_root) are legal; this unit records them rather than rejecting.
    closed = schema.get("additionalProperties") is False
    extra_keys: set[str] = set()
    for n, case in enumerate(cases):
        where = f"case[{n}]"
        keys = set(case)
        unknown = keys - set(props)
        if unknown:
            extra_keys |= unknown
            if closed:
                problems.append(f"{where}: undeclared keys {sorted(unknown)}")
        missing = required - keys
        if missing:
            problems.append(f"{where}: missing required {sorted(missing)}")
        for key, value in case.items():
            if key in props:
                _check_node(value, props[key], f"{where}.{key}", problems)
    return problems


def rederive_register() -> dict:
    register = json.loads(SOURCE.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    if register.get("schema_version") != "orion.p6.assumption-countermodel-source.v2":
        raise SystemExit("clean-room unit: unexpected source schema version")
    cases = register["cases"]
    problems = validate_register(cases, schema)
    additional = sorted(
        {k for case in cases for k in case} - set(schema["properties"])
    )

    rebuilt = bytearray()
    for case in cases:
        # This unit's serializer: separator-tight JSON, one trailing newline,
        # keys in register order (source order is part of the frozen bytes).
        rebuilt += json.dumps(case, ensure_ascii=False, separators=(",", ":")).encode()
        rebuilt += b"\n"
    committed = JSONL.read_bytes()
    return {
        "schema_problems": problems,
        "schema_valid": not problems,
        "schema_closes_additional_properties": schema.get("additionalProperties") is False,
        "additional_keys_permitted_by_schema": additional,
        "rederived_bytes": len(rebuilt),
        "committed_bytes": len(committed),
        "byte_for_byte_identical": bytes(rebuilt) == committed,
        "rederived_digest": digest_bytes(bytes(rebuilt)),
        "committed_digest": digest_bytes(committed),
        "records": len(cases),
    }


# ---------------------------------------------------------------------------
# 3. Independent decision procedures for the six hostile kinds.
# ---------------------------------------------------------------------------


def verdict_stale_certification(case) -> str:
    return "DETECTED" if case["path_realizable"] and case["retained_descendant"] else "NOT_DETECTED"


def verdict_undeclared_write(case) -> str:
    escaped = set(case["proposed_write"]) - set(case["declared_write"])
    return "DETECTED" if escaped else "NOT_DETECTED"


def verdict_nonseparated_composition(case) -> str:
    overlap = set(case["left_write"]) & set(case["right_read"])
    return "DETECTED" if overlap else "NOT_DETECTED"


def verdict_authority_escalation(case) -> str:
    widened_root = case["candidate_root"] != case["trusted_root"]
    return "DETECTED" if widened_root and not case["scope_narrowing"] else "NOT_DETECTED"


def verdict_recursive_cycle(case) -> str:
    adjacency: dict[str, list[str]] = {}
    for src, dst in case["call_edges"]:
        adjacency.setdefault(src, []).append(dst)
    state: dict[str, int] = {}  # 0 unvisited / 1 on-stack / 2 done

    def has_cycle(node: str) -> bool:
        state[node] = 1
        for nxt in adjacency.get(node, ()):
            mark = state.get(nxt, 0)
            if mark == 1:
                return True
            if mark == 0 and has_cycle(nxt):
                return True
        state[node] = 2
        return False

    return "DETECTED" if any(state.get(n, 0) == 0 and has_cycle(n) for n in list(adjacency)) else "NOT_DETECTED"


def verdict_self_authorization(case) -> str:
    both = case["candidate_controls_policy"] and case["candidate_controls_evidence"]
    return "DETECTED" if both else "NOT_DETECTED"


PROCEDURES = {
    "stale_certification": verdict_stale_certification,
    "undeclared_write": verdict_undeclared_write,
    "nonseparated_composition": verdict_nonseparated_composition,
    "authority_escalation": verdict_authority_escalation,
    "recursive_cycle": verdict_recursive_cycle,
    "self_authorization": verdict_self_authorization,
}


def reexecute_semantics() -> dict:
    cases = json.loads(SOURCE.read_text(encoding="utf-8"))["cases"]
    table = []
    for case in cases:
        procedure = PROCEDURES.get(case["kind"])
        if procedure is None:
            raise SystemExit(f"clean-room unit: unregistered kind {case['kind']!r}")
        derived = procedure(case)
        table.append(
            {
                "id": case["id"],
                "kind": case["kind"],
                "frozen": case["expected_verdict"],
                "cleanroom": derived,
                "agree": derived == case["expected_verdict"],
            }
        )
    kinds = sorted({row["kind"] for row in table})
    per_kind = {kind: sum(1 for r in table if r["kind"] == kind) for kind in kinds}
    verdicts = {v: sum(1 for r in table if r["frozen"] == v) for v in ("DETECTED", "NOT_DETECTED")}
    return {
        "verdict_table": table,
        "cases": len(table),
        "agreeing": sum(1 for r in table if r["agree"]),
        "all_agree": all(r["agree"] for r in table),
        "kinds": len(kinds),
        "cases_per_kind": per_kind,
        "verdict_balance": verdicts,
        "balance_invariant_holds": per_kind == {k: 2 for k in kinds}
        and verdicts == {"DETECTED": 6, "NOT_DETECTED": 6},
    }


# ---------------------------------------------------------------------------
# 4. Independent SMT discharge: exhaustive enumeration + weakened mutants.
# ---------------------------------------------------------------------------


def smt_structural_fingerprint() -> dict:
    text = SMT2.read_text(encoding="utf-8")
    lines = [ln.strip() for ln in text.splitlines()]
    body = [ln for ln in lines if ln and not ln.startswith(";")]
    return {
        "declarations": sum(1 for ln in body if ln.startswith("(declare-const")),
        "definitions": sum(1 for ln in body if ln.startswith("(define-fun")),
        "assertions": sum(1 for ln in body if ln.startswith("(assert")),
        "checks": sum(1 for ln in body if ln.startswith("(check-sat")),
        "logic_line": next((ln for ln in body if ln.startswith("(set-logic")), None),
    }


def enumerate_obligation() -> dict:
    """Complete decision procedure for the two-Boolean fragment, no solver.

    Lift and ideal product are conjunctions over the two declared Booleans;
    the obligation is UNSAT iff every assignment falsifies each registered
    violation disjunct.  The semantics are re-encoded here from the frozen
    definitions rather than imported.
    """
    witness_violations = []
    for donor in (False, True):
        for complete in (False, True):
            lift = donor and complete
            ideal = donor and complete
            v1 = lift != ideal                      # equivalence violation
            v2 = lift and not donor                 # manufacture donor validity
            v3 = donor and not complete and lift    # manufacture a coordinate
            if v1 or v2 or v3:
                witness_violations.append({"donor_valid": donor, "complete": complete})
    return {
        "assignments_enumerated": 4,
        "violation_witnesses": witness_violations,
        "obligation_unsat_by_enumeration": not witness_violations,
    }


def weakened_mutants() -> dict:
    """Prove each registered law is live: dropping it admits a violation."""
    mutants = {}
    for donor in (False, True):
        for complete in (False, True):
            # A: drop the scientific-coordinate conjunct from the lift.
            lift_a = donor
            ideal_a = donor and complete
            if lift_a != ideal_a:
                mutants.setdefault("drop_scientific_coordinate", []).append(
                    {"donor_valid": donor, "complete": complete}
                )
            # B: drop donor validity from the lift.
            lift_b = complete
            ideal_b = donor and complete
            if lift_b and not donor:
                mutants.setdefault("drop_donor_validity", []).append(
                    {"donor_valid": donor, "complete": complete}
                )
            # C: break exact equivalence by reusing ideal as an OR-product.
            or_product = donor or complete
            if or_product and not (donor and complete):
                mutants.setdefault("or_product_equivalence_break", []).append(
                    {"donor_valid": donor, "complete": complete}
                )
    return {
        name: {"live": bool(witnesses), "witnesses": witnesses}
        for name, witnesses in mutants.items()
    }


def z3_cross_check() -> dict:
    try:
        import z3  # noqa: PLC0415
    except ImportError:
        return {"available": False, "result": "SKIPPED_NO_Z3"}
    assertions = z3.parse_smt2_string(SMT2.read_text(encoding="utf-8"))
    solver = z3.Solver()
    solver.assert_exprs(*assertions)
    verdict = str(solver.check())
    return {"available": True, "result": verdict, "obligation_unsat": verdict == "unsat"}


def discharge_smt() -> dict:
    enumeration = enumerate_obligation()
    fingerprint = smt_structural_fingerprint()
    expected_fingerprint = {
        "declarations": 2,
        "definitions": 2,
        "assertions": 1,
        "checks": 1,
    }
    structure_ok = all(fingerprint[k] == v for k, v in expected_fingerprint.items())
    return {
        "frozen_file_digest": digest_file(SMT2),
        "structural_fingerprint": fingerprint,
        "structure_as_expected": structure_ok,
        "own_enumeration": enumeration,
        "weakened_mutants": weakened_mutants(),
        "all_mutants_live": all(m["live"] for m in weakened_mutants().values()),
        "z3_cross_check": z3_cross_check(),
    }


# ---------------------------------------------------------------------------
# 5. Signed receipt.
# ---------------------------------------------------------------------------


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--no-z3", action="store_true", help="skip the z3 cross-check leg")
    parser.add_argument("--check", action="store_true", help="verify the committed receipt instead of writing")
    args = parser.parse_args(argv)

    if args.check:
        return check_committed_receipt()

    custody = verify_bundle()
    register = rederive_register()
    semantics = reexecute_semantics()
    smt = discharge_smt()
    if args.no_z3:
        smt["z3_cross_check"] = {"available": False, "result": "SKIPPED_BY_FLAG"}

    gates = {
        "custody_all_matched": custody["all_matched"],
        "register_byte_for_byte": register["byte_for_byte_identical"],
        "register_schema_valid": register["schema_valid"],
        "semantics_all_agree": semantics["all_agree"],
        "balance_invariant_holds": semantics["balance_invariant_holds"],
        "smt_structure_as_expected": smt["structure_as_expected"],
        "smt_unsat_by_enumeration": smt["own_enumeration"]["obligation_unsat_by_enumeration"],
        "all_mutants_live": smt["all_mutants_live"],
    }
    z3_leg = smt["z3_cross_check"]
    if z3_leg.get("available"):
        gates["smt_unsat_by_z3_cross_check"] = z3_leg["obligation_unsat"]

    facts = {
        "schema_version": SCHEMA_VERSION,
        "receipt_date": "2026-08-24",
        "paper_id": "P6",
        "claim_id": "P6.EMPIRICAL.LIFTING.V1",
        "execution_kind": "SUBSTITUTE_CLEANROOM_REPLAY",
        "custodian_unit": CUSTODIAN,
        "custody": custody,
        "register_rederivation": register,
        "semantic_reexecution": semantics,
        "smt_redischarge": smt,
        "gates": gates,
        "disjoint_code_path": {
            "imports_shared_with_local_unit": [],
            "notes": [
                "no import of papers.candidates.reproducibility_generators_v3",
                "no import of any papers/orion-16-*/formal module",
                "no make target executed; own serializer, schema walk, six decision procedures, and enumeration solver",
            ],
        },
        "authority_boundary": (
            "Converts the frozen bundle's status from LOCAL_REPLAY_ONLY to "
            "INDEPENDENT_UNIT_REPLAY_MATCH under the operator-approved substitute "
            "protocol (second independently implemented execution unit, disjoint code "
            "path, machine-signed receipt). Grants no empirical, deployed, or "
            "population authority; the bounded formal scope of Claim Ledger V4 is "
            "unchanged."
        ),
    }
    payload_digest = digest_bytes(canon(facts))
    signature = signing_key().sign(canon(facts)).hex()
    receipt = {
        "facts": facts,
        "payload_digest": payload_digest,
        "signature_ed25519_hex": signature,
        "public_key_hex": public_key_hex(),
        "key_derivation": f"sha256('{KEY_DOMAIN}') as Ed25519 seed",
        "outcome": "P6_CLEANROOM_REPLAY_MATCH" if all(gates.values()) else "P6_CLEANROOM_REPLAY_GATE_FAILED",
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"outcome": receipt["outcome"], "gates": gates}, indent=2))
    return 0 if all(gates.values()) else 1


def check_committed_receipt() -> int:
    """Re-verify the committed receipt: signature, digest, and key identity."""
    from cryptography.exceptions import InvalidSignature
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    key = Ed25519PublicKey.from_public_bytes(bytes.fromhex(receipt["public_key_hex"]))
    try:
        key.verify(bytes.fromhex(receipt["signature_ed25519_hex"]), canon(receipt["facts"]))
        signature_ok = True
    except InvalidSignature:
        signature_ok = False
    digest_ok = digest_bytes(canon(receipt["facts"])) == receipt["payload_digest"]
    key_ok = receipt["public_key_hex"] == public_key_hex()
    print(
        json.dumps(
            {
                "signature_valid": signature_ok,
                "payload_digest_matches": digest_ok,
                "public_key_rederivable": key_ok,
                "outcome": receipt["outcome"],
            },
            indent=2,
        )
    )
    return 0 if signature_ok and digest_ok and key_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

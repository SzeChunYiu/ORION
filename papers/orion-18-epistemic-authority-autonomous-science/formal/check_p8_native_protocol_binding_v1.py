#!/usr/bin/env python3
"""Fail closed if P8's native cross-system protocol drifts across artifacts.

Binds ``P8.NATIVE.CROSS_SYSTEM_PROTOCOL.V1`` across the protocol document, its
machine-readable twin, the manuscript surfaces, the additive ledger and the
candidate V2 content manifest. The protocol's structure (4 systems, 12 ordered pairs,
24 case slots, hostile mechanisms) is validated, not just grep-checked: a
protocol whose slots no longer cover every ordered pair is a different protocol
and must not keep this contract id. Execution remains ``CANNOT_CHECK`` and the
checker refuses any state that quietly claims otherwise.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PAPER = "papers/orion-18-epistemic-authority-autonomous-science"
CONTRACT_ID = "P8.NATIVE.CROSS_SYSTEM_PROTOCOL.V1"

DOC = f"{PAPER}/formal/P8_NATIVE_CROSS_SYSTEM_PROTOCOL_V1.md"
TWIN = f"{PAPER}/formal/P8_NATIVE_CROSS_SYSTEM_PROTOCOL_2026-08-24.json"
CHECKER = f"{PAPER}/formal/check_p8_native_protocol_binding_v1.py"
FINAL = f"{PAPER}/manuscript/FINAL_V3.md"
CORE = f"{PAPER}/manuscript/FORMAL_CORE_V2_1.md"
LEDGER = f"{PAPER}/CLAIM_LEDGER_ADDENDUM_V3.md"
MANIFEST = f"{PAPER}/CONTENT_MANIFEST_V2.json"

FILES = (DOC, TWIN, CHECKER, FINAL, CORE, LEDGER)

SYSTEM_IDS = ("OPA", "CDR", "ITT", "SIG")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_protocol(payload: dict) -> list[str]:
    """Structural validation of the frozen protocol, independent of the files.

    Returns error strings; empty means the protocol is exactly what the issue
    box demands: every ordered cross-system pair, clean and hostile each.
    """

    errors: list[str] = []
    if payload.get("contract_id") != CONTRACT_ID:
        errors.append("twin is not bound to the contract id")
    if payload.get("execution_status") != "CANNOT_CHECK":
        errors.append("execution status must remain CANNOT_CHECK until a pinned-binary run exists")
    gap = payload.get("tooling_gap", {})
    for binary in ("opa", "cedar", "cosign", "in-toto-verify"):
        if binary not in gap.get("required_binaries", []):
            errors.append(f"tooling gap omits required binary: {binary}")

    systems = {s.get("id") for s in payload.get("systems", [])}
    if systems != set(SYSTEM_IDS):
        errors.append(f"system set is not the four type-distinct systems: {sorted(systems)}")

    pairs = payload.get("ordered_pairs", [])
    expected_pairs = {
        (emitter, consumer)
        for emitter in SYSTEM_IDS
        for consumer in SYSTEM_IDS
        if emitter != consumer
    }
    seen_pairs = [(p.get("emitter"), p.get("consumer")) for p in pairs]
    if set(seen_pairs) != expected_pairs or len(seen_pairs) != len(set(seen_pairs)):
        errors.append("ordered pairs do not cover exactly the 12 distinct cross-system pairs")
    if payload.get("slot_count") != 2 * len(expected_pairs):
        errors.append("slot count is not two per ordered pair")

    mechanisms = []
    for pair in pairs:
        emitter, consumer = pair.get("emitter"), pair.get("consumer")
        for kind in ("clean", "hostile"):
            case_id = pair.get(f"{kind}_case_id", "")
            if not re.fullmatch(rf"P8\.NC\.{emitter}_{consumer}\.{kind.upper()}", case_id):
                errors.append(f"case id does not follow the frozen pattern: {case_id}")
        mechanism = pair.get("hostile_mechanism", "")
        if not mechanism or not mechanism.strip():
            errors.append(f"empty hostile mechanism for {emitter}->{consumer}")
        mechanisms.append(mechanism)
    if len(set(mechanisms)) != len(mechanisms):
        errors.append("hostile mechanisms are not pairwise distinct")

    for clause in (
        "simulating any native system",
        "partial run",
    ):
        if clause not in " ".join(payload.get("prohibited_inference", [])):
            errors.append(f"prohibited inference omits: {clause}")
    if "AUTHORIZ" not in str(payload.get("hostile_pass_criterion", "")):
        errors.append("hostile pass criterion does not constrain AUTHORIZED")
    return errors


def audit(root: Path = ROOT) -> dict[str, object]:
    errors: list[str] = []
    texts: dict[str, str] = {}
    for relative in FILES:
        path = root / relative
        if not path.exists():
            errors.append(f"missing file: {relative}")
            continue
        texts[relative] = path.read_text(encoding="utf-8")
        if CONTRACT_ID not in texts[relative]:
            errors.append(f"missing contract id: {relative}")

    if TWIN in texts:
        try:
            payload = json.loads(texts[TWIN])
        except json.JSONDecodeError as exc:
            errors.append(f"twin is not valid JSON: {exc}")
        else:
            errors.extend(validate_protocol(payload))

    doc = " ".join(texts.get(DOC, "").lower().split())
    for phrase in (
        "Execution status: `CANNOT_CHECK`",
        "every ordered cross-system pair",
        "clean and hostile",
        "twenty-four case slots",
        "Nothing in this protocol is simulated",
        "not re-derive",
    ):
        if phrase.lower() not in doc:
            errors.append(f"protocol document missing frozen semantics: {phrase}")

    final = texts.get(FINAL, "")
    core = texts.get(CORE, "")
    ledger = texts.get(LEDGER, "")
    for path, text, phrases in (
        (FINAL, final, ("CANNOT_CHECK", "twelve ordered cross-system pairs", "not been run")),
        (CORE, core, ("is not executed", "P8.NATIVE.CROSS_SYSTEM_PROTOCOL.V1")),
        (LEDGER, ledger, ("CANNOT_CHECK", "additive rows only", "prohibited inference")),
    ):
        normalized = " ".join(text.lower().split())
        for phrase in phrases:
            if phrase.lower() not in normalized:
                errors.append(f"{path} missing bound semantics: {phrase}")

    manifest_path = root / MANIFEST
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        recorded_hashes = {
            row["path"]: row["sha256"]
            for row in manifest.get("bound_files", [])
            if isinstance(row, dict)
            and isinstance(row.get("path"), str)
            and isinstance(row.get("sha256"), str)
        }
        required_bound = set(FILES)
        for path in sorted(required_bound - set(recorded_hashes)):
            errors.append(f"content manifest omits contract artifact: {path}")
        if manifest.get("subject_commit_status") != "BOUND":
            errors.append("content manifest subject_commit_status is not BOUND")
        if manifest.get("subject_commit_unbound_paths") != []:
            errors.append("content manifest retains unbound contract paths")
        for path in sorted(required_bound):
            if recorded_hashes.get(path) != _sha256(root / path):
                errors.append(f"V2 content-manifest mismatch or omission: {path}")
    else:
        errors.append(f"missing manifest: {MANIFEST}")

    return {
        "schema": "orion.p8.native-protocol-binding.v1",
        "contract_id": CONTRACT_ID,
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "authority_boundary": (
            "a frozen test design validated structurally in the producing lane; "
            "no native system was executed, no output was simulated, and the "
            "CANNOT_CHECK execution status is enforced rather than asserted"
        ),
    }


def main() -> int:
    report = audit()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

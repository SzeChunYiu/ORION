"""Fail-closed drift checker for the issue #1086 P13-P15 lifecycle lane.

Verifies that the P13C/P14D integrations, the D7 scope narrowing, the
P13+P14 gold-derivation rule, the P15 internal-panel binding and the P15
failure ledger remain bound across the canonical artifacts. Any drift in
terminal strings, key numbers, authority rebuilds, hashes or manifest coverage
must surface as a non-empty error list (status FAIL).
"""

from __future__ import annotations

import json
import sys
from hashlib import sha1, sha256
from pathlib import Path
from typing import Any

CHECKER_ID = "ORION.P13P14P15.LIFECYCLE_CONSOLIDATION_BINDING.V1"
P13C_TERMINAL = "P13C_COMPOSED_SAFETY_EFFICACY_SUPPORTED"
P13C_REPLAY_SHA = "645961cf01afe15f1b5976244b76b846c31d3c6119af4fbbc031e4b2a3611e57"
P14D_TERMINAL = "P14D_EXTERNAL_ACQUISITION_BLOCKED"
P14C_TERMINAL = "P14C_SPECIFICATION_SEPARATED_GOVERNANCE_CONFORMANCE_SUPPORTED"
FORBIDDEN_P13_PHRASES = (
    "measured interior safety",
    "occupies the desired interior",
    "can eliminate unsafe compact reuse",
    "eliminate structurally unsafe state reuse",
    "safety–cost superiority evidence",
)

ROOT = Path(__file__).resolve().parents[2]
P13 = ROOT / "papers/paper-13-responsibility-carrying-state"
P14 = ROOT / "papers/paper-14-orion-rse"
P15 = ROOT / "papers/paper-15-orion-research-harness"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _json(path: Path) -> dict[str, Any]:
    return json.loads(_text(path))


def _sha256(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _git_blob_sha(path: Path) -> str:
    payload = path.read_bytes()
    header = f"blob {len(payload)}\0".encode()
    return sha1(header + payload).hexdigest()


def _require(errors: list[str], condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


def _check_p13(errors: list[str]) -> None:
    manuscript = _text(P13 / "MANUSCRIPT.md")
    for token in (
        "### 7.5 Composed safety–efficacy (P13C)",
        P13C_TERMINAL,
        P13C_REPLAY_SHA,
        "P13_ACTIVE_CLAIM_AUTHORITY_V3.json",
        "### 8.1 Scope binding",
        "P13_P14_LIFECYCLE_GOLD_DERIVATION_RULE_V1.md",
        "P13_P14_CONSOLIDATION_SCOPE_BINDING_V1.json",
        "two independent experts plus",
    ):
        _require(errors, token in manuscript, f"P13 MANUSCRIPT.md lost token: {token}")
    for phrase in FORBIDDEN_P13_PHRASES:
        _require(
            errors,
            phrase not in manuscript,
            f"P13 MANUSCRIPT.md regained forbidden phrase: {phrase}",
        )

    ledger = _text(P13 / "CLAIM_EVIDENCE_LEDGER.md")
    for token in (
        P13C_TERMINAL,
        "SUPPORTED / CONTROLLED P13C",
        "P13_ACTIVE_CLAIM_AUTHORITY_V3.json",
        "P13_P14_LIFECYCLE_GOLD_DERIVATION_RULE_V1.md",
        "P13_P14_CONSOLIDATION_SCOPE_BINDING_V1.json",
    ):
        _require(errors, token in ledger, f"P13 ledger lost token: {token}")
    _require(
        errors,
        ledger.count("**CANNOT_CHECK**") >= 1,
        "P13 ledger lost the CANNOT_CHECK broader-claims row",
    )


def _check_p13_authority(errors: list[str]) -> None:
    sys.path.insert(0, str(ROOT / "src"))
    try:
        from orion.study.p13.composed_authority import (  # noqa: PLC0415
            ACTIVE_TERMINAL,
            build_composed_claim_authority,
        )
    except Exception as exc:  # noqa: BLE001
        errors.append(f"P13 V3 builder not importable: {exc}")
        return
    finally:
        sys.path.remove(str(ROOT / "src"))

    committed = _json(P13 / "P13_ACTIVE_CLAIM_AUTHORITY_V3.json")
    try:
        rebuilt = build_composed_claim_authority()
    except Exception as exc:  # noqa: BLE001
        errors.append(f"P13 V3 rebuild failed: {exc}")
        return
    _require(
        errors,
        committed == rebuilt,
        "P13_ACTIVE_CLAIM_AUTHORITY_V3.json does not match its builder",
    )
    _require(
        errors,
        committed.get("active_terminal") == ACTIVE_TERMINAL,
        "P13 V3 active terminal drifted",
    )
    leaves = {leaf["claim_id"]: leaf for leaf in committed["active_claim_leaves"]}
    composed = leaves.get("P13C.COMPOSED.SAFETY_EFFICACY", {})
    result = composed.get("result", {})
    _require(
        errors,
        result.get("authenticated_unsafe_reuse") == 0,
        "P13C leaf lost zero-unsafe-reuse",
    )
    _require(
        errors,
        result.get("scheduled_corruptions_rejected") == "2457/2457",
        "P13C leaf lost 2457/2457 corruption rejection",
    )
    _require(
        errors,
        result.get("unverified_rcs_unsafe_reuse") == 330,
        "P13C leaf lost the unverified-RCS 330 unsafe reuses",
    )
    _require(
        errors,
        result.get("byte_identical_replay_core_sha256") == P13C_REPLAY_SHA,
        "P13C leaf replay digest drifted",
    )


def _check_scope_and_gold(errors: list[str]) -> None:
    binding = _json(P13 / "P13_P14_CONSOLIDATION_SCOPE_BINDING_V1.json")
    _require(errors, binding.get("decision_id") == "D7", "scope binding is not D7")
    _require(
        errors,
        binding.get("p14_separate_75_paper") is False,
        "scope binding must keep P14 below the separate-75+ bar",
    )
    _require(
        errors,
        binding.get("broader_claims_status") == "CANNOT_CHECK",
        "scope binding must keep broader claims CANNOT_CHECK",
    )
    _require(
        errors,
        set(binding.get("gold_objective_fact_classes", []))
        == {
            "object/hash existence",
            "ancestry",
            "tag/signature",
            "test exit",
            "timestamp order",
        },
        "scope binding gold fact classes drifted",
    )
    disposition = ROOT / binding["source_disposition_artifact"]
    _require(
        errors,
        binding["source_disposition_sha256"] == _sha256(disposition),
        "scope binding no longer binds the portfolio disposition by hash",
    )
    rule = ROOT / binding["gold_derivation_rule_artifact"]
    _require(
        errors,
        binding["gold_derivation_rule_sha256"] == _sha256(rule),
        "scope binding no longer binds the gold-derivation rule by hash",
    )
    rule_text = _text(rule)
    for token in (
        "PROSPECTIVE_PROTOCOL_RULE",
        "object/hash existence",
        "ancestry",
        "tag/signature",
        "test exit",
        "timestamp order",
        "**never** be used as an external subject",
        "CANNOT_CHECK",
    ):
        _require(errors, token in rule_text, f"gold rule lost token: {token}")


def _check_p14(errors: list[str]) -> None:
    manuscript = _text(P14 / "MANUSCRIPT.md")
    for token in (
        "### P14D — frozen acquisition contract; preflight blocked",
        P14D_TERMINAL,
        "execution_authorized=false",
        P14C_TERMINAL,
        "P13_P14_CONSOLIDATION_SCOPE_BINDING_V1.json",
        "P13_P14_LIFECYCLE_GOLD_DERIVATION_RULE_V1.md",
        "two independent experts plus",
        "CANNOT_CHECK",
    ):
        _require(errors, token in manuscript, f"P14 MANUSCRIPT.md lost token: {token}")
    _require(
        errors,
        "not** a separate paper at the 75+" in manuscript,
        "P14 manuscript lost the not-a-separate-75+ bound",
    )

    ledger = _text(P14 / "CLAIM_EVIDENCE_LEDGER.md")
    for token in (
        P14D_TERMINAL,
        "SUPPORTED / BINDING",
        "CANNOT_CHECK / CONSOLIDATED D7",
        "P13_P14_LIFECYCLE_GOLD_DERIVATION_RULE_V1.md",
    ):
        _require(errors, token in ledger, f"P14 ledger lost token: {token}")

    authority = _json(P14 / "P14_ACTIVE_CLAIM_AUTHORITY_V1.json")
    acquisition = authority["prospective_external_validation"]
    _require(
        errors,
        acquisition["execution_authorized"] is False,
        "P14 authority must keep external execution unauthorized",
    )
    _require(
        errors,
        acquisition["terminal"] == P14D_TERMINAL,
        "P14 authority terminal drifted",
    )
    for prefix in ("protocol", "preflight", "validator"):
        path = (P14 / acquisition[f"{prefix}_artifact"]).resolve()
        _require(
            errors,
            acquisition[f"{prefix}_sha256"] == _sha256(path),
            f"P14 authority {prefix} binding drifted",
        )


def _check_p15(errors: list[str]) -> None:
    binding = _json(P15 / "P15_INTERNAL_PANEL_EVIDENCE_BINDING_V1.json")
    _require(
        errors,
        binding["status"] == "SUPPORTED_INTERNAL_PANEL",
        "P15 binding status drifted",
    )
    _require(
        errors,
        binding["population_inference"] is False,
        "P15 binding must keep population_inference false",
    )
    _require(
        errors,
        binding["label_repository_status"] == "NO_DISTINCT_ARTIFACT",
        "P15 binding must keep the no-P15B-artifact record",
    )
    layers = binding["bound_result_layers"]
    _require(
        errors,
        set(layers) == {"sei_fault_v1", "provenance_interop_v1", "attestation_composition_v2"},
        "P15 binding result layers drifted",
    )
    for key, record in layers.items():
        path = ROOT / record["artifact"]
        _require(errors, path.is_file(), f"P15 binding layer {key} artifact missing")
        if path.is_file():
            _require(
                errors,
                record["git_blob_sha"] == _git_blob_sha(path),
                f"P15 binding layer {key} blob hash drifted",
            )
    v3 = _json(P15 / "P15_ACTIVE_CLAIM_AUTHORITY_V3.json")
    for key, record in layers.items():
        _require(
            errors,
            record["git_blob_sha"] == v3["result_authority"][key]["git_blob_sha"],
            f"P15 binding layer {key} diverges from V3 authority",
        )

    failure = _text(P15 / "P15_FAILURE_LEDGER_V1.md")
    for token in (
        "P15A_ACQUISITION_BLOCKED_NO_SCIENTIFIC_RESULT",
        "6 attempts, 0 detections",
        "6/6",
        "12",
        "Retained-run policy",
        "scientific_authority_delta: NONE",
    ):
        _require(errors, token in failure, f"P15 failure ledger lost token: {token}")

    ledger = _text(P15 / "CLAIM_EVIDENCE_LEDGER.md")
    for token in (
        "P15_ACTIVE_CLAIM_AUTHORITY_V3.json",
        "P15_BOUNDED_SEI_PROVENANCE_ATTESTATION_EARNED",
        "SUPPORTED_INTERNAL_PANEL / population_inference:false",
        "NO_DISTINCT_ARTIFACT",
        "P15_FAILURE_LEDGER_V1.md",
    ):
        _require(errors, token in ledger, f"P15 ledger lost token: {token}")


def _check_manifests(errors: list[str]) -> None:
    required = {
        P13: [
            "MANUSCRIPT.md",
            "CLAIM_EVIDENCE_LEDGER.md",
            "P13_ACTIVE_CLAIM_AUTHORITY_V3.json",
            "P13_P14_CONSOLIDATION_SCOPE_BINDING_V1.json",
            "P13_P14_LIFECYCLE_GOLD_DERIVATION_RULE_V1.md",
            "check_lifecycle_consolidation_binding_v1.py",
        ],
        P14: ["MANUSCRIPT.md", "CLAIM_EVIDENCE_LEDGER.md"],
        P15: [
            "CLAIM_EVIDENCE_LEDGER.md",
            "P15_INTERNAL_PANEL_EVIDENCE_BINDING_V1.json",
            "P15_FAILURE_LEDGER_V1.md",
        ],
    }
    for paper, names in required.items():
        manifest = _json(paper / "CONTENT_MANIFEST_V1.json")
        bound = {entry["path"] for entry in manifest["bound_files"]}
        _require(
            errors,
            manifest.get("subject_commit_status") == "BOUND",
            f"{paper.name} manifest is not BOUND",
        )
        _require(
            errors,
            manifest.get("subject_commit_unbound_paths") == [],
            f"{paper.name} manifest has unbound paths",
        )
        for name in names:
            relative = f"papers/{paper.name}/{name}"
            _require(
                errors,
                relative in bound,
                f"{paper.name} manifest does not cover {name}",
            )


def audit(root: Path | None = None) -> dict[str, Any]:
    global ROOT, P13, P14, P15  # noqa: PLW0603
    if root is not None:
        ROOT = root
        P13 = ROOT / "papers/paper-13-responsibility-carrying-state"
        P14 = ROOT / "papers/paper-14-orion-rse"
        P15 = ROOT / "papers/paper-15-orion-research-harness"

    errors: list[str] = []
    for check in (
        _check_p13,
        _check_p13_authority,
        _check_scope_and_gold,
        _check_p14,
        _check_p15,
        _check_manifests,
    ):
        try:
            check(errors)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{check.__name__} raised: {exc}")

    return {
        "checker_id": CHECKER_ID,
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "p13c_terminal": P13C_TERMINAL,
        "p14d_terminal": P14D_TERMINAL,
        "p15_status": "SUPPORTED_INTERNAL_PANEL",
        "population_inference": False,
        "authority_boundary": (
            "Registered composed finite worlds and internal panels only: no "
            "external validation, no population inference, no ORION-as-subject "
            "campaign; broader correct-governance and social-responsibility "
            "claims stay CANNOT_CHECK pending two independent experts plus "
            "tie-break/custodian."
        ),
    }


def main() -> int:
    report = audit()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Fail-closed audit for P12's stop/go frozen-menus and prior-evidence integration.

Validates, against the live tree:
- menu identity across arms (action menu and signal menu byte-identical for
  the adaptive and both one-signal arms);
- the declared inference unit (task family / domain);
- campaign scope minimums and the stop/go fail action;
- the binding prior adverse evidence (artifact SHA-256 + exact terminals,
  BROKEN verdicts verbatim, no euphemizing);
- the P12C label-honesty note;
- authority V5 preserving the landed lifecycle authority V4 exactly while
  adding only the stop/go leaf and new bindings;
- ledger and README integration markers.

This is a protocol-freeze audit. It confers no scientific authority
(scientific_authority_delta = NONE) and no external validation
(external_validation = CANNOT_CHECK).
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PAPER = ROOT / "papers/paper-12-adaptive-state-reasoning"
MENUS = PAPER / "top_tier/p12_stopgo_frozen_menus_v1.json"
MENUS_DOC = PAPER / "top_tier/P12_STOPGO_FROZEN_MENUS_V1.md"
AUTHORITY = PAPER / "P12_ACTIVE_CLAIM_AUTHORITY_V5.json"
AUTHORITY_PRIOR = PAPER / "P12_ACTIVE_CLAIM_AUTHORITY_V4.json"
LEDGER = PAPER / "CLAIM_EVIDENCE_LEDGER.md"
README = PAPER / "README.md"

P12B_ACTION_TUPLES = {(0, 0), (2, 0), (0, 2), (1, 1)}
CANONICAL_SIGNALS = [
    "S_PENDING_MULTIPLICITY",
    "S_DECLARED_MATERIALIZATION_COST",
    "S_DECLARED_SERVE_EXCHANGE_RATE",
    "S_FAMILY_DIFFICULTY_PRIOR",
]
PRIOR_BINDINGS = {
    "papers/paper-12-adaptive-state-reasoning/P12A_COMPARISON_VALIDITY_ADJUDICATION_V1.json": (
        "c57c6274c752c8be2a495e44730a4c3741be5f7f9aafb6294f14e0846331617e",
        "P12A_SUPERIORITY_AUTHORITY_WITHHELD",
    ),
    "papers/paper-12-adaptive-state-reasoning/top_tier/P12_ROBUSTNESS_STRESS_RESULT_RECEIPT_V1.md": (
        "f79e4d4c249e70e02fc6427b14d5843c41dd9ab26dc9381818d796d08f8ffd08",
        "P12_ROBUSTNESS_STRESS_V1_EXECUTED",
    ),
    "papers/paper-12-adaptive-state-reasoning/top_tier/P12_PRICE_AWARE_SUCCESSOR_RESULT_RECEIPT_V1.md": (
        "408372c2a4401907a96056ab9c1b3a137cffec32025c1f14bc3ea356703b20b2",
        "P12_PRICE_AWARE_SUCCESSOR_SUPPORTED",
    ),
}
LEDGER_MARKERS = [
    "NO ARTIFACT / LABEL WITHOUT REFERENT",
    "BINDING PRIOR / PROTOCOL-LEVEL",
    "FROZEN PROTOCOL / NO RESULTS",
]
README_MARKERS = [
    "Stop/go public-data campaign — frozen protocol (not executed)",
    "p12_stopgo_frozen_menus_v1.json",
]


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path, errors: list[str], label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"cannot parse {label}: {exc}")
        return {}
    if not isinstance(value, dict):
        errors.append(f"{label} is not a JSON object")
        return {}
    return value


def audit(
    menus_path: Path = MENUS,
    authority_path: Path = AUTHORITY,
    *,
    check_package: bool = True,
) -> dict[str, object]:
    errors: list[str] = []
    menus = _load(menus_path, errors, "frozen menus")
    authority = _load(authority_path, errors, "V5 authority")
    prior = _load(AUTHORITY_PRIOR, errors, "V4 authority")

    # --- protocol-freeze labelling -------------------------------------
    if menus.get("schema") != "ORION.P12.StopGoFrozenMenus.v1":
        errors.append("wrong menus schema")
    if menus.get("artifact_class") != "FROZEN_PROTOCOL":
        errors.append("menus artifact class must be FROZEN_PROTOCOL")
    if menus.get("results_exist") is not False:
        errors.append("menus claim results existence")
    if menus.get("campaign_executed") is not False:
        errors.append("menus claim campaign execution")

    # --- action-menu identity across arms -------------------------------
    canonical_actions = menus.get("canonical_action_menu")
    if not isinstance(canonical_actions, list) or not canonical_actions:
        errors.append("canonical action menu missing")
        canonical_actions = []
    tuples = {
        (a.get("state_construction_units"), a.get("reasoning_units"))
        for a in canonical_actions
        if isinstance(a, dict)
    }
    if tuples != P12B_ACTION_TUPLES:
        errors.append("canonical action menu drifted from the P12B four-action set")
    if any(
        (a.get("state_construction_units", 0) + a.get("reasoning_units", 0)) > 2
        for a in canonical_actions
        if isinstance(a, dict)
    ):
        errors.append("action charge exceeds the two-unit budget")
    arms = menus.get("arms")
    if not isinstance(arms, dict) or set(arms) != {
        "ADAPTIVE",
        "ONE_SIGNAL_STATE",
        "ONE_SIGNAL_REASON",
    }:
        errors.append("arm set must be exactly adaptive + two one-signal arms")
        arms = arms if isinstance(arms, dict) else {}
    for name, arm in arms.items():
        if arm.get("action_menu") != canonical_actions:
            errors.append(f"arm {name} action menu differs from canonical (identity broken)")

    # --- signal-menu identity and access rights -------------------------
    canonical_signals = menus.get("canonical_signal_menu")
    signal_ids = [
        s.get("signal_id") for s in canonical_signals if isinstance(s, dict)
    ] if isinstance(canonical_signals, list) else []
    if sorted(signal_ids) != sorted(CANONICAL_SIGNALS):
        errors.append("canonical signal menu drifted from the frozen four signals")
    if any(
        isinstance(s, dict) and s.get("pre_outcome") is not True
        for s in (canonical_signals or [])
    ):
        errors.append("non-pre-outcome signal in the menu")
    for name, arm in arms.items():
        if arm.get("signal_menu") != signal_ids:
            errors.append(f"arm {name} signal menu differs from canonical (identity broken)")
    readable = {name: (arm.get("readable_signals") or []) for name, arm in arms.items()}
    if sorted(readable.get("ADAPTIVE") or []) != sorted(CANONICAL_SIGNALS):
        errors.append("adaptive arm must read the full signal menu")
    for name in ("ONE_SIGNAL_STATE", "ONE_SIGNAL_REASON"):
        if len(readable.get(name) or []) != 1:
            errors.append(f"one-signal arm {name} must read exactly one signal")
    if readable.get("ONE_SIGNAL_STATE") == readable.get("ONE_SIGNAL_REASON"):
        errors.append("the two one-signal arms must read different signals")
    leaked = {
        signal
        for signals in readable.values()
        for signal in signals or []
        if signal not in CANONICAL_SIGNALS
    }
    if leaked:
        errors.append(f"readable signals outside the closed menu: {sorted(leaked)}")

    # --- inference unit and scope ---------------------------------------
    unit = menus.get("inference_unit") or {}
    if not isinstance(unit, dict):
        errors.append("inference unit must be an object")
        unit = {}
    if unit.get("primary") != "task_family" or unit.get("aggregation") != "domain":
        errors.append("inference unit must be task family aggregated by domain")
    for forbidden in ("generated_row", "seed", "episode", "individual_instance"):
        if forbidden not in (unit.get("forbidden_units") or []):
            errors.append(f"forbidden inference unit missing: {forbidden}")
    scope = menus.get("campaign_scope_minimums") or {}
    if not isinstance(scope, dict):
        errors.append("campaign scope must be an object")
        scope = {}
    if (scope.get("task_families") or 0) < 20:
        errors.append("campaign minimum must require >= 20 task families")
    if (scope.get("domains") or 0) < 3:
        errors.append("campaign minimum must require >= 3 domains")
    if (scope.get("model_families") or 0) < 2:
        errors.append("campaign minimum must require >= 2 model families")
    if scope.get("satisfied_by_this_artifact") is not False:
        errors.append("protocol artifact must not claim scope satisfaction")

    # --- stop/go rule ----------------------------------------------------
    gate = menus.get("stopgo_gate") or {}
    if not isinstance(gate, dict):
        errors.append("stop/go gate must be an object")
        gate = {}
    fail_action = gate.get("fail_action") or ""
    if "do not iterate until positive" not in fail_action:
        errors.append("stop/go fail action must forbid iterating until positive")
    if "preregistered protocol" not in fail_action:
        errors.append("stop/go fail action must require a new preregistered protocol")
    pass_rules = gate.get("pass_requires_all", [])
    if not isinstance(pass_rules, list) or len(pass_rules) < 4:
        errors.append("stop/go pass gate must keep all four frozen conditions")

    # --- binding prior adverse evidence ----------------------------------
    priors = menus.get("prior_adverse_evidence") or []
    if not isinstance(priors, list) or len(priors) < 3:
        errors.append("prior adverse evidence must bind the three landed adverse terminals")
        priors = [p for p in priors if isinstance(p, dict)] if isinstance(priors, list) else []
    for entry in priors:
        artifact = entry.get("artifact")
        expected = PRIOR_BINDINGS.get(artifact)
        if expected is None:
            errors.append(f"unexpected prior evidence artifact: {artifact}")
            continue
        sha, terminal = expected
        target = ROOT / artifact
        if not target.is_file():
            errors.append(f"prior evidence artifact missing: {artifact}")
        elif _sha(target) != sha:
            errors.append(f"prior evidence artifact drifted: {artifact}")
        if entry.get("terminal") != terminal:
            errors.append(f"prior evidence terminal drifted: {artifact}")
        if entry.get("sha256") != sha:
            errors.append(f"prior evidence sha declaration drifted: {artifact}")
    robustness = next(
        (e for e in priors if e.get("terminal") == "P12_ROBUSTNESS_STRESS_V1_EXECUTED"),
        {},
    )
    verdicts = robustness.get("verdicts") or {}
    if verdicts.get("price_axis") != "BROKEN" or verdicts.get("distribution_shift_axis") != "BROKEN":
        errors.append("robustness BROKEN verdicts must be carried verbatim (no euphemizing)")

    # --- P12C label honesty ----------------------------------------------
    note = menus.get("p12c_label_note") or ""
    if "No repository artifact" not in note or "none was invented" not in note:
        errors.append("P12C label-honesty note missing or softened")

    # --- protocol doc twin -------------------------------------------------
    if check_package:
        if not MENUS_DOC.is_file():
            errors.append("frozen menus protocol doc missing")
        else:
            doc = MENUS_DOC.read_text(encoding="utf-8")
            plain = doc.replace("**", "")
            if "FROZEN PROTOCOL — NO RESULTS" not in plain:
                errors.append("protocol doc must be labelled frozen-protocol-no-results")
            if "not been executed" not in plain:
                errors.append("protocol doc must state the campaign has not been executed")

    # --- authority V5 preserves V4 (lifecycle), adds only the stop/go layer -
    if authority.get("schema") != "ORION.P12.ActiveClaimAuthority.v5":
        errors.append("wrong V5 schema")
    if authority.get("paper_id") != "P12":
        errors.append("wrong paper id")
    if authority.get("active_terminal") != prior.get("active_terminal"):
        errors.append("V5 must preserve the V4 active terminal")
    if authority.get("active_claim_leaf") != prior.get("active_claim_leaf"):
        errors.append("V5 active claim leaf differs from V4")
    if authority.get("historical_boundary_leaf") != prior.get("historical_boundary_leaf"):
        errors.append("V5 historical boundary leaf differs from V4")
    if authority.get("paper_level_outcome") != prior.get("paper_level_outcome"):
        errors.append("V5 changed the paper-level outcome without new results")
    if authority.get("promotion_allowed") is not True:
        errors.append("promotion flag drifted")
    if authority.get("top_tier_submission_allowed") is not False:
        errors.append("top-tier submission gate must remain false")
    if authority.get("external_public_benchmark_status") != prior.get(
        "external_public_benchmark_status"
    ):
        errors.append("external public benchmark status must remain unchanged")
    bindings = authority.get("evidence_bindings") or {}
    prior_bindings = prior.get("evidence_bindings") or {}
    if not isinstance(bindings, dict) or not isinstance(prior_bindings, dict):
        errors.append("evidence bindings must be objects")
        bindings = bindings if isinstance(bindings, dict) else {}
        prior_bindings = prior_bindings if isinstance(prior_bindings, dict) else {}
    for name, binding in prior_bindings.items():
        if bindings.get(name) != binding:
            errors.append(f"V5 weakened or changed inherited binding: {name}")
    for forbidden in prior.get("forbidden_promotions") or []:
        if forbidden not in (authority.get("forbidden_promotions") or []):
            errors.append(f"V5 dropped a forbidden promotion: {forbidden}")
    stopgo = authority.get("stopgo_campaign_leaf") or {}
    if not isinstance(stopgo, dict):
        errors.append("stop/go leaf must be an object")
        stopgo = {}
    if stopgo.get("authority") != "FROZEN_PROTOCOL_PENDING_EXECUTION":
        errors.append("wrong stop/go authority class")
    if stopgo.get("results_exist") is not False:
        errors.append("stop/go leaf claims results")
    if stopgo.get("claim_id") != "P12.STOPGO.PUBLICDATA.V1":
        errors.append("wrong stop/go claim id")
    leaf_priors = stopgo.get("binding_prior_terminals") or []
    for _, terminal in PRIOR_BINDINGS.values():
        if terminal not in leaf_priors:
            errors.append(f"stop/go leaf missing prior terminal: {terminal}")
    leaf_note = stopgo.get("issue_1086_label_note") or ""
    if "No P12C artifact exists" not in leaf_note:
        errors.append("stop/go leaf missing the P12C no-artifact note")
    for key in ("stopgo_menus_json", "stopgo_menus_doc", "stopgo_checker"):
        binding = bindings.get(key)
        if not isinstance(binding, dict):
            errors.append(f"V5 missing stop/go binding: {key}")
            continue
        target = ROOT / binding.get("artifact", "")
        if not target.is_file():
            errors.append(f"stop/go binding target missing: {key}")
        elif _sha(target) != binding.get("sha256"):
            errors.append(f"stop/go binding sha mismatch: {key}")
    for key in ("robustness_result_receipt", "price_aware_result_receipt"):
        binding = bindings.get(key)
        if not isinstance(binding, dict):
            errors.append(f"V5 missing inherited prior-evidence binding: {key}")
            continue
        target = ROOT / binding.get("artifact", "")
        if not target.is_file():
            errors.append(f"prior-evidence binding target missing: {key}")
        elif _sha(target) != binding.get("sha256"):
            errors.append(f"prior-evidence binding sha mismatch: {key}")

    # --- ledger and README integration ------------------------------------
    if check_package:
        ledger_text = LEDGER.read_text(encoding="utf-8")
        for marker in LEDGER_MARKERS:
            if marker not in ledger_text:
                errors.append(f"ledger missing integration marker: {marker}")
        readme_text = README.read_text(encoding="utf-8")
        for marker in README_MARKERS:
            if marker not in readme_text:
                errors.append(f"README missing integration marker: {marker}")

    status = "PASS" if not errors else "FAIL"
    return {
        "status": status,
        "errors": errors,
        "scientific_authority_delta": "NONE",
        "external_validation": "CANNOT_CHECK",
        "artifact_class": "FROZEN_PROTOCOL_NO_RESULTS",
        "menus_sha256": _sha(menus_path) if menus_path.is_file() else None,
    }


def main() -> int:
    report = audit()
    encoded = json.dumps(report, indent=2, sort_keys=True)
    print(encoded)
    if re.search(r"\S", encoded) is None:
        print("audit produced an empty report", file=__import__("sys").stderr)
        return 2
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

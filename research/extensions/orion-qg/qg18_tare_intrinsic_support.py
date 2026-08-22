#!/usr/bin/env python3
"""QG-18: bind the exact TARE intrinsic support number from existing receipts.

V1 is deliberately receipt-derived: it selects the first already-serialized QG-7
fourth-regime witness, binds QG-7 C_Dplus to the exact R6P max_weight=1 family,
replays the support-2 witness, and combines the strict gap with the earned R6S
all-n support<=2 theorem. Independent primitive cap-1 brute force is owned by
qg18_generic_verify.py.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
ORION_Q = ROOT / "research/extensions/orion-q"
sys.path.insert(0, str(ORION_Q))

import max_r6p_weight2_frame_donor_closure as r6p  # noqa: E402

ISSUE = "SzeChunYiu/ORION#835"
PROTOCOL = ROOT / "development/orion-qg-regime-geometry/QG18_TARE_INTRINSIC_SUPPORT_PROTOCOL_V1.md"
QG7_PATH = ROOT / "research/extensions/orion-qg/QG7_BPRIME_COMPLETENESS_RESULTS.json"
R6S_PATH = ROOT / "research/extensions/orion-q/MAX_R6S_ALL_N_COMPOSITION_RESULTS.json"
DEFAULT_OUT = ROOT / "artifacts/orion-qg-qg18-intrinsic-support.json"
TOKEN = "ORIONQG_QG18="
QG7_DIGEST = "159d174fbb17a66aeb39a3efb53cf4c505f0a86ce8ef1dff76337d00837d152f"
POSITIVE = "QG18_TARE_KAPPA_IS_2__SUPPORT2_NECESSITY_WITNESS"


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def qg7_digest(raw: dict[str, Any]) -> str:
    unsigned = {k: v for k, v in raw.items() if k not in ("result_digest", "timing")}
    return hashlib.sha256(canonical(unsigned).encode()).hexdigest()


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=str(DEFAULT_OUT))
    args = parser.parse_args(argv)

    qg7 = json.loads(QG7_PATH.read_text())
    r6s = json.loads(R6S_PATH.read_text())
    rows = qg7.get("arm1_hostile_search", {}).get("fourth_regime_candidates_verbatim", [])
    selected = rows[0] if rows else None

    binding_errors = []
    if selected is None:
        binding_errors.append("QG7_FIRST_WITNESS_MISSING")
        selected = {}
    panel = str(selected.get("panel", ""))
    m = re.search(r"_n(\d+)$", panel)
    n = int(m.group(1)) if m else -1
    if n <= 0:
        binding_errors.append("QG7_PANEL_N_UNPARSEABLE")

    target_pairs = tuple(
        (tuple(int(x) for x in pair[0]), tuple(int(x) for x in pair[1]))
        for pair in selected.get("target_pairs", [])
    )
    production_cap1 = None
    cap1_witness = None
    support2_replay = False
    support2_cost = None
    support2_max_support = None
    if n > 0 and len(target_pairs) == 3 and selected.get("dxx_witness_verbatim"):
        cap1 = r6p.dxx_search(target_pairs, n, max_weight=1, want_witness=True)
        production_cap1 = int(cap1["C_Dxx"])
        cap1_witness = cap1["witness"]
        support2_replay = bool(r6p.verify_dxx_witness(
            target_pairs, n, selected["dxx_witness_verbatim"]))
        support2_cost = int(selected["dxx_witness_verbatim"]["C_Dxx"])
        support2_max_support = int(selected["dxx_witness_verbatim"].get("max_frame_support", -1))
    else:
        binding_errors.append("QG7_SELECTED_WITNESS_MALFORMED")

    gates = {
        "protocol_present": PROTOCOL.exists(),
        "qg7_schema": qg7.get("schema") == "ORIONQG.QG7.BprimeCompleteness.v1",
        "qg7_terminal": qg7.get("terminal") == "QG7_FOURTH_SUPPORT2_REGIME_FOUND",
        "qg7_digest_exact": qg7.get("result_digest") == QG7_DIGEST and qg7_digest(qg7) == QG7_DIGEST,
        "first_witness_frozen": selected.get("panel") == "H1_n3" and int(selected.get("local_index", -1)) == 2,
        "qg7_historical_values_control": (
            int(selected.get("C_DP", -1)) == 7
            and int(selected.get("C_Dxx", -1)) == 7
            and int(selected.get("C_Dplus", -1)) == 8
        ),
        "production_cap1_binds_qg7_dplus": production_cap1 is not None and production_cap1 == int(selected.get("C_Dplus", -1)),
        "support2_witness_replay": support2_replay,
        "support2_witness_uses_support2": support2_max_support == 2,
        "support2_strictly_beats_cap1": support2_cost is not None and production_cap1 is not None and support2_cost < production_cap1,
        "r6s_schema": r6s.get("schema") == "ORIONQ.MAXR6S.AllNComposition.v1",
        "r6s_all_gates": bool(r6s.get("gates")) and all(r6s.get("gates", {}).values()),
        "r6s_support2_parent": "DXX_EQUALS_DP_ALL_N" in str(r6s.get("authority", "")),
        "r6s_not_r6": r6s.get("r6_authority") is False and r6s.get("novelty_credit") is False,
        "protected_subject_untouched": qg7.get("reserved_stretched_n2_accessed") is False and r6s.get("reserved_stretched_n2_accessed") is False,
        "no_binding_errors": not binding_errors,
    }

    if all(gates.values()):
        terminal = POSITIVE
    elif not gates["production_cap1_binds_qg7_dplus"]:
        terminal = "QG18_CAP1_BINDING_GAP"
    elif not gates["support2_witness_replay"] or not gates["support2_strictly_beats_cap1"]:
        terminal = "QG18_SUPPORT2_WITNESS_REPLAY_FAILED"
    elif not gates["r6s_support2_parent"] or not gates["r6s_all_gates"]:
        terminal = "QG18_R6S_PARENT_BINDING_GAP"
    else:
        terminal = "QG18_CANNOT_CHECK"

    result = {
        "schema": "ORIONQG.QG18.TAREIntrinsicSupport.v1",
        "issue": ISSUE,
        "protocol": PROTOCOL.name,
        "protocol_sha256": file_sha(PROTOCOL) if PROTOCOL.exists() else None,
        "terminal": terminal,
        "claim": "kappa_TARE=2" if terminal == POSITIVE else None,
        "derivation_kind": "RECEIPT_DERIVED_COROLLARY_NOT_BLIND_DISCOVERY",
        "qg7_parent": {
            "result_digest": qg7.get("result_digest"),
            "terminal": qg7.get("terminal"),
            "selected_index": 0,
            "selected_witness_sha256": hashlib.sha256(canonical(selected).encode()).hexdigest(),
        },
        "r6s_parent": {
            "schema": r6s.get("schema"),
            "authority": r6s.get("authority"),
            "universal_support_upper_bound": 2,
        },
        "selected_witness": selected,
        "n": n,
        "support2_feasible_cost": support2_cost,
        "support2_max_frame_support": support2_max_support,
        "production_cap1_cost": production_cap1,
        "production_cap1_witness": cap1_witness,
        "strict_gap_cap1_minus_support2": (
            production_cap1 - support2_cost
            if production_cap1 is not None and support2_cost is not None else None
        ),
        "logical_implication": (
            "feasible_support2_cost<C_cap1 implies C_DP<C_cap1; R6S gives universal cap2; therefore kappa_TARE=2"
        ),
        "binding_errors": binding_errors,
        "gates": gates,
        "global_phase_boundary_complete": False,
        "novelty_authority": False,
        "r6_authority": False,
        "physical_quantum_advantage_claim": False,
        "protected_subject_read": False,
    }
    unsigned = dict(result)
    result["result_digest"] = hashlib.sha256(canonical(unsigned).encode()).hexdigest()

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(TOKEN + canonical({
        "terminal": terminal,
        "result_digest": result["result_digest"],
        "support2": support2_cost,
        "cap1": production_cap1,
        "gap": result["strict_gap_cap1_minus_support2"],
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

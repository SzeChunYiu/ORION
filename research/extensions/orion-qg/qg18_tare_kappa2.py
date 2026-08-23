#!/usr/bin/env python3
"""QG-18A: close TARE intrinsic support at kappa=2 from a protected QG-7 witness."""
from __future__ import annotations

import argparse, hashlib, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
Q = ROOT / "research/extensions/orion-q"
sys.path.insert(0, str(Q))

import max_r6m_exact_three_tare2_shared_factor_dp as r6m  # noqa: E402
import max_r6o_enlarged_tag_donor_closure as r6o  # noqa: E402
import max_r6p_weight2_frame_donor_closure as r6p  # noqa: E402

QG7 = ROOT / "research/extensions/orion-qg/QG7_BPRIME_COMPLETENESS_RESULTS.json"
R6S = Q / "MAX_R6S_ALL_N_COMPOSITION_RESULTS.json"
PROTOCOL = ROOT / "development/orion-qg-regime-geometry/QG18_TARE_KAPPA2_PROTOCOL_V1.md"
OUT = ROOT / "artifacts/orion-qg-qg18-tare-kappa2.json"
TOKEN = "ORIONQG_QG18="
TERMINAL = "QG18_TARE_KAPPA_IS_2__SUPPORT2_NECESSITY_WITNESS_MACHINE_VERIFIED"


def canonical(v):
    return json.dumps(v, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sha(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser(); ap.add_argument("--output", type=Path, default=OUT); args = ap.parse_args()
    q7 = json.loads(QG7.read_text())
    r6s = json.loads(R6S.read_text())
    rows = q7["arm1_hostile_search"]["fourth_regime_candidates_verbatim"]
    row = rows[0]
    tp = tuple((tuple(a), tuple(b)) for a, b in row["target_pairs"])
    n = 3

    # Production complete cap-1 and cap-2 families.
    cap1 = r6p.dxx_search(tp, n, max_weight=1, want_witness=True)
    cap2 = r6p.dxx_search(tp, n, max_weight=2, want_witness=True)
    tb1 = r6p._tables(n, 1)
    cap1_definition = {
        "pair_count": tb1.P,
        "expected_pair_count": 6 * n,
        "all_pairs_nonzero_anticommuting_support1": all(
            1 <= r6p.p10.wt(a) <= 1 and 1 <= r6p.p10.wt(b) <= 1 and r6p.p10.symp(a, b) == 1
            for a, b in tb1.pairs
        ),
    }

    terms = r6m._synthetic_terms(tp)
    cdp = int(r6o.dp_cost_frozen_configs(terms, n))
    dpw = r6m.exact_r6m_matching(terms, r6m._SYNTHETIC_MATCHING, n, list(range(6)))

    parent = {
        "qg7_first_row_replay_confirmed": row.get("replay_confirmed") is True,
        "qg7_recorded_values": [row.get("C_DP"), row.get("C_Dxx"), row.get("C_Dplus")],
        "r6s_authority": r6s.get("authority"),
        "r6s_gates": r6s.get("gates", {}),
    }
    gates = {
        "protocol_bound": bool(PROTOCOL.exists()),
        "qg7_first_row_replay_confirmed": parent["qg7_first_row_replay_confirmed"],
        "qg7_recorded_7_7_8": parent["qg7_recorded_values"] == [7, 7, 8],
        "cap1_definition_complete": cap1_definition["pair_count"] == 18 and cap1_definition["all_pairs_nonzero_anticommuting_support1"],
        "production_cap1_is_8": int(cap1["C_Dxx"]) == 8,
        "production_cap1_witness_verifies": r6p.verify_dxx_witness(tp, n, cap1["witness"]),
        "production_cap2_is_7": int(cap2["C_Dxx"]) == 7,
        "production_cap2_witness_verifies": r6p.verify_dxx_witness(tp, n, cap2["witness"]),
        "unrestricted_dp_is_7": cdp == 7 and int(dpw["C_R6M"]) == 7,
        "unrestricted_dp_checks": all(dpw.get("checks", {}).values()),
        "strict_support_gap": cdp < int(cap1["C_Dxx"]),
        "r6s_all_n_bound": str(r6s.get("authority", "")).startswith("MAX_R6S_ALL_N_COMPOSITION_THEOREM_MACHINE_CHECKED") and all(r6s.get("gates", {}).values()),
    }
    positive = all(gates.values())
    out = {
        "schema": "ORION.QG.QG18.TAREKappa.v1",
        "issue": "SzeChunYiu/ORION#838",
        "terminal": TERMINAL if positive else "QG18_PARENT_OR_REPLAY_BINDING_FAILED",
        "protocol_sha256": sha(PROTOCOL),
        "qg7_result_sha256": sha(QG7),
        "r6s_result_sha256": sha(R6S),
        "selected_witness": {
            "panel": row.get("panel"), "local_index": row.get("local_index"), "n": n,
            "target_pairs": row["target_pairs"], "recorded": parent["qg7_recorded_values"],
            "cap1": cap1, "cap2": cap2, "unrestricted_dp": cdp,
            "unrestricted_witness_checks": dpw.get("checks", {}),
        },
        "cap1_family_definition": cap1_definition,
        "proof": {
            "upper_bound": "R6S proves every instance has an optimum with frame support <=2",
            "lower_bound_witness": "selected admitted instance has C_DP=7 < C_cap1=8",
            "intrinsic_support_number": 2 if positive else None,
        },
        "gates": gates,
        "chemistry_sources_read": False,
        "protected_stretched_n2_read": False,
        "novelty_authority": False,
        "r6_authority": False,
        "physical_quantum_advantage_claim": False,
    }
    u = dict(out); out["result_digest"] = hashlib.sha256(canonical(u).encode()).hexdigest()
    args.output.parent.mkdir(parents=True, exist_ok=True); args.output.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(TOKEN + canonical({"terminal": out["terminal"], "result_digest": out["result_digest"], "kappa": out["proof"]["intrinsic_support_number"], "cap1": cap1["C_Dxx"], "dp": cdp}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

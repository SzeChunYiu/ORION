#!/usr/bin/env python3
"""NR-03 revival computation: P4 H3 V2.1 informedness over the frozen V2 battery.

Single targeted script (no pytest, no suites, no xdist). Executes the
pre-registered protocol in P4_H3_V21_PROTOCOL_PREREG.json: regenerates the v1
construction battery, re-runs the eleven frozen policies, checks the four
gates, computes J_CC per system and the registered bootstrap comparison.

Run:  PYTHONPATH=src python3 papers/orion-14-verified-scientific-discovery/top_tier/nr03_v21_informedness.py
"""
from __future__ import annotations

import importlib.util
import json
import random
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

HOST = REPO / "papers" / "orion-14-verified-scientific-discovery" / "host"
PUBLISHED = json.loads(
    (
        REPO
        / "papers/orion-14-verified-scientific-discovery/evidence/protected_v2/PUBLICATION_METRICS_V2.json"
    ).read_text(encoding="utf-8")
)

SEED_PRIMARY = "nr03-v21-20260823"
SEED_CHECK = "nr03-v21-seedcheck-90f1"
B = 10_000
BOOTSTRAP_SEED = 20260823

PUBLISHED_FP = {  # false promotions out of 360 hostile opportunities (published)
    "ORION": 0,
    "provenai-citation-fidelity-influence": 180,
    "deepsciverify-abstract-to-full-escalation": 210,
    "provenanceguard-style-source-routing": 210,
    "rewardhackingagents-search-contamination": 210,
    "attributionbench-multisource-attribution": 240,
    "claim-level-auditability-provenance": 240,
    "fire-iterative-retrieve-or-verify": 300,
    "citation-presence-format": 330,
    "claimbench-sciclaimhunt-scientific-evidence": 330,
    "pooled-evidence-nli-support": 330,
}


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


gen = _load("p4_nr03_generator", HOST / "generate_protected_cases.py")
baselines = _load("p4_nr03_baselines", HOST / "run_baselines.py")
baselines_v2 = _load("p4_nr03_baselines_v2", HOST / "run_baselines_v2.py")
candidate = _load("p4_nr03_candidate", HOST / "run_candidate.py")

# run_baselines.py defines RUNNERS in exactly this order (module-level tuple).
BASELINE_IDS_IN_ORDER = (
    "provenanceguard-style-source-routing",
    "attributionbench-multisource-attribution",
    "fire-iterative-retrieve-or-verify",
    "claimbench-sciclaimhunt-scientific-evidence",
    "provenai-citation-fidelity-influence",
    "rewardhackingagents-search-contamination",
    "citation-presence-format",
    "pooled-evidence-nli-support",
    "claim-level-auditability-provenance",
)
assert tuple(fn.__name__ for fn in baselines.RUNNERS) == (
    "_provenanceguard",
    "_attribution",
    "_fire",
    "_claimbench",
    "_provenai",
    "_reward",
    "_citation",
    "_pooled",
    "_auditability",
), "frozen baseline order drifted"
POLICIES: dict[str, object] = dict(
    zip(BASELINE_IDS_IN_ORDER, baselines.RUNNERS)
)
POLICIES["deepsciverify-abstract-to-full-escalation"] = baselines_v2._deepsci
POLICIES["ORION"] = candidate.evaluate_case


def battery(seed: str) -> list[dict]:
    cases = []
    ordinal = 0
    for family in gen.FAMILIES:
        for within in range(gen.COUNTS[family]):
            cases.append(
                gen._case(seed, ordinal, family, within, construction="v1")
            )
            ordinal += 1
    assert len(cases) == gen.EXPECTED_TOTAL == 420
    return cases


def cue(view: dict) -> bool:
    return view.get("evidence") == [] and view.get("retrieval_pool") == []


def run_seed(seed: str) -> dict:
    cases = battery(seed)
    golds = [case["expected_authority_terminal"] for case in cases]
    views = [case["candidate_visible"] for case in cases]
    ids = [case["case_id"] for case in cases]
    per_system: dict[str, dict[str, int]] = {}
    terminals: dict[str, list[str]] = {}
    for system_id, policy in POLICIES.items():
        terms = [
            policy(case_id, view)["authority_terminal"]
            for case_id, view in zip(ids, views)
        ]
        terminals[system_id] = terms
        per_system[system_id] = {
            "tp": sum(
                1
                for t, g in zip(terms, golds)
                if g == "CANNOT_CHECK" and t == "CANNOT_CHECK"
            ),
            "fa": sum(
                1
                for t, g in zip(terms, golds)
                if g != "CANNOT_CHECK" and t == "CANNOT_CHECK"
            ),
            "fa_on_promote_gold": sum(
                1
                for t, g in zip(terms, golds)
                if g == "PROMOTE" and t == "CANNOT_CHECK"
            ),
            "fa_on_block_gold": sum(
                1
                for t, g in zip(terms, golds)
                if g == "BLOCK" and t == "CANNOT_CHECK"
            ),
            "fp": sum(
                1
                for t, g in zip(terms, golds)
                if g != "PROMOTE" and t == "PROMOTE"
            ),
        }
    return {
        "seed": seed,
        "golds": golds,
        "terminals": terminals,
        "per_system": per_system,
        "cue_check": {
            "cue_equals_gold_cc": all(
                (cue(view) == (g == "CANNOT_CHECK"))
                for view, g in zip(views, golds)
            ),
            "non_cc_all_have_evidence_and_pool": all(
                (view.get("evidence") and view.get("retrieval_pool"))
                for view, g in zip(views, golds)
                if g != "CANNOT_CHECK"
            ),
            "gold_counts": {
                terminal: sum(1 for g in golds if g == terminal)
                for terminal in ("PROMOTE", "BLOCK", "CANNOT_CHECK")
            },
        },
    }


def j_of(tp: int, fa: int, n_pos: int, n_neg: int) -> float:
    return tp / n_pos + (n_neg - fa) / n_neg - 1.0


def paired_bootstrap(
    golds: list[str],
    terms_a: list[str],
    terms_b: list[str],
) -> dict:
    rng = random.Random(BOOTSTRAP_SEED)
    idx = list(range(len(golds)))
    diffs: list[float] = []
    draws = 0
    while len(diffs) < B:
        draws += 1
        sample = rng.choices(idx, k=len(idx))
        n_pos = sum(1 for i in sample if golds[i] == "CANNOT_CHECK")
        n_neg = len(sample) - n_pos
        if n_pos == 0 or n_neg == 0:
            continue
        tp_a = sum(
            1 for i in sample if golds[i] == "CANNOT_CHECK" and terms_a[i] == "CANNOT_CHECK"
        )
        fa_a = sum(
            1 for i in sample if golds[i] != "CANNOT_CHECK" and terms_a[i] == "CANNOT_CHECK"
        )
        tp_b = sum(
            1 for i in sample if golds[i] == "CANNOT_CHECK" and terms_b[i] == "CANNOT_CHECK"
        )
        fa_b = sum(
            1 for i in sample if golds[i] != "CANNOT_CHECK" and terms_b[i] == "CANNOT_CHECK"
        )
        diffs.append(j_of(tp_a, fa_a, n_pos, n_neg) - j_of(tp_b, fa_b, n_pos, n_neg))
    diffs.sort()
    lo = diffs[int(0.025 * (B - 1))]
    hi = diffs[int(0.975 * (B - 1))]
    return {"ci95_low": lo, "ci95_high": hi, "draws": draws}


def main() -> int:
    primary = run_seed(SEED_PRIMARY)
    check = run_seed(SEED_CHECK)

    failures: list[str] = []

    # GATE_CUE
    cc = primary["cue_check"]
    if not cc["cue_equals_gold_cc"]:
        failures.append("GATE_CUE: cue != gold CANNOT_CHECK on primary seed")
    if not cc["non_cc_all_have_evidence_and_pool"]:
        failures.append("GATE_CUE: some non-CC case lacks evidence or pool")
    if cc["gold_counts"] != {"PROMOTE": 60, "BLOCK": 330, "CANNOT_CHECK": 30}:
        failures.append(f"GATE_CUE: gold counts {cc['gold_counts']} != expected")

    # GATE_REPRO + GATE_FAMILY_DECISIONS
    for system_id, counts in primary["per_system"].items():
        if counts["tp"] != 30:
            failures.append(
                f"GATE_FAMILY_DECISIONS/GATE_REPRO: {system_id} correct-CC "
                f"{counts['tp']}/30 != 30/30"
            )
        if counts["fp"] != PUBLISHED_FP[system_id]:
            failures.append(
                f"GATE_REPRO: {system_id} FP {counts['fp']} != published "
                f"{PUBLISHED_FP[system_id]}"
            )
        published_rate = PUBLISHED["systems"][
            "ORION" if system_id == "ORION" else system_id
        ]["false_promotion_rate"]
        recomputed_rate = counts["fp"] / 360
        if abs(recomputed_rate - published_rate) > 1e-12:
            failures.append(
                f"GATE_REPRO: {system_id} FP rate {recomputed_rate} != published "
                f"{published_rate}"
            )

    # GATE_SEED
    for system_id in POLICIES:
        triple_p = (
            primary["per_system"][system_id]["tp"],
            primary["per_system"][system_id]["fa"],
            primary["per_system"][system_id]["fp"],
        )
        triple_c = (
            check["per_system"][system_id]["tp"],
            check["per_system"][system_id]["fa"],
            check["per_system"][system_id]["fp"],
        )
        if triple_p != triple_c:
            failures.append(
                f"GATE_SEED: {system_id} (tp,fa,fp) {triple_p} != seedcheck {triple_c}"
            )

    # V2.1 outcomes
    golds = primary["golds"]
    scores: dict[str, dict] = {}
    for system_id, counts in primary["per_system"].items():
        scores[system_id] = {
            **counts,
            "tpr": counts["tp"] / 30,
            "tnr": 1 - counts["fa"] / 390,
            "j_cc": j_of(counts["tp"], counts["fa"], 30, 390),
            "abstention_set_size": counts["tp"] + counts["fa"],
        }

    comparisons = {}
    for other in sorted(set(POLICIES) - {"ORION"}):
        boot = paired_bootstrap(
            golds, primary["terminals"]["ORION"], primary["terminals"][other]
        )
        comparisons[f"ORION-minus-{other}"] = {
            "delta_j": scores["ORION"]["j_cc"] - scores[other]["j_cc"],
            **boot,
        }

    registered = comparisons["ORION-minus-provenai-citation-fidelity-influence"]
    if failures:
        verdict = "CANNOT_CHECK"
    elif all(s["j_cc"] == 1.0 for s in scores.values()):
        verdict = "(b)_INSTRUMENT_NULL"
    elif registered["ci95_low"] > 0:
        verdict = "(a)_SUPPORTED"
    else:
        verdict = "(c)_DESCRIPTIVE_ONLY"

    result = {
        "schema": "orion.p4.h3.v21.results.v1",
        "protocol": "P4.H3.metric-degeneration.v21",
        "prereg_commit": "7f7f91931323cb891c323c898888fa81b86a2ac1",
        "seeds": {"primary": SEED_PRIMARY, "seedcheck": SEED_CHECK},
        "bootstrap": {"B": B, "seed": BOOTSTRAP_SEED, "method": "paired case-level percentile"},
        "gold_counts": cc["gold_counts"],
        "cue_check": cc,
        "gate_failures": failures,
        "scores": scores,
        "comparisons_orion_minus_each": comparisons,
        "registered_comparison": "ORION-minus-provenai-citation-fidelity-influence",
        "preregistered_outcome": verdict,
    }
    out = Path(__file__).resolve().parent / "P4_H3_V21_RESULTS_V1.json"
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(f"gold counts: {cc['gold_counts']}")
    print(f"cue==gold-CC: {cc['cue_equals_gold_cc']}; non-CC all populated: {cc['non_cc_all_have_evidence_and_pool']}")
    print(f"gate failures: {failures if failures else 'NONE'}")
    print(f"{'system':44s} {'TP':>3s} {'FA':>3s} {'FA|P':>4s} {'FA|B':>4s} {'FP':>3s} {'J_CC':>7s}")
    for system_id, s in sorted(scores.items(), key=lambda kv: -kv[1]["j_cc"]):
        print(
            f"{system_id:44s} {s['tp']:3d} {s['fa']:3d} {s['fa_on_promote_gold']:4d} "
            f"{s['fa_on_block_gold']:4d} {s['fp']:3d} {s['j_cc']:7.4f}"
        )
    print(f"registered delta_J ORION-provenai: {registered}")
    print(f"PREREGISTERED OUTCOME: {verdict}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

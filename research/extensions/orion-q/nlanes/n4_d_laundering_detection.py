"""ORION-Q N4-D: stronger-oracle laundering detection under representation remints.

Frozen protocol:
development/orion-q-nlane-closure/N4_D_LAUNDERING_DETECTION_PROTOCOL.md
Exact synthetic, deterministic. Hard gate: every laundering attempt that
smuggles a stronger oracle through an edit chain MUST be detected and rejected
by the full-chain checker; any miss fails the family.

Run:
    python research/extensions/orion-q/nlanes/n4_d_laundering_detection.py
"""

from __future__ import annotations

import json
import os
import random

SEED = 20260821
N_INSTANCES = 400
CLASSES = ("HONEST", "MISSING_RECEIPT", "SPOOFED_SUMMARY", "DEEP_SPLICE")
CHECKERS = ("LABEL_MATCH", "SUMMARY_TIER", "LAST_HOP_CHECK", "ORION_CHAIN_TRANSPORT")


def fresh_hash(rng: random.Random) -> int:
    return rng.randrange(2**48)


def base_chain(rng: random.Random, length: int, t_max: int) -> list[dict]:
    """Honest hop list: consistent hashes, receipts, tiers <= t_max."""
    hops = []
    prev = fresh_hash(rng)
    for _ in range(length):
        out = fresh_hash(rng)
        hops.append(
            {
                "receipt": {
                    "input_hash": prev,
                    "output_hash": out,
                    "tier_used": rng.randint(0, t_max),
                }
            }
        )
        prev = out
    return hops


def generate_instance(cls: str, rng: random.Random) -> dict:
    t_max = rng.choice([1, 2])
    length = rng.randint(3, 6) if cls == "DEEP_SPLICE" else rng.randint(2, 6)
    hops = base_chain(rng, length, t_max)

    if cls == "HONEST":
        pass
    elif cls == "MISSING_RECEIPT":
        # Interior hop loses its receipt entirely (never the final hop).
        k = rng.randint(0, length - 2)
        hops[k]["receipt"] = None
    elif cls == "SPOOFED_SUMMARY":
        # One hop truly used a stronger oracle; summary will report min not max.
        k = rng.randint(0, length - 1)
        hops[k]["receipt"]["tier_used"] = t_max + 1
    elif cls == "DEEP_SPLICE":
        # Interior hash-chain break: spliced artifact, tiers all look fine.
        k = rng.randint(1, length - 2)
        hops[k]["receipt"]["input_hash"] = fresh_hash(rng)
    else:
        raise ValueError(cls)

    tiers = [h["receipt"]["tier_used"] for h in hops if h["receipt"] is not None]
    if cls == "SPOOFED_SUMMARY":
        summary_tier = min(tiers)
    else:
        summary_tier = max(tiers) if tiers else 0
    return {
        "class": cls,
        "t_max": t_max,
        "length": length,
        "hops": hops,
        "label_matches": True,  # laundering always presents a matching label
        "summary_max_tier": summary_tier,
        "truth_accept": cls == "HONEST",
    }


def check(checker: str, inst: dict) -> bool:
    """True = accept."""
    hops = inst["hops"]
    t_max = inst["t_max"]
    if checker == "LABEL_MATCH":
        return inst["label_matches"]
    if checker == "SUMMARY_TIER":
        return inst["label_matches"] and inst["summary_max_tier"] <= t_max
    if checker == "LAST_HOP_CHECK":
        if not inst["label_matches"]:
            return False
        last = hops[-1]["receipt"]
        if last is None or last["tier_used"] > t_max:
            return False
        if len(hops) >= 2:
            prev = hops[-2]["receipt"]
            if prev is not None and last["input_hash"] != prev["output_hash"]:
                return False
        return True
    if checker == "ORION_CHAIN_TRANSPORT":
        if not inst["label_matches"]:
            return False
        prev_out = None
        for hop in hops:
            receipt = hop["receipt"]
            if receipt is None:
                return False
            if receipt["tier_used"] > t_max:
                return False
            if prev_out is not None and receipt["input_hash"] != prev_out:
                return False
            prev_out = receipt["output_hash"]
        return True
    raise ValueError(checker)


def main() -> None:
    rng = random.Random(SEED)
    n_honest = N_INSTANCES // 2
    n_per_launder = (N_INSTANCES - n_honest) // 3
    plan = (
        ["HONEST"] * n_honest
        + ["MISSING_RECEIPT"] * n_per_launder
        + ["SPOOFED_SUMMARY"] * n_per_launder
        + ["DEEP_SPLICE"] * (N_INSTANCES - n_honest - 2 * n_per_launder)
    )
    rng.shuffle(plan)
    instances = [generate_instance(cls, rng) for cls in plan]

    per_checker = {}
    for checker in CHECKERS:
        tp = fp = fn = tn = 0
        per_class_caught = {c: 0 for c in CLASSES if c != "HONEST"}
        per_class_total = {c: 0 for c in CLASSES if c != "HONEST"}
        for inst in instances:
            accepted = check(checker, inst)
            if inst["truth_accept"]:
                if accepted:
                    tn += 1
                else:
                    fp += 1
            else:
                per_class_total[inst["class"]] += 1
                if accepted:
                    fn += 1
                else:
                    tp += 1
                    per_class_caught[inst["class"]] += 1
        n_launder = tp + fn
        per_checker[checker] = {
            "recall_on_laundering": tp / n_launder,
            "false_positive_rate_on_honest": fp / (fp + tn),
            "accuracy": (tp + tn) / N_INSTANCES,
            "per_class_recall": {
                c: per_class_caught[c] / per_class_total[c] for c in per_class_total
            },
        }

    orion = per_checker["ORION_CHAIN_TRANSPORT"]
    summ = per_checker["SUMMARY_TIER"]
    gates = {
        "G1_orion_full_detection_and_zero_fpr": (
            orion["recall_on_laundering"] == 1.0
            and orion["false_positive_rate_on_honest"] == 0.0
            and all(v == 1.0 for v in orion["per_class_recall"].values())
        ),
        "G2_label_match_blind": per_checker["LABEL_MATCH"]["recall_on_laundering"]
        == 0.0,
        "G3_summary_spoof_effective": (
            summ["recall_on_laundering"] < 1.0
            and (1.0 - summ["per_class_recall"]["SPOOFED_SUMMARY"]) >= 0.9
            and (1.0 - summ["per_class_recall"]["DEEP_SPLICE"]) >= 0.9
        ),
        "G4_deep_splice_evades_last_hop": per_checker["LAST_HOP_CHECK"][
            "per_class_recall"
        ]["DEEP_SPLICE"]
        < 0.2,
    }
    if not gates["G2_label_match_blind"] or not gates[
        "G3_summary_spoof_effective"
    ] or not gates["G4_deep_splice_evades_last_hop"]:
        terminal = "N4_D_WORLD_INVALID"
    elif gates["G1_orion_full_detection_and_zero_fpr"]:
        terminal = "N4_D_CHAIN_TRANSPORT_LAUNDERING_DETECTION_SUPPORTED__EXACT_SYNTHETIC"
    else:
        terminal = "N4_D_CHAIN_TRANSPORT_INCOMPLETE"

    class_counts = {c: plan.count(c) for c in CLASSES}
    result = {
        "schema": "ORIONQ.N4D.StrongerOracleLaunderingDetection.v1",
        "issue": 677,
        "family": "5_stronger_oracle_laundering (family 3 remint transport as vector)",
        "protocol": (
            "development/orion-q-nlane-closure/N4_D_LAUNDERING_DETECTION_PROTOCOL.md"
        ),
        "seed": SEED,
        "instances": N_INSTANCES,
        "class_counts": class_counts,
        "checkers": per_checker,
        "gates": gates,
        "terminal": terminal,
        "interpretation": {
            "authority": (
                "exact-synthetic-bounded; no cryptographic security claim; no "
                "real-adversary claim; no P10/novelty; hashes are seeded "
                "integers, not digests"
            ),
            "claim_boundary": (
                "Completeness of full-chain checking holds only in this world "
                "where per-hop receipts cannot be forged consistently "
                "end-to-end; family 3 remint transport is exercised only as "
                "the laundering vector, not independently closed."
            ),
            "p10_authorized": False,
            "novelty_authorized": False,
        },
    }
    print(
        "ORIONQ_N4_D_LAUNDERING="
        + json.dumps(result, sort_keys=True, separators=(",", ":"))
    )
    pretty = json.dumps(result, indent=2, sort_keys=True)
    print(pretty)
    out_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "N4_D_LAUNDERING_DETECTION_RESULTS.json",
    )
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(pretty + "\n")


if __name__ == "__main__":
    main()

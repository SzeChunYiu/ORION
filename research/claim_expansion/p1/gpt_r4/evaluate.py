from __future__ import annotations

import importlib.util
import json
import random
from collections import Counter, defaultdict
from pathlib import Path
from typing import Mapping

ROOT = Path(__file__).resolve().parent
PLAN = json.loads((ROOT / "MATCHED_PAIR_PLAN_V1.json").read_text())
R2_ROOT = ROOT.parent / "gpt_r2"
R2_PROTOCOL = json.loads((R2_ROOT / "PROTOCOL_V1.json").read_text())

_spec = importlib.util.spec_from_file_location("p1_u_r2_policy_for_r4", R2_ROOT / "policy.py")
assert _spec and _spec.loader
POLICY = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(POLICY)

HIGH_LEVEL = {"OBJECTIVE_OR_MODEL_CLASS", "PROBLEM_BOUNDARY"}
LOW_LEVEL = {
    "SEARCH_OR_EVIDENCE",
    "REPRESENTATION_OR_INTERFACE",
    "IMPLEMENTATION_OR_ENVIRONMENT",
    "MEASUREMENT_OR_EVALUATOR",
}
SUBSTANTIVE = LOW_LEVEL | HIGH_LEVEL
CONTROL = "NO_HIGH_LEVEL_REFORMULATION"
UNRESOLVED = "UNRESOLVED"
ALL_GOLD = set(R2_PROTOCOL["classes"]) | {UNRESOLVED}
REQUIRED_PROBES = set(R2_PROTOCOL["probes"])
QUERY_MAP = {q["id"]: q for q in PLAN["queries"]}
PAIR_QUERIES = {qid: q for qid, q in QUERY_MAP.items() if q["class"] in SUBSTANTIVE}
UNRES_QUERIES = {qid: q for qid, q in QUERY_MAP.items() if q["class"] == UNRESOLVED}


class ProbeGate(Mapping[str, str]):
    def __init__(self, hidden: Mapping[str, str]):
        if set(hidden) != REQUIRED_PROBES:
            raise ValueError("probe set mismatch")
        self._hidden = dict(hidden)
        self.revealed: list[tuple[str, str]] = []

    def __getitem__(self, key: str) -> str:
        if key not in self._hidden:
            raise KeyError(key)
        value = self._hidden[key]
        self.revealed.append((key, value))
        return value

    def __iter__(self):
        raise RuntimeError("policy may not enumerate evaluator-owned probe outcomes")

    def __len__(self) -> int:
        return len(self._hidden)


def _validate_episode(ep: Mapping[str, object], *, expected_gold: str) -> None:
    for key in PLAN["case_schema"]["episode_required"]:
        if key not in ep:
            raise ValueError(f"episode missing field {key}")
    if str(ep["gold_class"]) != expected_gold:
        raise ValueError(f"episode {ep['id']} gold mismatch: expected {expected_gold}")
    if str(ep["gold_class"]) not in ALL_GOLD:
        raise ValueError(f"episode {ep['id']} invalid gold")
    if set(ep["probes"]) != REQUIRED_PROBES:
        raise ValueError(f"episode {ep['id']} probe set mismatch")
    allowed = set(R2_PROTOCOL["probe_observations"])
    if any(v not in allowed for v in ep["probes"].values()):
        raise ValueError(f"episode {ep['id']} invalid probe observation")
    if len(str(ep["dossier"]).split()) > int(PLAN["case_schema"]["dossier_max_words"]):
        raise ValueError(f"episode {ep['id']} dossier too long")


def _validate_pair(row: Mapping[str, object]) -> None:
    for key in PLAN["case_schema"]["pair_required"]:
        if key not in row:
            raise ValueError(f"pair missing field {key}")
    qid = str(row["query_id"])
    if qid not in PAIR_QUERIES:
        raise ValueError(f"pair {row['pair_id']} unknown substantive query")
    expected_class = str(PAIR_QUERIES[qid]["class"])
    if str(row["adverse_class"]) != expected_class:
        raise ValueError(f"pair {row['pair_id']} adverse class/query mismatch")
    if int(row["source_year"]) != int(PLAN["primary_year"]):
        raise ValueError(f"pair {row['pair_id']} wrong source year")
    rank = int(row["source_rank"])
    if rank < 1 or rank > int(PLAN["max_rank_scanned_per_query"]):
        raise ValueError(f"pair {row['pair_id']} invalid source rank")
    if not str(row["source_id"]).strip() or not str(row["source_url"]).strip():
        raise ValueError(f"pair {row['pair_id']} source identity missing")
    if not str(row["actual_domain"]).strip():
        raise ValueError(f"pair {row['pair_id']} domain missing")
    if not isinstance(row["pair_evidence"], Mapping) or not row["pair_evidence"]:
        raise ValueError(f"pair {row['pair_id']} pair evidence missing")
    _validate_episode(row["adverse"], expected_gold=expected_class)
    _validate_episode(row["control"], expected_gold=CONTROL)
    if str(row["adverse"]["id"]) == str(row["control"]["id"]):
        raise ValueError(f"pair {row['pair_id']} duplicate episode id")


def _validate_unresolved(row: Mapping[str, object]) -> None:
    for key in PLAN["case_schema"]["unresolved_required"]:
        if key not in row:
            raise ValueError(f"unresolved missing field {key}")
    qid = str(row["query_id"])
    if qid not in UNRES_QUERIES:
        raise ValueError(f"unresolved {row['id']} unknown query")
    if int(row["source_year"]) != int(PLAN["primary_year"]):
        raise ValueError(f"unresolved {row['id']} wrong source year")
    rank = int(row["source_rank"])
    if rank < 1 or rank > int(PLAN["max_rank_scanned_per_query"]):
        raise ValueError(f"unresolved {row['id']} invalid source rank")
    if not str(row["source_id"]).strip() or not str(row["source_url"]).strip():
        raise ValueError(f"unresolved {row['id']} source identity missing")
    if not str(row["actual_domain"]).strip():
        raise ValueError(f"unresolved {row['id']} domain missing")
    if str(row["gold_class"]) != UNRESOLVED:
        raise ValueError(f"unresolved {row['id']} gold must be UNRESOLVED")
    if set(row["probes"]) != REQUIRED_PROBES:
        raise ValueError(f"unresolved {row['id']} probe set mismatch")
    allowed = set(R2_PROTOCOL["probe_observations"])
    if any(v not in allowed for v in row["probes"].values()):
        raise ValueError(f"unresolved {row['id']} invalid probe observation")
    if len(str(row["dossier"]).split()) > int(PLAN["case_schema"]["dossier_max_words"]):
        raise ValueError(f"unresolved {row['id']} dossier too long")
    if not isinstance(row["admission_evidence"], Mapping) or not row["admission_evidence"]:
        raise ValueError(f"unresolved {row['id']} admission evidence missing")


def validate_acquisition(
    pairs: list[Mapping[str, object]],
    unresolved: list[Mapping[str, object]],
    dispositions: list[Mapping[str, object]],
) -> dict[str, object]:
    for row in pairs:
        _validate_pair(row)
    for row in unresolved:
        _validate_unresolved(row)

    pair_ids = [str(r["pair_id"]) for r in pairs]
    if len(pair_ids) != len(set(pair_ids)):
        raise ValueError("duplicate pair id")
    pair_qids = [str(r["query_id"]) for r in pairs]
    if len(pair_qids) != len(set(pair_qids)):
        raise ValueError("at most one pair per query")
    unresolved_qids = [str(r["query_id"]) for r in unresolved]
    if len(unresolved_qids) != len(set(unresolved_qids)):
        raise ValueError("at most one unresolved case per query")

    source_ids = [str(r["source_id"]) for r in pairs] + [str(r["source_id"]) for r in unresolved]
    if len(source_ids) != len(set(source_ids)):
        raise ValueError("all primary source identities must be disjoint")

    episode_ids = []
    for r in pairs:
        episode_ids.extend([str(r["adverse"]["id"]), str(r["control"]["id"])])
    episode_ids.extend(str(r["id"]) for r in unresolved)
    if len(episode_ids) != len(set(episode_ids)):
        raise ValueError("episode ids must be unique")

    disposition_map: dict[str, Mapping[str, object]] = {}
    for d in dispositions:
        qid = str(d.get("query_id", ""))
        if qid not in QUERY_MAP:
            raise ValueError(f"unknown disposition query id {qid}")
        if qid in disposition_map:
            raise ValueError(f"duplicate disposition {qid}")
        status = str(d.get("status", ""))
        if status not in {"ADMITTED", "NO_QUALIFYING_SOURCE"}:
            raise ValueError(f"invalid disposition status {status}")
        returned = int(d.get("results_returned", -1))
        scanned = int(d.get("results_scanned", -1))
        if returned < 0 or scanned < 0 or scanned > int(PLAN["max_rank_scanned_per_query"]):
            raise ValueError(f"invalid result counts for {qid}")
        if not isinstance(d.get("skipped", []), list):
            raise ValueError(f"skipped log must be list for {qid}")
        disposition_map[qid] = d

    expected_qids = set(QUERY_MAP)
    all_dispositions = set(disposition_map) == expected_qids
    all_admitted = all(
        qid in disposition_map and str(disposition_map[qid]["status"]) == "ADMITTED"
        for qid in expected_qids
    )

    pair_by_qid = {str(r["query_id"]): r for r in pairs}
    unresolved_by_qid = {str(r["query_id"]): r for r in unresolved}
    linkage_ok = True
    linkage_errors: list[str] = []
    for qid, q in QUERY_MAP.items():
        d = disposition_map.get(qid)
        if d is None:
            linkage_ok = False
            linkage_errors.append(f"missing disposition {qid}")
            continue
        if q["class"] in SUBSTANTIVE:
            obj = pair_by_qid.get(qid)
        else:
            obj = unresolved_by_qid.get(qid)
        if str(d["status"]) == "ADMITTED" and obj is None:
            linkage_ok = False
            linkage_errors.append(f"{qid} admitted without source object")
            continue
        if str(d["status"]) == "NO_QUALIFYING_SOURCE" and obj is not None:
            linkage_ok = False
            linkage_errors.append(f"{qid} no-source but source object exists")
            continue
        if obj is not None:
            if str(d.get("selected_source_id", "")) != str(obj["source_id"]):
                linkage_ok = False
                linkage_errors.append(f"{qid} source id mismatch")
            if int(d.get("selected_rank", -1)) != int(obj["source_rank"]):
                linkage_ok = False
                linkage_errors.append(f"{qid} source rank mismatch")

    class_counts = Counter(str(r["adverse_class"]) for r in pairs)
    class_balance = all(class_counts.get(cls, 0) == int(PLAN["corpus_requirements"]["required_pairs_per_substantive_class"]) for cls in sorted(SUBSTANTIVE))
    n_domains = len({str(r["actual_domain"]) for r in pairs} | {str(r["actual_domain"]) for r in unresolved})
    requirements = PLAN["corpus_requirements"]
    checks = {
        "all_query_dispositions": all_dispositions,
        "all_queries_admitted": all_admitted,
        "disposition_source_linkage": linkage_ok,
        "required_pair_sources": len(pairs) == int(requirements["required_pair_sources"]),
        "required_pairs_per_class": class_balance,
        "required_unresolved_sources": len(unresolved) == int(requirements["required_unresolved_sources"]),
        "required_total_sources": len(source_ids) == int(requirements["required_total_sources"]),
        "required_total_episodes": len(episode_ids) == int(requirements["required_total_episodes"]),
        "minimum_actual_domains": n_domains >= int(requirements["minimum_actual_domains"]),
    }
    return {
        "complete": all(checks.values()),
        "checks": checks,
        "n_pairs": len(pairs),
        "n_unresolved": len(unresolved),
        "n_sources": len(source_ids),
        "n_episodes": len(episode_ids),
        "n_domains": n_domains,
        "pair_class_counts": dict(sorted(class_counts.items())),
        "missing_dispositions": sorted(expected_qids - set(disposition_map)),
        "linkage_errors": linkage_errors,
    }


def _visible_episode(ep: Mapping[str, object]) -> tuple[dict[str, object], ProbeGate]:
    gate = ProbeGate(ep["probes"])
    return {"dossier": str(ep["dossier"]), "probes": gate}, gate


def _run_policy(policy_name: str, ep: Mapping[str, object]) -> dict[str, object]:
    visible, gate = _visible_episode(ep)
    if policy_name == "B0_NO_REFORMULATION":
        result = POLICY.no_reformulation_policy(visible)
    elif policy_name == "B1_ALWAYS_ESCALATE":
        result = POLICY.always_escalate_policy(visible)
    elif policy_name == "B2_IMMEDIATE_VOI":
        result = POLICY.donor_complete_policy(visible, horizon=1)
    elif policy_name == "B3_HORIZON2_DONOR_COMPLETE":
        result = POLICY.donor_complete_policy(visible, horizon=2)
    elif policy_name == "ORION_R2":
        result = POLICY.orion_r2_policy(visible)
    else:
        raise KeyError(policy_name)
    trace_pairs = [(str(t["probe"]), str(t["observation"])) for t in result["trace"]]
    if gate.revealed != trace_pairs:
        raise AssertionError(f"hidden probe access mismatch on {ep['id']} for {policy_name}")
    if int(result["cost"]) != len(gate.revealed) or int(result["cost"]) > int(R2_PROTOCOL["budget"]):
        raise AssertionError(f"probe cost mismatch on {ep['id']} for {policy_name}")
    gold = str(ep["gold_class"])
    choice = str(result["choice"])
    return {
        "choice": choice,
        "grs": int(choice == gold),
        "false_high_level": int(choice in HIGH_LEVEL and gold not in HIGH_LEVEL),
        "harmful_lower_level_skip": int(choice in HIGH_LEVEL and gold in LOW_LEVEL),
        "false_resolution_of_unresolved": int(gold == UNRESOLVED and choice != UNRESOLVED),
        "cost": int(result["cost"]),
        "trace": result["trace"],
    }


def _mean(xs: list[float]) -> float:
    return sum(xs) / len(xs) if xs else 0.0


def _bootstrap(diffs: list[float], *, n_rep: int, seed: int, interval: float) -> tuple[float, float]:
    rng = random.Random(seed)
    n = len(diffs)
    stats = []
    for _ in range(n_rep):
        stats.append(sum(diffs[rng.randrange(n)] for _ in range(n)) / n)
    stats.sort()
    alpha = 1.0 - interval
    return (
        stats[max(0, int((alpha / 2) * n_rep))],
        stats[min(n_rep - 1, int((1 - alpha / 2) * n_rep) - 1)],
    )


def evaluate(
    pairs: list[Mapping[str, object]],
    unresolved: list[Mapping[str, object]],
    dispositions: list[Mapping[str, object]],
) -> dict[str, object]:
    acquisition = validate_acquisition(pairs, unresolved, dispositions)
    if not acquisition["complete"]:
        return {
            "schema": "P1U.MatchedPair.Result.v1",
            "acquisition": acquisition,
            "policy_outcomes_generated": False,
            "terminal": "P1_R4_CANNOT_CHECK_MATCHED_SOURCE_UNIVERSE",
        }

    policy_names = [
        "B0_NO_REFORMULATION",
        "B1_ALWAYS_ESCALATE",
        "B2_IMMEDIATE_VOI",
        "B3_HORIZON2_DONOR_COMPLETE",
        "ORION_R2",
    ]

    episode_rows = []
    pair_rows = []
    for pair in pairs:
        outcomes = {}
        for name in policy_names:
            adverse_out = _run_policy(name, pair["adverse"])
            control_out = _run_policy(name, pair["control"])
            outcomes[name] = {
                "adverse": adverse_out,
                "control": control_out,
                "pair_selective_success": int(adverse_out["grs"] == 1 and control_out["grs"] == 1),
            }
            episode_rows.extend([
                {
                    "id": pair["adverse"]["id"],
                    "pair_id": pair["pair_id"],
                    "member": "adverse",
                    "actual_domain": pair["actual_domain"],
                    "gold_class": pair["adverse"]["gold_class"],
                    "policy": name,
                    "outcome": adverse_out,
                },
                {
                    "id": pair["control"]["id"],
                    "pair_id": pair["pair_id"],
                    "member": "control",
                    "actual_domain": pair["actual_domain"],
                    "gold_class": pair["control"]["gold_class"],
                    "policy": name,
                    "outcome": control_out,
                },
            ])
        pair_rows.append({
            "pair_id": pair["pair_id"],
            "adverse_class": pair["adverse_class"],
            "actual_domain": pair["actual_domain"],
            "source_id": pair["source_id"],
            "outcomes": outcomes,
        })

    for row in unresolved:
        for name in policy_names:
            episode_rows.append({
                "id": row["id"],
                "pair_id": None,
                "member": "unresolved",
                "actual_domain": row["actual_domain"],
                "gold_class": row["gold_class"],
                "policy": name,
                "outcome": _run_policy(name, row),
            })

    summary = {}
    for name in policy_names:
        rows = [r for r in episode_rows if r["policy"] == name]
        summary[name] = {
            "grs": _mean([r["outcome"]["grs"] for r in rows]),
            "false_high_level_rate": _mean([r["outcome"]["false_high_level"] for r in rows]),
            "harmful_lower_level_skips": sum(r["outcome"]["harmful_lower_level_skip"] for r in rows),
            "false_resolution_of_unresolved": sum(r["outcome"]["false_resolution_of_unresolved"] for r in rows),
            "mean_probe_cost": _mean([r["outcome"]["cost"] for r in rows]),
            "pair_selective_success": _mean([p["outcomes"][name]["pair_selective_success"] for p in pair_rows]),
            "harmful_control_high_escalations": sum(p["outcomes"][name]["control"]["false_high_level"] for p in pair_rows),
        }

    primary = "B3_HORIZON2_DONOR_COMPLETE"
    episode_diffs = []
    domain_diffs: dict[str, list[float]] = defaultdict(list)
    for pair in pairs:
        for member in ("adverse", "control"):
            o = _run_policy("ORION_R2", pair[member])
            b = _run_policy(primary, pair[member])
            diff = o["grs"] - b["grs"]
            episode_diffs.append(diff)
            domain_diffs[str(pair["actual_domain"])].append(diff)
    for row in unresolved:
        o = _run_policy("ORION_R2", row)
        b = _run_policy(primary, row)
        diff = o["grs"] - b["grs"]
        episode_diffs.append(diff)
        domain_diffs[str(row["actual_domain"])].append(diff)

    episode_mean_diff = _mean(episode_diffs)
    r2_cfg = R2_PROTOCOL["decision_rule"]
    episode_lo, episode_hi = _bootstrap(
        episode_diffs,
        n_rep=int(r2_cfg["paired_bootstrap_replicates"]),
        seed=int(r2_cfg["paired_bootstrap_seed"]),
        interval=float(r2_cfg["stability_interval"]),
    )
    domain_mean_diffs = {d: _mean(v) for d, v in sorted(domain_diffs.items())}

    pair_diffs = [
        p["outcomes"]["ORION_R2"]["pair_selective_success"] - p["outcomes"][primary]["pair_selective_success"]
        for p in pair_rows
    ]
    pair_mean_diff = _mean(pair_diffs)
    r4_cfg = PLAN["decision_rule"]
    pair_lo, pair_hi = _bootstrap(
        pair_diffs,
        n_rep=int(r4_cfg["pair_bootstrap_replicates"]),
        seed=int(r4_cfg["pair_bootstrap_seed"]),
        interval=float(r4_cfg["pair_stability_interval"]),
    )

    by_class: dict[str, list[float]] = defaultdict(list)
    for p, diff in zip(pair_rows, pair_diffs):
        by_class[str(p["adverse_class"])].append(diff)
    class_pair_diffs = {c: _mean(v) for c, v in sorted(by_class.items())}
    nonnegative_classes = sum(v >= 0.0 for v in class_pair_diffs.values())

    orion = summary["ORION_R2"]
    b3 = summary[primary]
    checks = {
        "episode_paired_margin": episode_mean_diff >= float(r2_cfg["paired_grs_margin"]),
        "episode_stability_lower_positive": episode_lo > 0.0,
        "domain_noninferiority": all(v >= float(r2_cfg["domain_noninferiority_floor"]) for v in domain_mean_diffs.values()),
        "unnecessary_high_level_guard": orion["false_high_level_rate"] <= b3["false_high_level_rate"] and orion["false_high_level_rate"] <= float(r2_cfg["max_orion_false_unnecessary_high_level_rate"]),
        "zero_lower_level_skip": orion["harmful_lower_level_skips"] <= int(r2_cfg["harmful_lower_level_skip_tolerance"]),
        "zero_false_unresolved_resolution": orion["false_resolution_of_unresolved"] <= int(r2_cfg["false_resolution_of_unresolved_tolerance"]),
        "pair_selective_margin": pair_mean_diff >= float(r4_cfg["pair_selective_margin"]),
        "pair_stability_lower_positive": pair_lo > 0.0,
        "zero_harmful_control_high_escalation": orion["harmful_control_high_escalations"] == 0,
        "minimum_nonnegative_substantive_classes": nonnegative_classes >= int(r4_cfg["minimum_nonnegative_substantive_classes"]),
        "substantive_class_floor": all(v >= float(r4_cfg["substantive_class_floor"]) for v in class_pair_diffs.values()),
    }
    terminal = (
        "P1_R4_PRIMARY_PASS_PENDING_2019_REPLICATION"
        if all(checks.values())
        else "P1_R4_PRIMARY_NOT_SUPPORTED"
    )
    return {
        "schema": "P1U.MatchedPair.Result.v1",
        "acquisition": acquisition,
        "policy_outcomes_generated": True,
        "summary": summary,
        "episode_orion_minus_b3_grs": episode_mean_diff,
        "episode_bootstrap_95_stability": [episode_lo, episode_hi],
        "domain_differences": domain_mean_diffs,
        "pair_orion_minus_b3_selective_success": pair_mean_diff,
        "pair_bootstrap_95_stability": [pair_lo, pair_hi],
        "substantive_class_pair_differences": class_pair_diffs,
        "checks": checks,
        "terminal": terminal,
        "pair_rows": pair_rows,
    }


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("pairs", type=Path)
    parser.add_argument("unresolved", type=Path)
    parser.add_argument("dispositions", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    result = evaluate(
        json.loads(args.pairs.read_text()),
        json.loads(args.unresolved.read_text()),
        json.loads(args.dispositions.read_text()),
    )
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.write_text(text)
    print(text, end="")


if __name__ == "__main__":
    main()

from __future__ import annotations

import importlib.util
import json
import random
from collections import Counter, defaultdict
from pathlib import Path
from typing import Mapping

ROOT = Path(__file__).resolve().parent
PLAN = json.loads((ROOT / "SOURCE_UNIVERSE_PLAN_V1.json").read_text())
R2_ROOT = ROOT.parent / "gpt_r2"
R2_PROTOCOL = json.loads((R2_ROOT / "PROTOCOL_V1.json").read_text())

_spec = importlib.util.spec_from_file_location("p1_u_r2_policy_for_r3", R2_ROOT / "policy.py")
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
ALL_GOLD = set(R2_PROTOCOL["classes"]) | {R2_PROTOCOL["unresolved_label"]}
REQUIRED_PROBES = set(R2_PROTOCOL["probes"])
QUERY_MAP = {q["id"]: q for q in PLAN["queries"]}
ALLOWED_DISPOSITIONS = {"ADMITTED", "NO_QUALIFYING_SOURCE"}


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


def _validate_case(case: Mapping[str, object]) -> None:
    required = set(PLAN["case_schema"]["required"])
    missing = required - set(case)
    if missing:
        raise ValueError(f"case missing fields: {sorted(missing)}")
    if str(case["query_id"]) not in QUERY_MAP:
        raise ValueError(f"unknown query id: {case['query_id']}")
    expected_query_class = str(QUERY_MAP[str(case["query_id"])]["class"])
    if str(case["query_class"]) != expected_query_class:
        raise ValueError(f"query class mismatch for {case['query_id']}")
    if int(case["source_year"]) != int(PLAN["primary_year"]):
        raise ValueError(f"case {case['id']} source year is not frozen primary year")
    rank = int(case["source_rank"])
    if rank < 1 or rank > int(PLAN["max_rank_scanned_per_query"]):
        raise ValueError(f"case {case['id']} invalid source rank")
    if str(case["gold_class"]) not in ALL_GOLD:
        raise ValueError(f"invalid gold class: {case['gold_class']}")
    if set(case["probes"]) != REQUIRED_PROBES:
        raise ValueError(f"case {case['id']} probe set mismatch")
    allowed_obs = set(R2_PROTOCOL["probe_observations"])
    if any(obs not in allowed_obs for obs in case["probes"].values()):
        raise ValueError(f"case {case['id']} has invalid probe observation")
    if len(str(case["dossier"]).split()) > int(PLAN["case_schema"]["dossier_max_words"]):
        raise ValueError(f"case {case['id']} dossier too long")
    if not str(case["actual_domain"]).strip():
        raise ValueError(f"case {case['id']} actual domain missing")
    if not str(case["source_id"]).strip() or not str(case["source_url"]).strip():
        raise ValueError(f"case {case['id']} source identity missing")
    evidence = case["admission_evidence"]
    if not isinstance(evidence, Mapping) or not evidence:
        raise ValueError(f"case {case['id']} admission evidence missing")


def validate_acquisition(
    cases: list[Mapping[str, object]], dispositions: list[Mapping[str, object]]
) -> dict[str, object]:
    for case in cases:
        _validate_case(case)

    case_ids = [str(c["id"]) for c in cases]
    if len(case_ids) != len(set(case_ids)):
        raise ValueError("duplicate case id")
    source_ids = [str(c["source_id"]) for c in cases]
    if len(source_ids) != len(set(source_ids)):
        raise ValueError("source identities must be unique")
    admitted_query_ids = [str(c["query_id"]) for c in cases]
    if len(admitted_query_ids) != len(set(admitted_query_ids)):
        raise ValueError("at most one case may be admitted per query")

    disposition_map: dict[str, Mapping[str, object]] = {}
    for row in dispositions:
        qid = str(row.get("query_id", ""))
        if qid not in QUERY_MAP:
            raise ValueError(f"unknown disposition query id: {qid}")
        if qid in disposition_map:
            raise ValueError(f"duplicate disposition for {qid}")
        status = str(row.get("status", ""))
        if status not in ALLOWED_DISPOSITIONS:
            raise ValueError(f"invalid disposition status for {qid}: {status}")
        if int(row.get("results_returned", -1)) < 0:
            raise ValueError(f"results_returned missing for {qid}")
        scanned = int(row.get("results_scanned", -1))
        if scanned < 0 or scanned > int(PLAN["max_rank_scanned_per_query"]):
            raise ValueError(f"invalid results_scanned for {qid}")
        skipped = row.get("skipped", [])
        if not isinstance(skipped, list):
            raise ValueError(f"skipped log must be a list for {qid}")
        disposition_map[qid] = row

    expected_queries = set(QUERY_MAP)
    observed_dispositions = set(disposition_map)
    all_dispositions = observed_dispositions == expected_queries

    admitted_by_qid = {str(c["query_id"]): c for c in cases}
    linkage_ok = True
    linkage_errors: list[str] = []
    for qid in sorted(expected_queries):
        row = disposition_map.get(qid)
        if row is None:
            linkage_ok = False
            linkage_errors.append(f"missing disposition {qid}")
            continue
        status = str(row["status"])
        has_case = qid in admitted_by_qid
        if status == "ADMITTED" and not has_case:
            linkage_ok = False
            linkage_errors.append(f"{qid} marked ADMITTED without case")
        if status == "NO_QUALIFYING_SOURCE" and has_case:
            linkage_ok = False
            linkage_errors.append(f"{qid} has case but disposition is NO_QUALIFYING_SOURCE")
        if status == "ADMITTED" and has_case:
            selected_source = str(row.get("selected_source_id", ""))
            selected_rank = int(row.get("selected_rank", -1))
            if selected_source != str(admitted_by_qid[qid]["source_id"]) or selected_rank != int(admitted_by_qid[qid]["source_rank"]):
                linkage_ok = False
                linkage_errors.append(f"{qid} selected source/rank mismatch")

    class_counts = Counter(str(c["gold_class"]) for c in cases)
    domain_count = len({str(c["actual_domain"]) for c in cases})
    quotas = PLAN["corpus_quotas"]
    class_quota_ok = all(
        class_counts.get(cls, 0) >= int(minimum)
        for cls, minimum in quotas["minimum_per_class"].items()
    )
    case_quota_ok = len(cases) >= int(quotas["minimum_admitted_cases"])
    domain_quota_ok = domain_count >= int(quotas["minimum_actual_domains"])

    checks = {
        "all_query_dispositions": all_dispositions,
        "disposition_case_linkage": linkage_ok,
        "minimum_admitted_cases": case_quota_ok,
        "minimum_actual_domains": domain_quota_ok,
        "minimum_per_gold_class": class_quota_ok,
    }
    complete = all(checks.values())
    return {
        "complete": complete,
        "checks": checks,
        "n_cases": len(cases),
        "n_domains": domain_count,
        "class_counts": dict(sorted(class_counts.items())),
        "missing_dispositions": sorted(expected_queries - observed_dispositions),
        "unexpected_dispositions": sorted(observed_dispositions - expected_queries),
        "linkage_errors": linkage_errors,
    }


def _visible_case(case: Mapping[str, object]) -> tuple[dict[str, object], ProbeGate]:
    gate = ProbeGate(case["probes"])
    return {"dossier": str(case["dossier"]), "probes": gate}, gate


def _run_one(policy_name: str, case: Mapping[str, object]) -> dict[str, object]:
    visible, gate = _visible_case(case)
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
        raise AssertionError(f"hidden-probe access mismatch on {case['id']} for {policy_name}")
    if int(result["cost"]) != len(gate.revealed) or int(result["cost"]) > int(R2_PROTOCOL["budget"]):
        raise AssertionError(f"probe cost mismatch on {case['id']} for {policy_name}")

    gold = str(case["gold_class"])
    choice = str(result["choice"])
    return {
        "choice": choice,
        "grs": int(choice == gold),
        "false_high_level": int(choice in HIGH_LEVEL and gold not in HIGH_LEVEL),
        "harmful_lower_level_skip": int(choice in HIGH_LEVEL and gold in LOW_LEVEL),
        "false_resolution_of_unresolved": int(gold == "UNRESOLVED" and choice != "UNRESOLVED"),
        "cost": int(result["cost"]),
        "trace": result["trace"],
    }


def _mean(xs: list[float]) -> float:
    return sum(xs) / len(xs) if xs else 0.0


def _bootstrap_interval(diffs: list[float]) -> tuple[float, float]:
    cfg = R2_PROTOCOL["decision_rule"]
    n_rep = int(cfg["paired_bootstrap_replicates"])
    rng = random.Random(int(cfg["paired_bootstrap_seed"]))
    n = len(diffs)
    stats = []
    for _ in range(n_rep):
        stats.append(sum(diffs[rng.randrange(n)] for _ in range(n)) / n)
    stats.sort()
    alpha = 1.0 - float(cfg["stability_interval"])
    return (
        stats[max(0, int((alpha / 2) * n_rep))],
        stats[min(n_rep - 1, int((1 - alpha / 2) * n_rep) - 1)],
    )


def evaluate(cases: list[Mapping[str, object]], dispositions: list[Mapping[str, object]]) -> dict[str, object]:
    acquisition = validate_acquisition(cases, dispositions)
    if not acquisition["complete"]:
        return {
            "schema": "P1U.SourceUniverse.Result.v1",
            "acquisition": acquisition,
            "terminal": "P1_R3_CANNOT_CHECK_SOURCE_UNIVERSE",
            "policy_outcomes_generated": False,
        }

    policy_names = [
        "B0_NO_REFORMULATION",
        "B1_ALWAYS_ESCALATE",
        "B2_IMMEDIATE_VOI",
        "B3_HORIZON2_DONOR_COMPLETE",
        "ORION_R2",
    ]
    rows = []
    for case in cases:
        outcomes = {name: _run_one(name, case) for name in policy_names}
        rows.append({
            "id": case["id"],
            "actual_domain": case["actual_domain"],
            "query_id": case["query_id"],
            "source_id": case["source_id"],
            "gold_class": case["gold_class"],
            "outcomes": outcomes,
        })

    summary = {}
    for name in policy_names:
        summary[name] = {
            "grs": _mean([r["outcomes"][name]["grs"] for r in rows]),
            "false_high_level_rate": _mean([r["outcomes"][name]["false_high_level"] for r in rows]),
            "harmful_lower_level_skips": sum(r["outcomes"][name]["harmful_lower_level_skip"] for r in rows),
            "false_resolution_of_unresolved": sum(r["outcomes"][name]["false_resolution_of_unresolved"] for r in rows),
            "mean_probe_cost": _mean([r["outcomes"][name]["cost"] for r in rows]),
        }

    primary = "B3_HORIZON2_DONOR_COMPLETE"
    diffs = [r["outcomes"]["ORION_R2"]["grs"] - r["outcomes"][primary]["grs"] for r in rows]
    mean_diff = _mean(diffs)
    lo, hi = _bootstrap_interval(diffs)
    by_domain: dict[str, list[float]] = defaultdict(list)
    for row, diff in zip(rows, diffs):
        by_domain[str(row["actual_domain"])].append(diff)
    domain_diffs = {d: _mean(v) for d, v in sorted(by_domain.items())}

    cfg = R2_PROTOCOL["decision_rule"]
    orion = summary["ORION_R2"]
    b3 = summary[primary]
    checks = {
        "paired_margin": mean_diff >= float(cfg["paired_grs_margin"]),
        "stability_lower_positive": lo > 0.0,
        "domain_noninferiority": all(v >= float(cfg["domain_noninferiority_floor"]) for v in domain_diffs.values()),
        "unnecessary_high_level_guard": orion["false_high_level_rate"] <= b3["false_high_level_rate"] and orion["false_high_level_rate"] <= float(cfg["max_orion_false_unnecessary_high_level_rate"]),
        "zero_lower_level_skip": orion["harmful_lower_level_skips"] <= int(cfg["harmful_lower_level_skip_tolerance"]),
        "zero_false_unresolved_resolution": orion["false_resolution_of_unresolved"] <= int(cfg["false_resolution_of_unresolved_tolerance"]),
    }
    terminal = (
        "P1_R3_PRIMARY_PASS_PENDING_2021_REPLICATION"
        if all(checks.values())
        else "P1_R3_PRIMARY_NOT_SUPPORTED"
    )
    return {
        "schema": "P1U.SourceUniverse.Result.v1",
        "acquisition": acquisition,
        "policy_outcomes_generated": True,
        "n_independent_cases": len(cases),
        "summary": summary,
        "paired_orion_minus_b3_grs": mean_diff,
        "paired_bootstrap_95_stability": [lo, hi],
        "domain_differences": domain_diffs,
        "checks": checks,
        "terminal": terminal,
        "rows": rows,
    }


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("cases", type=Path)
    parser.add_argument("dispositions", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    result = evaluate(json.loads(args.cases.read_text()), json.loads(args.dispositions.read_text()))
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.write_text(text)
    print(text, end="")


if __name__ == "__main__":
    main()

from __future__ import annotations

import importlib.util
import json
import random
from collections import defaultdict
from pathlib import Path
from typing import Mapping

ROOT = Path(__file__).resolve().parent
PROTOCOL = json.loads((ROOT / "PROTOCOL_V1.json").read_text())
ACQUISITION = json.loads((ROOT / "HELDOUT_ACQUISITION_PLAN_V1.json").read_text())

_spec = importlib.util.spec_from_file_location("p1_u_r2_policy", ROOT / "policy.py")
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
ALL_GOLD = set(PROTOCOL["classes"]) | {PROTOCOL["unresolved_label"]}
REQUIRED_PROBES = set(PROTOCOL["probes"])


class ProbeGate(Mapping[str, str]):
    """Evaluator-owned probe store that records every revealed observation."""

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


def _visible_case(case: Mapping[str, object]) -> tuple[dict[str, object], ProbeGate]:
    gate = ProbeGate(case["probes"])
    # Gold/source/query/resolution metadata is intentionally absent.
    return {"dossier": str(case["dossier"]), "probes": gate}, gate


def _validate_case(case: Mapping[str, object]) -> None:
    required = {"id", "domain", "query_id", "source_id", "source_url", "dossier", "probes", "gold_class"}
    missing = required - set(case)
    if missing:
        raise ValueError(f"case missing fields: {sorted(missing)}")
    if case["gold_class"] not in ALL_GOLD:
        raise ValueError(f"invalid gold class: {case['gold_class']}")
    if set(case["probes"]) != REQUIRED_PROBES:
        raise ValueError(f"case {case['id']} probe set mismatch")
    allowed_obs = set(PROTOCOL["probe_observations"])
    bad = {p: o for p, o in case["probes"].items() if o not in allowed_obs}
    if bad:
        raise ValueError(f"case {case['id']} invalid probe observations: {bad}")
    if len(str(case["dossier"]).split()) > 90:
        raise ValueError(f"case {case['id']} dossier exceeds 90-word freeze")


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
        raise AssertionError(
            f"{policy_name} hidden-probe access mismatch on {case['id']}: gate={gate.revealed} trace={trace_pairs}"
        )
    if int(result["cost"]) != len(gate.revealed):
        raise AssertionError(f"{policy_name} cost/reveal mismatch on {case['id']}")
    if int(result["cost"]) > int(PROTOCOL["budget"]):
        raise AssertionError(f"{policy_name} exceeded probe budget on {case['id']}")

    gold = str(case["gold_class"])
    choice = str(result["choice"])
    grs = int(choice == gold)
    false_high = int(choice in HIGH_LEVEL and gold not in HIGH_LEVEL)
    lower_skip = int(choice in HIGH_LEVEL and gold in LOW_LEVEL)
    false_resolution = int(gold == "UNRESOLVED" and choice != "UNRESOLVED")
    return {
        "choice": choice,
        "grs": grs,
        "false_high_level": false_high,
        "harmful_lower_level_skip": lower_skip,
        "false_resolution_of_unresolved": false_resolution,
        "cost": int(result["cost"]),
        "trace": result["trace"],
    }


def _mean(xs: list[float]) -> float:
    return sum(xs) / len(xs) if xs else 0.0


def _bootstrap_interval(diffs: list[float]) -> tuple[float, float]:
    cfg = PROTOCOL["decision_rule"]
    n_rep = int(cfg["paired_bootstrap_replicates"])
    rng = random.Random(int(cfg["paired_bootstrap_seed"]))
    n = len(diffs)
    if n == 0:
        return (0.0, 0.0)
    stats = []
    for _ in range(n_rep):
        stats.append(sum(diffs[rng.randrange(n)] for _ in range(n)) / n)
    stats.sort()
    alpha = 1.0 - float(cfg["stability_interval"])
    lo = stats[max(0, int((alpha / 2) * n_rep))]
    hi = stats[min(n_rep - 1, int((1 - alpha / 2) * n_rep) - 1)]
    return (lo, hi)


def evaluate(cases: list[Mapping[str, object]]) -> dict[str, object]:
    for case in cases:
        _validate_case(case)
    ids = [str(c["id"]) for c in cases]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate case id")
    source_ids = [str(c["source_id"]) for c in cases]
    if len(source_ids) != len(set(source_ids)):
        raise ValueError("source identities must be disjoint within primary corpus")

    expected_queries = {q["id"] for q in ACQUISITION["queries"]}
    observed_queries = {str(c["query_id"]) for c in cases}
    missing_queries = sorted(expected_queries - observed_queries)
    unexpected_queries = sorted(observed_queries - expected_queries)

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
        rows.append(
            {
                "id": case["id"],
                "domain": case["domain"],
                "query_id": case["query_id"],
                "source_id": case["source_id"],
                "gold_class": case["gold_class"],
                "outcomes": outcomes,
            }
        )

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
        by_domain[str(row["domain"])].append(diff)
    domain_diffs = {d: _mean(v) for d, v in sorted(by_domain.items())}

    cfg = PROTOCOL["decision_rule"]
    corpus_complete = not missing_queries and not unexpected_queries
    minimum_domains = int(ACQUISITION["corpus_target"]["minimum_distinct_domains"])
    domain_complete = len({str(c["domain"]) for c in cases if c["domain"] not in {"control", "unresolved"}}) >= minimum_domains
    orion = summary["ORION_R2"]
    b3 = summary[primary]

    checks = {
        "corpus_complete": corpus_complete,
        "minimum_domains": domain_complete,
        "paired_margin": mean_diff >= float(cfg["paired_grs_margin"]),
        "stability_lower_positive": lo > 0.0,
        "domain_noninferiority": all(v >= float(cfg["domain_noninferiority_floor"]) for v in domain_diffs.values()),
        "unnecessary_high_level_guard": orion["false_high_level_rate"] <= b3["false_high_level_rate"] and orion["false_high_level_rate"] <= float(cfg["max_orion_false_unnecessary_high_level_rate"]),
        "zero_lower_level_skip": orion["harmful_lower_level_skips"] <= int(cfg["harmful_lower_level_skip_tolerance"]),
        "zero_false_unresolved_resolution": orion["false_resolution_of_unresolved"] <= int(cfg["false_resolution_of_unresolved_tolerance"]),
    }

    if not corpus_complete or not domain_complete:
        terminal = "P1_R2_PRIMARY_CANNOT_CHECK_INCOMPLETE_CORPUS"
    elif all(checks.values()):
        terminal = "P1_R2_PRIMARY_PASS_PENDING_DISJOINT_REPLICATION"
    else:
        terminal = "P1_R2_PRIMARY_NOT_SUPPORTED"

    return {
        "schema": "P1U.NaturalisticARD.Result.v1",
        "n_independent_cases": len(cases),
        "missing_queries": missing_queries,
        "unexpected_queries": unexpected_queries,
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
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    cases = json.loads(args.cases.read_text())
    result = evaluate(cases)
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.write_text(text)
    print(text, end="")


if __name__ == "__main__":
    main()

from __future__ import annotations

import importlib.util
import json
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Mapping

ROOT = Path(__file__).resolve().parent
P1_ROOT = ROOT.parent
R2_ROOT = P1_ROOT / "gpt_r2"
R5_ROOT = P1_ROOT / "gpt_r5"
PROTOCOL = json.loads((ROOT / "NATIVE_PROTOCOL_V1.json").read_text())
R2_PROTOCOL = json.loads((R2_ROOT / "PROTOCOL_V1.json").read_text())
FIXED = json.loads((R5_ROOT / "FIXED_SOURCE_SET_V1.json").read_text())


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    except Exception:
        sys.modules.pop(name, None)
        raise
    return module


NATIVE = _load(ROOT / "native_orion.py", "p1_u_r6_native")
B3_POLICY = _load(R2_ROOT / "policy.py", "p1_u_r6_b3")
CORPUS = _load(R5_ROOT / "build_fixed_corpus.py", "p1_u_r6_fixed_corpus")

CONTROL = str(PROTOCOL["control_class"])
UNRESOLVED = str(PROTOCOL["unresolved_class"])
PROBES = set(PROTOCOL["probes"])
ALLOWED_OBS = set(PROTOCOL["probe_observations"])
HIGH = {"OBJECTIVE_OR_MODEL_CLASS", "PROBLEM_BOUNDARY"}
LOW = {
    "SEARCH_OR_EVIDENCE",
    "REPRESENTATION_OR_INTERFACE",
    "IMPLEMENTATION_OR_ENVIRONMENT",
    "MEASUREMENT_OR_EVALUATOR",
}
SUBSTANTIVE = LOW | HIGH
EXPECTED_PAIRS = {r["source_id"]: r for r in FIXED["pair_sources"]}
EXPECTED_UNRES = {r["source_id"]: r for r in FIXED["unresolved_sources"]}


class B3ProbeGate(Mapping[str, str]):
    def __init__(self, hidden: Mapping[str, str]):
        if set(hidden) != PROBES:
            raise ValueError("B3 probe set mismatch")
        self._hidden = dict(hidden)
        self.revealed: list[tuple[str, str]] = []

    def __getitem__(self, key: str) -> str:
        if key not in self._hidden:
            raise KeyError(key)
        value = str(self._hidden[key])
        self.revealed.append((key, value))
        return value

    def __iter__(self):
        raise RuntimeError("B3 may not enumerate evaluator-owned probes")

    def __len__(self) -> int:
        return len(self._hidden)


def fixed_corpus() -> tuple[list[dict], list[dict]]:
    pairs, unresolved = CORPUS.build()
    return list(pairs), list(unresolved)


def _validate_episode(ep: Mapping[str, object], expected_gold: str) -> None:
    for key in ("id", "dossier", "probes", "gold_class"):
        if key not in ep:
            raise ValueError(f"episode missing {key}")
    if str(ep["gold_class"]) != expected_gold:
        raise ValueError(f"episode {ep['id']} gold mismatch")
    if set(ep["probes"]) != PROBES:
        raise ValueError(f"episode {ep['id']} probe set mismatch")
    if any(str(value) not in ALLOWED_OBS for value in ep["probes"].values()):
        raise ValueError(f"episode {ep['id']} invalid probe observation")
    if len(str(ep["dossier"]).split()) > 90:
        raise ValueError(f"episode {ep['id']} dossier exceeds 90 words")


def validate_fixed_corpus(
    pairs: list[Mapping[str, object]], unresolved: list[Mapping[str, object]]
) -> dict[str, object]:
    errors: list[str] = []
    pair_sources = {str(row.get("source_id", "")) for row in pairs}
    unres_sources = {str(row.get("source_id", "")) for row in unresolved}
    if pair_sources != set(EXPECTED_PAIRS):
        errors.append("pair source set mismatch")
    if unres_sources != set(EXPECTED_UNRES):
        errors.append("unresolved source set mismatch")

    seen_sources: set[str] = set()
    seen_episodes: set[str] = set()
    classes: Counter[str] = Counter()
    domains: set[str] = set()

    for row in pairs:
        sid = str(row.get("source_id", ""))
        expected = EXPECTED_PAIRS.get(sid)
        if expected is None:
            continue
        if sid in seen_sources:
            errors.append(f"duplicate source {sid}")
        seen_sources.add(sid)
        if str(row.get("query_id")) != str(expected["query_id"]):
            errors.append(f"{sid} query mismatch")
        if str(row.get("adverse_class")) != str(expected["class"]):
            errors.append(f"{sid} class mismatch")
        if int(row.get("source_year", -1)) != 2020:
            errors.append(f"{sid} wrong year")
        cls = str(row.get("adverse_class", ""))
        classes[cls] += 1
        domains.add(str(row.get("actual_domain", "")))
        try:
            _validate_episode(row["adverse"], cls)
            _validate_episode(row["control"], CONTROL)
        except (KeyError, ValueError) as exc:
            errors.append(str(exc))
        for member in ("adverse", "control"):
            if member in row and isinstance(row[member], Mapping):
                eid = str(row[member].get("id", ""))
                if eid in seen_episodes:
                    errors.append(f"duplicate episode {eid}")
                seen_episodes.add(eid)

    for row in unresolved:
        sid = str(row.get("source_id", ""))
        expected = EXPECTED_UNRES.get(sid)
        if expected is None:
            continue
        if sid in seen_sources:
            errors.append(f"duplicate source {sid}")
        seen_sources.add(sid)
        if str(row.get("query_id")) != str(expected["query_id"]):
            errors.append(f"{sid} query mismatch")
        if int(row.get("source_year", -1)) != 2020:
            errors.append(f"{sid} wrong year")
        domains.add(str(row.get("actual_domain", "")))
        try:
            _validate_episode(row, UNRESOLVED)
        except ValueError as exc:
            errors.append(str(exc))
        eid = str(row.get("id", ""))
        if eid in seen_episodes:
            errors.append(f"duplicate episode {eid}")
        seen_episodes.add(eid)

    min_per_class = int(FIXED["minimum_pair_sources_per_substantive_class"])
    checks = {
        "exact_pair_sources": pair_sources == set(EXPECTED_PAIRS),
        "exact_unresolved_sources": unres_sources == set(EXPECTED_UNRES),
        "pair_count": len(pairs) == int(FIXED["expected_pair_source_count"]),
        "unresolved_count": len(unresolved) == int(FIXED["expected_unresolved_source_count"]),
        "episode_count": len(seen_episodes) == int(FIXED["expected_episode_count"]),
        "minimum_pairs_per_class": all(classes.get(cls, 0) >= min_per_class for cls in sorted(SUBSTANTIVE)),
        "minimum_domains": len(domains) >= int(FIXED["minimum_actual_domains"]),
        "no_errors": not errors,
    }
    return {
        "complete": all(checks.values()),
        "checks": checks,
        "errors": errors,
        "class_counts": dict(sorted(classes.items())),
        "n_domains": len(domains),
    }


def _b3(ep: Mapping[str, object]) -> dict[str, object]:
    gate = B3ProbeGate(ep["probes"])
    visible = {"dossier": str(ep["dossier"]), "probes": gate}
    result = B3_POLICY.donor_complete_policy(visible, horizon=2)
    trace_pairs = [(str(item["probe"]), str(item["observation"])) for item in result["trace"]]
    if gate.revealed != trace_pairs:
        raise AssertionError(f"B3 hidden-probe mismatch on {ep['id']}")
    if int(result["cost"]) != len(gate.revealed):
        raise AssertionError(f"B3 cost mismatch on {ep['id']}")
    if len(gate.revealed) > int(PROTOCOL["budget"]):
        raise AssertionError(f"B3 exceeded native-comparison budget on {ep['id']}")
    return {
        "choice": str(result["choice"]),
        "probe_accesses": [probe for probe, _ in gate.revealed],
        "cost": len(gate.revealed),
    }


def _verify_native_lineage(result: Mapping[str, object]) -> None:
    if result.get("grants_adoption_authority") is not False:
        raise AssertionError("native result unexpectedly grants adoption authority")
    if result.get("grants_promotion_authority") is not False:
        raise AssertionError("native result unexpectedly grants promotion authority")
    if result.get("grants_merge_authority") is not False:
        raise AssertionError("native result unexpectedly grants merge authority")
    root = result.get("root")
    if not isinstance(root, Mapping):
        raise AssertionError("native result missing root runtime lineage")
    required_root = set(PROTOCOL["root_runtime"]["required_operator_ids"])
    if not required_root <= set(map(str, root.get("operator_ids", []))):
        raise AssertionError("native root runtime lineage incomplete")
    required_probe = set(PROTOCOL["probe_runtime"]["required_operator_ids"])
    executions = result.get("probe_executions", [])
    if not isinstance(executions, list):
        raise AssertionError("native probe lineage malformed")
    for execution in executions:
        if not isinstance(execution, Mapping):
            raise AssertionError("native probe execution malformed")
        if not required_probe <= set(map(str, execution.get("operator_ids", []))):
            raise AssertionError("native child runtime lineage incomplete")
        if not str(execution.get("evidence_id", "")).startswith("evidence:p1-r6:"):
            raise AssertionError("native child runtime evidence identity missing")
    accesses = list(map(str, result.get("probe_accesses", [])))
    if len(accesses) > int(PROTOCOL["budget"]):
        raise AssertionError("native ARD exceeded probe budget")
    if accesses != [str(item.get("probe_id")) for item in executions]:
        raise AssertionError("native access/execution lineage mismatch")
    payload = {key: value for key, value in result.items() if key != "digest"}
    from orion.transfer.v2.canonical import content_digest

    if content_digest(payload) != str(result.get("digest", "")):
        raise AssertionError("native decision digest mismatch")


def _score(choice: str, gold: str) -> dict[str, int]:
    return {
        "grs": int(choice == gold),
        "false_high_level": int(choice in HIGH and gold not in HIGH),
        "harmful_lower_level_skip": int(choice in HIGH and gold in LOW),
        "false_resolution_of_unresolved": int(gold == UNRESOLVED and choice != UNRESOLVED),
    }


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _bootstrap(values: list[float], *, reps: int, seed: int, interval: float) -> tuple[float, float]:
    if not values:
        return (0.0, 0.0)
    rng = random.Random(seed)
    n = len(values)
    stats = [sum(values[rng.randrange(n)] for _ in range(n)) / n for _ in range(reps)]
    stats.sort()
    alpha = 1.0 - interval
    return (
        stats[max(0, int((alpha / 2) * reps))],
        stats[min(reps - 1, int((1 - alpha / 2) * reps) - 1)],
    )


def _stratified_macro_bootstrap(
    by_class: Mapping[str, list[float]], *, reps: int, seed: int, interval: float
) -> tuple[float, float]:
    rng = random.Random(seed)
    classes = sorted(by_class)
    stats: list[float] = []
    for _ in range(reps):
        means = []
        for cls in classes:
            xs = by_class[cls]
            means.append(sum(xs[rng.randrange(len(xs))] for _ in range(len(xs))) / len(xs))
        stats.append(sum(means) / len(means))
    stats.sort()
    alpha = 1.0 - interval
    return (
        stats[max(0, int((alpha / 2) * reps))],
        stats[min(reps - 1, int((1 - alpha / 2) * reps) - 1)],
    )


def evaluate(
    pairs: list[Mapping[str, object]], unresolved: list[Mapping[str, object]]
) -> dict[str, object]:
    data = validate_fixed_corpus(pairs, unresolved)
    if not data["complete"]:
        return {
            "schema": "P1U.NativeOrionResult.v1",
            "data": data,
            "policy_outcomes_generated": False,
            "terminal": "P1_R6_CANNOT_CHECK_FIXED_CORPUS",
        }

    rows: list[dict[str, object]] = []
    episode_diffs: list[float] = []
    domain_diffs: dict[str, list[float]] = defaultdict(list)
    pair_diffs: list[float] = []
    pair_by_class: dict[str, list[float]] = defaultdict(list)
    native_false_high = b3_false_high = 0
    native_lower_skips = native_false_unresolved = control_harm = 0
    native_base_differences = 0

    for pair in pairs:
        member_results: dict[str, object] = {}
        pair_native_correct = True
        pair_b3_correct = True
        for member in ("adverse", "control"):
            ep = pair[member]
            evidence_note = str(pair["pair_evidence"]["source_claim"])
            native = NATIVE.run_native_ard(ep, evidence_note=evidence_note)
            base = NATIVE.run_native_base(ep)
            b3 = _b3(ep)
            _verify_native_lineage(native)
            _verify_native_lineage(base)
            gold = str(ep["gold_class"])
            native_score = _score(str(native["choice"]), gold)
            base_score = _score(str(base["choice"]), gold)
            b3_score = _score(str(b3["choice"]), gold)
            if str(native["choice"]) != str(base["choice"]):
                native_base_differences += 1
            pair_native_correct = pair_native_correct and bool(native_score["grs"])
            pair_b3_correct = pair_b3_correct and bool(b3_score["grs"])
            diff = native_score["grs"] - b3_score["grs"]
            episode_diffs.append(diff)
            domain_diffs[str(pair["actual_domain"])].append(diff)
            native_false_high += native_score["false_high_level"]
            b3_false_high += b3_score["false_high_level"]
            native_lower_skips += native_score["harmful_lower_level_skip"]
            if member == "control":
                control_harm += native_score["false_high_level"]
            member_results[member] = {
                "gold_class": gold,
                "native_ard": {"result": native, "score": native_score},
                "native_base": {"result": base, "score": base_score},
                "b3": {"result": b3, "score": b3_score},
            }
        pair_diff = int(pair_native_correct) - int(pair_b3_correct)
        pair_diffs.append(pair_diff)
        pair_by_class[str(pair["adverse_class"])].append(pair_diff)
        rows.append(
            {
                "pair_id": pair["pair_id"],
                "source_id": pair["source_id"],
                "adverse_class": pair["adverse_class"],
                "actual_domain": pair["actual_domain"],
                "pair_selective_native": int(pair_native_correct),
                "pair_selective_b3": int(pair_b3_correct),
                "members": member_results,
            }
        )

    unresolved_rows: list[dict[str, object]] = []
    for ep in unresolved:
        evidence_note = str(ep["admission_evidence"]["source_claim"])
        native = NATIVE.run_native_ard(ep, evidence_note=evidence_note)
        base = NATIVE.run_native_base(ep)
        b3 = _b3(ep)
        _verify_native_lineage(native)
        _verify_native_lineage(base)
        gold = UNRESOLVED
        native_score = _score(str(native["choice"]), gold)
        base_score = _score(str(base["choice"]), gold)
        b3_score = _score(str(b3["choice"]), gold)
        if str(native["choice"]) != str(base["choice"]):
            native_base_differences += 1
        diff = native_score["grs"] - b3_score["grs"]
        episode_diffs.append(diff)
        domain_diffs[str(ep["actual_domain"])].append(diff)
        native_false_high += native_score["false_high_level"]
        b3_false_high += b3_score["false_high_level"]
        native_false_unresolved += native_score["false_resolution_of_unresolved"]
        unresolved_rows.append(
            {
                "id": ep["id"],
                "source_id": ep["source_id"],
                "native_ard": {"result": native, "score": native_score},
                "native_base": {"result": base, "score": base_score},
                "b3": {"result": b3, "score": b3_score},
            }
        )

    cfg = PROTOCOL["decision_rule"]
    reps = int(cfg["bootstrap_replicates"])
    seed = int(cfg["bootstrap_seed"])
    interval = float(cfg["stability_interval"])
    episode_diff = _mean(episode_diffs)
    ep_lo, ep_hi = _bootstrap(episode_diffs, reps=reps, seed=seed, interval=interval)
    pair_micro = _mean(pair_diffs)
    pair_lo, pair_hi = _bootstrap(pair_diffs, reps=reps, seed=seed + 1, interval=interval)
    class_means = {cls: _mean(values) for cls, values in sorted(pair_by_class.items())}
    pair_macro = _mean(list(class_means.values()))
    macro_lo, macro_hi = _stratified_macro_bootstrap(
        pair_by_class, reps=reps, seed=seed + 2, interval=interval
    )
    domain_means = {domain: _mean(values) for domain, values in sorted(domain_diffs.items())}
    n_episodes = len(episode_diffs)
    native_false_high_rate = native_false_high / n_episodes
    b3_false_high_rate = b3_false_high / n_episodes
    nonnegative_classes = sum(value >= 0 for value in class_means.values())

    checks = {
        "episode_margin": episode_diff >= float(cfg["episode_grs_margin"]),
        "episode_stability_lower_positive": ep_lo > 0,
        "pair_micro_margin": pair_micro >= float(cfg["pair_selective_margin"]),
        "pair_micro_stability_lower_positive": pair_lo > 0,
        "pair_macro_margin": pair_macro >= float(cfg["class_macro_pair_margin"]),
        "pair_macro_stability_lower_positive": macro_lo > 0,
        "domain_noninferiority": all(
            value >= float(cfg["domain_or_class_noninferiority_floor"])
            for value in domain_means.values()
        ),
        "class_noninferiority": all(
            value >= float(cfg["domain_or_class_noninferiority_floor"])
            for value in class_means.values()
        ),
        "at_least_three_nonnegative_classes": nonnegative_classes >= 3,
        "false_high_level_guard": native_false_high_rate <= b3_false_high_rate
        and native_false_high_rate <= float(cfg["max_false_high_level_rate"]),
        "zero_lower_level_skip": native_lower_skips
        <= int(cfg["harmful_lower_level_skip_tolerance"]),
        "zero_control_high_level_harm": control_harm == 0,
        "zero_false_unresolved_resolution": native_false_unresolved
        <= int(cfg["false_resolution_of_unresolved_tolerance"]),
        "native_ard_materially_differs_from_base": native_base_differences > 0,
    }
    terminal = (
        "P1_R6_NATIVE_PRIMARY_PASS_PENDING_2019_REPLICATION"
        if all(checks.values())
        else "P1_R6_NATIVE_PRIMARY_NOT_SUPPORTED"
    )
    return {
        "schema": "P1U.NativeOrionResult.v1",
        "data": data,
        "policy_outcomes_generated": True,
        "episode_orion_native_ard_minus_b3_grs": episode_diff,
        "episode_bootstrap_95_stability": [ep_lo, ep_hi],
        "pair_micro_orion_native_ard_minus_b3": pair_micro,
        "pair_micro_bootstrap_95_stability": [pair_lo, pair_hi],
        "pair_macro_equal_class_orion_native_ard_minus_b3": pair_macro,
        "pair_macro_bootstrap_95_stability": [macro_lo, macro_hi],
        "class_pair_differences": class_means,
        "domain_episode_differences": domain_means,
        "native_false_high_level_rate": native_false_high_rate,
        "b3_false_high_level_rate": b3_false_high_rate,
        "native_base_choice_differences": native_base_differences,
        "checks": checks,
        "terminal": terminal,
        "pair_rows": rows,
        "unresolved_rows": unresolved_rows,
    }


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    pairs, unresolved = fixed_corpus()
    result = evaluate(pairs, unresolved)
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.write_text(text)
    print(text, end="")


if __name__ == "__main__":
    main()

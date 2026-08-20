from __future__ import annotations

import argparse
import importlib.util
import json
import random
from collections import Counter, defaultdict
from pathlib import Path
from typing import Mapping

from gpt_r6_native_adapter import (
    CONTROL,
    HIGH,
    LOW,
    PROBE_TO_CLASS,
    ProbeGate,
    UNRESOLVED,
    run_native_episode,
)

ROOT = Path(__file__).resolve().parent
R2_ROOT = ROOT / "gpt_r2"
R2_PROTOCOL = json.loads((R2_ROOT / "PROTOCOL_V1.json").read_text())

_POLICY_SPEC = importlib.util.spec_from_file_location("p1_r6_frozen_b3", R2_ROOT / "policy.py")
assert _POLICY_SPEC and _POLICY_SPEC.loader
POLICY = importlib.util.module_from_spec(_POLICY_SPEC)
_POLICY_SPEC.loader.exec_module(POLICY)

SUBSTANTIVE = set(PROBE_TO_CLASS.values())
CLASSES = tuple(sorted(SUBSTANTIVE))
PROBES = set(PROBE_TO_CLASS)
ALLOWED_OBS = set(R2_PROTOCOL["probe_observations"])


def _import_builder(path: Path):
    spec = importlib.util.spec_from_file_location("p1_r6_frozen_builder", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import frozen builder: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_fixed_data(
    fixed: Mapping[str, object],
    pairs: list[Mapping[str, object]],
    unresolved: list[Mapping[str, object]],
) -> dict[str, object]:
    expected_pairs = {str(row["source_id"]): row for row in fixed["pair_sources"]}
    expected_unresolved = {str(row["source_id"]): row for row in fixed["unresolved_sources"]}
    actual_pairs = {str(row.get("source_id", "")) for row in pairs}
    actual_unresolved = {str(row.get("source_id", "")) for row in unresolved}
    errors: list[str] = []
    seen_sources: set[str] = set()
    seen_episodes: set[str] = set()
    domains: set[str] = set()
    class_counts: Counter[str] = Counter()

    if actual_pairs != set(expected_pairs):
        errors.append("pair source set mismatch")
    if actual_unresolved != set(expected_unresolved):
        errors.append("unresolved source set mismatch")
    if list(fixed.get("failed_r4_queries_retained", [])) != ["MEAS-P2", "BOUND-P1"]:
        errors.append("failed R4 routes were not preserved exactly")

    def validate_episode(ep: Mapping[str, object], expected_gold: str) -> None:
        for key in ("id", "dossier", "probes", "gold_class"):
            if key not in ep:
                raise ValueError(f"episode missing {key}")
        if str(ep["gold_class"]) != expected_gold:
            raise ValueError(f"episode {ep['id']} gold mismatch")
        probes = ep["probes"]
        if not isinstance(probes, Mapping) or set(probes) != PROBES:
            raise ValueError(f"episode {ep['id']} probe set mismatch")
        if any(str(value) not in ALLOWED_OBS for value in probes.values()):
            raise ValueError(f"episode {ep['id']} probe value invalid")
        if len(str(ep["dossier"]).split()) > 90:
            raise ValueError(f"episode {ep['id']} dossier exceeds 90 words")

    for row in pairs:
        source_id = str(row.get("source_id", ""))
        expected = expected_pairs.get(source_id)
        if expected is None:
            continue
        if source_id in seen_sources:
            errors.append(f"duplicate source: {source_id}")
        seen_sources.add(source_id)
        domains.add(str(row.get("actual_domain", "")))
        expected_class = str(expected["class"])
        if str(row.get("query_id")) != str(expected["query_id"]):
            errors.append(f"query mismatch: {source_id}")
        if str(row.get("adverse_class")) != expected_class:
            errors.append(f"class mismatch: {source_id}")
        if int(row.get("source_year", -1)) != 2020:
            errors.append(f"source year mismatch: {source_id}")
        class_counts[expected_class] += 1
        try:
            validate_episode(row["adverse"], expected_class)
            validate_episode(row["control"], CONTROL)
        except (KeyError, TypeError, ValueError) as exc:
            errors.append(str(exc))
        for member in ("adverse", "control"):
            episode = row.get(member)
            if isinstance(episode, Mapping):
                episode_id = str(episode.get("id", ""))
                if episode_id in seen_episodes:
                    errors.append(f"duplicate episode: {episode_id}")
                seen_episodes.add(episode_id)

    for row in unresolved:
        source_id = str(row.get("source_id", ""))
        expected = expected_unresolved.get(source_id)
        if expected is None:
            continue
        if source_id in seen_sources:
            errors.append(f"duplicate source: {source_id}")
        seen_sources.add(source_id)
        domains.add(str(row.get("actual_domain", "")))
        if str(row.get("query_id")) != str(expected["query_id"]):
            errors.append(f"unresolved query mismatch: {source_id}")
        if int(row.get("source_year", -1)) != 2020:
            errors.append(f"unresolved source year mismatch: {source_id}")
        try:
            validate_episode(row, UNRESOLVED)
        except (TypeError, ValueError) as exc:
            errors.append(str(exc))
        episode_id = str(row.get("id", ""))
        if episode_id in seen_episodes:
            errors.append(f"duplicate episode: {episode_id}")
        seen_episodes.add(episode_id)

    checks = {
        "exact_pair_source_set": actual_pairs == set(expected_pairs),
        "exact_unresolved_source_set": actual_unresolved == set(expected_unresolved),
        "expected_pair_count": len(pairs) == int(fixed["expected_pair_source_count"]),
        "expected_unresolved_count": len(unresolved)
        == int(fixed["expected_unresolved_source_count"]),
        "expected_episode_count": len(seen_episodes) == int(fixed["expected_episode_count"]),
        "minimum_pairs_per_class": all(
            class_counts.get(cls, 0) >= int(fixed["minimum_pair_sources_per_substantive_class"])
            for cls in CLASSES
        ),
        "minimum_domains": len(domains) >= int(fixed["minimum_actual_domains"]),
        "failed_routes_preserved": list(fixed.get("failed_r4_queries_retained", []))
        == ["MEAS-P2", "BOUND-P1"],
        "no_validation_errors": not errors,
    }
    return {
        "complete": all(checks.values()),
        "checks": checks,
        "errors": errors,
        "class_counts": dict(sorted(class_counts.items())),
        "n_domains": len(domains),
    }


def _run_b3(ep: Mapping[str, object]) -> dict[str, object]:
    gate = ProbeGate(ep["probes"])
    result = POLICY.donor_complete_policy(
        {"dossier": str(ep["dossier"]), "probes": gate}, horizon=2
    )
    trace = [(str(item["probe"]), str(item["observation"])) for item in result["trace"]]
    if gate.revealed != trace:
        raise AssertionError("B3 hidden-probe access does not match returned trace")
    if int(result["cost"]) != len(gate.revealed):
        raise AssertionError("B3 cost does not match probe access")
    if int(result["cost"]) > int(R2_PROTOCOL["budget"]):
        raise AssertionError("B3 exceeded frozen action budget")
    return {
        "choice": str(result["choice"]),
        "cost": int(result["cost"]),
        "trace": [list(item) for item in trace],
    }


def _is_hex64(value: object) -> bool:
    text = str(value)
    return len(text) == 64 and all(ch in "0123456789abcdef" for ch in text)


def _native_row_valid(native: Mapping[str, object]) -> bool:
    runtime = native["runtime"]
    base = native["base"]
    ard = native["ard"]
    if not isinstance(runtime, Mapping) or not isinstance(base, Mapping) or not isinstance(ard, Mapping):
        return False
    if not runtime.get("trace_id") or not runtime.get("receipt_ids"):
        return False
    if not all(
        _is_hex64(runtime[key])
        for key in ("pre_state_hash", "post_state_hash", "final_state_digest")
    ):
        return False
    required_ops = {"FRAME", "SEARCH", "ABSORB", "RECONSTRUCT"}
    if not required_ops.issubset(set(runtime.get("operator_sequence", []))):
        return False
    for arm in (base, ard):
        for key in ("responsibility_digest", "interface_digest", "revision_gate_digest"):
            if not _is_hex64(arm.get(key)):
                return False
        if not arm.get("mechanic_digests") or not arm.get("assessment_digests"):
            return False
        if not all(_is_hex64(value) for value in arm["mechanic_digests"]):
            return False
        if not all(_is_hex64(value) for value in arm["assessment_digests"]):
            return False
    return True


def _leakage_free(native: Mapping[str, object], forbidden_tokens: tuple[str, ...]) -> bool:
    serialized = json.dumps(native.get("request_payloads", []), sort_keys=True)
    return all(not token or token not in serialized for token in forbidden_tokens)


def _score(choice: str, gold: str) -> dict[str, int]:
    return {
        "grs": int(choice == gold),
        "false_high_level": int(choice in HIGH and gold not in HIGH),
        "harmful_lower_level_skip": int(choice in HIGH and gold in LOW),
        "false_resolution_of_unresolved": int(gold == UNRESOLVED and choice != UNRESOLVED),
    }


def _run_episode(
    ep: Mapping[str, object],
    *,
    source_uri: str,
    forbidden_tokens: tuple[str, ...],
) -> dict[str, object]:
    native = run_native_episode(
        dossier=str(ep["dossier"]),
        source_uri=source_uri,
        hidden_probes=ep["probes"],
    )
    b3 = _run_b3(ep)
    leakage_free = _leakage_free(native, forbidden_tokens)
    row_valid = _native_row_valid(native)
    gold = str(ep["gold_class"])
    base_choice = str(native["base"]["choice"])
    ard_choice = str(native["ard"]["choice"])
    request_payload_digest = __import__("hashlib").sha256(
        json.dumps(native.pop("request_payloads"), sort_keys=True).encode("utf-8")
    ).hexdigest()
    return {
        "gold": gold,
        "base": {"choice": base_choice, **_score(base_choice, gold)},
        "ard": {
            "choice": ard_choice,
            **_score(ard_choice, gold),
            "cost": int(native["ard"]["cost"]),
            "probe_trace": native["ard"]["probe_trace"],
        },
        "b3": {"choice": b3["choice"], **_score(str(b3["choice"]), gold), **b3},
        "runtime": native["runtime"],
        "base_native": native["base"],
        "ard_native": native["ard"],
        "native_row_valid": row_valid,
        "leakage_free": leakage_free,
        "request_payload_digest": request_payload_digest,
    }


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _bootstrap(
    diffs: list[float], reps: int, seed: int, interval: float
) -> tuple[float, float]:
    rng = random.Random(seed)
    n = len(diffs)
    values = [
        sum(diffs[rng.randrange(n)] for _ in range(n)) / n for _ in range(reps)
    ]
    values.sort()
    alpha = 1.0 - interval
    return (
        values[int((alpha / 2) * reps)],
        values[min(reps - 1, int((1 - alpha / 2) * reps) - 1)],
    )


def _stratified_macro_bootstrap(
    by_class: Mapping[str, list[float]], reps: int, seed: int, interval: float
) -> tuple[float, float]:
    rng = random.Random(seed)
    classes = sorted(by_class)
    values: list[float] = []
    for _ in range(reps):
        class_means = []
        for cls in classes:
            rows = by_class[cls]
            class_means.append(
                sum(rows[rng.randrange(len(rows))] for _ in range(len(rows))) / len(rows)
            )
        values.append(sum(class_means) / len(class_means))
    values.sort()
    alpha = 1.0 - interval
    return (
        values[int((alpha / 2) * reps)],
        values[min(reps - 1, int((1 - alpha / 2) * reps) - 1)],
    )


def evaluate(
    fixed: Mapping[str, object],
    pairs: list[Mapping[str, object]],
    unresolved: list[Mapping[str, object]],
) -> dict[str, object]:
    data = validate_fixed_data(fixed, pairs, unresolved)
    if not data["complete"]:
        return {
            "schema": "P1U.R6NativePrimary.v1",
            "data": data,
            "policy_outcomes_generated": False,
            "terminal": "P1_R6_CANNOT_CHECK_FIXED_DATA",
        }

    pair_rows: list[dict[str, object]] = []
    unresolved_rows: list[dict[str, object]] = []
    episode_diffs: list[float] = []
    domain_diffs: dict[str, list[float]] = defaultdict(list)
    class_episode_diffs: dict[str, list[float]] = defaultdict(list)
    ard_false_high = 0
    b3_false_high = 0
    ard_lower_skips = 0
    ard_false_unresolved = 0
    harmful_control_high = 0
    native_invalid_rows = 0
    leakage_rows = 0
    ard_base_adverse_choice_differences: dict[str, int] = defaultdict(int)

    for pair in pairs:
        pair_id = str(pair["pair_id"])
        query_id = str(pair["query_id"])
        adverse_class = str(pair["adverse_class"])
        source_id = str(pair["source_id"])
        source_uri = str(pair["source_url"])
        outcomes: dict[str, dict[str, object]] = {}
        for member in ("adverse", "control"):
            ep = pair[member]
            forbidden = (
                str(ep["id"]),
                pair_id,
                query_id,
                adverse_class,
                str(ep["gold_class"]),
            )
            row = _run_episode(ep, source_uri=source_uri, forbidden_tokens=forbidden)
            outcomes[member] = row
            diff = int(row["ard"]["grs"]) - int(row["b3"]["grs"])
            episode_diffs.append(float(diff))
            domain_diffs[str(pair["actual_domain"])].append(float(diff))
            class_episode_diffs[adverse_class].append(float(diff))
            ard_false_high += int(row["ard"]["false_high_level"])
            b3_false_high += int(row["b3"]["false_high_level"])
            ard_lower_skips += int(row["ard"]["harmful_lower_level_skip"])
            native_invalid_rows += int(not row["native_row_valid"])
            leakage_rows += int(not row["leakage_free"])
        harmful_control_high += int(outcomes["control"]["ard"]["false_high_level"])
        if outcomes["adverse"]["ard"]["choice"] != outcomes["adverse"]["base"]["choice"]:
            ard_base_adverse_choice_differences[adverse_class] += 1
        pair_rows.append(
            {
                "pair_id": pair_id,
                "query_id": query_id,
                "adverse_class": adverse_class,
                "actual_domain": pair["actual_domain"],
                "source_id": source_id,
                "outcomes": outcomes,
            }
        )

    for ep in unresolved:
        forbidden = (
            str(ep["id"]),
            str(ep["query_id"]),
            UNRESOLVED,
        )
        row = _run_episode(ep, source_uri=str(ep["source_url"]), forbidden_tokens=forbidden)
        diff = int(row["ard"]["grs"]) - int(row["b3"]["grs"])
        episode_diffs.append(float(diff))
        domain_diffs[str(ep["actual_domain"])].append(float(diff))
        class_episode_diffs[UNRESOLVED].append(float(diff))
        ard_false_high += int(row["ard"]["false_high_level"])
        b3_false_high += int(row["b3"]["false_high_level"])
        ard_false_unresolved += int(row["ard"]["false_resolution_of_unresolved"])
        native_invalid_rows += int(not row["native_row_valid"])
        leakage_rows += int(not row["leakage_free"])
        unresolved_rows.append(
            {
                "id": ep["id"],
                "query_id": ep["query_id"],
                "actual_domain": ep["actual_domain"],
                "source_id": ep["source_id"],
                "outcome": row,
            }
        )

    decision = R2_PROTOCOL["decision_rule"]
    n_episodes = len(episode_diffs)
    episode_diff = _mean(episode_diffs)
    episode_lo, episode_hi = _bootstrap(
        episode_diffs,
        int(decision["paired_bootstrap_replicates"]),
        int(decision["paired_bootstrap_seed"]),
        float(decision["stability_interval"]),
    )
    domain_means = {key: _mean(values) for key, values in sorted(domain_diffs.items())}
    class_means = {
        key: _mean(values) for key, values in sorted(class_episode_diffs.items())
    }

    pair_diffs: list[float] = []
    pair_by_class: dict[str, list[float]] = defaultdict(list)
    for row in pair_rows:
        outcomes = row["outcomes"]
        ard_pair = int(outcomes["adverse"]["ard"]["grs"] and outcomes["control"]["ard"]["grs"])
        b3_pair = int(outcomes["adverse"]["b3"]["grs"] and outcomes["control"]["b3"]["grs"])
        diff = float(ard_pair - b3_pair)
        pair_diffs.append(diff)
        pair_by_class[str(row["adverse_class"])].append(diff)
        row["pair_selective"] = {"ard": ard_pair, "b3": b3_pair, "difference": diff}

    pair_micro = _mean(pair_diffs)
    pair_lo, pair_hi = _bootstrap(pair_diffs, 20000, 20260820, 0.95)
    pair_class_means = {
        cls: _mean(pair_by_class[cls]) for cls in sorted(pair_by_class)
    }
    pair_macro = _mean(list(pair_class_means.values()))
    macro_lo, macro_hi = _stratified_macro_bootstrap(
        pair_by_class, 20000, 20260820, 0.95
    )

    ard_grs_values = [
        int(row["outcomes"][member]["ard"]["grs"])
        for row in pair_rows
        for member in ("adverse", "control")
    ] + [int(row["outcome"]["ard"]["grs"]) for row in unresolved_rows]
    b3_grs_values = [
        int(row["outcomes"][member]["b3"]["grs"])
        for row in pair_rows
        for member in ("adverse", "control")
    ] + [int(row["outcome"]["b3"]["grs"]) for row in unresolved_rows]
    base_grs_values = [
        int(row["outcomes"][member]["base"]["grs"])
        for row in pair_rows
        for member in ("adverse", "control")
    ] + [int(row["outcome"]["base"]["grs"]) for row in unresolved_rows]

    ard_false_high_rate = ard_false_high / n_episodes
    b3_false_high_rate = b3_false_high / n_episodes
    mechanism_classes = sorted(
        cls for cls, count in ard_base_adverse_choice_differences.items() if count > 0
    )

    checks = {
        "episode_grs_margin": episode_diff >= 0.10,
        "episode_bootstrap_lower_positive": episode_lo > 0,
        "domain_noninferiority": all(value >= -0.10 for value in domain_means.values()),
        "class_noninferiority": all(
            value >= -0.10 for cls, value in class_means.items() if cls != UNRESOLVED
        ),
        "pair_macro_margin": pair_macro >= 0.10,
        "pair_macro_stratified_lower_positive": macro_lo > 0,
        "pair_micro_margin": pair_micro >= 0.10,
        "pair_micro_lower_positive": pair_lo > 0,
        "zero_harmful_lower_level_skip": ard_lower_skips == 0,
        "zero_harmful_high_level_control_escalation": harmful_control_high == 0,
        "zero_false_resolution_unresolved": ard_false_unresolved == 0,
        "unnecessary_high_level_guard": (
            ard_false_high_rate <= b3_false_high_rate
            and ard_false_high_rate
            <= float(decision["max_orion_false_unnecessary_high_level_rate"])
        ),
        "zero_candidate_metadata_leakage": leakage_rows == 0,
        "every_native_row_bound": native_invalid_rows == 0,
        "ard_differs_from_native_base_on_protected_adverse_family": bool(mechanism_classes),
    }
    terminal = (
        "P1_R6_PRIMARY_PASS_PENDING_2019_REPLICATION"
        if all(checks.values())
        else "P1_R6_PRIMARY_NOT_SUPPORTED"
    )
    return {
        "schema": "P1U.R6NativePrimary.v1",
        "data": data,
        "policy_outcomes_generated": True,
        "n_episodes": n_episodes,
        "orion_native_ard_grs": _mean([float(value) for value in ard_grs_values]),
        "orion_native_base_grs": _mean([float(value) for value in base_grs_values]),
        "b3_grs": _mean([float(value) for value in b3_grs_values]),
        "episode_ard_minus_b3_grs": episode_diff,
        "episode_bootstrap_95_stability": [episode_lo, episode_hi],
        "domain_differences": domain_means,
        "class_episode_differences": class_means,
        "pair_micro_ard_minus_b3": pair_micro,
        "pair_micro_bootstrap_95_stability": [pair_lo, pair_hi],
        "pair_macro_class_balanced_ard_minus_b3": pair_macro,
        "pair_macro_stratified_bootstrap_95_stability": [macro_lo, macro_hi],
        "substantive_class_pair_differences": pair_class_means,
        "ard_false_high_level_rate": ard_false_high_rate,
        "b3_false_high_level_rate": b3_false_high_rate,
        "ard_harmful_lower_level_skips": ard_lower_skips,
        "ard_false_resolution_unresolved": ard_false_unresolved,
        "ard_harmful_control_high_escalations": harmful_control_high,
        "native_invalid_rows": native_invalid_rows,
        "candidate_metadata_leakage_rows": leakage_rows,
        "ard_base_adverse_difference_classes": mechanism_classes,
        "checks": checks,
        "terminal": terminal,
        "pair_rows": pair_rows,
        "unresolved_rows": unresolved_rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--builder", type=Path, required=True)
    parser.add_argument("--fixed", type=Path, required=True)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    fixed = json.loads(args.fixed.read_text())
    builder = _import_builder(args.builder)
    pairs, unresolved = builder.build()
    result = evaluate(fixed, pairs, unresolved)
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.write_text(text)
    print(text, end="")


if __name__ == "__main__":
    main()

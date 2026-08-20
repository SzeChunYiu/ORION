from __future__ import annotations

import importlib.util
import json
import random
from collections import Counter, defaultdict
from pathlib import Path
from typing import Mapping

ROOT = Path(__file__).resolve().parent
FIXED = json.loads((ROOT / "FIXED_SOURCE_SET_V1.json").read_text())
R2_ROOT = ROOT.parent / "gpt_r2"
R2_PROTOCOL = json.loads((R2_ROOT / "PROTOCOL_V1.json").read_text())

_spec = importlib.util.spec_from_file_location("p1_u_r2_policy_for_r5", R2_ROOT / "policy.py")
assert _spec and _spec.loader
POLICY = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(POLICY)

HIGH = {"OBJECTIVE_OR_MODEL_CLASS", "PROBLEM_BOUNDARY"}
LOW = {"SEARCH_OR_EVIDENCE", "REPRESENTATION_OR_INTERFACE", "IMPLEMENTATION_OR_ENVIRONMENT", "MEASUREMENT_OR_EVALUATOR"}
SUBSTANTIVE = LOW | HIGH
CONTROL = "NO_HIGH_LEVEL_REFORMULATION"
UNRESOLVED = "UNRESOLVED"
PROBES = set(R2_PROTOCOL["probes"])
ALLOWED_OBS = set(R2_PROTOCOL["probe_observations"])
EXPECTED_PAIRS = {r["source_id"]: r for r in FIXED["pair_sources"]}
EXPECTED_UNRES = {r["source_id"]: r for r in FIXED["unresolved_sources"]}
CLASSES = sorted(SUBSTANTIVE)


class ProbeGate(Mapping[str, str]):
    def __init__(self, hidden: Mapping[str, str]):
        if set(hidden) != PROBES:
            raise ValueError("probe set mismatch")
        self._hidden = dict(hidden)
        self.revealed: list[tuple[str, str]] = []

    def __getitem__(self, key: str) -> str:
        value = self._hidden[key]
        self.revealed.append((key, value))
        return value

    def __iter__(self):
        raise RuntimeError("policy may not enumerate hidden probes")

    def __len__(self) -> int:
        return len(self._hidden)


def _validate_episode(ep: Mapping[str, object], expected_gold: str) -> None:
    for k in ("id", "dossier", "probes", "gold_class"):
        if k not in ep:
            raise ValueError(f"episode missing {k}")
    if str(ep["gold_class"]) != expected_gold:
        raise ValueError(f"episode {ep['id']} gold mismatch")
    if set(ep["probes"]) != PROBES or any(v not in ALLOWED_OBS for v in ep["probes"].values()):
        raise ValueError(f"episode {ep['id']} probe encoding invalid")
    if len(str(ep["dossier"]).split()) > 90:
        raise ValueError(f"episode {ep['id']} dossier too long")


def validate_fixed_data(pairs: list[Mapping[str, object]], unresolved: list[Mapping[str, object]]) -> dict[str, object]:
    seen_sources: set[str] = set()
    seen_episodes: set[str] = set()
    domains: set[str] = set()
    class_counts: Counter[str] = Counter()
    errors: list[str] = []

    actual_pair_sources = {str(r.get("source_id", "")) for r in pairs}
    actual_unres_sources = {str(r.get("source_id", "")) for r in unresolved}
    if actual_pair_sources != set(EXPECTED_PAIRS):
        errors.append("pair source set mismatch")
    if actual_unres_sources != set(EXPECTED_UNRES):
        errors.append("unresolved source set mismatch")

    for row in pairs:
        sid = str(row.get("source_id", ""))
        expected = EXPECTED_PAIRS.get(sid)
        if expected is None:
            continue
        for k in ("pair_id", "query_id", "adverse_class", "actual_domain", "source_id", "source_url", "source_year", "adverse", "control", "pair_evidence"):
            if k not in row:
                errors.append(f"{sid} missing {k}")
                continue
        if str(row.get("query_id")) != str(expected["query_id"]) or str(row.get("adverse_class")) != str(expected["class"]):
            errors.append(f"{sid} fixed query/class mismatch")
        if int(row.get("source_year", -1)) != 2020:
            errors.append(f"{sid} wrong source year")
        if sid in seen_sources:
            errors.append(f"duplicate source {sid}")
        seen_sources.add(sid)
        domains.add(str(row.get("actual_domain", "")))
        class_counts[str(row.get("adverse_class", ""))] += 1
        try:
            _validate_episode(row["adverse"], str(expected["class"]))
            _validate_episode(row["control"], CONTROL)
        except (KeyError, ValueError) as exc:
            errors.append(str(exc))
        for ep_key in ("adverse", "control"):
            if ep_key in row and isinstance(row[ep_key], Mapping):
                eid = str(row[ep_key].get("id", ""))
                if eid in seen_episodes:
                    errors.append(f"duplicate episode {eid}")
                seen_episodes.add(eid)
        if not isinstance(row.get("pair_evidence"), Mapping) or not row.get("pair_evidence"):
            errors.append(f"{sid} missing pair evidence")

    for row in unresolved:
        sid = str(row.get("source_id", ""))
        expected = EXPECTED_UNRES.get(sid)
        if expected is None:
            continue
        for k in ("id", "query_id", "actual_domain", "source_id", "source_url", "source_year", "dossier", "probes", "gold_class", "admission_evidence"):
            if k not in row:
                errors.append(f"{sid} missing {k}")
        if str(row.get("query_id")) != str(expected["query_id"]):
            errors.append(f"{sid} fixed query mismatch")
        if int(row.get("source_year", -1)) != 2020:
            errors.append(f"{sid} wrong source year")
        if sid in seen_sources:
            errors.append(f"duplicate source {sid}")
        seen_sources.add(sid)
        domains.add(str(row.get("actual_domain", "")))
        try:
            _validate_episode(row, UNRESOLVED)
        except ValueError as exc:
            errors.append(str(exc))
        eid = str(row.get("id", ""))
        if eid in seen_episodes:
            errors.append(f"duplicate episode {eid}")
        seen_episodes.add(eid)
        if not isinstance(row.get("admission_evidence"), Mapping) or not row.get("admission_evidence"):
            errors.append(f"{sid} missing admission evidence")

    class_min = all(class_counts.get(c, 0) >= int(FIXED["minimum_pair_sources_per_substantive_class"]) for c in CLASSES)
    checks = {
        "exact_pair_source_set": actual_pair_sources == set(EXPECTED_PAIRS),
        "exact_unresolved_source_set": actual_unres_sources == set(EXPECTED_UNRES),
        "expected_pair_count": len(pairs) == int(FIXED["expected_pair_source_count"]),
        "expected_unresolved_count": len(unresolved) == int(FIXED["expected_unresolved_source_count"]),
        "expected_episode_count": len(seen_episodes) == int(FIXED["expected_episode_count"]),
        "minimum_pairs_per_class": class_min,
        "minimum_domains": len(domains) >= int(FIXED["minimum_actual_domains"]),
        "no_validation_errors": not errors,
    }
    return {"complete": all(checks.values()), "checks": checks, "errors": errors, "class_counts": dict(sorted(class_counts.items())), "n_domains": len(domains)}


def _run(name: str, ep: Mapping[str, object]) -> dict[str, object]:
    gate = ProbeGate(ep["probes"])
    visible = {"dossier": str(ep["dossier"]), "probes": gate}
    if name == "B3_HORIZON2_DONOR_COMPLETE":
        result = POLICY.donor_complete_policy(visible, horizon=2)
    elif name == "ORION_R2":
        result = POLICY.orion_r2_policy(visible)
    else:
        raise KeyError(name)
    trace = [(str(t["probe"]), str(t["observation"])) for t in result["trace"]]
    if gate.revealed != trace or int(result["cost"]) != len(gate.revealed):
        raise AssertionError(f"hidden-probe/cost mismatch on {ep['id']} for {name}")
    if int(result["cost"]) > int(R2_PROTOCOL["budget"]):
        raise AssertionError(f"budget exceeded on {ep['id']}")
    gold, choice = str(ep["gold_class"]), str(result["choice"])
    return {
        "choice": choice,
        "grs": int(choice == gold),
        "false_high_level": int(choice in HIGH and gold not in HIGH),
        "harmful_lower_level_skip": int(choice in HIGH and gold in LOW),
        "false_resolution_of_unresolved": int(gold == UNRESOLVED and choice != UNRESOLVED),
        "cost": int(result["cost"]),
        "trace": result["trace"],
    }


def _mean(xs: list[float]) -> float:
    return sum(xs) / len(xs) if xs else 0.0


def _bootstrap(diffs: list[float], reps: int, seed: int, interval: float) -> tuple[float, float]:
    rng = random.Random(seed)
    n = len(diffs)
    vals = [sum(diffs[rng.randrange(n)] for _ in range(n)) / n for _ in range(reps)]
    vals.sort()
    alpha = 1.0 - interval
    return vals[int((alpha/2)*reps)], vals[min(reps-1, int((1-alpha/2)*reps)-1)]


def _stratified_macro_bootstrap(by_class: Mapping[str, list[float]], reps: int, seed: int, interval: float) -> tuple[float, float]:
    rng = random.Random(seed)
    vals = []
    classes = sorted(by_class)
    for _ in range(reps):
        class_means = []
        for c in classes:
            xs = by_class[c]
            class_means.append(sum(xs[rng.randrange(len(xs))] for _ in range(len(xs))) / len(xs))
        vals.append(sum(class_means) / len(class_means))
    vals.sort()
    alpha = 1.0 - interval
    return vals[int((alpha/2)*reps)], vals[min(reps-1, int((1-alpha/2)*reps)-1)]


def evaluate(pairs: list[Mapping[str, object]], unresolved: list[Mapping[str, object]]) -> dict[str, object]:
    data = validate_fixed_data(pairs, unresolved)
    if not data["complete"]:
        return {"schema":"P1U.R5.Result.v1", "data":data, "policy_outcomes_generated":False, "terminal":"P1_R5_CANNOT_CHECK_FIXED_DATA"}

    pair_rows = []
    episode_diffs: list[float] = []
    domain_diffs: dict[str, list[float]] = defaultdict(list)
    orion_false_high = b3_false_high = 0
    orion_lower_skips = orion_false_unres = 0
    control_harm = 0

    for p in pairs:
        outs = {}
        for name in ("ORION_R2", "B3_HORIZON2_DONOR_COMPLETE"):
            a = _run(name, p["adverse"])
            c = _run(name, p["control"])
            outs[name] = {"adverse":a, "control":c, "pair_selective_success":int(a["grs"] and c["grs"])}
        for member in ("adverse", "control"):
            o = outs["ORION_R2"][member]
            b = outs["B3_HORIZON2_DONOR_COMPLETE"][member]
            d = o["grs"] - b["grs"]
            episode_diffs.append(d)
            domain_diffs[str(p["actual_domain"])].append(d)
            orion_false_high += o["false_high_level"]
            b3_false_high += b["false_high_level"]
            orion_lower_skips += o["harmful_lower_level_skip"]
        control_harm += outs["ORION_R2"]["control"]["false_high_level"]
        pair_rows.append({"pair_id":p["pair_id"], "adverse_class":p["adverse_class"], "actual_domain":p["actual_domain"], "source_id":p["source_id"], "outcomes":outs})

    unres_rows = []
    for ep in unresolved:
        o, b = _run("ORION_R2", ep), _run("B3_HORIZON2_DONOR_COMPLETE", ep)
        d = o["grs"] - b["grs"]
        episode_diffs.append(d)
        domain_diffs[str(ep["actual_domain"])].append(d)
        orion_false_high += o["false_high_level"]
        b3_false_high += b["false_high_level"]
        orion_false_unres += o["false_resolution_of_unresolved"]
        unres_rows.append({"id":ep["id"], "source_id":ep["source_id"], "orion":o, "b3":b})

    n_episodes = len(episode_diffs)
    episode_diff = _mean(episode_diffs)
    r2 = R2_PROTOCOL["decision_rule"]
    ep_lo, ep_hi = _bootstrap(episode_diffs, int(r2["paired_bootstrap_replicates"]), int(r2["paired_bootstrap_seed"]), float(r2["stability_interval"]))
    domain_means = {k:_mean(v) for k,v in sorted(domain_diffs.items())}

    pair_diffs = [r["outcomes"]["ORION_R2"]["pair_selective_success"] - r["outcomes"]["B3_HORIZON2_DONOR_COMPLETE"]["pair_selective_success"] for r in pair_rows]
    pair_micro = _mean(pair_diffs)
    pair_lo, pair_hi = _bootstrap(pair_diffs, 20000, 20260820, 0.95)
    by_class: dict[str, list[float]] = defaultdict(list)
    for r,d in zip(pair_rows,pair_diffs): by_class[str(r["adverse_class"])].append(d)
    class_means = {c:_mean(by_class[c]) for c in sorted(by_class)}
    pair_macro = _mean(list(class_means.values()))
    macro_lo, macro_hi = _stratified_macro_bootstrap(by_class, 20000, 20260820, 0.95)

    orion_grs = _mean([r["outcomes"]["ORION_R2"][m]["grs"] for r in pair_rows for m in ("adverse","control")] + [r["orion"]["grs"] for r in unres_rows])
    b3_grs = _mean([r["outcomes"]["B3_HORIZON2_DONOR_COMPLETE"][m]["grs"] for r in pair_rows for m in ("adverse","control")] + [r["b3"]["grs"] for r in unres_rows])
    orion_false_high_rate = orion_false_high / n_episodes
    b3_false_high_rate = b3_false_high / n_episodes
    nonneg = sum(v >= 0 for v in class_means.values())

    checks = {
        "episode_paired_margin": episode_diff >= float(r2["paired_grs_margin"]),
        "episode_stability_lower_positive": ep_lo > 0,
        "domain_noninferiority": all(v >= float(r2["domain_noninferiority_floor"]) for v in domain_means.values()),
        "unnecessary_high_level_guard": orion_false_high_rate <= b3_false_high_rate and orion_false_high_rate <= float(r2["max_orion_false_unnecessary_high_level_rate"]),
        "zero_lower_level_skip": orion_lower_skips <= int(r2["harmful_lower_level_skip_tolerance"]),
        "zero_false_unresolved_resolution": orion_false_unres <= int(r2["false_resolution_of_unresolved_tolerance"]),
        "pair_micro_margin": pair_micro >= 0.10,
        "pair_micro_stability_lower_positive": pair_lo > 0,
        "pair_macro_margin": pair_macro >= 0.10,
        "pair_macro_stability_lower_positive": macro_lo > 0,
        "zero_harmful_control_high_escalation": control_harm == 0,
        "minimum_nonnegative_classes": nonneg >= 3,
        "class_floor": all(v >= -0.10 for v in class_means.values()),
    }
    terminal = "P1_R5_PRIMARY_PASS_PENDING_2019_REPLICATION" if all(checks.values()) else "P1_R5_PRIMARY_NOT_SUPPORTED"
    return {
        "schema":"P1U.R5.Result.v1", "data":data, "policy_outcomes_generated":True,
        "n_episodes":n_episodes, "orion_grs":orion_grs, "b3_grs":b3_grs,
        "episode_orion_minus_b3_grs":episode_diff, "episode_bootstrap_95_stability":[ep_lo,ep_hi], "domain_differences":domain_means,
        "pair_micro_orion_minus_b3":pair_micro, "pair_micro_bootstrap_95_stability":[pair_lo,pair_hi],
        "pair_macro_class_balanced_orion_minus_b3":pair_macro, "pair_macro_stratified_bootstrap_95_stability":[macro_lo,macro_hi],
        "substantive_class_pair_differences":class_means,
        "orion_false_high_level_rate":orion_false_high_rate, "b3_false_high_level_rate":b3_false_high_rate,
        "orion_harmful_lower_level_skips":orion_lower_skips, "orion_false_resolution_unresolved":orion_false_unres,
        "orion_harmful_control_high_escalations":control_harm, "checks":checks, "terminal":terminal,
        "pair_rows":pair_rows, "unresolved_rows":unres_rows,
    }


def main() -> None:
    import argparse
    ap = argparse.ArgumentParser(); ap.add_argument("pairs", type=Path); ap.add_argument("unresolved", type=Path); ap.add_argument("--out", type=Path)
    a = ap.parse_args(); r = evaluate(json.loads(a.pairs.read_text()), json.loads(a.unresolved.read_text()))
    txt = json.dumps(r, indent=2, sort_keys=True) + "\n"
    if a.out: a.out.write_text(txt)
    print(txt, end="")

if __name__ == "__main__": main()

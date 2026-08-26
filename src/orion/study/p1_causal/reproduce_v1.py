"""Independently re-derive frozen P1 V1 headline facts from raw artifacts.

Never writes V1 tables. Emits an additive receipt under research/revival/p1/.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from collections.abc import Iterable
from pathlib import Path

from orion.study.p1.precision_tier import TierRule
from orion.study.p1.statistics import paired_bootstrap_difference

REPO_ROOT = Path(__file__).resolve().parents[4]
PAPER01 = REPO_ROOT / "papers" / "orion-11-recursive-epistemic-reconstruction"
SCORED = PAPER01 / "results" / "raw" / "test_scored.jsonl"
RUNS = PAPER01 / "results" / "raw" / "test_runs.jsonl"
T2_JSON = PAPER01 / "results" / "P1-T2_baseline_ablation_results.json"
T3_JSON = PAPER01 / "results" / "P1-T3_failure_taxonomy.json"
T2_MD = PAPER01 / "results" / "P1-T2_baseline_ablation_results.md"
T3_MD = PAPER01 / "results" / "P1-T3_failure_taxonomy.md"
V1_PROTOCOL = PAPER01 / "protocol" / "PROTOCOL_V1.json"
RECEIPT_PATH = (
    REPO_ROOT / "research" / "revival" / "p1" / "receipts" / "V1_REPRODUCTION_RECEIPT.json"
)

FROZEN_SUITE = "21b461d89280631b93b766d6fb000c7f9f5fbeccee7cb6664f238c2c5c8e6420"
FROZEN_REPEATS = 5
FROZEN_CASES = 48
FROZEN_SYSTEMS = 12
BOOTSTRAP_SEED = 20260815
BOOTSTRAP_RESAMPLES = 10000
SUBJECT = "orion_full"
COMPARATOR = "arex_like_recursive_audit_followup"
LIVE = "orion_live_provider"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_jsonl(path: Path) -> list[dict]:
    records = []
    for number, line in enumerate(path.read_text().splitlines(), start=1):
        if not line.strip():
            continue
        payload = json.loads(line)
        if not isinstance(payload, dict):
            raise ValueError(f"{path}:{number} is not an object")
        records.append(payload)
    return records


def _majority(flags: Iterable[bool]) -> bool:
    items = list(flags)
    return sum(1 for flag in items if flag) * 2 > len(items)


def _seed_mean(flags: Iterable[bool]) -> float:
    items = list(flags)
    return sum(1.0 for flag in items if flag) / len(items) if items else 0.0


def _groups(records: list[dict], system_id: str) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for record in records:
        if record["system_id"] == system_id:
            grouped[record["case_id"]].append(record)
    return grouped


def _claimed_facts() -> dict:
    return {
        "scored_records": 2880,
        "n_cases": FROZEN_CASES,
        "repeats_per_case": FROZEN_REPEATS,
        "cannot_check_after_stale_table_repair": 0,
        "suite_fingerprint_prefix": "21b461d8",
        "orion_full_root_success": {"successes": 1, "n": 48, "rate": 0.0208},
        "tied_with_arex_like": True,
        "h1_paired_difference": {"point": 0.0, "low": 0.0, "high": 0.0},
        "orion_full_abstention": {"cases": 47, "trials": 235, "trial_denominator": 240},
        "live_missed_reframe": {"cases": 32, "trials": 160},
        "live_wrong_responsibility": {"cases": 16, "trials": 80},
        "v1_underpowered_for_plus_0_05": True,
    }


def reproduce_v1(*, scored_path: Path = SCORED) -> dict:
    """Re-derive headline facts. Returns a receipt; does not touch V1 files."""

    artifacts = {
        "test_scored.jsonl": {"path": str(scored_path.relative_to(REPO_ROOT)), "sha256": _sha256(scored_path)},
        "test_runs.jsonl": {"path": str(RUNS.relative_to(REPO_ROOT)), "sha256": _sha256(RUNS)},
        "P1-T2.json": {"path": str(T2_JSON.relative_to(REPO_ROOT)), "sha256": _sha256(T2_JSON)},
        "P1-T3.json": {"path": str(T3_JSON.relative_to(REPO_ROOT)), "sha256": _sha256(T3_JSON)},
        "P1-T2.md": {"path": str(T2_MD.relative_to(REPO_ROOT)), "sha256": _sha256(T2_MD)},
        "P1-T3.md": {"path": str(T3_MD.relative_to(REPO_ROOT)), "sha256": _sha256(T3_MD)},
        "PROTOCOL_V1.json": {
            "path": str(V1_PROTOCOL.relative_to(REPO_ROOT)),
            "sha256": _sha256(V1_PROTOCOL),
        },
    }
    records = _load_jsonl(scored_path)
    blockers: list[str] = []
    n = len(records)
    systems = sorted({record["system_id"] for record in records})
    cases = sorted({record["case_id"] for record in records})
    seeds = sorted({record["seed"] for record in records})
    fingerprints = sorted({record["suite_fingerprint"] for record in records})
    revisions = sorted({record["subject_revision"] for record in records})
    statuses = Counter(record.get("status") for record in records)
    cannot_check = sum(1 for record in records if record.get("status") == "CANNOT_CHECK")
    nonempty_reason = sum(1 for record in records if record.get("cannot_check_reason"))
    repeats = Counter()
    for record in records:
        repeats[(record["system_id"], record["case_id"])] += 1
    repeat_set = sorted(set(repeats.values()))

    if n != 2880:
        blockers.append(f"record_count:{n}!=2880")
    if len(systems) != FROZEN_SYSTEMS:
        blockers.append(f"n_systems:{len(systems)}")
    if len(cases) != FROZEN_CASES:
        blockers.append(f"n_cases:{len(cases)}")
    if seeds != [0, 1, 2, 3, 4]:
        blockers.append(f"seeds:{seeds}")
    if repeat_set != [FROZEN_REPEATS]:
        blockers.append(f"repeats:{repeat_set}")
    if cannot_check != 0 or nonempty_reason != 0:
        blockers.append(f"cannot_check:{cannot_check}:reasons:{nonempty_reason}")
    if fingerprints != [FROZEN_SUITE]:
        blockers.append(f"fingerprint:{fingerprints}")
    if not FROZEN_SUITE.startswith("21b461d8"):
        blockers.append("fingerprint_prefix")

    of = _groups(records, SUBJECT)
    arex = _groups(records, COMPARATOR)
    live = _groups(records, LIVE)
    of_flags = {cid: [bool(item["root_success"]) for item in rows] for cid, rows in of.items()}
    arex_flags = {
        cid: [bool(item["root_success"]) for item in rows] for cid, rows in arex.items()
    }
    of_success_cases = sum(1 for flags in of_flags.values() if _majority(flags))
    arex_success_cases = sum(1 for flags in arex_flags.values() if _majority(flags))
    of_rate = of_success_cases / len(of_flags) if of_flags else None
    shared = sorted(set(of_flags) & set(arex_flags))
    maj_a = [1.0 if _majority(of_flags[cid]) else 0.0 for cid in shared]
    maj_b = [1.0 if _majority(arex_flags[cid]) else 0.0 for cid in shared]
    mean_a = [_seed_mean(of_flags[cid]) for cid in shared]
    mean_b = [_seed_mean(arex_flags[cid]) for cid in shared]
    h1 = paired_bootstrap_difference(
        maj_a, maj_b, resamples=BOOTSTRAP_RESAMPLES, seed=BOOTSTRAP_SEED
    )
    seed_mean_diff = (
        sum(left - right for left, right in zip(mean_a, mean_b, strict=True)) / len(shared)
        if shared
        else None
    )
    of_trials = [item for rows in of.values() for item in rows]
    abstention_trials = sum(1 for item in of_trials if item.get("failure_mode") == "ABSTENTION")
    abstention_cases = sum(
        1
        for rows in of.values()
        if all(item.get("failure_mode") == "ABSTENTION" for item in rows)
    )
    live_trials = [item for rows in live.values() for item in rows]
    live_modes = Counter(item.get("failure_mode") for item in live_trials)
    live_mode_cases = {
        mode: len({item["case_id"] for item in live_trials if item.get("failure_mode") == mode})
        for mode in live_modes
    }
    if of_success_cases != 1 or round(of_rate or 0.0, 4) != 0.0208:
        blockers.append(f"orion_full_root_success:{of_success_cases}/{len(of_flags)}")
    if arex_success_cases != of_success_cases:
        blockers.append("not_tied_with_arex")
    if h1.point != 0.0 or h1.low != 0.0 or h1.high != 0.0:
        blockers.append(f"h1:{h1.point},{h1.low},{h1.high}")
    if abstention_cases != 47 or abstention_trials != 235:
        blockers.append(f"abstention:{abstention_cases}cases/{abstention_trials}trials")
    if live_modes.get("MISSED_REFRAME") != 160 or live_mode_cases.get("MISSED_REFRAME") != 32:
        blockers.append(f"live_missed_reframe:{live_mode_cases.get('MISSED_REFRAME')}/{live_modes.get('MISSED_REFRAME')}")
    if live_modes.get("WRONG_RESPONSIBILITY") != 80 or live_mode_cases.get("WRONG_RESPONSIBILITY") != 16:
        blockers.append(
            "live_wrong_responsibility:"
            f"{live_mode_cases.get('WRONG_RESPONSIBILITY')}/{live_modes.get('WRONG_RESPONSIBILITY')}"
        )
    tier = TierRule.from_n(len(of_flags))
    if not tier.underpowered or tier.licenses_h1_superiority:
        blockers.append(f"tier:{tier.tier.value}")
    h_r6_masks = bool(
        seed_mean_diff not in (0.0, None) and (h1.point == 0.0)
    )
    verdict = "VERIFIED" if not blockers else "DATA_INTEGRITY_BLOCKER"
    return {
        "schema_version": "orion.p1.v1-reproduction-receipt.v1",
        "issue": 278,
        "verdict": verdict,
        "v1_files_mutated": False,
        "main_head_at_reproduction": None,
        "artifacts": artifacts,
        "archive": {
            "n_scored_records": n,
            "n_systems": len(systems),
            "system_ids": systems,
            "n_cases": len(cases),
            "seeds": seeds,
            "repeats_per_system_case": repeat_set,
            "statuses": dict(statuses),
            "cannot_check_records": cannot_check,
            "cannot_check_reasons_nonempty": nonempty_reason,
            "suite_fingerprints": fingerprints,
            "subject_revisions": revisions,
        },
        "orion_full": {
            "n_trials": len(of_trials),
            "majority_root_success_cases": of_success_cases,
            "n_cases": len(of_flags),
            "rate": of_rate,
            "rate_4dp": round(of_rate, 4) if of_rate is not None else None,
            "abstention_cases_all_repeats": abstention_cases,
            "abstention_trials": abstention_trials,
            "failure_modes": dict(Counter(item.get("failure_mode") for item in of_trials)),
        },
        "comparator": {
            "system_id": COMPARATOR,
            "majority_root_success_cases": arex_success_cases,
            "n_cases": len(arex_flags),
        },
        "h1": {
            "metric": "root_success",
            "reduction": "MAJORITY",
            "matched_units": len(shared),
            "point": h1.point,
            "low": h1.low,
            "high": h1.high,
            "two_sided_p": h1.two_sided_p,
            "resamples": h1.resamples,
            "seed": h1.seed,
            "seed_mean_difference_point": seed_mean_diff,
            "h_r6_majority_masks_seed_gains": h_r6_masks,
        },
        "orion_live_provider": {
            "n_trials": len(live_trials),
            "failure_modes": dict(live_modes),
            "failure_mode_cases": live_mode_cases,
        },
        "power": {
            "n": tier.n,
            "tier": tier.tier.value,
            "half_width_p05": tier.half_width,
            "underpowered": tier.underpowered,
            "licenses_h1_superiority": tier.licenses_h1_superiority,
            "frozen_h1_margin": 0.05,
        },
        "claimed_facts": _claimed_facts(),
        "blockers": blockers,
    }


def write_receipt(
    receipt: dict | None = None,
    *,
    path: Path = RECEIPT_PATH,
    head_sha: str | None = None,
) -> Path:
    payload = receipt if receipt is not None else reproduce_v1()
    if head_sha is not None:
        payload = {**payload, "main_head_at_reproduction": head_sha}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    return path


def main() -> int:
    import subprocess

    head = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True
    ).strip()
    receipt = reproduce_v1()
    write_receipt(receipt, head_sha=head)
    print(receipt["verdict"])
    print("blockers", receipt["blockers"])
    return 0 if receipt["verdict"] == "VERIFIED" else 2


if __name__ == "__main__":
    raise SystemExit(main())

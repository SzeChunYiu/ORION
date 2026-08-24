"""Execute frozen P13C composed safety-efficacy benchmark in two fresh subprocesses.

Composes the P13B authenticated-certificate mechanism (imported unchanged from
src/orion/study/p13/authenticated_successor.py) with the P13A randomized
efficacy benchmark (same seed, families, episode structure, truth model, costs)
over the six-form certificate class, under the four-world corruption register
at the frozen 1-in-5 schedule of P13C_COMPOSED_SAFETY_EFFICACY_PROTOCOL_V1.md.
"""

from __future__ import annotations

import argparse
import json
import platform
import random
import subprocess
import sys
import tempfile
from hashlib import sha256
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT))

from orion.study.p13.authenticated_successor import (  # noqa: E402
    CURRENT_EPOCH,
    TRUSTED_ISSUER,
    WORLDS,
    canonical_text,
    corrupt_certificate,
    file_sha256,
    gold_support,
    valid_certificate,
    validate_certificate,
)

SPEC = HERE / "P13C_COMPOSED_GOLD_SPEC_V1.json"
PROTOCOL = HERE / "P13C_COMPOSED_SAFETY_EFFICACY_PROTOCOL_V1.md"
OUT = HERE / "P13C_COMPOSED_RESULT_V1.json"

SEED = 2026082113
N_FAMILIES = 24
N = 512
RECOVER_P = 0.95
CONF_T = 0.80
TASKS = ("PREDICT", "DECIDE", "INTERVENE", "VERIFY", "REPAIR")
FORMS = ("Z1", "Z2", "Z3", "Z4", "Z5", "Z6")
COST = {"REUSE": 1.0, "REOPEN": 6.0, "CANNOT_CHECK": 0.5}
ARMS = ("UNQUALIFIED", "CONFIDENCE_ONLY", "UNVERIFIED_RCS", "AUTHENTICATED_RCS", "ALWAYS_RAW")
PARENT_FORMS = ("Z5", "Z1")  # P13A Z1 (x only) and P13A Z2 (x, m) under the P13C spec
SUPPORTED = "P13C_COMPOSED_SAFETY_EFFICACY_SUPPORTED"
NOT_SUPPORTED = "P13C_COMPOSED_SAFETY_EFFICACY_GATE_NOT_MET"

# Exact input sets of the P13A truth functions; mirrors the registered spec.
TASK_INPUTS = {
    "PREDICT": frozenset({"x"}),
    "DECIDE": frozenset({"x"}),
    "INTERVENE": frozenset({"x", "m"}),
    "VERIFY": frozenset({"x", "m"}),
    "REPAIR": frozenset({"r"}),
}
P13A_SUPPORT = {
    "Z1": {"PREDICT", "DECIDE"},
    "Z2": {"PREDICT", "DECIDE", "INTERVENE", "VERIFY"},
}


def truth(x, m, r, task):
    return {
        "PREDICT": x,
        "DECIDE": x,
        "INTERVENE": x * m,
        "VERIFY": x * m,
        "REPAIR": r,
    }[task]


def compact_pred(form_vars, x, m, r, task, p_m, p_r):
    if TASK_INPUTS[task] <= form_vars:
        return truth(x, m, r, task)
    map_m = 1 if p_m >= 0.5 else -1
    map_r = 1 if p_r >= 0.5 else -1
    if task in ("INTERVENE", "VERIFY"):
        return x * map_m
    if task == "REPAIR":
        return map_r
    raise AssertionError(task)


def confidence(form_vars, task, p_m, p_r):
    if TASK_INPUTS[task] <= form_vars:
        return 1.0
    if task in ("INTERVENE", "VERIFY"):
        return max(p_m, 1 - p_m)
    if task == "REPAIR":
        return max(p_r, 1 - p_r)
    return 1.0


def gold_consistency(spec):
    """Gate G1: the P13C subset rule reproduces the P13A truth-model semantics."""
    support_sets = {
        z: {t for t in TASKS if gold_support(spec, z, t)} for z in FORMS
    }
    parent_embedding_ok = (
        support_sets["Z5"] == P13A_SUPPORT["Z1"]
        and support_sets["Z1"] == P13A_SUPPORT["Z2"]
    )
    # Parent exact responsibility matrix, generalized to all six forms: a form's
    # variables determine the task truth iff the task inputs are contained in them.
    cube = [(x, m, r) for x in (-1, 1) for m in (-1, 1) for r in (-1, 1)]
    matrix = {}
    for z in FORMS:
        key_vars = [v for v in ("x", "m", "r") if v in set(spec["state_forms"][z])]
        matrix[z] = {}
        for task in TASKS:
            groups = {}
            for x, m, r in cube:
                values = {"x": x, "m": m, "r": r}
                k = tuple(values[v] for v in key_vars)
                groups.setdefault(k, set()).add(truth(x, m, r, task))
            matrix[z][task] = all(len(vals) == 1 for vals in groups.values())
    matrix_matches_gold = all(
        matrix[z][task] == gold_support(spec, z, task) for z in FORMS for task in TASKS
    )
    return {
        "support_sets": {z: sorted(s) for z, s in support_sets.items()},
        "parent_embedding_ok": parent_embedding_ok,
        "matrix_matches_gold": matrix_matches_gold,
        "exact_matrix": matrix,
    }


def build_core():
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    consistency = gold_consistency(spec)
    rng = random.Random(SEED)

    zero = {
        "unsafe": 0,
        "correct": 0,
        "unnecessary_reopen": 0,
        "cannot_total": 0,
        "cannot_expected": 0,
        "cost": 0.0,
    }
    totals = {arm: dict(zero) for arm in ARMS}
    valid_panel = {arm: dict(zero) for arm in ARMS}
    subpanel = {"AUTHENTICATED_RCS": dict(zero), "ALWAYS_RAW": dict(zero), "episodes": 0}
    unverified_by_world = {
        world: {"unsafe": 0, "unnecessary_reopen": 0, "episodes": 0} for world in WORLDS
    }
    adversary_forced_reopens = 0
    corrupted_total = 0
    rejected_total = 0
    valid_certificates = 0
    episodes = 0

    for family in range(N_FAMILIES):
        p_m = rng.uniform(0.65, 0.95)
        p_r = rng.uniform(0.65, 0.95)
        for j in range(N):
            x = rng.choice((-1, 1))
            m = 1 if rng.random() < p_m else -1
            r = 1 if rng.random() < p_r else -1
            z = rng.choice(FORMS)
            task = rng.choice(TASKS)
            recover = rng.random() < RECOVER_P
            i = family * N + j
            corrupted = (i % 5) == 4
            world = WORLDS[(i // 5) % 4] if corrupted else None

            form_vars = frozenset(spec["state_forms"][z])
            gold = gold_support(spec, z, task)
            y = truth(x, m, r, task)

            certificate = valid_certificate(spec, z)
            if corrupted:
                certificate = corrupt_certificate(certificate, world, spec, z)
                corrupted_total += 1
                if not validate_certificate(certificate, spec, z):
                    rejected_total += 1
            is_valid = validate_certificate(certificate, spec, z)
            if is_valid:
                valid_certificates += 1
            declared = bool(certificate["declared_support"][task])

            actions = {
                "UNQUALIFIED": "REUSE",
                "CONFIDENCE_ONLY": (
                    "REUSE"
                    if confidence(form_vars, task, p_m, p_r) >= CONF_T
                    else ("REOPEN" if recover else "CANNOT_CHECK")
                ),
                "UNVERIFIED_RCS": (
                    "REUSE" if declared else ("REOPEN" if recover else "CANNOT_CHECK")
                ),
                "AUTHENTICATED_RCS": (
                    ("REUSE" if declared else ("REOPEN" if recover else "CANNOT_CHECK"))
                    if is_valid
                    else ("REOPEN" if recover else "CANNOT_CHECK")
                ),
                "ALWAYS_RAW": "REOPEN" if recover else "CANNOT_CHECK",
            }
            if not is_valid and recover and actions["AUTHENTICATED_RCS"] == "REOPEN":
                adversary_forced_reopens += 1

            # Independent recount of the authenticated arm's cannot-check set (G9).
            auth_cannot_expected = (
                (not is_valid and not recover)
                or (is_valid and not gold and not recover)
            )

            episodes += 1
            in_subpanel = is_valid and z in PARENT_FORMS
            if in_subpanel:
                subpanel["episodes"] += 1

            for arm, action in actions.items():
                bucket = totals[arm]
                if action == "REUSE":
                    pred = compact_pred(form_vars, x, m, r, task, p_m, p_r)
                    bucket["correct"] += int(pred == y)
                    bucket["unsafe"] += int(not gold)
                elif action == "REOPEN":
                    bucket["correct"] += 1
                    bucket["unnecessary_reopen"] += int(gold)
                else:
                    bucket["cannot_total"] += 1
                bucket["cost"] += COST[action]
                if is_valid:
                    vb = valid_panel[arm]
                    if action == "REUSE":
                        pred = compact_pred(form_vars, x, m, r, task, p_m, p_r)
                        vb["correct"] += int(pred == y)
                        vb["unsafe"] += int(not gold)
                    elif action == "REOPEN":
                        vb["correct"] += 1
                        vb["unnecessary_reopen"] += int(gold)
                    else:
                        vb["cannot_total"] += 1
                    vb["cost"] += COST[action]
                if arm == "AUTHENTICATED_RCS":
                    bucket["cannot_expected"] += int(auth_cannot_expected)
                    if in_subpanel:
                        sb = subpanel["AUTHENTICATED_RCS"]
                        if action == "REUSE":
                            sb["unsafe"] += int(not gold)
                            sb["correct"] += int(
                                compact_pred(form_vars, x, m, r, task, p_m, p_r) == y
                            )
                        elif action == "REOPEN":
                            sb["unnecessary_reopen"] += int(gold)
                            sb["correct"] += 1
                        sb["cost"] += COST[action]
                if arm == "ALWAYS_RAW" and in_subpanel:
                    sb = subpanel["ALWAYS_RAW"]
                    if action == "REOPEN":
                        sb["correct"] += 1
                    sb["cost"] += COST[action]
                if arm == "UNVERIFIED_RCS" and corrupted:
                    w = unverified_by_world[world]
                    w["episodes"] += 1
                    if action == "REUSE":
                        w["unsafe"] += int(not gold)
                    elif action == "REOPEN":
                        w["unnecessary_reopen"] += int(gold)

    return {
        "schema": "ORION.P13C.ComposedSafetyEfficacy.Core.v1",
        "paper_id": "P13",
        "claim_id": "P13C_COMPOSED_SAFETY_EFFICACY",
        "authority_boundary": "registered_composed_finite_world_randomized",
        "protocol": str(PROTOCOL.relative_to(REPO_ROOT)),
        "protocol_sha256": file_sha256(PROTOCOL),
        "gold_spec": str(SPEC.relative_to(REPO_ROOT)),
        "gold_spec_sha256": file_sha256(SPEC),
        "subject_identity": {
            "trusted_issuer": TRUSTED_ISSUER,
            "current_epoch": CURRENT_EPOCH,
            "certificate_machinery": "src/orion/study/p13/authenticated_successor.py (imported unchanged)",
            "validator": "issuer_subject_epoch_mapping_witness_digest_v1",
        },
        "environment": {
            "python_implementation": platform.python_implementation(),
            "python_version": platform.python_version(),
        },
        "episode_design": {
            "seed": SEED,
            "n_families": N_FAMILIES,
            "episodes_per_family": N,
            "total_episodes": episodes,
            "form_class": list(FORMS),
            "tasks": list(TASKS),
            "recover_p": RECOVER_P,
            "rng": "stdlib random.Random (distribution-identical to parent numpy stream)",
            "corruption_schedule": "global episode index i corrupted iff i%5==4; world=WORLDS[(i//5)%4]",
            "costs": COST,
        },
        "gold_consistency": consistency,
        "counts": {
            "episodes": episodes,
            "corrupted_episodes": corrupted_total,
            "corrupted_certificates_rejected": rejected_total,
            "valid_certificates": valid_certificates,
            "adversary_forced_reopens_authenticated": adversary_forced_reopens,
        },
        "totals": totals,
        "valid_panel": valid_panel,
        "parent_form_subpanel": subpanel,
        "unverified_by_world": unverified_by_world,
    }


def _rates(bucket, denom):
    return {
        "unsafe_reuse": bucket["unsafe"],
        "verified_correct": bucket["correct"],
        "unnecessary_reopen": bucket["unnecessary_reopen"],
        "cannot_check": bucket["cannot_total"],
        "unsafe_reuse_rate": bucket["unsafe"] / denom,
        "verified_correct_rate": bucket["correct"] / denom,
        "unnecessary_reopen_rate": bucket["unnecessary_reopen"] / denom,
        "mean_cost": bucket["cost"] / denom,
    }


def adjudicate(core, *, byte_identical_replay):
    n = core["counts"]["episodes"]
    valid_n = core["counts"]["valid_certificates"]
    summary = {
        "arms": {arm: _rates(core["totals"][arm], n) for arm in ARMS},
        "valid_panel": {arm: _rates(core["valid_panel"][arm], valid_n) for arm in ARMS},
        "unverified_by_world": core["unverified_by_world"],
    }
    auth = summary["arms"]["AUTHENTICATED_RCS"]
    unv = summary["arms"]["UNVERIFIED_RCS"]
    raw = summary["arms"]["ALWAYS_RAW"]
    auth_valid = summary["valid_panel"]["AUTHENTICATED_RCS"]
    sub = core["parent_form_subpanel"]
    sub_auth_cost = sub["AUTHENTICATED_RCS"]["cost"] / sub["episodes"]
    sub_raw_cost = sub["ALWAYS_RAW"]["cost"] / sub["episodes"]
    by_world = core["unverified_by_world"]
    consistency = core["gold_consistency"]

    gates = {
        "G1_gold_spec_matches_p13a_truth_model": (
            consistency["parent_embedding_ok"] and consistency["matrix_matches_gold"]
        ),
        "G2_authenticated_zero_unsafe_reuse_overall": auth["unsafe_reuse"] == 0,
        "G3_authenticated_zero_unnecessary_reopen_valid_panel": (
            auth_valid["unnecessary_reopen"] == 0
        ),
        "G4_authenticated_correct_noninferior_always_raw_0_01": (
            auth["verified_correct_rate"] >= raw["verified_correct_rate"] - 0.01
        ),
        "G5_authenticated_correct_noninferior_unverified_0_01": (
            auth["verified_correct_rate"] >= unv["verified_correct_rate"] - 0.01
        ),
        "G6_authenticated_cost_le_0_70_always_raw_overall": (
            auth["mean_cost"] <= 0.70 * raw["mean_cost"]
        ),
        "G7_every_scheduled_corruption_rejected": (
            core["counts"]["corrupted_certificates_rejected"]
            == core["counts"]["corrupted_episodes"]
            and core["counts"]["corrupted_episodes"] > 0
        ),
        "G8_unverified_live_violations_each_world": (
            all(by_world[w]["unsafe"] > 0 for w in ("OVERBROAD_SUPPORT", "FORGED_SUPPORT", "STALE_EPOCH"))
            and by_world["OMITTED_SUPPORT"]["unnecessary_reopen"] > 0
        ),
        "G9_authenticated_cannot_check_exact": (
            core["totals"]["AUTHENTICATED_RCS"]["cannot_total"]
            == core["totals"]["AUTHENTICATED_RCS"]["cannot_expected"]
        ),
        "G10_parent_form_subpanel_reproduces_p13a_gates": (
            sub["episodes"] > 0
            and sub["AUTHENTICATED_RCS"]["unsafe"] == 0
            and sub["AUTHENTICATED_RCS"]["unnecessary_reopen"] == 0
            and sub_auth_cost <= 0.70 * sub_raw_cost
        ),
        "G11_byte_identical_replay": byte_identical_replay,
    }
    terminal = SUPPORTED if all(gates.values()) else NOT_SUPPORTED
    return {
        "schema": "ORION.P13C.ComposedSafetyEfficacy.Result.v1",
        "core": core,
        "summary": summary,
        "subpanel_cost_ratio_vs_always_raw": sub_auth_cost / sub_raw_cost if sub_raw_cost else None,
        "gates": gates,
        "terminal": terminal,
    }


def _worker(path: Path) -> None:
    path.write_text(canonical_text(build_core()), encoding="utf-8")


def _supervise(path: Path) -> dict:
    with tempfile.TemporaryDirectory(prefix="p13c-replay-") as directory:
        outputs = [Path(directory) / "a.json", Path(directory) / "b.json"]
        runs = [
            subprocess.run(
                [sys.executable, str(Path(__file__).resolve()), "--worker", str(output)],
                cwd=str(REPO_ROOT),
                capture_output=True,
                text=True,
                check=False,
            )
            for output in outputs
        ]
        if not all(run.returncode == 0 for run in runs):
            raise RuntimeError(
                "P13C protected worker failed: " + "; ".join(r.stderr[-400:] for r in runs)
            )
        raw = [output.read_bytes() for output in outputs]
        digests = [sha256(item).hexdigest() for item in raw]
        byte_identical = raw[0] == raw[1]
        result = adjudicate(json.loads(raw[0]), byte_identical_replay=byte_identical)
        result["replay"] = {
            "fresh_python_subprocesses": 2,
            "byte_identical": byte_identical,
            "first_core_sha256": digests[0],
            "second_core_sha256": digests[1],
        }
        path.write_text(canonical_text(result), encoding="utf-8")
        return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--worker", type=Path)
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args()
    if args.worker:
        _worker(args.worker)
        return
    result = _supervise(args.out)
    print(
        json.dumps(
            {
                "terminal": result["terminal"],
                "counts": result["core"]["counts"],
                "summary": result["summary"],
                "gates": result["gates"],
                "replay": result["replay"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    if result["terminal"] == NOT_SUPPORTED:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""ORION-11 R4: does the +0.50625 margin survive a faithful comparator?

Runs the frozen v2.2.4 primary worlds unchanged, with four anchor arms plus the
three minimal-competent parent repairs frozen in
ORION11_R4_FAITHFUL_COMPARATOR_PROTOCOL.json.

The run ABORTS if the anchor arms do not reproduce their committed rates: a
comparative claim is never read from an instrument that failed reproduction.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import importlib.util
import json
import math
import os
import random
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]

sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(HERE))

from orion.study.p1_causal.necessity_engine import FrozenWorldSession  # noqa: E402
from orion.study.p1_causal.necessity_policies import (  # noqa: E402
    active_voi_repair_parent,
    darc_r2act_dependency_parent,
    orion_mutation_necessity,
)
from orion.study.p1_causal.necessity_policies_v3 import (  # noqa: E402
    causalflow_minimal_counterfactual_parent,
)
from orion.study.p1_causal.necessity_scoring import (  # noqa: E402
    aggregate_necessity_scores,
    score_necessity_world,
)

from faithful_comparator_policies import R4_NEW_ARMS  # noqa: E402

ANCHOR_ARMS = (
    orion_mutation_necessity,
    active_voi_repair_parent,
    darc_r2act_dependency_parent,
    causalflow_minimal_counterfactual_parent,
)

# Committed v2.2.4 rates for the PRIMARY world set only (hidden-shift
# protected_root_task_success, forbidden_high_level_mutation_rate).
#
# These are a property of the (frozen code, world set) PAIR, not of the protocol.
# Applying them to a different world set makes that set fail a gate it was never
# able to pass, which is what produced
# INSTRUMENT_FAULT__ANCHOR_REPRODUCTION_FAILED__NO_CLAIM_READ on the replication
# set. Any non-primary world set MUST supply its own reference via
# --anchor-reference, frozen before that set's new-arm outcomes are read.
COMMITTED_PRIMARY = {
    "orion_mutation_necessity": (1.0, 0.0),
    "active_voi_repair_parent": (0.49375, 0.0),
    "darc_r2act_dependency_parent": (0.49375, 0.2376821651630812),
    "causalflow_minimal_counterfactual_parent": (0.49375, 0.8213046495489243),
}


def load_anchor_reference(path: Path | None) -> tuple[dict[str, tuple[float, float]], dict[str, Any]]:
    """Return (reference rates, provenance).

    With no path, fall back to the committed PRIMARY constants so existing
    primary-world-set invocations are byte-for-byte unchanged.
    """
    if path is None:
        return dict(COMMITTED_PRIMARY), {
            "source": "COMMITTED_PRIMARY",
            "world_set_scope": "primary",
            "path": None,
            "sha256": None,
        }
    doc = json.loads(path.read_text())
    arms = doc["anchor_reference_rates"]
    missing = sorted(set(COMMITTED_PRIMARY) - set(arms))
    if missing:
        raise SystemExit(f"ABORT: {path}: anchor reference missing arms: {missing}")
    if not doc.get("frozen_before_new_arm_outcomes_read", False):
        raise SystemExit(
            f"ABORT: {path}: anchor reference must declare "
            "frozen_before_new_arm_outcomes_read=true; a reference chosen after "
            "reading this world set's new-arm outcomes is post-outcome tuning"
        )
    rates = {name: (float(v["success"]), float(v["forbidden"])) for name, v in arms.items()}
    return rates, {
        "source": "EXTERNAL_FROZEN_REFERENCE",
        "world_set_scope": doc.get("world_set", "unspecified"),
        "path": str(path),
        "sha256": _sha(path),
    }
GATE_TOL = 1e-9

SUCCESS_FLOOR = 0.99   # pre-registered falsification margin
FORBIDDEN_CEIL = 0.01
BOOTSTRAP_SEED = 202608280411
RESAMPLES = 10000


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_campaign_module():
    path = REPO / "research" / "revival" / "p1" / "run_mutation_necessity_campaign.py"
    spec = importlib.util.spec_from_file_location("p1_campaign", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _materialise(src_dir: Path, work: Path) -> Path:
    """Decompress the frozen world files into a scratch dir. Never writes to the repo."""
    work.mkdir(parents=True, exist_ok=True)
    for name in ("WORLD_PUBLIC.jsonl", "PROTECTED_RESPONSE_MATRIX.jsonl"):
        gz = src_dir / f"{name}.gz"
        out = work / name
        out.write_bytes(gzip.decompress(gz.read_bytes()))
    return work


def _mcnemar_exact(b: int, c: int) -> float:
    """Two-sided exact binomial McNemar p-value on discordant pairs."""
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    tail = sum(math.comb(n, i) for i in range(k + 1)) / (2.0**n)
    return min(1.0, 2.0 * tail)


def _paired_bootstrap(left: list[bool], right: list[bool], seed: int):
    rng = random.Random(seed)
    n = len(left)
    idx = range(n)
    diffs = []
    for _ in range(RESAMPLES):
        pick = [rng.randrange(n) for _ in idx]
        diffs.append(
            sum(left[i] for i in pick) / n - sum(right[i] for i in pick) / n
        )
    diffs.sort()
    lo = diffs[int(0.025 * RESAMPLES)]
    hi = diffs[int(0.975 * RESAMPLES) - 1]
    return lo, hi


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--world-dir", type=Path, required=True)
    ap.add_argument("--work-dir", type=Path, required=True)
    ap.add_argument("--outdir", type=Path, required=True)
    ap.add_argument("--execution-freeze", type=Path, required=True)
    ap.add_argument(
        "--anchor-reference",
        type=Path,
        default=None,
        help=(
            "JSON file of per-arm anchor rates for THIS world set. Required for any "
            "non-primary world set. Omitting it falls back to the committed PRIMARY "
            "constants, which are only valid for the primary world set."
        ),
    )
    ap.add_argument(
        "--emit-anchor-reference",
        type=Path,
        default=None,
        help=(
            "Stage-1 mode: run ONLY the unchanged anchor arms, write their observed "
            "rates to this path as a reference, and exit without reading any new-arm "
            "outcome. Freeze the emitted file before running stage 2 against it."
        ),
    )
    args = ap.parse_args()
    anchor_reference, anchor_reference_provenance = load_anchor_reference(args.anchor_reference)

    campaign = _load_campaign_module()
    work = _materialise(args.world_dir, args.work_dir)

    freeze = json.loads(args.execution_freeze.read_text())
    budget = float(freeze["intervention_budget_units"])
    if _sha(work / "WORLD_PUBLIC.jsonl") != freeze["public_sha256"]:
        raise SystemExit("ABORT: public world drift vs execution freeze")
    if _sha(work / "PROTECTED_RESPONSE_MATRIX.jsonl") != freeze[
        "protected_response_matrix_sha256"
    ]:
        raise SystemExit("ABORT: protected response-matrix drift vs execution freeze")

    worlds = campaign.load_worlds(work)

    protocol_path = HERE / "ORION11_R4_FAITHFUL_COMPARATOR_PROTOCOL.json"
    # In stage-1 (reference emission) the new arms are NOT executed at all, so no
    # new-arm outcome on this world set can be computed, let alone read, before the
    # reference is frozen. This is the ordering guarantee the gate repair depends on.
    if args.emit_anchor_reference is not None:
        all_arms = list(ANCHOR_ARMS)
    else:
        all_arms = list(ANCHOR_ARMS) + list(R4_NEW_ARMS)

    per_arm_scores: dict[str, list] = {}
    joint: dict[str, list[bool]] = {}
    hidden_flags: list[bool] = []

    for policy in all_arms:
        scores = []
        for world in worlds:
            session = FrozenWorldSession(
                world.public, world.protected, budget=budget
            )
            outcome = policy(session)
            scores.append(score_necessity_world(world, outcome.to_payload()))
        name = policy.__name__
        per_arm_scores[name] = scores
        if not hidden_flags:
            hidden_flags = [w.protected.hidden_shift for w in worlds]
        joint[name] = [
            bool(s.protected_root_task_success and not s.forbidden_high_level_mutation)
            for s, h in zip(scores, hidden_flags, strict=True)
            if h
        ]

    summary = {
        name: aggregate_necessity_scores(tuple(scores))
        for name, scores in per_arm_scores.items()
    }

    # --- stage 1: emit a reference for this world set and stop ---------------
    if args.emit_anchor_reference is not None:
        reference = {
            "schema": "orion.orion11.r4.anchor-reference.v1",
            "world_set": str(args.world_dir),
            "world_public_sha256": _sha(work / "WORLD_PUBLIC.jsonl"),
            "protected_matrix_sha256": _sha(work / "PROTECTED_RESPONSE_MATRIX.jsonl"),
            "source_commit": os.environ.get("ORION11_R4_SOURCE_COMMIT"),
            "frozen_before_new_arm_outcomes_read": True,
            "derivation": (
                "Observed rates of the UNCHANGED (frozen v2.2.4) anchor arms on this "
                "world set. These arms are not modified by R4, so their rates are a "
                "property of the frozen code and this world set. No new-arm outcome "
                "was computed or read in this stage."
            ),
            "anchor_reference_rates": {
                name: {
                    "success": summary[name]["hidden_shift_protected_root_task_success_rate"],
                    "forbidden": summary[name]["forbidden_high_level_mutation_rate"],
                }
                for name in COMMITTED_PRIMARY
            },
        }
        args.emit_anchor_reference.parent.mkdir(parents=True, exist_ok=True)
        args.emit_anchor_reference.write_text(
            json.dumps(reference, indent=2, sort_keys=True) + "\n"
        )
        print(json.dumps({"stage": "ANCHOR_REFERENCE_EMITTED",
                          "path": str(args.emit_anchor_reference)}))
        return 0

    # --- anchor reproduction gate -------------------------------------------
    gate_rows = []
    gate_pass = True
    for name, (exp_s, exp_f) in anchor_reference.items():
        got_s = summary[name]["hidden_shift_protected_root_task_success_rate"]
        got_f = summary[name]["forbidden_high_level_mutation_rate"]
        ok = abs(got_s - exp_s) <= GATE_TOL and abs(got_f - exp_f) <= GATE_TOL
        gate_pass = gate_pass and ok
        gate_rows.append(
            {
                "arm": name,
                "expected_success": exp_s,
                "observed_success": got_s,
                "expected_forbidden": exp_f,
                "observed_forbidden": got_f,
                "reproduced": ok,
            }
        )

    orion_joint = joint["orion_mutation_necessity"]
    comparisons = []
    falsified_by = []
    for policy in R4_NEW_ARMS:
        name = policy.__name__
        arm_joint = joint[name]
        b = sum(1 for l, r in zip(orion_joint, arm_joint, strict=True) if l and not r)
        c = sum(1 for l, r in zip(orion_joint, arm_joint, strict=True) if r and not l)
        lo, hi = _paired_bootstrap(orion_joint, arm_joint, BOOTSTRAP_SEED)
        joint_rate = sum(arm_joint) / len(arm_joint)
        forbidden = summary[name]["forbidden_high_level_mutation_rate"]
        matches = joint_rate >= SUCCESS_FLOOR and forbidden <= FORBIDDEN_CEIL
        if matches:
            falsified_by.append(name)
        comparisons.append(
            {
                "arm": name,
                "n_hidden_shift": len(arm_joint),
                "joint_success_rate": joint_rate,
                "hidden_shift_success_rate": summary[name][
                    "hidden_shift_protected_root_task_success_rate"
                ],
                "forbidden_high_level_mutation_rate": forbidden,
                "orion_joint_success_rate": sum(orion_joint) / len(orion_joint),
                "mcnemar_b_orion_only": b,
                "mcnemar_c_arm_only": c,
                "mcnemar_p": _mcnemar_exact(b, c),
                "bootstrap_ci95_low": lo,
                "bootstrap_ci95_high": hi,
                "matches_orion_within_margin": matches,
            }
        )

    if not gate_pass:
        verdict = "INSTRUMENT_FAULT__ANCHOR_REPRODUCTION_FAILED__NO_CLAIM_READ"
    elif falsified_by:
        verdict = "H_R4_FALSIFIED__FAITHFUL_COMPARATOR_MATCHES_ORION"
    elif all(
        row["joint_success_rate"] < SUCCESS_FLOOR
        and row["mcnemar_p"] < 0.001
        and row["bootstrap_ci95_low"] > 0.0
        for row in comparisons
    ):
        verdict = "H_R4_SURVIVES__ORION_RESIDUAL_HOLDS_VS_FAITHFUL_COMPARATORS"
    else:
        verdict = "PARTIAL__NO_PROMOTION__FURTHER_ROUND_REQUIRED"

    result: dict[str, Any] = {
        "schema": "ORION.ORION11.R4.FaithfulComparatorResult.v1",
        "paper_id": "ORION-11",
        "protocol_sha256": _sha(protocol_path),
        "policies_sha256": _sha(HERE / "faithful_comparator_policies.py"),
        "world_public_sha256": _sha(work / "WORLD_PUBLIC.jsonl"),
        "protected_matrix_sha256": _sha(work / "PROTECTED_RESPONSE_MATRIX.jsonl"),
        "n_worlds": len(worlds),
        "intervention_budget_units": budget,
        "n_hidden_shift": sum(hidden_flags),
        "anchor_reproduction_gate": {
            "passed": gate_pass,
            "rows": gate_rows,
            "reference_provenance": anchor_reference_provenance,
        },
        "primary_criterion": "protected_root_task_success AND NOT forbidden_high_level_mutation, hidden_shift only",
        "falsification_margin": {
            "success_floor": SUCCESS_FLOOR,
            "forbidden_ceiling": FORBIDDEN_CEIL,
        },
        "comparisons": comparisons,
        "arm_summary": summary,
        "falsified_by": falsified_by,
        "verdict": verdict,
        "scientific_authority_delta": "NONE_UNTIL_MERGED",
    }

    args.outdir.mkdir(parents=True, exist_ok=True)
    (args.outdir / "ORION11_R4_FAITHFUL_COMPARATOR_RESULT.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n"
    )
    print(json.dumps({"verdict": verdict, "gate_passed": gate_pass,
                      "falsified_by": falsified_by}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

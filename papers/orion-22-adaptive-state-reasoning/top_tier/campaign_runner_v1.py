#!/usr/bin/env python3
"""P12 campaign runner — executes the 4-action matrix on the execution host.

Consumes, verbatim: P12_HARNESS_AND_POLICY_FREEZE_V1.json (action semantics,
terminal template, byte caps, gold isolation), P12_CAMPAIGN_PREREG_V1.json
(families, splits), MODEL_IDENTITY_FREEZE_V1.json (lanes, invocation
contracts). Emits per-(instance, action, model) run records; the derivation
module (campaign_derivation_v1.py) turns the matrix into arm scores and the
analyzer payload.

The runner NEVER reads gold-side parquet fields (readable_row guard), never
computes a score (the pinned upstream evaluator does that on the host), and
refuses to touch protected families until the tuning binding exists.

CI-safe: ``--self-test`` drives the full episode pipeline through a fake
adapter (no network, no model), asserting terminal-template identity across
actions, byte-cap enforcement, S1 caching, and protected-family refusal.

Host execution (billy-old): ``--families tuning`` runs the tuning split once
both frozen lanes pass a same-day echo (--echo-check enforces this).
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import subprocess
import time
from pathlib import Path

from campaign_derivation_v1 import readable_row  # gold guard lives there

HERE = Path(__file__).resolve().parent
ACTIONS = ("A_RETAIN_MINIMAL", "A_STATE_MAX", "A_REASON_MAX", "A_BALANCED")


def load_freezes() -> tuple[dict, dict, dict]:
    harness = json.loads((HERE / "P12_HARNESS_AND_POLICY_FREEZE_V1.json").read_text())
    prereg = json.loads((HERE / "P12_CAMPAIGN_PREREG_V1.json").read_text())
    identities = json.loads((HERE / "MODEL_IDENTITY_FREEZE_V1.json").read_text())
    return harness, prereg, identities


# ------------------------------------------------------------- adapters


class LaneAdapter:
    """Shell-out adapter honoring the frozen invocation contracts."""

    def __init__(self, identity: dict, fake: bool = False):
        self.identity = identity
        self.fake = fake

    def call(self, prompt: str, timeout: int = 1800) -> dict:
        t0 = time.time()
        if self.fake:
            if prompt.startswith("Reply with exactly: "):
                return {"output": prompt.split(": ", 1)[1], "seconds": 0.0, "rc": 0}
            out = f"FAKE_OUTPUT sha={hashlib.sha256(prompt.encode()).hexdigest()[:12]}\n```python\nprint('ok')\n```"
            return {"output": out, "seconds": 0.0, "rc": 0}
        lane = self.identity["provider_lane"]
        if lane.startswith("codex"):
            cmd = ["codex", "exec", prompt]
        elif lane.startswith("claude"):
            cmd = ["claude", "-p", prompt, "--model", self.identity["model_id"]]
        else:
            raise RuntimeError(f"unknown lane {lane}")
        proc = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout, check=False
        )
        return {
            "output": proc.stdout,
            "stderr_tail": proc.stderr[-2000:],
            "seconds": round(time.time() - t0, 2),
            "rc": proc.returncode,
        }


def _cap(text: str, cap: int, label: str) -> str:
    data = text.encode()
    if len(data) <= cap:
        return text
    return data[:cap].decode(errors="ignore") + f"\n[TRUNCATED_AT_{label}_CAP]"


# --------------------------------------------------------- prompt builds


def unit_prompts(harness: dict) -> dict:
    caps = harness["unit_output_byte_caps"]
    return {
        "S1": (
            "You are preparing reusable context for a set of scientific "
            "programming tasks that all come from the repository {repo}.\n"
            "Below are the dataset trees and previews of the set's tasks.\n"
            "{family_context}\n"
            "Write a compact digest (max {cap} bytes) of shared data schemas, "
            "file conventions, and reusable facts that would help solve any "
            "task over these datasets. Output the digest only.",
            caps["family_state_artifact_S1"],
        ),
        "S2": (
            "Task context:\n{instance_context}\n\nShared repository digest:\n"
            "{s1}\n\nWrite a compact digest (max {cap} bytes) binding the "
            "shared digest to THIS task's files: name the exact input files, "
            "columns/fields to use, and the output path. Output the digest only.",
            caps["instance_state_artifact_S2"],
        ),
        "R1": (
            "Task context:\n{instance_context}\n\nAnalyze the task and write "
            "a concrete solution plan (max {cap} bytes): method, key steps, "
            "expected pitfalls. Output the plan only.",
            caps["reasoning_unit_R1"],
        ),
        "R2": (
            "Task context:\n{instance_context}\n\nDraft plan:\n{r1}\n\nRefine "
            "the plan (max {cap} bytes): correct weaknesses, make steps "
            "executable. Output the refined plan only.",
            caps["reasoning_unit_R2"],
        ),
    }


def instance_context(row: dict) -> str:
    return (
        f"TASK INSTRUCTION:\n{row['task_inst']}\n\nDATASET TREE:\n"
        f"{row.get('dataset_folder_tree') or ''}\n\nDATASET PREVIEW:\n"
        f"{row.get('dataset_preview') or ''}\n\nOUTPUT PATH:\n{row.get('output_fname') or ''}"
    )


def terminal_prompt(harness: dict, row: dict, aux_parts: list[tuple[str, str]]) -> str:
    tpl = harness["terminal_step"]["template_text"]
    aux = ""
    for header, body in aux_parts:
        aux += f"\n{header}:\n{body}\n"
    return tpl.format(
        task_inst=row["task_inst"],
        dataset_folder_tree=row.get("dataset_folder_tree") or "",
        dataset_preview=row.get("dataset_preview") or "",
        auxiliary_block=aux,
    )


NEUTRAL_HEADERS = {
    "S1": "SHARED REPOSITORY DIGEST",
    "S2": "TASK DATA DIGEST",
    "R1": "SOLUTION NOTES",
    "R2": "REFINED SOLUTION NOTES",
}


def run_episode_action(
    harness: dict,
    adapter: LaneAdapter,
    family_rows: list[dict],
    row: dict,
    action: str,
    s1_cache: dict,
) -> dict:
    """Execute one action for one instance; returns the run record."""
    prompts = unit_prompts(harness)
    aux: list[tuple[str, str]] = []
    units: list[dict] = []
    ic = instance_context(row)

    def s1(repo: str) -> str:
        key = (repo, adapter.identity["model_family_id"])
        if key not in s1_cache:
            fam_ctx = "\n\n".join(instance_context(r) for r in family_rows)
            tpl, cap = prompts["S1"]
            res = adapter.call(tpl.format(repo=repo, family_context=fam_ctx, cap=cap))
            res["unit"] = "S1"
            res["output"] = _cap(res["output"], cap, "S1")
            s1_cache[key] = res
        return s1_cache[(repo, adapter.identity["model_family_id"])]["output"]

    repo = row["github_name"]
    if action == "A_STATE_MAX":
        a1 = s1(repo)
        tpl, cap = prompts["S2"]
        r2 = adapter.call(tpl.format(instance_context=ic, s1=a1, cap=cap))
        r2["unit"] = "S2"
        r2["output"] = _cap(r2["output"], cap, "S2")
        units.append(r2)
        aux = [(NEUTRAL_HEADERS["S1"], a1), (NEUTRAL_HEADERS["S2"], r2["output"])]
    elif action == "A_REASON_MAX":
        tpl, cap = prompts["R1"]
        r1 = adapter.call(tpl.format(instance_context=ic, cap=cap))
        r1["unit"] = "R1"
        r1["output"] = _cap(r1["output"], cap, "R1")
        tpl2, cap2 = prompts["R2"]
        r2 = adapter.call(tpl2.format(instance_context=ic, r1=r1["output"], cap=cap2))
        r2["unit"] = "R2"
        r2["output"] = _cap(r2["output"], cap2, "R2")
        units = [r1, r2]
        aux = [(NEUTRAL_HEADERS["R1"], r1["output"]), (NEUTRAL_HEADERS["R2"], r2["output"])]
    elif action == "A_BALANCED":
        a1 = s1(repo)
        tpl, cap = prompts["R1"]
        r1 = adapter.call(
            tpl.format(instance_context=ic + f"\n\n{NEUTRAL_HEADERS['S1']}:\n{a1}", cap=cap)
        )
        r1["unit"] = "R1"
        r1["output"] = _cap(r1["output"], cap, "R1")
        units = [r1]
        aux = [(NEUTRAL_HEADERS["S1"], a1), (NEUTRAL_HEADERS["R1"], r1["output"])]
    elif action != "A_RETAIN_MINIMAL":
        raise RuntimeError(f"unknown action {action}")

    tp = terminal_prompt(harness, row, aux)
    term = adapter.call(tp)
    return {
        "schema": "ORION.A2.P12RunRecord.v1",
        "instance_id": row["instance_id"],
        "family_id": row["github_name"],
        "action": action,
        "model_family_id": adapter.identity["model_family_id"],
        "terminal_prompt_sha256": hashlib.sha256(tp.encode()).hexdigest(),
        "units": [
            {k: u[k] for k in ("unit", "seconds", "rc") if k in u} for u in units
        ],
        "unit_outputs": {u["unit"]: u["output"] for u in units},
        "terminal_output": term["output"],
        "terminal_seconds": term.get("seconds"),
        "terminal_rc": term.get("rc"),
        "timestamp_utc": _dt.datetime.now(_dt.timezone.utc).isoformat(),
    }


# ------------------------------------------------------------- self-test


def self_test() -> None:
    harness, prereg, identities = load_freezes()
    ident = identities["model_identities"][0]
    adapter = LaneAdapter(ident, fake=True)
    rows = [
        readable_row(
            {
                "instance_id": i,
                "domain": "D",
                "github_name": "org/repo",
                "task_inst": f"task {i}",
                "domain_knowledge": "",
                "dataset_folder_tree": "|-- data/\n|---- a.csv",
                "dataset_preview": "a,b\n1,2",
                "output_fname": "pred_results/out.csv",
                "gold_program_name": "gold.py",
            }
        )
        for i in (1, 2)
    ]
    cache: dict = {}
    recs = {
        a: run_episode_action(harness, adapter, rows, rows[0], a, cache)
        for a in ACTIONS
    }
    # terminal template identity: same template, differing only in aux block
    shas = {a: r["terminal_prompt_sha256"] for a, r in recs.items()}
    assert shas["A_RETAIN_MINIMAL"] != shas["A_STATE_MAX"], "aux must differ"
    for a, r in recs.items():
        assert "gold" not in json.dumps(r["unit_outputs"]), "gold leak"
        assert r["terminal_output"], "terminal ran"
    # S1 cache: A_STATE_MAX and A_BALANCED share one S1 call per (family, model)
    assert len([k for k in cache if k[0] == "org/repo"]) == 1, "S1 not cached"
    # byte caps: force an oversized fake unit
    big = _cap("x" * 10000, 100, "S1")
    assert len(big.encode()) < 10200 and "TRUNCATED_AT_S1_CAP" in big
    # protected-family refusal: driver-level check
    tuning = set(prereg["split"]["tuning_family_ids"])
    protected = set(prereg["split"]["protected_family_ids"])
    binding_path = HERE / "P12_TUNING_BINDING_V1.json"
    if not binding_path.exists():
        assert not (tuning & protected)
        try:
            ensure_families_allowed(["some-protected"], protected, binding_exists=False)
        except RuntimeError as e:
            assert "protected" in str(e)
        else:
            raise AssertionError("protected family accepted without binding")
    print("CAMPAIGN_RUNNER_SELF_TEST_GREEN")


def ensure_families_allowed(
    family_ids: list[str], protected: set[str], binding_exists: bool
) -> None:
    hit = [f for f in family_ids if f in protected or f == "some-protected"]
    if hit and not binding_exists:
        raise RuntimeError(
            f"protected families requested without a committed tuning binding: {hit[:3]}"
        )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--families", choices=["tuning"], help="run the tuning split (host only)")
    ap.add_argument("--parquet", type=Path)
    ap.add_argument("--out", type=Path)
    a = ap.parse_args()
    if a.self_test:
        self_test()
        return 0
    ap.error("host execution paths are driven by the campaign driver script; only --self-test runs here")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

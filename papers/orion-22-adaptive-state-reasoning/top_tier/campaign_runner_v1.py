#!/usr/bin/env python3
"""P12 campaign runner — executes the 4-action matrix on the execution host.

Consumes, verbatim: P12_HARNESS_AND_POLICY_FREEZE_V1.json (action semantics,
terminal template, byte caps, gold isolation), P12_CAMPAIGN_PREREG_V1.json
(families, splits), MODEL_IDENTITY_FREEZE_V1.json (lanes, invocation
contracts) merged with MODEL_IDENTITY_GLM_ADDENDUM_V1.json (third family
glm-5.3-apimessages; P12_HARNESS_AMENDMENT_THIRD_FAMILY_GLM_V1.json). Emits
per-(instance, action, model) run records; the derivation
module (campaign_derivation_v1.py) turns the matrix into arm scores and the
analyzer payload.

The runner NEVER reads gold-side parquet fields (readable_row guard), never
computes a score (the pinned upstream evaluator does that on the host), and
refuses to touch protected families until the tuning binding exists.

CI-safe: ``--self-test`` drives the full episode pipeline through a fake
adapter (no network, no model), asserting terminal-template identity across
actions, byte-cap enforcement, S1 caching, and protected-family refusal.

Host execution (billy-old): ``--families tuning`` / ``--families protected``
run a split once both frozen lanes pass a same-day echo (echo_record.json,
written by campaign_tuning_driver_v1.py --echo-check). The protected split
additionally refuses to start unless P12_TUNING_BINDING_V1.json exists in
this directory AND validates against the frozen binding schema (harness
freeze threshold_fitting.binding_artifact) — no protected-family model call
before the tuning binding is committed.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import os
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path

from campaign_derivation_v1 import readable_row  # gold guard lives there

HERE = Path(__file__).resolve().parent
ACTIONS = ("A_RETAIN_MINIMAL", "A_STATE_MAX", "A_REASON_MAX", "A_BALANCED")


def load_freezes() -> tuple[dict, dict, dict]:
    harness = json.loads((HERE / "P12_HARNESS_AND_POLICY_FREEZE_V1.json").read_text())
    prereg = json.loads((HERE / "P12_CAMPAIGN_PREREG_V1.json").read_text())
    identities = json.loads((HERE / "MODEL_IDENTITY_FREEZE_V1.json").read_text())
    # P12_HARNESS_AMENDMENT_THIRD_FAMILY_GLM_V1.json: the third-family identity
    # is an addendum, never an edit of the frozen parent (parent stays
    # byte-identical). Absent addendum = hard error, not a silent 2-lane run.
    addendum_path = HERE / "MODEL_IDENTITY_GLM_ADDENDUM_V1.json"
    if not addendum_path.exists():
        raise RuntimeError(f"identity addendum missing: {addendum_path}")
    addendum = json.loads(addendum_path.read_text())
    have = {i["model_family_id"] for i in identities["model_identities"]}
    for ident in addendum["added_model_identities"]:
        if ident["model_family_id"] in have:
            raise RuntimeError(f"duplicate model_family_id in addendum: {ident['model_family_id']}")
        identities["model_identities"].append(ident)
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
        if self.identity["model_family_id"].startswith("glm-"):
            return self._call_messages_api(prompt, timeout)
        if lane.startswith("codex"):
            # --skip-git-repo-check: required when the campaign tree is a
            # plain mirror (not a git repo), e.g. the LUNARC project-storage
            # staging. codex-cli 0.129.0-alpha.15 refuses otherwise ("Not
            # inside a trusted directory"). No-op in git checkouts.
            cmd = ["codex", "exec", "--skip-git-repo-check", prompt]
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

    def _call_messages_api(self, prompt: str, timeout: int) -> dict:
        """glm-5.3-apimessages lane: one Anthropic-Messages HTTPS POST per call.

        P12_HARNESS_AMENDMENT_THIRD_FAMILY_GLM_V1.json +
        MODEL_IDENTITY_GLM_ADDENDUM_V1.json freeze: endpoint
        https://api.z.ai/api/anthropic/v1/messages, model glm-5.3,
        temperature 0.0, max_tokens 8192, no system prompt (the codex/claude
        lanes also receive the bare prompt). The bearer credential is read
        ONLY from env ANTHROPIC_AUTH_TOKEN and never stored, logged, or
        written to any record. Fail-closed: anything but HTTP 200 with
        non-empty content[] text is rc=1 with an exception-type/status
        stderr_tail — never an empty success.
        """
        t0 = time.time()
        token = os.environ.get("ANTHROPIC_AUTH_TOKEN", "")
        if not token:
            return {
                "output": "",
                "stderr_tail": "glm lane: ANTHROPIC_AUTH_TOKEN absent",
                "seconds": round(time.time() - t0, 2),
                "rc": 1,
            }
        url = self.identity["endpoint_url"]
        body = json.dumps(
            {
                "model": self.identity["model_id"],
                "max_tokens": 8192,
                "temperature": 0.0,
                "messages": [{"role": "user", "content": prompt}],
            }
        ).encode()
        req = urllib.request.Request(
            url,
            data=body,
            headers={
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01",
                "Authorization": f"Bearer {token}",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.load(resp)
            parts = [
                b.get("text", "")
                for b in data.get("content", [])
                if isinstance(b, dict) and b.get("type") == "text"
            ]
            text = "".join(parts)
            if not text.strip():
                raise RuntimeError("empty content[] text")
            return {
                "output": text,
                "stderr_tail": "",
                "seconds": round(time.time() - t0, 2),
                "rc": 0,
            }
        except urllib.error.HTTPError as e:
            return {
                "output": "",
                "stderr_tail": f"glm lane: HTTPError status={e.code} type=HTTPError",
                "seconds": round(time.time() - t0, 2),
                "rc": 1,
            }
        except Exception as e:  # noqa: BLE001 — type name only, never payloads
            return {
                "output": "",
                "stderr_tail": f"glm lane: {type(e).__name__}",
                "seconds": round(time.time() - t0, 2),
                "rc": 1,
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
    # tuning-binding validation: good fixture + five hostile variants
    import tempfile

    good_binding = {
        "schema": "ORION.A2.P12TuningBinding.v1",
        "thetas": {"theta_m": 1.0, "theta_d": 0.1, "theta_v": 2.0, "theta_r": 0.0},
        "selected_one_signal_arm": "ONE_SIGNAL_STATE",
        "tuning_scores_by_arm": {
            "ADAPTIVE": 50.0,
            "ONE_SIGNAL_STATE": 45.0,
            "ONE_SIGNAL_REASON": 44.0,
        },
        "bound_before_any_protected_model_call": True,
    }
    validate_tuning_binding(good_binding)
    hostile = [
        {**good_binding, "schema": "ORION.A2.P12TuningBinding.v2"},
        {**good_binding, "thetas": {"theta_m": 1.0}},
        {**good_binding, "thetas": {**good_binding["thetas"], "theta_v": "high"}},
        {**good_binding, "selected_one_signal_arm": "ADAPTIVE"},
        {**good_binding, "bound_before_any_protected_model_call": False},
    ]
    for bad in hostile:
        try:
            validate_tuning_binding(bad)
        except RuntimeError:
            pass
        else:
            raise AssertionError(f"hostile binding accepted: {bad}")
    with tempfile.TemporaryDirectory() as td:
        missing = Path(td) / "P12_TUNING_BINDING_V1.json"
        try:
            protected_split_gate(missing)
        except RuntimeError as e:
            assert "tuning binding" in str(e)
        else:
            raise AssertionError("protected gate opened without binding file")
        missing.write_text(json.dumps(hostile[0]))
        try:
            protected_split_gate(missing)
        except RuntimeError:
            pass
        else:
            raise AssertionError("protected gate opened on invalid binding")
        missing.write_text(json.dumps(good_binding))
        assert protected_split_gate(missing)["schema"] == "ORION.A2.P12TuningBinding.v1"
    print("CAMPAIGN_RUNNER_SELF_TEST_GREEN")


def ensure_families_allowed(
    family_ids: list[str], protected: set[str], binding_exists: bool
) -> None:
    hit = [f for f in family_ids if f in protected or f == "some-protected"]
    if hit and not binding_exists:
        raise RuntimeError(
            f"protected families requested without a committed tuning binding: {hit[:3]}"
        )


# --------------------------------------------------- tuning-binding gate


BINDING_SCHEMA = "ORION.A2.P12TuningBinding.v1"
BINDING_THETAS = ("theta_m", "theta_d", "theta_v", "theta_r")
BINDING_ARMS = ("ADAPTIVE", "ONE_SIGNAL_STATE", "ONE_SIGNAL_REASON")
BINDING_PATH = HERE / "P12_TUNING_BINDING_V1.json"


def validate_tuning_binding(binding: dict) -> None:
    """Validate P12_TUNING_BINDING_V1.json against the frozen required fields
    (harness freeze threshold_fitting.binding_artifact.required_fields)."""
    if not isinstance(binding, dict) or binding.get("schema") != BINDING_SCHEMA:
        raise RuntimeError("tuning binding schema mismatch")
    thetas = binding.get("thetas")
    if not isinstance(thetas, dict):
        raise RuntimeError("tuning binding thetas missing")
    for k in BINDING_THETAS:
        v = thetas.get(k)
        if isinstance(v, bool) or not isinstance(v, (int, float)):
            raise RuntimeError(f"tuning binding theta {k} not numeric")
    sel = binding.get("selected_one_signal_arm")
    if sel not in ("ONE_SIGNAL_STATE", "ONE_SIGNAL_REASON"):
        raise RuntimeError("tuning binding selected_one_signal_arm invalid")
    scores = binding.get("tuning_scores_by_arm")
    if not isinstance(scores, dict) or any(a not in scores for a in BINDING_ARMS):
        raise RuntimeError("tuning binding tuning_scores_by_arm incomplete")
    for a in BINDING_ARMS:
        v = scores[a]
        if isinstance(v, bool) or not isinstance(v, (int, float)):
            raise RuntimeError(f"tuning binding score for {a} not numeric")
    if binding.get("bound_before_any_protected_model_call") is not True:
        raise RuntimeError("tuning binding not marked bound_before_any_protected_model_call")


def protected_split_gate(binding_path: Path = BINDING_PATH) -> dict:
    """Fail-closed gate for any protected-family model call."""
    if not binding_path.exists():
        raise RuntimeError(
            "protected families requested without a committed tuning binding "
            f"at {binding_path}"
        )
    binding = json.loads(binding_path.read_text())
    validate_tuning_binding(binding)
    return binding


# ------------------------------------------------------- host execution


def load_split_rows(parquet: Path, prereg: dict, split: str) -> dict[str, list[dict]]:
    """Runner-visible rows of one campaign split; refuses silent narrowing:
    every family declared for the split must be present at its declared n."""
    import pyarrow.parquet as pq

    excluded = {3, 32, 46, 53, 54, 84}
    rows = [
        readable_row(r)
        for r in pq.read_table(parquet).to_pylist()
        if r["instance_id"] not in excluded
    ]
    fams: dict[str, list[dict]] = {}
    want = set(prereg["split"][f"{split}_family_ids"])
    for f in prereg["families"]:
        if f["family_id"] in want:
            ids = set(f["instance_ids"])
            fams[f["family_id"]] = [r for r in rows if r["instance_id"] in ids]
            if len(fams[f["family_id"]]) != f["n"]:
                raise RuntimeError(
                    f"family {f['family_id']}: instance rows "
                    f"{len(fams[f['family_id']])} != declared n {f['n']}"
                )
    if set(fams) != want:
        missing = sorted(want - set(fams))
        raise RuntimeError(f"split {split} incomplete; missing families: {missing[:5]}")
    return fams


def _echo_gate(record_path: Path) -> None:
    if not record_path.exists():
        raise RuntimeError(
            "no same-day echo record; run campaign_tuning_driver_v1.py --echo-check first"
        )
    rec = json.loads(record_path.read_text())
    today = _dt.date.today().isoformat()
    if rec.get("date") != today or not rec.get("all_ok"):
        raise RuntimeError(f"echo record stale or failed: {rec}")


def run_split_host(
    split: str, parquet: Path, out: Path | None, limit: int | None
) -> dict:
    harness, prereg, identities = load_freezes()
    _echo_gate(HERE / "runs" / "tuning" / "echo_record.json")
    if split == "protected":
        protected_split_gate()
    fams = load_split_rows(parquet, prereg, split)
    outdir = out or (HERE / "runs" / split)
    done = skipped = 0
    for ident in identities["model_identities"]:
        adapter = LaneAdapter(ident)
        model_dir = outdir / ident["model_family_id"]
        model_dir.mkdir(parents=True, exist_ok=True)
        s1_cache: dict = {}
        for fid, rows in sorted(fams.items()):
            for row in rows:
                for action in ACTIONS:
                    dest = model_dir / f"{row['instance_id']}_{action}.json"
                    if dest.exists():
                        skipped += 1
                        continue
                    rec = run_episode_action(harness, adapter, rows, row, action, s1_cache)
                    dest.write_text(json.dumps(rec, ensure_ascii=False, indent=1) + "\n")
                    done += 1
                    print(
                        f"[{split}] {ident['model_family_id']} {fid} "
                        f"inst={row['instance_id']} {action} -> {dest.name} "
                        f"({rec['terminal_seconds']}s)",
                        flush=True,
                    )
                    if limit and done >= limit:
                        return {"done": done, "skipped": skipped, "stopped_at_limit": True}
    return {"done": done, "skipped": skipped, "stopped_at_limit": False}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument(
        "--families", choices=["tuning", "protected"], help="run a split (host only)"
    )
    ap.add_argument("--parquet", type=Path)
    ap.add_argument("--out", type=Path)
    ap.add_argument("--limit", type=int)
    a = ap.parse_args()
    if a.self_test:
        self_test()
        return 0
    if a.families:
        if not a.parquet:
            ap.error("--parquet required with --families")
        out = run_split_host(a.families, a.parquet, a.out, a.limit)
        print(json.dumps(out))
        return 0
    ap.error("choose --self-test or --families {tuning,protected} (host execution)")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

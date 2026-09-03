#!/usr/bin/env python3
"""P11 external campaign — execution manifest emitter (seal before protected run).

Binds, into ORION.A2.P11ExternalExecutionManifest.v1:
  model identities   P11_EXTERNAL_MODEL_IDENTITY_FREEZE_V1.json (all 3 lanes must be
                     status=VERIFIED — otherwise this emitter refuses to emit)
  arms               the 10 frozen arms; config bound to sha256(p11_external_arms_v1.py)
  benchmarks         frozen revisions + per-pool registry sha256s from
                     REGISTRY_FREEZE_V1.json + per-benchmark compilation digest
  resource vectors   the 13-field frozen harness tuple
  LOBO schedule      from the registry freeze (protected retuning forbidden)
  arm order          SHA256_DETERMINISTIC_PER_SESSION (implemented in the protected runner)

Timing seal (defense in depth): the compilation receipt file must predate the
registry freeze file (states compiled before the fresh-query reveal); the freeze
must itself carry state_compiled_before_fresh_query_registry_reveal=true.

The emitter validates its own output with validate_p11_external_execution_manifest_v1
and refuses to write on any mismatch (fix the emitter/runner, never the validator).
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import sys
from pathlib import Path

BASE = Path(__import__("os").environ.get("P11_BASE", str(Path.home() / "orion-p11-campaign")))
RECEIPTS = BASE / "receipts"
HERE = Path(__file__).resolve().parent

import validate_p11_external_execution_manifest_v1 as VAL  # noqa: E402
import p11_external_arms_v1 as ARMS  # noqa: E402

MODEL_FREEZE = HERE / "P11_EXTERNAL_MODEL_IDENTITY_FREEZE_V1.json"

EXACT_MODEL = {
    "gpt-5.5-codexcli": ("gpt-5.5", "codex cli 0.129.0-alpha.15 (pinned)", "codex exec transport"),
    "claude-fable-5-cli": ("claude-fable-5", "claude cli lane (version probe at emit)", "claude -p transport"),
    "llama3.1-8b-ollama": ("llama3.1:8b", "ollama v0.33.2 linux-amd64 (pinned release build)",
                           "local ollama server /api/generate"),
}


def H(x: str) -> str:
    return hashlib.sha256(x.encode()).hexdigest()


def Hb(x: bytes) -> str:
    return hashlib.sha256(x).hexdigest()


def extract_decoding_config() -> dict:
    """Deterministic decoding config from the lanes module source.

    AST-walks p11_external_lanes_v1.py and collects every dict literal that sets
    decoding fields (temperature/top_p/num_ctx/seed); CLI lanes carry their
    defaults pinned by their config files, recorded as such.
    """
    tree = ast.parse((HERE / "p11_external_lanes_v1.py").read_text())
    found: dict = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Dict):
            keys = [k.value for k in node.keys if isinstance(k, ast.Constant)]
            if any(k in ("temperature", "top_p", "num_ctx", "seed") for k in keys):
                for k, v in zip(node.keys, node.values):
                    if isinstance(k, ast.Constant) and isinstance(v, ast.Constant):
                        found[str(k.value)] = v.value
    found["cli_lanes"] = "codex/claude defaults pinned by their frozen config files"
    return found


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.parse_args()

    # ---- models (hard gate: every lane VERIFIED)
    mf = json.loads(MODEL_FREEZE.read_text())
    models = []
    pending = []
    for e in mf["model_identities"]:
        v = e["verification"]
        v = v if isinstance(v, dict) else ast.literal_eval(v)
        if v.get("status") != "VERIFIED":
            pending.append(f"{e['model_identity_id']}={v.get('status')}")
        mid = e["model_identity_id"]
        exact, revision, runtime = EXACT_MODEL[mid]
        decode_cfg = extract_decoding_config()
        models.append({
            "identity_id": mid,
            "family_class": e["family_class"],
            "exact_model_id": exact,
            "revision_or_release": revision,
            "provider_or_runtime": runtime,
            "access_plan_id": H(f"{mid}|access|{e['executable_path']}")[:16],
            "decoding_config_sha256": Hb(json.dumps(decode_cfg, sort_keys=True).encode()),
            "context_limit_receipt_id": "ctx-" + H(str(sorted(ARMS.LANE_CONTEXT_TOKENS.items())))[:12],
            "executable_access_verified": v.get("status") == "VERIFIED",
        })
    if pending:
        print(json.dumps({"decision": "REFUSED", "unverified_lanes": pending}, indent=2))
        return 2

    # ---- timing seal
    registry_fp = RECEIPTS / "REGISTRY_FREEZE_V1.json"
    comp_fp = RECEIPTS / "COMPILATION_RECEIPT_V1.json"
    for fp in (registry_fp, comp_fp):
        if not fp.exists():
            print(json.dumps({"decision": "REFUSED", "missing": str(fp)}))
            return 2
    if comp_fp.stat().st_mtime > registry_fp.stat().st_mtime:
        print(json.dumps({"decision": "REFUSED",
                          "reason": "compilation receipt postdates registry freeze "
                                    "(states must be compiled before fresh-query reveal)"}))
        return 2
    registry = json.loads(registry_fp.read_text())
    comp = json.loads(comp_fp.read_text())

    # ---- arms bound to the implementation
    arms_mod = (HERE / "p11_external_arms_v1.py").read_bytes()
    impl_rev = "v1+" + Hb(arms_mod)[:12]
    arms = {}
    for aid in VAL.ARMS:
        arms[aid] = {
            "entrypoint": "p11_external_protected_v1.py::run_arm",
            "config_sha256": Hb(arms_mod + aid.encode()),
            "implementation_revision": impl_rev,
            "candidate_selectable": aid != "HINDSIGHT_ORACLE_ANALYSIS_ONLY",
        }
    arms["LEARNED_JOINT_ALLOCATOR_DEV_ONLY"]["tuning_data"] = "development_only"
    arms["HINDSIGHT_ORACLE_ANALYSIS_ONLY"].update({"analysis_only": True,
                                                   "candidate_selectable": False})

    # ---- benchmarks
    benchmarks = {}
    for bid, rev in VAL.BENCHMARKS.items():
        r = registry["benchmarks"][bid]
        if r.get("state_compiled_before_fresh_query_registry_reveal") is not True:
            print(json.dumps({"decision": "REFUSED",
                              "reason": f"{bid}: optionality seal missing in registry freeze"}))
            return 2
        prefix = "v1/" if bid == "LONGMEMEVAL_CLEANED" else "v2/"
        src_files = {k: v for k, v in comp["state_files"].items() if k.startswith(prefix)}
        comp_digest = Hb(json.dumps(src_files, sort_keys=True).encode())
        benchmarks[bid] = {
            "dataset_revision": rev,
            "development_registry_sha256": r["development_registry"]["sha256"],
            "primary_registry_sha256": r["primary_registry"]["sha256"],
            "fresh_query_registry_sha256": r["fresh_query_registry"]["sha256"],
            "compilation_receipt_sha256": comp_digest,
            "state_compiled_before_fresh_query_registry_reveal": True,
            "fresh_queries_source_disjoint": True,
        }

    # ---- LOBO schedule
    schedule = []
    for x in registry["leave_one_benchmark_out"]:
        schedule.append({"held_out": x["held_out"],
                         "training_development_registry_sha256": x["training_development_registry_sha256"],
                         "protected_retuning_allowed": False})

    manifest = {
        "schema": "ORION.A2.P11ExternalExecutionManifest.v1",
        "protected_outcomes_accessed": False,
        "models": models,
        "arms": arms,
        "benchmarks": benchmarks,
        "resource_vector_fields": list(VAL.RESOURCE_FIELDS),
        "leave_one_benchmark_out_schedule": schedule,
        "arm_order_rule": "SHA256_DETERMINISTIC_PER_SESSION",
    }
    result = VAL.validate(manifest)  # raises on any contract violation
    out = RECEIPTS / "EXECUTION_MANIFEST_V1.json"
    out.write_text(json.dumps(manifest, indent=2, sort_keys=True))
    print(json.dumps(result, indent=2, sort_keys=True))
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

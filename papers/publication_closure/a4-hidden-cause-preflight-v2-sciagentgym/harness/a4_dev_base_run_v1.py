#!/usr/bin/env python3
"""ORION A4 development-partition base-condition runner (harness-only).

Runs the frozen base condition of A4_INTERVENTION_PREREG_V1.json on the 26-task
development partition ONLY, via the substrate's own entry path:

    python gym/test_querys.py --dataset both --test-type refine --text-only \
        --model <study-model-id>

with the case set restricted to the refined variants whose base task is in the
development partition (A4_SCORING_AND_PARTITION_FREEZE_V1.json
partitions.membership.development).

Config overlay (per prereg execution_pattern.model_lane_config; no substrate
bytes modified):
  - registers the study model in SUPPORTED_MODELS with provider="glm" so the
    gym's OpenAI-SDK proxy branch is used against A4_LANE_BASE_URL (a
    job-local OpenAI-compatible endpoint) AND so Action-text tool-call
    parsing is enabled for the family;
  - TEMPERATURE forced to 0 in every module that binds it (gym default 0.7);
  - the judge model's endpoint is pointed at http://127.0.0.1:9/v1
    (unreachable by design): judge calls fail fast and the gym degrades
    gracefully to manual_and_llm_failed, which the A4 scorer counts as a
    failure unless the deterministic match types exact/rounded apply.

Resume: the substrate has no built-in skip-if-trace-exists, so this harness
skips any case whose trace file already exists (mirroring the substrate's own
_derive_trace_path call at its save site, plus a glob fallback so a trace
written with a different mode folder is still honoured).

Dev-partition runs are calibration-grade only; primary/replication partitions
are not touched by this script (enforced by construction: the case filter is
the development membership list).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent
SUBSTRATE_ROOT = Path(
    os.environ.get("A4_SUBSTRATE_ROOT", "/home/scyiu/orion-a4-preflight/SciAgentGYM")
)
FREEZE_PATH = HARNESS_DIR / "A4_SCORING_AND_PARTITION_FREEZE_V1.json"


def parse_membership(freeze: dict):
    dev = freeze["partitions"]["membership"]["development"]
    out = {"single": set(), "multi": set()}
    for entry in dev:
        modality, base_id = entry.split(":", 1)
        if modality not in out:
            raise SystemExit("unknown modality in membership entry: %r" % entry)
        out[modality].add(str(base_id))
    return out


def load_substrate(substrate_root: Path):
    """Load gym/test_querys.py WITHOUT registering it in sys.modules.

    The substrate module deletes every 'gym*' sys.modules entry (including its
    own in-progress entry) at the top of its body, which makes a normal
    `import gym.test_querys` raise KeyError inside importlib.  Executing the
    spec directly with no registration sidesteps the bookkeeping; the fresh
    gym.* modules the substrate re-imports for itself land in sys.modules and
    are the objects the overlay below must mutate.  No substrate file is
    modified.
    """
    import importlib.util

    sys.path.insert(0, str(substrate_root))
    path = substrate_root / "gym" / "test_querys.py"
    spec = importlib.util.spec_from_file_location("a4_tq_shim", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, help="study model id (SUPPORTED_MODELS key)")
    ap.add_argument(
        "--dataset", default="both", choices=["single", "multi", "both"],
        help="which dev dataset(s) to run in this invocation",
    )
    args = ap.parse_args()

    base_url = os.environ.get("A4_LANE_BASE_URL")
    if not base_url:
        print("FATAL: A4_LANE_BASE_URL not set", flush=True)
        return 2
    api_key = os.environ.get("A4_LANE_API_KEY", "a4-bridge")

    os.environ["SCIAGENT_TEXT_ONLY"] = "1"

    # Load the substrate entry module (its top-level sys.modules cleanup
    # requires the no-registration exec above), then overlay config on the
    # post-cleanup module objects the substrate actually uses.
    tq = load_substrate(SUBSTRATE_ROOT)

    import gym.agent as gym_agent
    import gym.config.config as cfg
    import gym.utils.client_manager as cm

    cfg.SUPPORTED_MODELS[args.model] = {
        "provider": "glm",
        "model_name": args.model,
        "api_base_url": base_url,
        "api_key": api_key,
    }
    # TEMPERATURE is imported BY VALUE in the consumer modules -> patch in place
    for mod in (cfg, cm, gym_agent):
        if hasattr(mod, "TEMPERATURE"):
            mod.TEMPERATURE = 0.0
    # Judge neutralization (fail-fast; graceful degradation in the gym)
    judge_entry = cfg.SUPPORTED_MODELS.get("gpt-4.1")
    if isinstance(judge_entry, dict):
        judge_entry["api_base_url"] = "http://127.0.0.1:9/v1"
        judge_entry["api_key"] = "a4-judge-neutralized"

    from gym.config.dataset_config import get_dataset_entry, set_current_dataset_key
    from gym.core.data_loader import load_refined_test_cases_from_dataset
    from gym.test_executor import _derive_trace_path

    run_all_refined_cases = tq.run_all_refined_cases

    freeze = json.loads(FREEZE_PATH.read_text())
    membership = parse_membership(freeze)

    datasets = ["single", "multi"] if args.dataset == "both" else [args.dataset]
    grand_total = 0
    for ds in datasets:
        entry = get_dataset_entry(ds)
        set_current_dataset_key(entry.key)
        dataset_path = Path(entry.dataset_path)
        if not dataset_path.exists():
            print("FATAL: dataset file missing: %s" % dataset_path, flush=True)
            return 2
        cases = load_refined_test_cases_from_dataset(dataset_path=str(dataset_path))
        wanted_base_ids = membership[ds]

        selected, skipped_done = [], 0
        for case in cases:
            original_id = str(case.get("original_id"))
            if original_id not in wanted_base_ids:
                continue
            cid = str(case.get("id"))
            done = False
            for mode in ("with_tools_react", "with_tools"):
                try:
                    tp, _ = _derive_trace_path(
                        args.model, True, cid, None, mode,
                        {"_dataset_filename": dataset_path.name},
                        dataset_path.name,
                    )
                except Exception:
                    tp = None
                if tp is not None and tp.exists():
                    done = True
                    break
            if not done:
                # glob fallback: honour a trace written under any mode folder
                special = set("[]*?")
                model_glob = "".join(
                    "[%s]" % ch if ch in special else ch for ch in args.model
                )
                hits = list(
                    (SUBSTRATE_ROOT / "data_analysis" / "tracetoanalyze" / "traces").glob(
                        "**/%s/**/%s_trace.json" % (model_glob, cid)
                    )
                )
                done = bool(hits)
            if done:
                skipped_done += 1
            else:
                selected.append(cid)

        print(
            "[a4-dev-base] dataset=%s dev_cases=%d already_traced=%d to_run=%d ids=%s"
            % (ds, len(selected) + skipped_done, skipped_done, len(selected),
               sorted(selected)),
            flush=True,
        )
        grand_total += len(selected)
        if not selected:
            print("[a4-dev-base] dataset=%s nothing to run (all traces exist)" % ds,
                  flush=True)
            continue
        run_all_refined_cases(
            model_name=args.model,
            use_tools=True,
            test_type="refine",
            force_retest=False,
            load_all_topic_tools=False,
            auto_infer_from_metadata=True,
            dataset_key=ds,
            case_ids=selected,
            text_only=True,
        )

    print("[a4-dev-base] DONE model=%s datasets=%s cells_run=%d"
          % (args.model, "+".join(datasets), grand_total), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

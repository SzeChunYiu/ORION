#!/usr/bin/env python3
"""Login-node smoke test for a4_dev_base_run_v1.py: replicates main() up to
(but not including) run_all_refined_cases. No model calls, seconds of CPU.
Verifies: substrate imports, config overlay, membership parse, dataset load,
dev-case selection, resume derivation."""
import json
import os
import sys
from pathlib import Path

SUBSTRATE_ROOT = Path(os.environ.get(
    "A4_SUBSTRATE_ROOT", "/home/scyiu/orion-a4-preflight/SciAgentGYM"))
HARNESS_DIR = Path(__file__).resolve().parent
MODEL = os.environ.get("A4_SMOKE_MODEL", "gpt-5.5")

os.environ["SCIAGENT_TEXT_ONLY"] = "1"

sys.path.insert(0, str(HARNESS_DIR))
from a4_dev_base_run_v1 import load_substrate

tq = load_substrate(SUBSTRATE_ROOT)

import gym.agent as gym_agent
import gym.config.config as cfg
import gym.utils.client_manager as cm

cfg.SUPPORTED_MODELS[MODEL] = {
    "provider": "glm", "model_name": MODEL,
    "api_base_url": "http://127.0.0.1:1/v1", "api_key": "a4-smoke",
}
for mod in (cfg, cm, gym_agent):
    if hasattr(mod, "TEMPERATURE"):
        mod.TEMPERATURE = 0.0
je = cfg.SUPPORTED_MODELS.get("gpt-4.1")
if isinstance(je, dict):
    je["api_base_url"] = "http://127.0.0.1:9/v1"
    je["api_key"] = "a4-judge-neutralized"

print("overlay:", json.dumps(cfg.SUPPORTED_MODELS[MODEL]))
print("client_manager.TEMPERATURE =", cm.TEMPERATURE)
print("config.TEMPERATURE =", cfg.TEMPERATURE)
print("agent.TEMPERATURE =", getattr(gym_agent, "TEMPERATURE", "<absent>"))
print("judge entry:", json.dumps(cfg.SUPPORTED_MODELS.get("gpt-4.1")))

from gym.config.dataset_config import get_dataset_entry, set_current_dataset_key
from gym.core.data_loader import load_refined_test_cases_from_dataset
from gym.test_executor import _derive_trace_path

run_all_refined_cases = tq.run_all_refined_cases  # import check

freeze = json.loads((HARNESS_DIR / "A4_SCORING_AND_PARTITION_FREEZE_V1.json").read_text())
dev = freeze["partitions"]["membership"]["development"]
membership = {"single": set(), "multi": set()}
for e in dev:
    m, b = e.split(":", 1)
    membership[m].add(str(b))

for ds in ("single", "multi"):
    entry = get_dataset_entry(ds)
    set_current_dataset_key(entry.key)
    dp = Path(entry.dataset_path)
    cases = load_refined_test_cases_from_dataset(dataset_path=str(dp))
    wanted = membership[ds]
    sel, done = [], []
    for case in cases:
        oid = str(case.get("original_id"))
        if oid not in wanted:
            continue
        cid = str(case.get("id"))
        assert cid.startswith(oid + "_ref_"), (cid, oid)
        hit = None
        for mode in ("with_tools_react", "with_tools"):
            tp, _ = _derive_trace_path(
                MODEL, True, cid, None, mode,
                {"_dataset_filename": dp.name}, dp.name)
            if tp is not None and tp.exists():
                hit = str(tp)
                break
        (done if hit else sel).append((cid, hit))
    print("dataset=%s total_refined=%d dev=%d already=%d to_run=%d"
          % (ds, len(cases), len(sel) + len(done), len(done), len(sel)))
    print("  to_run ids:", sorted(cid for cid, _ in sel))
    for cid, hit in done:
        print("  already traced:", cid, "->", hit)
print("SMOKE_OK")

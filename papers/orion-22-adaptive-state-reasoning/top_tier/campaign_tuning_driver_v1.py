#!/usr/bin/env python3
"""P12 tuning-phase driver (execution host only).

Runs the 4-action matrix over the TUNING families for every frozen model lane
and writes run records to runs/tuning/<model>/<instance>_<action>.json.
Refuses to run unless both frozen lanes pass a same-day echo (--echo-check
runs and records it). Never touches protected families; never computes a
score (SAB evaluation is a separate step); never reads gold fields.

Usage (billy-old, from the campaign worktree's top_tier dir):
  python3 campaign_tuning_driver_v1.py --echo-check
  python3 campaign_tuning_driver_v1.py --parquet ~/a2-deps/sab_verified.parquet --run
  python3 campaign_tuning_driver_v1.py --self-test   (CI-safe, fake adapters)
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import subprocess
from pathlib import Path

from campaign_derivation_v1 import readable_row
from campaign_runner_v1 import ACTIONS, LaneAdapter, load_freezes, run_episode_action

HERE = Path(__file__).resolve().parent
RUNS = HERE / "runs" / "tuning"
ECHO_RECORD = RUNS / "echo_record.json"


def _today() -> str:
    return _dt.date.today().isoformat()


def echo_check(identities: dict, fake: bool = False) -> dict:
    results = {}
    for ident in identities["model_identities"]:
        adapter = LaneAdapter(ident, fake=fake)
        token = f"ECHO_{ident['model_family_id']}"
        res = adapter.call(f"Reply with exactly: {token}", timeout=300)
        ok = token in (res.get("output") or "")
        results[ident["model_family_id"]] = {"ok": ok, "rc": res.get("rc")}
    record = {
        "schema": "ORION.A2.P12EchoRecord.v1",
        "date": _today(),
        "results": results,
        "all_ok": all(r["ok"] for r in results.values()),
    }
    RUNS.mkdir(parents=True, exist_ok=True)
    ECHO_RECORD.write_text(json.dumps(record, indent=1) + "\n")
    return record


def load_tuning_rows(parquet: Path, prereg: dict) -> dict[str, list[dict]]:
    import pyarrow.parquet as pq

    excluded = {3, 32, 46, 53, 54, 84}
    rows = [
        readable_row(r)
        for r in pq.read_table(parquet).to_pylist()
        if r["instance_id"] not in excluded
    ]
    fams = {}
    tuning = set(prereg["split"]["tuning_family_ids"])
    for f in prereg["families"]:
        if f["family_id"] in tuning:
            ids = set(f["instance_ids"])
            fams[f["family_id"]] = [r for r in rows if r["instance_id"] in ids]
            assert len(fams[f["family_id"]]) == f["n"], f["family_id"]
    return fams


def run_tuning(parquet: Path, fake: bool = False, limit: int | None = None) -> dict:
    harness, prereg, identities = load_freezes()
    if not fake:
        if not ECHO_RECORD.exists():
            raise RuntimeError("no echo record; run --echo-check first")
        rec = json.loads(ECHO_RECORD.read_text())
        if rec["date"] != _today() or not rec["all_ok"]:
            raise RuntimeError(f"echo record stale or failed: {rec}")
    fams = load_tuning_rows(parquet, prereg)
    done = skipped = 0
    for ident in identities["model_identities"]:
        adapter = LaneAdapter(ident, fake=fake)
        outdir = RUNS / ident["model_family_id"]
        outdir.mkdir(parents=True, exist_ok=True)
        s1_cache: dict = {}
        for fid, rows in sorted(fams.items()):
            for row in rows:
                for action in ACTIONS:
                    dest = outdir / f"{row['instance_id']}_{action}.json"
                    if dest.exists():
                        skipped += 1
                        continue
                    rec = run_episode_action(harness, adapter, rows, row, action, s1_cache)
                    dest.write_text(json.dumps(rec, ensure_ascii=False, indent=1) + "\n")
                    done += 1
                    if limit and done >= limit:
                        return {"done": done, "skipped": skipped, "stopped_at_limit": True}
    return {"done": done, "skipped": skipped, "stopped_at_limit": False}


def self_test() -> None:
    harness, prereg, identities = load_freezes()
    rec = echo_check(identities, fake=True)
    assert rec["all_ok"], rec
    # fake tuning micro-run over synthetic rows via monkeypatched loader
    g = globals()

    fake_rows = {
        prereg["split"]["tuning_family_ids"][0]: [
            readable_row(
                {
                    "instance_id": 99901,
                    "domain": "D",
                    "github_name": prereg["split"]["tuning_family_ids"][0],
                    "task_inst": "t",
                    "domain_knowledge": "",
                    "dataset_folder_tree": "|-- a.csv",
                    "dataset_preview": "a\n1",
                    "output_fname": "o.csv",
                }
            )
        ]
    }
    orig = g["load_tuning_rows"]
    g["load_tuning_rows"] = lambda p, pr: fake_rows
    try:
        out = run_tuning(Path("/nonexistent"), fake=True, limit=4)
    finally:
        g["load_tuning_rows"] = orig
    assert out["done"] >= 4 or out["skipped"] >= 4, out
    # protected refusal is structural: loader only ever yields tuning families
    assert set(fake_rows) <= set(prereg["split"]["tuning_family_ids"])
    # cleanup synthetic run records
    for ident in identities["model_identities"]:
        for f in (RUNS / ident["model_family_id"]).glob("99901_*.json"):
            f.unlink()
    print("TUNING_DRIVER_SELF_TEST_GREEN")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--echo-check", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--parquet", type=Path)
    ap.add_argument("--limit", type=int)
    a = ap.parse_args()
    if a.self_test:
        self_test()
        return 0
    _, _, identities = load_freezes()
    if a.echo_check:
        rec = echo_check(identities)
        print(json.dumps(rec, indent=1))
        return 0 if rec["all_ok"] else 1
    if a.run:
        if not a.parquet:
            ap.error("--parquet required with --run")
        out = run_tuning(a.parquet, limit=a.limit)
        print(json.dumps(out))
        return 0
    ap.error("choose --self-test, --echo-check or --run")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

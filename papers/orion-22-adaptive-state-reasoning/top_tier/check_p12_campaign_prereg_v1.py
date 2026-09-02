#!/usr/bin/env python3
"""Fail-closed verifier for P12_CAMPAIGN_PREREG_V1.json.

Recomputes the family census, the S_FAMILY_DIFFICULTY_PRIOR values and the
tuning/protected split from the exact pinned verified parquet, and asserts
byte-level agreement with the frozen prereg. Reads ONLY the four licensed
metadata fields for the prior; the gold-side columns are never accessed by the
recomputation path. Any disagreement, any protected-minimum violation, or any
non-false execution flag terminates RED.

Usage:
  check_p12_campaign_prereg_v1.py --self-test
  check_p12_campaign_prereg_v1.py --freeze P12_CAMPAIGN_PREREG_V1.json \
      --parquet /tmp/scienceagentbench-verified.parquet
"""

from __future__ import annotations

import argparse
import copy
import json
import math
import random
import statistics
import sys
from collections import Counter
from pathlib import Path

EXCLUDED_INSTANCE_IDS = {3, 32, 46, 53, 54, 84}
CLEAN_COUNT = 96
PRIOR_FIELDS = ("task_inst", "domain_knowledge", "dataset_folder_tree", "subtask_categories")
SEED = 20260902


def _file_count(tree: str) -> int:
    return sum(
        1
        for line in tree.splitlines()
        if line.strip() and not line.strip().endswith("/")
    )


def _comma_count(s: str) -> int:
    return len([x for x in s.split(",") if x.strip()])


def recompute(rows: list[dict]) -> dict:
    clean = sorted(
        (r for r in rows if r["instance_id"] not in EXCLUDED_INSTANCE_IDS),
        key=lambda r: r["instance_id"],
    )
    if len(clean) != CLEAN_COUNT:
        raise ValueError(f"clean count {len(clean)} != {CLEAN_COUNT}")

    feats = []
    for r in clean:
        # The recomputation path touches only the licensed metadata fields.
        feats.append(
            {
                "iid": r["instance_id"],
                "fam": r["github_name"],
                "dom": r["domain"],
                "f1": math.log(1 + len(r["task_inst"].encode())),
                "f2": math.log(1 + len((r["domain_knowledge"] or "").encode())),
                "f3": math.log(1 + _file_count(r["dataset_folder_tree"] or "")),
                "f4": float(_comma_count(r["subtask_categories"] or "")),
            }
        )
    for k in ("f1", "f2", "f3", "f4"):
        vals = [f[k] for f in feats]
        mu = statistics.mean(vals)
        sd = statistics.pstdev(vals)
        for f in feats:
            f[k + "z"] = 0.0 if sd == 0 else (f[k] - mu) / sd
    for f in feats:
        f["d"] = round(f["f1z"] + f["f2z"] + f["f3z"] + f["f4z"], 6)

    fams: dict[str, list[dict]] = {}
    for f in feats:
        fams.setdefault(f["fam"], []).append(f)

    fam_rows = []
    for fam, members in sorted(fams.items()):
        domc = Counter(m["dom"] for m in members)
        primary = sorted(domc.items(), key=lambda x: (-x[1], x[0]))[0][0]
        fam_rows.append(
            {
                "family_id": fam,
                "primary_domain": primary,
                "domains": sorted(domc),
                "instance_ids": sorted(m["iid"] for m in members),
                "n": len(members),
                "difficulty_prior": round(
                    statistics.mean(m["d"] for m in members), 6
                ),
            }
        )

    by_dom: dict[str, list[dict]] = {}
    for fr in fam_rows:
        by_dom.setdefault(fr["primary_domain"], []).append(fr)
    rng = random.Random(SEED)
    tuning, protected = [], []
    for dom in sorted(by_dom):
        rows_d = sorted(by_dom[dom], key=lambda r: r["family_id"])
        k = max(1, len(rows_d) // 4)
        pick = set(rng.sample(range(len(rows_d)), k))
        for i, fr in enumerate(rows_d):
            (tuning if i in pick else protected).append(fr["family_id"])

    return {
        "families": fam_rows,
        "tuning_family_ids": tuning,
        "protected_family_ids": protected,
    }


def verify(freeze: dict, rows: list[dict]) -> dict:
    errors: list[str] = []

    for flag, value in freeze["flags"].items():
        if value is not False:
            errors.append(f"execution flag not false: {flag}")

    live = recompute(rows)

    if live["families"] != freeze["families"]:
        errors.append("family census / difficulty priors disagree with freeze")
    if live["tuning_family_ids"] != freeze["split"]["tuning_family_ids"]:
        errors.append("tuning split disagrees with freeze")
    if live["protected_family_ids"] != freeze["split"]["protected_family_ids"]:
        errors.append("protected split disagrees with freeze")

    protected = set(freeze["split"]["protected_family_ids"])
    tuning = set(freeze["split"]["tuning_family_ids"])
    if protected & tuning:
        errors.append("split overlap")
    if len(protected) < 20:
        errors.append(f"protected families {len(protected)} < 20")
    prot_domains: set[str] = set()
    prot_instances = 0
    for fr in freeze["families"]:
        if fr["family_id"] in protected:
            prot_domains.update(fr["domains"])
            prot_instances += fr["n"]
    if len(prot_domains) < 3:
        errors.append(f"protected domains {len(prot_domains)} < 3")
    if prot_instances != freeze["split"]["protected_instances"]:
        errors.append("protected instance count disagrees with freeze")

    forbidden = set(freeze["difficulty_prior"]["gold_fields_forbidden"])
    declared = set(freeze["difficulty_prior"]["licensed_input_fields"])
    if declared != set(PRIOR_FIELDS):
        errors.append("declared prior inputs differ from checker inputs")
    if forbidden & declared:
        errors.append("a forbidden gold field is declared as a prior input")

    return {
        "schema": "ORION.A2.P12CampaignPreregCheckResult.v1",
        "decision": "RED" if errors else "GREEN",
        "errors": errors,
        "families": len(freeze["families"]),
        "tuning_families": len(tuning),
        "protected_families": len(protected),
        "protected_instances": prot_instances,
        "protected_domains": sorted(prot_domains),
        "flags_all_false": all(v is False for v in freeze["flags"].values()),
    }


def _load_rows(parquet_path: Path) -> list[dict]:
    import pyarrow.parquet as pq

    return pq.read_table(parquet_path).to_pylist()


def self_test(freeze: dict, rows: list[dict]) -> None:
    base = verify(freeze, rows)
    assert base["decision"] == "GREEN", f"clean case must pass: {base['errors']}"

    m = copy.deepcopy(freeze)
    m["families"][0]["difficulty_prior"] = round(
        m["families"][0]["difficulty_prior"] + 0.000001, 6
    )
    assert verify(m, rows)["decision"] == "RED", "mutated prior must fail"

    m = copy.deepcopy(freeze)
    moved = m["split"]["protected_family_ids"].pop(0)
    m["split"]["tuning_family_ids"].append(moved)
    assert verify(m, rows)["decision"] == "RED", "moved family must fail"

    m = copy.deepcopy(freeze)
    m["flags"]["campaign_executed"] = True
    assert verify(m, rows)["decision"] == "RED", "true flag must fail"

    m = copy.deepcopy(freeze)
    m["difficulty_prior"]["licensed_input_fields"] = list(PRIOR_FIELDS) + [
        "gold_program_name"
    ]
    m["difficulty_prior"]["gold_fields_forbidden"] = ["output_fname"]
    assert verify(m, rows)["decision"] == "RED", "gold input must fail"

    mrows = copy.deepcopy(rows)
    for r in mrows:
        if r["instance_id"] == 5:
            r["task_inst"] = r["task_inst"] + " MUTATED"
    assert verify(freeze, mrows)["decision"] == "RED", "mutated substrate must fail"

    print("SELF_TEST_GREEN: 6/6 hostile controls behave")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--freeze", type=Path)
    ap.add_argument("--parquet", type=Path)
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    here = Path(__file__).resolve().parent
    freeze_path = args.freeze or here / "P12_CAMPAIGN_PREREG_V1.json"
    freeze = json.loads(freeze_path.read_text())

    if args.self_test:
        if not args.parquet:
            print(
                "SELF_TEST_SKIPPED_WITHOUT_PARQUET: structural checks only",
            )
            for flag, value in freeze["flags"].items():
                assert value is False, flag
            assert len(freeze["split"]["protected_family_ids"]) >= 20
            print("STRUCTURAL_GREEN")
            return 0
        self_test(freeze, _load_rows(args.parquet))
        return 0

    if not args.parquet:
        print("ERROR: --parquet required", file=sys.stderr)
        return 2
    result = verify(freeze, _load_rows(args.parquet))
    print(json.dumps(result, indent=1))
    return 0 if result["decision"] == "GREEN" else 1


if __name__ == "__main__":
    raise SystemExit(main())

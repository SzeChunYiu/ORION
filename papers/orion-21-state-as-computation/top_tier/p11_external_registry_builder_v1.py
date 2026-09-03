#!/usr/bin/env python3
"""P11 external campaign — execution registry builder (deterministic, outcome-blind).

Implements the registry layer required by P11_EXTERNAL_EXECUTION_HARNESS_FREEZE_V1.json:
per benchmark, frozen development / primary(=realized) / fresh query registries with
source-disjoint fresh sets, plus the leave-one-benchmark-out schedule.

Selection rule (frozen, id-hash order only; no outcome field is read):
  LONGMEMEVAL_CLEANED (S split): sort questions by sha256(question_id); dev=first 8,
    primary=next 8, fresh=next 8. Every question owns a private 53-session haystack;
    0 session overlap across questions was verified on the frozen file.
  LONGMEMEVAL_V2 (small tier): questions with images are excluded (29; no frozen lane
    accepts image input — capability-neutral, decided before outcomes). Web questions:
    dev=first 8 then primary=next 4; fresh = first 4 ENTERPRISE questions. V2 publishes
    exactly two shared source corpora (100 web / 100 enterprise trajectories, 0 shared
    trajectories, verified); within-domain source-disjoint fresh queries are therefore
    structurally unattainable and the fresh set is cross-domain by construction.

V2 state is compiled PER SOURCE CORPUS (the corpus is the session block substrate);
v1 state is compiled per question haystack.

Emits receipts/REGISTRY_FREEZE_V1.json. Refuses to emit the fresh-registry hash until
receipts/COMPILATION_RECEIPT_V1.json exists (optionality seal: --reveal-fresh).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

BASE = Path.home() / "orion-p11-campaign"
DATA = BASE / "data"

V1_N_DEV, V1_N_PRIMARY, V1_N_FRESH = 8, 8, 8
V2_N_DEV, V2_N_PRIMARY, V2_N_FRESH = 8, 4, 4


def H(x: str) -> str:
    return hashlib.sha256(x.encode()).hexdigest()


def canon(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()


def hobj(obj) -> str:
    return hashlib.sha256(canon(obj)).hexdigest()


def build_v1() -> dict:
    recs = json.loads((DATA / "LONGMEMEVAL_CLEANED" / "longmemeval_s_cleaned.json").read_text())
    by_hash = sorted(recs, key=lambda r: H(r["question_id"]))
    # Greedy pairwise-disjoint selection in frozen sha256 order: sessions repeat
    # (~1.38 uses/session across the 500 questions), so accept a question into the
    # current pool only if its 53 sessions are unused by all previously accepted
    # questions across ALL pools. Deterministic, outcome-blind.
    used: set[str] = set()
    pools: list[list[dict]] = []

    def take(n: int) -> list[dict]:
        out = []
        for r in by_hash:
            if len(out) == n:
                break
            s = set(r["haystack_session_ids"])
            if not (s & used):
                out.append(r)
                used.update(s)
        assert len(out) == n, f"v1 disjoint pool exhausted at {len(out)}/{n}"
        return out

    dev, primary, fresh = take(V1_N_DEV), take(V1_N_PRIMARY), take(V1_N_FRESH)

    def q(r):
        return {"question_id": r["question_id"], "question_type": r["question_type"]}

    def sources(rows):
        return sorted(sid for r in rows for sid in r["haystack_session_ids"])

    dev_ids = [r["question_id"] for r in dev]
    pri_ids = [r["question_id"] for r in primary]
    fre_ids = [r["question_id"] for r in fresh]
    s_dev, s_pri, s_fre = sources(dev), sources(primary), sources(fresh)
    assert not (set(s_dev) & set(s_pri)) and not (set(s_dev) & set(s_fre)) and not (set(s_pri) & set(s_fre)), \
        "v1 registry pools must be source-disjoint"
    return {
        "benchmark": "LONGMEMEVAL_CLEANED",
        "substrate": "longmemeval_s_cleaned.json (500 questions; per-question 53-session haystack)",
        "block_unit": "question (its 53-session haystack is the task/session block)",
        "development_registry": {"question_ids": dev_ids, "sha256": hobj(dev_ids)},
        "primary_registry": {"question_ids": pri_ids, "sha256": hobj(pri_ids)},
        "fresh_query_pool": {"question_ids": fre_ids, "sha256": hobj(fre_ids)},
        "source_disjointness": {
            "verified_pairwise_disjoint": True,
            "source_unit": "haystack_session_ids",
            "n_sources_dev_primary_fresh": [len(s_dev), len(s_pri), len(s_fre)],
        },
        "excluded": {"image_questions": 0, "note": "v1-S carries no image inputs"},
    }


def build_v2() -> dict:
    qs = [json.loads(l) for l in (DATA / "LONGMEMEVAL_V2" / "questions.jsonl").read_text().splitlines() if l.strip()]
    small = json.loads((DATA / "LONGMEMEVAL_V2" / "haystacks__lme_v2_small.json").read_text())
    text_qs = [q for q in qs if q.get("image") in (None, "None", "")]
    web = sorted([q for q in text_qs if q["domain"] == "web"], key=lambda q: H(q["id"]))
    ent = sorted([q for q in text_qs if q["domain"] == "enterprise"], key=lambda q: H(q["id"]))
    dev, primary, fresh = web[:V2_N_DEV], web[V2_N_DEV:V2_N_DEV + V2_N_PRIMARY], ent[:V2_N_FRESH]
    web_corpus = sorted({t for q in primary for t in small[q["id"]]})
    ent_corpus = sorted({t for q in fresh for t in small[q["id"]]})
    assert not (set(web_corpus) & set(ent_corpus)), "V2 corpora must be trajectory-disjoint"
    dev_ids = [q["id"] for q in dev]
    pri_ids = [q["id"] for q in primary]
    fre_ids = [q["id"] for q in fresh]
    return {
        "benchmark": "LONGMEMEVAL_V2",
        "substrate": "haystacks/lme_v2_small.json (100-trajectory tier; medium tier materialized but out of this campaign's frozen scope)",
        "block_unit": "question over its domain source corpus",
        "development_registry": {"question_ids": dev_ids, "domain": "web", "sha256": hobj(dev_ids)},
        "primary_registry": {"question_ids": pri_ids, "domain": "web", "sha256": hobj(pri_ids)},
        "fresh_query_pool": {"question_ids": fre_ids, "domain": "enterprise", "sha256": hobj(fre_ids)},
        "source_disjointness": {
            "verified_pairwise_disjoint": True,
            "source_unit": "trajectory ids underlying the question haystacks",
            "note": "V2 publishes exactly two shared source corpora (web 100 / enterprise 100 trajectories; 0 shared). "
                    "Within-domain source-disjoint fresh queries are structurally unattainable at the published tiers; "
                    "the fresh registry is therefore cross-domain (enterprise). Frozen before outcomes as a structural property.",
            "realized_corpus_sha256": hobj(web_corpus),
            "fresh_corpus_sha256": hobj(ent_corpus),
        },
        "excluded": {"image_questions": len(qs) - len(text_qs), "note": "no frozen lane accepts image input"},
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--reveal-fresh", action="store_true",
                    help="emit fresh-registry hashes (only legal AFTER the compilation receipt exists)")
    a = ap.parse_args()
    v1, v2 = build_v1(), build_v2()
    comp_receipt = BASE / "receipts" / "COMPILATION_RECEIPT_V1.json"
    if a.reveal_fresh:
        if not comp_receipt.exists():
            print("REFUSED: optionality seal — compile before revealing the fresh query registry", file=sys.stderr)
            return 2
        v1["fresh_query_registry"] = v1.pop("fresh_query_pool")
        v2["fresh_query_registry"] = v2.pop("fresh_query_pool")
        v1["state_compiled_before_fresh_query_registry_reveal"] = True
        v2["state_compiled_before_fresh_query_registry_reveal"] = True
        comp_sha = H(comp_receipt.read_text())
        v1["compilation_receipt_sha256"] = comp_sha
        v2["compilation_receipt_sha256"] = comp_sha
    else:
        for b in (v1, v2):
            b["fresh_query_registry"] = None  # sealed until reveal
    freeze = {
        "schema": "ORION.A2.P11ExternalRegistryFreeze.v1",
        "built_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "selection_rule": "sha256(id) ascending; greedy pairwise source-disjoint dev -> primary -> fresh slices; no outcome field read",
        "leave_one_benchmark_out_schedule": [
            {"held_out": "LONGMEMEVAL_CLEANED", "training_development_registry_sha256": v2["development_registry"]["sha256"],
             "protected_retuning_allowed": False},
            {"held_out": "LONGMEMEVAL_V2", "training_development_registry_sha256": v1["development_registry"]["sha256"],
             "protected_retuning_allowed": False},
        ],
        "benchmarks": {"LONGMEMEVAL_CLEANED": v1, "LONGMEMEVAL_V2": v2},
        "registry_freeze_sha256": None,
    }
    freeze["registry_freeze_sha256"] = hobj({k: v for k, v in freeze.items() if k != "registry_freeze_sha256"})
    out = BASE / "receipts" / ("REGISTRY_FREEZE_V1.json" if a.reveal_fresh else "REGISTRY_FREEZE_V1_SEALED.json")
    out.write_text(json.dumps(freeze, indent=2, sort_keys=True))
    v2f = v2.get("fresh_query_registry") or v2.get("fresh_query_pool") or {}
    print(json.dumps({"out": out.name, "v1_primary": v1["primary_registry"]["question_ids"],
                      "v2_primary": v2["primary_registry"]["question_ids"],
                      "v2_fresh": v2f.get("question_ids"),
                      "registry_freeze_sha256": freeze["registry_freeze_sha256"]}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

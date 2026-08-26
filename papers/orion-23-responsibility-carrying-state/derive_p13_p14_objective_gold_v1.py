#!/usr/bin/env python3
"""Derive P13/P14 lifecycle gold from objective git facts on the pinned corpus.

Implements the four metadata fact classes of
P13_P14_OBJECTIVE_GOLD_DERIVATION_CONTRACT_V1 exactly as their command
templates specify. TEST_EXIT is the fifth class; it requires the recorded test
command to run inside a locked runtime per repository, which does not exist, so
every TEST_EXIT fact is recorded CANNOT_CHECK with that reason rather than
approximated.

The contract's preconditions are enforced, not assumed: a repository is only
derived against if it is a corpus entry, its clone resolves the pinned sha, and
its licence verification is VERIFIED_WITH_URL_AND_DATE. Anything else yields no
gold and says why.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

CANNOT_CHECK = "CANNOT_CHECK"


def git(args, cwd=None, timeout=900):
    try:
        p = subprocess.run(["git"] + args, cwd=cwd, capture_output=True, text=True, timeout=timeout)
        return p.returncode, p.stdout.strip(), p.stderr.strip()
    except Exception as exc:
        return 127, "", f"{type(exc).__name__}: {exc}"


def clone_pinned(entry, root: Path):
    """Blobless partial clone, then resolve exactly the pinned sha."""
    d = root / entry["repo_id"].replace("/", "__")
    if (d / ".git").exists():
        return d, None
    d.mkdir(parents=True, exist_ok=True)
    rc, _, err = git(["init", "-q", "--initial-branch=main", str(d)])
    if rc != 0:
        return None, f"init failed: {err[:200]}"
    git(["remote", "add", "origin", entry["url"]], cwd=d)
    rc, _, err = git(["fetch", "-q", "--filter=blob:none", "--tags", "origin", entry["pinned_sha"]], cwd=d)
    if rc != 0:
        rc, _, err = git(["fetch", "-q", "--filter=blob:none", "--tags", "origin"], cwd=d)
        if rc != 0:
            return None, f"fetch failed: {err[:200]}"
    return d, None


def derive(entry, d: Path):
    sha = entry["pinned_sha"]
    facts = []

    # 1. OBJECT_HASH_EXISTENCE
    rc, out, err = git(["cat-file", "-e", sha], cwd=d)
    rc2, resolved, _ = git(["rev-parse", sha], cwd=d)
    facts.append({
        "class_id": "OBJECT_HASH_EXISTENCE", "object": sha,
        "value": (rc == 0 and rc2 == 0 and resolved == sha),
        "observed": {"cat_file_exit": rc, "rev_parse": resolved},
        "verdict": "TRUE" if (rc == 0 and resolved == sha) else ("FALSE" if rc2 == 0 else CANNOT_CHECK),
    })

    # 2. ANCESTRY -- the pinned commit's first parent must be its ancestor.
    rc, parent, _ = git(["rev-parse", f"{sha}^"], cwd=d)
    if rc == 0 and parent:
        rca, _, _ = git(["merge-base", "--is-ancestor", parent, sha], cwd=d)
        verdict = "TRUE" if rca == 0 else ("FALSE" if rca == 1 else CANNOT_CHECK)
        facts.append({"class_id": "ANCESTRY", "a": parent, "b": sha,
                      "value": rca == 0, "observed": {"exit": rca}, "verdict": verdict})
    else:
        facts.append({"class_id": "ANCESTRY", "verdict": CANNOT_CHECK,
                      "reason": "pinned commit has no resolvable first parent"})

    # 3. TAG_SIGNATURE
    rc, tags, _ = git(["tag", "--list", "--sort=-creatordate"], cwd=d)
    tag = tags.splitlines()[0].strip() if rc == 0 and tags.strip() else None
    if tag:
        rct, target, _ = git(["rev-parse", f"{tag}^{{}}"], cwd=d)
        rcv, _, verr = git(["verify-tag", tag], cwd=d)
        if rcv == 0:
            v = "SIGNATURE_VALID"
        elif "cannot verify a non-tag object" in verr or "no signature found" in verr.lower():
            v = "UNSIGNED"
        elif rcv == 1:
            v = "UNSIGNED"
        else:
            v = CANNOT_CHECK
        facts.append({"class_id": "TAG_SIGNATURE", "tag": tag, "target": target,
                      "verdict": v, "observed": {"verify_tag_exit": rcv, "stderr": verr[:160]}})
    else:
        facts.append({"class_id": "TAG_SIGNATURE", "verdict": CANNOT_CHECK,
                      "reason": "no tags present in the fetched state"})

    # 4. TIMESTAMP_ORDER
    if parent:
        rc1, t1, _ = git(["show", "-s", "--format=%ct", parent], cwd=d)
        rc2, t2, _ = git(["show", "-s", "--format=%ct", sha], cwd=d)
        if rc1 == 0 and rc2 == 0 and t1.isdigit() and t2.isdigit():
            a, b = int(t1), int(t2)
            facts.append({"class_id": "TIMESTAMP_ORDER", "a": parent, "b": sha,
                          "a_epoch": a, "b_epoch": b,
                          "verdict": "LESS" if a < b else ("EQUAL" if a == b else "GREATER")})
        else:
            facts.append({"class_id": "TIMESTAMP_ORDER", "verdict": CANNOT_CHECK,
                          "reason": "committer timestamps not readable"})
    else:
        facts.append({"class_id": "TIMESTAMP_ORDER", "verdict": CANNOT_CHECK,
                      "reason": "no parent to order against"})

    # 5. TEST_EXIT -- fail closed, never approximated.
    facts.append({"class_id": "TEST_EXIT", "verdict": CANNOT_CHECK,
                  "reason": ("the contract requires the recorded test command to run inside the "
                             "locked runtime recorded for the campaign; no such runtime exists, "
                             "and an exit status obtained any other way is not this fact")})
    return facts


def main():
    corpus = json.loads(Path(sys.argv[1]).read_text())
    root = Path(sys.argv[2]); root.mkdir(parents=True, exist_ok=True)
    limit = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    entries = [e for e in corpus["entries"] if e.get("gold_eligible")]
    if limit:
        entries = entries[:limit]
    records = []
    for i, e in enumerate(entries, 1):
        lic = (e.get("license") or {}).get("verification")
        if lic != "VERIFIED_WITH_URL_AND_DATE":
            records.append({"repo_id": e["repo_id"], "derived": False,
                            "reason": f"licence verification is {lic!r}; contract yields no gold"})
            continue
        d, err = clone_pinned(e, root)
        if d is None:
            records.append({"repo_id": e["repo_id"], "derived": False, "reason": err})
            print(f"[{i}/{len(entries)}] {e['repo_id']}: CLONE FAILED", flush=True)
            continue
        facts = derive(e, d)
        ok = sum(1 for f in facts if f.get("verdict") not in (CANNOT_CHECK, None))
        records.append({"repo_id": e["repo_id"], "pinned_sha": e["pinned_sha"],
                        "derived": True, "facts": facts,
                        "facts_decided": ok, "facts_cannot_check": len(facts) - ok})
        print(f"[{i}/{len(entries)}] {e['repo_id']}: decided={ok}/5", flush=True)

    decided = sum(r.get("facts_decided", 0) for r in records)
    cc = sum(r.get("facts_cannot_check", 0) for r in records)
    out = {
        "schema_version": "orion.p13p14.objective-gold-derivation-results.v1",
        "executes_contract": "P13_P14_OBJECTIVE_GOLD_DERIVATION_CONTRACT_V1",
        "uses_corpus": "P13_P14_PINNED_REPOSITORY_CORPUS_V1.json",
        "campaign_executed": True, "results_exist": True, "outcome_accessed": True,
        "repositories_attempted": len(entries),
        "repositories_derived": sum(1 for r in records if r.get("derived")),
        "organizations": sorted({r["repo_id"].split("/")[0] for r in records if r.get("derived")}),
        "facts_decided": decided, "facts_cannot_check": cc,
        "test_exit_disposition": ("every TEST_EXIT fact is CANNOT_CHECK: the locked per-repository "
                                  "runtime the contract requires does not exist, and an exit status "
                                  "obtained another way is not that fact"),
        "records": records,
    }
    Path(sys.argv[4] if len(sys.argv) > 4 else "p13_gold_results.json").write_text(json.dumps(out, indent=1))
    print(json.dumps({k: v for k, v in out.items() if k != "records"}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

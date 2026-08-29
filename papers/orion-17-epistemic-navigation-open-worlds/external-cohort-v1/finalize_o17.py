#!/usr/bin/env python3
"""Final ORION-17 cohort assembly: rank-order acceptance plus an artifact screen.

Stratum A (`small_fewedge_dense`): accept the first 10 qualifying candidates in
rank order. No screen is needed -- the repo-root module-naming artifact can only
LOWER measured density, so it cannot falsely admit anything to the dense stratum.

Stratum B (`large_manyedge_sparse`): the same artifact CAN falsely admit here, by
making a dense package look sparse. So eligibility for stratum B requires density
< 1.5 under BOTH the campaign convention AND a re-rooted cross-check that removes
the `src.` prefix. Candidates are screened in rank order and the first 10 that
pass are accepted.

The screen is structural and outcome-blind: it re-measures an import graph and
consults no policy, no history and no outcome. Cohort metrics remain reported on
the campaign's own convention, because the frozen thresholds were derived there.
"""
import glob
import json
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from measure_p7 import build_import_graph  # noqa: E402

TARGET = 10
DENSITY_T, MODULE_T, EDGE_T = 1.5, 49, 216
WORK = HERE / "final_work"


def predictions(m, e):
    return {
        "density_rule": "unsound" if (e / m) >= DENSITY_T else "sound",
        "module_rule": "unsound" if m >= MODULE_T else "sound",
        "edge_rule": "unsound" if e >= EDGE_T else "sound",
    }


def screen(r, attempts=3):
    """Re-measure with the package parent as root.

    Returns (verdict, detail) where verdict is "PASS", "FAIL" or "CANNOT_CHECK".
    CANNOT_CHECK is NEVER merged into FAIL: failing to screen a candidate is not
    the same as screening it and finding it contaminated. A CANNOT_CHECK
    candidate is excluded conservatively (it cannot be admitted unverified) but
    is recorded in its own list.
    """
    d = WORK / r["project"].replace("/", "_")
    rc = 1
    for _ in range(attempts):
        shutil.rmtree(d, ignore_errors=True)
        try:
            rc = subprocess.run(["git", "clone", "-q", "--depth", "1",
                                 "--filter=blob:none",
                                 f"https://github.com/{r['repo']}", str(d)],
                                capture_output=True, timeout=900).returncode
        except subprocess.TimeoutExpired:
            rc = 124
        if rc == 0:
            break
    if rc:
        shutil.rmtree(d, ignore_errors=True)
        return "CANNOT_CHECK", {"screen": "CANNOT_CHECK",
                                "reason": f"clone_failed_after_{attempts}_attempts"}
    subprocess.run(["git", "checkout", "-q", r["sha"]], cwd=d,
                   capture_output=True, timeout=900)
    pkg = r["package"]
    if "/" in pkg:
        parent, leaf = pkg.rsplit("/", 1)
        mods, edges = build_import_graph(d / parent, leaf)
    else:
        mods, edges = build_import_graph(d, pkg)
    n = sum(len(v) for v in edges.values())
    shutil.rmtree(d, ignore_errors=True)
    if not mods:
        return "CANNOT_CHECK", {"screen": "CANNOT_CHECK",
                                "reason": "rerooted_measurement_found_no_modules"}
    dens = n / len(mods)
    verdict = "PASS" if dens < DENSITY_T else "FAIL"
    return verdict, {"screen": verdict,
                     "rerooted_modules": len(mods), "rerooted_edges": n,
                     "rerooted_density": round(dens, 4),
                     "edge_delta_vs_as_measured": n - r["import_edges"]}


def entry(r, extra=None):
    p = predictions(r["modules"], r["import_edges"])
    e = {
        "project": r["project"],
        "repo_url": f"https://github.com/{r['repo']}",
        "pinned_commit_sha": r["sha"],
        "package_dir": r["package"],
        "pypi_download_rank": r["rank"],
        "modules": r["modules"],
        "import_edges": r["import_edges"],
        "edges_per_module": r["edges_per_module"],
        "predictions": p,
        "disagrees_with_module_rule": p["density_rule"] != p["module_rule"],
        "disagrees_with_edge_rule": p["density_rule"] != p["edge_rule"],
    }
    if extra:
        e["artifact_screen"] = extra
    return e


def main():
    rows = []
    for f in sorted(glob.glob(str(HERE / "shard_*.jsonl"))):
        for line in open(f):
            if line.strip():
                rows.append(json.loads(line))
    # A repair pass re-measured every candidate lost to ENOSPC during the
    # parallel sweep. Where a repair row exists it SUPERSEDES the original
    # failure row, so each project is counted once, at its repaired outcome.
    superseded = {r["project"] for r in rows if r.get("repair_pass")}
    n_superseded = sum(1 for r in rows
                       if not r.get("repair_pass") and r["project"] in superseded)
    rows = [r for r in rows
            if r.get("repair_pass") or r["project"] not in superseded]
    rows.sort(key=lambda r: r["rank"])
    WORK.mkdir(parents=True, exist_ok=True)

    A = [entry(r) for r in rows
         if r.get("stratum") == "small_fewedge_dense"][:TARGET]

    B, rejected, unscreenable = [], [], []
    for r in rows:
        if len(B) >= TARGET:
            break
        if r.get("stratum") != "large_manyedge_sparse":
            continue
        verdict, detail = screen(r)
        print(f"screen {r['project']:16s} {verdict} "
              f"reroot_d={detail.get('rerooted_density')}", flush=True)
        if verdict == "PASS":
            B.append(entry(r, detail))
        elif verdict == "FAIL":
            rejected.append(entry(r, detail))
        else:
            unscreenable.append(entry(r, detail))

    accepted = A + B
    dm = sum(1 for e in accepted if e["disagrees_with_module_rule"])
    de = sum(1 for e in accepted if e["disagrees_with_edge_rule"])
    db = sum(1 for e in accepted if e["disagrees_with_module_rule"]
             and e["disagrees_with_edge_rule"])

    reasons = {}
    for r in rows:
        if not r.get("usable"):
            reasons[r.get("reason", "?")] = reasons.get(r.get("reason", "?"), 0) + 1

    doc = {
        "schema": "ORION.ORION17.RuleDisagreementCohort.v1",
        "identity": "ORION17.RULE_DISAGREEMENT.v1.external_cohort",
        "terminal": "COHORT_ACQUIRED__OUTCOME_BLIND__NO_OUTCOME_AUTHORITY",
        "grants_scientific_authority": False,
        "outcomes_accessed": False,
        "policy_executed": False,
        "protocol_source": ("papers/publication_closure/issue1701_ab_multiplex_v1/"
                            "ORION17_RULE_DISAGREEMENT_PROTOCOL_V1.json "
                            "(branch chatgpt/issue1701-canonical-ab-multiplex-20260829)"),
        "frozen_constants": {
            "density_rule": "unsound iff edges/modules >= 1.5",
            "module_rule": "unsound iff modules >= 49",
            "edge_rule": "unsound iff edges >= 216",
            "note": "Historical constants from the protocol. NOT re-derived, NOT re-fitted.",
            "derivation_reproduced": ("modules (24+74)/2 = 49 and edges (19+412)/2 = 215.5 -> 216, "
                                      "from max-sound flask and min-unsound tornado across the 8 "
                                      "calibration+evaluation projects. Both close exactly, which is "
                                      "the evidence the exclusion list below is complete."),
        },
        "builder": {
            "function": "build_import_graph",
            "source": ("papers/orion-17-epistemic-navigation-open-worlds/transitions/"
                       "measure_p7_closure_retention_v1.py on branch "
                       "origin/shadow/orion17-density-v2-recovery-20260829"),
            "validation_against_published_table": {
                "requests": {"published": [19, 16], "reproduced": [19, 16], "exact": True},
                "tornado": {"published": [74, 412], "reproduced": [74, 412], "exact": True},
                "networkx": {"published": [583, 1245], "reproduced": [583, 1245], "exact": True},
                "django": {"published": [906, 3336], "reproduced": [906, 3315], "exact": False},
                "sympy": {"published": [1566, 13622], "reproduced": [1566, 13591], "exact": False},
                "summary": "module counts 5/5 exact; edge counts 3/5 exact, two deltas sub-1% on the most actively developed repos",
            },
        },
        "enumeration": {
            "source": "https://hugovk.github.io/top-pypi-packages/top-pypi-packages.min.json",
            "ordering": "download_count descending; fixed before any measurement",
            "rule": "first 10 qualifying candidates per stratum in rank order",
            "examined": len(rows),
            "usable": sum(1 for r in rows if r.get("usable")),
            "reject_reasons": reasons,
            "max_rank_reached": max(r["rank"] for r in rows) if rows else 0,
            "enospc_repair": {
                "why": ("The 10-way parallel sweep filled the disk while cloning very "
                        "large generated monorepos. Those failures were NOT random -- "
                        "they hit large repositories, exactly the population the sparse "
                        "stratum draws from -- so leaving them out would have biased "
                        "stratum B."),
                "candidates_repaired": n_superseded,
                "method": ("re-measured one at a time with a sparse checkout and a "
                           "free-space guard, so only the package subtree was fetched"),
                "outcome": ("Every ENOSPC-lost candidate was re-measured. One, faker at "
                            "rank 406, qualified for the sparse stratum and is now in "
                            "the cohort; the rest were excluded by the same "
                            "package-directory rule applied to every other candidate. "
                            "No candidate remains unmeasured because of disk space."),
                "residual_enospc_rejections": 0,
            },
        },
        "artifact_screen": {
            "applies_to": "large_manyedge_sparse only",
            "why_not_stratum_A": ("The repo-root module-naming artifact can only LOWER measured "
                                  "density, so it cannot falsely admit anything to the dense "
                                  "stratum. Stratum A needs no screen for validity."),
            "rule": "eligible only if density < 1.5 under BOTH the campaign convention and the re-rooted cross-check",
            "screened": len(B) + len(rejected),
            "rejected_by_screen": [e["project"] for e in rejected],
            "rejected_detail": rejected,
            "cannot_check_not_merged_into_rejected": [e["project"] for e in unscreenable],
            "cannot_check_detail": unscreenable,
            "cannot_check_policy": ("A candidate that could not be screened is excluded "
                                    "conservatively -- it cannot be admitted unverified -- "
                                    "but is recorded separately. Failing to screen is not "
                                    "the same as screening and finding contamination."),
        },
        "counts": {"small_fewedge_dense": len(A), "large_manyedge_sparse": len(B)},
        "target_per_stratum": TARGET,
        "complete": len(A) >= TARGET and len(B) >= TARGET,
        "cohort": {"small_fewedge_dense": A, "large_manyedge_sparse": B},
        "rule_disagreement": {
            "accepted_total": len(accepted),
            "disagree_with_module_rule": dm,
            "disagree_with_edge_rule": de,
            "disagree_with_both_rivals": db,
            "interpretation": ("DEFINITIONAL, NOT EMPIRICAL. Each stratum's criteria are exactly "
                               "the region where the density rule and both absolute-size rivals "
                               "give opposite predictions, so full disagreement is guaranteed by "
                               "the selection criteria. This is a correctness check on the "
                               "selector -- any value below the accepted total would be a bug. "
                               "It is NOT evidence for or against the density rule."),
        },
        "excluded_dev_eval_repos": ["numpy", "scipy", "flask", "requests",
                                    "networkx", "django", "tornado", "sympy"],
    }
    (HERE / "COHORT_V1.json").write_text(json.dumps(doc, indent=2) + "\n")
    with (HERE / "CANDIDATES_EXAMINED_V1.jsonl").open("w") as fh:
        for r in rows:
            fh.write(json.dumps(r, sort_keys=True) + "\n")
    shutil.rmtree(WORK, ignore_errors=True)
    print(json.dumps({"A": len(A), "B": len(B), "complete": doc["complete"],
                      "screen_rejected": [e["project"] for e in rejected],
                      "screen_cannot_check": [e["project"] for e in unscreenable],
                      "disagree_both": db}, indent=1))


if __name__ == "__main__":
    main()

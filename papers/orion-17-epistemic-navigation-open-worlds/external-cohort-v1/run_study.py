#!/usr/bin/env python3
"""ORION-17 rule-disagreement study: measure the donor-coarse outcome.

The outcome is NOT invented here. It is the campaign's own instrument,
`measure_p7_closure_retention_v1.py`, invoked through its documented CLI so no
policy logic is retranscribed:

    measure_p7.py <root> <out.json> '[{"repo_dir":..,"pkg":..}]' <n_changes>

Outcome rule, read off that instrument: `donor-coarse` is UNSOUND on a
repository iff its `false_closure_retention > 0`.

n_changes = 700, RECOVERED (not chosen) from the campaign's own
HELD_OUT_RESULT.json: tornado and sympy both saturate at commits_examined=700,
and the per-domain totals reproduce the manuscript's 2,265 changes and
1,671,821 certificate decisions exactly.

Fetch depth 800 matches the campaign's own `o17_density.py`.

Each repository is cloned, measured, and deleted before the next one, behind a
free-space guard.
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
WORK = HERE / "study_work"
N_CHANGES = 700
FETCH_DEPTH = 800
MIN_FREE_GB = 2.0


def free_gb():
    st = os.statvfs("/")
    return st.f_bavail * st.f_frsize / 1e9


def sh(a, cwd=None, t=2700):
    try:
        p = subprocess.run(a, cwd=cwd, capture_output=True, text=True, timeout=t)
        return p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired:
        return 124, "", "timeout"


def fetch(name, repo_url, sha):
    """Shallow-fetch history around the pinned SHA. Returns (dir, err)."""
    d = WORK / name.replace("/", "_")
    shutil.rmtree(d, ignore_errors=True)
    d.mkdir(parents=True, exist_ok=True)
    sh(["git", "init", "-q", str(d)])
    sh(["git", "remote", "add", "origin", repo_url], cwd=d)
    # Try the pinned SHA directly first; GitHub allows reachable-SHA fetches.
    rc, _, err = sh(["git", "fetch", "-q", "--filter=blob:none",
                     "--depth", str(FETCH_DEPTH), "origin", sha], cwd=d)
    if rc:
        rc2, _, err2 = sh(["git", "fetch", "-q", "--filter=blob:none",
                           "--depth", str(FETCH_DEPTH), "origin", "HEAD"], cwd=d)
        if rc2:
            return None, f"fetch_failed:{(err or err2).strip()[:100]}"
    rc, _, err = sh(["git", "checkout", "-q", "FETCH_HEAD" if sha=="HEAD" else sha], cwd=d)
    if rc:
        return None, "pinned_sha_not_reachable_within_depth_800"
    return d, None


def measure(name, pkg, d):
    """Run the campaign's own instrument via its CLI."""
    out = WORK / f"{name.replace('/', '_')}.result.json"
    rc, so, se = sh([sys.executable, str(HERE / "measure_p7.py"), str(WORK),
                     str(out), json.dumps([{"repo_dir": d.name, "pkg": pkg}]),
                     str(N_CHANGES)])
    if rc or not out.exists():
        return None, f"instrument_failed:{(se or so).strip()[:140]}"
    rep = json.loads(out.read_text())
    out.unlink(missing_ok=True)
    doms = rep.get("domains", [])
    if not doms or not doms[0].get("usable"):
        return None, doms[0].get("reason", "unusable") if doms else "no_domain"
    return doms[0], None


def run_one(name, repo_url, sha, pkg):
    if free_gb() < MIN_FREE_GB:
        return {"usable": False, "reason": "skipped_low_disk"}
    d, err = fetch(name, repo_url, sha)
    if err:
        shutil.rmtree(WORK / name.replace("/", "_"), ignore_errors=True)
        return {"usable": False, "reason": err}
    dom, err = measure(name, pkg, d)
    shutil.rmtree(d, ignore_errors=True)
    if err:
        return {"usable": False, "reason": err}
    donor = dom["policies"]["donor-coarse"]
    exact = dom["policies"]["exact-containment"]
    return {
        "usable": True,
        "modules": dom["modules"], "import_edges": dom["import_edges"],
        "commits_examined": dom["commits_examined"],
        "changes_used": dom["changes_used"],
        "certificate_decisions": dom["certificate_decisions"],
        "donor_preserve": donor["preserve"], "donor_reopen": donor["reopen"],
        "false_closure_retention": donor["false_closure_retention"],
        "donor_unnecessary_reopenings": donor["unnecessary_reopenings"],
        "exact_false_closure_retention": exact["false_closure_retention"],
        # THE OUTCOME, per the campaign's instrument.
        "outcome": "unsound" if donor["false_closure_retention"] > 0 else "sound",
        # Degeneracy: donor-coarse preserved nothing, i.e. it collapsed to
        # always-reopen, which cannot falsely retain and so is "sound" for
        # free. Uninformative for EVERY rule, symmetrically.
        "donor_degenerate": donor["preserve"] == 0,
    }


def main():
    targets = json.loads(Path(sys.argv[1]).read_text())
    outpath = Path(sys.argv[2])
    WORK.mkdir(parents=True, exist_ok=True)
    done = {}
    if outpath.exists():
        done = {r["project"]: r for r in json.loads(outpath.read_text())}
    results = list(done.values())
    for t in targets:
        if t["project"] in done:
            continue
        rec = dict(t)
        rec.update(run_one(t["project"], t["repo_url"], t["sha"], t["pkg"]))
        results.append(rec)
        outpath.write_text(json.dumps(results, indent=1))
        print(f"{t['project']:18s} {t.get('layout',''):5s} "
              f"{rec.get('outcome', rec.get('reason', '?')):9s} "
              f"pres={rec.get('donor_preserve')} fcr={rec.get('false_closure_retention')} "
              f"chg={rec.get('changes_used')} degen={rec.get('donor_degenerate')} "
              f"free={free_gb():.1f}GB", flush=True)
    shutil.rmtree(WORK, ignore_errors=True)


if __name__ == "__main__":
    main()

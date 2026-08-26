#!/usr/bin/env python3
"""Fail-closed R9-R11 science/manuscript audit for Q1, AB, C, D, and NQ.

This script does not rerun scientific computations. It inventories immutable branch/PR
receipts, extracts authority and terminal statements, and writes additive manuscript
audit appendices. It never promotes local harness conformance to top-tier or external
authority.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import urllib.parse
import urllib.request

REPO = "SzeChunYiu/ORION"
EXPECTED_MAIN = "926c7529e7b1a4aad18e8a8d7067c2fb293fe771"
PROTECTED_BRANCH = "codex/orion-v1-takeover-01a03f7a-20260826"
CLOSED_PROGRAMME_ISSUE = 1332
DATE = "2026-08-26"
LANES = ("Q1", "AB", "C", "D", "NQ")
OUTPUT_ROOT = Path("papers/manuscript-science-audit-r12")
CANONICAL_DIRS = {
    "Q1": Path("papers/Q-paper-01-tare-expressivity"),
    "AB": Path("papers/five-paper-top-tier-r8/AB"),
    "C": Path("papers/five-paper-top-tier-r8/C"),
    "D": Path("papers/five-paper-top-tier-r8/D"),
    "NQ": Path("papers/five-paper-top-tier-r8/NQ"),
}

AUTHORITY_WORDS = (
    "authority", "terminal", "status", "claim", "scope", "external", "journal",
    "production", "runtime", "hardware", "generalization", "novelty", "review",
    "cannot_check", "cannot check", "adverse", "null", "unsupported", "disagreement",
    "timeout", "resource exhaustion", "resource_exhaustion",
)
POSITIVE_TERMINALS = (
    "PASS", "SUPPORTED", "PROOF_RECONSTRUCTED_EQUIVALENT",
    "BOUNDED_CORROBORATION_ONLY", "EXACT", "GREEN",
)
NEGATIVE_TERMINALS = (
    "FAIL", "UNSUPPORTED", "NULL", "ADVERSE", "MISMATCH", "DISAGREEMENT",
    "TIMEOUT", "RESOURCE_EXHAUSTION", "CANNOT_CHECK", "CANNOT CHECK",
)


def api(path: str):
    url = "https://api.github.com" + path
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "ORION-R12-manuscript-science-audit",
        },
    )
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(request, timeout=90) as response:
        return json.load(response)


def api_pages(path: str):
    rows = []
    page = 1
    while True:
        sep = "&" if "?" in path else "?"
        batch = api(f"{path}{sep}per_page=100&page={page}")
        if not batch:
            break
        rows.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    return rows


def run(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        check=check,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def git(*args: str, check: bool = True) -> str:
    return run("git", *args, check=check).stdout.strip()


def changed_files(pr_number: int) -> list[str]:
    return [
        row["filename"]
        for row in api_pages(f"/repos/{REPO}/pulls/{pr_number}/files")
    ]


def revision_level(head: str, title: str) -> int | None:
    match = re.search(
        r"(?i)(?:^|[^a-z0-9])r(9|10|11)(?:[^0-9]|$)",
        f"{head} {title}",
    )
    return int(match.group(1)) if match else None


def lane_for(head: str, title: str, files: list[str]) -> str | None:
    combined = " ".join((head, title, *files)).lower()
    if "q-paper-01" in combined or re.search(r"(^|[^a-z0-9])q1([^a-z0-9]|$)", combined):
        return "Q1"
    for lane in ("AB", "C", "D", "NQ"):
        token = lane.lower()
        if any(f"/{token}/" in path.lower() for path in files):
            return lane
        if re.search(rf"(^|[-_/]){re.escape(token)}([-_/]|$)", head.lower()):
            return lane
    return None


def list_tree(ref: str) -> list[str]:
    result = run("git", "ls-tree", "-r", "--name-only", ref, check=False)
    return result.stdout.splitlines() if result.returncode == 0 else []


def show(ref: str, path: str) -> str | None:
    result = run("git", "show", f"{ref}:{path}", check=False)
    return result.stdout if result.returncode == 0 else None


def blob_sha(ref: str, path: str) -> str:
    result = run("git", "rev-parse", f"{ref}:{path}", check=False)
    return result.stdout.strip() if result.returncode == 0 else "CANNOT_CHECK"


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def scalar_receipt_rows(value, prefix: str = "") -> list[tuple[str, object]]:
    rows: list[tuple[str, object]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            path = f"{prefix}.{key}" if prefix else key
            rows.extend(scalar_receipt_rows(child, path))
    elif isinstance(value, list):
        if len(value) <= 8:
            for index, child in enumerate(value):
                rows.extend(scalar_receipt_rows(child, f"{prefix}[{index}]"))
    elif isinstance(value, (str, int, float, bool)) or value is None:
        lower = prefix.lower()
        if any(word in lower for word in AUTHORITY_WORDS) or lower.endswith(
            ("count", "cases", "failures", "mismatches")
        ):
            rows.append((prefix, value))
    return rows


def extract_json(text: str, branch: str, path: str) -> dict | None:
    try:
        value = json.loads(text)
    except json.JSONDecodeError:
        return None
    return {
        "branch": branch,
        "path": path,
        "blob_sha": blob_sha(f"origin/{branch}", path),
        "sha256": sha256_text(text),
        "rows": scalar_receipt_rows(value)[:100],
    }


def extract_markdown(text: str, branch: str, path: str) -> dict:
    rows = []
    for number, line in enumerate(text.splitlines(), 1):
        lower = line.lower()
        if any(word in lower for word in AUTHORITY_WORDS):
            rows.append((number, line.strip()))
    return {
        "branch": branch,
        "path": path,
        "blob_sha": blob_sha(f"origin/{branch}", path),
        "sha256": sha256_text(text),
        "rows": rows[:140],
    }


def relevant_paths(lane: str, ref: str) -> list[str]:
    selected = []
    for path in list_tree(ref):
        lower = path.lower()
        if lane == "Q1":
            in_lane = "q-paper-01" in lower or "/q1_" in lower
        else:
            token = lane.lower()
            in_lane = f"/{token}/" in lower or f"_{token}_" in lower
        if not in_lane:
            continue
        if not path.endswith((".json", ".md", ".txt")):
            continue
        if any(
            word in lower
            for word in (
                "result", "receipt", "claim_ledger", "manuscript", "milestone",
                "review", "adjudication", "audit", "proof", "novelty",
            )
        ):
            selected.append(path)

    def score(path: str):
        lower = path.lower()
        value = 0
        for revision in (11, 10, 9):
            if f"r{revision}" in lower:
                value += 100 + revision
        if path.endswith(".json"):
            value += 40
        if "claim_ledger" in lower:
            value += 35
        if "manuscript" in lower:
            value += 25
        if "result" in lower or "receipt" in lower:
            value += 20
        return value, path

    return sorted(selected, key=score, reverse=True)[:36]


def generic_gates(lane: str) -> list[str]:
    return [
        "Bind every surviving claim to the newest immutable R9-R11 receipt and retain contradictory, null, timeout, and resource-exhaustion controls in the claim ledger.",
        "Close any theorem-to-mechanism gap with an independent proof/replay audit; a same-code harness pass is not independent scientific validation.",
        "Run a prospectively frozen discriminator on an external or held-out subject when the current evidence is internal or synthetic.",
        "Refresh novelty against the exact final claim and obtain domain-expert review.",
        "Top-tier, journal, production, hardware, and unseen-instance authority remain `CANNOT_CHECK` until separately evidenced.",
    ]


def q1_gates() -> list[str]:
    return [
        "Freeze Q1-B2 from a proof-free source packet with a denylist covering the registered proof, Q1-A, registered solver/canonicalizer/witness/result trees, and #1448 outcomes until the new result is immutable.",
        "Use a structurally independent encoding where feasible and preserve first disagreement, timeout, resource exhaustion, the support-three out-of-scope control, and the n=2 support-one sharpness failure.",
        "Obtain external quantum/formal review of the all-size support-two theorem and the <=9 auxiliary-core interpretation.",
        "Keep auxiliary-core size separate from physical circuit/resource and runtime value; target Restore support may remain outside the core.",
        "Complete the final novelty refresh only after Q1-B2 custody is clean.",
    ]


def c_gates() -> list[str]:
    return [
        "Materialize and review the immutable R11 ASlib result plus compressed worst-fibre witnesses in-repository; preserve a null/adverse discriminator verbatim if the static optimum does not beat both registered baselines.",
        "Run the prospectively frozen, outcome-blind R12 transfer scenarios before any cross-scenario generalization statement.",
        "Study adaptive answer/refine/defer only after the static same-unit result is frozen; do not retrofit a learned-selector claim onto exhaustive static evidence.",
        "Obtain independent algorithm-selection review of aggregation, PAR10, missingness, and novelty conventions.",
        "Unseen-instance and deployment authority remain `CANNOT_CHECK`.",
    ]


def classify(json_receipts: list[dict], markdown_receipts: list[dict]) -> dict:
    text = "\n".join(
        str(value)
        for receipt in json_receipts
        for _, value in receipt["rows"]
    )
    text += "\n" + "\n".join(
        line
        for receipt in markdown_receipts
        for _, line in receipt["rows"]
    )
    upper = text.upper()
    positive = any(marker in upper for marker in POSITIVE_TERMINALS)
    negative = any(marker in upper for marker in NEGATIVE_TERMINALS)
    cannot_check = "CANNOT_CHECK" in upper or "CANNOT CHECK" in upper
    return {
        "receipt_bound_science_present": positive,
        "adverse_or_null_marker_present": negative,
        "cannot_check_present": cannot_check,
        "top_tier_sufficiency": "NOT_CLOSED",
        "external_authority": "CANNOT_CHECK",
    }


def write_lane_appendix(lane: str, data: dict) -> Path:
    destination = CANONICAL_DIRS[lane]
    if not destination.is_dir():
        destination = OUTPUT_ROOT
    path = destination / f"{lane}_RECEIPT_BOUND_MANUSCRIPT_UPDATE_R12_2026-08-26.md"
    lines = [
        f"# {lane} receipt-bound manuscript update — R12",
        "",
        "> Additive science audit. This file does not replace the canonical manuscript or claim ledger and grants no external authority.",
        "",
        "## Authority split",
        "",
        "- **Scientific result:** only the immutable receipts listed below.",
        "- **Local conformance:** checker/workflow status only.",
        "- **Top-tier sufficiency:** a separate scientific/editorial gate.",
        "- **External review, journal, production, hardware, and generalization:** `CANNOT_CHECK` unless separately evidenced.",
        "",
        "## Current classification",
        "",
    ]
    for key, value in data["classification"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.append("")

    if lane == "Q1":
        lines.extend([
            "## Receipt-supported manuscript content",
            "",
            "- Support-two sufficiency with the registered support-one sharpness control.",
            "- A common auxiliary frame/Tag union of at most nine system qubits, while target Restore support may remain outside that core.",
            "- Exact ordered anticommuting-pair count `P(n)=6n+54n(n-1)^2` and the `O(n^9)` direct checker after target-only outside-core preprocessing.",
            "- Q1-A is same-program proof reconstruction. Q1-B/#1448 is `BOUNDED_CORROBORATION_ONLY`, not a clean-room independent attack, because its source manifest exposed the authoring lane to the registered proof.",
            "- The bounded n=3 finite result may be stated with its ceiling: 14 support-one, 1 support-two, 0 support-three, with no solver/semantic-evaluator disagreement on the declared subject.",
            "",
            "**Manuscript-ready:** the theorem, exact counting law, auxiliary-core consequence, sharpness result, and bounded histogram are ready for integration with the stated independence ceiling.",
            "",
            "**Top-tier sufficiency:** not closed until Q1-B2, external quantum/formal review, final novelty, and non-inflated resource interpretation are complete.",
            "",
        ])
        gates = q1_gates()
    elif lane == "C":
        lines.extend([
            "## Receipt-supported manuscript content",
            "",
            "- Exact same-unit robust action value on the pinned public ASlib SAT12-ALL scenario.",
            "- Exhaustive evaluation of every dependency-closed static feature-step representation under one statewise virtual-best baseline.",
            "- Exact robust total excess, action-only regret, realized excess summaries, Pareto structure, and compressed worst-fibre witnesses.",
            "- The experiment is corpus-complete static evidence only; a null result is first-class, and no learned-selector, unseen-instance, or deployment claim follows.",
            "",
            "**Manuscript-ready:** the formulation, public-corpus binding, exhaustive static optimum, witness compression, and frozen R11 outcome are ready once the immutable artifact is materialized without changing its terminal.",
            "",
            "**Top-tier sufficiency:** promising but not closed; one public scenario and a static exhaustive selector do not establish transfer or deployment value.",
            "",
        ])
        gates = c_gates()
    else:
        lines.extend([
            "## Receipt-supported manuscript content",
            "",
            "Only claims explicitly represented by the newest receipts below may be integrated. The automated scan deliberately does not infer a scientific claim from a workflow pass alone.",
            "",
            "**Top-tier sufficiency:** not declared by this audit. Independent theory/mechanism review, a prospective discriminator, and final novelty review remain required unless a receipt below closes them explicitly.",
            "",
        ])
        gates = generic_gates(lane)

    lines.extend(["## Remaining evidence gate", ""])
    for index, gate in enumerate(gates, 1):
        lines.append(f"{index}. {gate}")
    lines.extend(["", "## Audited refs", ""])
    for candidate in data["candidates"]:
        if candidate["number"] is None:
            label = "branch"
        else:
            label = f"PR #{candidate['number']}"
        lines.append(
            f"- [{label}]({candidate['url']}) `{candidate['head']}` @ `{candidate['head_sha']}`"
        )
    lines.extend(["", "## Immutable evidence inventory", ""])
    for receipt in data["json_receipts"][:12]:
        lines.append(
            f"- `{receipt['branch']}:{receipt['path']}` — blob `{receipt['blob_sha']}`, SHA-256 `{receipt['sha256']}`"
        )
        for key, value in receipt["rows"][:14]:
            lines.append(f"  - `{key}` = `{value}`")
    for receipt in data["markdown_receipts"][:10]:
        lines.append(
            f"- `{receipt['branch']}:{receipt['path']}` — blob `{receipt['blob_sha']}`, SHA-256 `{receipt['sha256']}`"
        )
        for number, line in receipt["rows"][:10]:
            lines.append(f"  - L{number}: {line}")
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def main() -> None:
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    git("fetch", "origin", "+refs/heads/*:refs/remotes/origin/*")
    observed_main = git("rev-parse", "origin/main")

    branches = {
        row["name"]: row["commit"]["sha"]
        for row in api_pages(f"/repos/{REPO}/branches")
    }
    open_prs = api_pages(
        f"/repos/{REPO}/pulls?state=open&sort=updated&direction=desc"
    )
    pr_rows = []
    for pr in open_prs:
        files = changed_files(pr["number"])
        pr_rows.append({
            "number": pr["number"],
            "url": pr["html_url"],
            "title": pr["title"],
            "draft": pr["draft"],
            "head": pr["head"]["ref"],
            "head_sha": pr["head"]["sha"],
            "base": pr["base"]["ref"],
            "files": files,
            "lane": lane_for(pr["head"]["ref"], pr["title"], files),
            "revision": revision_level(pr["head"]["ref"], pr["title"]),
        })

    lane_data = {}
    open_heads = {row["head"] for row in pr_rows}
    for lane in LANES:
        candidates = [
            row for row in pr_rows
            if row["lane"] == lane and row["revision"] in (9, 10, 11)
        ]
        for branch, sha in branches.items():
            if branch in open_heads or not branch.startswith("chatgpt/"):
                continue
            revision = revision_level(branch, "")
            if revision not in (9, 10, 11):
                continue
            if lane_for(branch, "", []) != lane:
                continue
            candidates.append({
                "number": None,
                "url": f"https://github.com/{REPO}/tree/{urllib.parse.quote(branch, safe='/')}",
                "title": "branch without open PR",
                "draft": None,
                "head": branch,
                "head_sha": sha,
                "base": None,
                "files": [],
                "lane": lane,
                "revision": revision,
            })
        candidates.sort(
            key=lambda row: (row["revision"] or 0, row["number"] or 0),
            reverse=True,
        )
        candidates = candidates[:8]

        json_receipts = []
        markdown_receipts = []
        for candidate in candidates:
            ref = f"origin/{candidate['head']}"
            for path in relevant_paths(lane, ref):
                text = show(ref, path)
                if text is None:
                    continue
                if path.endswith(".json"):
                    receipt = extract_json(text, candidate["head"], path)
                    if receipt:
                        json_receipts.append(receipt)
                else:
                    markdown_receipts.append(
                        extract_markdown(text, candidate["head"], path)
                    )

        lane_data[lane] = {
            "candidates": candidates,
            "json_receipts": json_receipts,
            "markdown_receipts": markdown_receipts,
            "classification": classify(json_receipts, markdown_receipts),
        }

    generated_paths = []
    for lane in LANES:
        generated_paths.append(str(write_lane_appendix(lane, lane_data[lane])))

    report = [
        "# ORION R9-R11 science and manuscript-readiness audit",
        "",
        f"- Generated: `{DATE}`",
        f"- Coordination main: `{EXPECTED_MAIN}`",
        f"- Observed `origin/main`: `{observed_main}`",
        f"- Protected branch: `{PROTECTED_BRANCH}` — untouched",
        f"- Closed computation programme: [#{CLOSED_PROGRAMME_ISSUE}](https://github.com/{REPO}/issues/{CLOSED_PROGRAMME_ISSUE}) — not rerun",
        "",
    ]
    if observed_main != EXPECTED_MAIN:
        report.extend([
            "> **Main drift, fail closed:** observed main differs from the coordination SHA. This tranche remains additive and does not rewrite canonical identities or historical receipts.",
            "",
        ])
    report.extend([
        "## Authority model",
        "",
        "1. Scientific result authority comes from the theorem/experiment and immutable receipt.",
        "2. Local harness conformance is only a checker/workflow property.",
        "3. Top-tier sufficiency requires coherent novelty, independent scrutiny, and discriminating evidence.",
        "4. External review, journal acceptance, production/hardware value, and unseen-instance generalization remain `CANNOT_CHECK` unless separately evidenced.",
        "",
        "## Collision/ownership result",
        "",
        f"- Expanded **{len(pr_rows)}** open PRs to changed-file inventories before writing.",
        "- This branch writes uniquely named additive audit files only.",
        f"- `{PROTECTED_BRANCH}` and its ORION V1/Receipt V3/control-plane/evidence-audit ownership are excluded.",
        "- #1332 artifacts are excluded.",
        "",
        "## Open R9-R11 manuscript-lane PRs",
        "",
    ])
    for row in pr_rows:
        if row["lane"] and row["revision"] in (9, 10, 11):
            report.append(
                f"- **{row['lane']} R{row['revision']}** — [#{row['number']}]({row['url']}) "
                f"`{row['head']}` @ `{row['head_sha']}` → `{row['base']}`; "
                f"draft={row['draft']}; {len(row['files'])} changed files."
            )
    report.extend(["", "## Manuscript decisions", ""])
    decisions = {
        "Q1": "Receipt-bound theorem content is manuscript-ready with an explicit independence ceiling. Top-tier sufficiency is not closed until Q1-B2, external quantum/formal review, final novelty, and non-inflated resource interpretation are complete.",
        "AB": "Integrate only claims named by the newest immutable receipts. A local pass is not a top-tier sufficiency result; retain every null/adverse/CANNOT_CHECK marker listed in the AB appendix.",
        "C": "The exact same-unit ASlib formulation and frozen static result are manuscript-ready after artifact materialization. Top-tier sufficiency remains open pending outcome-blind transfer and independent algorithm-selection review.",
        "D": "Integrate only claims named by the newest immutable receipts. A local pass is not a top-tier sufficiency result; retain every null/adverse/CANNOT_CHECK marker listed in the D appendix.",
        "NQ": "Integrate only claims named by the newest immutable receipts. A local pass is not a top-tier sufficiency result; retain every null/adverse/CANNOT_CHECK marker listed in the NQ appendix.",
    }
    for lane in LANES:
        report.extend([
            f"### {lane}",
            "",
            decisions[lane],
            "",
            f"Classification: `{json.dumps(lane_data[lane]['classification'], sort_keys=True)}`",
            "",
        ])
    report.extend([
        "## Programme-level decision",
        "",
        "- Do not freeze ORION V1 merely because local harnesses are green; close the surviving manuscripts' theory/mechanism and prospective-discriminator gates first.",
        "- Update manuscripts now where receipts bind the science. Q1 and C already have material suitable for additive integration with strict ceilings. AB, D, and NQ remain governed by their generated evidence inventories.",
        "- Preserve all adverse, null, disagreement, timeout, resource-exhaustion, and `CANNOT_CHECK` outcomes.",
        "- Do not reopen or overwrite #1332.",
        "",
        "## Generated manuscript appendices",
        "",
    ])
    report.extend(f"- `{path}`" for path in generated_paths)
    report.append("")
    report_path = OUTPUT_ROOT / "ORION_R9_R11_MANUSCRIPT_SCIENCE_AUDIT_2026-08-26.md"
    report_path.write_text("\n".join(report), encoding="utf-8")

    manifest = {
        "schema": "ORION.ManuscriptScienceAudit.R12.v1",
        "generated": DATE,
        "repo": REPO,
        "expected_main": EXPECTED_MAIN,
        "observed_main": observed_main,
        "protected_branch": PROTECTED_BRANCH,
        "closed_programme_issue": CLOSED_PROGRAMME_ISSUE,
        "open_pr_count": len(pr_rows),
        "generated_paths": [str(report_path), *generated_paths],
        "lanes": {
            lane: {
                "candidate_refs": len(data["candidates"]),
                "json_receipts": len(data["json_receipts"]),
                "authority_markdown_receipts": len(data["markdown_receipts"]),
                "classification": data["classification"],
            }
            for lane, data in lane_data.items()
        },
        "status": "PASS" if observed_main == EXPECTED_MAIN else "MAIN_DRIFT_FAIL_CLOSED",
        "authority": {
            "open_pr_file_inventory_exact": True,
            "scientific_claims_auto_promoted": False,
            "top_tier_sufficiency_auto_promoted": False,
            "external_authority": False,
        },
    }
    payload = json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode()
    manifest["content_sha256"] = hashlib.sha256(payload).hexdigest()
    (OUTPUT_ROOT / "ORION_R9_R11_MANUSCRIPT_SCIENCE_AUDIT_2026-08-26.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

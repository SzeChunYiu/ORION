#!/usr/bin/env python3
"""Static scientific-artifact validation for P3 V7T. No pytest or repo CI."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path


LANE = Path(__file__).resolve().parent
ROOT = LANE.parents[2]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main() -> None:
    checks: list[dict] = []

    def check(name: str, passed: bool, detail: str = "") -> None:
        checks.append({"check": name, "pass": bool(passed), "detail": detail})

    protocol = json.loads((LANE / "PROTOCOL_V7T.json").read_text())
    rebind = json.loads((LANE / "PROTOCOL_MANUSCRIPT_SOURCE_REBIND_V7T_A1.json").read_text())
    result = json.loads((LANE / "RESULT_V7T.json").read_text())
    counter = json.loads((LANE / "FINITE_COUNTERMODEL_RESULT_V7T.json").read_text())
    literature = json.loads((LANE / "LITERATURE_RECEIPT_V7T.json").read_text())

    drift_path = (LANE / rebind["trigger"]["path"]).resolve()
    for rec in protocol["frozen_inputs"]:
        path = (LANE / rec["path"]).resolve()
        if path == drift_path:
            check(
                "original_manuscript_drift_preserved",
                rec["sha256"] == rebind["trigger"]["predecessor_expected_sha256"]
                and sha256(path) == rebind["trigger"]["observed_current_sha256"]
                and rec["sha256"] != sha256(path),
                str(path),
            )
            continue
        check(
            "frozen_input_" + path.name,
            path.is_file() and sha256(path) == rec["sha256"],
            str(path),
        )

    for rec in rebind["rebound_patch_sources"]:
        path = (LANE / rec["path"]).resolve()
        check("rebound_source_" + path.name, path.is_file() and sha256(path) == rec["sha256"], str(path))

    check("countermodel_two_worlds", counter["world_count"] == 2)
    check("countermodel_one_observation", counter["observed_signature_count"] == 1)
    check("countermodel_local_pass", counter["all_local_gates_true"] and counter["all_local_artifacts_fixed"])
    check("countermodel_global_nonidentification", counter["global_query_identified_set"] == [0, 1] and not counter["global_query_point_identified"])
    check("v6_smoke_2_of_3", result["evidence_integration"]["v6_native_smoke_ready"] == 2 and result["evidence_integration"]["v6_native_smoke_total"] == 3)
    check("v5_scientific_readiness_unchanged", result["evidence_integration"]["v5_scientific_comparator_readiness"] == "0/3_UNCHANGED")
    check("no_outcomes_opened", not result["evidence_integration"]["performance_scoring_performed"] and not result["evidence_integration"]["protected_or_gold_outcomes_opened"])
    check("novelty_cannot_check", result["novelty"].startswith("CANNOT_CHECK"))
    check("not_submission_ready", result["submission_readiness"] == "NOT_SUBMISSION_READY")

    record_path = (LANE / literature["direct_record"]["crossref_record_path"]).resolve()
    record = json.loads(record_path.read_text())["message"]
    check("crossref_doi", record["DOI"].lower() == "10.3390/app14114679")
    licences = {x.get("URL", "") for x in record.get("license", [])}
    check("crossref_cc_by_record", "https://creativecommons.org/licenses/by/4.0/" in licences)
    check("full_text_not_claimed", literature["direct_record"]["authority_used"] == "Crossref metadata and abstract only")

    patch = LANE / "MANUSCRIPT_INTEGRATION_V7T.patch"
    check("rebuilt_patch_hash", sha256(patch) == rebind["rebuilt_patch"]["sha256"])
    git_check = subprocess.run(
        ["git", "-C", str(ROOT / "work/orion-takeover"), "apply", "--check", str(patch)],
        capture_output=True,
        text=True,
    )
    check("manuscript_patch_applies", git_check.returncode == 0, git_check.stderr.strip())

    patched = LANE / "manuscript-patched-v7t"
    tex = "\n".join(p.read_text() for p in sorted(patched.rglob("*.tex")))
    labels = re.findall(r"\\label\{([^}]+)\}", tex)
    check("no_duplicate_labels_in_patched_files", len(labels) == len(set(labels)))
    check("authority_label_present", "thm:authority-fibre" in labels)
    check("new_citation_present", "\\cite{osman2024uncertainty}" in tex)
    check("new_bib_entry_present", "@article{osman2024uncertainty" in (patched / "bibliography.bib").read_text())
    check("patch_does_not_duplicate_v6_results", "Outcome-blind V6 comparator-native preflight" not in patch.read_text())
    check("terminal_preserved", "P3_V6_TWO_OF_THREE_NATIVE_SMOKE_READY__BERTMAP_PINNED_LOCK_API_INCOMPATIBILITY_CANNOT_CHECK__V5_SCIENTIFIC_READINESS_UNCHANGED_ZERO_OF_THREE" in (ROOT / "work/orion-takeover/papers/orion-13-global-knowledge-portrait/manuscript/sections/06-results.tex").read_text())

    receipt = {
        "schema_version": "orion.p3.authority-composition-theory.validation.v7t",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "checks": checks,
        "passed": sum(c["pass"] for c in checks),
        "total": len(checks),
        "status": "PASS" if all(c["pass"] for c in checks) else "FAIL",
    }
    (LANE / "VALIDATION_RECEIPT_V7T.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    if receipt["status"] != "PASS":
        for c in checks:
            if not c["pass"]:
                print(json.dumps(c, sort_keys=True))
        raise SystemExit(1)
    print(f"PASS {receipt['passed']}/{receipt['total']}")


if __name__ == "__main__":
    main()

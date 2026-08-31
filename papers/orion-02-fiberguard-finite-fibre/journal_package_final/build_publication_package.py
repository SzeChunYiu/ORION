#!/usr/bin/env python3
'''Deterministically build and verify the bounded anonymous TMLR package.

The script does not run upstream-data experiments or change scientific results.
It copies the canonical manuscript and ledger, creates anonymous scientific
projections of frozen result objects, reruns enclosed standard-library checks,
builds deterministic ZIP files, and binds package files with SHA-256.
'''
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile

PACKAGE = Path(__file__).resolve().parent
PAPER = PACKAGE.parent
REPO = PAPER.parents[1]
SUB = PACKAGE / "submission"
ANC = SUB / "anc"
EPOCH = (2026, 8, 31, 0, 0, 0)
SKILLS_REVISION = "0c05ac4c2c7f6a6a7d26dad22c1de1efdc186b4b"
TMLR_STYLE_REVISION = "7bf90efe3a0debbba703c05c43f3ff7e4d4a2992"

RAW = {
    "paired_route_result.json": PAPER / "extensions/r18/FIBERGUARD_PAIRED_ROUTE_R18_RECOVERY_RESULTS.json",
    "joint_route_repair_result.json": PAPER / "extensions/r19/JOINT_ROUTE_R19_RESULTS.json",
    "initial_neighbourhood_result.json": PAPER / "experiments/results/CERTIFIED_NEIGHBORHOOD_RESULT_V1.json",
    "corrected_neighbourhood_result.json": PAPER / "experiments/results/CERTIFIED_NEIGHBORHOOD_CONFORMAL_RECOVERY_RESULT_V2.json",
    "density_backoff_result.json": PAPER / "rounds/r23-density-backoff-revival/FIBERGUARD_PMLB_PROPOSAL_ORDERING_R23_RESULTS.json",
    "density_paired_comparison.json": PAPER / "rounds/r23-density-backoff-revival/R23_CONTROL_PAIRED_TEST_V1.json",
    "arm_conditional_result.json": PAPER / "rounds/r24-arm-conditional-fibres-revival/failed-executions/3550275/run_a.result.json",
    "selector_diagnostic.json": PAPER / "experiments/selective-fibre-risk-v1/SELECTOR_LIMIT_RESULT_V1.json",
}
DROP_KEYS = {
    "environment",
    "upstream",
    "implementation_sha256",
    "source_base_commit",
    "corrected_parent_receipt_sha256",
}
REPLACEMENTS = (
    ("ORION.FiberGuard", "ANON"),
    ("ORION.ORION02", "ANON"),
    ("ORION02", "ANON"),
    ("ORION-02", "ANON"),
    ("FIBERGUARD", "ANON"),
    ("FiberGuard", "AnonymizedMethod"),
    ("orion02", "anon"),
    ("orion.", "anon."),
    ("fiberguard", "anonymized_method"),
    ("R18", "STUDY_A"),
    ("R19", "STUDY_B"),
    ("R23", "STUDY_E"),
    ("R24", "STUDY_F"),
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n"


def replace_text(text: str) -> str:
    for old, new in REPLACEMENTS:
        text = text.replace(old, new)
    return text


def project(value: object) -> object:
    if isinstance(value, dict):
        return {replace_text(str(k)): project(v) for k, v in value.items() if k not in DROP_KEYS}
    if isinstance(value, list):
        return [project(v) for v in value]
    if isinstance(value, str):
        return replace_text(value)
    return value


def scrub_script(source: Path, destination: Path, extra: tuple[tuple[str, str], ...] = ()) -> None:
    text = source.read_text(encoding="utf-8")
    for old, new in extra + REPLACEMENTS:
        text = text.replace(old, new)
    destination.write_text(text, encoding="utf-8")


def run_stdout(command: list[str], cwd: Path) -> str:
    proc = subprocess.run(command, cwd=cwd, text=True, capture_output=True)
    if proc.returncode:
        print(proc.stdout)
        print(proc.stderr, file=sys.stderr)
        raise SystemExit(f"failed ({proc.returncode}): {' '.join(command)}")
    return proc.stdout


def write_zip(path: Path, base: Path, members: list[Path]) -> None:
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for member in sorted(members, key=lambda x: x.relative_to(base).as_posix()):
            info = zipfile.ZipInfo(member.relative_to(base).as_posix(), date_time=EPOCH)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, member.read_bytes())


def prepare_ancillary() -> None:
    ANC.mkdir(parents=True, exist_ok=True)
    data = ANC / "results"
    data.mkdir(parents=True, exist_ok=True)
    for name, source in RAW.items():
        value = json.loads(source.read_text(encoding="utf-8"))
        (data / name).write_text(canonical(project(value)), encoding="utf-8")

    scrub_script(
        PAPER / "experiments/fibre-diameter-floor-v1/check_fibre_diameter_floor.py",
        ANC / "check_fibre_diameter_floor.py",
    )
    scrub_script(
        PAPER / "experiments/refinement-to-certifiability-v1/check_refinement_to_certifiability.py",
        ANC / "check_refinement_to_certifiability.py",
    )
    scrub_script(
        PAPER / "extensions/r19/fiberguard_joint_route_r19_core.py",
        ANC / "joint_route_core.py",
        (("fiberguard_joint_route_r19_core", "joint_route_core"),),
    )
    scrub_script(
        PAPER / "extensions/r19/verify_fiberguard_joint_route_r19.py",
        ANC / "verify_joint_route_repair.py",
        (
            ("fiberguard_joint_route_r19_core", "joint_route_core"),
            ("fiberguard_joint_route_r19_core.py", "joint_route_core.py"),
            ("SOURCE_BASE_COMMIT = \"f34b61e0051289588eaf144a580dca7bc9b7e707\"", "SOURCE_BASE_COMMIT = \"ANONYMIZED\""),
        ),
    )
    scrub_script(
        PAPER / "rounds/r23-density-backoff-revival/verify_r23_control_paired_test.py",
        ANC / "verify_density_paired_comparison.py",
    )
    scrub_script(
        PAPER / "experiments/selective-fibre-risk-v1/analyze_selector_limit.py",
        ANC / "analyze_selector_diagnostic.py",
    )

    (ANC / "expected_fibre_diameter_floor.json").write_text(
        run_stdout([sys.executable, "check_fibre_diameter_floor.py"], ANC),
        encoding="utf-8",
    )
    (ANC / "expected_refinement_to_certifiability.json").write_text(
        run_stdout([sys.executable, "check_refinement_to_certifiability.py"], ANC),
        encoding="utf-8",
    )
    run_stdout(
        [sys.executable, "verify_joint_route_repair.py", "--output", "expected_joint_route_repair.json"],
        ANC,
    )
    (ANC / "expected_density_paired_comparison.json").write_text(
        run_stdout(
            [
                sys.executable,
                "verify_density_paired_comparison.py",
                "--results",
                "results/density_backoff_result.json",
            ],
            ANC,
        ),
        encoding="utf-8",
    )
    (ANC / "expected_selector_diagnostic.json").write_text(
        run_stdout(
            [
                sys.executable,
                "analyze_selector_diagnostic.py",
                "results/arm_conditional_result.json",
            ],
            ANC,
        ),
        encoding="utf-8",
    )


def write_rechecker() -> None:
    text = r'''#!/usr/bin/env python3
"Fail-closed checks of the claims carried by enclosed result objects."
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent / "results"


def load(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def main():
    a = load("paired_route_result.json")
    assert a["development"]["candidate_count"] == 99
    assert a["development"]["feasible_candidate_count"] == 0
    assert a["development"]["selected_route"]["metrics"]["route_change_coverage"] == 0
    assert a["terminal"] == "ANON_STUDY_A_NO_PAIRED_ROUTE_VALUE"

    b = load("joint_route_repair_result.json")
    assert b["invalid_STUDY_B_pairing_counterexample"]["original_randomized_value"] == "35"
    assert b["invalid_STUDY_B_pairing_counterexample"]["shortcut_randomized_value"] == "70"
    assert b["same_marginals_different_joint_system"]["full_pair_randomized_value"] == "0"
    assert b["same_marginals_different_joint_system"]["diagonal_pair_randomized_value"] == "50"

    n1 = load("initial_neighbourhood_result.json")
    assert n1["overall_verdict"] == "CERTIFICATE_INVALID"
    official = n1["splits"][0]
    assert official["relations"]["NBR_FULL"]["heldout_coverage"]["epsilon_5000"] == 0.20945945945945946
    assert official["relations"]["NBR_PCA10"]["heldout_coverage"]["epsilon_5000"] == 0.3310810810810811
    assert official["relations"]["NBR_FULL"]["certificate_heldout_violation_rate"] == 0.16891891891891891
    assert official["relations"]["NBR_PCA10"]["certificate_heldout_violation_rate"] == 0.18243243243243243

    n2 = load("corrected_neighbourhood_result.json")
    assert n2["overall_verdict"] == "VALID_WITHOUT_COVERAGE_OR_VALUE"
    for split in n2["splits"]:
        for rec in split["relations"].values():
            assert rec["heldout_coverage"]["epsilon_5000"] == 0.0

    e = load("density_backoff_result.json")
    assert e["coverage"]["backoff_summary"]["certified_coverage"] == 0.727272727273
    assert e["coverage"]["negative_control_summary"]["certified_coverage"] == 0.886363636364
    assert e["coverage"]["target"] == 0.95
    pair = load("density_paired_comparison.json")
    assert pair["geometry_certified"] == 32 and pair["control_certified"] == 39
    assert pair["mcnemar_exact_two_sided_p"] == 0.09228515625
    assert not pair["bootstrap"]["ci_excludes_zero"]

    f = load("arm_conditional_result.json")
    assert f["primary"]["certified_n"] == 44 and f["primary"]["n"] == 44
    assert f["primary"]["violations_strict"] == 20
    assert "per_instance_policy_arm_violation_flags" not in f

    selector = load("selector_diagnostic.json")
    assert selector["n"] == 44
    assert round(selector["selector_signal"]["pearson"], 3) == -0.144
    assert round(selector["selector_signal"]["permutation_p_two_sided"], 3) == 0.353
    print("ENCLOSED_RESULT_RECHECK_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''
    (ANC / "recheck_enclosed_results.py").write_text(text, encoding="utf-8")


def write_ancillary_docs() -> None:
    readme = '''# Anonymous reproducibility supplement

This archive supports the finite-fibre theorem/adverse paper without identifying the authors or linking to a named repository.

## Rechecks available from the enclosed files

Run, using Python 3.10 or later:

    python3 check_fibre_diameter_floor.py
    python3 check_refinement_to_certifiability.py
    python3 verify_joint_route_repair.py --output /tmp/joint.json
    python3 verify_density_paired_comparison.py --results results/density_backoff_result.json
    python3 analyze_selector_diagnostic.py results/arm_conditional_result.json
    python3 recheck_enclosed_results.py

All scripts use only the Python standard library. The expected JSON files are frozen outputs from the package build. The theorem checkers search for finite counterexamples and include planted controls. Their output corroborates transcription and implementation; the manuscript proofs carry general authority.

The result files are deterministic anonymous scientific projections of the full frozen objects: manuscript-relevant outcomes and per-dataset records are preserved, while environment, repository, commit and implementation-digest fields are withheld for double-blind review. MANIFEST.json binds every enclosed file.

## What this archive does not provide

It does not include the upstream ASlib or PMLB datasets and therefore does not rerun the original model-fitting pipelines. It rechecks the enclosed frozen outcomes, the exact paired coverage analysis, the selector diagnostic, and the analytic finite verifiers. Full provenance-bearing objects, upstream acquisition instructions and a permanent archival identifier are camera-ready actions after deanonymization.

The primary/control violation margin in the final held-out study remains CANNOT_CHECK: the full frozen object contains aggregate counts but did not serialize the per-instance policy-arm flags required for a paired comparison. No script in this archive invents those missing flags.

The supplementary verification code is distributed under Apache License 2.0; see LICENSE_CODE.txt. Manuscript licensing is governed separately by the TMLR submission terms.
'''
    (ANC / "README.md").write_text(readme, encoding="utf-8")
    shutil.copy2(REPO / "LICENSE", ANC / "LICENSE_CODE.txt")


def write_anc_manifest() -> None:
    files = {}
    for path in sorted(ANC.rglob("*")):
        if (path.is_file() and path.name != "MANIFEST.json" and not path.name.startswith("_")
                and "__pycache__" not in path.parts):
            files[path.relative_to(ANC).as_posix()] = sha(path)
    manifest = {
        "schema": "AnonymousFiniteFibreSupplement.v2",
        "generated": "2026-08-31",
        "scope": "enclosed-result rechecks and finite analytic verification",
        "full_upstream_data_rerun": False,
        "files": files,
    }
    (ANC / "MANIFEST.json").write_text(canonical(manifest), encoding="utf-8")


def verify_anonymity() -> None:
    forbidden = ("SzeChunYiu", "/Users/", "github.com/SzeChunYiu", "ORION", "FiberGuard")
    checked = [
        p for p in [SUB / "When_a_Representation_Can_Certify.tex", SUB / "references.bib", *ANC.rglob("*")]
        if p.is_file() and p.suffix.lower() not in {".pdf", ".zip", ".pyc"}
        and "__pycache__" not in p.parts
    ]
    findings = []
    for path in checked:
        text = path.read_text(encoding="utf-8", errors="replace")
        for token in forbidden:
            if token.lower() in text.lower():
                findings.append((path.relative_to(PACKAGE).as_posix(), token))
    if findings:
        raise SystemExit(f"anonymity scan failed: {findings}")


def verify_rechecks() -> None:
    commands = [
        [sys.executable, "check_fibre_diameter_floor.py"],
        [sys.executable, "check_refinement_to_certifiability.py"],
        [sys.executable, "verify_joint_route_repair.py", "--output", "_joint.tmp.json"],
        [sys.executable, "verify_density_paired_comparison.py", "--results", "results/density_backoff_result.json"],
        [sys.executable, "analyze_selector_diagnostic.py", "results/arm_conditional_result.json"],
        [sys.executable, "recheck_enclosed_results.py"],
    ]
    for command in commands:
        run_stdout(command, ANC)
    temporary = ANC / "_joint.tmp.json"
    if temporary.exists():
        temporary.unlink()


def build_archives() -> None:
    anc_members = [
        p for p in ANC.rglob("*")
        if p.is_file() and not p.name.startswith("_") and "__pycache__" not in p.parts
    ]
    write_zip(SUB / "When_a_Representation_Can_Certify_supplementary_anonymous.zip", ANC, anc_members)
    source_members = [
        SUB / name for name in (
            "When_a_Representation_Can_Certify.tex",
            "references.bib",
            "tmlr.sty",
            "tmlr.bst",
        )
    ]
    write_zip(SUB / "When_a_Representation_Can_Certify_tmlr_source.zip", SUB, source_members)


def write_package_manifest() -> None:
    shutil.copy2(PAPER / "MANUSCRIPT_V3.md", PACKAGE / "MANUSCRIPT.md")
    shutil.copy2(PAPER / "CLAIM_LEDGER_V3.md", PACKAGE / "CLAIM_LEDGER.md")
    for name in (
        "PUBLICATION_CLOSURE_V4.md",
        "HOSTILE_REVIEW_AND_CLOSURE_V4.md",
        "SKILLS_APPLIED_V4.md",
        "LITERATURE_VERIFICATION_V4.md",
        "ANONYMITY_AUDIT_V4.md",
        "VISUAL_QA_V4.md",
        "TMLR_FILING_CHECKLIST_V4.md",
        "PORTAL_METADATA_TEMPLATE.md",
    ):
        shutil.copy2(PAPER / name, PACKAGE / name)
    files = {}
    for path in sorted(PACKAGE.rglob("*")):
        if not path.is_file():
            continue
        if "__pycache__" in path.parts:
            continue
        rel = path.relative_to(PACKAGE).as_posix()
        if rel in {"PACKAGE_MANIFEST.json", "SHA256SUMS"}:
            continue
        if (path.suffix in {".aux", ".bbl", ".blg", ".log", ".out"}
                or path.name.endswith(".synctex.gz") or path.name.startswith("_")):
            continue
        files[rel] = sha(path)
    manifest = {
        "schema": "ORION.PublicationClosure.FinalJournalPackage.v2",
        "paper": "ORION-02",
        "primary_target": "Transactions on Machine Learning Research (TMLR)",
        "scientific_authority_delta": "NONE__EDITORIAL_AND_PACKAGE_CLOSURE_ONLY",
        "academic_paper_skills_revision": SKILLS_REVISION,
        "tmlr_style_revision": TMLR_STYLE_REVISION,
        "canonical_science_path": str((PAPER / "MANUSCRIPT_V3.md").relative_to(REPO)),
        "canonical_science_sha256": sha(PAPER / "MANUSCRIPT_V3.md"),
        "claim_ledger_path": str((PAPER / "CLAIM_LEDGER_V3.md").relative_to(REPO)),
        "claim_ledger_sha256": sha(PAPER / "CLAIM_LEDGER_V3.md"),
        "anonymous_supplement_is_scientific_projection": True,
        "full_upstream_data_rerun_from_supplement": False,
        "files": files,
    }
    (PACKAGE / "PACKAGE_MANIFEST.json").write_text(canonical(manifest), encoding="utf-8")
    lines = []
    for path in sorted(PACKAGE.rglob("*")):
        if not path.is_file():
            continue
        if "__pycache__" in path.parts:
            continue
        rel = path.relative_to(PACKAGE).as_posix()
        if (rel == "SHA256SUMS"
                or path.suffix in {".aux", ".bbl", ".blg", ".log", ".out"}
                or path.name.endswith(".synctex.gz") or path.name.startswith("_")):
            continue
        lines.append(f"{sha(path)}  {rel}")
    (PACKAGE / "SHA256SUMS").write_text("\n".join(lines) + "\n", encoding="utf-8")


def verify_manifest() -> None:
    manifest = json.loads((PACKAGE / "PACKAGE_MANIFEST.json").read_text(encoding="utf-8"))
    for rel, digest in manifest["files"].items():
        if sha(PACKAGE / rel) != digest:
            raise SystemExit(f"manifest mismatch: {rel}")
    for line in (PACKAGE / "SHA256SUMS").read_text(encoding="utf-8").splitlines():
        digest, rel = line.split("  ", 1)
        if sha(PACKAGE / rel) != digest:
            raise SystemExit(f"SHA256SUMS mismatch: {rel}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()
    if not args.verify_only:
        prepare_ancillary()
        write_rechecker()
        write_ancillary_docs()
        write_anc_manifest()
        verify_anonymity()
        verify_rechecks()
        build_archives()
        write_package_manifest()
    verify_anonymity()
    verify_rechecks()
    verify_manifest()
    print("ORION02_PUBLICATION_PACKAGE_VERIFIED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

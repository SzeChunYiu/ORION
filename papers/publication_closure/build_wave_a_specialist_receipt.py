#!/usr/bin/env python3
"""Build the fail-closed repository-side specialist closure receipt for Wave A.

This script never submits a paper and never invents author declarations. It
requires one target-specific package per Wave-A paper, validates package hashes
and PDF structure, and checks current content binding for manuscript trees that
were changed during this closure wave. The terminal means only that repository-
side scientific/reproduction/package work is closed for the bounded specialist
claim; listed human filing attestations remain open.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
TARGETS = ROOT / "papers/publication_closure/WAVE_A_SPECIALIST_TARGETS_V1.json"
SUBMISSIONS = ROOT / "papers/publication_closure/submissions"
TERMINAL = "GOOD_SPECIALIST_REPOSITORY_PACKAGE_READY__HUMAN_FILING_ATTESTATIONS_OPEN"
QUANTUM_REPLAY_TERMINAL = "WAVE_A_QUANTUM_DIRECT_REPLAYS_PASS__BOUNDED_AUTHORITY_ONLY"
QG_PROGRAMME_TERMINAL = (
    "ORION_QG_PROGRAMME_SCIENTIFICALLY_CLOSED__"
    "THEOREMS_REFUTATIONS_AND_BOUNDED_CANNOT_CHECKS_RECEIPTED__NOT_NOVELTY_AUTHORITY"
)
R11_TERMINAL = "Q1_R11_EXACT_O_N9_DIRECT_SOLVER_THEOREM"
LIVE_R11_RESULT = ROOT / "papers/orion-05-tare-expressivity/Q1_R11_SPARSE_DIRECT_EXECUTABLE_RESULT_V1.json"
LIVE_R11_PROTOCOL = ROOT / "papers/orion-05-tare-expressivity/Q1_R11_SPARSE_DIRECT_EXECUTABLE_PROTOCOL_V1.md"
LIVE_R11_ADDENDUM = ROOT / "papers/publication_closure/tqe/ORION-05_R11_ADDENDUM.md"

TQE_REQUIRED = [
    "main.pdf",
    "main.tex",
    "references.bib",
    "SCIENTIFIC_MASTER_CITED.md",
    "SUBMISSION_PROJECTION.md",
    "TQE_PROJECTION_REPORT.txt",
    "TQE_ABSTRACTS_V1.json",
    "QUANTUM_REPLAY_RECEIPT_V1.json",
    "quantum-replay-raw",
    "ABSTRACT_WORD_COUNT.txt",
    "SHA256SUMS",
]
PACKAGE = {
    "ORION-05": (
        "TQE",
        TQE_REQUIRED
        + [
            "Q1_R11_SPARSE_DIRECT_EXECUTABLE_RESULT_V1.json",
            "Q1_R11_SPARSE_DIRECT_EXECUTABLE_PROTOCOL_V1.md",
            "ORION-05_R11_ADDENDUM.md",
        ],
    ),
    "ORION-09": ("TQE", TQE_REQUIRED),
    "ORION-10": ("TQE", TQE_REQUIRED),
    "ORION-14": ("TMLR", ["main.pdf", "source", "REPOSITORY_FILING_PREFLIGHT_V1.json", "SHA256SUMS"]),
    "ORION-17": ("AIJ", ["main.pdf", "AIJ_MANUSCRIPT.tex", "bibliography.bib", "CHECKS.txt", "SHA256SUMS"]),
    "ORION-19": ("TMLR", ["main.pdf", "main.tex", "references.bib", "sections", "CHECKS.txt", "SHA256SUMS"]),
    "ORION-22": ("TMLR", ["main.pdf", "main.tex", "references.bib", "sections", "CHECKS.txt", "SHA256SUMS"]),
    "ORION-23": ("JAAMAS", ["main.pdf", "main.tex", "references.bib", "sections", "JAAMAS_INFORMATION_SHEET.md", "CHECKS.txt", "SHA256SUMS"]),
}

CURRENT_BINDING = {
    "ORION-19": ROOT / "papers/orion-19-structured-epistemic-learning/CONTENT_MANIFEST_V1.json",
    "ORION-22": ROOT / "papers/orion-22-adaptive-state-reasoning/CONTENT_MANIFEST_V1.json",
    "ORION-23": ROOT / "papers/orion-23-responsibility-carrying-state/CONTENT_MANIFEST_V1.json",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(["git", "-C", str(ROOT), *args], text=True).strip()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SystemExit(f"not a JSON object: {path}")
    return value


def verify_sha_manifest(base: Path) -> list[dict[str, Any]]:
    manifest = base / "SHA256SUMS"
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for raw in manifest.read_text(encoding="utf-8").splitlines():
        if not raw.strip():
            continue
        expected, name = raw.split(None, 1)
        name = name.lstrip("* ")
        if name in seen:
            raise SystemExit(f"duplicate SHA256SUMS row: {base / name}")
        seen.add(name)
        target = base / name
        if not target.is_file():
            raise SystemExit(f"missing SHA256SUMS target: {target}")
        observed = sha256(target)
        if observed != expected:
            raise SystemExit(f"SHA256 mismatch: {target}: {observed} != {expected}")
        rows.append({"path": str(target.relative_to(ROOT)), "sha256": observed, "bytes": target.stat().st_size})
    if not rows:
        raise SystemExit(f"empty SHA256SUMS: {manifest}")
    return rows


def pdf_ok(path: Path) -> bool:
    raw = path.read_bytes()
    return raw.startswith(b"%PDF-") and b"%%EOF" in raw[-8192:]


def verify_quantum_replay(paper_id: str, base: Path) -> dict[str, Any]:
    path = base / "QUANTUM_REPLAY_RECEIPT_V1.json"
    replay = load_json(path)
    if replay.get("schema") != "ORION.WaveAQuantumReplayReceipt.v1":
        raise SystemExit(f"bad quantum replay schema for {paper_id}")
    if replay.get("terminal") != QUANTUM_REPLAY_TERMINAL:
        raise SystemExit(f"quantum replay terminal not green for {paper_id}")
    if replay.get("scientific_authority_delta") != "NONE":
        raise SystemExit(f"quantum replay acquired authority for {paper_id}")
    if replay.get("novelty_authority") is not False:
        raise SystemExit(f"quantum replay acquired novelty authority for {paper_id}")

    raw = replay.get("raw_artifacts")
    if not isinstance(raw, dict):
        raise SystemExit(f"quantum replay raw artifact map missing for {paper_id}")
    raw_keys = {"q1_stdout", "r11_pair_checker_log", "pytest_log", "qg9", "qg12", "qg_programme"}
    if not raw_keys.issubset(raw):
        raise SystemExit(f"quantum replay raw artifact map incomplete for {paper_id}")
    raw_paths = {key: base / str(raw[key]) for key in raw_keys}
    for key, raw_path in raw_paths.items():
        if not raw_path.is_file():
            raise SystemExit(f"packaged raw quantum replay missing for {paper_id}: {key}")

    q1 = replay.get("orion05", {})
    qsync = replay.get("q_series_publication_sync", {})
    qg09 = replay.get("orion09", {})
    qg10 = replay.get("orion10", {})
    if sha256(raw_paths["q1_stdout"]) != q1.get("stdout_sha256"):
        raise SystemExit(f"ORION-05 raw proof-sanity digest mismatch in {paper_id} package")
    r11 = q1.get("r11", {}) if isinstance(q1, dict) else {}
    if not isinstance(r11, dict):
        raise SystemExit(f"ORION-05 R11 replay row missing in {paper_id} package")
    if sha256(raw_paths["r11_pair_checker_log"]) != r11.get("fresh_pair_replay_sha256"):
        raise SystemExit(f"ORION-05 R11 fresh pair replay digest mismatch in {paper_id} package")
    if sha256(raw_paths["pytest_log"]) != qsync.get("log_sha256"):
        raise SystemExit(f"Q-series pytest digest mismatch in {paper_id} package")
    if sha256(raw_paths["qg9"]) != qg09.get("qg9_sha256"):
        raise SystemExit(f"QG9 replay digest mismatch in {paper_id} package")
    if sha256(raw_paths["qg12"]) != qg09.get("qg12_sha256"):
        raise SystemExit(f"QG12 replay digest mismatch in {paper_id} package")
    programme_sha = sha256(raw_paths["qg_programme"])
    if programme_sha != qg09.get("programme_sha256") or programme_sha != qg10.get("programme_sha256"):
        raise SystemExit(f"QG programme replay digest mismatch in {paper_id} package")

    if paper_id == "ORION-05":
        if q1.get("independent_sanity_status") != "PASS":
            raise SystemExit("ORION-05 direct replay sanity not PASS")
        if q1.get("restore_max_delta_f3") != 2:
            raise SystemExit("ORION-05 direct replay Restore bound drifted")
        if q1.get("support2_sharp_failure_patterns") != 4 or q1.get("support3_to_8_failures") != 0:
            raise SystemExit("ORION-05 direct replay sharpness/class boundary drifted")
        if r11.get("terminal") != R11_TERMINAL or r11.get("algorithmic_theorem") is not True:
            raise SystemExit("ORION-05 R11 algorithmic replay not green")
        if r11.get("novelty_authority") is not False or r11.get("production_runtime_value") is not False:
            raise SystemExit("ORION-05 R11 replay exceeded authority")
        if r11.get("complete_n1_denominator") != 729 or r11.get("all_executable_gates") is not True:
            raise SystemExit("ORION-05 R11 replay denominator/gates drifted")
    elif paper_id == "ORION-09":
        if qg09.get("qg9_all_gates") is not True or qg09.get("qg9_intrinsic_support_number") != 1:
            raise SystemExit("ORION-09 QG9 theorem replay not green")
        if qg09.get("qg12_all_gates") is not True or qg09.get("qg12_n1") != 729 or qg09.get("qg12_n2") != 38760:
            raise SystemExit("ORION-09 SixLCU theorem replay not green")
        if qg09.get("programme_terminal") != QG_PROGRAMME_TERMINAL or qg09.get("programme_all_gates") is not True:
            raise SystemExit("ORION-09 QG programme closure replay not green")
    elif paper_id == "ORION-10":
        if qg10.get("programme_terminal") != QG_PROGRAMME_TERMINAL or qg10.get("programme_all_gates") is not True:
            raise SystemExit("ORION-10 QG programme closure replay not green")
        cannot = qg10.get("bounded_cannot_checks")
        if not isinstance(cannot, dict) or not {"qg7d", "qg11"}.issubset(cannot):
            raise SystemExit("ORION-10 replay lost bounded CANNOT_CHECK history")
    return replay


def verify_orion05_r11_package(base: Path, replay: dict[str, Any]) -> dict[str, Any]:
    packaged_result_path = base / "Q1_R11_SPARSE_DIRECT_EXECUTABLE_RESULT_V1.json"
    packaged_protocol_path = base / "Q1_R11_SPARSE_DIRECT_EXECUTABLE_PROTOCOL_V1.md"
    packaged_addendum_path = base / "ORION-05_R11_ADDENDUM.md"
    projection_path = base / "SUBMISSION_PROJECTION.md"
    projection_report_path = base / "TQE_PROJECTION_REPORT.txt"

    if sha256(packaged_result_path) != sha256(LIVE_R11_RESULT):
        raise SystemExit("ORION-05 packaged R11 result differs from live result")
    if sha256(packaged_protocol_path) != sha256(LIVE_R11_PROTOCOL):
        raise SystemExit("ORION-05 packaged R11 protocol differs from live protocol")
    if sha256(packaged_addendum_path) != sha256(LIVE_R11_ADDENDUM):
        raise SystemExit("ORION-05 packaged R11 addendum differs from live projection authority")

    result = load_json(packaged_result_path)
    if result.get("terminal") != R11_TERMINAL:
        raise SystemExit("ORION-05 packaged R11 terminal not green")
    authority = result.get("authority")
    if not isinstance(authority, dict):
        raise SystemExit("ORION-05 packaged R11 authority missing")
    if authority.get("algorithmic_theorem") is not True:
        raise SystemExit("ORION-05 packaged R11 lacks algorithmic theorem authority")
    for key in ("novelty_authority", "physical_quantum_resource_authority", "production_runtime_value", "submission_authority"):
        if authority.get(key) is not False:
            raise SystemExit(f"ORION-05 packaged R11 exceeded authority: {key}")
    if result.get("protocol_sha256") != sha256(packaged_protocol_path):
        raise SystemExit("ORION-05 packaged R11 result/protocol binding drifted")

    projection = projection_path.read_text(encoding="utf-8")
    addendum = packaged_addendum_path.read_text(encoding="utf-8").strip()
    if addendum not in projection:
        raise SystemExit("ORION-05 R11 addendum is not embedded verbatim in submission projection")
    if R11_TERMINAL not in projection or "O(n^9)" not in projection:
        raise SystemExit("ORION-05 R11 load-bearing projection tokens missing")
    report = projection_report_path.read_text(encoding="utf-8")
    if "TQE_SUBMISSION_PROJECTION=PASS" not in report or "SCIENTIFIC_EXTENSION=R11_RESULT_BOUND_ALGORITHMIC_SECTION" not in report:
        raise SystemExit("ORION-05 TQE result-bound projection report not green")
    replay_r11 = replay.get("orion05", {}).get("r11", {})
    if replay_r11.get("result_sha256") != sha256(packaged_result_path):
        raise SystemExit("ORION-05 replay and packaged R11 result digest disagree")
    return {
        "terminal": result["terminal"],
        "result_sha256": sha256(packaged_result_path),
        "protocol_sha256": sha256(packaged_protocol_path),
        "addendum_sha256": sha256(packaged_addendum_path),
        "algorithmic_theorem": True,
        "novelty_authority": False,
        "production_runtime_value": False,
        "scope": authority.get("scope"),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source-commit", required=True)
    ap.add_argument("--package-commit", default=None)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    targets = load_json(TARGETS)
    target_rows = targets.get("targets")
    if not isinstance(target_rows, dict) or set(target_rows) != set(PACKAGE):
        raise SystemExit("specialist target set does not match Wave A")

    papers: dict[str, Any] = {}
    for paper_id, (venue_dir, required) in PACKAGE.items():
        base = SUBMISSIONS / paper_id / venue_dir
        if not base.is_dir():
            raise SystemExit(f"missing package directory: {base}")
        for name in required:
            if not (base / name).exists():
                raise SystemExit(f"missing package component: {base / name}")
        pdf = base / "main.pdf"
        if not pdf_ok(pdf):
            raise SystemExit(f"invalid PDF structure: {pdf}")
        hash_rows = verify_sha_manifest(base)
        filing = target_rows[paper_id].get("human_only_before_filing")
        if not isinstance(filing, list) or not filing:
            raise SystemExit(f"human filing list missing for {paper_id}")
        row: dict[str, Any] = {
            "venue": target_rows[paper_id]["primary"],
            "article_type": target_rows[paper_id]["article_type"],
            "claim_surface": target_rows[paper_id]["claim_surface"],
            "package_dir": str(base.relative_to(ROOT)),
            "pdf_sha256": sha256(pdf),
            "pdf_bytes": pdf.stat().st_size,
            "package_hash_rows": hash_rows,
            "human_only_before_filing": filing,
            "top_tier_route": target_rows[paper_id]["optional_stronger_route"],
            "repository_terminal": TERMINAL,
            "submission_authority": False,
        }
        manifest_path = CURRENT_BINDING.get(paper_id)
        if manifest_path:
            manifest = load_json(manifest_path)
            if manifest.get("subject_commit_status") != "BOUND":
                raise SystemExit(f"current content manifest not BOUND: {paper_id}")
            if manifest.get("subject_commit_blocker") not in (None, ""):
                raise SystemExit(f"content manifest has blocker: {paper_id}")
            row["content_manifest"] = {
                "path": str(manifest_path.relative_to(ROOT)),
                "sha256": sha256(manifest_path),
                "subject_commit": manifest.get("subject_commit"),
                "status": manifest.get("subject_commit_status"),
            }
        if paper_id == "ORION-14":
            preflight = load_json(base / "REPOSITORY_FILING_PREFLIGHT_V1.json")
            if preflight.get("ok") is not True or preflight.get("failure_count") != 0:
                raise SystemExit("ORION-14 filing preflight not green")
            row["filing_preflight_terminal"] = preflight.get("terminal")
        if paper_id in {"ORION-05", "ORION-09", "ORION-10"}:
            count_text = (base / "ABSTRACT_WORD_COUNT.txt").read_text().strip()
            try:
                count = int(count_text)
            except ValueError as exc:
                raise SystemExit(f"bad abstract count for {paper_id}: {count_text}") from exc
            if not 150 <= count <= 250:
                raise SystemExit(f"TQE abstract word count outside 150..250 for {paper_id}: {count}")
            abstract_source = load_json(base / "TQE_ABSTRACTS_V1.json")
            if abstract_source.get("schema") != "ORION.TQEAbstractOverrides.v1":
                raise SystemExit(f"bad TQE abstract source schema for {paper_id}")
            report = (base / "TQE_PROJECTION_REPORT.txt").read_text(encoding="utf-8")
            if "TQE_SUBMISSION_PROJECTION=PASS" not in report:
                raise SystemExit(f"TQE projection report not green for {paper_id}")
            replay = verify_quantum_replay(paper_id, base)
            row["abstract_word_count"] = count
            row["abstract_source_sha256"] = sha256(base / "TQE_ABSTRACTS_V1.json")
            row["submission_projection_sha256"] = sha256(base / "SUBMISSION_PROJECTION.md")
            row["quantum_replay_terminal"] = replay["terminal"]
            row["quantum_replay_sha256"] = sha256(base / "QUANTUM_REPLAY_RECEIPT_V1.json")
            if paper_id == "ORION-05":
                row["r11"] = verify_orion05_r11_package(base, replay)
        papers[paper_id] = row

    receipt = {
        "schema": "ORION.WaveASpecialistClosureReceipt.v1",
        "date": "2026-08-27",
        "source_commit": args.source_commit,
        "package_commit": args.package_commit,
        "generated_from_head": git("rev-parse", "HEAD"),
        "target_manifest": str(TARGETS.relative_to(ROOT)),
        "target_manifest_sha256": sha256(TARGETS),
        "paper_count": len(papers),
        "papers": papers,
        "terminal": TERMINAL,
        "all_repository_side_specialist_packages_ready": True,
        "all_top_tier_discriminators_required_for_specialist_closure": False,
        "scientific_authority_delta_from_receipt": "NONE",
        "external_human_peer_review_claimed": False,
        "submission_authority": False,
        "boundary": "Repository-side bounded specialist objects are complete. Authorship, declarations and journal-portal filing remain human attestations; optional stronger experiments do not block these bounded packages."
    }
    out = ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(TERMINAL)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

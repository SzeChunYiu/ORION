from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[3]
PAPER = ROOT / "papers/orion-05-tare-expressivity"
PDF = PAPER / "manuscript/main.pdf"
PACKAGE_PDF = PAPER / "journal_package/manuscript.pdf"
ARCHIVE = PAPER / "journal_package/support_two_normal_form_review_2026-08-28.zip"
EXPECTED_PDF_SHA256 = "75a893f32465a8eabba8161f2368839a880b3c046f1b0edf04cc6375d46a968b"
EXPECTED_ARCHIVE_SHA256 = "8ff07f17b23f9ba96736ac67a88308c809e9837122c662e97bccf4679e5dc09c"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pdf_text() -> str:
    return "\n".join(page.extract_text() or "" for page in PdfReader(PDF).pages)


def test_exact_pdf_copies_and_geometry_are_bound() -> None:
    assert PDF.read_bytes() == PACKAGE_PDF.read_bytes()
    assert sha256(PDF) == EXPECTED_PDF_SHA256
    reader = PdfReader(PDF)
    assert len(reader.pages) == 8
    for page in reader.pages:
        assert round(float(page.mediabox.width)) == 612
        assert round(float(page.mediabox.height)) == 792
    metadata = " ".join(str(value) for value in (reader.metadata or {}).values())
    assert "Sze Chun Yiu" not in metadata
    assert "sze-chun.yiu" not in metadata.lower()
    assert "Support-Two Normal Forms for a Shared-Tag Pauli Compilation Grammar" in metadata
    assert "Anonymous authors" in metadata


def test_reader_facing_pdf_has_no_internal_code_or_transport_leakage() -> None:
    text = pdf_text()
    forbidden = {
        "project_name": r"\bORION(?:-\d+)?\b",
        "paper_codes": r"\bP\d{1,2}\b",
        "q_series": r"\bQ1\b|\bQG[A-Z0-9_-]*\b",
        "result_rounds": r"\bR6[A-Z0-9_-]*\b|\bR\d+[A-Z]*\b",
        "hypothesis_or_baseline_codes": r"\bH\d+\b|\bB\d+\b",
        "machine_state": (
            r"\b(?:round|lane|terminal|CANNOT_CHECK|READY_TO_SUBMIT|"
            r"scientifically_sound_but_target_mismatch|current_claims_not_established|"
            r"blocked_by_integrity_or_compliance)\b"
        ),
        "transport_history": (
            r"\b(?:repository|commit|workflow|CI)\b|pull request|issue #|"
            r"\b(?:git|source|development|feature|release) branch\b"
        ),
        "hashes": (
            r"\bsha(?:-?256)?\b|\b(?:hash(?:es|ed|ing)?|digest(?:s|ed|ing)?)\b|"
            r"\b[0-9a-f]{40,64}\b"
        ),
        "paths_or_filenames": r"/[A-Za-z0-9_.-]+/|\.(?:py|json|md|tex|ya?ml)\b",
        "author_identity": r"Sze Chun Yiu|sze-chun\.yiu|SzeChunYiu",
        "private_lineage": (
            r"authorized conclusion|production value|production advantage|release decisions|"
            r"donor method|donor construction|production raw cost|production internal"
        ),
        "removed_claims": (
            r"separate exact referee|complete one-qubit domain|two nonzero symplectic labels"
        ),
    }
    for label, pattern in forbidden.items():
        assert re.search(pattern, text, flags=re.IGNORECASE) is None, (label, pattern)
    assert "B(n)" not in text
    assert "R0" not in text and "R1" not in text


def test_pdf_retains_the_exact_claim_and_adverse_carriers() -> None:
    text = " ".join(pdf_text().split())
    for carrier in (
        "support-one cost 6",
        "120 attempts",
        "108 completed and 12 timed out",
        "no runtime or memory improvement is established",
        "Large language models were used",
    ):
        assert carrier in text
    compact = re.sub(r"\s+", "", text)
    assert "(XI,XI)" in compact
    assert "(IX,IY)" in compact


def test_anonymous_review_archive_is_identity_scrubbed_and_bound() -> None:
    assert sha256(ARCHIVE) == EXPECTED_ARCHIVE_SHA256
    forbidden = (
        rb"sze[ -]?chun[ .-]?yiu",
        rb"/users/",
        rb"github\.com/",
        rb"\borion(?:[-_ ]?\d+)?\b",
        rb"\bqg[-_ ]?[a-z0-9]+\b",
        rb"\b(?:cannot_check|ready_to_submit|scientifically_sound_but_target_mismatch|current_claims_not_established|blocked_by_integrity_or_compliance)\b",
        rb"\b(?:commit|pull request|issue #|workflow|continuous integration|build history)\b",
        rb"\b(?:git|source|development|feature|release) branch\b",
        rb"\b(?:pr|issue)\s*#?\d+\b",
        rb"\bsha(?:-?256)?\b",
        rb"\b(?:hash(?:es|ed|ing)?|digest(?:s|ed|ing)?)\b",
        rb"\b[0-9a-f]{40,64}\b",
        rb"\bauthorized_(?:interpretation|conclusion)\b",
        rb"\bproduction_(?:internal|raw|checks?)\b",
        rb"\b(?:donor[-_ ]owned|donor method|donor construction)\b",
        rb"\b(?:frozen|production|internal) (?:grammar|system|convention|checks?|history|release|raw cost)\b",
    )
    internal_code = rb"\b(?:P\d{1,2}|Q\d+[A-Z0-9_-]*|R\d+[A-Z0-9_-]*|H\d+[A-Z0-9_-]*|B\d+[A-Z0-9_-]*)\b"
    with zipfile.ZipFile(ARCHIVE) as archive:
        assert archive.testzip() is None
        names = set(archive.namelist())
        assert {
            "proof_sanity.py",
            "verify_sharpness.py",
            "direct_solver.py",
            "aggregate_runtime.py",
            "literature_boundary.md",
            "runtime_attempts.jsonl",
            "runtime_environment.json",
            "runtime_specification.json",
            "runtime_summary.json",
        } <= names
        for name in names:
            original = archive.read(name)
            lowered = original.lower()
            lowered_name = name.lower().encode()
            for pattern in forbidden:
                assert re.search(pattern, lowered) is None, (name, pattern)
                assert re.search(pattern, lowered_name) is None, (name, pattern)
            assert re.search(internal_code, original) is None, name


def test_anonymous_runtime_rows_regenerate_the_adverse_summary() -> None:
    with tempfile.TemporaryDirectory() as temp:
        with zipfile.ZipFile(ARCHIVE) as archive:
            archive.extractall(temp)
        subprocess.run(
            [sys.executable, "aggregate_runtime.py", "--check", "runtime_summary.json"],
            cwd=temp,
            check=True,
        )
        summary = json.loads((Path(temp) / "runtime_summary.json").read_text())
        assert summary["attempt_counts"] == {
            "completed": 108,
            "errors": 0,
            "timeouts": 12,
            "total": 120,
        }
        assert summary["three_qubit_scale"]["support_two_timeouts"] == 6
        assert summary["full_subject"]["support_two_timeouts"] == 6
        assert summary["positive_performance_rule_satisfied"] is False
        assert summary["supported_interpretation"] == (
            "no measured runtime or memory improvement; all timeout rows are retained"
        )
        assert "authorized_interpretation" not in summary

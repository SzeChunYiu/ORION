import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
VERIFY = ROOT / "papers/verify_five_theory_hardening_r2.py"
RESULT = ROOT / "papers/FIVE_THEORY_HARDENING_R2_RESULTS.json"
MANUSCRIPTS = {
    "A": ROOT / "papers/theory-A-multitag-constraint-rank/MANUSCRIPT_V2.md",
    "B": ROOT / "papers/theory-B-certificate-complexity/MANUSCRIPT_V2.md",
    "C": ROOT / "papers/theory-C-low-order-information/MANUSCRIPT_V2.md",
    "D": ROOT / "papers/theory-D-falsification-authority/MANUSCRIPT_V2.md",
    "N": ROOT / "papers/nonquantum-c5cubed-davenport/MANUSCRIPT_V2.md",
}


def test_r2_verifier_replays_exactly():
    proc = subprocess.run(
        [sys.executable, str(VERIFY)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr or proc.stdout
    observed = json.loads(proc.stdout)
    committed = json.loads(RESULT.read_text(encoding="utf-8"))
    assert observed == committed
    assert observed["all_checks"] is True
    assert observed["paper_a_b"]["all_checks"] is True
    assert observed["paper_c"]["all_checks"] is True
    assert observed["paper_d"]["least_fixed_point_disagreements"] == 0
    assert observed["nonquantum"]["exact_d4_authority"] is False
    assert observed["nonquantum"]["support23_theorem_authority"] is False


def test_r2_manuscripts_are_self_contained_and_boundary_explicit():
    for paper_id, path in MANUSCRIPTS.items():
        text = path.read_text(encoding="utf-8")
        assert "## Abstract" in text, paper_id
        assert "## 1. Introduction" in text, paper_id
        assert "## Reproducibility" in text or "Reproducibility" in text, paper_id
        assert "## Limitations" in text or "Limitations" in text, paper_id
        assert "## Publication decision record" in text, paper_id

    a = MANUSCRIPTS["A"].read_text()
    assert "zsf(H;A)" in a
    assert "mu >= (b-1)t_R" in a
    assert "kappa_R6M=2" in a

    b = MANUSCRIPTS["B"].read_text()
    assert "beta_rank-only(R6I)=5" in b
    assert "kappa_R6I=1" in b
    assert "Theta(n^(4t))" in b

    c = MANUSCRIPTS["C"].read_text()
    assert "sqrt(6/5)" in c
    assert "integer error at least `t`" in c
    assert "common padding" in c.lower()

    d = MANUSCRIPTS["D"].read_text()
    assert "Typed proof-tree" in d
    assert "cannot manufacture prospective authority" in d
    assert "support-at-least-23" in d

    n = MANUSCRIPTS["N"].read_text()
    assert "s+c_4<=24" in n
    assert "atom repetition/overlap identity" in n
    assert "D_4(C_5^3) remains 30/31" in n


def test_r2_claim_ledgers_forbid_overpromotion():
    a = (ROOT / "papers/theory-A-multitag-constraint-rank/CLAIM_LEDGER_R2.md").read_text()
    b = (ROOT / "papers/theory-B-certificate-complexity/CLAIM_LEDGER_R2.md").read_text()
    c = (ROOT / "papers/theory-C-low-order-information/CLAIM_LEDGER_R2.md").read_text()
    d = (ROOT / "papers/theory-D-falsification-authority/CLAIM_LEDGER_R2.md").read_text()
    n = (ROOT / "papers/nonquantum-c5cubed-davenport/CLAIM_LEDGER_R2.md").read_text()
    assert "OPEN; NOT CLAIMED" in a
    assert "Every local proof system" in b and "OPEN; NOT CLAIMED" in b
    assert "Common padding is minimal" in c and "OPEN; NOT CLAIMED" in c
    assert "DONOR-OWNED" in d
    assert "OPEN; TOP-TIER BLOCKER" in n
    assert "theorem_authority=false" in n


def test_recursive_release_gate_remains_honest():
    review = (ROOT / "papers/FIVE_PAPER_REVIEW_SYNTHESIS_R2_2026-08-25.md").read_text()
    assert "FIVE_PAPER_UMBRELLA_MERGE_GATE = CLOSED" in review
    assert "top-tier theory candidate" in review.lower()
    assert "exact `D_4`" in review
    packet = (ROOT / "development/five-paper-hardening-r2-2026-08-25/DEVELOPMENT_PACKET.md").read_text()
    assert "academic-paper-skills@188e83e639571c435344630ae68fdc66072650d2" in packet
    assert "stacked PR" in packet


def test_recursive_skill_figure_and_availability_contracts():
    skill = (ROOT / "papers/FIVE_PAPER_SKILL_APPLICATION_R2_2026-08-25.md").read_text()
    for token in (
        "nature-paper-card",
        "nature-citation",
        "researchwrite",
        "nature-writing",
        "nature-figure",
        "nature-reviewer",
        "nature-ref-verifier",
        "nature-data",
        "nature-polishing",
    ):
        assert token in skill
    figures = (ROOT / "papers/FIVE_PAPER_FIGURE_CONTRACTS_R2_2026-08-25.md").read_text()
    for token in ("Figure A1", "Figure B1", "Figure C1", "Figure D1", "Figure N1"):
        assert token in figures
    availability = (ROOT / "papers/FIVE_PAPER_DATA_CODE_AVAILABILITY_R2_2026-08-25.md").read_text()
    assert "No external DOI" in availability
    assert "withholds theorem authority" in availability


def test_r2_manifest_binds_every_declared_file():
    import hashlib
    manifest = json.loads(
        (ROOT / "development/five-paper-hardening-r2-2026-08-25/R2_FILE_MANIFEST.json").read_text()
    )
    assert manifest["novelty_authority"] is False
    assert manifest["venue_authority"] is False
    assert manifest["external_replication"] is False
    for item in manifest["files"]:
        payload = (ROOT / item["path"]).read_bytes()
        assert len(payload) == item["bytes"]
        assert hashlib.sha256(payload).hexdigest() == item["sha256"]

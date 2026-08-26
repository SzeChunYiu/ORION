import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MANUSCRIPTS = {
    "A": ROOT / "papers/archive/2026-08-pre-unification/theory-A-multitag-constraint-rank/MANUSCRIPT_V1.md",
    "B": ROOT / "papers/archive/2026-08-pre-unification/theory-B-certificate-complexity/MANUSCRIPT_V1.md",
    "C": ROOT / "papers/archive/2026-08-pre-unification/theory-C-low-order-information/MANUSCRIPT_V1.md",
    "D": ROOT / "papers/archive/2026-08-pre-unification/theory-D-falsification-authority/MANUSCRIPT_V1.md",
    "N": ROOT / "papers/archive/2026-08-pre-unification/nonquantum-c5cubed-davenport/MANUSCRIPT_V1.md",
}


def test_five_theory_upgrade_verifier_passes():
    proc = subprocess.run(
        [sys.executable, str(ROOT / "papers/verify_five_theory_upgrades.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr or proc.stdout
    result = json.loads(proc.stdout)
    assert result["all_checks"] is True
    assert result["paper_a"]["certificate_cone"] == "mu >= (b-1)*t_R"
    assert result["paper_b"]["tight_control"] is True
    assert result["paper_b"]["loose_control"] is True
    assert result["paper_c"]["all_checks"] is True
    assert result["paper_d"]["all_checks"] is True
    assert result["nonquantum"]["checks"]["d4_open"] is True
    assert result["nonquantum"]["checks"]["frontier_not_theorem"] is True


def test_all_five_manuscripts_are_self_contained_and_boundary_explicit():
    for paper_id, path in MANUSCRIPTS.items():
        text = path.read_text(encoding="utf-8")
        assert "## Abstract" in text, paper_id
        assert "## 1. Introduction" in text, paper_id
        assert "Limitations" in text, paper_id
        assert "Reproducibility" in text, paper_id
        assert "Publication decision record" in text, paper_id

    a = MANUSCRIPTS["A"].read_text(encoding="utf-8")
    assert "mu >= (b-1)t_R" in a
    assert "kappa_R6M=2" in a

    b = MANUSCRIPTS["B"].read_text(encoding="utf-8")
    assert "beta_rank-only(R6I)=5" in b
    assert "kappa_R6I=1" in b
    assert "no unrestricted proof-system lower bound" in b.lower()

    c = MANUSCRIPTS["C"].read_text(encoding="utf-8")
    assert "delta(S)=(-1)^(q-|S|)c" in c
    assert "padding minimality remains open" in c.lower()

    d = MANUSCRIPTS["D"].read_text(encoding="utf-8")
    assert "Auth(R)=lfp(T_R)" in d
    assert "unsupported cycles" in d.lower()

    n = MANUSCRIPTS["N"].read_text(encoding="utf-8")
    assert "D_4(C_5^3) remains unresolved" in n
    assert "theorem_authority=false" in n
    assert "TOP_TIER_GATE_NOT_MET" in n


def test_claim_ledgers_forbid_known_overpromotions():
    ledgers = {
        "A": ROOT / "papers/orion-01-certificate-realization/theory-A-CLAIM_LEDGER.md",
        "B": ROOT / "papers/orion-01-certificate-realization/theory-B-CLAIM_LEDGER.md",
        "C": ROOT / "papers/orion-02-fiberguard-finite-fibre/CLAIM_LEDGER.md",
        "D": ROOT / "papers/orion-03-typed-merge-falsification/CLAIM_LEDGER.md",
        "N": ROOT / "papers/orion-04-rooted-completion-certificates/CLAIM_LEDGER.md",
    }
    assert "OPEN; explicitly not claimed" in ledgers["A"].read_text()
    assert "no unrestricted proof lower bound" in ledgers["B"].read_text().lower()
    assert "common padding is minimal" in ledgers["C"].read_text()
    assert "DONOR-OWNED" in ledgers["D"].read_text()
    n = ledgers["N"].read_text()
    assert "N-C10" in n and "OPEN; top-tier blocker" in n
    assert "N-C11" in n and "OPEN; top-tier blocker" in n


def test_release_gate_remains_closed_until_all_five_pass_top_tier():
    review = (ROOT / "papers/archive/2026-08-pre-unification/FIVE_PAPER_REVIEW_SYNTHESIS_2026-08-24.md").read_text()
    assert "integration to `main` is blocked" in review
    assert "RIGOROUS_SPECIALIST_MANUSCRIPT__TOP_TIER_GATE_NOT_MET" in review
    assert "draft PR" in review

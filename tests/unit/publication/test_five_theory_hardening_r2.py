import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
VERIFY = ROOT / "papers/verify_five_theory_hardening_r2.py"
RESULT = ROOT / "papers/FIVE_THEORY_HARDENING_R2_RESULTS.json"
MANUSCRIPTS = {
    "A": ROOT / "papers/orion-01-certificate-realization/theory-A-MANUSCRIPT_V2.md",
    "B": ROOT / "papers/orion-01-certificate-realization/theory-B-MANUSCRIPT_V2.md",
    "C": ROOT / "papers/orion-02-fiberguard-finite-fibre/MANUSCRIPT_V2.md",
    "D": ROOT / "papers/orion-03-typed-merge-falsification/MANUSCRIPT_V2.md",
    "N": ROOT / "papers/orion-04-rooted-completion-certificates/MANUSCRIPT_V2.md",
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
    assert "support at least 23" in d

    n = MANUSCRIPTS["N"].read_text()
    assert "s+c_4<=24" in n
    assert "atom repetition/overlap identity" in n
    assert "D_4(C_5^3) remains 30/31" in n


def test_r0_namespace_unification_keeps_math_ids_and_paper_ids_distinct():
    fiberguard = MANUSCRIPTS["C"].read_text(encoding="utf-8")
    assert fiberguard.count("`P4(m)`") == 2
    assert fiberguard.count("`P4`") == 1
    assert "`ORION-14(m)`" not in fiberguard
    assert "violate `ORION-14`" not in fiberguard

    regime_history = (
        ROOT
        / "papers/orion-05-tare-expressivity/CLAIM_LEDGER_ALL_N_REGIME_HISTORY_2026-08-23.md"
    ).read_text(encoding="utf-8")
    assert "Original R6Q predicate `P1(t)` classifies donor-exactness" in regime_history
    assert "predicate `ORION-11(t)`" not in regime_history

    geometry = (
        ROOT / "papers/orion-09-compilation-regime-geometry/CLAIM_LEDGER.md"
    ).read_text(encoding="utf-8")
    for phrase in (
        "baseline P1 commits 327 errors",
        "predicate P1 transfers exactly",
        "first false positive for the R6Q predicate P1",
    ):
        assert phrase in geometry
    for false_alias in (
        "baseline ORION-11 commits 327 errors",
        "predicate ORION-11 transfers exactly",
        "R6Q predicate ORION-11",
    ):
        assert false_alias not in geometry

    forecasting = (
        ROOT / "papers/orion-10-certified-static-forecasting/CLAIM_LEDGER.md"
    ).read_text(encoding="utf-8")
    for phrase in (
        "checks, predicate P1)",
        "predicate P1(t) :=",
        "P1 <-> donor_exact",
        "first P1 false positive",
        "identity false; P1 false positive",
        "R6Q predicate origin: P1 decides",
        "P1's first false positive",
        "baseline P1 commits 327 errors",
    ):
        assert phrase in forecasting

    preservation = (
        ROOT / "papers/candidates/CROSS_PAPER_PRESERVATION_THEORY_V1.md"
    ).read_text(encoding="utf-8")
    for property_id, count in {"P0": 1, "P1": 3, "P2": 4, "P3": 14, "P4": 3}.items():
        assert preservation.count(f"`{property_id}`") == count
    for false_alias in ("`ORION-11`", "`ORION-12`", "`ORION-13`", "`ORION-14`"):
        assert false_alias not in preservation

    # These are genuine paper references. A blanket ORION-to-P rewrite would
    # make this half of the guard fail even if it repaired the properties above.
    for paper_reference in (
        "ORION-11 `REOPEN` supplies",
        "ORION-12 route/task stop supplies",
        "ORION-13 meaning projection supplies",
        "ORION-14 hard gates/protected authority supply",
        "ORION-15 fresh/protected readiness supplies",
    ):
        assert paper_reference in preservation


def test_r2_claim_ledgers_forbid_overpromotion():
    a = (ROOT / "papers/orion-01-certificate-realization/theory-A-CLAIM_LEDGER_R2.md").read_text()
    b = (ROOT / "papers/orion-01-certificate-realization/theory-B-CLAIM_LEDGER_R2.md").read_text()
    c = (ROOT / "papers/orion-02-fiberguard-finite-fibre/CLAIM_LEDGER_R2.md").read_text()
    d = (ROOT / "papers/orion-03-typed-merge-falsification/CLAIM_LEDGER_R2.md").read_text()
    n = (ROOT / "papers/orion-04-rooted-completion-certificates/CLAIM_LEDGER_R2.md").read_text()
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


CURRENT_MANIFEST = "development/five-paper-hardening-r3-2026-08-28/R3_FILE_MANIFEST.json"
SUPERSEDED_MANIFEST = "development/five-paper-hardening-r2-2026-08-25/R2_FILE_MANIFEST.json"


def test_the_superseded_r2_manifest_is_retained():
    """R2 recorded what was hardened before the audited corrections. It stays."""
    r2 = json.loads((ROOT / SUPERSEDED_MANIFEST).read_text())
    assert r2["schema"] == "ORION.FivePaperHardeningR2.Manifest.v1"
    assert len(r2["files"]) == 20
    r3 = json.loads((ROOT / CURRENT_MANIFEST).read_text())
    assert r3["supersedes"] == SUPERSEDED_MANIFEST
    assert r3["mathematics_unchanged"] is True
    # a supersession narrows or corrects; it never restores authority
    for key in ("novelty_authority", "venue_authority", "external_replication"):
        assert r3[key] is False
    # every path R2 bound is still bound; a supersession may not drop coverage
    assert {f["path"] for f in r3["files"]} == {f["path"] for f in r2["files"]}


def test_r2_manifest_binds_every_declared_file():
    """The CURRENT manifest must describe the current files, byte for byte."""
    import hashlib
    manifest = json.loads((ROOT / CURRENT_MANIFEST).read_text())
    assert manifest["novelty_authority"] is False
    assert manifest["venue_authority"] is False
    assert manifest["external_replication"] is False
    digest_payload = {key: value for key, value in manifest.items() if key != "manifest_digest"}
    assert manifest["manifest_digest"] == hashlib.sha256(
        json.dumps(digest_payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    for item in manifest["files"]:
        payload = (ROOT / item["path"]).read_bytes()
        assert len(payload) == item["bytes"]
        assert hashlib.sha256(payload).hexdigest() == item["sha256"]

import json
import subprocess
from pathlib import Path

import pytest

from orion.self_orion.phase1_terminal_receipt import (
    PHASE1_DERIVATION_RULE_ID,
    PHASE1_DERIVATION_RULE_STATEMENT,
    PHASE1_TERMINAL_RECEIPT_V1_SCHEMA,
    AnchorSubject,
    ExternalTerminalDeclaration,
    Phase1TerminalReceipt,
    TerminalCIEvidence,
    git_ancestry_probe,
    load_phase1_terminal_receipt_v1,
    phase1_terminal_receipt_v1_to_dict,
    verify_phase1_derived_subject,
    write_phase1_terminal_receipt_v1,
)
from orion.self_orion.phase2_terminal_receipts import CIEvidenceConclusion
from orion.self_orion.readiness import EvidenceStatus


REPO_ROOT = Path(__file__).resolve().parents[3]
COMMITTED_RECEIPT = REPO_ROOT / "provenance" / "phases" / "PHASE1_TERMINAL_RECEIPT_V1.json"

ANCHOR_OID = "7983401847ea2b33706aacbf6e45b6bc63a60d0d"
OTHER_OID = "6c7d2afbae96057ffa821ff538ff913e962066c8"


def _receipt(*, head_sha: str = ANCHOR_OID) -> Phase1TerminalReceipt:
    return Phase1TerminalReceipt(
        declaration=ExternalTerminalDeclaration(
            declaring_system="github.com/SzeChunYiu/ORION",
            declaring_artifact="issue/75",
            declaring_reference="issuecomment-5307421385",
            declared_terminal="PHASE_1_CORE_TECHNICALLY_CLOSED",
            declared_at="2026-08-16T12:25:27Z",
        ),
        anchor=AnchorSubject(
            repository_identity="github.com/SzeChunYiu/ORION",
            commit_oid=ANCHOR_OID,
            tree_oid="fd86b448b04e27ccd7ecc2372f1f391e6200c567",
            git_object_format="sha1",
        ),
        ci_evidence=TerminalCIEvidence(
            workflow_name="ci",
            run_id="31946971360",
            head_sha=head_sha,
            conclusion=CIEvidenceConclusion.SUCCESS,
        ),
    )


def _tamper(path: Path, mutate) -> Path:
    document = json.loads(path.read_text(encoding="utf-8"))
    mutate(document)
    path.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


# --- round trip and the committed artifact ------------------------------------


def test_receipt_round_trips_through_disk(tmp_path):
    path = tmp_path / "receipt.json"
    write_phase1_terminal_receipt_v1(_receipt(), path)
    loaded = load_phase1_terminal_receipt_v1(path)
    assert loaded.receipt == _receipt()
    rebuilt = phase1_terminal_receipt_v1_to_dict(loaded.receipt)
    assert rebuilt["receipt_hash"] == loaded.receipt_hash
    assert rebuilt["document_hash"] == loaded.document_hash
    assert rebuilt["schema"] == PHASE1_TERMINAL_RECEIPT_V1_SCHEMA


def test_committed_phase1_receipt_loads_and_binds_the_declared_terminal():
    """No-alarm case for the artifact itself: the shipped receipt must validate."""

    loaded = load_phase1_terminal_receipt_v1(COMMITTED_RECEIPT)
    receipt = loaded.receipt
    assert receipt.anchor.commit_oid == ANCHOR_OID
    assert receipt.ci_evidence.head_sha == receipt.anchor.commit_oid
    assert receipt.ci_evidence.conclusion is CIEvidenceConclusion.SUCCESS
    assert receipt.declaration.declaring_artifact == "issue/75"
    assert receipt.declaration.declaring_reference == "issuecomment-5307421385"
    assert receipt.derivation_rule_id == PHASE1_DERIVATION_RULE_ID


def test_committed_receipt_agrees_with_the_human_readable_anchor_record():
    """The two artifacts describe one commit; they must not drift apart."""

    anchor_record = json.loads(
        (REPO_ROOT / "research" / "phase2" / "PHASE1_TERMINAL_SUBJECT_ANCHOR_V1.json").read_text(
            encoding="utf-8"
        )
    )
    receipt = load_phase1_terminal_receipt_v1(COMMITTED_RECEIPT).receipt
    assert anchor_record["anchor"]["commit_oid"] == receipt.anchor.commit_oid
    assert anchor_record["anchor"]["tree_oid"] == receipt.anchor.tree_oid
    assert anchor_record["phase_1_ci_receipt"]["run_id"] == receipt.ci_evidence.run_id
    assert (
        anchor_record["phase_1_terminal_declaration"]["declaring_comment_id"]
        == 5307421385
    )


# --- a wrong or rewritten anchor must be caught -------------------------------


def test_rewritten_anchor_commit_is_rejected(tmp_path):
    path = tmp_path / "receipt.json"
    write_phase1_terminal_receipt_v1(_receipt(), path)

    def rewrite(document):
        document["receipt"]["anchor"]["commit_oid"] = OTHER_OID

    _tamper(path, rewrite)
    with pytest.raises(ValueError):
        load_phase1_terminal_receipt_v1(path)


def test_rewritten_anchor_tree_is_rejected(tmp_path):
    path = tmp_path / "receipt.json"
    write_phase1_terminal_receipt_v1(_receipt(), path)

    def rewrite(document):
        document["receipt"]["anchor"]["tree_oid"] = "0" * 40

    _tamper(path, rewrite)
    with pytest.raises(ValueError):
        load_phase1_terminal_receipt_v1(path)


def test_recomputed_hashes_do_not_launder_a_rewritten_anchor(tmp_path):
    """Rewriting the anchor *and* both hashes still fails the CI-head invariant."""

    path = tmp_path / "receipt.json"
    write_phase1_terminal_receipt_v1(_receipt(), path)
    document = json.loads(path.read_text(encoding="utf-8"))
    document["receipt"]["anchor"]["commit_oid"] = OTHER_OID

    import hashlib

    def canonical(payload):
        return hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()

    document["receipt_hash"] = canonical(document["receipt"])
    document.pop("document_hash")
    document["document_hash"] = canonical(document)
    path.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    with pytest.raises(ValueError):
        load_phase1_terminal_receipt_v1(path)


def test_ci_evidence_head_must_equal_the_anchor_commit():
    with pytest.raises(ValueError):
        _receipt(head_sha=OTHER_OID)


def test_non_success_ci_conclusion_cannot_form_a_terminal_receipt():
    with pytest.raises(ValueError):
        TerminalCIEvidence(
            workflow_name="ci",
            run_id="31946971360",
            head_sha=ANCHOR_OID,
            conclusion=CIEvidenceConclusion.FAILURE,
        )


# --- records an external decision, does not make one --------------------------


@pytest.mark.parametrize(
    "field_name",
    [
        "declaring_system",
        "declaring_artifact",
        "declaring_reference",
        "declared_terminal",
        "declared_at",
    ],
)
def test_declaration_cannot_omit_its_provenance(field_name):
    values = {
        "declaring_system": "github.com/SzeChunYiu/ORION",
        "declaring_artifact": "issue/75",
        "declaring_reference": "issuecomment-5307421385",
        "declared_terminal": "PHASE_1_CORE_TECHNICALLY_CLOSED",
        "declared_at": "2026-08-16T12:25:27Z",
    }
    values[field_name] = "   "
    with pytest.raises(ValueError):
        ExternalTerminalDeclaration(**values)


def test_receipt_cannot_smuggle_in_a_phase2_closure_subject(tmp_path):
    path = tmp_path / "receipt.json"
    write_phase1_terminal_receipt_v1(_receipt(), path)

    def widen(document):
        document["receipt"]["closure_subject"] = {"commit_oid": OTHER_OID}

    _tamper(path, widen)
    with pytest.raises(ValueError):
        load_phase1_terminal_receipt_v1(path)


def test_rule_cannot_claim_sufficiency_for_closure(tmp_path):
    path = tmp_path / "receipt.json"
    write_phase1_terminal_receipt_v1(_receipt(), path)

    def widen(document):
        document["receipt"]["derivation_rule"]["sufficient_for_phase2_closure"] = True

    _tamper(path, widen)
    with pytest.raises(ValueError):
        load_phase1_terminal_receipt_v1(path)


def test_frozen_rule_statement_cannot_be_edited(tmp_path):
    path = tmp_path / "receipt.json"
    write_phase1_terminal_receipt_v1(_receipt(), path)

    def rewrite(document):
        document["receipt"]["derivation_rule"]["statement"] = "ancestry proves closure"

    _tamper(path, rewrite)
    with pytest.raises(ValueError):
        load_phase1_terminal_receipt_v1(path)


def test_rule_statement_says_ancestry_is_not_sufficient():
    assert "not sufficient" in PHASE1_DERIVATION_RULE_STATEMENT


# --- the derivation rule: every probe outcome, including the no-alarm case ----


def test_ancestor_subject_passes():
    """No-alarm case: a correct anchor must still validate, or the check is broken shut."""

    verdict = verify_phase1_derived_subject(
        _receipt(), OTHER_OID, ancestry_probe=lambda anchor, subject: True
    )
    assert verdict.status is EvidenceStatus.PASS
    assert verdict.anchor_commit_oid == ANCHOR_OID
    assert verdict.subject_commit_oid == OTHER_OID
    assert verdict.sufficient_for_phase2_closure is False


def test_non_ancestor_subject_fails():
    verdict = verify_phase1_derived_subject(
        _receipt(), OTHER_OID, ancestry_probe=lambda anchor, subject: False
    )
    assert verdict.status is EvidenceStatus.FAIL


def test_undetermined_ancestry_is_cannot_check_not_fail():
    verdict = verify_phase1_derived_subject(
        _receipt(), OTHER_OID, ancestry_probe=lambda anchor, subject: None
    )
    assert verdict.status is EvidenceStatus.CANNOT_CHECK


def test_probe_that_raises_is_cannot_check_never_pass():
    def exploding(anchor, subject):
        raise RuntimeError("git exploded")

    verdict = verify_phase1_derived_subject(
        _receipt(), OTHER_OID, ancestry_probe=exploding
    )
    assert verdict.status is EvidenceStatus.CANNOT_CHECK


@pytest.mark.parametrize("truthy", [1, "yes", [0], object()])
def test_truthy_non_boolean_probe_result_cannot_become_pass(truthy):
    verdict = verify_phase1_derived_subject(
        _receipt(), OTHER_OID, ancestry_probe=lambda anchor, subject: truthy
    )
    assert verdict.status is EvidenceStatus.CANNOT_CHECK


def test_unusable_subject_identity_is_cannot_check():
    verdict = verify_phase1_derived_subject(
        _receipt(), "not-an-oid", ancestry_probe=lambda anchor, subject: True
    )
    assert verdict.status is EvidenceStatus.CANNOT_CHECK


# --- the git-backed probe discriminates its exit codes ------------------------


def _git(root: Path, *args: str) -> str:
    return subprocess.run(
        ("git", "-C", str(root), *args),
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    ).stdout.strip()


@pytest.fixture
def tiny_repo(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    _git(root, "init", "-q")
    _git(root, "config", "user.email", "test@example.org")
    _git(root, "config", "user.name", "test")
    (root / "a.txt").write_text("a\n", encoding="utf-8")
    _git(root, "add", "a.txt")
    _git(root, "commit", "-q", "-m", "first")
    base = _git(root, "rev-parse", "HEAD")
    (root / "b.txt").write_text("b\n", encoding="utf-8")
    _git(root, "add", "b.txt")
    _git(root, "commit", "-q", "-m", "second")
    tip = _git(root, "rev-parse", "HEAD")
    _git(root, "checkout", "-q", "-b", "side", base)
    (root / "c.txt").write_text("c\n", encoding="utf-8")
    _git(root, "add", "c.txt")
    _git(root, "commit", "-q", "-m", "side")
    side = _git(root, "rev-parse", "HEAD")
    return root, base, tip, side


def test_git_probe_reports_true_for_a_real_ancestor(tiny_repo):
    root, base, tip, _side = tiny_repo
    assert git_ancestry_probe(root)(base, tip) is True


def test_git_probe_reports_false_for_a_diverged_head(tiny_repo):
    root, _base, tip, side = tiny_repo
    assert git_ancestry_probe(root)(tip, side) is False


def test_git_probe_reports_none_for_an_absent_object(tiny_repo):
    """The shallow-clone case: a missing anchor is CANNOT_CHECK, never FAIL."""

    root, _base, tip, _side = tiny_repo
    assert git_ancestry_probe(root)("0" * 40, tip) is None


def test_git_probe_reports_none_outside_a_repository(tmp_path):
    assert git_ancestry_probe(tmp_path)(ANCHOR_OID, OTHER_OID) is None


def test_git_probe_absent_object_yields_cannot_check_end_to_end(tiny_repo):
    root, _base, tip, _side = tiny_repo
    verdict = verify_phase1_derived_subject(
        _receipt(), tip, ancestry_probe=git_ancestry_probe(root)
    )
    assert verdict.status is EvidenceStatus.CANNOT_CHECK

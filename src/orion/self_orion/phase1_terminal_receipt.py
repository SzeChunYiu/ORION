"""Machine-readable transcription of the externally declared Phase-1 terminal.

Roadmap #208 requires every phase transition to have a machine-readable,
content/lineage-bound receipt tied to an exact merged subject. Phase 1's
terminal existed only as prose in a closed GitHub issue, so every downstream
derivation check rested on a comment rather than a repository artifact.

This module supplies the missing record. Two properties are load-bearing:

1. The receipt **transcribes** a host decision; it does not make one. Every
   field of :class:`ExternalTerminalDeclaration` is required, so a receipt that
   cannot name the artifact and reference that declared the terminal cannot be
   constructed. ORION certifying its own phase closure is the failure this
   record exists to make impossible.
2. The receipt binds the Phase-1 anchor only. It carries no Phase-2 closure
   subject, because none exists until a closure run freezes one. The exact-key
   validation in :func:`load_phase1_terminal_receipt_v1` is what keeps that
   mechanical: a later edit that smuggles in a closure-subject field fails to
   load rather than quietly widening the record's meaning.

The derivation rule is stored as a rule to be re-evaluated, not as a cached
result. Ancestry is *necessary and not sufficient*: issue #76 additionally
requires every Phase-2 evidence family to share one ``subject_revision_hash``.
A ``PASS`` here means only that a subject descends from the Phase-1 anchor.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from orion.self_orion.phase2_terminal_receipts import CIEvidenceConclusion
from orion.self_orion.readiness import EvidenceStatus


PHASE1_TERMINAL_RECEIPT_V1_SCHEMA = "Phase1TerminalReceipt.v1"

PHASE1_DERIVATION_RULE_ID = "PHASE_1_DERIVED_SUBJECT"

PHASE1_DERIVATION_RULE_STATEMENT = (
    "A repository subject S is Phase-1-derived iff the receipt's anchor commit "
    "is an ancestor of S.commit_oid, evaluated at audit time. Ancestry is "
    "necessary and not sufficient for Phase-2 closure."
)

RECEIPT_DOCUMENT_KEYS = frozenset({"schema", "receipt", "receipt_hash", "document_hash"})

RECEIPT_PAYLOAD_KEYS = frozenset(
    {"declaration", "anchor", "ci_evidence", "derivation_rule"}
)

_DECLARATION_KEYS = frozenset(
    {
        "declaring_system",
        "declaring_artifact",
        "declaring_reference",
        "declared_terminal",
        "declared_at",
    }
)

_ANCHOR_KEYS = frozenset(
    {"repository_identity", "commit_oid", "tree_oid", "git_object_format"}
)

_CI_KEYS = frozenset({"workflow_name", "run_id", "head_sha", "conclusion"})

_RULE_KEYS = frozenset({"rule_id", "statement", "sufficient_for_phase2_closure"})


def _canonical_hash(payload: object) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _object(value: object, name: str) -> dict[str, object]:
    if not isinstance(value, dict):
        raise ValueError(f"{name} must be an object")
    return value


def _string(value: object, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value


def _exact_keys(value: dict[str, object], expected: frozenset[str], name: str) -> None:
    actual = set(value)
    if actual != set(expected):
        missing = sorted(set(expected) - actual)
        extra = sorted(actual - set(expected))
        raise ValueError(f"{name} keys mismatch: missing={missing} extra={extra}")


def _object_id(value: object, name: str) -> str:
    text = _string(value, name)
    lowered = text.strip()
    if lowered != text or len(lowered) not in (40, 64):
        raise ValueError(f"{name} must be a full 40- or 64-character object id")
    if any(character not in "0123456789abcdef" for character in lowered):
        raise ValueError(f"{name} must be lowercase hexadecimal")
    return lowered


def _ci_conclusion(value: object, name: str) -> CIEvidenceConclusion:
    text = _string(value, name)
    try:
        return CIEvidenceConclusion(text)
    except ValueError as exc:
        raise ValueError(f"{name} is not a known CI conclusion") from exc


@dataclass(frozen=True)
class ExternalTerminalDeclaration:
    """The host act this receipt transcribes. ORION never produces one."""

    declaring_system: str
    declaring_artifact: str
    declaring_reference: str
    declared_terminal: str
    declared_at: str

    def __post_init__(self) -> None:
        for name in sorted(_DECLARATION_KEYS):
            _string(getattr(self, name), f"declaration.{name}")


@dataclass(frozen=True)
class AnchorSubject:
    """Content/lineage identity of the merged commit the terminal was declared on."""

    repository_identity: str
    commit_oid: str
    tree_oid: str
    git_object_format: str

    def __post_init__(self) -> None:
        _string(self.repository_identity, "anchor.repository_identity")
        _string(self.git_object_format, "anchor.git_object_format")
        _object_id(self.commit_oid, "anchor.commit_oid")
        _object_id(self.tree_oid, "anchor.tree_oid")


@dataclass(frozen=True)
class TerminalCIEvidence:
    """The CI receipt the host cited when declaring the terminal."""

    workflow_name: str
    run_id: str
    head_sha: str
    conclusion: CIEvidenceConclusion

    def __post_init__(self) -> None:
        _string(self.workflow_name, "ci_evidence.workflow_name")
        _string(self.run_id, "ci_evidence.run_id")
        _object_id(self.head_sha, "ci_evidence.head_sha")
        if self.conclusion is not CIEvidenceConclusion.SUCCESS:
            raise ValueError(
                "a Phase-1 terminal receipt requires a successful CI conclusion"
            )


@dataclass(frozen=True)
class Phase1TerminalReceipt:
    """Transcribed Phase-1 terminal, bound to its anchor and CI evidence."""

    declaration: ExternalTerminalDeclaration
    anchor: AnchorSubject
    ci_evidence: TerminalCIEvidence
    derivation_rule_id: str = PHASE1_DERIVATION_RULE_ID

    def __post_init__(self) -> None:
        if self.ci_evidence.head_sha != self.anchor.commit_oid:
            raise ValueError(
                "CI evidence head does not match the anchor commit; a receipt "
                "may not cite a run that executed on a different subject"
            )
        if self.derivation_rule_id != PHASE1_DERIVATION_RULE_ID:
            raise ValueError("unsupported Phase-1 derivation rule id")


def phase1_terminal_receipt_payload(
    receipt: Phase1TerminalReceipt,
) -> dict[str, object]:
    return {
        "declaration": {
            "declaring_system": receipt.declaration.declaring_system,
            "declaring_artifact": receipt.declaration.declaring_artifact,
            "declaring_reference": receipt.declaration.declaring_reference,
            "declared_terminal": receipt.declaration.declared_terminal,
            "declared_at": receipt.declaration.declared_at,
        },
        "anchor": {
            "repository_identity": receipt.anchor.repository_identity,
            "commit_oid": receipt.anchor.commit_oid,
            "tree_oid": receipt.anchor.tree_oid,
            "git_object_format": receipt.anchor.git_object_format,
        },
        "ci_evidence": {
            "workflow_name": receipt.ci_evidence.workflow_name,
            "run_id": receipt.ci_evidence.run_id,
            "head_sha": receipt.ci_evidence.head_sha,
            "conclusion": receipt.ci_evidence.conclusion.value,
        },
        "derivation_rule": {
            "rule_id": receipt.derivation_rule_id,
            "statement": PHASE1_DERIVATION_RULE_STATEMENT,
            "sufficient_for_phase2_closure": False,
        },
    }


def phase1_terminal_receipt_v1_to_dict(
    receipt: Phase1TerminalReceipt,
) -> dict[str, object]:
    payload = phase1_terminal_receipt_payload(receipt)
    document: dict[str, object] = {
        "schema": PHASE1_TERMINAL_RECEIPT_V1_SCHEMA,
        "receipt_hash": _canonical_hash(payload),
        "receipt": payload,
    }
    document["document_hash"] = _canonical_hash(document)
    return document


def write_phase1_terminal_receipt_v1(
    receipt: Phase1TerminalReceipt,
    path: str | Path,
) -> None:
    Path(path).write_text(
        json.dumps(phase1_terminal_receipt_v1_to_dict(receipt), indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )


@dataclass(frozen=True)
class LoadedPhase1TerminalReceiptV1:
    receipt: Phase1TerminalReceipt
    receipt_hash: str
    document_hash: str


def load_phase1_terminal_receipt_v1(
    path: str | Path,
) -> LoadedPhase1TerminalReceiptV1:
    try:
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"unable to load Phase-1 terminal receipt: {exc}") from exc

    document = _object(raw, "Phase-1 terminal receipt document")
    _exact_keys(document, RECEIPT_DOCUMENT_KEYS, "Phase-1 terminal receipt document")
    if document.get("schema") != PHASE1_TERMINAL_RECEIPT_V1_SCHEMA:
        raise ValueError("unsupported Phase-1 terminal receipt schema")

    claimed_document_hash = _string(document.get("document_hash"), "document_hash")
    without_document_hash = {
        key: value for key, value in document.items() if key != "document_hash"
    }
    if _canonical_hash(without_document_hash) != claimed_document_hash:
        raise ValueError("Phase-1 terminal receipt document hash mismatch")

    payload = _object(document.get("receipt"), "receipt")
    _exact_keys(payload, RECEIPT_PAYLOAD_KEYS, "receipt")

    claimed_receipt_hash = _string(document.get("receipt_hash"), "receipt_hash")
    if _canonical_hash(payload) != claimed_receipt_hash:
        raise ValueError("Phase-1 terminal receipt payload hash mismatch")

    declaration_raw = _object(payload.get("declaration"), "receipt.declaration")
    _exact_keys(declaration_raw, _DECLARATION_KEYS, "receipt.declaration")
    anchor_raw = _object(payload.get("anchor"), "receipt.anchor")
    _exact_keys(anchor_raw, _ANCHOR_KEYS, "receipt.anchor")
    ci_raw = _object(payload.get("ci_evidence"), "receipt.ci_evidence")
    _exact_keys(ci_raw, _CI_KEYS, "receipt.ci_evidence")
    rule_raw = _object(payload.get("derivation_rule"), "receipt.derivation_rule")
    _exact_keys(rule_raw, _RULE_KEYS, "receipt.derivation_rule")

    if rule_raw.get("sufficient_for_phase2_closure") is not False:
        raise ValueError(
            "receipt.derivation_rule.sufficient_for_phase2_closure must be false"
        )
    if rule_raw.get("statement") != PHASE1_DERIVATION_RULE_STATEMENT:
        raise ValueError("receipt.derivation_rule.statement is not the frozen rule")

    receipt = Phase1TerminalReceipt(
        declaration=ExternalTerminalDeclaration(
            declaring_system=_string(
                declaration_raw.get("declaring_system"),
                "receipt.declaration.declaring_system",
            ),
            declaring_artifact=_string(
                declaration_raw.get("declaring_artifact"),
                "receipt.declaration.declaring_artifact",
            ),
            declaring_reference=_string(
                declaration_raw.get("declaring_reference"),
                "receipt.declaration.declaring_reference",
            ),
            declared_terminal=_string(
                declaration_raw.get("declared_terminal"),
                "receipt.declaration.declared_terminal",
            ),
            declared_at=_string(
                declaration_raw.get("declared_at"), "receipt.declaration.declared_at"
            ),
        ),
        anchor=AnchorSubject(
            repository_identity=_string(
                anchor_raw.get("repository_identity"),
                "receipt.anchor.repository_identity",
            ),
            commit_oid=_object_id(
                anchor_raw.get("commit_oid"), "receipt.anchor.commit_oid"
            ),
            tree_oid=_object_id(anchor_raw.get("tree_oid"), "receipt.anchor.tree_oid"),
            git_object_format=_string(
                anchor_raw.get("git_object_format"), "receipt.anchor.git_object_format"
            ),
        ),
        ci_evidence=TerminalCIEvidence(
            workflow_name=_string(
                ci_raw.get("workflow_name"), "receipt.ci_evidence.workflow_name"
            ),
            run_id=_string(ci_raw.get("run_id"), "receipt.ci_evidence.run_id"),
            head_sha=_object_id(
                ci_raw.get("head_sha"), "receipt.ci_evidence.head_sha"
            ),
            conclusion=_ci_conclusion(
                ci_raw.get("conclusion"), "receipt.ci_evidence.conclusion"
            ),
        ),
        derivation_rule_id=_string(rule_raw.get("rule_id"), "receipt.derivation_rule.rule_id"),
    )

    rebuilt = phase1_terminal_receipt_v1_to_dict(receipt)
    if rebuilt["receipt_hash"] != claimed_receipt_hash:
        raise ValueError("Phase-1 terminal receipt semantic hash mismatch")
    if rebuilt["document_hash"] != claimed_document_hash:
        raise ValueError("Phase-1 terminal receipt semantic document mismatch")

    return LoadedPhase1TerminalReceiptV1(
        receipt=receipt,
        receipt_hash=claimed_receipt_hash,
        document_hash=claimed_document_hash,
    )


@dataclass(frozen=True)
class Phase1DerivationVerdict:
    """Outcome of the derivation rule for one candidate subject.

    ``PASS`` asserts exactly one thing: the subject descends from the Phase-1
    anchor. It is not Phase-2 closure, it does not bind a closure subject, and
    it grants no authority. ``CANNOT_CHECK`` is returned whenever ancestry could
    not be established either way — an absent object in a shallow clone, a git
    error, or a probe that raised. A failure to check never becomes a pass.
    """

    status: EvidenceStatus
    anchor_commit_oid: str
    subject_commit_oid: str
    detail: str
    sufficient_for_phase2_closure: bool = field(default=False, init=False)


AncestryProbe = Callable[[str, str], "bool | None"]


def verify_phase1_derived_subject(
    receipt: Phase1TerminalReceipt,
    subject_commit_oid: str,
    *,
    ancestry_probe: AncestryProbe,
) -> Phase1DerivationVerdict:
    """Re-evaluate the derivation rule for ``subject_commit_oid``.

    The rule is re-evaluated on every call by design: a history rewrite or a
    subject taken from a branch that does not contain the anchor must invalidate
    a previously true result.
    """

    anchor = receipt.anchor.commit_oid
    try:
        subject = _object_id(subject_commit_oid, "subject_commit_oid")
    except ValueError as exc:
        return Phase1DerivationVerdict(
            status=EvidenceStatus.CANNOT_CHECK,
            anchor_commit_oid=anchor,
            subject_commit_oid=str(subject_commit_oid),
            detail=f"subject identity unusable: {exc}",
        )

    try:
        outcome = ancestry_probe(anchor, subject)
    except Exception as exc:  # any probe failure is CANNOT_CHECK, never a pass
        return Phase1DerivationVerdict(
            status=EvidenceStatus.CANNOT_CHECK,
            anchor_commit_oid=anchor,
            subject_commit_oid=subject,
            detail=f"ancestry probe raised: {exc!r}",
        )

    if outcome is True:
        return Phase1DerivationVerdict(
            status=EvidenceStatus.PASS,
            anchor_commit_oid=anchor,
            subject_commit_oid=subject,
            detail="subject descends from the Phase-1 anchor; ancestry is not sufficient for closure",
        )
    if outcome is False:
        return Phase1DerivationVerdict(
            status=EvidenceStatus.FAIL,
            anchor_commit_oid=anchor,
            subject_commit_oid=subject,
            detail="subject does not descend from the Phase-1 anchor",
        )
    return Phase1DerivationVerdict(
        status=EvidenceStatus.CANNOT_CHECK,
        anchor_commit_oid=anchor,
        subject_commit_oid=subject,
        detail="ancestry could not be established; the probe reported no verdict",
    )


def _git_exit_code(root: Path, *args: str) -> int:
    try:
        completed = subprocess.run(
            ("git", "-C", str(root), *args),
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except OSError:
        return -1
    return completed.returncode


def git_ancestry_probe(repository_root: str | Path) -> AncestryProbe:
    """Ancestry probe backed by ``git merge-base --is-ancestor``.

    Exit codes are discriminated explicitly: ``0`` is ancestor, ``1`` is not
    ancestor, and anything else — a bad object, a corrupt or absent repository —
    yields ``None`` so the caller reports ``CANNOT_CHECK``. Both object ids are
    confirmed present first, because a shallow clone that lacks the anchor would
    otherwise report a false negative.
    """

    root = Path(repository_root)

    def probe(anchor_commit_oid: str, subject_commit_oid: str) -> bool | None:
        for oid in (anchor_commit_oid, subject_commit_oid):
            if _git_exit_code(root, "cat-file", "-e", f"{oid}^{{commit}}") != 0:
                return None
        code = _git_exit_code(root, "merge-base", "--is-ancestor", anchor_commit_oid, subject_commit_oid)
        if code == 0:
            return True
        if code == 1:
            return False
        return None

    return probe


__all__ = [
    "AncestryProbe",
    "AnchorSubject",
    "ExternalTerminalDeclaration",
    "LoadedPhase1TerminalReceiptV1",
    "PHASE1_DERIVATION_RULE_ID",
    "PHASE1_DERIVATION_RULE_STATEMENT",
    "PHASE1_TERMINAL_RECEIPT_V1_SCHEMA",
    "Phase1DerivationVerdict",
    "Phase1TerminalReceipt",
    "RECEIPT_DOCUMENT_KEYS",
    "RECEIPT_PAYLOAD_KEYS",
    "TerminalCIEvidence",
    "git_ancestry_probe",
    "load_phase1_terminal_receipt_v1",
    "phase1_terminal_receipt_payload",
    "phase1_terminal_receipt_v1_to_dict",
    "verify_phase1_derived_subject",
    "write_phase1_terminal_receipt_v1",
]

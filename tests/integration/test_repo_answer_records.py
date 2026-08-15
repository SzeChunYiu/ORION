from __future__ import annotations

from pathlib import Path

from orion.kernel import AnswerAuthority, grade_and_apply
from orion.kernel.evidence import EvidenceStatus, resolve_evidence_refs
from orion.mechanics.answers import audit_answer_application, load_answer_records
from orion.mechanics.program import current_program_cells, observe_mechanics_program

REPO_ROOT = Path(__file__).resolve().parents[2]
ANSWERS_ROOT = REPO_ROOT / "research" / "development" / "mechanic-answer-loop" / "answers"
RAKL_ROOT = REPO_ROOT.parent / "RAKL"


def _evidence_roots() -> dict[str, Path]:
    roots = {"orion": REPO_ROOT}
    if (RAKL_ROOT / ".git").exists():
        roots["rakl"] = RAKL_ROOT
    return roots


def test_committed_answers_never_close_a_question_by_themselves():
    """The anti-laundering invariant, bound to CI on the real answer ledger.

    Every record in the repository is a machine-authored proposal. Applying all
    of them must leave `open_question_count` exactly where it was: content may
    land, but authority may not, because no independently laned discriminating
    check has judged them. If this ever drops, the loop has found a way to
    close its own audit and the result of every prior run is void.
    """

    records = load_answer_records(ANSWERS_ROOT)
    assert records, "the answer ledger exists and is non-empty"

    cells = current_program_cells()
    before = observe_mechanics_program(cells).open_question_count
    result = grade_and_apply(cells, records, evidence_roots=_evidence_roots())
    after = observe_mechanics_program(result.cells).open_question_count

    assert after == before
    assert result.verified_record_ids == ()
    assert audit_answer_application(before, after, result.report) == ()


def test_committed_answers_target_live_mechanics():
    """A record whose mechanic no longer exists is a stale ledger entry."""

    records = load_answer_records(ANSWERS_ROOT)
    known = {cell.mechanic_id for cell in current_program_cells()}
    orphans = sorted({item.mechanic_id for item in records} - known)
    assert not orphans, f"answer records target mechanics that no longer exist: {orphans}"


def test_every_committed_citation_resolves_where_its_root_is_available():
    """Citations must point at real artifacts, and say so with a pinned anchor.

    Schemes whose root is absent in this environment resolve to UNKNOWN_SCHEME;
    that is a missing root, not a bad citation, so it is reported rather than
    silently accepted or silently failed.
    """

    records = load_answer_records(ANSWERS_ROOT)
    roots = _evidence_roots()
    refs = tuple(dict.fromkeys(ref for item in records for ref in item.evidence_refs))
    resolutions = resolve_evidence_refs(refs, roots)

    unreachable = [
        item.ref for item in resolutions if item.status is EvidenceStatus.UNKNOWN_SCHEME
    ]
    broken = [
        (item.ref, item.status.value)
        for item in resolutions
        if not item.resolved and item.status is not EvidenceStatus.UNKNOWN_SCHEME
    ]

    assert not broken, f"citations that could be checked and failed: {broken}"
    if unreachable:
        # CANNOT_CHECK, stated rather than rounded to a pass.
        assert all(ref.split(":", 1)[0] not in roots for ref in unreachable)


def test_committed_answers_reach_evidence_bound_when_roots_are_available():
    """With every root present, the ledger should be fully evidence-bound.

    This is the positive control for the gate: it proves the refusals in the
    test above come from missing verification, not from a resolver that refuses
    everything.
    """

    roots = _evidence_roots()
    if "rakl" not in roots:
        return  # provenance root absent in this environment

    records = load_answer_records(ANSWERS_ROOT)
    result = grade_and_apply(
        current_program_cells(), records, evidence_roots=roots
    )
    authorities = {item.authority for item in result.gradings}
    assert authorities == {AnswerAuthority.EVIDENCE_BOUND}
    assert not [item for grading in result.gradings for item in grading.evidence if not item.resolved]

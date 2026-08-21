"""P10's shipped binding, measured against the files in this checkout.

The finding is one pair of verdicts:
``test_the_shipped_binding_is_clean_and_its_membership_is_open``. Everything else
here is a ratchet on one of the numbers that pair rests on, so that closing the
gap reds these tests and widening it reds them harder.

Nothing in this file edits ``papers/``. The lane is content-bound, and an audit
that had to modify its subject to measure it would be reporting on a different
artifact.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from orion.programme.content_binding_coverage import (
    PaperBindingState,
    assess_paper,
    inspect_paper,
)
from orion.programme.manifest_membership import (
    ManifestMembershipNotClosed,
    assess_drift,
    assess_membership,
    audit_outcome,
    audit_report,
    require_closed_membership,
)
from orion.programme.records import Outcome
from orion.study.p10 import publication_binding as shipped
from orion.study.p10.membership_audit import audit_p10_publication_binding

REPO_ROOT = Path(__file__).resolve().parents[4]

#: Files inside the manifest's own declared scope that no gate can observe. Named
#: rather than counted, because the count alone would let one be swapped for
#: another. The first is the runner ``REPRODUCE_LOCAL_CLOSURE.sh`` executes and
#: whose committed output the manifest *does* bind; the last two are the toolchain
#: pin and the native shim behind P10's eight Lean acceptance receipts.
LOAD_BEARING_UNENROLLED = (
    "papers/orion-learning-machine/experiments/phase1_mechanic_composition/run_v2.py",
    "papers/orion-learning-machine/experiments/phase0_solver_ecology/run.py",
    "papers/orion-learning-machine/experiments/phase2_real_source/run_phase2a.py",
    "papers/orion-learning-machine/VERIFY_LOCAL_CLOSURE_V2.sh",
    "papers/paper-xx-content-bound-math-evaluation/benchmark/corpus/"
    "mathlib4_e72c1e277f31/lean-toolchain",
    "papers/paper-xx-content-bound-math-evaluation/benchmark/native/lean_readlink_self.c",
)

#: Measured 2026-08-21. A ratchet, not a target: enrolling a file may only lower
#: it, and every drop should come with the manifest regeneration that caused it.
UNENROLLED_CEILING = 20


@pytest.fixture(scope="module")
def audit():
    return shipped.audit_p10_publication(REPO_ROOT)


def test_the_shipped_binding_is_clean_and_its_membership_is_open(audit) -> None:
    """The finding, in two verdicts on one artifact.

    Drift ``PASS`` is not disputed: 551 enrolled files, none changed, and the
    shipped verifier really does red on the first byte of any of them. Membership
    ``FAIL`` says the 551 was chosen by ``included_files()`` inside the lane the
    manifest protects, and that twenty files inside that same declared scope are
    named by no digest a gate opens.
    """

    assert assess_drift(audit).outcome is Outcome.PASS
    assert assess_membership(audit).outcome is Outcome.FAIL
    assert audit_outcome(audit) is Outcome.FAIL
    assert audit_outcome(audit).blocks

    with pytest.raises(ManifestMembershipNotClosed, match="named by no enforced binding"):
        require_closed_membership(audit)


def test_the_load_bearing_files_are_the_unenrolled_ones(audit) -> None:
    unenrolled = {path.relative_to(REPO_ROOT).as_posix() for path in audit.unenrolled}
    assert set(LOAD_BEARING_UNENROLLED) <= unenrolled
    assert len(audit.unenrolled) <= UNENROLLED_CEILING


def test_every_experiment_driver_in_the_lane_is_unenrolled(audit) -> None:
    """The producers are outside the binding; the results they produced are inside.

    ``results/`` is one of the generator's four roots and ``experiments/`` is not,
    so the manifest pins every committed number and none of the code that made
    them.
    """

    unenrolled = {path.relative_to(REPO_ROOT).as_posix() for path in audit.unenrolled}
    experiments = REPO_ROOT / shipped.LANE / "experiments"
    drivers = {
        path.relative_to(REPO_ROOT).as_posix()
        for path in experiments.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    }
    assert drivers, "the experiments directory is empty; this test has lost its subject"
    assert drivers <= unenrolled

    enrolled = {path.relative_to(REPO_ROOT).as_posix() for path in audit.enrolled}
    results = {
        path.relative_to(REPO_ROOT).as_posix()
        for path in (REPO_ROOT / shipped.LANE / "results").iterdir()
        if path.is_file()
    }
    assert results <= enrolled


def test_the_historical_script_manifest_is_dereferenced_by_nothing_and_says_so(
    audit,
) -> None:
    """A receipt is not a check, and the proof is that it has already drifted.

    ``SCRIPT_MANIFEST_SHA256.txt`` names twelve of the twenty unenrolled files.
    If anything hashed the paths it names, ten disagreements could not coexist
    with a green suite.
    """

    check = next(item for item in audit.checks if item.binding_id == shipped.SCRIPT_MANIFEST)
    assert check.enforced is False
    assert check.named == 36
    assert len(check.drifted) >= 10
    assert len(audit.stale_only) == 12
    assert len(audit.unenforced_drift) == len(check.drifted)
    # And none of it is scored against the guard that does run.
    assert audit.enforced_violations == 0


def test_the_overlay_supersedes_five_paths_that_had_not_changed() -> None:
    """Only four of the overlay's nine paths are content it alone binds.

    ``VERIFY_LOCAL_CLOSURE_V2.sh`` skips five legacy sha256 rows as superseded and
    re-checks those paths by Git blob id. All five still match the sha256 the
    legacy manifest records, so the substitution pins the same bytes twice under
    two algorithms; the overlay's real contribution is the four additive paths.
    """

    supersession = shipped.overlay_supersession(REPO_ROOT)
    assert supersession == {
        "overlay_paths": 9,
        "substitutions": 5,
        "additive": 4,
        "substitutions_whose_legacy_digest_still_matches": 5,
    }


def test_the_overlay_verifies_by_recomputed_git_blob_identity(audit) -> None:
    """The audit must not need ``git`` to check a Git-addressed binding."""

    check = next(item for item in audit.checks if item.binding_id == shipped.OVERLAY)
    assert check.enforced is True
    assert check.named == 9
    assert check.drifted == () and check.missing == ()


def test_the_committed_manifest_is_what_the_shipped_generator_derives() -> None:
    """Point the instrument at the shipped artifact, not at a transcription.

    If these disagree, the manifest was hand-edited or the generator changed
    without a regeneration, and every other number here describes the wrong
    object.
    """

    derived = shipped.shipped_generator_enrolment(REPO_ROOT)
    committed = shipped.committed_publication_paths(REPO_ROOT)
    assert derived == committed


def test_the_declared_scope_can_never_be_narrower_than_the_generator_enrols() -> None:
    """The ratchet on ``SCOPE_ROOTS``.

    A denominator transcribed from a generator can drift away from it. Adding a
    root there without adding it here would shrink the scope silently, which is
    the failure this module exists to report, one level up.

    Two enrolled files are legitimately outside the roots: the generator reaches
    into two other papers by name. Reaching *out* is extra coverage, never a hole,
    so they are pinned by name here rather than folded into the scope --- and a
    third one appearing means a new root that the scope has not been told about.
    """

    scope = shipped.declared_scope(REPO_ROOT).paths
    outside = {
        path.relative_to(REPO_ROOT).as_posix()
        for path in shipped.shipped_generator_enrolment(REPO_ROOT) - scope
    }
    assert outside == {
        "papers/paper-08-epistemic-authority-autonomous-science/benchmark/"
        "P9_GOVERNED_CAPABILITY_COMPANION.md",
        "papers/candidates/P6_P10_ISSUE_RECONCILIATION_2026-08-18.md",
    }


def test_the_published_count_is_mostly_a_vendored_lean_checkout() -> None:
    """``PASS (547 files)`` is not 547 files of P10.

    461 are Mathlib source and 7 are an ASlib scenario --- material the lane did
    not write. 514 of the 547 are not in the lane directory at all: they belong to
    the two retired ``paper-xx-`` predecessors, whose grade the superiority ledger
    records as discharging no P10-U terminal.
    """

    origin = shipped.manifest_entry_origin(REPO_ROOT)
    assert origin["vendored_lean_corpus"] == 461
    assert origin["vendored_aslib_scenario"] == 7
    assert origin["outside_the_lane_directory"] == 514
    assert origin["shared_lane"] == 33
    authored = sum(
        origin[name]
        for name in ("p10_predecessor_authored", "p9_predecessor_authored", "shared_lane",
                     "other_papers")
    )
    assert authored == 79


def test_the_active_p10_identity_carries_no_binding_at_all() -> None:
    """Everything bound belongs to a predecessor or to a shared lane.

    ``papers/paper-10-structured-problem-solving/`` is P10's registered active
    directory in ``PAPER_DIRECTORIES``. Its single file is named by none of the
    three digest files.
    """

    active = REPO_ROOT / "papers" / "paper-10-structured-problem-solving"
    files = {path.resolve() for path in active.rglob("*") if path.is_file()}
    assert files, "the active P10 directory is empty; this test has lost its subject"
    named: set[Path] = set()
    for binding in shipped.shipped_bindings(REPO_ROOT):
        named.update(binding.named_paths)
    assert not (files & named)


def test_the_existing_coverage_survey_cannot_see_this_binding() -> None:
    """Why this is not ``content_binding_coverage`` again.

    That survey discovers bindings by a ``SHA256SUMS`` file, which the lane does
    not use, so it reports the lane as ``UNBOUND`` --- wrong about a directory
    carrying 547 live digests, and right only by accident that it blocks. It also
    reports partial coverage without acting on it: a paper with one bound file
    among five hundred assesses ``PASS``.
    """

    binding = inspect_paper(REPO_ROOT, REPO_ROOT / shipped.LANE)
    assert binding.state is PaperBindingState.UNBOUND
    assert binding.files_bound == 0
    assert assess_paper(binding).outcome is Outcome.CANNOT_CHECK


def test_the_cli_report_carries_both_denominators_and_blocks() -> None:
    report = audit_p10_publication_binding(REPO_ROOT)
    assert report["outcome"] == "FAIL"
    assert report["files_enrolled"] == 551
    assert report["files_in_scope"] == report["files_enrolled"] + report["files_unenrolled"]
    assert report["drift_verdict"]["outcome"] == "PASS"
    assert report["membership_verdict"]["outcome"] == "FAIL"
    assert report["generator_agrees_with_committed_manifest"] is True


def test_the_audit_never_writes_to_the_content_bound_lane(audit) -> None:
    """Loading the generator must not regenerate the manifest it audits."""

    lane = REPO_ROOT / shipped.LANE
    manifest = lane / shipped.PUBLICATION_MANIFEST
    before = manifest.read_bytes()
    shipped.shipped_generator_enrolment(REPO_ROOT)
    audit_report(audit)
    assert manifest.read_bytes() == before

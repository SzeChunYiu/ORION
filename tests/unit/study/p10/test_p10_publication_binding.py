"""P10's shipped binding, measured against the files in this checkout.

The finding these tests were written for is closed. They said the shipped
manifest bound every committed number and none of the code that produced them,
and they were built so that closing the gap would red them --- which it did. They
now pin the closed state, with the same reasoning kept: what has to stay true is
that the producers are inside the binding, not merely that some count is small.

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

#: The files whose absence from the binding was the finding. Named rather than
#: counted, because a count alone would let one be swapped for another. The first
#: is the runner ``REPRODUCE_LOCAL_CLOSURE.sh`` executes and whose committed
#: output the manifest already bound; the last two are the toolchain pin and the
#: native shim behind P10's eight Lean acceptance receipts --- both of which
#: decide what the proofs compile to, and neither of which carried an extension
#: on the generator's old allowlist.
LOAD_BEARING = (
    "papers/orion-learning-machine/experiments/phase1_mechanic_composition/run_v2.py",
    "papers/orion-learning-machine/experiments/phase0_solver_ecology/run.py",
    "papers/orion-learning-machine/experiments/phase2_real_source/run_phase2a.py",
    "papers/orion-learning-machine/VERIFY_LOCAL_CLOSURE_V2.sh",
    "papers/archive/2026-08-pre-unification/paper-xx-content-bound-math-evaluation/benchmark/corpus/"
    "mathlib4_e72c1e277f31/lean-toolchain",
    "papers/archive/2026-08-pre-unification/paper-xx-content-bound-math-evaluation/benchmark/native/lean_readlink_self.c",
)

#: Was 20, measured 2026-08-21; the ratchet said enrolling a file may only lower
#: it and every drop must come with the manifest regeneration that caused it.
#: Both happened: ``experiments/`` became a generator root, the suffix allowlist
#: became a build-output denylist, three lane-root files were named, and the
#: manifest was regenerated to 567 entries.
UNENROLLED_CEILING = 0


@pytest.fixture(scope="module")
def audit():
    return shipped.audit_p10_publication(REPO_ROOT)


def test_the_shipped_binding_is_clean_and_its_membership_is_closed(audit) -> None:
    """The finding, closed, in two verdicts on one artifact.

    Drift ``PASS`` was never disputed: the enrolled files are unchanged and the
    shipped verifier really does red on the first byte of any of them. What was
    ``FAIL`` is membership --- the enrolled set was chosen by ``included_files()``
    inside the lane the manifest protects, and twenty files inside the same
    declared scope were named by no digest a gate opens. Scope and enrolment now
    agree at 587, so both verdicts pass and the closure requirement no longer
    raises.
    """

    assert assess_drift(audit).outcome is Outcome.PASS
    assert assess_membership(audit).outcome is Outcome.PASS
    assert audit_outcome(audit) is Outcome.PASS
    assert not audit_outcome(audit).blocks

    require_closed_membership(audit)  # no longer raises


def test_the_load_bearing_files_are_now_inside_the_binding(audit) -> None:
    """Named, not counted: a count would let one be swapped for another."""

    enrolled = {path.relative_to(REPO_ROOT).as_posix() for path in audit.enrolled}
    missing = sorted(set(LOAD_BEARING) - enrolled)
    assert not missing, missing
    assert len(audit.unenrolled) <= UNENROLLED_CEILING


def test_every_experiment_driver_in_the_lane_is_enrolled(audit) -> None:
    """The producers are inside the binding, alongside the results they produced.

    ``results/`` was one of the generator's roots and ``experiments/`` was not, so
    the manifest pinned every committed number and none of the code that made
    them: a reader could confirm the numbers had not moved while the program that
    computed them changed underneath. ``experiments/`` is now a root, and this
    fails if it is ever dropped again.
    """

    enrolled = {path.relative_to(REPO_ROOT).as_posix() for path in audit.enrolled}
    experiments = REPO_ROOT / shipped.LANE / "experiments"
    drivers = {
        path.relative_to(REPO_ROOT).as_posix()
        for path in experiments.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    }
    assert drivers, "the experiments directory is empty; this test has lost its subject"
    assert drivers <= enrolled, sorted(drivers - enrolled)

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
    """A receipt is not a check, and nothing here dereferences this one.

    ``SCRIPT_MANIFEST_SHA256.txt`` used to be the only thing naming twelve of the
    twenty unenrolled files, which is what ``stale_only`` counted: named by a
    digest file, observed by no gate. Those twelve are now in the enforced
    manifest, so ``stale_only`` is empty.

    This test used to make its point with drift: the receipt disagreed with the
    bytes in ten places, and a green suite proved nothing was hashing the paths it
    names. That evidence is gone, and deliberately so --- 42b53b2e6 re-pinned the
    learning-machine manifests after R0's renames, and the copy this audit reads
    now matches in all 36 named-and-present paths.

    Repairing the drift did not make the receipt a check, so the claim is asserted
    against what still carries it rather than against a number that has been
    fixed. ``enforced`` is False and ``dereferenced_by`` is empty: no gate reads
    this file, which is why its digests were free to drift in the first place and
    would be free to drift again. The stale copy under
    ``papers/candidates/orion-learning-machine/`` still disagrees in five places
    and still reds nothing.
    """

    check = next(item for item in audit.checks if item.binding_id == shipped.SCRIPT_MANIFEST)
    assert check.enforced is False
    assert check.dereferenced_by == ""
    assert check.named == 36
    # Re-pinned by 42b53b2e6; the unenforced-ness below is the surviving claim.
    assert len(check.drifted) == 0
    assert len(audit.stale_only) == 0
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
        "papers/orion-18-epistemic-authority-autonomous-science/benchmark/"
        "P9_GOVERNED_CAPABILITY_COMPANION.md",
        "papers/candidates/P6_P10_ISSUE_RECONCILIATION_2026-08-18.md",
    }


def test_the_published_count_is_mostly_a_vendored_lean_checkout() -> None:
    """A passing membership verdict is still not 587 files of P10.

    463 are Mathlib source and 8 are an ASlib scenario --- material the lane did
    not write. 520 of the 587 are not in the lane directory at all: they belong to
    the two retired ``paper-xx-`` predecessors, whose grade the superiority ledger
    records as discharging no P10-U terminal. Closing the membership gap enlarged
    the authored count from 79 to 96, because seventeen of the newly enrolled
    files are the lane's own experiment drivers; it did not make the vendored
    majority any less vendored. Closing the 2026-08-26 payload hole (fourteen
    more lane files: the phase2_real_source experiment set, the framework
    package, the programme doc) enlarged it again from 96 to 112, once more
    without adding a single vendored file.
    """

    origin = shipped.manifest_entry_origin(REPO_ROOT)
    assert origin["vendored_lean_corpus"] == 463
    assert origin["vendored_aslib_scenario"] == 8
    assert origin["outside_the_lane_directory"] == 520
    assert origin["shared_lane"] == 63
    authored = sum(
        origin[name]
        for name in ("p10_predecessor_authored", "p9_predecessor_authored", "shared_lane",
                     "other_papers")
    )
    assert authored == 112


def test_the_active_p10_identity_carries_no_binding_at_all() -> None:
    """Everything bound belongs to a predecessor or to a shared lane.

    ``papers/orion-20-structured-problem-solving/`` is P10's registered active
    directory in ``PAPER_DIRECTORIES``. Its single file is named by none of the
    three digest files.
    """

    active = REPO_ROOT / "papers" / "orion-20-structured-problem-solving"
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


def test_the_cli_report_carries_both_denominators_and_no_longer_blocks() -> None:
    """Both denominators still reported; they now agree.

    The pair is the point, not the pass. A report that printed only the drift
    verdict would have said PASS throughout the period when twenty files were
    unobservable, which is why the enrolled count and the scope are both here.
    """

    report = audit_p10_publication_binding(REPO_ROOT)
    assert report["outcome"] == "PASS"
    assert report["files_enrolled"] == 587
    assert report["files_unenrolled"] == 0
    assert report["files_in_scope"] == report["files_enrolled"] + report["files_unenrolled"]
    assert report["drift_verdict"]["outcome"] == "PASS"
    assert report["membership_verdict"]["outcome"] == "PASS"
    assert report["generator_agrees_with_committed_manifest"] is True


def test_the_audit_never_writes_to_the_content_bound_lane(audit) -> None:
    """Loading the generator must not regenerate the manifest it audits."""

    lane = REPO_ROOT / shipped.LANE
    manifest = lane / shipped.PUBLICATION_MANIFEST
    before = manifest.read_bytes()
    shipped.shipped_generator_enrolment(REPO_ROOT)
    audit_report(audit)
    assert manifest.read_bytes() == before

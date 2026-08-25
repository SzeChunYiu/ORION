"""Whether a paper's content change is something the repository can notice.

``papers/SYNC_CONTRACT.md`` names two obligations and they are not the same:

1. *Framework/paper terminology sync* --- ``papers/FRAMEWORK_SNAPSHOT.json``
   against ``orion.registry``. Machine-checked, and the contract is explicit
   that matching it "proves only terminology/mechanic synchronization, not
   scientific validity or empirical support".
2. *Paper content binding* --- a committed digest per file, so that changing a
   paper's bytes without regenerating its manifest fails a check.

The second is what makes a content change visible. Measured on this tree by the
survey below: **eight of the twenty-four directories under ``papers/`` bind
something, 214 files bound, 1 427 unbound, 0 drifted** --- and only three of the
eight bind their whole selves. P6, P7 and P8 enumerate their directories and
cover them completely. P1-P5 bind a declared list from a ``journal_package/``,
covering between 10% and 22% of their files; the rest of the tree binds nothing.

Both halves of that sentence are corrections to this module's first version,
which looked for a digest file at each paper's root and nowhere else. It
therefore reported P1-P5 as binding nothing at all, and would have reported a
paper covering 34 of its 283 files identically to one covering all of them ---
the same conflation it was written to prevent, one level up. Hence
:data:`PaperBindingState.BOUND_PARTIAL` and
:attr:`PaperBinding.coverage_outcome`: a clean drift verdict over a corner of a
paper is a true statement about that corner and says nothing about the rest.

The defect this module exists to prevent is not that the unbound papers are
wrong. It is that they are *silent*. Ask "how many files drifted?" and an
unbound paper answers ``0``, exactly as a bound and clean one does. That is the
2. *Paper content binding* --- a committed digest per watched file, so that
   changing canonical paper bytes without regenerating the binding fails a check.

Two binding forms currently exist:

- P6, P7 and P8 carry per-directory ``CONTENT_MANIFEST_V1.json`` / ``SHA256SUMS``;
- the closed ORION-Q publication wave carries one deliberate cross-paper binding,
  ``papers/Q_SERIES_CONTENT_BINDING_V1.json``, over the canonical Q1-Q4
  submission surfaces while leaving historical snapshots visibly outside that
  publication subset.

The defect this module exists to prevent is not that an unbound paper is wrong.
It is that it is *silent*. Ask "how many files drifted?" and an unbound paper
answers ``0``, exactly as a bound and clean one does. That is the
``VACUOUS_GUARD_ZERO_DENOMINATOR`` shape
(``research/failures/2026-08-vacuous-guard-zero-denominator/``) applied to
content binding: the numerator is carried and the denominator is dropped, so
"nothing changed" and "nothing was watched" print the same character.

So this module reports the denominator. A paper that binds nothing is
:data:`PaperBindingState.UNBOUND` and contributes no opportunities, which makes
its guard :data:`~orion.programme.records.Outcome.CANNOT_CHECK` rather than a
pass --- and by ``Outcome.blocks`` that stops a promotion exactly as a ``FAIL``
would.

The per-directory verification is deliberately independent of
``papers/candidates/checkers/check_content_binding_v1.py``. The Q-series
cross-binding is independently recomputed through
``orion.programme.q_series_content_binding``. Neither path derives the bytes it
expects while comparing them, so a stale committed digest remains observable.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Sequence
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from orion.programme.guard_exercise import (
    GuardAssessment,
    GuardExercise,
    assess_guard,
    worst_outcome,
)
from orion.programme.q_series_content_binding import (
    BINDING_PATH as Q_SERIES_BINDING_PATH,
    git_blob_sha1,
    q_series_bound_rows_for_directory,
)
from orion.programme.records import Outcome

PAPERS_DIRNAME = "papers"
SUMS_NAME = "SHA256SUMS"
MANIFEST_GLOB = "*MANIFEST*.json"
OVERLAY_GLOB = "*OVERLAY*.json"

CONTENT_DRIFT_GUARD_ID = "PAPERS.CONTENT_DRIFT"
CONTENT_DRIFT_OPPORTUNITY = (
    "one file whose bytes a committed digest binds; a file no manifest lists "
    "cannot be observed to drift, so it offers the guard no opportunity to fire"
)

#: Build output that no content binding should ever cover. Bytecode filenames
#: carry the interpreter and plugin versions that produced them, so binding them
#: fails on machine identity rather than on content --- the reason
#: ``check_content_binding_v1`` excludes them too, kept in step here.
_EXCLUDED_DIR_NAMES = frozenset({"__pycache__", ".pytest_cache", ".ruff_cache", ".mypy_cache"})
_EXCLUDED_SUFFIXES = frozenset(
    {".pyc", ".pyo", ".pyd", ".aux", ".bbl", ".blg", ".fdb_latexmk", ".fls", ".synctex"}
)

#: Suffixes that are LaTeX sidecars *only when they sit beside their own source*.
#: `.log` cannot be excluded outright --- three tracked logs under `papers/` are
#: evidence rather than residue --- so a `.log` counts as residue exactly when a
#: `.tex` of the same stem is its neighbour.
_SIDECAR_SUFFIXES = frozenset({".log", ".out", ".toc"})

#: Directories under ``papers/`` that are shared material rather than one paper.
#: ``candidates`` holds the P6-P8 shared package, which those papers' own
#: manifests already bind; counting it as its own unbound paper would report the
#: same files twice, once bound and once not.
_NOT_A_PAPER = frozenset({"candidates"})


class PaperBindingState(str, Enum):
    """Total taxonomy of what a repository can say about one paper's watched bytes.

    ``UNBOUND`` is the state the previous accounting could not express: it looks
    identical to ``BOUND_CURRENT`` in any report that counts only drifted files.
    """

    BOUND_CURRENT = "BOUND_CURRENT"
    BOUND_PARTIAL = "BOUND_PARTIAL"
    BOUND_DRIFTED = "BOUND_DRIFTED"
    BOUND_UNREADABLE = "BOUND_UNREADABLE"
    UNBOUND = "UNBOUND"

    @property
    def exercises_drift_guard(self) -> bool:
        """Only a readable binding gives the drift guard something to observe."""

        return self in {
            PaperBindingState.BOUND_CURRENT,
            PaperBindingState.BOUND_PARTIAL,
            PaperBindingState.BOUND_DRIFTED,
        }

    @property
    def covers_the_whole_paper(self) -> bool:
        """Whether a clean drift verdict speaks for the paper rather than a corner of it."""

        return self is PaperBindingState.BOUND_CURRENT


@dataclass(frozen=True)
class PaperBinding:
    """One paper directory's binding state, with the counts that justify it."""

    paper_id: str
    directory: str
    state: PaperBindingState
    files_on_disk: int
    files_bound: int
    drifted_paths: tuple[str, ...]
    missing_paths: tuple[str, ...]
    detail: str

    def __post_init__(self) -> None:
        if not self.paper_id.strip():
            raise ValueError("a binding record requires a paper id")
        if self.files_on_disk < 0 or self.files_bound < 0:
            raise ValueError(f"{self.paper_id}: file counts cannot be negative")
        if not self.state.exercises_drift_guard and (self.drifted_paths or self.missing_paths):
            raise ValueError(
                f"{self.paper_id}: {self.state.value} cannot carry drifted or missing "
                "paths; nothing was compared"
            )
        if self.state is PaperBindingState.UNBOUND and self.files_bound:
            raise ValueError(f"{self.paper_id}: UNBOUND contradicts {self.files_bound} bound files")
        if self.state is PaperBindingState.BOUND_CURRENT and self.drifted_paths:
            raise ValueError(f"{self.paper_id}: BOUND_CURRENT contradicts recorded drift")
        if self.state is PaperBindingState.BOUND_CURRENT and self.unbound_files:
            raise ValueError(
                f"{self.paper_id}: BOUND_CURRENT claims the whole paper is watched while "
                f"{self.unbound_files} of its {self.files_on_disk} files are not; that is "
                "BOUND_PARTIAL"
            )
        if self.state is PaperBindingState.BOUND_PARTIAL and not self.files_bound:
            raise ValueError(
                f"{self.paper_id}: BOUND_PARTIAL covers no file of this paper; that is UNBOUND"
            )
        if self.state is PaperBindingState.BOUND_PARTIAL and not self.unbound_files:
            raise ValueError(
                f"{self.paper_id}: BOUND_PARTIAL covers every file; that is BOUND_CURRENT"
            )
        if self.state is PaperBindingState.BOUND_DRIFTED and not (
            self.drifted_paths or self.missing_paths
        ):
            raise ValueError(f"{self.paper_id}: BOUND_DRIFTED names no drifted or missing path")

    @property
    def unbound_files(self) -> int:
        """Files present in the directory that no digest covers.

        Non-zero on a ``BOUND_*`` paper means the binding is partial. For the
        Q-series this is intentional: historical manuscript snapshots remain
        provenance while the canonical submission subset is what the cross-paper
        manifest watches.
        """

        return max(0, self.files_on_disk - self.files_bound)

    @property
    def violations(self) -> int:
        return len(self.drifted_paths) + len(self.missing_paths)

    @property
    def coverage_outcome(self) -> Outcome:
        """Whether this paper's contents are watched *at all*, drift aside.

        Deliberately separate from the drift verdict. A binding that covers 34 of
        283 files and reports no drift has told the truth about 34 files and
        nothing about the other 249, and the two facts must not be summed into
        one character. Coverage is never ``FAIL``: an unwatched file is an absent
        measurement, not a detected violation.
        """

        if self.state.covers_the_whole_paper:
            return Outcome.PASS
        return Outcome.CANNOT_CHECK

    def as_json(self) -> dict[str, object]:
        return {
            "paper_id": self.paper_id,
            "directory": self.directory,
            "state": self.state.value,
            "files_on_disk": self.files_on_disk,
            "files_bound": self.files_bound,
            "unbound_files": self.unbound_files,
            "coverage_outcome": self.coverage_outcome.value,
            "drifted_paths": list(self.drifted_paths),
            "missing_paths": list(self.missing_paths),
            "detail": self.detail,
        }


def is_build_artifact(path: Path) -> bool:
    """True for generated files no content binding should include.

    Defined here and imported by `check_content_binding_v1.py` rather than
    written out twice. It *was* written out twice, identically, and the two
    copies drifted the moment LaTeX trees arrived: the checker learned to skip
    `main.fdb_latexmk` and this module did not, so one reported the binding
    current while the other reported seven files nobody was watching.
    """

    if path.suffix in _EXCLUDED_SUFFIXES:
        return True
    if path.suffix in _SIDECAR_SUFFIXES and path.with_suffix(".tex").is_file():
        return True
    return any(part in _EXCLUDED_DIR_NAMES for part in path.parts)


def _files_on_disk(directory: Path) -> int:
    return sum(
        1
        for path in directory.rglob("*")
        if path.is_file() and not is_build_artifact(path) and path.name != SUMS_NAME
    )


def parse_sums(text: str) -> dict[str, str]:
    """Parse a ``sha256sum``-format digest file into ``{path: digest}``.

    Raises rather than skipping a malformed line. A digest file that silently
    drops the entries it could not read binds fewer files than it appears to,
    which is the same missing-denominator defect in miniature.
    """

    mapping: dict[str, str] = {}
    for number, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        digest, separator, rest = line.partition("  ")
        if not separator or not rest.strip():
            raise ValueError(f"malformed digest line {number}: {raw!r}")
        if len(digest) != 64 or any(character not in "0123456789abcdef" for character in digest):
            raise ValueError(f"line {number} does not carry a lowercase sha256: {digest!r}")
        mapping[rest.strip()] = digest
    return mapping


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def _sums_files(directory: Path) -> tuple[Path, ...]:
    """Every digest file anywhere under a paper, not only one at its root.

    The first version of this looked for ``SHA256SUMS`` beside the paper's
    ``README`` and nowhere else, which is where P6-P8 happen to put theirs. P1-P5
    put theirs in ``journal_package/`` and P3 keeps four more under
    ``evidence/``; all of them were reported as declaring no binding at all. A
    survey that promises to discover by convention and then hardcodes one
    directory is the enumerated-registry failure it was written to avoid, so
    discovery is now by search.
    """

    return tuple(sorted(path for path in directory.rglob(SUMS_NAME) if path.is_file()))


def _resolve_recorded(recorded_path: str, *bases: Path) -> Path | None:
    """Locate one digest-file entry against the path conventions in use here.

    P6-P8 record repo-relative paths because their reproduction subject reaches
    outside their own directory; P1-P5's journal packages record paths relative
    to the paper root. Neither convention is wrong and neither is declared in the
    file, so both are tried and the first that names a real file wins.
    """

    for base in bases:
        candidate = base / recorded_path
        if candidate.is_file():
            return candidate.resolve()
    return None


def _inspect_q_series_cross_binding(
    repo_root: Path, directory: Path, *, files_on_disk: int
) -> PaperBinding | None:
    """Inspect the canonical Q-series subset when this directory participates.

    The binding itself sits at ``papers/Q_SERIES_CONTENT_BINDING_V1.json``, so a
    per-directory convention scan cannot discover it. This adapter keeps the
    repository-wide survey truthful while preserving the deliberate distinction
    between canonical submission files and historical snapshots.
    """

    relative = directory.relative_to(repo_root).as_posix()
    declared = (repo_root / Q_SERIES_BINDING_PATH).is_file()
    if not declared:
        return None
    try:
        rows = q_series_bound_rows_for_directory(repo_root, directory)
    except (OSError, TypeError, ValueError, json.JSONDecodeError) as error:
        if directory.name.startswith("Q-paper-"):
            return PaperBinding(
                paper_id=directory.name,
                directory=relative,
                state=PaperBindingState.BOUND_UNREADABLE,
                files_on_disk=files_on_disk,
                files_bound=0,
                drifted_paths=(),
                missing_paths=(),
                detail=f"{Q_SERIES_BINDING_PATH.as_posix()} could not be read: {error}",
            )
        return None
    if not rows:
        return None

    drifted: list[str] = []
    missing: list[str] = []
    for row in rows:
        path_value = str(row["path"])
        expected = str(row["git_blob_sha1"])
        target = repo_root / path_value
        if not target.is_file():
            missing.append(path_value)
        elif git_blob_sha1(target.read_bytes()) != expected:
            drifted.append(path_value)

    state = (
        PaperBindingState.BOUND_DRIFTED
        if drifted or missing
        else PaperBindingState.BOUND_CURRENT
    )
    if state is PaperBindingState.BOUND_DRIFTED:
        detail = (
            f"{relative}: Q-series canonical binding has {len(drifted)} changed and "
            f"{len(missing)} missing path(s) among {len(rows)} watched publication files"
        )
    else:
        detail = (
            f"{relative}: {len(rows)} canonical publication files match the shared "
            "Q-series Git-blob binding; other files in this directory are historical or "
            "non-canonical unless separately bound"
        )

    return PaperBinding(
        paper_id=directory.name,
        directory=relative,
        state=state,
        files_on_disk=files_on_disk,
        files_bound=len(rows),
        drifted_paths=tuple(sorted(drifted)),
        missing_paths=tuple(sorted(missing)),
        detail=detail,
    )


def inspect_paper(repo_root: Path, directory: Path) -> PaperBinding:
    """Judge one paper directory by hashing what is on disk.

    Reads only committed artifacts --- the digest files under the paper --- and
    never derives what a manifest ought to say. Deriving it is the generator's
    job; agreeing with a derivation is not the same as agreeing with the bytes.

    The subject is *this paper's contents*. A manifest may also bind files
    outside the paper (P6-P8's bind their shared checkers and tests); those are
    watched by the checker that owns them and are not counted here, so a paper
    cannot look well covered because its manifest reaches elsewhere.
    Reads only committed binding artifacts and never derives what the binding
    ought to say. Direct SHA256SUMS packages and the Q-series cross-binding use
    different content identities but the same guard semantics.
    """

    paper_id = directory.name
    relative = directory.relative_to(repo_root).as_posix()
    on_disk = _files_on_disk(directory)
    sums_files = _sums_files(directory)

    q_series = _inspect_q_series_cross_binding(repo_root, directory, files_on_disk=on_disk)
    if q_series is not None:
        return q_series

    if not sums_files:
        return PaperBinding(
            paper_id=paper_id,
            directory=relative,
            state=PaperBindingState.UNBOUND,
            files_on_disk=on_disk,
            files_bound=0,
            drifted_paths=(),
            missing_paths=(),
            detail=(
                f"{relative} declares no content binding, so none of its {on_disk} files "
                "can be observed to change; this is an absent measurement, not a clean one"
            ),
        )

    root = directory.resolve()
    covered: dict[Path, str] = {}
    unresolved: list[str] = []
    for sums_path in sums_files:
        try:
            recorded = parse_sums(sums_path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as error:
            return PaperBinding(
                paper_id=paper_id,
                directory=relative,
                state=PaperBindingState.BOUND_UNREADABLE,
                files_on_disk=on_disk,
                files_bound=0,
                drifted_paths=(),
                missing_paths=(),
                detail=f"{sums_path.relative_to(repo_root)} could not be read: {error}",
            )
        for recorded_path, digest in sorted(recorded.items()):
            target = _resolve_recorded(recorded_path, repo_root, sums_path.parent, directory)
            if target is None:
                # Only a path that should have named a file inside this paper is
                # this survey's business; an entry naming a vanished file
                # elsewhere belongs to whichever checker owns that manifest.
                if (directory / recorded_path).parent.is_dir() or recorded_path.startswith(
                    relative + "/"
                ):
                    unresolved.append(recorded_path)
                continue
            # A digest file is not paper content, and `_files_on_disk` already
            # excludes it from the denominator. Counting one here would let a
            # nested manifest that binds another manifest push `files_bound`
            # past the number of files there are, and report a stale
            # digest-of-a-digest as a change to the paper.
            if (
                root in target.parents
                and target.name != SUMS_NAME
                and not is_build_artifact(target)
            ):
                covered[target] = digest

    # A successor manifest binds files that V1 deliberately excludes from its
    # frozen identity, and it carries its own sha256 per file. Reading only
    # SHA256SUMS therefore reported those files as watched by nothing, which
    # was false: for P6 that produced "the other 10 can change without any
    # check noticing" while CONTENT_MANIFEST_V2 was watching all ten with
    # current, matching digests.
    #
    # This still reads only COMMITTED digest artifacts and never derives what a
    # binding ought to say -- a V2 manifest is such an artifact.
    for manifest_path in sorted(directory.glob("CONTENT_MANIFEST_V*.json")):
        try:
            payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            # An unreadable successor manifest must not be treated as coverage,
            # and must not mask the V1 result either. Leave it uncounted.
            continue
        for entry in payload.get("bound_files", ()):
            if not isinstance(entry, dict):
                continue
            digest = entry.get("sha256")
            recorded_path = entry.get("path")
            if not digest or not recorded_path:
                continue
            target = _resolve_recorded(
                str(recorded_path), repo_root, manifest_path.parent, directory
            )
            if target is None:
                continue
            if (
                root in target.parents
                and target.name != SUMS_NAME
                and not is_build_artifact(target)
            ):
                covered.setdefault(target, digest)

    drifted = sorted(
        path.relative_to(repo_root).as_posix()
        for path, digest in covered.items()
        if _sha256(path) != digest
    )
    missing = sorted(set(unresolved))

    if drifted or missing:
        return PaperBinding(
            paper_id=paper_id,
            directory=relative,
            state=PaperBindingState.BOUND_DRIFTED,
            files_on_disk=on_disk,
            files_bound=len(covered),
            drifted_paths=tuple(drifted),
            missing_paths=tuple(missing),
            detail=(
                f"{relative}: {len(drifted)} of {len(covered)} bound files changed without "
                f"the digest file, and {len(missing)} bound path(s) are gone"
            ),
        )

    if not covered:
        return PaperBinding(
            paper_id=paper_id,
            directory=relative,
            state=PaperBindingState.UNBOUND,
            files_on_disk=on_disk,
            files_bound=0,
            drifted_paths=(),
            missing_paths=(),
            detail=(
                f"{relative} carries {len(sums_files)} digest file(s) that bind no file of "
                f"this paper, so none of its {on_disk} files can be observed to change"
            ),
        )

    if len(covered) >= on_disk:
        return PaperBinding(
            paper_id=paper_id,
            directory=relative,
            state=PaperBindingState.BOUND_CURRENT,
            files_on_disk=on_disk,
            files_bound=len(covered),
            drifted_paths=(),
            missing_paths=(),
            detail=f"{relative}: all {len(covered)} files match their committed digests",
        )

    return PaperBinding(
        paper_id=paper_id,
        directory=relative,
        state=PaperBindingState.BOUND_PARTIAL,
        files_on_disk=on_disk,
        files_bound=len(covered),
        drifted_paths=(),
        missing_paths=(),
        detail=(
            f"{relative}: {len(covered)} of {on_disk} files are bound and all match; the "
            f"other {on_disk - len(covered)} can change without any check noticing"
        ),
    )


def survey_paper_bindings(repo_root: Path) -> tuple[PaperBinding, ...]:
    """Every directory under ``papers/``, whether or not it declares a binding.

    Discovery is by convention for local bindings plus the canonical cross-series
    Q binding. A paper that never adopts either form cannot drop off the report.
    """

    # Resolved, not taken as given. Every path this module compares against the
    # root is resolved, so a relative ``--repo-root .`` made `relative_to` raise
    # on the first drifted file -- a crash reachable only when something had
    # actually drifted, which is the worst possible time for the survey to die.
    repo_root = Path(repo_root).resolve()
    papers = repo_root / PAPERS_DIRNAME
    if not papers.is_dir():
        raise FileNotFoundError(f"no {PAPERS_DIRNAME}/ directory under {repo_root}")
    return tuple(
        inspect_paper(repo_root, directory)
        for directory in sorted(papers.iterdir())
        if directory.is_dir() and directory.name not in _NOT_A_PAPER
    )


def drift_exercise(bindings: tuple[PaperBinding, ...]) -> GuardExercise:
    """The drift guard's denominator: files under binding, not files in ``papers/``."""

    watched = tuple(item for item in bindings if item.state.exercises_drift_guard)
    return GuardExercise(
        guard_id=CONTENT_DRIFT_GUARD_ID,
        arm_id="papers",
        opportunities=sum(item.files_bound for item in watched),
        violations=sum(item.violations for item in watched),
        opportunity_definition=CONTENT_DRIFT_OPPORTUNITY,
    )


def assess_paper(binding: PaperBinding) -> GuardAssessment:
    """One paper's drift verdict, with its own denominator."""

    return assess_guard(
        GuardExercise(
            guard_id=CONTENT_DRIFT_GUARD_ID,
            arm_id=binding.paper_id,
            opportunities=binding.files_bound if binding.state.exercises_drift_guard else 0,
            violations=binding.violations,
            opportunity_definition=CONTENT_DRIFT_OPPORTUNITY,
        )
    )


def assess_binding_coverage(bindings: tuple[PaperBinding, ...]) -> GuardAssessment:
    """Roll per-paper verdicts up without letting one bound paper cover for another.

    Assessing only the pooled exercise can report a clean pass while another paper
    is entirely unobserved. The roll-up is therefore over per-paper verdicts, and
    one ``UNBOUND`` paper keeps the overall survey at ``CANNOT_CHECK``.
    """

    if not bindings:
        raise ValueError("an empty survey cannot be rolled up; it blocks by construction")
    return max(
        (assess_paper(item) for item in bindings),
        key=lambda item: (item.outcome is Outcome.FAIL, item.outcome is not Outcome.PASS),
    )


def survey_report(bindings: tuple[PaperBinding, ...]) -> dict[str, object]:
    """The machine-readable survey, denominator first."""

    pooled = drift_exercise(bindings)
    per_paper = {item.paper_id: assess_paper(item) for item in bindings}
    unbound = tuple(item for item in bindings if item.state is PaperBindingState.UNBOUND)
    return {
        "schema_version": "orion.programme.content-binding-coverage.v1",
        "outcome": worst_outcome(tuple(per_paper.values())).value,
        "papers_surveyed": len(bindings),
        "papers_bound": sum(1 for item in bindings if item.state.exercises_drift_guard),
        "papers_unbound": len(unbound),
        "files_bound": pooled.opportunities,
        "files_unbound": sum(item.unbound_files for item in bindings),
        "files_drifted": pooled.violations,
        "pooled_exercise": pooled.as_json(),
        "pooled_verdict_is_not_the_answer": (
            "the pooled exercise is reported for completeness; the survey outcome is the "
            "worst per-paper verdict, because a bound paper's clean digests say nothing "
            "about an unbound paper's bytes"
        ),
        "by_paper": {item.paper_id: item.as_json() for item in bindings},
        "verdicts": {name: item.as_json() for name, item in sorted(per_paper.items())},
    }


class ContentBindingNotCovered(RuntimeError):
    """Raised when a paper's content changes cannot be observed at all."""


def require_binding_coverage(bindings: tuple[PaperBinding, ...]) -> None:
    """Refuse to treat the survey as clean while any paper is unwatched.

    Raises rather than returning a verdict for the reason ``orion.core.digests``
    does: a boundary that answers ``False`` is indistinguishable from a negative
    result, and here the two mean opposite things.
    """

    unbound = tuple(item for item in bindings if item.state is PaperBindingState.UNBOUND)
    drifted = tuple(item for item in bindings if item.state is PaperBindingState.BOUND_DRIFTED)
    if drifted:
        named = ", ".join(f"{item.paper_id} ({item.violations})" for item in drifted[:5])
        raise ContentBindingNotCovered(
            f"{len(drifted)} paper(s) changed without regenerating their digests: {named}"
        )
    if unbound:
        names = ", ".join(item.paper_id for item in unbound[:5])
        more = "" if len(unbound) <= 5 else f" (+{len(unbound) - 5} more)"
        raise ContentBindingNotCovered(
            f"{len(unbound)} of {len(bindings)} papers declare no content binding, so "
            f"{sum(item.files_on_disk for item in unbound)} files cannot be observed to "
            f"change: {names}{more}"
        )


def main(argv: Sequence[str]) -> int:
    """Report the survey. Exit 0 earned, 1 real drift, 3 CANNOT_CHECK.

    ``argv`` is required rather than defaulting to ``sys.argv[1:]``. A zero-
    argument callable in this package is walked and invoked by
    ``tests/unit/programme/test_constitutional_boundary.py``; one that reads
    global state would parse the *test runner's* arguments and exit the
    interpreter, and ``SystemExit`` is not an ``Exception``, so it escapes that
    walker's guard. Taking the input explicitly is the better shape regardless.
    """

    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parents[3],
        help="repository root containing papers/",
    )
    parser.add_argument("--json", action="store_true", help="emit the machine-readable survey")
    arguments = parser.parse_args(argv)

    bindings = survey_paper_bindings(arguments.repo_root)
    report = survey_report(bindings)
    if arguments.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(
            f"{report['papers_bound']}/{report['papers_surveyed']} papers bound; "
            f"{report['files_bound']} files bound, {report['files_unbound']} unbound; "
            f"{report['files_drifted']} drifted"
        )
        for item in bindings:
            verdict = assess_paper(item)
            print(f"  {item.paper_id:<48} {item.state.value:<18} {verdict.outcome.value}")

    outcome = Outcome(report["outcome"])
    if outcome is Outcome.PASS:
        return 0
    return 1 if outcome is Outcome.FAIL else 3


__all__ = [
    "CONTENT_DRIFT_GUARD_ID",
    "CONTENT_DRIFT_OPPORTUNITY",
    "ContentBindingNotCovered",
    "PaperBinding",
    "PaperBindingState",
    "assess_binding_coverage",
    "assess_paper",
    "drift_exercise",
    "inspect_paper",
    "parse_sums",
    "require_binding_coverage",
    "survey_paper_bindings",
    "survey_report",
]


if __name__ == "__main__":  # pragma: no cover
    import sys

    raise SystemExit(main(sys.argv[1:]))

"""Whether a digest manifest's watched set is closed against the tree it protects.

A content-binding check answers one of two questions and prints the same line
for both:

1. *Inclusion.* Do the files this manifest names still hash to the digests it
   records? Real, falsifiable, and what every verifier in this repository
   implements: walk the manifest, hash each named path, compare.
2. *Membership.* Is every file inside the manifest's own declared scope named by
   it? Nothing implements this, and it is the half a reader assumes when a
   verifier prints ``publication manifest: PASS (547 files)``.

The two come apart the moment membership is decided by the artifact under
protection. P10's ``papers/orion-learning-machine/generate_publication_manifest.py``
declares four ``rglob`` roots and a suffix filter, emits a 547-line manifest, and
``VERIFY_LOCAL_CLOSURE.sh`` then iterates *the manifest*. Twenty files sit inside
those same roots and are named by no digest any gate dereferences --- among them
every experiment driver in the lane, the corrected Phase-1 runner whose committed
output the manifest does bind, and the Lean toolchain pin of the native corpus.
Rewriting any of them leaves the verifier at ``PASS (547 files)``;
appending a byte to a file the manifest *does* name reds it immediately. The
guard is real, its denominator is real and non-zero, and the denominator is an
output of the thing being guarded.

The failure class is recorded under
``research/failures/2026-08-self-scoped-manifest-unclosed-membership/``.

That is the distinction from
``research/failures/2026-08-unwatched-paper-content-silent-drift/``, where
:mod:`orion.programme.content_binding_coverage` reports the *absence* of a
binding. Here the binding is present, exercised and clean; what is missing is any
rule that adding a file to the tree adds an opportunity to the guard. That
module's :attr:`~orion.programme.content_binding_coverage.PaperBinding.unbound_files`
already reports the gap, but its verdict does not read it: a binding with one
bound file among five hundred assesses ``PASS``.

So membership is given its own exercise here, with the *declared scope* as the
denominator rather than the enrolled set, and the audit's verdict is the worse of
the two. A manifest cannot list its own digest, so an enforced manifest's own
path is exempt --- and only its own: a second copy of the same digests in another
file is decoration, not a binding.

The third state the module exists to name is a manifest nobody dereferences.
``SCRIPT_MANIFEST_SHA256.txt`` names 36 files, is itself bound by the publication
manifest, and is described in ``REPRODUCE.md`` as "a historical receipt". Ten of
its 36 digests already disagree with disk while every gate is green, which is the
measurement that settles it: a digest file no checker reads enrolls nothing, and
counting its entries as coverage is how twelve experiment files came to look
watched. :attr:`DigestBinding.dereferenced_by` is required and may be empty, and
an unenforced binding contributes no enrolment --- only a reported
:attr:`MembershipAudit.unenforced_drift`.

Scope-general on purpose. It knows nothing about P10, papers or publication; it
takes a declared scope, a set of digest bindings and the tree, and returns a
typed verdict.
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
from orion.programme.records import Outcome

DRIFT_GUARD_ID = "MANIFEST.CONTENT_DRIFT"
MEMBERSHIP_GUARD_ID = "MANIFEST.MEMBERSHIP_CLOSURE"

DRIFT_OPPORTUNITY = (
    "one file an enforced digest binding names; a file no enforced binding names "
    "cannot be observed to drift, so it offers the drift guard no opportunity"
)
MEMBERSHIP_OPPORTUNITY = (
    "one file inside the scope the manifest itself declares; a file present in "
    "that scope and named by no enforced binding is a file the binding was never "
    "asked about, and adding one does not add an opportunity"
)


class DigestAlgorithm(str, Enum):
    """How a binding addresses content.

    Two are in use here because P10's binding uses both: the publication manifest
    records ``sha256`` of the file bytes, and the V2 overlay records Git blob
    identity. They are different functions of the same bytes, so a binding must
    say which one it means before anything can recompute it.
    """

    SHA256 = "SHA256"
    GIT_BLOB_SHA1 = "GIT_BLOB_SHA1"

    @property
    def digest_length(self) -> int:
        return 64 if self is DigestAlgorithm.SHA256 else 40

    def digest(self, data: bytes) -> str:
        if self is DigestAlgorithm.SHA256:
            return hashlib.sha256(data).hexdigest()
        # Git's object identity is a hash of a typed, length-prefixed envelope,
        # not of the bytes. Recomputing it here rather than shelling out to
        # ``git hash-object`` keeps the audit runnable against a plain directory,
        # which is what makes it usable on an exported publication package.
        header = f"blob {len(data)}\0".encode()
        # sha1 is Git's identity function here, not a security choice.
        return hashlib.sha1(header + data).hexdigest()


def parse_digest_manifest(
    text: str,
    *,
    algorithm: DigestAlgorithm = DigestAlgorithm.SHA256,
    header_lines: int = 0,
) -> tuple[tuple[str, str], ...]:
    """Parse ``<digest>  <path>`` lines into ordered ``(path, digest)`` pairs.

    Raises rather than skipping a malformed line, for the reason
    ``content_binding_coverage.parse_sums`` does: a digest file that silently
    drops what it could not read binds fewer files than it appears to.

    ``header_lines`` is how many leading lines are an uncommented prose preamble
    --- P10's ``SCRIPT_MANIFEST_SHA256.txt`` opens with three. It has to be
    declared rather than inferred, because "skip anything that does not parse" is
    the behaviour this function exists to refuse.
    """

    rows: list[tuple[str, str]] = []
    for number, raw in enumerate(text.splitlines(), start=1):
        if number <= header_lines:
            continue
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        digest, separator, rest = line.partition("  ")
        if not separator or not rest.strip():
            raise ValueError(f"malformed digest line {number}: {raw!r}")
        if len(digest) != algorithm.digest_length or any(
            character not in "0123456789abcdef" for character in digest
        ):
            raise ValueError(
                f"line {number} does not carry a lowercase {algorithm.value}: {digest!r}"
            )
        rows.append((rest.strip(), digest))
    return tuple(rows)


@dataclass(frozen=True)
class DigestBinding:
    """One digest file, the paths it names, and whether any gate reads it.

    ``dereferenced_by`` names the checker that hashes the paths and compares. It
    is required and may be empty, and an empty value is a claim with a
    consequence: the binding enrolls nothing. A digest file that no gate opens is
    a transcript of a past state, and the repository cannot tell the two apart by
    looking at the file.
    """

    binding_id: str
    algorithm: DigestAlgorithm
    base_dir: Path
    manifest_path: Path
    entries: tuple[tuple[str, str], ...]
    dereferenced_by: str

    def __post_init__(self) -> None:
        if not self.binding_id.strip():
            raise ValueError("a digest binding requires an id")
        seen: set[str] = set()
        for relative, _ in self.entries:
            if relative in seen:
                raise ValueError(f"{self.binding_id}: {relative} is named twice")
            seen.add(relative)

    @property
    def enforced(self) -> bool:
        return bool(self.dereferenced_by.strip())

    @property
    def named_paths(self) -> tuple[Path, ...]:
        return tuple((self.base_dir / relative).resolve() for relative, _ in self.entries)

    def check(self) -> "BindingCheck":
        """Hash every named path on disk and compare against the recorded digest."""

        matched: list[str] = []
        drifted: list[str] = []
        missing: list[str] = []
        for relative, expected in self.entries:
            target = self.base_dir / relative
            if not target.is_file():
                missing.append(relative)
            elif self.algorithm.digest(target.read_bytes()) == expected:
                matched.append(relative)
            else:
                drifted.append(relative)
        return BindingCheck(
            binding_id=self.binding_id,
            enforced=self.enforced,
            dereferenced_by=self.dereferenced_by,
            named=len(self.entries),
            matched=tuple(matched),
            drifted=tuple(drifted),
            missing=tuple(missing),
        )


@dataclass(frozen=True)
class BindingCheck:
    """What one binding says about the tree right now."""

    binding_id: str
    enforced: bool
    dereferenced_by: str
    named: int
    matched: tuple[str, ...]
    drifted: tuple[str, ...]
    missing: tuple[str, ...]

    @property
    def violations(self) -> int:
        return len(self.drifted) + len(self.missing)

    def as_json(self) -> dict[str, object]:
        return {
            "binding_id": self.binding_id,
            "enforced": self.enforced,
            "dereferenced_by": self.dereferenced_by,
            "named": self.named,
            "matched": len(self.matched),
            "drifted": list(self.drifted),
            "missing": list(self.missing),
        }


@dataclass(frozen=True)
class ManifestScope:
    """The universe the manifest itself claims to cover.

    ``scope_definition`` is required and must be non-empty, for the reason
    ``GuardExercise.opportunity_definition`` is: a denominator nobody can state
    in a sentence is a denominator nobody can dispute. It should be traceable to
    the artifact --- the roots its own generator walks --- and not to the
    auditor's opinion of what ought to be covered.
    """

    scope_id: str
    scope_definition: str
    paths: frozenset[Path]

    def __post_init__(self) -> None:
        if not self.scope_id.strip():
            raise ValueError("a scope requires an id")
        if not self.scope_definition.strip():
            raise ValueError(
                f"{self.scope_id}: a scope definition is required; a watched set whose "
                "boundary cannot be stated cannot be checked for closure"
            )


@dataclass(frozen=True)
class MembershipAudit:
    """One scope, the bindings offered over it, and what each side actually covers."""

    scope: ManifestScope
    bindings: tuple[DigestBinding, ...]
    checks: tuple[BindingCheck, ...]

    def __post_init__(self) -> None:
        if not self.bindings:
            raise ValueError(
                f"{self.scope.scope_id}: an audit with no bindings is the unbound case "
                "content_binding_coverage already reports; it does not belong here"
            )

    @property
    def enrolled(self) -> frozenset[Path]:
        """Scope paths some enforced binding is responsible for.

        An enforced binding's own file is included: a manifest cannot record its
        own digest, and pretending otherwise would report a structural
        impossibility as a hole. Only the binding's own path earns this --- a
        second file repeating the same digests is not a binding, because nothing
        opens it.
        """

        covered: set[Path] = set()
        for binding in self.bindings:
            if not binding.enforced:
                continue
            covered.update(binding.named_paths)
            covered.add(binding.manifest_path.resolve())
        return frozenset(covered & self.scope.paths)

    @property
    def unenrolled(self) -> tuple[Path, ...]:
        return tuple(sorted(self.scope.paths - self.enrolled))

    @property
    def stale_only(self) -> tuple[Path, ...]:
        """Scope paths named *only* by a binding nothing dereferences.

        Separated out because these are the ones that read as covered. A file
        listed in a committed digest file looks bound to any reviewer who greps
        for its name, and the difference is invisible in the file itself.
        """

        unenforced: set[Path] = set()
        for binding in self.bindings:
            if not binding.enforced:
                unenforced.update(binding.named_paths)
        return tuple(sorted(unenforced & set(self.unenrolled)))

    @property
    def unenforced_drift(self) -> tuple[tuple[str, str], ...]:
        """``(binding_id, path)`` where an unread digest already disagrees with disk.

        This is the measurement that settles whether a digest file is a check.
        A binding whose digests have drifted while every gate is green was not
        being read by any of them.
        """

        return tuple(
            (check.binding_id, relative)
            for check in self.checks
            if not check.enforced
            for relative in check.drifted + check.missing
        )

    @property
    def enforced_violations(self) -> int:
        return sum(check.violations for check in self.checks if check.enforced)


def audit_membership(
    scope: ManifestScope, bindings: tuple[DigestBinding, ...]
) -> MembershipAudit:
    """Run every binding against the tree and pair the results with the scope."""

    return MembershipAudit(
        scope=scope,
        bindings=bindings,
        checks=tuple(binding.check() for binding in bindings),
    )


def drift_exercise(audit: MembershipAudit) -> GuardExercise:
    """The shipped verifier's question: do the enrolled files still match?"""

    return GuardExercise(
        guard_id=DRIFT_GUARD_ID,
        arm_id=audit.scope.scope_id,
        opportunities=len(audit.enrolled),
        violations=audit.enforced_violations,
        opportunity_definition=DRIFT_OPPORTUNITY,
    )


def membership_exercise(audit: MembershipAudit) -> GuardExercise:
    """The question nothing asks: is every file in scope enrolled at all?"""

    return GuardExercise(
        guard_id=MEMBERSHIP_GUARD_ID,
        arm_id=audit.scope.scope_id,
        opportunities=len(audit.scope.paths),
        violations=len(audit.unenrolled),
        opportunity_definition=MEMBERSHIP_OPPORTUNITY,
    )


def assess_drift(audit: MembershipAudit) -> GuardAssessment:
    return assess_guard(drift_exercise(audit))


def assess_membership(audit: MembershipAudit) -> GuardAssessment:
    return assess_guard(membership_exercise(audit))


def audit_outcome(audit: MembershipAudit) -> Outcome:
    """Non-compensatory. A clean drift result does not buy off an open membership.

    Assessing drift alone reports ``PASS`` on P10's tree --- 551 enrolled files,
    0 drifted --- and that pass would be exactly the substitution this module
    exists to refuse: intact bytes standing in for a watched set.
    """

    return worst_outcome((assess_drift(audit), assess_membership(audit)))


def audit_report(audit: MembershipAudit) -> dict[str, object]:
    """The machine-readable audit, denominator first."""

    drift = drift_exercise(audit)
    membership = membership_exercise(audit)
    return {
        "schema_version": "orion.programme.manifest-membership.v1",
        "outcome": audit_outcome(audit).value,
        "scope_id": audit.scope.scope_id,
        "scope_definition": audit.scope.scope_definition,
        "files_in_scope": len(audit.scope.paths),
        "files_enrolled": len(audit.enrolled),
        "files_unenrolled": len(audit.unenrolled),
        "files_stale_only": len(audit.stale_only),
        "unenrolled_paths": [str(path) for path in audit.unenrolled],
        "stale_only_paths": [str(path) for path in audit.stale_only],
        "unenforced_drift": [list(item) for item in audit.unenforced_drift],
        "drift_exercise": drift.as_json(),
        "membership_exercise": membership.as_json(),
        "drift_verdict": assess_drift(audit).as_json(),
        "membership_verdict": assess_membership(audit).as_json(),
        "drift_verdict_is_not_the_answer": (
            "a clean drift result is a statement about the files the manifest named; "
            "the audit outcome is the worse of the two verdicts, because the set of "
            "named files is chosen by the artifact the manifest protects"
        ),
        "bindings": [check.as_json() for check in audit.checks],
    }


class ManifestMembershipNotClosed(RuntimeError):
    """Raised when a file inside a manifest's own declared scope is enrolled nowhere."""


def require_closed_membership(audit: MembershipAudit) -> None:
    """Refuse to read the binding as complete while any scope file is unenrolled.

    Raises rather than returning a verdict for the reason
    ``content_binding_coverage.require_binding_coverage`` does: a boundary that
    answers ``False`` is indistinguishable from a negative result, and here the
    two mean opposite things.
    """

    if audit.enforced_violations:
        drifted = [
            f"{check.binding_id}:{relative}"
            for check in audit.checks
            if check.enforced
            for relative in check.drifted + check.missing
        ]
        raise ManifestMembershipNotClosed(
            f"{len(drifted)} enrolled file(s) no longer match their digests: "
            f"{', '.join(drifted[:5])}"
        )
    unenrolled = audit.unenrolled
    if unenrolled:
        names = ", ".join(path.name for path in unenrolled[:5])
        more = "" if len(unenrolled) <= 5 else f" (+{len(unenrolled) - 5} more)"
        raise ManifestMembershipNotClosed(
            f"{len(unenrolled)} of {len(audit.scope.paths)} files inside "
            f"{audit.scope.scope_id} are named by no enforced binding, so editing them "
            f"cannot be observed: {names}{more}"
        )


def render_audit(audit: MembershipAudit) -> str:
    """One human-readable block; the two denominators are the first thing shown."""

    report = audit_report(audit)
    lines = [
        f"{report['files_enrolled']}/{report['files_in_scope']} files in "
        f"{report['scope_id']} enrolled; {report['files_unenrolled']} unenrolled "
        f"({report['files_stale_only']} named only by an unread digest file)",
        f"  drift      {report['drift_verdict']['outcome']}",  # type: ignore[index]
        f"  membership {report['membership_verdict']['outcome']}",  # type: ignore[index]
    ]
    for check in audit.checks:
        state = check.dereferenced_by if check.enforced else "nothing dereferences it"
        lines.append(
            f"  {check.binding_id:<34} names {check.named:>4}  "
            f"drifted {len(check.drifted):>3}  missing {len(check.missing):>3}  [{state}]"
        )
    for path in audit.unenrolled:
        lines.append(f"    unenrolled  {path}")
    return "\n".join(lines)


def main(argv: Sequence[str]) -> int:
    """Report an audit built from a JSON registration. Exit 0 earned, 1 blocked, 3 empty.

    ``1`` covers both defects: enrolled bytes that drifted, and scope files no
    enforced binding names. Both are demonstrated --- the offending paths are
    listed --- so neither is the ``CANNOT_CHECK`` that ``3`` reports, which is
    reserved for a scope with nothing in it.

    ``argv`` is required rather than defaulting to ``sys.argv[1:]``. A zero-
    argument callable in this package is walked and invoked by
    ``tests/unit/programme/test_constitutional_boundary.py``; one that reads
    global state would parse the *test runner's* arguments and exit the
    interpreter, and ``SystemExit`` is not an ``Exception``, so it escapes that
    walker's guard.
    """

    import argparse

    parser = argparse.ArgumentParser(description="audit a digest manifest for membership closure")
    parser.add_argument(
        "registration",
        type=Path,
        help="JSON file naming the scope roots and the digest bindings over them",
    )
    parser.add_argument("--json", action="store_true", help="emit the machine-readable audit")
    arguments = parser.parse_args(argv)

    audit = audit_from_registration(json.loads(arguments.registration.read_text(encoding="utf-8")))
    print(json.dumps(audit_report(audit), indent=2, sort_keys=True) if arguments.json
          else render_audit(audit))

    outcome = audit_outcome(audit)
    if outcome is Outcome.PASS:
        return 0
    return 1 if outcome is Outcome.FAIL else 3


def audit_from_registration(registration: dict[str, object]) -> MembershipAudit:
    """Build an audit from a plain JSON registration, so a package can carry its own.

    Keeps the module usable outside this repository: an exported publication
    directory can ship the registration beside its manifests and be audited with
    no ORION-specific study module in the loop.
    """

    scope_roots = [Path(str(item)) for item in registration["scope_roots"]]  # type: ignore[union-attr]
    excluded = {str(item) for item in registration.get("excluded_dir_names", ())}
    excluded_suffixes = {str(item) for item in registration.get("excluded_suffixes", ())}
    paths = scope_paths(scope_roots, excluded_dir_names=excluded, excluded_suffixes=excluded_suffixes)
    scope = ManifestScope(
        scope_id=str(registration["scope_id"]),
        scope_definition=str(registration["scope_definition"]),
        paths=paths,
    )
    bindings = tuple(
        binding_from_manifest(
            binding_id=str(entry["binding_id"]),
            manifest_path=Path(str(entry["manifest_path"])),
            base_dir=Path(str(entry.get("base_dir", Path(str(entry["manifest_path"])).parent))),
            algorithm=DigestAlgorithm(str(entry.get("algorithm", DigestAlgorithm.SHA256.value))),
            dereferenced_by=str(entry.get("dereferenced_by", "")),
        )
        for entry in registration["bindings"]  # type: ignore[union-attr]
    )
    return audit_membership(scope, bindings)


def binding_from_manifest(
    *,
    binding_id: str,
    manifest_path: Path,
    base_dir: Path,
    algorithm: DigestAlgorithm = DigestAlgorithm.SHA256,
    dereferenced_by: str = "",
    header_lines: int = 0,
) -> DigestBinding:
    """Read a ``<digest>  <path>`` manifest off disk into a binding."""

    return DigestBinding(
        binding_id=binding_id,
        algorithm=algorithm,
        base_dir=base_dir,
        manifest_path=manifest_path,
        entries=parse_digest_manifest(
            manifest_path.read_text(encoding="utf-8"),
            algorithm=algorithm,
            header_lines=header_lines,
        ),
        dereferenced_by=dereferenced_by,
    )


def binding_from_mapping(
    *,
    binding_id: str,
    manifest_path: Path,
    base_dir: Path,
    entries: dict[str, str],
    algorithm: DigestAlgorithm,
    dereferenced_by: str = "",
) -> DigestBinding:
    """Build a binding from a ``{path: digest}`` mapping, e.g. a JSON overlay.

    P10's overlay is JSON rather than ``sha256sum`` format, and it addresses
    content by Git blob identity. Both are legitimate; what matters for closure
    is only which paths it makes someone responsible for.
    """

    for relative, digest in entries.items():
        if len(digest) != algorithm.digest_length or any(
            character not in "0123456789abcdef" for character in digest
        ):
            raise ValueError(
                f"{binding_id}: {relative} does not carry a lowercase "
                f"{algorithm.value}: {digest!r}"
            )
    return DigestBinding(
        binding_id=binding_id,
        algorithm=algorithm,
        base_dir=base_dir,
        manifest_path=manifest_path,
        entries=tuple(sorted(entries.items())),
        dereferenced_by=dereferenced_by,
    )


def scope_paths(
    roots: Sequence[Path],
    *,
    excluded_dir_names: frozenset[str] | set[str] = frozenset(),
    excluded_suffixes: frozenset[str] | set[str] = frozenset(),
) -> frozenset[Path]:
    """Every file under ``roots``, discovered by walking rather than by list.

    The discovery has to be a walk. A scope enumerated from a fixed list is the
    same defect one level up: it can only report on files somebody remembered to
    write down, which is precisely what the manifest already does.
    """

    found: set[Path] = set()
    for root in roots:
        if not root.is_dir():
            continue
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix in excluded_suffixes:
                continue
            if any(part in excluded_dir_names for part in path.parts):
                continue
            found.add(path.resolve())
    return frozenset(found)


__all__ = [
    "DRIFT_GUARD_ID",
    "DRIFT_OPPORTUNITY",
    "MEMBERSHIP_GUARD_ID",
    "MEMBERSHIP_OPPORTUNITY",
    "BindingCheck",
    "DigestAlgorithm",
    "DigestBinding",
    "ManifestMembershipNotClosed",
    "ManifestScope",
    "MembershipAudit",
    "assess_drift",
    "assess_membership",
    "audit_from_registration",
    "audit_membership",
    "audit_outcome",
    "audit_report",
    "binding_from_manifest",
    "binding_from_mapping",
    "drift_exercise",
    "main",
    "membership_exercise",
    "parse_digest_manifest",
    "render_audit",
    "require_closed_membership",
    "scope_paths",
]

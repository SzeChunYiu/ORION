#!/usr/bin/env python3
"""Bind each P6-P8 candidate package to its own bytes and to a subject commit (issue #347).

Before this checker the three candidate packages carried no content binding at
all: no digest, no manifest, no commit. P8's own `REPRODUCE.md` names its
reproduction subject as the branch `shadow/p6-p8-wide-sync-2026-08-17` and calls
it a "moving reference" -- a subject that cannot be re-fetched is not a subject.

This mirrors `research/paper-programme-v1/journal_package/check_journal_package.py`
for P1-P5: a manifest naming the package, a `SHA256SUMS` holding the digests, a
`--check` that fails on drift and a `--write` that regenerates. Three deliberate
departures from that checker:

* The binding artifacts sit at the candidate root, not in a `journal_package/`
  directory. `papers/candidates/README.md` forbids these candidates from reading
  as flagship identities, and a journal package is a submission claim.
* The hashed set is enumerated from the filesystem, not read back out of the
  manifest. `check_journal_package.py::hashed_paths` derives what to hash from
  `required_files`, so a file that is on disk but absent from the manifest is
  never hashed and the manifest can silently shrink its own coverage.
* Paths are repo-relative throughout. Each candidate's reproduction subject
  reaches outside its own directory -- into `papers/candidates/checkers/` and
  `tests/unit/candidates/` -- so a paper-root-relative convention could not
  express it.

The artifact binds bytes and nothing else. It does not tick a reproducibility
target, close a gate, or license an archive; `reproducibility_targets` records
which of issue #347's bullets remain `CANNOT_CHECK` and names the blocker for
each, so that a byte binding is not mistaken for the reproducibility work it is
merely a prerequisite for.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

# The exclusion rule lives in orion.programme.content_binding_coverage; this
# checker and that module must agree on what a bound file is, and when the rule
# was written out in both places they drifted as soon as LaTeX trees appeared.
from orion.programme.content_binding_coverage import is_build_artifact as _is_build_artifact
from typing import Any

SCHEMA_VERSION = "orion.candidate-content-binding.v1"
ISSUE = 347

CANDIDATES_DIR = Path("papers/candidates")
PAPERS_DIR = Path("papers")
MANIFEST_NAME = "CONTENT_MANIFEST_V1.json"
SUMS_NAME = "SHA256SUMS"

#: The normative package declaration. `CURRENT_PACKAGE_V2_1.md` states its own
#: supersession rule ("where an older V1/V2 artifact conflicts with a path named
#: here, this package is normative"), so roles are parsed from it rather than
#: restated here -- a second hand-maintained list would be free to disagree with
#: the normative one.
PACKAGE_DECLARATION = CANDIDATES_DIR / "CURRENT_PACKAGE_V2_1.md"

#: Directory names are long enough that inlining them breaks the 100-column
#: limit at almost every use site.
CANDIDATE_DIRS = {
    "P6": PAPERS_DIR / "orion-16-formal-epistemic-structures-and-mechanics",
    "P7": PAPERS_DIR / "orion-17-epistemic-navigation-open-worlds",
    "P8": PAPERS_DIR / "orion-18-epistemic-authority-autonomous-science",
}

# Successor artifacts are deliberately outside the frozen V1 package identity.
# Their exact set is not restated here: CONTENT_MANIFEST_V2 is the binding that
# owns it.  A new paper file is excluded from V1 only when V2 names it, so an
# unmanifested addition still turns this checker red instead of shrinking the
# old binding by convention.
SUCCESSOR_MANIFEST_NAME = "CONTENT_MANIFEST_V2.json"

#: Reproduction-subject files that live outside the candidate directory. Every
#: candidate's `REPRODUCE_V2_1.md` invokes the donor-envelope checker and the two
#: pytest wrappers; the per-candidate finite falsifier is named by the V1
#: `REPRODUCE.md` reproduction subject. `_unbound_reproduce_paths` re-derives
#: this from the prose on every run, so an added command cannot quietly widen the
#: subject past what is bound here. The programme-level documents are not listed:
#: they carry roles in the declaration's own `## Programme` section and are
#: picked up from there, so this tuple never disagrees with the normative doc.
SHARED_SUBJECT = (
    PACKAGE_DECLARATION,
    CANDIDATES_DIR / "CHECK_RESULTS_V2.md",
    CANDIDATES_DIR / "checkers" / "README.md",
    CANDIDATES_DIR / "checkers" / "check_donor_complete_envelope_v1.py",
    Path("tests/unit/candidates/test_p6_p8_candidate_embedding.py"),
    Path("tests/unit/candidates/test_p6_p8_theory_closure_v21.py"),
    Path("tests/unit/candidates/test_p6_p8_merged_review_suites.py"),
)

#: Heading of the declaration section holding artifacts shared by all three
#: candidates rather than owned by one.
PROGRAMME_SECTION = "PROGRAMME"
FALSIFIERS = {
    candidate_id: CANDIDATES_DIR / "checkers" / f"{candidate_id.lower()}_finite_falsifiers_v1.py"
    for candidate_id in CANDIDATE_DIRS
}

#: Files one candidate owns that live outside its own directory.
#:
#: `SHARED_SUBJECT` is the wrong home for these: everything in it is bound into all
#: three packages, so putting a P8-only test there would bind it into P6 and P7 and
#: make their manifests claim a subject they do not have.
#:
#: P8's `REPRODUCE` prose tells a reader to run `test_p8_formal_core_primitives.py`,
#: which lives under `tests/unit/candidates/` because that is where the suite
#: collects from. Naming a file in reproduction instructions without binding it means
#: the file can change while the binding still verifies -- the reader runs something
#: other than what was bound, and nothing says so. The checker caught exactly that.
#: P6 is the same case, and it arrived the same way. Its `REPRODUCE` prose names
#: `test_p6_formal_refutation_capacity.py`, the suite that pins the refutation
#: capacity its two repaired checkers gained; the checker refused the manifest
#: until the file it tells a reader to run was bound.
CANDIDATE_SUBJECT: dict[str, tuple[Path, ...]] = {
    "P6": (Path("tests/unit/candidates/test_p6_formal_refutation_capacity.py"),),
    "P8": (Path("tests/unit/candidates/test_p8_formal_core_primitives.py"),),
}

CLAIM_SCOPE = (
    "Binds the bytes of one candidate package and names the commit they were "
    "read at. Not a readiness verdict, not novelty or claim authority, and not "
    "permission to deposit a permanent archive."
)

#: Issue #347's per-paper reproducibility targets, in the order the issue lists
#: them. Only the first is settled by a byte binding; the rest name what is
#: actually missing, because "no manifest exists" and "the manifest says the
#: artifact is absent" are different states and only the second is auditable.
COMMON_TARGETS: tuple[tuple[str, str, str | None], ...] = (
    (
        "exact_subject_commit_identities",
        "BOUND",
        None,
    ),
    (
        "versioned_protocol_generator_schemas",
        "CANNOT_CHECK",
        "Benchmark instances are committed as data with no versioned generator "
        "schema; nothing declares the shape they must conform to.",
    ),
    (
        "immutable_raw_result_formats",
        "CANNOT_CHECK",
        "The formal checkers emit prose on stdout and write no result file, so "
        "there are no result bytes for this manifest to bind.",
    ),
    (
        "one_command_regeneration_from_raw",
        "CANNOT_CHECK",
        "Blocked on immutable_raw_result_formats: with no raw artifact committed "
        "there is nothing to regenerate a table or figure from.",
    ),
    (
        "clean_environment_reproduction_instructions",
        "CANNOT_CHECK",
        "REPRODUCE_V2_1.md gives commands but no lockfile, image digest or "
        "pinned interpreter; the environment exists only as prose.",
    ),
    (
        "dependency_model_provider_tool_versions",
        "CANNOT_CHECK",
        "REPRODUCE.md records one observed interpreter and kernel string from a "
        "single machine; no machine-readable dependency pin is committed.",
    ),
    (
        "negative_null_history_retained",
        "CANNOT_CHECK",
        "Superseded V1/V2 documents are retained in the tree and bound here, but "
        "retaining superseded prose is not retaining negative or null results; "
        "no null-result record is committed.",
    ),
    (
        "independent_replay_attestation",
        "CANNOT_CHECK",
        "No ScientificResultVerification.v1 record under "
        "research/verification/records names a candidate (issue #283).",
    ),
    (
        "permanent_archive_after_authority_stabilizes",
        "CANNOT_CHECK",
        "Candidate authority is PROPOSED/CANNOT_CHECK. No DOI or deposit exists, "
        "and this manifest does not license one.",
    ),
)

#: The issue's paper-specific tail: "P6 additionally needs proof/checker
#: reproducibility; P7 needs benchmark generator and navigation-trace replay; P8
#: needs protected authority labels/custody and cross-capability attack replay."
CANDIDATE_TARGETS: dict[str, tuple[tuple[str, str, str | None], ...]] = {
    "P6": (
        (
            "proof_and_checker_reproducibility",
            "CANNOT_CHECK",
            "The checker sources are bound byte-for-byte, but they are finite "
            "hand-built fixtures; no machine-checked proof object is committed.",
        ),
    ),
    "P7": (
        (
            "benchmark_generator_and_trace_replay",
            "CANNOT_CHECK",
            "benchmark/instances_v2.jsonl is committed without the generator "
            "that produced it, and no navigation trace is committed to replay.",
        ),
    ),
    "P8": (
        (
            "protected_labels_custody_and_attack_replay",
            "CANNOT_CHECK",
            "Issue #341 requires labels the candidate cannot write. Every "
            "authority case and its expected terminal is in the public tree, so "
            "custody separation does not exist to be bound.",
        ),
    ),
}

#: Repo-relative path tokens inside a `REPRODUCE_*.md` command block. Extensions
#: are required so that `PYTHONPATH=src` and bare directory names do not read as
#: files that ought to be bound.
REPRODUCE_PATH = re.compile(r"\b((?:papers|tests|src|research)/[\w./-]+\.(?:py|md|jsonl|json))\b")
ROLE_LINE = re.compile(r"^-\s+(?P<role>[^:]+):\s+`(?P<path>[^`]+)`\s*$")
SECTION_LINE = re.compile(r"^##\s+(?P<name>.+?)\s*$")
HEX = set("0123456789abcdef")


class BindingReport:
    """Errors and CANNOT_CHECK outcomes for one candidate, kept apart.

    A blocker that prevented a check is not a check that passed, and it is not a
    check that failed either; collapsing the three is how "could not verify"
    gets recorded as "verified".
    """

    def __init__(self, candidate_id: str) -> None:
        self.candidate_id = candidate_id
        self.errors: list[str] = []
        self.cannot_check: list[str] = []
        self.notes: list[str] = []

    @property
    def ok(self) -> bool:
        return not self.errors

    def as_dict(self) -> dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "ok": self.ok,
            "errors": self.errors,
            "cannot_check": self.cannot_check,
            "notes": self.notes,
        }


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _is_sha(value: str, length: int) -> bool:
    return len(value) == length and all(ch in HEX for ch in value.lower())


def parse_package_declaration(repo_root: Path) -> dict[str, dict[str, str]]:
    """Map section -> {repo-relative path: role} from the normative package doc.

    Sections are the three candidate ids plus `PROGRAMME`, whose artifacts are
    normative for all three. Paths in the declaration are written relative to
    `papers/candidates/`, except the CI wrappers under `tests/`, which are
    already repo-relative.
    """

    text = (repo_root / PACKAGE_DECLARATION).read_text(encoding="utf-8")
    roles: dict[str, dict[str, str]] = {key: {} for key in (*CANDIDATE_DIRS, PROGRAMME_SECTION)}
    section: str | None = None
    for raw in text.splitlines():
        heading = SECTION_LINE.match(raw)
        if heading:
            first = heading.group("name").split()[0]
            section = first.upper() if first.upper() in roles else None
            continue
        entry = ROLE_LINE.match(raw)
        if not entry or section is None:
            continue
        relative = entry.group("path")
        # The document writes paths relative to papers/candidates/, except the CI
        # wrappers under tests/. The paper packages themselves now live directly
        # under papers/, so a declaration entry that no longer resolves under
        # papers/candidates/ is retried there before falling back to the
        # repo-relative form. A path that resolves no way at all is reported in
        # the declaration's own convention so the gap message names what a reader
        # would go looking for.
        resolved = CANDIDATES_DIR / relative
        if not (repo_root / resolved).is_file():
            for alternative in (PAPERS_DIR / relative, Path(relative)):
                if (repo_root / alternative).is_file():
                    resolved = alternative
                    break
        roles[section][resolved.as_posix()] = entry.group("role").strip()
    return roles


def successor_v2_paths(repo_root: Path, candidate_id: str) -> set[str]:
    """Paths added after V1 that the content-bound V2 successor owns.

    V2 may also re-bind old V1 paths so current checkers have one complete,
    commit-addressed view.  Only the V2-minus-V1 difference is excluded from
    V1's historical enumeration; otherwise re-binding an old path in V2 would
    silently delete it from the frozen V1 subject.
    """

    directory = repo_root / CANDIDATE_DIRS[candidate_id]
    v1_path = directory / MANIFEST_NAME
    v2_path = directory / SUCCESSOR_MANIFEST_NAME
    successor = {(CANDIDATE_DIRS[candidate_id] / SUCCESSOR_MANIFEST_NAME).as_posix()}
    try:
        v1 = json.loads(v1_path.read_text(encoding="utf-8"))
        v2 = json.loads(v2_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return successor
    if not isinstance(v1, dict) or not isinstance(v2, dict):
        return successor
    if (
        v2.get("schema_version") != "orion.candidate-content-binding.v2"
        or v2.get("candidate_id") != candidate_id
    ):
        return successor
    v1_bound = {
        str(entry["path"])
        for entry in v1.get("bound_files", ())
        if isinstance(entry, dict) and isinstance(entry.get("path"), str)
    }
    v2_bound = {
        str(entry["path"])
        for entry in v2.get("bound_files", ())
        if isinstance(entry, dict) and isinstance(entry.get("path"), str)
    }
    return successor | (v2_bound - v1_bound)



def bound_paths(repo_root: Path, candidate_id: str) -> list[str]:
    """Every file this manifest binds, repo-relative and sorted.

    `SHA256SUMS` is excluded because it cannot hold its own digest. The manifest
    is *not* excluded: writing it first and hashing it second is what lets the
    digest file bind the manifest's bytes, which is how P1-P5 do it.
    """

    directory = repo_root / CANDIDATE_DIRS[candidate_id]
    successor_paths = successor_v2_paths(repo_root, candidate_id)
    paths = {
        path.relative_to(repo_root).as_posix()
        for path in directory.rglob("*")
        if path.is_file()
        and path.name != SUMS_NAME
        and not _is_build_artifact(path)
        and path.relative_to(repo_root).as_posix() not in successor_paths
    }
    # Listed unconditionally: on a first `--write` the manifest does not exist
    # yet, and enumerating only what is on disk would omit it from its own set,
    # so the next `--check` would report drift against a tree nobody touched.
    paths.add((CANDIDATE_DIRS[candidate_id] / MANIFEST_NAME).as_posix())
    for shared in (
        *SHARED_SUBJECT,
        FALSIFIERS[candidate_id],
        *CANDIDATE_SUBJECT.get(candidate_id, ()),
    ):
        if (repo_root / shared).is_file():
            paths.add(shared.as_posix())
    programme = parse_package_declaration(repo_root)[PROGRAMME_SECTION]
    paths.update(path for path in programme if (repo_root / path).is_file())
    return sorted(paths)


def _subject_paths(paths: list[str]) -> list[str]:
    """Bound paths minus the manifest, which `--write` rewrites by construction.

    Including it would make every generation report its own commit as unbound.
    `SHA256SUMS` is already absent from `paths` for the same kind of reason.
    """

    return [path for path in paths if not path.endswith(f"/{MANIFEST_NAME}")]


def commit_disagreement(repo_root: Path, commit: str, paths: list[str]) -> list[str] | None:
    """Bound subject paths whose bytes differ from `commit`; `None` if git cannot say.

    Asked against the *recorded* commit rather than HEAD. Against HEAD the answer
    would change on every unrelated commit; against the recorded commit it only
    changes when a bound file does, which is the question the field claims to
    answer.
    """

    subject = _subject_paths(paths)
    try:
        modified = subprocess.run(
            ["git", "-C", str(repo_root), "diff", "--name-only", commit, "--", *subject],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.split()
        untracked = subprocess.run(
            ["git", "-C", str(repo_root), "ls-files", "--others", "--exclude-standard", "--", *subject],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.split()
    except (OSError, subprocess.CalledProcessError):
        return None
    return sorted(set(modified) | set(untracked))


def _subject_commit(repo_root: Path, paths: list[str]) -> dict[str, Any]:
    """HEAD, plus whether the bound subject actually matched it when read."""

    try:
        head = subprocess.run(
            ["git", "-C", str(repo_root), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        return {
            "subject_commit": None,
            "subject_commit_status": "CANNOT_CHECK",
            "subject_commit_blocker": f"git metadata unavailable: {exc}",
            "subject_commit_unbound_paths": [],
        }
    drifted = commit_disagreement(repo_root, head, paths) or []
    if drifted:
        return {
            "subject_commit": head,
            "subject_commit_status": "CANNOT_CHECK",
            "subject_commit_blocker": (
                "bound files differ from the recorded commit; the commit does not "
                "describe these bytes"
            ),
            "subject_commit_unbound_paths": drifted,
        }
    return {
        "subject_commit": head,
        "subject_commit_status": "BOUND",
        "subject_commit_blocker": None,
        "subject_commit_unbound_paths": [],
    }


def reproducibility_targets(candidate_id: str) -> dict[str, dict[str, Any]]:
    entries = (*COMMON_TARGETS, *CANDIDATE_TARGETS[candidate_id])
    return {
        name: {"status": status, "blocker": blocker} for name, status, blocker in entries
    }


def declaration_gaps(repo_root: Path, candidate_id: str) -> list[str]:
    """Paths the normative package declares that are not on disk.

    A named-but-absent artifact is the normative document drifting away from the
    tree it describes. Silently skipping it would let the manifest look complete
    while binding a package that no longer has the file it is defined by.
    """

    declaration = parse_package_declaration(repo_root)
    declared = {**declaration[PROGRAMME_SECTION], **declaration[candidate_id]}
    return sorted(path for path in declared if not (repo_root / path).is_file())


def derive_manifest(repo_root: Path, candidate_id: str) -> dict[str, Any]:
    paths = bound_paths(repo_root, candidate_id)
    declaration = parse_package_declaration(repo_root)
    roles = {**declaration[PROGRAMME_SECTION], **declaration[candidate_id]}
    # V1 role labels are part of the frozen historical declaration. A later
    # package document may add a role for the same path, but that does not
    # retroactively rewrite V1; V2 owns the current binding surface.
    try:
        frozen = json.loads(
            (repo_root / CANDIDATE_DIRS[candidate_id] / MANIFEST_NAME).read_text(
                encoding="utf-8"
            )
        )
    except (OSError, json.JSONDecodeError):
        frozen = {}
    frozen_roles = {
        str(entry["path"]): entry.get("role")
        for entry in frozen.get("bound_files", ())
        if isinstance(entry, dict) and isinstance(entry.get("path"), str)
    }
    return {
        "schema_version": SCHEMA_VERSION,
        "candidate_id": candidate_id,
        "issue": ISSUE,
        "grants_authority": "NONE",
        "closes_gate": None,
        "claim_scope": CLAIM_SCOPE,
        **_subject_commit(repo_root, paths),
        "digest_file": (CANDIDATE_DIRS[candidate_id] / SUMS_NAME).as_posix(),
        "bound_files": [
            {"path": path, "role": frozen_roles.get(path, roles.get(path))} for path in paths
        ],
        "reproducibility_targets": reproducibility_targets(candidate_id),
    }


def _dumps(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def parse_sha256sums(path: Path) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        digest, _, rest = line.partition("  ")
        if not rest or not _is_sha(digest, 64):
            raise ValueError(f"malformed SHA256SUMS line: {raw!r}")
        mapping[rest] = digest.lower()
    return mapping


def write_binding(repo_root: Path, candidate_id: str) -> tuple[Path, Path]:
    directory = repo_root / CANDIDATE_DIRS[candidate_id]
    manifest_path = directory / MANIFEST_NAME
    sums_path = directory / SUMS_NAME
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"frozen {MANIFEST_NAME} is unavailable or unreadable") from exc
    derived = derive_manifest(repo_root, candidate_id)
    provenance = {
        "subject_commit",
        "subject_commit_status",
        "subject_commit_blocker",
        "subject_commit_unbound_paths",
    }
    if {key: value for key, value in manifest.items() if key not in provenance} != {
        key: value for key, value in derived.items() if key not in provenance
    }:
        raise ValueError(
            f"frozen {MANIFEST_NAME} no longer describes the V1 subject; "
            "bind additive files in CONTENT_MANIFEST_V2.json"
        )
    # V1 is historical and must not be rewritten merely because HEAD moved.
    # SHA256SUMS remains the live digest layer for the paths V1 declared.
    lines = [
        f"{sha256_file(repo_root / entry['path'])}  {entry['path']}"
        for entry in manifest["bound_files"]
    ]
    sums_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return manifest_path, sums_path


def _unbound_reproduce_paths(repo_root: Path, candidate_id: str, bound: set[str]) -> list[str]:
    """Paths a candidate's REPRODUCE prose invokes that this manifest does not bind.

    A reproduction subject that grows by one command is a subject that stopped
    being described by its manifest, and nothing else would notice.
    """

    directory = repo_root / CANDIDATE_DIRS[candidate_id]
    unbound: set[str] = set()
    for doc in sorted(directory.glob("REPRODUCE*.md")):
        for match in REPRODUCE_PATH.finditer(doc.read_text(encoding="utf-8")):
            path = match.group(1)
            if path not in bound and (repo_root / path).is_file():
                unbound.add(path)
    return sorted(unbound)


def check_binding(repo_root: Path, candidate_id: str) -> BindingReport:
    report = BindingReport(candidate_id)
    directory = repo_root / CANDIDATE_DIRS[candidate_id]
    manifest_path = directory / MANIFEST_NAME
    sums_path = directory / SUMS_NAME

    for path in (manifest_path, sums_path):
        if not path.is_file():
            report.errors.append(f"binding artifact missing: {path.relative_to(repo_root)}")
    if report.errors:
        return report

    try:
        committed = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        report.errors.append(f"{MANIFEST_NAME} unreadable: {exc}")
        return report
    if not isinstance(committed, dict):
        report.errors.append(f"{MANIFEST_NAME} must contain one JSON object")
        return report

    derived = derive_manifest(repo_root, candidate_id)

    # `subject_commit` and its status are generation provenance: HEAD moves on
    # every commit, so comparing them would red-line every commit that did not
    # regenerate the manifest. Byte authority comes from the digests below.
    # This follows papers/orion-11-.../scripts/make_mechanical_arm_case_table.py.
    provenance = {"subject_commit", "subject_commit_status", "subject_commit_blocker",
                  "subject_commit_unbound_paths"}
    for key in sorted(set(derived) - provenance):
        if committed.get(key) != derived[key]:
            report.errors.append(f"{key} drifted from the derived value")

    recorded_commit = committed.get("subject_commit")
    if recorded_commit is None:
        report.cannot_check.append(
            "subject_commit is null; the package is not bound to any commit identity"
        )
    elif not isinstance(recorded_commit, str) or not _is_sha(recorded_commit, 40):
        report.errors.append("subject_commit must be a 40-character git SHA or null")
    elif not _commit_exists(repo_root, recorded_commit):
        report.cannot_check.append(
            f"subject_commit {recorded_commit} is not in this object database "
            "(shallow clone or export); commit identity cannot be resolved here"
        )
    elif committed.get("subject_commit_status") == "BOUND":
        # The recorded status is a claim about bytes-versus-commit, so it has to
        # be re-asked rather than trusted; a status field nothing re-evaluates is
        # a claim that silently stops being true. Asked against the recorded
        # commit, so an unrelated later commit cannot falsify it.
        # Compared against the same set `--write` pinned. `_subject_commit` derives
        # the pin over `_subject_paths`, which drops the manifest because a manifest
        # that recorded its own commit would report itself unbound on every
        # generation. Asking `--check` over the unfiltered list asks a different
        # question than the write answered, and the manifest is then permanently
        # drifted: recording a subject_commit edits it, so its bytes cannot equal
        # any commit that already exists. The manifest stays in `bound_files` and
        # stays covered by `SHA256SUMS`, which is what pins its bytes.
        drifted = commit_disagreement(
            repo_root,
            recorded_commit,
            _subject_paths([str(entry["path"]) for entry in derived["bound_files"]]),
        )
        if drifted is None:
            report.cannot_check.append("git cannot compare the tree to subject_commit here")
        elif drifted:
            report.errors.append(
                f"subject_commit_status claims BOUND but these differ from "
                f"{recorded_commit}: " + ", ".join(drifted)
            )
    if committed.get("subject_commit_status") == "CANNOT_CHECK":
        report.cannot_check.append(
            "recorded subject_commit_status is CANNOT_CHECK: "
            + str(committed.get("subject_commit_blocker"))
        )

    try:
        sums = parse_sha256sums(sums_path)
    except (OSError, ValueError) as exc:
        report.errors.append(str(exc))
        return report

    expected = [str(entry["path"]) for entry in derived["bound_files"]]
    missing = sorted(set(expected) - set(sums))
    extra = sorted(set(sums) - set(expected))
    if missing:
        report.errors.append(f"{SUMS_NAME} does not cover: " + ", ".join(missing))
    if extra:
        report.errors.append(f"{SUMS_NAME} names paths that are not bound: " + ", ".join(extra))
    for path in expected:
        target = repo_root / path
        if not target.is_file():
            report.errors.append(f"bound file has disappeared: {path}")
            continue
        digest = sums.get(path)
        if digest is not None and digest != sha256_file(target):
            report.errors.append(f"hash mismatch for {path}")

    unbound = _unbound_reproduce_paths(repo_root, candidate_id, set(expected))
    if unbound:
        report.errors.append(
            "REPRODUCE prose invokes files this manifest does not bind: " + ", ".join(unbound)
        )
    gaps = declaration_gaps(repo_root, candidate_id)
    if gaps:
        report.errors.append(
            f"{PACKAGE_DECLARATION.as_posix()} names artifacts that are not on disk: "
            + ", ".join(gaps)
        )
    return report


def _commit_exists(repo_root: Path, commit: str) -> bool:
    try:
        subprocess.run(
            ["git", "-C", str(repo_root), "cat-file", "-e", f"{commit}^{{commit}}"],
            capture_output=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return False
    return True


def check_repository(repo_root: Path) -> list[BindingReport]:
    return [check_binding(repo_root, candidate_id) for candidate_id in sorted(CANDIDATE_DIRS)]


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--check",
        action="store_true",
        help="validate committed manifests and digests against the tree",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help=f"regenerate {MANIFEST_NAME} and {SUMS_NAME} for every candidate",
    )
    return parser


def main() -> int:
    args = _parser().parse_args()
    root = args.root.resolve()

    if args.write:
        for candidate_id in sorted(CANDIDATE_DIRS):
            manifest_path, sums_path = write_binding(root, candidate_id)
            print(f"wrote {manifest_path.relative_to(root)}")
            print(f"wrote {sums_path.relative_to(root)}")
        return 0

    reports = check_repository(root)
    if not args.check:
        print(_dumps([derive_manifest(root, cid) for cid in sorted(CANDIDATE_DIRS)]), end="")
        return 0

    for report in reports:
        for error in report.errors:
            print(f"{report.candidate_id}: {error}", file=sys.stderr)
    failed = [report.candidate_id for report in reports if not report.ok]
    if failed:
        print(f"P6-P8 CANDIDATE CONTENT BINDING: FAIL ({', '.join(failed)})", file=sys.stderr)
        return 1

    print("P6-P8 CANDIDATE CONTENT BINDING: PASS")
    for report in reports:
        bound = len(parse_sha256sums(root / CANDIDATE_DIRS[report.candidate_id] / SUMS_NAME))
        print(f"  {report.candidate_id}: {bound} files bound")
        for blocker in report.cannot_check:
            print(f"    CANNOT_CHECK: {blocker}")
    unbound_targets = sorted(
        {
            name
            for candidate_id in CANDIDATE_DIRS
            for name, target in reproducibility_targets(candidate_id).items()
            if target["status"] == "CANNOT_CHECK"
        }
    )
    print(f"  issue #{ISSUE} targets still CANNOT_CHECK: {len(unbound_targets)}")
    for name in unbound_targets:
        print(f"    CANNOT_CHECK: {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

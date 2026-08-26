"""Registration of P10's shipped publication binding, read off the repository.

P10 is one of four paper lanes in this repository that carries a real content
binding, and the only one with two digest algorithms and three digest files. This
module registers them as they ship --- it derives nothing and re-implements
nothing --- so :mod:`orion.programme.manifest_membership` can be asked the
question the shipped verifiers do not: is the watched set closed against the tree
the manifest itself declares?

The three digest files, and what actually reads each:

``PUBLICATION_MANIFEST_SHA256.txt``
    547 sha256 rows. Dereferenced by ``VERIFY_LOCAL_CLOSURE.sh`` (run from
    ``tests/unit/candidates/test_p9_p10_learning_machine.py``) and, for all but
    five rows, by ``VERIFY_LOCAL_CLOSURE_V2.sh`` in both CI workflows.

``P10_PUBLICATION_OVERLAY_V2.json``
    9 Git blob ids, five of which restate paths the sha256 manifest already
    binds. Dereferenced by ``VERIFY_LOCAL_CLOSURE_V2.sh``.

``SCRIPT_MANIFEST_SHA256.txt``
    36 sha256 rows covering the experiment drivers. ``REPRODUCE.md`` calls it "a
    historical receipt for the 36 files as delivered at commit ``bbe178d``", and
    no script or test hashes a single path it names. It is registered here with
    an empty ``dereferenced_by`` and the audit reports the consequence rather
    than asserting it: ten of its thirty-six digests already disagree with disk
    while every gate is green.

The scope is the four ``rglob`` roots that
``papers/orion-learning-machine/generate_publication_manifest.py`` walks, plus
the lane root itself, which that generator also draws eight individual files
from. Those roots are transcribed here and re-checked against the shipped
generator by :func:`shipped_generator_enrolment`, so a root added there and not
here reds rather than silently narrowing the denominator.

What is *not* the scope: the generator's suffix filter. Which suffixes a manifest
chooses to bind is precisely the membership decision under audit, so excluding
``lean-toolchain`` and ``lean_readlink_self.c`` from the denominator because the
manifest excluded them would make the measurement agree with the artifact by
construction. Only build output is dropped, on the same identity grounds
``content_binding_coverage`` drops it: a ``.pyc`` filename carries the
interpreter that produced it, so binding one fails on machine identity rather
than on content.
"""

from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path

from orion.programme.manifest_membership import (
    DigestAlgorithm,
    DigestBinding,
    ManifestScope,
    MembershipAudit,
    audit_membership,
    binding_from_manifest,
    binding_from_mapping,
    scope_paths,
)

LANE = "papers/orion-learning-machine"
PUBLICATION_MANIFEST = "PUBLICATION_MANIFEST_SHA256.txt"
SCRIPT_MANIFEST = "SCRIPT_MANIFEST_SHA256.txt"
OVERLAY = "P10_PUBLICATION_OVERLAY_V2.json"
GENERATOR = "generate_publication_manifest.py"

SCOPE_ID = "P10_PUBLICATION_UNIVERSE"
SCOPE_DEFINITION = (
    "every file under the roots generate_publication_manifest.py walks --- the "
    "lane's framework/ and results/, the two paper-xx- predecessor packages, and "
    "the lane root it draws eight named files from --- excluding build output, "
    "whose filenames carry the interpreter that produced them"
)

#: The roots the shipped generator declares, transcribed. Kept as a tuple of
#: repository-relative strings rather than as a call into the generator because
#: the roots are locals inside ``included_files()``; :func:`shipped_generator_enrolment`
#: is what stops the transcription drifting.
SCOPE_ROOTS: tuple[str, ...] = (
    f"{LANE}/framework",
    f"{LANE}/results",
    "papers/paper-xx-executable-research-core",
    "papers/archive/2026-08-pre-unification/paper-xx-content-bound-math-evaluation",
    LANE,
)

#: Bytecode and tool caches. Same exclusion, and the same reason, as
#: ``content_binding_coverage``: these are outputs of a machine, not of a lane.
EXCLUDED_DIR_NAMES = frozenset({"__pycache__", ".pytest_cache", ".ruff_cache", ".mypy_cache"})
EXCLUDED_SUFFIXES = frozenset({".pyc", ".pyo", ".pyd"})

PUBLICATION_DEREFERENCED_BY = (
    "VERIFY_LOCAL_CLOSURE.sh; VERIFY_LOCAL_CLOSURE_V2.sh (all rows but the five "
    "the overlay supersedes); tests/unit/candidates/test_p9_p10_learning_machine.py"
)
OVERLAY_DEREFERENCED_BY = (
    "VERIFY_LOCAL_CLOSURE_V2.sh, run by p9-p10-publication-closure.yml and "
    "p10-publication-overlay-v2.yml"
)
#: Empty on purpose, and the claim the audit then measures. ``REPRODUCE.md``
#: calls this file a historical receipt; nothing in the repository hashes a path
#: it names.
SCRIPT_MANIFEST_DEREFERENCED_BY = ""

#: The three prose lines that open ``SCRIPT_MANIFEST_SHA256.txt`` before its rows.
SCRIPT_MANIFEST_HEADER_LINES = 3


def lane_dir(repo_root: Path) -> Path:
    return repo_root / LANE


def declared_scope(repo_root: Path) -> ManifestScope:
    """The universe the shipped generator's own roots describe."""

    return ManifestScope(
        scope_id=SCOPE_ID,
        scope_definition=SCOPE_DEFINITION,
        paths=scope_paths(
            [repo_root / root for root in SCOPE_ROOTS],
            excluded_dir_names=EXCLUDED_DIR_NAMES,
            excluded_suffixes=EXCLUDED_SUFFIXES,
        ),
    )


def publication_binding(repo_root: Path) -> DigestBinding:
    lane = lane_dir(repo_root)
    return binding_from_manifest(
        binding_id=PUBLICATION_MANIFEST,
        manifest_path=lane / PUBLICATION_MANIFEST,
        base_dir=lane,
        algorithm=DigestAlgorithm.SHA256,
        dereferenced_by=PUBLICATION_DEREFERENCED_BY,
    )


def overlay_binding(repo_root: Path) -> DigestBinding:
    lane = lane_dir(repo_root)
    overlay = json.loads((lane / OVERLAY).read_text(encoding="utf-8"))
    return binding_from_mapping(
        binding_id=OVERLAY,
        manifest_path=lane / OVERLAY,
        # The overlay's keys are rooted at papers/, not at the lane, which is why
        # VERIFY_LOCAL_CLOSURE_V2.sh has to rewrite the legacy manifest's
        # ``../paper-xx-...`` prefix before it can compare the two.
        base_dir=repo_root / "papers",
        entries=dict(overlay["paths"]),
        algorithm=DigestAlgorithm.GIT_BLOB_SHA1,
        dereferenced_by=OVERLAY_DEREFERENCED_BY,
    )


def script_manifest_binding(repo_root: Path) -> DigestBinding:
    lane = lane_dir(repo_root)
    return binding_from_manifest(
        binding_id=SCRIPT_MANIFEST,
        manifest_path=lane / SCRIPT_MANIFEST,
        base_dir=lane,
        algorithm=DigestAlgorithm.SHA256,
        dereferenced_by=SCRIPT_MANIFEST_DEREFERENCED_BY,
        header_lines=SCRIPT_MANIFEST_HEADER_LINES,
    )


def shipped_bindings(repo_root: Path) -> tuple[DigestBinding, ...]:
    """All three digest files the lane ships, in the order a reader meets them."""

    return (
        publication_binding(repo_root),
        overlay_binding(repo_root),
        script_manifest_binding(repo_root),
    )


def audit_p10_publication(repo_root: Path) -> MembershipAudit:
    """The audit, against the files on disk."""

    return audit_membership(declared_scope(repo_root), shipped_bindings(repo_root))


def shipped_generator_enrolment(repo_root: Path) -> frozenset[Path]:
    """What ``generate_publication_manifest.included_files()`` would enroll today.

    Loads the shipped generator and calls the enrolment function only. ``main()``
    is never called: it rewrites ``PUBLICATION_MANIFEST_SHA256.txt``, and an
    auditor that regenerates the artifact it audits is measuring itself.

    Pointing at the shipped module rather than at a transcription is the property
    ``research/failures/2026-08-unconditional-terminal-self-issued-authority/``
    asks for: an instrument that only ever runs against its own fixture is the
    failure it was written to catch.
    """

    generator = lane_dir(repo_root) / GENERATOR
    spec = importlib.util.spec_from_file_location("orion_p10_publication_generator", generator)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load the shipped generator at {generator}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return frozenset(path.resolve() for path in module.included_files())


def committed_publication_paths(repo_root: Path) -> frozenset[Path]:
    """The paths the committed sha256 manifest names, resolved against the lane."""

    return frozenset(publication_binding(repo_root).named_paths)


def manifest_entry_origin(repo_root: Path) -> dict[str, int]:
    """Where the 547 bound paths live, counted by what they are.

    The count a reader takes from ``publication manifest: PASS (547 files)`` is
    dominated by a vendored Mathlib checkout and an ASlib scenario --- material
    the lane did not write and does not claim. Splitting it out is the difference
    between "547 files are intact" and "79 authored files are intact".
    """

    origins = {
        "vendored_lean_corpus": 0,
        "vendored_aslib_scenario": 0,
        "p10_predecessor_authored": 0,
        "p9_predecessor_authored": 0,
        "shared_lane": 0,
        "other_papers": 0,
    }
    lane = lane_dir(repo_root)
    for relative, _ in publication_binding(repo_root).entries:
        if "benchmark/corpus/mathlib4_" in relative:
            origins["vendored_lean_corpus"] += 1
        elif "benchmark/aslib_" in relative:
            origins["vendored_aslib_scenario"] += 1
        elif relative.startswith("../archive/2026-08-pre-unification/paper-xx-content-bound-math-evaluation"):
            origins["p10_predecessor_authored"] += 1
        elif relative.startswith("../paper-xx-executable-research-core"):
            origins["p9_predecessor_authored"] += 1
        elif relative.startswith(".."):
            origins["other_papers"] += 1
        else:
            origins["shared_lane"] += 1
    # Resolving is what proves the ``..`` rows really do leave the lane; the
    # relative-prefix test above is only a label for them.
    outside = sum(
        1
        for path in committed_publication_paths(repo_root)
        if os.path.relpath(path, lane).startswith("..")
    )
    origins["outside_the_lane_directory"] = outside
    return origins


#: Overlay keys are rooted at ``papers/`` and legacy manifest rows at the lane,
#: so one is the other with ``../`` in front. ``VERIFY_LOCAL_CLOSURE_V2.sh``
#: performs the same rewrite, restricted to the one namespace it may normalize.
_LEGACY_OVERLAY_PREFIX_ROOT = "../"


def overlay_supersession(repo_root: Path) -> dict[str, int]:
    """What the V2 overlay actually adds over the sha256 manifest it supersedes.

    ``VERIFY_LOCAL_CLOSURE_V2.sh`` skips five legacy sha256 rows as "intentionally
    superseded" and re-checks those paths by Git blob id instead. Whether that
    skip removes anything is measurable: if a superseded path still matches the
    sha256 the legacy manifest records, the two bindings pin the same bytes and
    the supersession moved nothing. Only the four *additive* paths are content
    the overlay is the sole binding for.
    """

    lane = lane_dir(repo_root)
    overlay = json.loads((lane / OVERLAY).read_text(encoding="utf-8"))["paths"]
    legacy = dict(publication_binding(repo_root).entries)
    legacy_row = {key: _LEGACY_OVERLAY_PREFIX_ROOT + key for key in overlay}
    substitutions = [key for key in overlay if legacy_row[key] in legacy]
    unchanged = [
        key
        for key in substitutions
        if DigestAlgorithm.SHA256.digest((repo_root / "papers" / key).read_bytes())
        == legacy[legacy_row[key]]
    ]
    return {
        "overlay_paths": len(overlay),
        "substitutions": len(substitutions),
        "additive": len(overlay) - len(substitutions),
        "substitutions_whose_legacy_digest_still_matches": len(unchanged),
    }


__all__ = [
    "EXCLUDED_DIR_NAMES",
    "EXCLUDED_SUFFIXES",
    "GENERATOR",
    "LANE",
    "OVERLAY",
    "OVERLAY_DEREFERENCED_BY",
    "PUBLICATION_DEREFERENCED_BY",
    "PUBLICATION_MANIFEST",
    "SCOPE_DEFINITION",
    "SCOPE_ID",
    "SCOPE_ROOTS",
    "SCRIPT_MANIFEST",
    "SCRIPT_MANIFEST_DEREFERENCED_BY",
    "SCRIPT_MANIFEST_HEADER_LINES",
    "audit_p10_publication",
    "committed_publication_paths",
    "declared_scope",
    "lane_dir",
    "manifest_entry_origin",
    "overlay_binding",
    "overlay_supersession",
    "publication_binding",
    "script_manifest_binding",
    "shipped_bindings",
    "shipped_generator_enrolment",
]

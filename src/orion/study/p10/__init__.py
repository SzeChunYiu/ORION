"""P10 instruments that make a self-scoped content binding report its own scope.

P10's publication manifest is real: 547 sha256 rows, 0 drifted, and appending one
byte to a file it names reds ``VERIFY_LOCAL_CLOSURE.sh`` immediately. What it
never answers is whether the 547 is the right 547. Membership is decided by
``generate_publication_manifest.included_files()`` inside the lane the manifest
protects, and both shipped verifiers iterate the manifest rather than the tree,
so a file inside the manifest's own declared roots that it does not name is a
file no gate can see.

:mod:`publication_binding` registers the three shipped digest files as they ship;
:mod:`membership_audit` runs them and blocks when the watched set turns out not
to be closed against the tree. The mechanism is
:mod:`orion.programme.manifest_membership`, which builds its verdict from
:class:`orion.programme.guard_exercise.GuardExercise` with the *declared scope*
as the denominator rather than the enrolled set.

The failure they close is recorded under
``research/failures/2026-08-self-scoped-manifest-unclosed-membership/``.
"""

from __future__ import annotations

from .publication_binding import (
    LANE,
    OVERLAY,
    PUBLICATION_MANIFEST,
    SCOPE_ID,
    SCRIPT_MANIFEST,
    audit_p10_publication,
    committed_publication_paths,
    declared_scope,
    manifest_entry_origin,
    shipped_bindings,
    shipped_generator_enrolment,
)

__all__ = [
    "LANE",
    "OVERLAY",
    "PUBLICATION_MANIFEST",
    "SCOPE_ID",
    "SCRIPT_MANIFEST",
    "audit_p10_publication",
    "committed_publication_paths",
    "declared_scope",
    "manifest_entry_origin",
    "shipped_bindings",
    "shipped_generator_enrolment",
]

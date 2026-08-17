"""Activation is withheld. That fact is code, not a comment.

Issue #210 may not authorize a self-sustaining programme while #209 is open.
This module is the lock: every grant is hardwired ``False``, the status string
is ``PREPARATORY_AWAITING_ACTIVATION``, and any ``p4-programme`` /
``p4-epoch-manifest`` / ``p4-anti-collapse`` workflow sitting under
``.github/workflows/`` with a live YAML extension is a defect.

Nothing here becomes true when #209 closes. An external host has to authorize.
"""

from __future__ import annotations

from pathlib import Path

PREPARATORY_STATUS = "PREPARATORY_AWAITING_ACTIVATION"
BLOCKING_DEPENDENCY = "#209"
BLOCKING_DEPENDENCIES = ("#209", "#76")

# Same sentinel as ``orion.self_orion.phase3_preflight.UNBOUND_DIGEST``. Duplicated
# rather than imported so ``orion.programme`` does not take a Self-ORION dependency.
UNBOUND_DIGEST = "0" * 64

_LIVE_YAML_SUFFIXES = {".yml", ".yaml"}
_LIVE_PROGRAMME_WORKFLOW_PREFIXES = (
    "p4-programme",
    "p4-epoch-manifest",
    "p4-anti-collapse",
)

_FORBIDDEN_RUNNER_ROOT = "src/phase4"


def activation_authorized() -> bool:
    return False


def grants_self_sustaining_authority() -> bool:
    return False


def grants_phase4_closure() -> bool:
    return False


def live_phase4_programme_workflow_names(workflows_dir: Path) -> tuple[str, ...]:
    """Return live GitHub Actions filenames that would run a Phase-4 programme.

    GitHub loads every ``*.yml`` / ``*.yaml`` under ``.github/workflows/``. A
    ``.template.yml`` suffix is still ``.yml`` and therefore live. Templates
    belong under ``research/phase-4-protocol/workflows/`` with a non-YAML
    suffix such as ``.yml.template``.
    """

    if not workflows_dir.is_dir():
        return ()
    names: list[str] = []
    for path in sorted(workflows_dir.iterdir()):
        if path.suffix not in _LIVE_YAML_SUFFIXES:
            continue
        if any(path.name.startswith(prefix) for prefix in _LIVE_PROGRAMME_WORKFLOW_PREFIXES):
            names.append(path.name)
    return tuple(names)


def forbidden_phase4_runner_present(repo_root: Path) -> bool:
    """True if the live runner tree the old templates pointed at exists.

    Creating ``src/phase4/`` would turn relocated templates into an executable
    programme path. The runner tree is deferred until authorization.
    """

    return (repo_root / _FORBIDDEN_RUNNER_ROOT).exists()


def activation_blockers(
    *,
    workflows_dir: Path,
    repo_root: Path,
) -> tuple[str, ...]:
    blockers = [
        f"blocked on {dependency}"
        for dependency in BLOCKING_DEPENDENCIES
    ]
    blockers.append("no protected Phase-4 longitudinal evidence exists")
    blockers.append("programme activation is withheld")
    for name in live_phase4_programme_workflow_names(workflows_dir):
        blockers.append(f"live Phase-4 programme workflow present: {name}")
    if forbidden_phase4_runner_present(repo_root):
        blockers.append("forbidden live runner tree present: src/phase4")
    return tuple(blockers)


__all__ = [
    "BLOCKING_DEPENDENCIES",
    "BLOCKING_DEPENDENCY",
    "PREPARATORY_STATUS",
    "UNBOUND_DIGEST",
    "activation_authorized",
    "activation_blockers",
    "forbidden_phase4_runner_present",
    "grants_phase4_closure",
    "grants_self_sustaining_authority",
    "live_phase4_programme_workflow_names",
]

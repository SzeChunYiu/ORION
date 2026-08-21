"""Audit P10's shipped publication binding for membership closure.

Reports both denominators side by side: the enrolled set the shipped verifiers
walk, and the declared scope they never compare it against. Exits non-zero when either
guard blocks, so it fails a pipeline rather than printing a table nobody reads::

    python -m orion.study.p10.membership_audit
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Sequence

from orion.programme.manifest_membership import (
    audit_outcome,
    audit_report,
    render_audit,
)
from orion.programme.records import Outcome
from orion.study.p10 import publication_binding as shipped

REPO_ROOT = Path(__file__).resolve().parents[4]


def audit_p10_publication_binding(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    """The audit report, plus the two facts that explain the numbers in it."""

    audit = shipped.audit_p10_publication(repo_root)
    report = dict(audit_report(audit))
    report["manifest_entry_origin"] = shipped.manifest_entry_origin(repo_root)
    # The generator's enrolment is checked against the committed manifest here
    # rather than trusted: if they disagree, the committed manifest was hand-
    # edited or the generator was changed without regenerating, and either makes
    # every other number on this page a statement about the wrong artifact.
    derived = shipped.shipped_generator_enrolment(repo_root)
    committed = shipped.committed_publication_paths(repo_root)
    report["generator_agrees_with_committed_manifest"] = derived == committed
    report["generator_only"] = sorted(str(path) for path in derived - committed)
    report["committed_only"] = sorted(str(path) for path in committed - derived)
    return report


def _render(report: dict[str, Any]) -> str:
    origin = report["manifest_entry_origin"]
    lines = [
        f"P10 publication binding: {report['outcome']}",
        f"  scope        {report['files_in_scope']} files "
        f"({report['scope_definition']})",
        f"  enrolled     {report['files_enrolled']}  drift verdict "
        f"{report['drift_verdict']['outcome']}",
        f"  unenrolled   {report['files_unenrolled']}  membership verdict "
        f"{report['membership_verdict']['outcome']}",
        f"  named only by an unread digest file: {report['files_stale_only']}",
        f"  digests that disagree in an unread file: {len(report['unenforced_drift'])}",
        "  what the enrolled count is made of:",
    ]
    for name, count in sorted(origin.items(), key=lambda item: -item[1]):
        lines.append(f"    {count:>4}  {name}")
    lines.append(
        "  generator agrees with the committed manifest: "
        f"{report['generator_agrees_with_committed_manifest']}"
    )
    for path in report["unenrolled_paths"]:
        lines.append(f"    unenrolled  {path}")
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--json", action="store_true", help="emit the audit as JSON")
    args = parser.parse_args(argv)

    report = audit_p10_publication_binding(args.repo_root)
    print(json.dumps(report, indent=2, sort_keys=True) if args.json else _render(report))

    outcome = Outcome(report["outcome"])
    if outcome is Outcome.PASS:
        return 0
    return 1 if outcome is Outcome.FAIL else 3


def audit_outcome_for(repo_root: Path = REPO_ROOT) -> Outcome:
    """The audit's typed verdict without rendering it."""

    return audit_outcome(shipped.audit_p10_publication(repo_root))


def render(repo_root: Path = REPO_ROOT) -> str:
    return render_audit(shipped.audit_p10_publication(repo_root))


if __name__ == "__main__":
    raise SystemExit(main())

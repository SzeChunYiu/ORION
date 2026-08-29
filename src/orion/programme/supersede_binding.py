"""Explicit SUPERSEDED reconciliation of a paper's content binding.

``papers/CONTENT_BINDING_DRIFT_BASELINE_V1.json`` states the only two ways a paper
leaves the drift debt record:

    Entries leave only after a real rebuild or an explicit SUPERSEDED reconciliation
    that retains the historical render closure and denies current submission
    authority; never by an unqualified hash-only rewrite.

The first exit exists: ``check_journal_package.py --write-hashes`` rebuilds a package
for papers in the journal-package registry. The second was specified but never
implemented, which left every paper bound by a top-level ``SHA256SUMS`` with no legal
way to correct its own manuscript (see the tracker issue for the four Wave-2
corrections stalled on this).

This implements it, with the two properties the baseline demands made structural rather
than advisory:

* **the historical closure is retained** --- every superseded digest is written to an
  immutable record before the manifest is touched, so the evidence that content moved
  survives the move;
* **current submission authority is denied** --- the record sets it false, and it can
  only be restored by whatever process earns it, not by this tool.

It refuses the failure mode the baseline names. A run that would change digests without
a stated reason, or that finds nothing actually moved, is rejected: an unqualified
hash-only rewrite is exactly what must not be possible.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "orion.programme.superseded-binding.v1"


class SupersedeRefused(Exception):
    """Raised when a reconciliation would violate the baseline's own conditions."""


@dataclass(frozen=True)
class Supersession:
    paper_id: str
    directory: str
    sums_file: str
    reason: str
    authority_reference: str
    superseded: dict[str, str] = field(default_factory=dict)
    replacement: dict[str, str] = field(default_factory=dict)

    @property
    def moved_paths(self) -> tuple[str, ...]:
        return tuple(sorted(p for p, d in self.superseded.items()
                            if self.replacement.get(p) != d))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_sums(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        digest, _, rel = line.partition("  ")
        if digest and rel:
            out[rel] = digest
    return out


def plan(repo_root: Path, sums_file: Path, reason: str,
         authority_reference: str) -> Supersession:
    """Compute what a reconciliation would record. Reads only; writes nothing."""
    if not reason or not reason.strip():
        raise SupersedeRefused(
            "a reconciliation requires a stated reason; an unqualified hash-only "
            "rewrite is exactly what the baseline forbids"
        )
    if not authority_reference or not authority_reference.strip():
        raise SupersedeRefused(
            "a reconciliation requires an authority reference (issue or decision id) "
            "so the record names who decided it"
        )
    recorded = parse_sums(sums_file)
    if not recorded:
        raise SupersedeRefused(f"{sums_file} records no digests")

    replacement: dict[str, str] = {}
    for rel in recorded:
        target = (repo_root / rel)
        if not target.is_file():
            target = (sums_file.parent / rel)
        if not target.is_file():
            raise SupersedeRefused(
                f"cannot reconcile: {rel} is recorded but absent on disk. A missing "
                "file is a deletion to account for, not a digest to refresh."
            )
        replacement[rel] = _sha256(target)

    paper_dir = sums_file.parent
    sup = Supersession(
        paper_id=paper_dir.name,
        directory=paper_dir.relative_to(repo_root).as_posix(),
        sums_file=sums_file.relative_to(repo_root).as_posix(),
        reason=reason.strip(),
        authority_reference=authority_reference.strip(),
        superseded=recorded,
        replacement=replacement,
    )
    if not sup.moved_paths:
        raise SupersedeRefused(
            "nothing moved: every recorded digest already matches its file. There is "
            "no supersession to record, and rewriting the manifest would be a "
            "hash-only rewrite."
        )
    return sup


def apply(repo_root: Path, sup: Supersession, *, now: datetime | None = None) -> Path:
    """Write the immutable record, then the corrected manifest. Order matters."""
    stamp = (now or datetime.now(timezone.utc)).strftime("%Y%m%dT%H%M%SZ")
    paper_dir = repo_root / sup.directory
    record_path = paper_dir / f"SUPERSEDED_BINDING_{stamp}_V1.json"
    if record_path.exists():
        raise SupersedeRefused(f"{record_path} already exists; refusing to overwrite history")

    record = {
        "schema": SCHEMA,
        "paper_id": sup.paper_id,
        "directory": sup.directory,
        "sums_file": sup.sums_file,
        "superseded_at": stamp,
        "reason": sup.reason,
        "authority_reference": sup.authority_reference,
        "current_submission_authority": False,
        "authority_note": (
            "Denied by this reconciliation. It is not restored by rewriting a manifest; "
            "it is re-earned by whatever process grants it, and this record does not "
            "grant it."
        ),
        "scientific_authority_delta": "NONE",
        "historical_render_closure": dict(sorted(sup.superseded.items())),
        "replacement_digests": dict(sorted(sup.replacement.items())),
        "moved_paths": list(sup.moved_paths),
        "unchanged_path_count": len(sup.superseded) - len(sup.moved_paths),
        "retention_note": (
            "historical_render_closure is the binding as it stood before this change. "
            "It is retained so the evidence that content moved survives the move, which "
            "is the condition CONTENT_BINDING_DRIFT_BASELINE_V1 places on this exit."
        ),
    }
    # history first: if the manifest write fails, the record of what was superseded stands
    record_path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")

    sums_path = repo_root / sup.sums_file
    sums_path.write_text(
        "".join(f"{sup.replacement[rel]}  {rel}\n" for rel in sorted(sup.replacement))
    )
    return record_path

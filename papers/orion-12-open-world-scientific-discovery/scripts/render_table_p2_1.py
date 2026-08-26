#!/usr/bin/env python3
"""Render Table P2-1 (benchmark / data / license / provider / freeze manifest).

The table is generated from ``protocol/EXTERNAL_ACCESS_AUDIT_V1.json`` and never
hand-transcribed, per rule 7 of ``research/paper-programme-v1/protocols/README.md``.

Usage::

    python3 papers/orion-12-open-world-scientific-discovery/scripts/render_table_p2_1.py            # write
    python3 papers/orion-12-open-world-scientific-discovery/scripts/render_table_p2_1.py --check    # verify
    python3 papers/orion-12-open-world-scientific-discovery/scripts/render_table_p2_1.py --stdout   # print

Standard library only. Exit codes: 0 ok, 1 drift under ``--check``, 2 missing input.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PAPER_ROOT = Path(__file__).resolve().parents[1]
AUDIT_PATH = PAPER_ROOT / "protocol" / "EXTERNAL_ACCESS_AUDIT_V1.json"
TABLE_PATH = PAPER_ROOT / "protocol" / "TABLE_P2-1_freeze_manifest.md"

STATE_ORDER = {"OBTAINED": 0, "AVAILABLE_LICENSE_BLOCKED": 1, "NOT_OBTAINABLE": 2, "CANNOT_CHECK": 3}


def cell(value: object) -> str:
    """Render one value as a pipe-table cell: never empty, never pipe-breaking."""
    if value is None:
        return "n/a"
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, (list, tuple)):
        return "; ".join(cell(v) for v in value) if value else "n/a"
    text = str(value).replace("|", "\\|").replace("\n", " ").strip()
    return text or "n/a"


def clip(value: object, limit: int) -> str:
    """Cell text bounded to ``limit`` characters, with an explicit ellipsis."""
    text = cell(value)
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "\u2026"


def binding(artifact: dict) -> str:
    """The stable content binding for this artifact, in preference order."""
    hashes = artifact.get("content_hashes")
    if not hashes:
        return "none"
    for key in ("git_tree_sha", "decrypted_bundle_sha256", "hf_revision_sha"):
        if hashes.get(key):
            return f"{key}={hashes[key][:16]}\u2026"
    verified = hashes.get("verified_local_download") or {}
    if verified.get("local_sha256"):
        return f"local_sha256={verified['local_sha256'][:16]}\u2026 ({verified.get('path')})"
    return "recorded, see audit JSON"


def sort_key(artifact: dict) -> tuple:
    """Protocol-pinned artifacts first, then by state severity, then by id."""
    pinned = 0 if artifact.get("protocol_reference_key") else 1
    return (pinned, STATE_ORDER.get(artifact["state"], 9), artifact["artifact_id"])


def render(audit: dict) -> str:
    artifacts = sorted(audit["artifacts"], key=sort_key)
    lines: list[str] = []
    add = lines.append

    add("# Table P2-1: benchmark / data / license / provider / freeze manifest")
    add("")
    add("<!-- GENERATED FILE - DO NOT EDIT BY HAND.")
    add("     Regenerate with:")
    add("       python3 papers/orion-12-open-world-scientific-discovery/scripts/render_table_p2_1.py")
    add("     Source of record: protocol/EXTERNAL_ACCESS_AUDIT_V1.json -->")
    add("")
    add(f"Audit performed `{audit['audit_timestamp_utc']}` - `{audit['audit_completed_utc']}`.")
    add(f"Schema `{audit['schema_version']}` for protocol `{audit['protocol_id']}`.")
    add("")
    add(
        "This table is outcome-blind: it records what can be obtained, under what licence, at what "
        "cost, and with what contamination exposure. It contains no ORION-vs-baseline results."
    )
    add("")

    add("## A. Freeze manifest - identity, licence, obtainability")
    add("")
    add("| Artifact | Kind | Pinned revision | Rev. exists | State | Licence | Redistribute | Content binding |")
    add("| --- | --- | --- | --- | --- | --- | --- | --- |")
    for a in artifacts:
        rev = a.get("pinned_revision")
        add(
            "| `{id}` | {kind} | {rev} | {exists} | `{state}` | {lic} | {redist} | {bind} |".format(
                id=cell(a["artifact_id"]),
                kind=cell(a["kind"]),
                rev=f"`{rev[:12]}\u2026`" if rev else "not pinned",
                exists=cell(a.get("revision_exists")) if a.get("revision_exists") is not None else "n/a",
                state=cell(a["state"]),
                lic=clip(a.get("license"), 46),
                redist=cell(a.get("redistribution_allowed")),
                bind=cell(binding(a)),
            )
        )
    add("")

    add("## B. Official-evaluation runnability by task family")
    add("")
    add(
        "Obtaining an artifact and being able to run its official scorer are different questions. "
        "This section answers the second one, which is what decides whether a task family can carry "
        "evidence."
    )
    add("")
    runnable = audit["official_evaluation_runnable_by_family"]
    add("| Task family | Official scorer runnable | Meaning |")
    add("| --- | --- | --- |")
    for family, verdict in runnable["families"].items():
        add(f"| `{cell(family)}` | `{cell(verdict)}` | {clip(runnable['enum'][verdict], 120)} |")
    add("")

    add("## C. Provider, run requirements and contamination exposure")
    add("")
    add("| Artifact | State | Evaluator needs | Reference agent needs | Hard blocker | Contamination |")
    add("| --- | --- | --- | --- | --- | --- |")
    for a in artifacts:
        rr = a.get("run_requirements") or {}
        er = rr.get("evaluator_requirements")
        if isinstance(er, dict):
            needs = "; ".join(f"{k}: {v.get('credentials')}" for k, v in er.items())
        else:
            needs = rr.get("provider")
        agent = (rr.get("reference_agent_requirements") or {}).get("credentials")
        add(
            "| `{id}` | `{state}` | {needs} | {agent} | {blk} | {cont} |".format(
                id=cell(a["artifact_id"]),
                state=cell(a["state"]),
                needs=clip(needs, 110),
                agent=clip(agent, 70),
                blk=clip(rr.get("hard_blocker"), 150),
                cont=clip(a.get("contamination_note"), 120),
            )
        )
    add("")

    add("## D. Locators and licence evidence")
    add("")
    add("| Artifact | Locator | Licence source (verbatim check) |")
    add("| --- | --- | --- |")
    for a in artifacts:
        add(
            "| `{id}` | {loc} | {src} |".format(
                id=cell(a["artifact_id"]),
                loc=clip(a.get("locator"), 70),
                src=clip(a.get("license_source"), 190),
            )
        )
    add("")

    add("## E. Pinned-revision integrity")
    add("")
    integrity = audit["pinned_revision_integrity"]
    for key in (
        "reference_revision_keys_total",
        "keys_with_pinned_sha",
        "keys_without_pinned_sha",
        "keys_without_pinned_sha_list",
        "pinned_shas_resolving",
        "pinned_shas_missing",
    ):
        add(f"- `{key}`: {cell(integrity[key])}")
    add(f"- verdict: {integrity['verdict']}")
    add("")

    add("## F. Cross-cutting findings")
    add("")
    for item in audit["cross_cutting_findings"]:
        add(f"- {item}")
    add("")

    add("## G. Explicitly not established by this audit")
    add("")
    for item in audit["explicitly_not_established"]:
        add(f"- {item}")
    add("")

    add("## H. State counts")
    add("")
    counts: dict[str, int] = {}
    for a in artifacts:
        counts[a["state"]] = counts.get(a["state"], 0) + 1
    add("| State | Artifacts |")
    add("| --- | --- |")
    for state in sorted(counts, key=lambda s: STATE_ORDER.get(s, 9)):
        add(f"| `{state}` | {counts[state]} |")
    add("")
    add(f"Total artifacts audited: {len(artifacts)}.")
    add("")

    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if the committed table differs from a fresh render")
    parser.add_argument("--stdout", action="store_true", help="print the rendered table instead of writing it")
    args = parser.parse_args(argv)

    if not AUDIT_PATH.exists():
        print(f"missing audit input: {AUDIT_PATH}", file=sys.stderr)
        return 2

    rendered = render(json.loads(AUDIT_PATH.read_text(encoding="utf-8")))

    if args.stdout:
        sys.stdout.write(rendered)
        return 0

    if args.check:
        if not TABLE_PATH.exists():
            print(f"missing rendered table: {TABLE_PATH}", file=sys.stderr)
            return 1
        current = TABLE_PATH.read_text(encoding="utf-8")
        if current != rendered:
            print("TABLE_P2-1 is stale; rerun render_table_p2_1.py", file=sys.stderr)
            return 1
        print("TABLE_P2-1 matches EXTERNAL_ACCESS_AUDIT_V1.json")
        return 0

    TABLE_PATH.write_text(rendered, encoding="utf-8")
    print(f"wrote {TABLE_PATH} ({len(rendered)} chars)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

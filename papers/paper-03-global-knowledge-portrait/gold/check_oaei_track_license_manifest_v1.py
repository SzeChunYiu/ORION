#!/usr/bin/env python3
"""Validate the frozen OAEI/SemTab track licence-and-selection manifest.

`OAEI_TRACK_LICENSE_MANIFEST_V1.json` is the only sanctioned record of which
external ontology-alignment sources may be downloaded and scored, and
`OAEI_MULTI_CASE_ANALYSIS_FREEZE_V1.json` is the analysis contract that freezes
gates, arms and statistical units before any scoring. Both are worthless if
edited after the fact or written loosely, so this checker enforces the
structural invariants that make the freeze meaningful:

* freeze honesty — the manifest asserts outcome_accessed=false with an ISO-8601
  frozen_utc and a FROZEN status, and nothing claims a download happened;
* verified-or-CANNOT_CHECK — the one selected primary source carries a licence
  name with VERIFIED_WITH_URL_AND_DATE plus evidence URL, field and fetch hash;
  every CANNOT_CHECK licence entry has a null name and a stated reason, so an
  unverified licence can never masquerade under a familiar name;
* exclusions present — the UMLS-associated tracks and eClass are excluded with
  recorded bases, not silently dropped;
* natural-pair requirement — at least one natural ontology-pair candidate is
  recorded, licence-blocked, and bench23 is bound as single-seed insufficient
  on its own;
* analysis-contract binding — the frozen analysis keeps the inference unit at
  ontology pair/track (never the correspondence row), keeps unavailable arms
  CANNOT_CHECK without proxy substitution, and carries the issue pass gates
  verbatim (0.03 macro-F1 / 0.01+0.05 noninferiority-plus-recall, 100% valid
  output, zero added incoherence).

Exit codes: 0 conformant, 1 violation found, 2 the manifest (or a bound
artifact) could not be read — distinct from clean, because "could not check"
must never be reported as "checked and fine".
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

GOLD_DIR = Path(__file__).resolve().parent
DEFAULT_MANIFEST = GOLD_DIR / "OAEI_TRACK_LICENSE_MANIFEST_V1.json"
DEFAULT_FREEZE = GOLD_DIR.parent / "protocol" / "OAEI_MULTI_CASE_ANALYSIS_FREEZE_V1.json"

REQUIRED_VERIFICATION = "VERIFIED_WITH_URL_AND_DATE"
BLOCKED_VERIFICATION = "CANNOT_CHECK"


def _violations(doc: dict) -> list[str]:
    problems: list[str] = []

    # --- freeze honesty -----------------------------------------------------
    if "FROZEN" not in str(doc.get("manifest_status", "")):
        problems.append(f"manifest_status {doc.get('manifest_status')!r} is not a frozen record")
    if doc.get("outcome_accessed") is not False:
        problems.append(f"outcome_accessed is {doc.get('outcome_accessed')!r}, not false")
    frozen_utc = doc.get("frozen_utc")
    try:
        datetime.fromisoformat(str(frozen_utc).replace("Z", "+00:00"))
    except (ValueError, TypeError):
        problems.append(f"frozen_utc {frozen_utc!r} is not an ISO-8601 timestamp")

    # --- primary source: verified licence or nothing ------------------------
    primaries = doc.get("primary_sources", [])
    if not primaries:
        problems.append("no primary source recorded")
    for source in primaries:
        licence = source.get("license", {})
        if licence.get("verification") != REQUIRED_VERIFICATION:
            problems.append(
                f"primary source {source.get('source_id')!r} licence is not "
                f"{REQUIRED_VERIFICATION}: {licence.get('verification')!r}"
            )
        else:
            if not licence.get("name"):
                problems.append("verified licence carries no name")
            for field in ("evidence_url", "evidence_field", "evidence_fetch_sha256", "verified_utc"):
                if not licence.get(field):
                    problems.append(f"verified licence is missing {field}")
        if "DOWNLOADED" in str(source.get("download_status", "")) and "NOT_DOWNLOADED" not in str(
            source.get("download_status", "")
        ):
            problems.append(
                f"primary source {source.get('source_id')!r} claims a download: "
                f"{source.get('download_status')!r}"
            )
        if source.get("record", {}).get("file_sha256_published") is not None and not source.get(
            "record", {}
        ).get("integrity_note"):
            problems.append("published hash without an integrity note")

    # --- CANNOT_CHECK never wears a licence name ----------------------------
    for candidate in doc.get("natural_pair_candidates", []):
        licence = candidate.get("license", {})
        if licence.get("verification") == BLOCKED_VERIFICATION:
            if licence.get("name") is not None:
                problems.append(
                    f"{candidate.get('source_id')!r} is CANNOT_CHECK yet carries licence name "
                    f"{licence.get('name')!r}"
                )
            if not licence.get("reason"):
                problems.append(f"{candidate.get('source_id')!r} CANNOT_CHECK licence has no reason")
    fallback = doc.get("licensed_fallback", {})
    if fallback and fallback.get("license", {}).get("verification") == BLOCKED_VERIFICATION:
        if fallback.get("license", {}).get("name") is not None:
            problems.append(
                f"licensed fallback {fallback.get('source_id')!r} is CANNOT_CHECK yet carries licence name "
                f"{fallback.get('license', {}).get('name')!r}"
            )
        if fallback.get("activation_status") != "NOT_ACTIVATED":
            problems.append(
                f"licensed fallback activation_status is {fallback.get('activation_status')!r}, not NOT_ACTIVATED"
            )

    # --- issue-mandated exclusions -------------------------------------------
    excluded_ids = [entry.get("source_id") for entry in doc.get("excluded_tracks", [])]
    for required in ("OAEI_LARGEBIO_LEGACY_2015", "ECLASS"):
        if required not in excluded_ids:
            problems.append(f"required exclusion {required!r} is missing from excluded_tracks")
    for entry in doc.get("excluded_tracks", []):
        if not entry.get("exclusion_terminal") or not entry.get("basis"):
            problems.append(f"exclusion {entry.get('source_id')!r} lacks a terminal or a basis")

    # --- natural-pair requirement --------------------------------------------
    candidates = doc.get("natural_pair_candidates", [])
    if not any("natural" in str(entry.get("role", "")) for entry in candidates):
        problems.append("no natural ontology-pair candidate recorded (bench23 alone is insufficient)")
    for source in primaries:
        if source.get("composition_limitation") is None:
            problems.append(
                f"primary source {source.get('source_id')!r} records no single-seed composition limitation"
            )

    # --- scoring framework not executed ---------------------------------------
    framework = doc.get("scoring_framework", {})
    if framework.get("name") != "MELT":
        problems.append(f"scoring framework is {framework.get('name')!r}, not MELT")
    if "NOT_EXECUTED" not in str(framework.get("execution_status", "")):
        problems.append(
            f"scoring framework execution_status {framework.get('execution_status')!r} claims execution"
        )

    # --- non-bypass boundaries present ---------------------------------------
    if len(doc.get("non_bypass_boundaries", [])) < 3:
        problems.append("fewer than three non-bypass boundaries recorded")

    return problems


def _freeze_violations(freeze: dict) -> list[str]:
    problems: list[str] = []

    if freeze.get("freeze_status") != "FROZEN_BEFORE_ANY_OAEI_SCORING":
        problems.append(f"freeze_status is {freeze.get('freeze_status')!r}")
    if freeze.get("outcome_accessed") is not False:
        problems.append(f"freeze outcome_accessed is {freeze.get('outcome_accessed')!r}, not false")
    try:
        datetime.fromisoformat(str(freeze.get("frozen_utc")).replace("Z", "+00:00"))
    except (ValueError, TypeError):
        problems.append(f"freeze frozen_utc {freeze.get('frozen_utc')!r} is not ISO-8601")

    # gold rule
    if freeze.get("gold_standard_rule", {}).get("rule") != "OFFICIAL_RDF_REFERENCE_ALIGNMENTS_ONLY":
        problems.append("gold rule is not OFFICIAL_RDF_REFERENCE_ALIGNMENTS_ONLY")

    # inference unit
    unit = str(freeze.get("statistical_unit_rule", {}).get("inference_unit", ""))
    if "ontology pair" not in unit or "track" not in unit:
        problems.append(f"inference unit {unit!r} is not ontology pair or track")
    if "correspondence" not in unit or "never" not in unit:
        problems.append("inference unit does not exclude the correspondence row")

    # arms: comparators present, honest
    arms = {arm.get("arm_id"): arm for arm in freeze.get("arms", [])}
    for comparator in ("LOGMAP", "AML"):
        arm = arms.get(comparator)
        if arm is None:
            problems.append(f"comparator arm {comparator} missing from the frozen analysis")
        elif "CANNOT_CHECK" not in str(arm.get("status", "")) and "NOT_EXECUTED" not in str(
            arm.get("status", "")
        ):
            problems.append(f"{comparator} status {arm.get('status')!r} claims an execution")
    if "ORION_FULL_POLICY" not in arms:
        problems.append("candidate arm ORION_FULL_POLICY missing from the frozen analysis")
    policy = str(freeze.get("unavailable_arm_policy", "")).lower()
    if "prox" not in policy or "substitut" not in policy:
        problems.append("unavailable-arm policy does not forbid proxy substitution")

    # multi-case requirement
    composition = freeze.get("case_composition_rule", {})
    if composition.get("bench23_alone_is_insufficient") is not True:
        problems.append("case composition does not record bench23-alone insufficiency")
    if not composition.get("natural_pair_blocker"):
        problems.append("no recorded licence blocker on the natural-pair track")

    # pass gates verbatim from the issue
    gate = freeze.get("pass_gate", {})
    if "100%" not in str(gate.get("valid_output_coverage", "")):
        problems.append("valid-output coverage gate is not 100% of cases")
    if "0.03" not in str(gate.get("primary", "")):
        problems.append("primary gate is not the >=0.03 macro-F1 advantage")
    alternative = str(gate.get("alternative", ""))
    if "0.01" not in alternative or "0.05" not in alternative:
        problems.append("alternative gate lacks the 0.01 noninferiority + 0.05 recall thresholds")
    if "zero" not in str(gate.get("logical_incoherence", "")).lower():
        problems.append("logical-incoherence gate is not zero increase")

    # open-world boundary
    if "true negative" not in str(freeze.get("open_world_boundary", {}).get("rule", "")):
        problems.append("open-world boundary does not bind absent pairs away from true negatives")

    return problems


def run(manifest_path: Path = DEFAULT_MANIFEST, freeze_path: Path | None = None) -> int:
    """Entry point usable from tests; returns the process exit code."""

    if not manifest_path.is_file():
        print(f"CANNOT_CHECK: no licence manifest at {manifest_path}", file=sys.stderr)
        return 2
    try:
        doc = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as error:
        print(f"CANNOT_CHECK: manifest could not be read: {error}", file=sys.stderr)
        return 2
    if not isinstance(doc, dict):
        print("CANNOT_CHECK: manifest root is not a JSON object", file=sys.stderr)
        return 2

    freeze = None
    bound = freeze_path or DEFAULT_FREEZE
    if bound.is_file():
        try:
            freeze = json.loads(bound.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as error:
            print(f"CANNOT_CHECK: bound analysis freeze could not be read: {error}", file=sys.stderr)
            return 2

    problems = _violations(doc)
    if freeze is not None:
        problems.extend(_freeze_violations(freeze))
    else:
        problems.append(
            "bound analysis freeze not found; the licence record cannot be separated from its gates"
        )

    if problems:
        print(f"OAEI TRACK LICENCE MANIFEST: FAIL — {len(problems)} violation(s)")
        for problem in problems:
            print(f"  - {problem}")
        return 1

    print(
        "OAEI TRACK LICENCE MANIFEST: conformant "
        "(verified-or-CANNOT_CHECK, exclusions recorded, natural-pair blocked, freeze bound)"
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--freeze", type=Path, default=None)
    args = parser.parse_args(argv)
    return run(args.manifest, args.freeze)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

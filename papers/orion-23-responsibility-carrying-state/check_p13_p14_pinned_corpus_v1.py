#!/usr/bin/env python3
"""Checker for the P13+P14 corpus and objective-gold freeze (issue #1086).

Verifies two frozen artifacts:
  - P13_P14_PINNED_REPOSITORY_CORPUS_V1.json (ORION.P13P14.PinnedRepositoryCorpus.v1)
  - P13_P14_OBJECTIVE_GOLD_DERIVATION_CONTRACT_V1.json
    (ORION.P13P14.ObjectiveGoldDerivationContract.v1)

Both bind P13_P14_LIFECYCLE_GOLD_DERIVATION_RULE_V1.md by SHA-256, recomputed
live against disk; the contract's protocol doc must embed that rule verbatim.

Exit codes:
  0 — both frozen artifacts are intact and internally consistent
  1 — VIOLATIONS: an artifact was edited in a way that breaks the freeze
  2 — CANNOT_CHECK: an artifact is missing or unparseable, or a bound
      artifact is absent from disk so the sha binding cannot be recomputed
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
P13 = "papers/paper-13-responsibility-carrying-state"
RULE_REL = f"{P13}/P13_P14_LIFECYCLE_GOLD_DERIVATION_RULE_V1.md"
CONTRACT_REL = f"{P13}/P13_P14_OBJECTIVE_GOLD_DERIVATION_CONTRACT_V1.json"
CONTRACT_DOC_REL = f"{P13}/P13_P14_OBJECTIVE_GOLD_DERIVATION_CONTRACT_V1.md"
CORPUS_REL = f"{P13}/P13_P14_PINNED_REPOSITORY_CORPUS_V1.json"

EXPECTED_RULE_SHA = "3656565539ea89742dd0f876347ba0b7ec918dfe605d95ab691c5323b77f8ce9"
EXPECTED_CONTRACT_SHA = "43af90733fb1a1f7fadd261d1a9ff41fcb20c1ec2e394626be2850ed8f65aed0"

EXPECTED_FACT_CLASS_IDS = {
    "OBJECT_HASH_EXISTENCE",
    "ANCESTRY",
    "TAG_SIGNATURE",
    "TEST_EXIT",
    "TIMESTAMP_ORDER",
}

HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
FORBIDDEN_SUBJECT = re.compile(r"szechunyiu|(^|/)orion(/|$)", re.IGNORECASE)


def _sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _violations_corpus(doc: dict) -> list[str]:
    v: list[str] = []

    if doc.get("artifact_class") != "FROZEN_CORPUS_PINNING":
        v.append("artifact_class must be FROZEN_CORPUS_PINNING")
    for flag in ("results_exist", "campaign_executed", "outcome_accessed"):
        if doc.get(flag) is not False:
            v.append(f"{flag} must be false (frozen corpus pinning, no results)")
    if "never be cited as evidence" not in doc.get("labeling_rule", ""):
        v.append("labeling_rule must forbid citing this artifact as campaign evidence")
    if not doc.get("execution_status", "").startswith("CANNOT_CHECK__"):
        v.append("execution_status must stay CANNOT_CHECK__* (no campaign has executed)")

    # --- binding hashes (frozen value + live recompute against disk) ------------
    binding = doc.get("binding", {})
    rule_b = binding.get("rule", {})
    if rule_b.get("artifact") != RULE_REL:
        v.append("binding.rule.artifact must name the V1 rule of record")
    if rule_b.get("sha256") != EXPECTED_RULE_SHA:
        v.append(f"binding.rule.sha256 drifted from the frozen value: {rule_b.get('sha256')!r}")
    live_rule = _sha256_of(REPO_ROOT / RULE_REL)
    if live_rule != rule_b.get("sha256"):
        v.append("binding.rule.sha256 does not match the on-disk rule of record")
    con_b = binding.get("derivation_contract", {})
    if con_b.get("artifact") != CONTRACT_REL:
        v.append("binding.derivation_contract.artifact must name the frozen contract")
    if con_b.get("sha256") != EXPECTED_CONTRACT_SHA:
        v.append(f"binding.derivation_contract.sha256 drifted from the frozen value: {con_b.get('sha256')!r}")
    live_con = _sha256_of(REPO_ROOT / CONTRACT_REL)
    if live_con != con_b.get("sha256"):
        v.append("binding.derivation_contract.sha256 does not match the on-disk contract")

    # --- entries ------------------------------------------------------------------
    entries = doc.get("entries", [])
    seen: set[str] = set()
    for e in entries:
        rid = e.get("repo_id", "<none>")
        if rid in seen:
            v.append(f"{rid}: duplicate entry")
        seen.add(rid)
        if FORBIDDEN_SUBJECT.search(rid or ""):
            v.append(f"{rid}: ORION/SzeChunYiu-owned repository is forbidden as an external subject")
        if not str(e.get("url", "")).startswith("https://"):
            v.append(f"{rid}: url must be an https URL")
        if not e.get("org_login"):
            v.append(f"{rid}: org_login required")
        if not e.get("pinned_ref"):
            v.append(f"{rid}: pinned_ref required")
        if not HEX40.match(e.get("pinned_sha", "") or ""):
            v.append(f"{rid}: pinned_sha must be a 40-hex commit sha")
        if not e.get("retrieval_utc"):
            v.append(f"{rid}: retrieval_utc required")
        lic = e.get("license")
        if not isinstance(lic, dict):
            v.append(f"{rid}: license object required")
            continue
        verification = lic.get("verification")
        eligible = e.get("gold_eligible")
        if verification == "VERIFIED_WITH_URL_AND_DATE":
            if eligible is not True:
                v.append(f"{rid}: VERIFIED licence must set gold_eligible true")
            spdx = lic.get("spdx_id")
            if not spdx or spdx == "NOASSERTION":
                v.append(f"{rid}: VERIFIED licence must carry a real SPDX id")
            if not str(lic.get("evidence_url", "")).startswith("https://"):
                v.append(f"{rid}: VERIFIED licence must carry an https evidence_url")
            if not HEX64.match(lic.get("evidence_fetch_sha256", "") or ""):
                v.append(f"{rid}: VERIFIED licence must carry a 64-hex evidence_fetch_sha256")
        elif verification == "CANNOT_CHECK__LICENSE_UNCLEAR":
            if eligible is not False:
                v.append(f"{rid}: licence-unclear entry must set gold_eligible false")
            if lic.get("spdx_id") is not None:
                v.append(f"{rid}: CANNOT_CHECK licence must not assert an SPDX id")
        else:
            v.append(f"{rid}: licence verification must be VERIFIED_WITH_URL_AND_DATE or CANNOT_CHECK__LICENSE_UNCLEAR, got {verification!r}")

    # --- box minimums recomputed from entries, cross-checked against summary ------
    orgs = {e.get("org_login") for e in entries}
    elig = [e for e in entries if e.get("gold_eligible") is True]
    elig_orgs = {e.get("org_login") for e in elig}
    if not 30 <= len(entries) <= 50:
        v.append(f"box minimum: repository count must be within 30-50, found {len(entries)}")
    if len(orgs) < 5:
        v.append(f"box minimum: distinct organizations must be >= 5, found {len(orgs)}")
    if not 30 <= len(elig) <= 50:
        v.append(f"box minimum: gold-eligible repository count must be within 30-50, found {len(elig)}")
    if len(elig_orgs) < 5:
        v.append(f"box minimum: gold-eligible organizations must be >= 5, found {len(elig_orgs)}")

    summary = doc.get("summary", {})
    for key, live_val in (
        ("repository_count", len(entries)),
        ("distinct_org_count", len(orgs)),
        ("gold_eligible_count", len(elig)),
        ("gold_eligible_org_count", len(elig_orgs)),
        ("cannot_check_license_count", len(entries) - len(elig)),
    ):
        if summary.get(key) != live_val:
            v.append(f"summary.{key} drifted from the recomputed value: {summary.get(key)!r} != {live_val}")
    if sorted(summary.get("org_logins", [])) != sorted(orgs):
        v.append("summary.org_logins drifted from the entry org set")
    if sorted(summary.get("gold_eligible_org_logins", [])) != sorted(elig_orgs):
        v.append("summary.gold_eligible_org_logins drifted from the eligible org set")
    met = summary.get("box_minimums_met", {})
    for key, expect in (
        ("repository_count_in_30_50", 30 <= len(entries) <= 50),
        ("distinct_orgs_ge_5", len(orgs) >= 5),
        ("gold_eligible_repository_count_in_30_50", 30 <= len(elig) <= 50),
        ("gold_eligible_orgs_ge_5", len(elig_orgs) >= 5),
    ):
        if met.get(key) is not expect:
            v.append(f"summary.box_minimums_met.{key} must be {expect}")

    # --- box verdict + boundaries ---------------------------------------------------
    box = doc.get("box_verdicts", {}).get("box_pinned_repository_corpus", {})
    if box.get("verdict") != "CORPUS_FROZEN__CAMPAIGN_USE_PENDING":
        v.append("box_pinned_repository_corpus verdict must be CORPUS_FROZEN__CAMPAIGN_USE_PENDING")
    if "open_remainder" not in box or not box.get("open_remainder"):
        v.append("box_pinned_repository_corpus must record its open remainder")
    if len(doc.get("non_bypass_boundaries", [])) < 4:
        v.append("non_bypass_boundaries must keep all four frozen boundary statements")
    if doc.get("scientific_authority_delta") != "NONE":
        v.append("scientific_authority_delta must stay NONE")

    return v


def _violations_contract(doc: dict) -> list[str]:
    v: list[str] = []

    if doc.get("artifact_class") != "FROZEN_DERIVATION_CONTRACT":
        v.append("contract artifact_class must be FROZEN_DERIVATION_CONTRACT")
    for flag in ("results_exist", "campaign_executed", "outcome_accessed"):
        if doc.get(flag) is not False:
            v.append(f"contract {flag} must be false (frozen contract, no results)")
    if "never be cited as evidence" not in doc.get("labeling_rule", ""):
        v.append("contract labeling_rule must forbid citing this artifact as campaign evidence")
    if not doc.get("execution_status", "").startswith("CANNOT_CHECK__"):
        v.append("contract execution_status must stay CANNOT_CHECK__*")

    rule_b = doc.get("gold_rule_binding", {})
    if rule_b.get("artifact") != RULE_REL:
        v.append("gold_rule_binding.artifact must name the V1 rule of record")
    if rule_b.get("sha256") != EXPECTED_RULE_SHA:
        v.append(f"gold_rule_binding.sha256 drifted from the frozen value: {rule_b.get('sha256')!r}")
    if _sha256_of(REPO_ROOT / RULE_REL) != rule_b.get("sha256"):
        v.append("gold_rule_binding.sha256 does not match the on-disk rule of record")

    classes = doc.get("admissible_fact_classes", [])
    ids = [c.get("class_id") for c in classes]
    if set(ids) != EXPECTED_FACT_CLASS_IDS or len(ids) != 5:
        v.append(f"admissible_fact_classes must be exactly the five frozen classes, got {sorted(set(ids))}")
    for c in classes:
        cid = c.get("class_id", "<none>")
        if not c.get("rule_ref", "").startswith("P13_P14_LIFECYCLE_GOLD_DERIVATION_RULE_V1.md"):
            v.append(f"{cid}: rule_ref must cite the V1 rule item")
        if not c.get("fact"):
            v.append(f"{cid}: fact statement required")
        pred = c.get("predicate", {})
        for field in ("command_template", "machine_check", "label_type"):
            if not pred.get(field):
                v.append(f"{cid}: predicate.{field} required")
        if "CANNOT_CHECK" not in pred.get("label_type", ""):
            v.append(f"{cid}: predicate.label_type must include the CANNOT_CHECK fail-closed label")
        if not c.get("inadmissible_interpretations"):
            v.append(f"{cid}: inadmissible_interpretations required")

    pre = doc.get("derivation_preconditions", {})
    for field in ("corpus_membership", "license_gate", "clone_verification", "fail_closed"):
        if not pre.get(field):
            v.append(f"derivation_preconditions.{field} required")
    if "no gold" not in pre.get("license_gate", ""):
        v.append("derivation_preconditions.license_gate must fail closed for licence-unclear entries")

    if len(doc.get("prohibitions", [])) < 4:
        v.append("prohibitions must keep all four frozen prohibitions")
    if doc.get("scientific_authority_delta") != "NONE":
        v.append("contract scientific_authority_delta must stay NONE")
    box = doc.get("box_verdicts", {}).get("box_objective_gold_derivation", {})
    if box.get("verdict") != "CONTRACT_FROZEN_EXECUTION_CANNOT_CHECK":
        v.append("box_objective_gold_derivation verdict must be CONTRACT_FROZEN_EXECUTION_CANNOT_CHECK")
    if not box.get("open_remainder"):
        v.append("box_objective_gold_derivation must record its open remainder")

    # --- protocol doc must embed the rule verbatim -------------------------------
    doc_path = REPO_ROOT / CONTRACT_DOC_REL
    if not doc_path.is_file():
        v.append(f"contract protocol doc absent: {CONTRACT_DOC_REL}")
    else:
        rule_text = (REPO_ROOT / RULE_REL).read_text(encoding="utf-8").rstrip("\n")
        doc_text = doc_path.read_text(encoding="utf-8")
        if rule_text not in doc_text:
            v.append("contract protocol doc no longer embeds the V1 rule verbatim")

    return v


def run(corpus_path: Path, contract_path: Path) -> int:
    for label, path in (("corpus", corpus_path), ("contract", contract_path)):
        if not path.is_file():
            print(f"CANNOT_CHECK: {label} artifact not found: {path}")
            return 2
    try:
        corpus = json.loads(corpus_path.read_text(encoding="utf-8"))
        contract = json.loads(contract_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        print(f"CANNOT_CHECK: artifact unparseable: {exc}")
        return 2
    if not isinstance(corpus, dict) or corpus.get("schema") != "ORION.P13P14.PinnedRepositoryCorpus.v1":
        print("CANNOT_CHECK: corpus artifact is not ORION.P13P14.PinnedRepositoryCorpus.v1")
        return 2
    if not isinstance(contract, dict) or contract.get("schema") != "ORION.P13P14.ObjectiveGoldDerivationContract.v1":
        print("CANNOT_CHECK: contract artifact is not ORION.P13P14.ObjectiveGoldDerivationContract.v1")
        return 2

    for rel in (RULE_REL, CONTRACT_REL, CONTRACT_DOC_REL):
        if not (REPO_ROOT / rel).is_file():
            print(f"CANNOT_CHECK: bound artifact absent from disk, sha binding not recomputable: {rel}")
            return 2

    violations = _violations_corpus(corpus) + _violations_contract(contract)
    if violations:
        print(f"VIOLATIONS ({len(violations)}):")
        for item in violations:
            print(f"  - {item}")
        return 1

    n = len(corpus["entries"])
    orgs = len({e["org_login"] for e in corpus["entries"]})
    elig = sum(1 for e in corpus["entries"] if e["gold_eligible"])
    elig_orgs = len({e["org_login"] for e in corpus["entries"] if e["gold_eligible"]})
    print(
        f"P13_P14 corpus+contract freeze intact: {n} repos / {orgs} orgs "
        f"(eligible {elig} repos / {elig_orgs} orgs), "
        "rule+contract sha bindings recomputed live, five fact classes frozen, no ORION subject"
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("corpus", nargs="?", default=REPO_ROOT / CORPUS_REL, type=Path)
    parser.add_argument("contract", nargs="?", default=REPO_ROOT / CONTRACT_REL, type=Path)
    args = parser.parse_args()
    return run(args.corpus, args.contract)


if __name__ == "__main__":
    sys.exit(main())

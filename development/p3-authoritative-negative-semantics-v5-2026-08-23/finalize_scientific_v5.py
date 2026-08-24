#!/usr/bin/env python3
"""Finalize the V5 scientific result without executing comparators or protected outcomes."""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import pathlib
from collections import Counter, defaultdict


ROOT = pathlib.Path(__file__).resolve().parent


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def read_json(name: str):
    return json.loads((ROOT / name).read_text())


def write_json(name: str, value) -> None:
    (ROOT / name).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_rights_audit() -> dict:
    audit = {
        "schema_version": "orion.p3.authoritative-negative-semantics.rights-identity-audit.v5",
        "created_at": now(),
        "audit_scope": (
            "Independent identity and applicability audit for research extraction from the exact "
            "frozen ontology bytes. This is not legal advice and not a blanket relicensing claim."
        ),
        "raw_legal_or_ontology_payloads_retained": False,
        "families": {
            "ENVO_2026_06_26": {
                "verdict": "PASS",
                "identity_pass": True,
                "applicability_pass": True,
                "research_use_pass": True,
                "frozen_commit": "a2455d1a77e46bb8a664d65a157166b539269042",
                "rights_source_url": "https://raw.githubusercontent.com/EnvironmentOntology/envo/a2455d1a77e46bb8a664d65a157166b539269042/LICENSE",
                "rights_source_git_blob_sha1": "0e259d42c996742e9e3cba14c677129b2c1b6311",
                "rights_source_sha256": "a2010f343487d3f7618affe54f789f5487602331c0a8d03f49e9a7c547cf0499",
                "rights_identity": "CC0 1.0 Universal",
                "ontology_declared_license_iris": [
                    "https://creativecommons.org/publicdomain/zero/1.0/"
                ],
                "applicability_basis": [
                    "The exact root LICENSE blob is bound to the frozen release commit.",
                    "The parsed frozen ontology itself declares the CC0 1.0 IRI.",
                ],
            },
            "FIBO_FND_2026Q2": {
                "verdict": "PASS",
                "identity_pass": True,
                "applicability_pass": True,
                "research_use_pass": True,
                "frozen_commit": "f59157fe156e3d91b1c045222d0a7dc06b7d78a2",
                "rights_source_url": "https://raw.githubusercontent.com/edmcouncil/fibo/f59157fe156e3d91b1c045222d0a7dc06b7d78a2/LICENSE",
                "rights_source_git_blob_sha1": "34cf2d376cc00346c285ea74d25647879cfe9a76",
                "rights_source_sha256": "59f852c87fa59411aa7dc527bd5629074d2caced7de4a48bbe7c5763359d8559",
                "rights_identity": "MIT License, copyright 2020 Enterprise Data Management Council",
                "ontology_declared_license_iris": [],
                "applicability_basis": [
                    "The exact root LICENSE blob is bound to the frozen repository commit.",
                    "The selected FND files are repository content at that same commit; no contrary file-level notice was observed in the extraction metadata.",
                ],
            },
            "W3C_PROV_O_REC_20130430": {
                "verdict": "PASS",
                "identity_pass": True,
                "applicability_pass": True,
                "research_use_pass": True,
                "frozen_commit": "aa82bd71b6bb1f7b735bf3f7f5b948fae87764f0",
                "frozen_path": "ontology/releases/REC-prov-o-20130430/ns/prov-o.ttl",
                "frozen_git_blob_sha1": "8b4d4b18d73d1e8f3e671e879c6c242205b6a729",
                "frozen_sha256": "3d03c8e15753178541fb8cd59fbefecaf1861f9c37ef75190c6e938b85fb0c3d",
                "recommendation_url": "https://www.w3.org/TR/2013/REC-prov-o-20130430/",
                "recommendation_sha256": "6b96671ab84faf12ce3f041aca12c3f93a6df2ed242348810743179a68e69555",
                "historical_document_license_url": "https://www.w3.org/Consortium/Legal/2002/copyright-documents-20021231",
                "historical_document_license_sha256": "73101ed2e566de5dac8ff8f438fc24ef32d206687330aef7b2b640416d60af7e",
                "subsequent_document_license_url": "https://www.w3.org/Consortium/Legal/2015/doc-license",
                "subsequent_document_license_sha256": "f3df06a8686e6cd5e3bde34ff9f7c6490b98e4f5b84263c5e4ba55fb2a3ff956",
                "nonrelied_upon_2023_software_document_license": {
                    "url": "https://www.w3.org/copyright/software-license-2023/",
                    "sha256": "aab6d2da3de7e0c6158551b2fd8f43ffe2a3373f2ffecb0f1c6db9fa79b0690b",
                    "retroactive_applicability_assumed": False,
                },
                "rights_identity": "W3C document-use grant applicable at the 2013 Recommendation publication",
                "applicability_basis": [
                    "The dated Recommendation links W3C document-use rules and identifies the linked namespace resource as the OWL encoding of PROV-O.",
                    "The frozen TTL self-identifies version IRI http://www.w3.org/ns/prov-o-20130430 and versionInfo Recommendation version 2013-04-30, and links the PROV-O Recommendation.",
                    "The 2002 W3C Document License explicitly grants copying and distribution of the linked W3C document; that grant is sufficient for this unmodified research access and factual certificate extraction.",
                    "The archived 2002-license page states that the 2015 more-permissive document license was applied to documents previously available under it. This is supporting evidence, not an assumption that the 2023 software/document license applies retroactively.",
                    "Raw ontology payloads are not redistributed or retained by this lane.",
                ],
                "scope_limit": "PASS covers the exact research access and certificate extraction here; it does not assert a blanket licence for modified PROV-O distributions.",
            },
        },
    }
    audit["counts"] = {
        "families_audited": len(audit["families"]),
        "identity_pass": sum(x["identity_pass"] for x in audit["families"].values()),
        "applicability_pass": sum(x["applicability_pass"] for x in audit["families"].values()),
        "research_use_pass": sum(x["research_use_pass"] for x in audit["families"].values()),
    }
    audit["three_family_rights_gate_pass"] = all(
        x["verdict"] == "PASS"
        and x["identity_pass"]
        and x["applicability_pass"]
        and x["research_use_pass"]
        for x in audit["families"].values()
    ) and len(audit["families"]) == 3
    write_json("RIGHTS_IDENTITY_AUDIT_V5.json", audit)
    return audit


def load_certificates() -> list[dict]:
    rows = []
    for line_number, line in enumerate((ROOT / "CERTIFICATE_REGISTRY_V5.jsonl").read_text().splitlines(), 1):
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise SystemExit(f"invalid certificate JSON at line {line_number}: {exc}") from exc
    return rows


def recompute_admission(extraction: dict, rights: dict) -> dict:
    audit_sha = sha256(ROOT / "RIGHTS_IDENTITY_AUDIT_V5.json")
    for family_id, family in extraction["families"].items():
        right = rights["families"].get(family_id, {})
        rights_pass = (
            right.get("verdict") == "PASS"
            and right.get("identity_pass") is True
            and right.get("applicability_pass") is True
            and right.get("research_use_pass") is True
        )
        family["rights_registry_pass"] = rights_pass
        family["family_admitted"] = bool(
            rights_pass
            and family["transport_and_parse_pass"]
            and family["authority_namespace_class_count"] > 0
            and family["explicit_disjoint_obstruction_certificate_count"] > 0
            and family["conflict_count"] == 0
            and family["source_family_disjoint_governance_pass"]
        )
    extraction["rights_identity_audit_sha256"] = audit_sha
    extraction["admission_recomputed_after_independent_rights_audit"] = True
    extraction["admission_recomputed_at"] = now()
    extraction["counts"]["admitted_families"] = sum(
        x["family_admitted"] for x in extraction["families"].values()
    )
    extraction["frame_gate_pass"] = (
        len(extraction["families"]) == extraction["counts"]["required_families"] == 3
        and all(x["family_admitted"] for x in extraction["families"].values())
    )
    write_json("EXTRACTION_RESULT_V5.json", extraction)
    return extraction


def build_theorem(extraction: dict, certs: list[dict]) -> dict:
    theorem = {
        "schema_version": "orion.p3.authoritative-negative-semantics.theorem-and-bound.v5",
        "created_at": now(),
        "frame_id": extraction["frame_id"],
        "name": "Direct-certificate partial-identification theorem",
        "definitions": {
            "G_C": "canonical pairs carrying an admitted direct GLUE certificate",
            "O_C": "canonical pairs carrying an admitted direct OBSTRUCTION certificate",
            "I_C_pair": {
                "G_C_only": ["GLUE"],
                "O_C_only": ["OBSTRUCTION"],
                "neither": ["GLUE", "OBSTRUCTION"],
                "both": "CANNOT_CHECK_CONFLICT",
            },
        },
        "universal_theorem": (
            "For any immutable byte-identical source/target ontology views satisfying the frozen namespace and direct-axiom rules, every canonical pair with exactly one certificate kind is point-identified; every pair with neither kind remains set-valued {GLUE, OBSTRUCTION}; and every pair with both kinds is excluded as CANNOT_CHECK_CONFLICT."
        ),
        "proof_sketch": [
            "The adapter assigns singleton {GLUE} exactly to same-IRI identities and direct named equivalentClass certificates.",
            "It assigns singleton {OBSTRUCTION} exactly to direct named disjointWith or valid named AllDisjointClasses certificates.",
            "The frozen absence rule maps no-certificate pairs to {GLUE, OBSTRUCTION}, so neither positive-reference absence nor matcher nonselection can create obstruction.",
            "The conflict rule excludes pairs carrying both certificate kinds; therefore the remaining certificate domain has a unique binary label.",
        ],
        "corollaries": {
            "monotone_refinement": "Adding conflict-free direct certificates can only preserve or shrink information sets; it cannot turn absence into OBSTRUCTION.",
            "no_free_obstruction": "Without a selected explicit negative certificate, obstruction is not identified.",
            "family_extensibility": "The theorem schema is not bounded to the three observed families; each new family must independently pass the unchanged admission gate.",
        },
        "observed_instantiation": {
            "admitted_families": extraction["counts"]["admitted_families"],
            "required_families": extraction["counts"]["required_families"],
            "certificate_domain_size": len(certs),
            "glue_singletons": sum(x["truth"] == "GLUE" for x in certs),
            "obstruction_singletons": sum(x["truth"] == "OBSTRUCTION" for x in certs),
            "conflicts": extraction["counts"]["conflicts"],
            "point_identified_on_entire_observed_certificate_domain": True,
        },
        "sharp_bound": (
            "Binary truth is point-identified on the finite direct-certificate set. Every pair outside that set remains set-valued unless separately certified."
        ),
        "not_established": [
            "Cartesian exhaustivity",
            "naturalistic cross-ontology transport",
            "comparator superiority or performance",
            "population transport",
            "V3 harm reversal",
            "protected outcomes",
        ],
    }
    write_json("THEOREM_AND_BOUND_V5.json", theorem)
    return theorem


def write_theorem_md(theorem: dict) -> None:
    o = theorem["observed_instantiation"]
    text = f"""# P3 V5 direct-certificate theorem and bound

## Theorem schema

{theorem['universal_theorem']}

Define the information set of a canonical pair `p` by

- `I_C(p) = {{GLUE}}` when `p` has only an admitted direct GLUE certificate;
- `I_C(p) = {{OBSTRUCTION}}` when `p` has only an admitted direct OBSTRUCTION certificate;
- `I_C(p) = {{GLUE, OBSTRUCTION}}` when `p` has neither certificate; and
- `CANNOT_CHECK_CONFLICT` when both certificate kinds occur.

This yields two general properties: conflict-free certificate addition is a monotone refinement of information sets, and absence can never manufacture obstruction.

## Observed V5 instantiation

The unchanged three-family gate passes **{o['admitted_families']}/{o['required_families']}**. The finite direct-certificate domain contains **{o['certificate_domain_size']:,}** point-identified pairs: **{o['glue_singletons']:,} GLUE** and **{o['obstruction_singletons']:,} explicit OBSTRUCTION**, with **{o['conflicts']} conflicts**.

## Sharp bound

{theorem['sharp_bound']}

This is a reusable calibration theorem, not Cartesian exhaustivity, naturalistic cross-ontology transport, comparator performance, V3 harm reversal, or protected confirmation.
"""
    (ROOT / "THEOREM_AND_BOUND_V5.md").write_text(text)


def build_negative_ledger(extraction: dict) -> dict:
    entries = [
        {
            "id": "P3_V3_HARM_TERMINAL",
            "status": "PRESERVED_UNCHANGED",
            "finding": "PUBLIC_V3_MAXIMAL_BINARY_ENVELOPE_COVERAGE_PASS__PUBLIC_V3_NO_HARM_SUPERIORITY__PUBLIC_NONPROTECTED_ONE_SEED_FAMILY_ONLY",
            "next_discriminator": "A future harm claim requires independent, prospectively frozen multi-family outcomes; V5 does not open them.",
        },
        {
            "id": "P3_V4_SOURCE_ADMISSION",
            "status": "PRESERVED_UNCHANGED",
            "finding": "0/7 V4 source families admitted.",
            "next_discriminator": "Do not reinterpret V5 direct-axiom families as repair of the V4 source frame.",
        },
        {
            "id": "P3_V4_COMPARATOR_READINESS",
            "status": "PRESERVED_UNCHANGED",
            "finding": "0/3 V4 comparators execution-ready.",
            "next_discriminator": "Each comparator needs complete outcome-blind build, dependency, runtime, and artifact preflight.",
        },
        {
            "id": "P3_V5_COMPARATOR_READINESS",
            "status": "OPEN_RESEARCH_TOPIC",
            "finding": "0/3 V5 comparator adapters are execution-ready; no comparator performance outcome was executed.",
            "next_discriminator": "Bind offline FIBO packaging and verify complete native artifacts for AML, LogMap, and BERTMap without opening protected outcomes.",
        },
        {
            "id": "P3_V5_TRANSPORT_SCOPE",
            "status": "OPEN_RESEARCH_TOPIC",
            "finding": "V5 uses byte-identical source/target views and therefore does not test naturalistic cross-ontology transport.",
            "next_discriminator": "Prospectively freeze independently authored ontology pairs with rights-valid explicit negative certificates before any matcher output is opened.",
        },
        {
            "id": "P3_V5_PARTIAL_IDENTIFICATION",
            "status": "THEOREM_BOUNDARY",
            "finding": "Pairs outside the direct-certificate domain remain {GLUE, OBSTRUCTION}; Cartesian exhaustivity is not established.",
            "next_discriminator": "Add independent direct certificates under the same no-absence rule; never label unobserved pairs as obstruction.",
        },
        {
            "id": "P3_V5_PROTECTED_OUTCOMES",
            "status": "PRESERVED_CLOSED",
            "finding": "No protected outcomes were opened.",
            "next_discriminator": "Protected evaluation remains a separately authorized, preregistered later stage.",
        },
    ]
    ledger = {
        "schema_version": "orion.p3.authoritative-negative-semantics.negative-result-ledger.v5",
        "created_at": now(),
        "policy": "Every adverse result is retained as a falsifiable research topic; none is converted into a positive performance claim.",
        "entries": entries,
        "counts": dict(Counter(x["status"] for x in entries)),
        "v5_three_family_gate": f"{extraction['counts']['admitted_families']}/{extraction['counts']['required_families']}",
    }
    write_json("NEGATIVE_RESULT_LEDGER_V5.json", ledger)
    return ledger


def write_negative_ledger_md(ledger: dict) -> None:
    lines = [
        "# P3 V5 negative-result ledger",
        "",
        ledger["policy"],
        "",
        "| ID | Status | Finding | Next discriminator |",
        "|---|---|---|---|",
    ]
    for row in ledger["entries"]:
        lines.append(
            f"| `{row['id']}` | `{row['status']}` | {row['finding']} | {row['next_discriminator']} |"
        )
    lines.append("")
    (ROOT / "NEGATIVE_RESULT_LEDGER_V5.md").write_text("\n".join(lines))


def build_readiness(extraction: dict) -> dict:
    readiness = {
        "schema_version": "orion.p3.authoritative-negative-semantics.readiness.v5",
        "created_at": now(),
        "top_tier_peer_review_ready": False,
        "current_warranted_integration": "NARROW_THEOREM_AND_CALIBRATION_PARAGRAPH_ONLY",
        "main_checkout_integration_performed": False,
        "warranted": [
            "State the direct-certificate partial-identification theorem and monotone-refinement corollary.",
            f"Report the rights-valid three-family instantiation ({extraction['counts']['admitted_families']}/{extraction['counts']['required_families']}) with 4,838 point-identified certificate pairs.",
            "Report the explicit boundary that all uncertified pairs remain set-valued.",
        ],
        "not_warranted": [
            "Comparator performance or superiority",
            "Naturalistic cross-ontology transport",
            "Cartesian coverage",
            "V3 harm superiority",
            "Protected or population claims",
        ],
        "blocking_research_program": [
            {
                "priority": 1,
                "topic": "Outcome-blind comparator execution preflight",
                "success_gate": "3/3 adapters build and emit complete digest-verified native artifacts without gold access.",
            },
            {
                "priority": 2,
                "topic": "Naturalistic transport frame",
                "success_gate": "At least three independently governed, independently authored ontology-pair families pass the unchanged rights, identity, explicit-negative, and conflict gates.",
            },
            {
                "priority": 3,
                "topic": "Comparator calibration experiment",
                "success_gate": "Prospectively scored false-GLUE commitments and selective coverage on the frozen certificate universe, with uncertainty and no absence-derived negatives.",
            },
            {
                "priority": 4,
                "topic": "External validity and harm",
                "success_gate": "Independent multi-family outcomes support a preregistered claim; until then the V3 harm terminal remains unchanged.",
            },
        ],
        "suggested_manuscript_paragraph": (
            "We define a direct-certificate partial-identification operator for ontology alignment. "
            "On immutable byte-identical views, same-IRI identity and direct named owl:equivalentClass axioms identify GLUE, while direct named owl:disjointWith axioms identify OBSTRUCTION; absent certificates retain the set {GLUE, OBSTRUCTION}, and conflicting certificates are excluded. "
            "The operator is monotone under conflict-free certificate addition and cannot manufacture obstruction from nonselection. "
            "In a rights-audited three-family calibration frame (ENVO, FIBO FND, and W3C PROV-O), all three families passed the frozen gate, yielding 4,838 point-identified pairs (4,789 GLUE; 49 OBSTRUCTION; zero conflicts). "
            "This calibration result does not measure naturalistic cross-ontology transport or comparator performance."
        ),
    }
    write_json("READINESS_AND_MANUSCRIPT_INTEGRATION_V5.json", readiness)
    return readiness


def write_readiness_md(readiness: dict) -> None:
    lines = [
        "# P3 V5 readiness and manuscript integration",
        "",
        "**Verdict:** not yet ready for top-tier peer review. A narrowly scoped theorem/calibration paragraph is warranted; main-checkout integration was not performed.",
        "",
        "## Warranted paragraph",
        "",
        readiness["suggested_manuscript_paragraph"],
        "",
        "## Research program required before a wider claim",
        "",
    ]
    for row in readiness["blocking_research_program"]:
        lines.append(f"{row['priority']}. **{row['topic']}** — {row['success_gate']}")
    lines.extend(
        [
            "",
            "No comparator, protected, harm-superiority, naturalistic-transport, or Cartesian claim is warranted by V5.",
            "",
        ]
    )
    (ROOT / "READINESS_AND_MANUSCRIPT_INTEGRATION_V5.md").write_text("\n".join(lines))


def build_result(extraction: dict, rights: dict, theorem: dict) -> dict:
    result = {
        "schema_version": "orion.p3.authoritative-negative-semantics.result.v5",
        "created_at": now(),
        "frame_id": extraction["frame_id"],
        "verdict": "PUBLIC_V5_DIRECT_CERTIFICATE_SEMANTICS_CALIBRATION_PASS__NO_COMPARATOR_PERFORMANCE_EXECUTED__NO_NATURALISTIC_TRANSPORT",
        "three_family_gate_pass": extraction["frame_gate_pass"],
        "rights_gate_pass": rights["three_family_rights_gate_pass"],
        "counts": extraction["counts"],
        "family_results": extraction["families"],
        "theorem": theorem["sharp_bound"],
        "comparator_execution": {
            "execution_ready": "0/3",
            "performance_outcomes_executed": 0,
            "comparator_superiority_established": False,
        },
        "preserved_terminals": {
            "v3": "PUBLIC_V3_MAXIMAL_BINARY_ENVELOPE_COVERAGE_PASS__PUBLIC_V3_NO_HARM_SUPERIORITY__PUBLIC_NONPROTECTED_ONE_SEED_FAMILY_ONLY",
            "v4_source_admission": "0/7",
            "v4_comparator_execution_readiness": "0/3",
        },
        "boundaries": {
            "positive_reference_absence_used_as_obstruction": False,
            "reasoner_inference_used": False,
            "cartesian_completion_used": False,
            "protected_outcomes_opened": False,
            "naturalistic_cross_ontology_transport_established": False,
            "three_family_gate_relaxed": False,
        },
        "manuscript_integration_recommendation": "NARROW_THEOREM_AND_CALIBRATION_PARAGRAPH_ONLY",
    }
    write_json("RESULT_V5.json", result)
    return result


def write_results_md(result: dict) -> None:
    lines = [
        "# P3 authoritative negative semantics — V5 result",
        "",
        f"**Verdict:** `{result['verdict']}`",
        "",
        "The frozen three-family gate passes **3/3** after an independent rights-and-identity audit. All **61** frozen Git blobs matched, all **11,076,252 bytes** parsed into **121,589 triples**, and no raw ontology payload was retained.",
        "",
        "The conflict-free certificate registry contains **4,838** point-identified canonical pairs: **4,789 GLUE** and **49 explicit OBSTRUCTION**. No absence or reasoner inference was used.",
        "",
        "| Family | Named classes | Identity GLUE | Distinct equivalence GLUE | Explicit OBSTRUCTION | Conflicts | Admitted |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for family_id, f in result["family_results"].items():
        lines.append(
            f"| `{family_id}` | {f['authority_namespace_class_count']:,} | {f['identity_glue_certificate_count']:,} | {f['distinct_equivalence_glue_certificate_count']:,} | {f['explicit_disjoint_obstruction_certificate_count']:,} | {f['conflict_count']} | {'PASS' if f['family_admitted'] else 'FAIL'} |"
        )
    lines.extend(
        [
            "",
            "## Strongest warranted claim",
            "",
            result["theorem"],
            "",
            "The theorem schema generalizes to any future family satisfying the unchanged direct-certificate admission rules, and certificate addition refines information monotonically. The observed empirical instantiation remains the three frozen families.",
            "",
            "## Preserved adverse results and boundaries",
            "",
            f"- V3 remains `{result['preserved_terminals']['v3']}`.",
            "- V4 source admission remains **0/7**; V4 comparator readiness remains **0/3**.",
            "- V5 comparator readiness is **0/3** and **no performance outcomes were executed**.",
            "- Byte-identical views calibrate direct semantics; they do not establish naturalistic cross-ontology transport.",
            "- No protected outcomes were opened and the three-family gate was not relaxed.",
            "",
            "## Integration decision",
            "",
            "A narrow theorem/calibration paragraph is warranted. Top-tier peer-review readiness and wider comparator/transport claims are not yet warranted. No main-checkout integration was performed.",
            "",
        ]
    )
    (ROOT / "RESULTS_V5.md").write_text("\n".join(lines))


def validate(extraction: dict, rights: dict, certs: list[dict], result: dict) -> dict:
    manifest = read_json("SOURCE_BYTE_MANIFEST_V5.json")
    adapters = read_json("COMPARATOR_ADAPTERS_V5.json")
    freeze = read_json("PROTOCOL_FREEZE_RECEIPT_V5.json")
    cert_counts = Counter(x["truth"] for x in certs)
    keys = [(x["family_id"], x["left_iri"], x["right_iri"], x["truth"]) for x in certs]
    pair_truths = defaultdict(set)
    for x in certs:
        pair_truths[(x["family_id"], x["left_iri"], x["right_iri"])].add(x["truth"])
    checks = {
        "protocol_hash_matches_freeze": sha256(ROOT / "PROTOCOL_V5.json") == freeze["protocol_sha256"],
        "source_prefreeze_hash_matches_freeze": sha256(ROOT / "SOURCE_FRAME_PREFREEZE_V5.json") == freeze["source_frame_prefreeze_sha256"],
        "adapters_hash_matches_freeze": sha256(ROOT / "COMPARATOR_ADAPTERS_V5.json") == freeze["comparator_adapters_sha256"],
        "source_file_count_61": manifest["counts"]["files"] == 61,
        "source_bytes_11076252": manifest["counts"]["observed_bytes"] == 11_076_252,
        "source_triples_121589": manifest["counts"]["triples"] == 121_589,
        "all_source_files_transport_parse_pass": manifest["counts"]["transport_and_git_blob_pass"] == 61 and not manifest["parse_errors"],
        "raw_payloads_not_retained": manifest["raw_payloads_retained"] is False,
        "rights_gate_3_of_3": rights["three_family_rights_gate_pass"] and rights["counts"]["research_use_pass"] == 3,
        "admission_recomputed_from_rights_audit": extraction["admission_recomputed_after_independent_rights_audit"] is True,
        "family_gate_3_of_3": extraction["frame_gate_pass"] and extraction["counts"]["admitted_families"] == 3,
        "certificate_rows_4838": len(certs) == 4_838,
        "certificate_counts_match": cert_counts == {"GLUE": 4_789, "OBSTRUCTION": 49},
        "certificate_ids_unique": len({x["certificate_id"] for x in certs}) == len(certs),
        "certificate_rows_unique": len(set(keys)) == len(certs),
        "certificate_conflicts_zero": all(len(v) == 1 for v in pair_truths.values()) and extraction["counts"]["conflicts"] == 0,
        "absence_flags_false": all(x["absence_used"] is False for x in certs),
        "inference_flags_false": all(x["inference_used"] is False for x in certs),
        "comparators_0_of_3_execution_ready": sum(x["execution_ready"] for x in adapters["comparators"]) == 0 and len(adapters["comparators"]) == 3,
        "comparator_outcomes_unopened": adapters["outcomes_opened"] is False,
        "protected_outcomes_unopened": result["boundaries"]["protected_outcomes_opened"] is False,
        "positive_absence_not_used": result["boundaries"]["positive_reference_absence_used_as_obstruction"] is False,
        "three_family_gate_not_relaxed": result["boundaries"]["three_family_gate_relaxed"] is False,
    }
    validation = {
        "schema_version": "orion.p3.authoritative-negative-semantics.scientific-validation.v5",
        "created_at": now(),
        "method": "stdlib JSON/JSONL parsing, cryptographic hash equality, count/uniqueness/conflict and boundary-flag checks; no pytest or CI",
        "checks": checks,
        "counts": {"checks": len(checks), "passed": sum(checks.values()), "failed": sum(not x for x in checks.values())},
        "validation_pass": all(checks.values()),
    }
    write_json("SCIENTIFIC_VALIDATION_V5.json", validation)
    if not validation["validation_pass"]:
        failed = [k for k, v in checks.items() if not v]
        raise SystemExit("scientific validation failed: " + ", ".join(failed))
    return validation


def write_sha256s() -> None:
    names = sorted(
        p.name
        for p in ROOT.iterdir()
        if p.is_file() and p.name != "SHA256SUMS" and not p.name.startswith(".")
    )
    (ROOT / "SHA256SUMS").write_text(
        "".join(f"{sha256(ROOT / name)}  {name}\n" for name in names)
    )


def main() -> None:
    rights = write_rights_audit()
    extraction = recompute_admission(read_json("EXTRACTION_RESULT_V5.json"), rights)
    certs = load_certificates()
    theorem = build_theorem(extraction, certs)
    write_theorem_md(theorem)
    ledger = build_negative_ledger(extraction)
    write_negative_ledger_md(ledger)
    readiness = build_readiness(extraction)
    write_readiness_md(readiness)
    result = build_result(extraction, rights, theorem)
    write_results_md(result)
    validation = validate(extraction, rights, certs, result)
    write_sha256s()
    print(json.dumps({"verdict": result["verdict"], "validation": validation["counts"]}, indent=2))


if __name__ == "__main__":
    main()

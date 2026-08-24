#!/usr/bin/env python3
"""Build the bounded P1 V4 public-standard construct-feasibility packet.

Requires temporary response bytes in .capture_tmp produced after the V4/V4A
freezes. Retains only hashes, bounded tokens, and exact aggregate decisions.
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from bs4 import BeautifulSoup

LANE = Path(__file__).resolve().parent
TMP = LANE / ".capture_tmp"
TERMINAL = (
    "P1_V4_PUBLIC_POSTPUBLICATION_STANDARD_SCAFFOLD_FEASIBLE__"
    "ZERO_OF_TWELVE_OWNER_ALGEBRA_GROUPS_SUFFICIENT__"
    "SCIENTIFIC_ACTION_GOLD_AND_CONSTRUCT_VALIDITY_CANNOT_CHECK"
)


def sha_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def dump(name: str, obj: object) -> None:
    (LANE / name).write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n")


def normalized_text_from_html(name: str, selector: str) -> tuple[str, str]:
    b = (TMP / name).read_bytes()
    soup = BeautifulSoup(b, "html.parser")
    node = soup.select_one(selector)
    if node is None:
        raise RuntimeError(f"missing selector {selector} in {name}")
    text = " ".join(node.get_text(" ", strip=True).split())
    return text, sha_bytes(text.encode())


def pdf_text(name: str) -> tuple[str, str]:
    path = TMP / name
    text = path.read_text(errors="replace")
    text = "\n".join(line.rstrip() for line in text.splitlines()).strip() + "\n"
    return text, sha_bytes(text.encode())


def counts(text: str, terms: list[str]) -> dict[str, int]:
    out = {}
    for term in terms:
        pat = r"(?<![A-Za-z0-9_-])" + re.escape(term) + r"(?![A-Za-z0-9_-])"
        n = len(re.findall(pat, text, flags=re.I))
        if n:
            out[term] = n
    return out


def cap(name: str, *, status: int, final_url: str, ctype: str, requested_url=None, last_modified=None,
        etag=None, selector=None, text_file=None, identity=None, rights=None,
        pages=None, family=None, institutional_role=None) -> dict:
    raw = (TMP / name).read_bytes()
    captured_at = datetime.fromtimestamp((TMP / name).stat().st_mtime, timezone.utc).isoformat()
    row = {
        "source_id": name.rsplit(".", 1)[0],
        "institutional_family": family,
        "institutional_role": institutional_role,
        "requested_route": requested_url,
        "final_url": final_url,
        "captured_at_utc": captured_at,
        "http_status": status,
        "content_type": ctype,
        "content_length_bytes": len(raw),
        "response_sha256": sha_bytes(raw),
        "etag": etag,
        "last_modified": last_modified,
        "identity": identity,
        "identity_verified": status == 200 and identity is not None,
        "rights": rights,
        "raw_response_retained": False,
    }
    if pages is not None:
        row["pdf_pages"] = pages
    if status == 200 and selector:
        text, text_sha = normalized_text_from_html(name, selector)
        row["bounded_extraction"] = {
            "selector": selector,
            "normalized_selected_text_sha256": text_sha,
            "allowlisted_token_counts": counts(text, TERMS),
        }
    if status == 200 and text_file:
        text, text_sha = pdf_text(text_file)
        row["bounded_extraction"] = {
            "selector": "pdftotext normalized text",
            "normalized_selected_text_sha256": text_sha,
            "allowlisted_token_counts": counts(text, TERMS),
        }
    if status != 200:
        row["disposition"] = "CANNOT_CHECK_HTTP_NON_2XX__NO_SUBSTITUTE"
    return row


TERMS = [
    "retraction", "retracted", "removal", "removed", "expression of concern",
    "correction", "corrected", "update", "updated", "withdrawal", "withdrawn",
    "version of record", "current", "status", "policy", "maintain", "preserve",
    "notice", "isReplacedBy", "Replaces", "isVersionOf", "hasVersion", "updates",
    "addendum", "commentary", "corrected-article", "correction-forward",
    "retracted-article", "retraction-forward",
]


def main() -> None:
    now = datetime.now(timezone.utc).isoformat()
    protocol = json.loads((LANE / "PROTOCOL_V4.json").read_text())
    amendment = json.loads((LANE / "SOURCE_INTERFACE_AMENDMENT_V4A.json").read_text())
    # The exact files and protocol-frozen identities captured in this run.
    rows = [
        cap("NISO_CREC_RP45_LANDING.html", status=200,
            final_url="https://www.niso.org/publications/rp-45-2024-crec",
            ctype="text/html; charset=UTF-8", last_modified="Sun, 23 Aug 2026 19:00:05 GMT", etag='"1787511605"',
            selector="main#content", family="NISO", institutional_role="consensus recommended-practice publisher",
            identity="NISO RP-45-2024 CREC official landing page",
            rights="LANDING_PAGE_REUSE_TERMS_NOT_SEPARATELY_BOUND__PDF_RIGHTS_BOUND_BELOW"),
        cap("NISO_CREC_RP45_PDF.pdf", status=200,
            final_url="https://groups.niso.org/higherlogic/ws/public/download/30869/NISO_RP-45-2024_CREC.pdf",
            ctype=None, text_file="NISO_CREC_RP45_PDF.txt", pages=66,
            family="NISO", institutional_role="consensus recommended-practice publisher",
            identity="NISO RP-45-2024; DOI 10.3789/niso-rp-45-2024; NISO CREC Working Group; 2024",
            rights="COPYRIGHT_NISO_2024__NONCOMMERCIAL_REPRODUCTION_PERMISSION_WITH_ACKNOWLEDGEMENT__NO_SPDX_ASSERTED__NOT_R7_TARGET_ALGEBRA_RIGHTS"),
        cap("CROSSREF_CROSSMARK.html", status=200,
            final_url="https://www.crossref.org/documentation/crossmark/", ctype="text/html",
            selector="div#content", family="Crossref", institutional_role="Crossmark metadata operator",
            identity="Crossref official Crossmark documentation",
            rights="CC-BY-4.0_SITE_CONTENT__NOT_R7_TARGET_ALGEBRA_RIGHTS"),
        cap("CROSSREF_POLICY_PAGE.html", status=200,
            final_url="https://www.crossref.org/documentation/crossmark/crossmark-policy-page/", ctype="text/html",
            selector="div#content", family="Crossref", institutional_role="Crossmark policy-page interface operator",
            identity="Crossref official Update policy page documentation",
            rights="CC-BY-4.0_SITE_CONTENT__NOT_R7_TARGET_ALGEBRA_RIGHTS"),
        cap("CROSSREF_RELATIONSHIPS.html", status=200,
            final_url="https://www.crossref.org/documentation/schema-library/markup-guide-metadata-segments/relationships/", ctype="text/html",
            selector="div#content", family="Crossref", institutional_role="DOI relationship metadata operator",
            identity="Crossref official Relationships documentation",
            rights="CC-BY-4.0_SITE_CONTENT__NOT_R7_TARGET_ALGEBRA_RIGHTS"),
        cap("NLM_JATS_RELATED_ARTICLE.html", status=200,
            final_url="https://jats.nlm.nih.gov/publishing/tag-library/1.4/element/related-article.html",
            ctype="text/html; charset=utf-8", last_modified="Fri, 25 Oct 2024 14:27:53 GMT",
            selector="div#text", family="NLM_JATS", institutional_role="JATS tag-library host",
            identity="JATS Publishing Tag Library 1.4, related-article element",
            rights="EXACT_PAGE_REUSE_LICENCE_NOT_BOUND__BOUNDED_FACTUAL_TOKENS_AND_HASH_ONLY__NOT_R7_TARGET_ALGEBRA_RIGHTS"),
        cap("COPE_RETRACTION_GUIDELINES.html", status=200,
            requested_url="https://publicationethics.org/retraction-guidelines",
            final_url="https://publicationethics.org/guidance/guideline/retraction-guidelines",
            ctype="text/html; charset=UTF-8", selector="main#main-content", family="COPE",
            institutional_role="publication-ethics policy publisher",
            identity="COPE Retraction guidelines official page; last reviewed 29 August 2025",
            rights="LANDING_PAGE_REUSE_TERMS_NOT_SEPARATELY_BOUND__PDF_CC-BY-NC-ND-4.0_BOUND_BELOW"),
        cap("COPE_RETRACTION_GUIDELINES_PDF.pdf", status=200,
            final_url="https://publicationethics.org/media/848/download?attachment",
            ctype="application/pdf", last_modified="Mon, 01 Sep 2025 16:43:14 GMT",
            text_file="COPE_RETRACTION_GUIDELINES_PDF.txt", pages=17, family="COPE",
            institutional_role="publication-ethics policy publisher",
            identity="COPE Retraction Guidelines Version 3, August 2025; DOI 10.24318/cope.2019.1.4",
            rights="CC-BY-NC-ND-4.0__BOUNDED_FACTUAL_TOKENS_ONLY__NOT_R7_TARGET_ALGEBRA_RIGHTS"),
        cap("ICMJE_CORRECTIONS_ROUTE.html", status=404,
            final_url="https://www.icmje.org/recommendations/browse/publishing-and-editorial-issues/corrections-retractions-republications-and-version-control.html",
            ctype="text/html; charset=iso-8859-1", family="ICMJE",
            institutional_role="medical-journal recommendation publisher",
            identity=None, rights="CANNOT_CHECK_HTTP_404"),
    ]
    for row in rows:
        if row["requested_route"] is None:
            row["requested_route"] = row["final_url"]
    receipt = {
        "schema_version":"orion.p1.owner-algebra-construct-validity.source-capture-rights-receipt.v4",
        "captured_and_adjudicated_at":now,
        "protocol_sha256":sha(LANE / "PROTOCOL_V4.json"),
        "amendment_sha256":sha(LANE / "SOURCE_INTERFACE_AMENDMENT_V4A.json"),
        "sources":rows,
        "capture_summary":{
            "frozen_routes_after_amendment":9,
            "http_200_documents":8,
            "http_non_2xx_documents":1,
            "accessible_institutional_families":["COPE","Crossref","NISO","NLM_JATS"],
            "accessible_institutional_family_count":4,
            "raw_html_or_pdf_retained":False,
            "case_or_outcome_content_accessed":False,
        },
        "rights_boundary":{
            "crossref_documentation":"CC-BY-4.0 displayed by exact captured pages",
            "cope_pdf":"CC-BY-NC-ND-4.0 displayed in exact captured PDF",
            "niso_pdf":"NISO 2024 copyright with stated noncommercial reproduction permission and acknowledgement conditions; no SPDX identifier asserted",
            "jats_page":"exact reuse licence CANNOT_CHECK; only digest and factual element/token presence retained",
            "target_algebra":"No captured source licenses, owns, signs, delegates, or reviews the R7 target algebra.",
            "legal_advice":False,
        },
        "terminal":"P1_V4_SOURCE_PROVENANCE_HASHES_BOUND__PUBLIC_STANDARD_DOCUMENT_RIGHTS_HETEROGENEOUS__TARGET_ALGEBRA_RIGHTS_CANNOT_CHECK",
    }
    dump("SOURCE_CAPTURE_AND_RIGHTS_RECEIPT_V4.json", receipt)

    envelope = {
        "schema_version":"orion.p1.owner-algebra-construct-validity.standard-native-action-envelope.v4",
        "authority":"SOURCE_NATIVE_STANDARD_SCAFFOLD_ONLY__NO_R7_CROSSWALK",
        "source_families":[
            {
                "family":"NISO_CREC_RP45_2024",
                "native_objects":["retraction","removal","expression of concern","retraction notice","retraction-related metadata"],
                "source_native_role":"Recommended metadata creation, transfer, display, linking and preservation practices for specified editorial events.",
                "bounded_scope":"Corrections/errata/corrigenda/addenda are expressly outside the principal CREC scope even though mentioned.",
                "closed_r7_action_algebra":False,
                "r7_owner_or_delegation":False,
            },
            {
                "family":"COPE_RETRACTION_GUIDELINES_V3_2025",
                "native_objects":["retraction","correction","expression of concern","retraction with replacement","retraction with removal"],
                "source_native_role":"Formal COPE policy advising editors and publishers when retraction is or is not appropriate and who issues it.",
                "bounded_scope":"Guideline concerns scholarly retraction; corrections and expressions of concern are covered elsewhere except as alternatives/boundaries.",
                "closed_r7_action_algebra":False,
                "r7_owner_or_delegation":False,
            },
            {
                "family":"CROSSREF_CROSSMARK_AND_RELATIONSHIPS",
                "native_objects":["current status","corrections","retractions","updates","update policy","isReplacedBy","Replaces","isVersionOf","hasVersion"],
                "source_native_role":"Publisher-deposited status/update/relationship metadata and policy-page interface; Crossref records information supplied by members.",
                "bounded_scope":"Crossref exposes record status/relations and publisher policy, not an exhaustive case-level scientific action decision.",
                "closed_r7_action_algebra":False,
                "r7_owner_or_delegation":False,
            },
            {
                "family":"NLM_JATS_1_4_RELATED_ARTICLE",
                "native_objects":["related-article","related-article-type","corrected-article","companion"],
                "source_native_role":"Markup relation naming and linking between separately published journal articles.",
                "bounded_scope":"The element page gives examples of relationship purpose; it does not close or authorize an R7 action vocabulary.",
                "closed_r7_action_algebra":False,
                "r7_owner_or_delegation":False,
            },
        ],
        "exact_construction":{
            "institutional_families_byte_bound":4,
            "families_with_explicit_postpublication_native_token":4,
            "families_distinguishing_status_relation_policy_or_notice_roles":4,
            "scaffold_gate_pass":True,
            "construction":"A four-family typed envelope whose observations are native editorial events, notices, statuses, update relations and publisher policies; no total or partial function to an R7 decision is defined.",
        },
        "nonidentification_witnesses":[
            "COPE treats correction or expression of concern as boundary alternatives to retraction while delegating case decisions to editors; the public standard is not a case adjudication.",
            "CREC treats retraction, removal and expression of concern as metadata communication objects and excludes other postpublication notices from its principal scope.",
            "Crossmark communicates current publisher-supplied status and policy rather than defining an exhaustive universal action terminal.",
            "JATS related-article-type names a relation/purpose and supplies examples; it is not execution or recommendation authority.",
        ],
        "forbidden_promotions":[
            "No native token is scientific-action gold.",
            "No source event is mapped to KEEP_SEARCH, KEEP_COMPILE, KEEP_REPAIR, REVISE_MEASUREMENT, REFORMULATE_OBJECTIVE, REFORMULATE_BOUNDARY or UNRESOLVED.",
            "No publisher/editor authority is transferred to Orion or the R7 vocabulary owner.",
            "No standard document is an independent semantic review of an R7 algebra.",
        ],
        "terminal":"P1_V4_FOUR_FAMILY_SOURCE_NATIVE_POSTPUBLICATION_STANDARD_SCAFFOLD_FEASIBLE__NO_R7_DECISION_CROSSWALK",
    }
    dump("STANDARD_NATIVE_ACTION_ENVELOPE_V4.json", envelope)

    groups = [
        ("G01","closed_world","No captured source asserts that the seven R7 targets are exhaustive.",[],"R7 vocabulary owner must sign closed_world=true for the exact seven-target algebra."),
        ("G02","targets[*].scientific_process_coordinate","Standards define their own editorial/status objects, not exhaustive R7 scientific-process coordinates.",["NISO: retraction/removal/EoC metadata objects","Crossref: current status"],"R7 vocabulary owner must ratify exhaustive, overlap-resolved coordinates."),
        ("G03","targets[*].postpublication_coordinate","Public standards supply strong postpublication coordinate analogues but none assigns one exact coordinate or NONE to every R7 target.",["COPE: retraction/correction/EoC/replacement/removal","NISO: retraction/removal/EoC","Crossref: correction/retraction/update"],"R7 vocabulary owner must assign the exact coordinate or NONE per target."),
        ("G04","targets[*].licensed_postpublication_operations","Recommendations and publisher policies are not the exhaustive licensed R7 operation sets.",["COPE formal policy for editors/publishers","Crossref publisher update policy"],"Owner must enumerate exhaustive licensed operations for every target."),
        ("G05","targets[*].forbidden_postpublication_operations","COPE supplies retraction contraindications, but not the exhaustive forbidden V8 operation complement for seven R7 targets.",["COPE: when retraction is not appropriate"],"Owner must enumerate exhaustive forbidden operations for every target."),
        ("G06","decision_probe_typing","The sources distinguish notices, status metadata, relations, policies and editorial actions, but contain no owner-approved R7 probe/decision bridge table or explicit NONE.",["CREC: event versus notice/metadata","Crossref: status versus update relation/policy","JATS: relation link"],"Owner must retain decision/probe separation and sign EXPLICIT_TABLE or NONE."),
        ("G07","targets[*].recommendation_authority","COPE advises editors/publishers and Crossref records publisher policy; neither grants R7 target recommendation authority.",["COPE: formal advisory policy","Crossref: publisher-owned update policy"],"R7 vocabulary owner and host-authority owner must jointly bind per-target recommendation authority."),
        ("G08","targets[*].execution_authority","Editorial standards locate action with editors/publishers; they do not bind the P1 host or grant SYSTEM execution.",["COPE: editors/publishers issue retractions"],"Host-authority owner must assign NONE, EXTERNAL_OWNER_ONLY, or SYSTEM per target."),
        ("G09","terminal_behavior.{abstention,error,timeout,malformed,unsupported}","COPE gives an inconclusive-evidence boundary, but no source defines all five R7 non-success terminals.",["COPE: inconclusive evidence can lead to expression-of-concern consideration"],"Owner must bind all five fail-closed terminals."),
        ("G10","rights.{public_archive_url,reuse_licence_spdx,licence_text_sha256}","Document reuse rights are heterogeneous and apply to the documents, not a completed R7 target algebra.",["Crossref docs: CC-BY-4.0","COPE PDF: CC-BY-NC-ND-4.0","NISO PDF: custom noncommercial permission"],"Target-algebra rights holder must publish the exact completed algebra and exact applicable licence-text hash."),
        ("G11","ratification","Institutional publication and local response hashing are not a content-addressed signature by the R7 owner over a completed algebra.",[],"R7 owner or delegated custodian must sign the completed algebra with identity, delegation, digest, key and timestamp."),
        ("G12","ratification.independent_semantic_reviewer","Consensus standards and cross-institution agreement are not independent semantic review of an authored R7 algebra.",[],"An independent reviewer with no algebra authorship or case-outcome custody must issue a content-addressed CONFORMANT review."),
    ]
    # bind exact required custodians from unchanged V8 registry
    registry=json.loads(Path(protocol["predecessors"]["v8_custodian_registry"]["path"]).read_text())
    by_field={r["field_path"]:r for r in registry["requirements"]}
    decisions=[]
    for gid,field,reason,analogues,next_d in groups:
        req=by_field[field]
        decisions.append({
            "group_id":gid,"field_path":field,
            "required_custodian":req["required_custodian"],
            "required_source":req["required_source"],
            "source_native_structural_analogues":analogues,
            "structural_analogue_observed":bool(analogues),
            "named_custodian_authorship_or_explicit_delegation_evidenced":False,
            "exact_r7_target_coverage_and_exhaustiveness":False,
            "applicable_completed_target_algebra_rights_bound":False,
            "all_schema_subfields_satisfied":False,
            "counts_as_sufficient_owner_group":False,
            "sufficiency":"INSUFFICIENT",
            "reason":reason,
            "next_discriminator":next_d,
        })
    feasibility={
        "schema_version":"orion.p1.owner-algebra-construct-validity.owner-group-feasibility.v4",
        "authority":"PUBLIC_STANDARD_CONSTRUCT_FEASIBILITY_ONLY",
        "protocol_sha256":sha(LANE / "PROTOCOL_V4.json"),
        "amendment_sha256":sha(LANE / "SOURCE_INTERFACE_AMENDMENT_V4A.json"),
        "v8_registry_sha256":protocol["predecessors"]["v8_custodian_registry"]["sha256"],
        "decision_rule":"Every group is conjunctive. Structural analogues contribute zero unless the exact required custodian/delegation, R7 coverage/exhaustiveness, schema subfields, and applicable target-algebra rights all pass.",
        "field_decisions":decisions,
        "counts":{
            "requirement_groups":12,
            "groups_with_source_native_structural_analogue":sum(d["structural_analogue_observed"] for d in decisions),
            "groups_with_named_custodian_or_delegation":0,
            "sufficient_owner_groups":0,
            "scientific_action_gold_cells":0,
        },
        "exact_nondelegation_upper_bound":{
            "named_custodian_conjunct_true_groups":0,
            "maximum_sufficient_groups":0,
            "proof":"For every group, sufficiency implies its named-custodian/delegation conjunct. The conjunct is false in all twelve rows; therefore every sufficiency indicator is zero and their sum is zero.",
            "future_owner_signed_algebra_impossible":False,
        },
        "adapter_rerun":{"performed":False,"v8_720_survivors_changed":False,"reason":"The V8 execution precondition requires a completed licensed signed owner algebra and independent CONFORMANT review; V4 supplies neither."},
        "terminal":TERMINAL,
    }
    dump("OWNER_GROUP_FEASIBILITY_V4.json", feasibility)

    result={
        "schema_version":"orion.p1.owner-algebra-construct-validity.result.v4",
        "result_id":"P1.V4.PUBLIC.POSTPUBLICATION.STANDARD.CONSTRUCT.FEASIBILITY.RESULT",
        "generated_at":now,
        "authority":"PUBLIC_STANDARD_SEMANTICS_PROVENANCE_AND_EXACT_CONSTRUCT_FEASIBILITY_ONLY",
        "terminology_amendment_sha256":sha(LANE / "CLAIM_TERMINOLOGY_AMENDMENT_V4B.json"),
        "aggregate_count_correction_sha256":sha(LANE / "AGGREGATE_COUNT_CORRECTION_V4C.json"),
        "institutional_family_distinctness_boundary":"Distinct source institutions only; no statistical, ownership, reviewer, or custody independence is claimed.",
        "rights_language_boundary":"Rights-bounded nonredistributive evidence handling, not a legal determination and not rights over an R7 target algebra.",
        "source_capture_receipt_sha256":sha(LANE / "SOURCE_CAPTURE_AND_RIGHTS_RECEIPT_V4.json"),
        "standard_native_envelope_sha256":sha(LANE / "STANDARD_NATIVE_ACTION_ENVELOPE_V4.json"),
        "owner_group_feasibility_sha256":sha(LANE / "OWNER_GROUP_FEASIBILITY_V4.json"),
        "positive_result":"Four distinct institutional source families are byte-bound and expose a rights-bounded nonredistributive scaffold of postpublication editorial events, notices, current-status metadata, update relations, publisher policies and relation markup. This is a source-native standards envelope, not an R7 decision algebra or case-level scientific action.",
        "exact_feasibility_result":"Under the unchanged V8 conjunctive custodian rule, the captured library evidences named-custodian authorship or delegation for 0/12 groups. The custodian-nondelegation upper bound is therefore exactly 0 sufficient groups even though 9/12 groups have at least one structural public-standard analogue.",
        "owner_algebra":{"requirement_groups":12,"structural_analogue_groups":9,"named_custodian_or_delegation_groups":0,"sufficient_groups":0},
        "scientific_action_gold_cells":0,
        "construct_validity":"CANNOT_CHECK",
        "adapter":{"rerun":False,"fully_certified_unchanged":0,"known_rejected_unchanged":116929,"not_disproved_but_uncertified_unchanged":720},
        "readiness":{"before":"NOT_SUBMISSION_READY","after":"NOT_SUBMISSION_READY","changed":False,"reason":"No scientific-action gold, eligible naturalistic dossiers, signed owner algebra, target-algebra rights, independent semantic review, protected execution or independent scorer custody was created."},
        "current_terminal_supersedes_v3":False,
        "next_discriminator":"The R7 vocabulary owner or formally delegated custodian and host/rights owners must complete, license and sign the exact seven-target algebra; an independent reviewer must issue CONFORMANT review. Only then may the unchanged 117,649-map audit run, followed separately by owner-separated scientific-action adjudication on eligible cases.",
        "not_warranted":[
            "A retraction, correction, removal, expression-of-concern, update or relation token is an R7 decision.",
            "A public standard is owner ratification, host authority, or independent R7 semantic review.",
            "Any scientific-action gold cell or naturalistic effect exists.",
            "The 720 V8 survivor maps were adjudicated or changed.",
            "P1 is ready for top-tier submission or peer review.",
        ],
        "terminal":TERMINAL,
    }
    dump("RESULT_V4.json", result)

    theorem = f"""# Custodian-nondelegation upper bound (P1 V4)\n\n## Frozen setting\n\nLet $G=\\{{g_1,\\ldots,g_{{12}}\\}}$ be the twelve requirement groups in the byte-bound V8 custodian registry (`{protocol['predecessors']['v8_custodian_registry']['sha256']}`). For a frozen source library $S$, define\n\n$$\\operatorname{{Suff}}(g,S)=A_g(S)\\land C_g(S)\\land L_g(S)\\land E_g(S),$$\n\nwhere $A_g$ is named-custodian authorship or explicit delegation, $C_g$ is exact R7 target coverage, $L_g$ is applicable completed-target-algebra rights, and $E_g$ is satisfaction of all schema and exhaustiveness conjuncts. This is not a new admission rule; it is the V8 rule written as a conjunction.\n\n## Theorem\n\nFor every $g$, $\\operatorname{{Suff}}(g,S)\\le A_g(S)$. Hence\n\n$$\\sum_{{g\\in G}}\\operatorname{{Suff}}(g,S)\\le \\sum_{{g\\in G}}A_g(S).$$\n\nIf no captured source is authored by the named R7/host/target-rights/review custodian and no source contains explicit delegation from that custodian over the completed R7 algebra, then the right-hand side is zero and exactly zero requirement groups can be sufficient.\n\n## Proof\n\nConjunction elimination gives $A_g(S)$ from $\\operatorname{{Suff}}(g,S)$, so each Boolean sufficiency indicator is bounded by its authority indicator. Summing preserves the inequality. V4 evaluates $A_g(S)=0$ in all twelve frozen rows. Nonnegativity then gives both an upper and lower bound of zero. $\\square$\n\n## Exact V4 evaluation\n\n- Accessible authoritative institutional families: **4** (NISO, Crossref, NLM/JATS, COPE).\n- Source-native structural-analogue groups: **9/12**.\n- Named-custodian/delegation groups: **0/12**.\n- Sufficient owner-algebra groups: **0/12**.\n- Scientific-action gold cells: **0**.\n\n## Scope boundary\n\nThis theorem says web standards cannot substitute for the named owner/custodian conjunct in this frozen registry. It does **not** prove that a future owner-signed algebra is impossible, that any postpublication standard is defective, or that any R7 map is false. The 720 V8 maps remain `CANNOT_CHECK`; the map audit was not rerun.\n"""
    (LANE / "CUSTODIAN_NONDELEGATION_THEOREM_V4.md").write_text(theorem)

    report = f"""# P1 V4 public postpublication standard construct-validity report\n\n## Question and precommitment\n\nBefore any source capture, V4 froze whether authoritative public postpublication standards could (i) construct a lawful source-native action/status scaffold and (ii) make any unchanged V8 owner-algebra group sufficient without case text, outcomes, or self-assigned authority. The protocol digest is `{sha(LANE/'PROTOCOL_V4.json')}`. A parser-only V4A amendment bound raw pre-amendment hashes, excluded dynamic navigation/news material, admitted official Crossref casing, and froze the official linked COPE PDF before fetching it; its digest is `{sha(LANE/'SOURCE_INTERFACE_AMENDMENT_V4A.json')}`.\n\n## Claim-language amendment\n\nV4B fixes two interpretation boundaries before validation: source families are distinct institutions, not statistically/custodially independent, and the scaffold is rights-bounded/nonredistributive rather than a legal determination. Its digest is `{sha(LANE/'CLAIM_TERMINOLOGY_AMENDMENT_V4B.json')}`. Counts and terminal are unchanged.\n\n## Aggregate-count correction\n\nThe first native validation pass recomputed the field table and corrected a summary transcription from 8 to **9/12** structural-analogue groups (G02--G10). V4C digest: `{sha(LANE/'AGGREGATE_COUNT_CORRECTION_V4C.json')}`. Sufficient groups, gold, terminal and readiness remain unchanged.\n\n## Sources and exact provenance\n\nEight 200-response documents from four institutional families were byte-bound; the frozen ICMJE route returned HTTP 404 and was not replaced by a search snippet or third-party copy. The source receipt contains requested/final URLs, response sizes, SHA-256 hashes, timestamps, response headers where supplied, normalized content hashes, bounded token counts, document identity and rights disposition. Raw HTML/PDF and extracted text were deleted.\n\nThe strongest accessible standards were:\n\n1. **NISO RP-45-2024 CREC**, DOI 10.3789/niso-rp-45-2024, 66 pages: a consensus recommended practice for communicating retractions, removals and expressions of concern through metadata, notices and display. Its stated permissions are noncommercial and conditional, not an SPDX licence for an R7 algebra.\n2. **COPE Retraction Guidelines, Version 3 (August 2025)**, DOI 10.24318/cope.2019.1.4, 17 pages, CC BY-NC-ND 4.0: formal policy for editors/publishers on retraction and boundary alternatives.\n3. **Crossref Crossmark, update-policy and relationship documentation**, captured under displayed CC BY 4.0 site terms: member-supplied current-status/update metadata, publisher policy, and typed DOI relations.\n4. **NLM JATS Publishing Tag Library 1.4 `<related-article>`**: a structured relation element and relation-purpose examples; exact page reuse licensing remained `CANNOT_CHECK`, so only digest and bounded factual tokens were retained.\n\n## Positive construction result\n\nThe frozen scaffold gate passes: four distinct institutional families expose exact native postpublication objects and distinguish at least one of event, notice, status, relation, metadata or policy roles. V4 therefore constructs a four-family typed **standards envelope**. It is stronger than raw metadata co-occurrence because each type is source-native and byte-bound. It deliberately defines no crosswalk to an R7 decision.\n\n## Decisive construct result\n\nPublic standards improve the scaffold but cannot supply the ownership relation that makes it scientific-action gold. Nine of twelve groups have a structural analogue, yet all twelve fail the named-custodian/delegation conjunct; several also fail exact target coverage, exhaustiveness, applicable target-algebra rights or complete terminal behavior. By the exact nondelegation theorem, **0/12** can be sufficient for this source library.\n\nThe result is not caused by an absence of postpublication terminology. It is caused by a typed authority mismatch: NISO communicates metadata; Crossref registers publisher-supplied status/relations; JATS encodes links; COPE advises editors and publishers. None claims to own or be delegated authority over the R7 vocabulary, P1 host, completed target corpus or independent semantic review.\n\n## Scientific boundary and readiness\n\n- Scientific-action gold cells: **0**.\n- Eligible naturalistic R7A dossiers: **0 created**.\n- V8 map audit: **not rerun**; 116,929 rejected, 720 `CANNOT_CHECK`, 0 certified remain unchanged.\n- Owner-algebra groups sufficient: **0/12**.\n- P1 readiness: **unchanged, `NOT_SUBMISSION_READY`**.\n\n## Exact terminal\n\n`{TERMINAL}`\n\n## Next discriminator\n\nThe route is now narrower and operational: authoritatively bind the completed seven-target algebra, not more web taxonomies. The named R7 vocabulary owner/delegate, host authority owner and target-corpus rights holder must complete, license and sign it; an independent reviewer must issue a content-addressed `CONFORMANT` review. Only then may the unchanged map audit run. Case-level scientific-action gold remains a separate owner-separated adjudication task.\n"""
    (LANE / "CONSTRUCT_VALIDITY_REPORT_V4.md").write_text(report)

    boundary = f"""# P1 V4 claim boundary\n\n## Warranted\n\n- Four authoritative institutional families were captured from official routes and bound by exact response hashes.\n- Those sources expose a rights-bounded nonredistributive, source-native postpublication standards scaffold spanning editorial events, notices, status/update metadata, publisher policy and relation markup.\n- Under the unchanged V8 conjunctive rule, the absence of named-custodian authorship/delegation in every row gives an exact upper bound of **0/12 sufficient groups** for this source library.\n- The standards route is valuable as an adjudicator interface and vocabulary scaffold, not as owner authority or gold.\n\n## Not warranted\n\n- No standard token is mapped to an R7 decision.\n- No owner ratification, target-corpus licence, host execution authority, independent semantic review or protected custody was created.\n- No case, model/comparator output, protected score or scientific-action label was accessed.\n- No negative or positive naturalistic effect is estimated.\n- The unchanged 117,649-function audit was not rerun, and all 720 survivors remain `CANNOT_CHECK`.\n- P1 is not ready for top-tier submission or peer review.\n\n## Rights boundary\n\nCrossref documentation displayed CC BY 4.0; the COPE PDF states CC BY-NC-ND 4.0; the NISO PDF states custom conditional noncommercial reproduction permission; exact JATS page reuse licensing was not bound. No raw source document is redistributed. These are evidence-handling facts, not legal advice and not rights over an R7 target algebra.\n\n## Terminal\n\n`{TERMINAL}`\n"""
    (LANE / "CLAIM_BOUNDARY_V4.md").write_text(boundary)

    # Raw copyrighted pages/PDFs and text extractions are deliberately absent from final packet.
    shutil.rmtree(TMP)
    print(json.dumps({"status":"BUILT","terminal":TERMINAL,"sufficient_groups":0,"scientific_action_gold":0}, sort_keys=True))


if __name__ == "__main__":
    main()

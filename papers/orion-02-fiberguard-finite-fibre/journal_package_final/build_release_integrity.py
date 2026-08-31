#!/usr/bin/env python3
"""Build ORION-02's fail-closed research and publication release bindings.

The objects produced here are control-plane records.  They do not upgrade any
scientific result.  Candidate builds remain explicitly pending.  A final build
may copy the reviewer-computed manuscript fingerprint from an external frozen
receipt, but it never recomputes or substitutes that reviewer field.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


MANUSCRIPT_ID = "ORION-02-TMLR-20260831"
AUTHORING_AGENT_ID = "orion02-publication-closure-authoring-lane-20260831"
CHECKED_AT = "2026-08-31T19:45:00+02:00"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(path: Path) -> str:
    return "sha256:" + sha256(path)


def canonical(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def _require_equal(actual: Any, expected: Any, label: str) -> None:
    if actual != expected:
        raise ValueError(f"independent review {label} mismatch")


def _load_independent_review(
    path: Path | None,
    *,
    pdf: Path,
    inventory_path: Path,
    supplement_zip: Path,
    source_zip: Path,
) -> dict[str, Any] | None:
    """Validate a frozen external reviewer receipt without rebinding it."""
    if path is None:
        return None
    review = json.loads(path.read_text(encoding="utf-8"))
    _require_equal(review.get("schema"), "1.0", "schema")
    _require_equal(review.get("paper"), "ORION-02", "paper identity")
    _require_equal(review.get("decision"), "PASS", "decision")
    _require_equal(review.get("verification_scope"), "full_manuscript", "verification scope")
    _require_equal(review.get("package_scope"), "full_candidate_package", "package scope")
    _require_equal(review.get("scope_match"), "MATCH", "scope match")
    reviewer = review.get("reviewer", {})
    _require_equal(
        reviewer.get("separate_from_candidate_authoring_lane"),
        True,
        "reviewer independence",
    )
    reviewer_id = str(reviewer.get("identity", "")).strip()
    if not reviewer_id or reviewer_id == AUTHORING_AGENT_ID:
        raise ValueError("independent review reviewer identity is missing or not independent")

    coverage = review.get("coverage_check", {})
    _require_equal(coverage.get("status"), "PASS", "coverage decision")
    _require_equal(coverage.get("verification_scope"), "full_manuscript", "coverage scope")
    _require_equal(coverage.get("scope_match"), "MATCH", "coverage scope match")
    _require_equal(coverage.get("claim_count_declared"), len(CLAIM_SPECS), "declared claim count")
    _require_equal(coverage.get("claim_count_reviewed"), len(CLAIM_SPECS), "reviewed claim count")
    _require_equal(coverage.get("citation_use_count_reviewed"), 39, "reviewed citation-use count")
    reviewed_fingerprint = str(coverage.get("reviewed_manuscript_fingerprint", ""))
    _require_equal(reviewed_fingerprint, digest(pdf), "reviewer-computed PDF fingerprint")

    immutable = review.get("candidate", {}).get("immutable_objects", {})
    expected_objects = {
        "reader_pdf": pdf,
        "atomic_claim_inventory": inventory_path,
        "anonymous_supplement": supplement_zip,
        "source_archive": source_zip,
    }
    for key, object_path in expected_objects.items():
        record = immutable.get(key, {})
        _require_equal(record.get("sha256"), sha256(object_path), f"{key} SHA-256")
        _require_equal(record.get("byte_count"), object_path.stat().st_size, f"{key} byte count")
    return review


# key, identifier scheme/value, title, authors, year, venue, source type,
# identity/status provider.  Exact claim roles are recorded separately below.
SOURCE_SPECS = [
    ("blackwell1953", "doi", "10.1214/aoms/1177729032", "Equivalent Comparisons of Experiments", ["David Blackwell"], 1953, "The Annals of Mathematical Statistics", "scholarly_work", "Crossref"),
    ("rice1976", "doi", "10.1016/S0065-2458(08)60520-3", "The Algorithm Selection Problem", ["John R. Rice"], 1976, "Advances in Computers", "scholarly_work", "Crossref"),
    ("bischl2016", "doi", "10.1016/j.artint.2016.04.003", "ASlib: A Benchmark Library for Algorithm Selection", ["Bernd Bischl", "Pascal Kerschke", "Lars Kotthoff", "et al."], 2016, "Artificial Intelligence", "scholarly_work", "Crossref"),
    ("olson2017", "doi", "10.1186/s13040-017-0154-4", "PMLB: A Large Benchmark Suite for Machine Learning Evaluation and Comparison", ["Randal S. Olson", "William La Cava", "Patryk Orzechowski", "Ryan J. Urbanowicz", "Jason H. Moore"], 2017, "BioData Mining", "scholarly_work", "Crossref"),
    ("vovk2005", "doi", "10.1007/b106715", "Algorithmic Learning in a Random World", ["Vladimir Vovk", "Alexander Gammerman", "Glenn Shafer"], 2005, "Springer", "book", "Crossref"),
    ("elyaniv2010", "url", "https://www.jmlr.org/papers/v11/el-yaniv10a.html", "On the Foundations of Noise-Free Selective Classification", ["Ran El-Yaniv", "Yair Wiener"], 2010, "Journal of Machine Learning Research", "scholarly_work", "JMLR official article page"),
    ("geifman2017", "arxiv", "1705.08500", "Selective Classification for Deep Neural Networks", ["Yonatan Geifman", "Ran El-Yaniv"], 2017, "Advances in Neural Information Processing Systems", "scholarly_work", "NeurIPS proceedings and arXiv"),
    ("angelopoulos2023", "doi", "10.1561/2200000101", "Conformal Prediction: A Gentle Introduction", ["Anastasios N. Angelopoulos", "Stephen Bates"], 2023, "Foundations and Trends in Machine Learning", "scholarly_work", "Crossref"),
    ("barber2021", "doi", "10.1093/imaiai/iaaa017", "The Limits of Distribution-Free Conditional Predictive Inference", ["Rina Foygel Barber", "Emmanuel J. Candes", "Aaditya Ramdas", "Ryan J. Tibshirani"], 2021, "Information and Inference", "scholarly_work", "Crossref"),
    ("jin2025", "doi", "10.1093/jrsssb/qkaf016", "Confidence on the Focal: Conformal Prediction with Selection-Conditional Coverage", ["Ying Jin", "Zhimei Ren"], 2025, "Journal of the Royal Statistical Society Series B", "scholarly_work", "Crossref"),
    ("sale2025", "arxiv", "2503.16809", "Online Selective Conformal Prediction: Errors and Solutions", ["Yusuf Sale", "Aaditya Ramdas"], 2025, "arXiv preprint", "preprint", "arXiv API"),
    ("zhou2026", "arxiv", "2603.27189v2", "Conformal Prediction Assessment: A Framework for Conditional Coverage Evaluation and Selection", ["Zheng Zhou", "Xiangfei Zhang", "Chongguang Tao", "Yuhong Yang"], 2026, "arXiv preprint", "preprint", "arXiv API"),
    ("min2026", "arxiv", "2605.11602v3", "A Unified Theory of Conditional Coverage in Conformal Prediction with Applications", ["Yinjie Min", "Liuhua Peng", "Changliang Zou"], 2026, "arXiv preprint", "preprint", "arXiv API"),
]


def claim(
    claim_id: str,
    location: str,
    text: str,
    claim_class: str,
    status: str,
    warrant_type: str,
    pointer: str | None = None,
    *,
    sources: tuple[str, ...] = (),
    risk: str = "normal",
    support: str | None = None,
) -> dict[str, Any]:
    return {
        "claim_id": claim_id,
        "location": location,
        "text": text,
        "claim_class": claim_class,
        "target_release_status": status,
        "warrant_type": warrant_type,
        "artifact_pointer": pointer,
        "source_keys": list(sources),
        "risk": risk,
        "support_status": support or ("BOUNDS" if status == "BOUNDED_INFERENCE" else "ENTAILS"),
    }


CLAIM_SPECS: list[dict[str, Any]] = [
    # Abstract and scope.
    claim("C_ABS_001", "Abstract", "The paper studies deterministic certificates on finite representation fibres.", "definition", "COHERENT_DEFINITION", "definition"),
    claim("C_ABS_002", "Abstract", "Every fibre-constant point certificate has worst-case error at least half the fibre's target diameter.", "formal_claim", "VERIFIED", "proof", "MANUSCRIPT.md#Theorem-1"),
    claim("C_ABS_003", "Abstract", "The midpoint of the extreme target values attains the half-diameter bound.", "formal_claim", "VERIFIED", "proof", "MANUSCRIPT.md#Theorem-1"),
    claim("C_ABS_004", "Abstract", "A deterministic certificate with tolerance epsilon exists exactly when the target diameter is at most two epsilon.", "formal_claim", "VERIFIED", "proof", "MANUSCRIPT.md#Theorem-2"),
    claim("C_ABS_005", "Abstract", "A greedy interval cover gives the minimum unconstrained refinement of a finite fibre.", "formal_claim", "VERIFIED", "proof", "MANUSCRIPT.md#Theorem-3"),
    claim("C_ABS_006", "Abstract", "Under a restricted separator family, certification is possible exactly when no separator-indistinguishable pair differs by more than two epsilon.", "formal_claim", "VERIFIED", "proof", "MANUSCRIPT.md#Theorem-4"),
    claim("C_ABS_007", "Abstract", "Without refinement, maximum whole-fibre coverage is the mass of fibres satisfying the diameter threshold.", "formal_claim", "VERIFIED", "proof", "MANUSCRIPT.md#Theorem-5"),
    claim("C_ABS_008", "Abstract", "The preserved applications failed at decision value, useful coverage, or held-out validity.", "interpretation", "BOUNDED_INFERENCE", "analysis", "CLAIM_LEDGER.md#B-Preserved-application-and-repair-boundaries", risk="high"),
    claim("C_ABS_009", "Abstract", "The analytic joint-profile repair corrected a specification defect without establishing transfer value.", "interpretation", "BOUNDED_INFERENCE", "analysis", "submission/anc/results/joint_route_repair_result.json", risk="high"),
    claim("C_ABS_010", "Abstract", "The paper makes no broad empirical-transfer claim.", "interpretation", "BOUNDED_INFERENCE", "analysis", "CLAIM_LEDGER.md#C-Forbidden-promotions-and-open-authority", risk="high"),

    # Formal definitions and assumptions.
    claim("C_FORM_001", "Formal setting", "The instance set X is finite.", "definition", "COHERENT_DEFINITION", "definition"),
    claim("C_FORM_002", "Formal setting", "A representation phi maps X to representation states Z and induces non-empty attained fibres.", "definition", "COHERENT_DEFINITION", "definition"),
    claim("C_FORM_003", "Formal setting", "The certified target is a scalar-valued function V on X.", "definition", "COHERENT_DEFINITION", "definition"),
    claim("C_FORM_004", "Formal setting", "Target diameter is the maximum within-fibre absolute target difference.", "definition", "COHERENT_DEFINITION", "definition"),
    claim("C_FORM_005", "Formal setting", "A fibre-constant point certificate observes only the representation state.", "definition", "COHERENT_DEFINITION", "definition"),
    claim("C_FORM_006", "Formal setting", "A refinement may split but not merge original fibres.", "definition", "COHERENT_DEFINITION", "definition"),
    claim("C_FORM_007", "Formal setting", "An S-measurable refinement may use only the original state and the joint signature of the declared separator family.", "definition", "COHERENT_DEFINITION", "definition"),
    claim("C_FORM_008", "Formal setting", "The formal results assume no sampling, exchangeability, smoothness, computational, or model-class condition.", "interpretation", "BOUNDED_INFERENCE", "analysis", "MANUSCRIPT.md#Formal-setting"),

    # Complete formal claim surface and finite corroboration.
    claim("C_THEORY_001", "Theorem 1", "The sharp deterministic point-certificate floor is D_phi(z)/2.", "formal_claim", "VERIFIED", "proof", "MANUSCRIPT.md#Theorem-1"),
    claim("C_THEORY_002", "Corollary 1", "A centred interval of radius below D_phi(z)/2 cannot cover every target in the fibre.", "formal_claim", "VERIFIED", "proof", "MANUSCRIPT.md#Corollary-1"),
    claim("C_THEORY_003", "Interval witness", "A balanced distribution on diameter endpoints gives at least one-half conditional miscoverage for a narrower fibre-constant interval.", "formal_claim", "VERIFIED", "proof", "MANUSCRIPT.md#Interval-certificates"),
    claim("C_THEORY_004", "Theorem 2", "Fibre certifiability at tolerance epsilon is equivalent to D_phi(z) <= 2 epsilon.", "formal_claim", "VERIFIED", "proof", "MANUSCRIPT.md#Theorem-2"),
    claim("C_THEORY_005", "Theorem 3", "The left-to-right greedy cover of sorted target values minimizes the number of diameter-at-most-two-epsilon parts.", "formal_claim", "VERIFIED", "proof", "MANUSCRIPT.md#Theorem-3"),
    claim("C_THEORY_006", "Theorem 4", "Separator realizability is equivalent to the absence of a target-separated S-indistinguishable pair within an original fibre.", "formal_claim", "VERIFIED", "proof", "MANUSCRIPT.md#Theorem-4"),
    claim("C_THEORY_007", "Theorem 5", "Whole-fibre acceptance attains exactly the total mass of original fibres meeting the diameter threshold.", "formal_claim", "VERIFIED", "proof", "MANUSCRIPT.md#Theorem-5"),
    claim("C_CHECK_001", "Finite model checks", "The floor checker found zero violations on 784 registered configurations and fired its planted control.", "quantitative_result", "VERIFIED", "method_record", "submission/anc/expected_fibre_diameter_floor.json", risk="high"),
    claim("C_CHECK_002", "Finite model checks", "The refinement checker found zero violations on 4,704 main configurations, matched greedy counts to exhaustive minima, exercised separator enumeration, and fired planted controls.", "quantitative_result", "VERIFIED", "method_record", "submission/anc/expected_refinement_to_certifiability.json", risk="high"),
    claim("C_CHECK_003", "Finite model checks", "Finite implementation checks corroborate transcription but do not replace the general proofs or constitute external replication.", "interpretation", "BOUNDED_INFERENCE", "analysis", "MANUSCRIPT.md#Finite-model-checks"),

    # Application and repair boundaries, including every ledger-preserved terminal.
    claim("C_APP_001", "Preserved adverse boundaries", "The outcome-exposed paired-route recovery found zero feasible candidates among 99 and changed no route decision; its former positive interpretation remains retracted.", "quantitative_result", "VERIFIED", "author_data", "submission/anc/results/paired_route_result.json", risk="high"),
    claim("C_APP_002", "Preserved adverse boundaries", "The exact joint-route repair exposes a 35-to-70 diagonal-shortcut error and a 0-versus-50 compatibility counterexample without establishing empirical transfer.", "quantitative_result", "VERIFIED", "analysis", "submission/anc/results/joint_route_repair_result.json", risk="high"),
    claim("C_APP_003", "Preserved adverse boundaries", "The initial certified-neighbourhood study was invalid on both splits; official-split coverages were 0.210 and 0.331, violation rates were 0.169 and 0.182, and family-disjoint coverage was zero.", "quantitative_result", "VERIFIED", "author_data", "submission/anc/results/initial_neighbourhood_result.json", risk="high"),
    claim("C_APP_004", "Preserved adverse boundaries", "The corrected split-conformal neighbourhood envelope met its marginal criterion only with zero held-out coverage and no decision-value improvement.", "empirical_result", "VERIFIED", "author_data", "submission/anc/results/corrected_neighbourhood_result.json", risk="high"),
    claim("C_APP_005", "Preserved adverse boundaries", "The held-out density-backoff study covered 32 of 44 datasets versus 39 of 44 for its lexical control; exact McNemar p=0.09228515625 and a bootstrap interval including zero do not establish the paired difference.", "quantitative_result", "VERIFIED", "author_data", "submission/anc/results/density_paired_comparison.json", risk="high"),
    claim("C_APP_006", "Preserved adverse boundaries", "The held-out arm-conditional study covered 44 of 44 datasets but the geometry primary had 20 strict violations and retained the invalid-certificate terminal.", "quantitative_result", "VERIFIED", "author_data", "submission/anc/results/arm_conditional_result.json", risk="high"),
    claim("C_APP_007", "Preserved adverse boundaries", "The frozen R24 paired flags reconstruct 20 of 44 versus 14 of 44 strict violations, contingency 14/6/0/24, and exact two-sided McNemar p=0.03125.", "quantitative_result", "VERIFIED", "analysis", "submission/anc/expected_arm_strict_violation_comparator.json", risk="high"),
    claim("C_APP_008", "Preserved adverse boundaries", "Both R24 policies fail the frozen maximum violation rate of 0.10; the correction supports neither geometry superiority nor broad lexical superiority.", "interpretation", "BOUNDED_INFERENCE", "analysis", "submission/anc/expected_arm_strict_violation_comparator.json", risk="high"),
    claim("C_APP_009", "Selector diagnostic", "On the 44 R24 held-out decisions, the available score had Pearson r=-0.144 and permutation p=0.353 under 20,000 permutations.", "quantitative_result", "VERIFIED", "author_data", "submission/anc/results/selector_diagnostic.json", risk="high"),
    claim("C_APP_010", "Selector diagnostic", "The selector diagnostic did not establish a useful association and does not prove zero population association.", "interpretation", "BOUNDED_INFERENCE", "analysis", "submission/anc/results/selector_diagnostic.json", risk="high"),
    claim("C_APP_011", "Claim ledger", "None of the application records directly measures target diameter on accepted empirical fibres.", "interpretation", "BOUNDED_INFERENCE", "analysis", "CLAIM_LEDGER.md#V3-E9", risk="high"),
    claim("C_APP_012", "Claim ledger", "The BNSL study is a consumed null because the zero-cost basic_extended representation already attained virtual-best actions on all 1,179 instances; its overlapping-predicate positive-looking terminal remains quarantined.", "quantitative_result", "VERIFIED", "author_data", "CLAIM_LEDGER.md#V3-E10", risk="high"),
    claim("C_APP_013", "Claim ledger", "The prospectively frozen TSP-LION2015 run remains a subject-prerequisite CANNOT_CHECK caused by 21 missing numeric feature-cost cells and produced no learned model or comparison.", "availability_or_compliance", "VERIFIED", "method_record", "CLAIM_LEDGER.md#V3-E11", risk="high"),
    claim("C_APP_014", "Claim ledger", "The untouched-subject CSP-MZN recovery was adverse: the certified router increased mean total excess and timeouts relative to its registered same-information comparator.", "empirical_result", "VERIFIED", "author_data", "CLAIM_LEDGER.md#V3-E12", risk="high"),
    claim("C_APP_015", "Claim ledger", "The cached-ASlib exposure occurred before a Round-3 freeze, disqualified the cached tree as untouched, consumed no round, and produced no science terminal.", "availability_or_compliance", "VERIFIED", "method_record", "CLAIM_LEDGER.md#V3-E13", risk="high"),

    # Literature and novelty subtraction.  Each external proposition is source-bound.
    claim("C_LIT_001", "Introduction and related work", "Blackwell comparison orders experiments by usefulness across decision problems.", "literature_fact", "VERIFIED", "literature", sources=("blackwell1953",)),
    claim("C_LIT_002", "Introduction and related work", "Rice formulated the instance-to-algorithm selection problem.", "literature_fact", "VERIFIED", "literature", sources=("rice1976",)),
    claim("C_LIT_003", "Introduction and related work", "ASlib is the public algorithm-selection benchmark resource used by the preserved algorithm-selection studies.", "literature_fact", "VERIFIED", "literature", sources=("bischl2016",)),
    claim("C_LIT_004", "Introduction and related work", "PMLB is the public machine-learning benchmark resource used by the preserved classification studies.", "literature_fact", "VERIFIED", "literature", sources=("olson2017",)),
    claim("C_LIT_005", "Introduction and related work", "Conformal prediction provides finite-sample marginal guarantees under exchangeability.", "literature_fact", "VERIFIED", "literature", sources=("vovk2005", "angelopoulos2023")),
    claim("C_LIT_006", "Introduction and related work", "Selective classification studies coverage-risk trade-offs when a predictor may abstain.", "literature_fact", "VERIFIED", "literature", sources=("elyaniv2010", "geifman2017")),
    claim("C_LIT_007", "Introduction and related work", "Exact conditional validity cannot generally be obtained distribution-free without restrictions.", "literature_fact", "VERIFIED", "literature", sources=("barber2021",)),
    claim("C_LIT_008", "Introduction and related work", "Recent work develops selection-conditional conformal procedures.", "literature_fact", "VERIFIED", "literature", sources=("jin2025", "sale2025")),
    claim("C_LIT_009", "Introduction and related work", "Recent work develops local or structured conditional-coverage assessment.", "literature_fact", "VERIFIED", "literature", sources=("zhou2026", "min2026")),
    claim("C_LIT_010", "Relation to prior work", "The manuscript does not claim a new general information order, generic conformal validity, generic selective prediction, the interval midpoint, or the greedy sorted-point cover.", "novelty_or_priority", "BOUNDED_INFERENCE", "literature", sources=tuple(x[0] for x in SOURCE_SPECS), risk="high"),
    claim("C_LIT_011", "Relation to prior work", "The bounded residual contribution is the unified finite-fibre certificate/refinement calculus together with a fail-closed adverse application boundary.", "novelty_or_priority", "BOUNDED_INFERENCE", "analysis", "CLAIM_LEDGER.md#Prior-work-and-novelty-boundary", sources=tuple(x[0] for x in SOURCE_SPECS), risk="high"),

    # Discussion, limitations, and release-facing claims.
    claim("C_DISC_001", "Discussion", "Representational sufficiency is relative to the certified question, not merely the action-selection task.", "interpretation", "BOUNDED_INFERENCE", "analysis", "MANUSCRIPT.md#Discussion"),
    claim("C_DISC_002", "Discussion", "Calibration repair, selector repair, and representation refinement address distinct failure classes.", "interpretation", "BOUNDED_INFERENCE", "analysis", "MANUSCRIPT.md#Discussion"),
    claim("C_DISC_003", "Discussion", "The correct interpretation of the adverse studies is as successor-question delimiters rather than near successes.", "interpretation", "BOUNDED_INFERENCE", "analysis", "MANUSCRIPT.md#Discussion", risk="high"),
    claim("C_LIM_001", "Limitations", "Infinite spaces and vector-valued targets require assumptions not supplied by the finite scalar theorems.", "interpretation", "BOUNDED_INFERENCE", "analysis", "MANUSCRIPT.md#Limitations"),
    claim("C_LIM_002", "Limitations", "Randomized certificates require a separate declared loss and coverage convention.", "interpretation", "BOUNDED_INFERENCE", "analysis", "MANUSCRIPT.md#Limitations"),
    claim("C_LIM_003", "Limitations", "Estimating target values and diameters without leakage is a separate statistical problem.", "interpretation", "BOUNDED_INFERENCE", "analysis", "MANUSCRIPT.md#Limitations"),
    claim("C_LIM_004", "Limitations", "The paper neither learns nor prices separator families.", "interpretation", "BOUNDED_INFERENCE", "analysis", "MANUSCRIPT.md#Limitations"),
    claim("C_LIM_005", "Limitations", "The preserved studies do not establish broad transfer, production advantage, computational hardness, or comparative superiority.", "interpretation", "BOUNDED_INFERENCE", "analysis", "CLAIM_LEDGER.md#C-Forbidden-promotions-and-open-authority", risk="high"),
    claim("C_REL_001", "Data and code availability", "The anonymous supplement contains theorem checkers, expected outputs, anonymized projections of the manuscript-relevant result objects, paired-comparison code, and the selector diagnostic.", "availability_or_compliance", "VERIFIED", "method_record", "submission/When_a_Representation_Can_Certify_supplementary_anonymous.zip", risk="high"),
    claim("C_REL_002", "Data and code availability", "The supplement rechecks enclosed frozen outcomes but does not rerun the upstream ASlib or PMLB model-fitting pipelines.", "availability_or_compliance", "VERIFIED", "method_record", "submission/anc/README.md", risk="high"),
    claim("C_REL_003", "Data and code availability", "The source archive contains the TMLR LaTeX, bibliography, and unmodified style inputs used for the review build.", "availability_or_compliance", "VERIFIED", "method_record", "submission/When_a_Representation_Can_Certify_tmlr_source.zip", risk="high"),
    claim("C_REL_004", "Generative AI disclosure", "A generative language model assisted with organization, language revision, adversarial review, and package preparation.", "availability_or_compliance", "VERIFIED", "method_record", "MANUSCRIPT.md#Generative-AI-disclosure", risk="high"),
    claim("C_REL_005", "Generative AI disclosure", "The author remains responsible for the scientific claims, citations, code, and final submission.", "availability_or_compliance", "VERIFIED", "method_record", "MANUSCRIPT.md#Generative-AI-disclosure", risk="high"),
]


def _artifact(path: Path, artifact_id: str, role: str, package: Path) -> dict[str, Any]:
    return {
        "artifact_id": artifact_id,
        "role": role,
        "path": path.relative_to(package).as_posix(),
        "sha256": digest(path),
        "byte_count": path.stat().st_size,
    }


def _build_sources(literature_record: Path) -> list[dict[str, Any]]:
    sources = []
    for key, scheme, value, title, authors, year, venue, source_type, provider in SOURCE_SPECS:
        method = "registry_lookup" if scheme in {"doi", "arxiv"} else "publisher_or_primary_record"
        sources.append({
            "source_id": f"S_{key}",
            "source_type": source_type,
            "identifiers": [{"scheme": scheme, "value": value}],
            "bibliographic": {"title": title, "authors": authors, "year": year, "venue": venue},
            "declared_publication_status": "ACTIVE",
            "identity_checks": [{
                "provider": provider,
                "status": "MATCH",
                "checked_at": CHECKED_AT,
                "verification_method": method,
                "verifier_id": AUTHORING_AGENT_ID,
                "notes": "Identity was checked against the provider recorded in LITERATURE_VERIFICATION_V4.md and must be reconfirmed by the checksum-bound independent reviewer.",
            }],
            "status_checks": [{
                "provider": provider,
                "status": "ACTIVE",
                "checked_at": CHECKED_AT,
                "verification_method": method,
                "verifier_id": AUTHORING_AGENT_ID,
                "notes": "No retraction or withdrawal signal was found at the recorded check; preprint version identity remains explicit.",
            }],
            "status_adjudication": {"status": "PASS", "notes": "Use is bounded to the proposition and publication state recorded in the ledger."},
            "record_fingerprint": digest(literature_record),
        })
    return sources


def build(package: Path, paper: Path, review_receipt: Path | None = None) -> None:
    pdf = package / "submission/When_a_Representation_Can_Certify.pdf"
    arxiv_pdf = package / "submission/When_a_Representation_Can_Certify_arxiv.pdf"
    source_zip = package / "submission/When_a_Representation_Can_Certify_tmlr_source.zip"
    arxiv_source_zip = package / "submission/When_a_Representation_Can_Certify_arxiv_source.zip"
    supplement_zip = package / "submission/When_a_Representation_Can_Certify_supplementary_anonymous.zip"
    manuscript = package / "MANUSCRIPT.md"
    scientific_ledger = package / "CLAIM_LEDGER.md"
    literature_record = package / "LITERATURE_VERIFICATION_V4.md"
    stale_review_provenance = package / "INDEPENDENT_REVIEW_PROVENANCE.json"
    if review_receipt is None:
        stale_review_provenance.unlink(missing_ok=True)

    inventory = {
        "schema": "ORION.PublicationClosure.AtomicClaimInventory.v1",
        "paper": "ORION-02",
        "manuscript_id": MANUSCRIPT_ID,
        "reader_pdf_sha256": digest(pdf),
        "verification_scope": "full_manuscript",
        "claim_count": len(CLAIM_SPECS),
        "claims": CLAIM_SPECS,
        "review_state": "PENDING_CHECKSUM_BOUND_INDEPENDENT_CONFIRMATION",
    }
    inventory_path = package / "ATOMIC_CLAIM_INVENTORY.json"
    inventory_path.write_text(canonical(inventory), encoding="utf-8")

    independent_review = _load_independent_review(
        review_receipt,
        pdf=pdf,
        inventory_path=inventory_path,
        supplement_zip=supplement_zip,
        source_zip=source_zip,
    )
    reviewer_id = (
        str(independent_review["reviewer"]["identity"])
        if independent_review is not None
        else "PENDING_INDEPENDENT_REVIEW"
    )
    independent_status = "PASS" if independent_review is not None else "NOT_DONE"

    sources = _build_sources(literature_record)
    claims = []
    receipts = []
    for spec in CLAIM_SPECS:
        cid = spec["claim_id"]
        claims.append({
            "claim_id": cid,
            "location": spec["location"],
            "text": spec["text"],
            "claim_class": spec["claim_class"],
            "risk": spec["risk"],
            "release_status": spec["target_release_status"],
            "independent_check": {
                "status": independent_status,
                "verifier_id": reviewer_id,
                "notes": (
                    "Bound to the validated frozen independent review receipt."
                    if independent_review is not None
                    else "Candidate state; no independent review has yet been copied into the release ledger."
                ),
            },
            "counterevidence_search": {
                "status": "DONE" if spec["risk"] == "high" or spec["source_keys"] else "NOT_APPLICABLE",
                "notes": "Adverse, null, retracted, CANNOT_CHECK, superseded, and scope-limiting records were retained rather than promoted or deleted.",
            },
        })

        for key in spec["source_keys"]:
            receipts.append({
                "receipt_id": f"E_{cid}_{key}",
                "claim_id": cid,
                "warrant_type": "literature",
                "source_id": f"S_{key}",
                "locator": f"LITERATURE_VERIFICATION_V4.md row for {key}; exact manuscript use at {spec['location']}",
                "evidence_fingerprint": digest(literature_record),
                "verification_method": "independent_model_with_retrieved_source",
                "support_status": "BOUNDS" if spec["target_release_status"] == "BOUNDED_INFERENCE" else "ENTAILS",
                "scope_match": "MATCH",
                "verifier_id": reviewer_id,
                "notes": "The source supports only the recorded context proposition, not an ORION empirical or formal result.",
            })

        if spec["warrant_type"] not in {"literature", "source"} or spec["artifact_pointer"]:
            receipt: dict[str, Any] = {
                "receipt_id": f"E_{cid}_internal",
                "claim_id": cid,
                "warrant_type": spec["warrant_type"],
                "verification_method": {
                    "proof": "deterministic_derivation",
                    "author_data": "deterministic_recompute",
                    "analysis": "human_review",
                    "method_record": "authoritative_project_record",
                    "definition": "human_review",
                }[spec["warrant_type"]],
                "support_status": spec["support_status"],
                "scope_match": "MATCH",
                "verifier_id": reviewer_id,
                "notes": "Exact warrant and authority ceiling are subject to the checksum-bound independent review.",
            }
            if spec["artifact_pointer"]:
                raw = spec["artifact_pointer"].split("#", 1)[0]
                target = (package / raw).resolve()
                target.relative_to(package.resolve())
                if not target.exists():
                    raise ValueError(f"claim pointer does not resolve: {spec['artifact_pointer']}")
                receipt["artifact_pointer"] = spec["artifact_pointer"]
            receipts.append(receipt)

    citations = []
    for spec in CLAIM_SPECS:
        for key in spec["source_keys"]:
            citations.append({
                "citation_id": f"CITE_{spec['claim_id']}_{key}",
                "source_id": f"S_{key}",
                "location": spec["location"],
                "claim_ids": [spec["claim_id"]],
            })

    ledger = {
        "schema_version": "1.0",
        "manuscript_id": MANUSCRIPT_ID,
        "manuscript_fingerprint": digest(pdf),
        "authoring_agent_id": AUTHORING_AGENT_ID,
        "verification_scope": "full_manuscript",
        "coverage_check": {
            "status": independent_status,
            "verifier_id": reviewer_id,
            "verification_method": "independent_model_with_retrieved_source",
            "checked_at": (
                str(independent_review["coverage_check"].get("checked_at", CHECKED_AT))
                if independent_review is not None
                else CHECKED_AT
            ),
            "notes": (
                f"The frozen independent receipt confirms all {len(CLAIM_SPECS)} declared atomic claims and every citation use on this exact reader artifact."
                if independent_review is not None
                else f"Candidate state pending independent coverage of all {len(CLAIM_SPECS)} declared atomic claims and every citation use."
            ),
        },
        "sources": sources,
        "claims": claims,
        "evidence_receipts": receipts,
        "citation_usages": citations,
        "release": {"requested_state": "submission_ready"},
        "review_state": "PASS" if independent_review is not None else "PENDING_CHECKSUM_BOUND_INDEPENDENT_CONFIRMATION",
        "does_not_certify": [
            "scientific_truth",
            "external_replication",
            "external_peer_review",
            "journal_acceptance",
            "portal_upload",
            "author_approval",
        ],
    }
    if independent_review is not None:
        # This value is copied verbatim from the frozen reviewer output.  The
        # equality check above prevents author-side rebinding to later bytes.
        ledger["coverage_check"]["reviewed_manuscript_fingerprint"] = independent_review[
            "coverage_check"
        ]["reviewed_manuscript_fingerprint"]
    ledger_path = package / "RESEARCH_INTEGRITY_LEDGER.json"
    ledger_path.write_text(canonical(ledger), encoding="utf-8")

    review_provenance_path: Path | None = None
    if independent_review is not None and review_receipt is not None:
        review_provenance_path = package / "INDEPENDENT_REVIEW_PROVENANCE.json"
        review_provenance_path.write_text(
            canonical(
                {
                    "schema": "ORION.PublicationClosure.IndependentReviewProvenance.v1",
                    "paper": "ORION-02",
                    "disposition": "EXTERNAL_FROZEN_RECEIPT__EXCLUDED_FROM_UPLOAD_SET",
                    "reviewer_identity": reviewer_id,
                    "sha256": sha256(review_receipt),
                    "byte_count": review_receipt.stat().st_size,
                    "reviewed_manuscript_fingerprint": independent_review["coverage_check"][
                        "reviewed_manuscript_fingerprint"
                    ],
                    "does_not_certify": [
                        "external_peer_review",
                        "journal_acceptance",
                        "portal_upload",
                    ],
                }
            ),
            encoding="utf-8",
        )

    artifacts = [
        _artifact(pdf, "reader-pdf", "reader_manuscript", package),
        _artifact(arxiv_pdf, "arxiv-reader-pdf", "reader_manuscript", package),
        _artifact(ledger_path, "research-integrity-ledger", "claim_ledger", package),
        _artifact(manuscript, "canonical-markdown-source", "manuscript_source", package),
        _artifact(scientific_ledger, "scientific-claim-ledger", "release_receipt", package),
        _artifact(inventory_path, "atomic-claim-inventory", "release_receipt", package),
        _artifact(source_zip, "tmlr-source-archive", "submission_component", package),
        _artifact(arxiv_source_zip, "arxiv-source-archive", "submission_component", package),
        _artifact(supplement_zip, "anonymous-supplement", "reproducibility_component", package),
    ]
    if review_provenance_path is not None:
        artifacts.append(
            _artifact(
                review_provenance_path,
                "independent-review-provenance",
                "release_receipt",
                package,
            )
        )
    source_tex = package / "submission/When_a_Representation_Can_Certify.tex"
    artifacts.append(_artifact(source_tex, "reader-latex-source", "manuscript_source", package))
    arxiv_tex = package / "submission/When_a_Representation_Can_Certify_arxiv.tex"
    artifacts.append(_artifact(arxiv_tex, "arxiv-latex-source", "manuscript_source", package))

    candidates = [
        {
            "manuscript_id": MANUSCRIPT_ID,
            "artifact_id": "reader-pdf",
            "sha256": digest(pdf),
            "disposition": "authoritative",
            "reason": "Exact anonymous reader-facing PDF governing the TMLR review package.",
        },
        {
            "manuscript_id": "ORION-02-ARXIV-20260831",
            "artifact_id": "arxiv-reader-pdf",
            "sha256": digest(arxiv_pdf),
            "disposition": "excluded_incompatible",
            "reason": "Identified public arXiv rendering of the identical scientific body; it is intentionally excluded from the anonymous TMLR release package and does not compete with that route's reader authority.",
        },
        {
            "manuscript_id": "ORION-02-V3-EDITABLE-SOURCE",
            "sha256": digest(paper / "MANUSCRIPT_V3.md"),
            "disposition": "historical_provenance",
            "reason": "Canonical editable scientific source bound to the PDF; it is not a competing reader artifact.",
        },
        {
            "manuscript_id": "ORION-02-V3-PACKAGE-SOURCE",
            "sha256": digest(manuscript),
            "disposition": "historical_provenance",
            "reason": "Byte-identical package copy of the canonical editable source; not a separate authority.",
        },
        {
            "manuscript_id": "ORION-02-V3-TMLR-LATEX",
            "sha256": digest(source_tex),
            "disposition": "historical_provenance",
            "reason": "Editable target-specific source from which the authoritative reader PDF is built.",
        },
        {
            "manuscript_id": "ORION-02-V2",
            "sha256": digest(paper / "MANUSCRIPT_V2.md"),
            "disposition": "superseded",
            "superseded_by": MANUSCRIPT_ID,
            "reason": "Earlier manuscript retained only as development provenance.",
        },
        {
            "manuscript_id": "ORION-02-V3-PIPELINE-DRAFT",
            "sha256": digest(paper / "MANUSCRIPT_V3_PIPELINE.md"),
            "disposition": "superseded",
            "superseded_by": MANUSCRIPT_ID,
            "reason": "Repository-facing pipeline draft excluded from the journal upload set.",
        },
        {
            "manuscript_id": "ORION-02-HISTORICAL-SUBMISSION-PDF",
            "sha256": digest(paper / "submission/Low-Order_Decision_Certificates_and_Value_Limits_in_a_Pauli-String_Partition_Model.pdf"),
            "disposition": "superseded",
            "superseded_by": MANUSCRIPT_ID,
            "reason": "Historical predecessor rendering with a different title and superseded scientific surface.",
        },
    ]

    publication_manifest = {
        "schema_version": "1.0",
        "release_id": "ORION-02-TMLR-PUBLICATION-CLOSURE-20260831",
        "canonical_paper_id": "ORION-02",
        "requested_state": "submission_ready",
        "authority": {
            "manuscript_id": MANUSCRIPT_ID,
            "manuscript_artifact_id": "reader-pdf",
            "claim_ledger_artifact_id": "research-integrity-ledger",
        },
        "manuscript_candidates": candidates,
        "artifacts": artifacts,
        "package": {
            "format": "file_set",
            "members": [
                {"member_path": "submission/When_a_Representation_Can_Certify.pdf", "artifact_id": "reader-pdf"},
                {"member_path": "submission/When_a_Representation_Can_Certify_supplementary_anonymous.zip", "artifact_id": "anonymous-supplement"},
            ],
        },
    }
    (package / "PUBLICATION_RELEASE_MANIFEST.json").write_text(
        canonical(publication_manifest), encoding="utf-8"
    )

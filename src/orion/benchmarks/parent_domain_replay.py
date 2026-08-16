from __future__ import annotations

from orion.benchmarks.degeneracy import DegeneracyStatus, LabeledRecord, probe_records

from dataclasses import dataclass
from enum import Enum

from orion.benchmarks.result import BenchmarkReport, report_from_checks
from orion.knowledge.parent_domains import (
    FunctionalOperationSignature,
    ParentDisciplineProfile,
    named_basis_mentions,
    top_parent_discipline,
)


RAKL_SELF_RAKL_SOURCE = (
    "github:SzeChunYiu/RAKL@bd4ce50f48bbfd7d36e9a41ded9566f77d8105ca:"
    "skills/rakl-core/workflows/self-rakl.md"
)

# Verbatim conceptual families frozen from the historical Self-RAKL workflow.
# These are not ORION's current search ontology; they are replay evidence.
HISTORICAL_MINIMUM_ROUTE_FAMILIES = (
    "scientific method philosophy of science metascience",
    "metacognition self regulated learning expert learning",
    "expertise acquisition deliberate practice adaptive expertise",
    "cognitive problem solving insight representation restructuring",
    "learning science productive failure contrastive learning self explanation",
    "memory retrieval spacing interleaving chunking script formation",
    "creativity design fixation incubation recombination",
    "entrepreneurship effectuation action under uncertainty",
    "organizational learning exploration exploitation brokerage across communities",
    "active learning experiment design optimal control",
    "formal methods truth maintenance belief revision provenance",
    "knowledge representation local to global consistency",
    "causal inference identification partial identification",
    "information retrieval databases memory context compression",
    "software reliability reproducibility supply chain provenance",
    "self improving agents program evolution skill learning",
    "scientific visualization human factors communication",
    "domain specific non LLM research workflows",
)


class HistoricalCausalVerdict(str, Enum):
    PARTIALLY_IDENTIFIED = "PARTIALLY_IDENTIFIED"
    IDENTIFIED = "IDENTIFIED"
    CANNOT_CHECK = "CANNOT_CHECK"


@dataclass(frozen=True)
class ParentDomainReplayResult:
    local_report: BenchmarkReport
    historical_causal_verdict: HistoricalCausalVerdict
    historical_blockers: tuple[str, ...]
    named_basis_omissions: tuple[str, ...]
    fresh_transfer_accuracy: float

    @property
    def rules_out_required_method_basis_change(self) -> bool:
        """Current/fresh known worlds succeed without inventing a new research operator."""

        return self.local_report.passed and self.fresh_transfer_accuracy == 1.0


def _profiles() -> tuple[ParentDisciplineProfile, ...]:
    evidence = ("benchmark:parent-domain-profile-source",)
    return (
        ParentDisciplineProfile(
            "profile:scientific-language",
            "computational linguistics",
            mechanism_terms=(
                "coreference resolution",
                "semantic role labeling",
                "modality scope",
                "negation scope",
                "discourse relation",
                "attribution",
            ),
            object_terms=("mention referent proposition scientific text" ,),
            failure_terms=("reference ambiguity scope ambiguity discourse loss",),
            invariant_terms=("preserve polarity modality attribution",),
            evidence_ids=evidence,
        ),
        ParentDisciplineProfile(
            "profile:measurement-validity",
            "psychometrics",
            mechanism_terms=(
                "construct validity",
                "reliability",
                "measurement invariance",
                "item response",
                "latent trait",
            ),
            object_terms=("construct item instrument evaluator score",),
            failure_terms=("construct underrepresentation measurement bias evaluator variance",),
            invariant_terms=("separate latent construct from observed score",),
            evidence_ids=evidence,
        ),
        ParentDisciplineProfile(
            "profile:search-control",
            "information foraging",
            mechanism_terms=(
                "patch switching",
                "scent",
                "query reformulation",
                "marginal gain",
                "search stopping",
            ),
            object_terms=("search patch route evidence cost",),
            failure_terms=("premature stopping fixation low yield route",),
            invariant_terms=("route stop is not task stop",),
            evidence_ids=evidence,
        ),
        ParentDisciplineProfile(
            "profile:identity-integration",
            "data integration",
            mechanism_terms=(
                "entity resolution",
                "schema matching",
                "record linkage",
                "mapping composition",
            ),
            object_terms=("record entity schema provenance lineage",),
            failure_terms=("duplicate identity schema mismatch conflicting records",),
            invariant_terms=("preserve source lineage mapping witness",),
            evidence_ids=evidence,
        ),
        ParentDisciplineProfile(
            "profile:measurement-traceability",
            "metrology",
            mechanism_terms=(
                "measurand",
                "calibration",
                "measurement uncertainty",
                "traceability",
                "unit consistency",
            ),
            object_terms=("measurement instrument unit reference standard",),
            failure_terms=("uncalibrated instrument unit mismatch uncertainty omission",),
            invariant_terms=("measurement carries uncertainty and traceability",),
            evidence_ids=evidence,
        ),
    )


def _cases() -> tuple[tuple[str, FunctionalOperationSignature, str], ...]:
    return (
        (
            "historical-01",
            FunctionalOperationSignature(
                "signature:scientific-language",
                operation_terms=(
                    "resolve coreference",
                    "assign semantic roles",
                    "track modality scope",
                    "track negation scope",
                    "connect discourse relations",
                    "preserve attribution",
                ),
                object_terms=("mention referent proposition scientific text",),
                failure_terms=("reference ambiguity scope ambiguity discourse loss",),
                invariant_terms=("preserve polarity modality attribution",),
            ),
            "computational linguistics",
        ),
        (
            "historical-02",
            FunctionalOperationSignature(
                "signature:benchmark-validity",
                operation_terms=(
                    "validate construct",
                    "estimate reliability",
                    "test measurement invariance",
                    "model item response",
                    "separate latent trait",
                ),
                object_terms=("construct item instrument evaluator score",),
                failure_terms=("construct underrepresentation measurement bias evaluator variance",),
                invariant_terms=("separate latent construct from observed score",),
            ),
            "psychometrics",
        ),
        (
            "fresh-01",
            FunctionalOperationSignature(
                "signature:route-control",
                operation_terms=("patch switching", "scent", "query reformulation", "marginal gain", "search stopping"),
                object_terms=("search patch route evidence cost",),
                failure_terms=("premature stopping fixation low yield route",),
                invariant_terms=("route stop is not task stop",),
            ),
            "information foraging",
        ),
        (
            "fresh-02",
            FunctionalOperationSignature(
                "signature:cross-source-identity",
                operation_terms=("entity resolution", "schema matching", "record linkage", "mapping composition"),
                object_terms=("record entity schema provenance lineage",),
                failure_terms=("duplicate identity schema mismatch conflicting records",),
                invariant_terms=("preserve source lineage mapping witness",),
            ),
            "data integration",
        ),
        (
            "fresh-03",
            FunctionalOperationSignature(
                "signature:measurement",
                operation_terms=("measurand", "calibration", "measurement uncertainty", "traceability", "unit consistency"),
                object_terms=("measurement instrument unit reference standard",),
                failure_terms=("uncalibrated instrument unit mismatch uncertainty omission",),
                invariant_terms=("measurement carries uncertainty and traceability",),
            ),
            "metrology",
        ),
    )


def run_parent_domain_replay(*, original_query_trace_available: bool = False) -> ParentDomainReplayResult:
    profiles = _profiles()
    cases = _cases()
    outcomes: list[tuple[str, str, bool, bool]] = []
    for case_id, signature, expected in cases:
        candidate = top_parent_discipline(signature, profiles)
        outcomes.append(
            (
                case_id,
                "" if candidate is None else candidate.discipline_id,
                bool(candidate and candidate.lexically_independent),
                candidate is not None and candidate.discipline_id == expected,
            )
        )

    historical_targets = ("computational linguistics", "psychometrics")
    omissions = tuple(
        target
        for target in historical_targets
        if not named_basis_mentions(HISTORICAL_MINIMUM_ROUTE_FAMILIES, target)
    )
    fresh = [item for item in outcomes if item[0].startswith("fresh-")]
    fresh_accuracy = sum(int(item[3]) for item in fresh) / len(fresh)

    # Construct-validity probe over the panel itself: if a case id carries the
    # discipline it is labelled with, or a responder reading only case ids can
    # beat the majority baseline, the replay measures a shortcut and its own
    # accuracy numbers above are not evidence. Ported from RAKL, where this
    # class of leak scored ALR 0.143 on a panel while doing no reasoning.
    probe = probe_records(
        [
            LabeledRecord(record_id=case_id, features={"case_id": case_id}, label=found)
            for case_id, found, _, _ in outcomes
        ],
        surface="parent-domain-replay",
        blind_responders={"case_id_only": lambda r: r.features["case_id"]},
    )

    checks = (
        (
            "panel is not degenerate (no label in ids, no blind-responder ceiling)",
            probe.status is DegeneracyStatus.CLEAN,
        ),
        ("historical named basis omits both target disciplines", set(omissions) == set(historical_targets)),
        ("functional matcher recovers historical NLP target", outcomes[0][3]),
        ("functional matcher recovers historical psychometrics target", outcomes[1][3]),
        ("historical recoveries do not leak discipline labels into signatures", outcomes[0][2] and outcomes[1][2]),
        ("fresh hidden-domain transfer is perfect", fresh_accuracy == 1.0),
        ("fresh transfer remains label-independent", all(item[2] for item in fresh)),
    )
    report = report_from_checks(
        paper_id="P1",
        case_id="parent-discipline-omission-replay",
        checks=checks,
        metrics=(
            ("historical_targets_recovered", float(sum(int(item[3]) for item in outcomes[:2]))),
            ("fresh_transfer_accuracy", fresh_accuracy),
            ("historical_named_basis_omissions", float(len(omissions))),
        ),
        observations=(
            f"Historical route source: {RAKL_SELF_RAKL_SOURCE}",
            "The historical named-basis omission is observable; original execution causality requires the original query/retrieval trace.",
        ),
    )

    if original_query_trace_available:
        # V1 deliberately has no fabricated trace parser. A real replay package
        # would need to bind the historical query/retrieval artifacts before an
        # IDENTIFIED verdict could be returned.
        causal = HistoricalCausalVerdict.CANNOT_CHECK
        blockers = ("historical trace supplied but no bound trace-replay artifact was registered",)
    else:
        causal = HistoricalCausalVerdict.PARTIALLY_IDENTIFIED
        blockers = (
            "original query/retrieval trace is unavailable: cannot distinguish faithful-route retrieval miss from execution/routing/fixation on the original run",
        )

    return ParentDomainReplayResult(
        local_report=report,
        historical_causal_verdict=causal,
        historical_blockers=blockers,
        named_basis_omissions=omissions,
        fresh_transfer_accuracy=fresh_accuracy,
    )


__all__ = [
    "HISTORICAL_MINIMUM_ROUTE_FAMILIES",
    "HistoricalCausalVerdict",
    "ParentDomainReplayResult",
    "RAKL_SELF_RAKL_SOURCE",
    "run_parent_domain_replay",
]

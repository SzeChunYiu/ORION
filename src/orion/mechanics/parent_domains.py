from __future__ import annotations

from dataclasses import dataclass, replace

from .model import MechanicCell


@dataclass(frozen=True)
class ParentDomain:
    domain_id: str
    canonical_problem: str
    characteristic_variables: tuple[str, ...]
    transferable_mechanisms: tuple[str, ...]
    provenance_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.domain_id.strip() or not self.canonical_problem.strip():
            raise ValueError("parent domain identity and canonical problem are required")
        if not self.characteristic_variables or not self.transferable_mechanisms or not self.provenance_ids:
            raise ValueError("parent domain requires variables, transferable mechanisms and provenance")


@dataclass(frozen=True)
class ParentDomainHypothesis:
    mechanic_id: str
    domain_id: str
    mapping_question: str
    expected_missing_coordinates: tuple[str, ...]
    status: str = "CANDIDATE_SEARCH_SEED"

    def __post_init__(self) -> None:
        if any(not item.strip() for item in (self.mechanic_id, self.domain_id, self.mapping_question, self.status)):
            raise ValueError("parent-domain hypothesis fields cannot be empty")
        if not self.expected_missing_coordinates:
            raise ValueError("parent-domain hypothesis requires expected missing coordinates")


DOMAIN_CATALOG: dict[str, ParentDomain] = {
    "systems-engineering": ParentDomain(
        "systems-engineering",
        "Decompose stakeholder needs into traceable requirements, interfaces, designs, verification obligations and controlled changes.",
        ("requirements", "interfaces", "states", "verification methods", "technical performance measures", "dependencies"),
        ("hierarchical decomposition", "requirements traceability", "interface management", "verification matrices", "decision analysis"),
        ("PRIMARY:NASA-Systems-Engineering-Handbook",),
    ),
    "decision-analysis-operations-research": ParentDomain(
        "decision-analysis-operations-research",
        "Choose among alternatives under objectives, constraints, uncertainty, resources and risk.",
        ("alternatives", "objectives", "constraints", "resources", "uncertainty", "risk"),
        ("multi-criteria decision analysis", "optimization", "sensitivity analysis", "resource allocation"),
        ("PRIMARY:NASA-Decision-Analysis",),
    ),
    "information-retrieval": ParentDomain(
        "information-retrieval",
        "Retrieve and rank relevant information from a corpus under incomplete vocabulary and limited search budget.",
        ("query", "corpus", "relevance", "ranking", "recall", "precision", "retrieval cost"),
        ("query reformulation", "sparse/dense retrieval", "relevance feedback", "recall estimation", "active search"),
        ("RAKL:search-policy-learning", "RAKL:epistemic-search"),
    ),
    "systematic-review-information-science": ParentDomain(
        "systematic-review-information-science",
        "Search heterogeneous literature sources transparently enough to support evidence synthesis and stopping decisions.",
        ("databases", "search strategies", "screening decisions", "recall", "study identity", "stopping criteria"),
        ("multi-database search", "deduplication", "screening", "search documentation", "stopping/recall audits"),
        ("RAKL:epistemic-saturation",),
    ),
    "literature-based-discovery": ParentDomain(
        "literature-based-discovery",
        "Discover useful implicit connections among literatures that do not cite or name one another.",
        ("literature clusters", "bridge concepts", "latent relations", "novel hypotheses"),
        ("cross-literature bridge search", "open/closed discovery", "concept linking"),
        ("RAKL:apple-jump", "RAKL:open-world-discovery"),
    ),
    "computational-linguistics": ParentDomain(
        "computational-linguistics",
        "Represent and recover meaning expressed in natural language across syntax, semantics, discourse and pragmatics.",
        ("predicates", "arguments", "referents", "events", "scope", "modality", "discourse relations", "coreference"),
        ("semantic role labeling", "semantic parsing", "coreference", "discourse analysis", "scientific information extraction"),
        ("PRIMARY:ACL-SciERC-D18-1360", "PRIMARY:ACL-DyGIE-D19-1585"),
    ),
    "data-integration-entity-resolution": ParentDomain(
        "data-integration-entity-resolution",
        "Reconcile heterogeneous schemas/records and determine when different records denote the same underlying entity or event.",
        ("schemas", "records", "entities", "keys", "mappings", "provenance", "conflicts"),
        ("schema mapping", "entity matching", "mapping composition", "data lineage", "conflict resolution"),
        ("PRIMARY:Halevy-Rajaraman-Ordille-2006",),
    ),
    "knowledge-representation-reasoning": ParentDomain(
        "knowledge-representation-reasoning",
        "Represent structured knowledge, compatibility, inconsistency and inference while preserving logical scope and provenance.",
        ("facts", "relations", "constraints", "contexts", "proofs", "inconsistencies"),
        ("typed relations", "constraint reasoning", "belief revision", "truth maintenance", "local/global consistency"),
        ("RAKL:formal-system-specification",),
    ),
    "truth-maintenance-incremental-reasoning": ParentDomain(
        "truth-maintenance-incremental-reasoning",
        "Track justifications/dependencies so new information can retract or reconsider only affected beliefs/results.",
        ("beliefs", "justifications", "dependencies", "assumptions", "retractions", "contexts"),
        ("dependency-directed reconsideration", "truth maintenance", "incremental invalidation", "minimal change"),
        ("PRIMARY:AAAI-Truth-Maintenance",),
    ),
    "reliability-model-based-diagnosis": ParentDomain(
        "reliability-model-based-diagnosis",
        "Explain abnormal observations using models of components, failure modes, effects and competing diagnoses.",
        ("components", "expected behavior", "observations", "failure modes", "causes", "diagnoses", "detectability"),
        ("FMEA", "model-based diagnosis", "fault isolation", "discriminating tests", "failure propagation"),
        ("PRIMARY:AAAI-Model-Based-Diagnosis",),
    ),
    "causal-inference-experimental-design": ParentDomain(
        "causal-inference-experimental-design",
        "Separate competing causal explanations and select observations/interventions that identify target effects or mechanisms.",
        ("causal hypotheses", "interventions", "confounders", "identification", "outcomes", "design"),
        ("identification analysis", "controlled intervention", "optimal/discriminating experiment design", "sensitivity analysis"),
        ("RAKL:causal-inference-route",),
    ),
    "measurement-science-psychometrics": ParentDomain(
        "measurement-science-psychometrics",
        "Define the construct/measurand, instrument, validity, uncertainty and generalizability of measurements/evaluations.",
        ("construct", "measurand", "instrument", "items", "methods", "validity", "reliability", "uncertainty"),
        ("construct validation", "measurement uncertainty", "generalizability", "measurement invariance", "item-level modeling"),
        ("PRIMARY:NIST-AI-Measurement-Science",),
    ),
    "metareasoning-control": ParentDomain(
        "metareasoning-control",
        "Allocate computation/attention/actions adaptively based on expected value, progress, cost and feedback.",
        ("state", "observations", "actions", "utility/value", "cost", "feedback", "stopping"),
        ("value of computation", "feedback control", "exploration/exploitation", "strategy switching"),
        ("RAKL:challenge-learning", "RAKL:search-control"),
    ),
    "case-based-experience-learning": ParentDomain(
        "case-based-experience-learning",
        "Retrieve structurally similar prior episodes, adapt their lessons, and verify reuse in the new case.",
        ("cases", "problem signatures", "solutions", "outcomes", "similarity", "adaptation", "reuse validity"),
        ("case retrieval", "structural matching", "adaptation", "experience-aided diagnosis", "transfer validation"),
        ("RAKL:experience-substrate",),
    ),
    "software-reliability-reproducibility": ParentDomain(
        "software-reliability-reproducibility",
        "Execute workflows reproducibly under concurrency, retries, failures, external side effects and versioned dependencies.",
        ("run identity", "state", "events", "side effects", "retries", "versions", "artifacts", "SLOs"),
        ("idempotency", "durable execution", "content addressing", "event sourcing", "fault containment", "CI/hostile testing"),
        ("PRIMARY:NASA-Software-Engineering-Handbook",),
    ),
    "human-sensemaking-information-foraging": ParentDomain(
        "human-sensemaking-information-foraging",
        "Allocate attention/search among information patches and restructure representations as evidence accumulates.",
        ("information scent", "patch value", "switching cost", "representation", "attention", "sensemaking state"),
        ("patch switching", "information foraging", "sensemaking loops", "representation restructuring"),
        ("RAKL:self-rakl-human-breakthrough-route",),
    ),
}


_DEFAULT_BY_PREFIX: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("FRAME.", ("systems-engineering", "decision-analysis-operations-research", "measurement-science-psychometrics")),
    ("SEARCH.", ("information-retrieval", "systematic-review-information-science", "literature-based-discovery", "human-sensemaking-information-foraging")),
    ("ABSORB.", ("computational-linguistics", "data-integration-entity-resolution", "measurement-science-psychometrics", "knowledge-representation-reasoning")),
    ("RECONSTRUCT.", ("data-integration-entity-resolution", "knowledge-representation-reasoning", "systems-engineering")),
    ("DETECT.", ("knowledge-representation-reasoning", "reliability-model-based-diagnosis", "measurement-science-psychometrics")),
    ("DIAGNOSE.", ("reliability-model-based-diagnosis", "causal-inference-experimental-design", "case-based-experience-learning", "metareasoning-control")),
    ("REFRAME.", ("metareasoning-control", "systems-engineering", "human-sensemaking-information-foraging", "decision-analysis-operations-research")),
    ("REOPEN.", ("truth-maintenance-incremental-reasoning", "knowledge-representation-reasoning", "software-reliability-reproducibility")),
    ("SATURATE.", ("systematic-review-information-science", "information-retrieval", "human-sensemaking-information-foraging", "metareasoning-control")),
    ("CROSS.MEMORY", ("case-based-experience-learning", "information-retrieval", "software-reliability-reproducibility")),
    ("CROSS.AUTHORITY", ("knowledge-representation-reasoning", "measurement-science-psychometrics", "systems-engineering")),
    ("CROSS.EXPERIENCE", ("case-based-experience-learning", "reliability-model-based-diagnosis")),
    ("CROSS.REVIEW", ("systems-engineering", "reliability-model-based-diagnosis", "measurement-science-psychometrics")),
    ("CROSS.BENCHMARK", ("measurement-science-psychometrics", "causal-inference-experimental-design")),
    ("CROSS.EXPERIMENT_SELECTION", ("causal-inference-experimental-design", "decision-analysis-operations-research", "metareasoning-control")),
    ("CROSS.EXECUTION", ("software-reliability-reproducibility", "systems-engineering")),
    ("CROSS.CONTEXT_POLICY", ("metareasoning-control", "human-sensemaking-information-foraging", "decision-analysis-operations-research")),
)

_TOP_LEVEL: dict[str, tuple[str, ...]] = {
    "ORION_SOLVE.v1": ("systems-engineering", "metareasoning-control", "knowledge-representation-reasoning", "software-reliability-reproducibility"),
    "FRAME.v1": ("systems-engineering", "decision-analysis-operations-research"),
    "SEARCH.v1": ("information-retrieval", "systematic-review-information-science", "literature-based-discovery"),
    "ABSORB.v1": ("computational-linguistics", "data-integration-entity-resolution", "measurement-science-psychometrics"),
    "RECONSTRUCT.v1": ("data-integration-entity-resolution", "knowledge-representation-reasoning"),
    "DETECT.v1": ("reliability-model-based-diagnosis", "knowledge-representation-reasoning"),
    "DIAGNOSE.v1": ("reliability-model-based-diagnosis", "causal-inference-experimental-design", "case-based-experience-learning"),
    "REFRAME.v1": ("metareasoning-control", "human-sensemaking-information-foraging", "systems-engineering"),
    "REOPEN.v1": ("truth-maintenance-incremental-reasoning", "software-reliability-reproducibility"),
    "SATURATE_BOUNDED.v3": ("systematic-review-information-science", "information-retrieval", "human-sensemaking-information-foraging"),
}


def candidate_parent_domain_ids(cell: MechanicCell) -> tuple[str, ...]:
    direct = _TOP_LEVEL.get(cell.mechanic_id)
    if direct is not None:
        return direct
    for prefix, domain_ids in _DEFAULT_BY_PREFIX:
        if cell.mechanic_id.startswith(prefix):
            return domain_ids
    return ("systems-engineering", "metareasoning-control")


def parent_domain_hypotheses(cell: MechanicCell) -> tuple[ParentDomainHypothesis, ...]:
    hypotheses: list[ParentDomainHypothesis] = []
    for domain_id in candidate_parent_domain_ids(cell):
        domain = DOMAIN_CATALOG[domain_id]
        hypotheses.append(
            ParentDomainHypothesis(
                mechanic_id=cell.mechanic_id,
                domain_id=domain_id,
                mapping_question=(
                    f"How does {domain_id} formulate the operation '{cell.purpose}', and which variables, failure modes, interfaces or validation practices does that formulation expose that the current mechanic cell lacks?"
                ),
                expected_missing_coordinates=domain.characteristic_variables,
            )
        )
    return tuple(hypotheses)


def apply_parent_domain_hypotheses(cell: MechanicCell) -> MechanicCell:
    hypotheses = parent_domain_hypotheses(cell)
    empirical_open = tuple(
        dict.fromkeys(
            cell.empirical_open_coordinates
            + (
                "parent-domain hypotheses are search seeds only; live domain search, nearest-work assimilation and independent omission challenge remain open",
            )
        )
    )
    return replace(
        cell,
        parent_domain_hypotheses=tuple(item.domain_id for item in hypotheses),
        empirical_open_coordinates=empirical_open,
    )


def apply_parent_domain_hypotheses_to_all(cells: tuple[MechanicCell, ...]) -> tuple[MechanicCell, ...]:
    return tuple(apply_parent_domain_hypotheses(cell) for cell in cells)

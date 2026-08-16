"""Knowledge-space representation: retrieval, assimilation and source-local meaning."""

from orion.knowledge.ignorance import (
    IgnoranceAction,
    IgnoranceActionPlan,
    IgnoranceKind,
    IgnoranceProjection,
    ScientificIgnoranceInterpreter,
    deduplicate_ignorance,
    plan_for_ignorance,
)
from orion.knowledge.parent_domains import (
    FunctionalOperationSignature,
    ParentDisciplineCandidate,
    ParentDisciplineProfile,
    discover_parent_disciplines,
    named_basis_mentions,
    top_parent_discipline,
)
from orion.knowledge.semantics import (
    MeaningComparison,
    MeaningRelation,
    Modality,
    Polarity,
    ScientificLanguageInterpreter,
    ScientificMeaningProjection,
    bridge_compatible,
    compare_meaning,
)

__all__ = [
    "FunctionalOperationSignature",
    "IgnoranceAction",
    "IgnoranceActionPlan",
    "IgnoranceKind",
    "IgnoranceProjection",
    "MeaningComparison",
    "MeaningRelation",
    "Modality",
    "ParentDisciplineCandidate",
    "ParentDisciplineProfile",
    "Polarity",
    "ScientificIgnoranceInterpreter",
    "ScientificLanguageInterpreter",
    "ScientificMeaningProjection",
    "bridge_compatible",
    "compare_meaning",
    "deduplicate_ignorance",
    "discover_parent_disciplines",
    "named_basis_mentions",
    "plan_for_ignorance",
    "top_parent_discipline",
]

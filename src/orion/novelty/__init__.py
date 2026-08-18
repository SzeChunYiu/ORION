"""Scientific novelty certificates with explicit authority semantics."""

from orion.novelty.authority import decide_final_state
from orion.novelty.certificate import (
    CertificateDraft,
    DatedSearchSnapshot,
    DiscriminatingExperiment,
    HostileAlreadySolvedRoute,
    MechanismAtom,
    OverlapRecord,
    PriorWorkRef,
    ScientificNoveltyCertificate,
    seal_certificate,
)
from orion.novelty.fixtures import adversarial_fixtures
from orion.novelty.saturation import (
    SearchRoundRecord,
    SearchSaturationProtocol,
    SaturationStopReport,
    assess_saturation,
)
from orion.novelty.self_application import apply_orion_residuals
from orion.novelty.types import (
    SCHEMA_ID,
    ExperimentStatus,
    MechanismOverlap,
    NoveltyFinalState,
    NoveltySearchRoute,
    REQUIRED_SEARCH_ROUTES,
    SourceAccess,
)

__all__ = [
    "SCHEMA_ID",
    "CertificateDraft",
    "DatedSearchSnapshot",
    "DiscriminatingExperiment",
    "ExperimentStatus",
    "HostileAlreadySolvedRoute",
    "MechanismAtom",
    "MechanismOverlap",
    "NoveltyFinalState",
    "NoveltySearchRoute",
    "OverlapRecord",
    "PriorWorkRef",
    "REQUIRED_SEARCH_ROUTES",
    "SearchRoundRecord",
    "SearchSaturationProtocol",
    "SaturationStopReport",
    "ScientificNoveltyCertificate",
    "SourceAccess",
    "adversarial_fixtures",
    "apply_orion_residuals",
    "assess_saturation",
    "decide_final_state",
    "seal_certificate",
]

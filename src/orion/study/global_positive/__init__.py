"""GlobalPositiveCertificate.v1 — Pareto admission freeze (issue #285)."""

from orion.study.global_positive.admission import (
    AdmissionDecision,
    ProgrammeDecision,
    admit_candidate,
    programme_terminal,
    published_programme_state,
)
from orion.study.global_positive.baselines import (
    BaselineKind,
    certificate_versus_baselines,
    score_all_baselines,
    score_baseline,
)
from orion.study.global_positive.outcomes import (
    CandidateOutcomeBundle,
    NegativeHistory,
    NegativeHistoryRecord,
    ObservationStatus,
    family_outcome,
)
from orion.study.global_positive.packet import build_packet
from orion.study.global_positive.portfolio import (
    freeze_fingerprint,
    load_portfolio,
    portfolio_hash,
)
from orion.study.global_positive.schema import (
    CandidateTerminal,
    ProgrammeTerminal,
    load_schema,
    schema_hash,
)

ADOPTION_BOUNDARY = "V2_ADDITIVE"

__all__ = [
    "AdmissionDecision",
    "BaselineKind",
    "CandidateOutcomeBundle",
    "CandidateTerminal",
    "NegativeHistory",
    "NegativeHistoryRecord",
    "ObservationStatus",
    "ProgrammeDecision",
    "ProgrammeTerminal",
    "admit_candidate",
    "build_packet",
    "certificate_versus_baselines",
    "family_outcome",
    "freeze_fingerprint",
    "load_portfolio",
    "load_schema",
    "portfolio_hash",
    "programme_terminal",
    "published_programme_state",
    "schema_hash",
    "score_all_baselines",
    "score_baseline",
]

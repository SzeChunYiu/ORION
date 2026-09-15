"""Credential-free substrate for the frozen Shadow Self-ORION live research trial.

This package builds everything issue #8 requires *except* the live execution, and
freezes it before any outcome can be observed. Nothing here makes a network call,
reads a credential value, or needs a provider to be constructed. What it produces:

* a frozen task packet (one wide-literature task, one deep-target task) whose
  provider identities, resource limits, evaluator and matched baseline are fixed
  and bound by content hash, exactly as the ORION-P1 suite binds its cases;
* a mechanical question surface built from fixed mechanic cells, so the eight
  dimensions the issue names -- observability, mathematics, handoff, failure,
  storage, verification, parent-discipline and saturation -- are exposed by a
  fixed audit grammar rather than by asking a model what it forgot;
* raw query/retrieval trace retention, with retrieved-but-unused distinguished
  from present-but-missed *where ground truth permits* and reported as
  CANNOT_CHECK where it does not;
* immutable episodes for every failed, partial or refused mechanic execution,
  shaped so `orion.experience.learning.propose_failure_pattern` can match them;
* an authority boundary that refuses promotion structurally rather than by
  convention.

**Success boundary (issue #8, honoured verbatim).** Success for this trial means
the live stack exercises ORION's governed loop and yields interpretable evidence
about failures. It does not by itself establish general autonomous-science
capability, and it does not establish Self-ORION readiness. No object, verdict or
field in this package may be read as evidence of either. `AuthorityDecision` can
only ever be a refusal, and `BoundedSaturationState.certifies_recall` is fixed at
False for the same reason `orion.kernel.saturation.SaturationReport` fixes it.

**Credential handling.** Follows `orion.study.p1.provider`: presence is tested via
`os.environ`, the value is never read into a variable, never stored on an object,
never serialized. Absence is a typed refusal that records CANNOT_CHECK, never a
zero -- "could not check" and "checked and found wrong" are different facts, and a
substrate that records the first as the second reports a missing environment
variable as a failed trial. The refusal is defined locally rather than imported so
that paper-05 substrate does not drag the P1 case/system modules or P1's subject
model id into its dependency surface; what is shared is the contract, not the code.

**No fabrication.** The packet defines tasks. It contains no literature, no
citations, no results and no provider responses. The deep-target ground truth is
a protected gold whose plaintext never reaches the public document -- only its
digest does -- following the `protected_gold` separation in the P1 case suite.

**Layout.** One module per numbered section of the original design, in dependency
order. Every public name is re-exported here, so `orion.self_orion.live_packet`
remains the single import surface.

* `constants`        -- frozen ids, paths, exit codes, the one hashing primitive
* `identity`         -- (1) provider identities, resource limits, evaluator spec
* `tasks`            -- (2) the two frozen tasks and the protected gold
* `packet`           -- (3) the packet and its JSON publish/load round trip
* `mechanic_cells`   -- (4a) the fixed mechanic cells
* `question_surface` -- (4b) the mechanical question surface over those cells
* `trace`            -- (5) raw trace retention, evidence-use classification
* `evaluation`       -- (6) the frozen criterion evaluator
* `refusal`          -- (7) typed provider refusal and episode minting
* `authority`        -- (8, 9) authority boundary, bounded-saturation outcomes
* `cli`              -- (10) preflight, execution manifest and the one command
* `__main__`         -- keeps `python -m orion.self_orion.live_packet` working,
  which the published packet names in the `execution` block its fingerprint
  covers
"""

from __future__ import annotations

from orion.core.problem import Problem
from orion.core.search import SearchRouteKind
from orion.experience.learning import propose_failure_pattern
from orion.experience.model import (
    EpisodeOutcome, FailurePatternCandidate, LessonAuthority, TaskEpisode,
)
from orion.mechanics.model import (
    HandoffField, MechanicCell, MechanicDimension, MetricDirection, MetricKind, MetricSpec,
)
from orion.mechanics.questioning import MechanicQuestion, generate_mechanic_questions
from orion.self_orion.live_trial import (
    FrozenLiveTrialPacket, FrozenTrialTask, ResearchTrialKind, ShadowLiveTrialRunner,
)

from .constants import (
    _sha256, BASELINE_ID, EVALUATION_EPOCH_ID, EXIT_CANNOT_CHECK, EXIT_ERROR, EXIT_OK, LIVE_RUNNER,
    LIVE_STACK_CONSTRUCTOR, PACKET_ID, PACKET_SCHEMA, PREFLIGHT_TIMESTAMP, PROTOCOL_PATH,
    PROTOCOL_RELATIVE_PATH, REPO_ROOT, SUCCESS_BOUNDARY, UNBOUND,
)
from .identity import (
    CheckableCriterion, CREDENTIAL_ENV_VARS, CriterionCheck, DEEP_CRITERIA, FROZEN_BASELINE,
    FROZEN_EVALUATOR, FROZEN_LIMITS, FROZEN_PROVIDERS, FrozenEvaluatorSpec, FrozenProviderIdentity,
    FrozenResourceLimits, MatchedBaselineSpec, WIDE_CRITERIA,
)
from .tasks import (
    _DEEP_TASK, _DEEP_TASK_GOLD, _WIDE_TASK, DEEP_TASK_ID, FrozenTaskBinding, ProtectedTargetGold,
    WIDE_TASK_ID,
)
from .packet import (
    _provider_manifest_hash, _reject_secret_material, frozen_live_research_packet,
    FrozenLiveResearchPacket, load_packet_document, packet_document, write_packet_document,
)
from .mechanic_cells import (
    _fibre, _SHARED_AUTHORITY, _SHARED_ENGINEERING, _SHARED_PROVENANCE, _SHARED_REOPEN,
    _SHARED_RESOURCES, FIBRE_PROVIDER_ROLES, ISSUE_8_DIMENSIONS, live_trial_mechanic_cells,
)
from .question_surface import (
    emit_open_questions, question_surface_coverage, question_surface_summary,
    QuestionSurfaceCoverage,
)
from .trace import (
    classify_evidence_use, EvidenceUseClass, EvidenceUseReport, QueryTrace, RawTrialTrace,
    TraceItem,
)
from .evaluation import (
    _evaluate_criterion, CriterionResult, CriterionStatus, evaluate_task, TaskOutcomeInput,
)
from .refusal import (
    _state_hash, blocked_mechanic_ids, credential_present, failure_pattern_candidates,
    LiveProviderStatus, missing_credential_env_vars, NO_CREDENTIAL_SIGNATURE, refusal_episodes,
)
from .authority import (
    AuthorityDecision, AuthorityRequestKind, BoundedSaturationOutcome, BoundedSaturationState,
    pre_execution_saturation_state, propose_repair, RepairProposal, request_promotion,
)
from .cli import (
    _print_status, _run_live, execution_manifest, EXECUTION_MANIFEST_SCHEMA, LiveTrialPreflight,
    main, preflight,
)


__all__ = [
    "BASELINE_ID",
    "CREDENTIAL_ENV_VARS",
    "EVALUATION_EPOCH_ID",
    "EXECUTION_MANIFEST_SCHEMA",
    "EXIT_CANNOT_CHECK",
    "EXIT_ERROR",
    "EXIT_OK",
    "FIBRE_PROVIDER_ROLES",
    "FROZEN_BASELINE",
    "FROZEN_EVALUATOR",
    "FROZEN_LIMITS",
    "FROZEN_PROVIDERS",
    "ISSUE_8_DIMENSIONS",
    "NO_CREDENTIAL_SIGNATURE",
    "PACKET_ID",
    "PACKET_SCHEMA",
    "PREFLIGHT_TIMESTAMP",
    "PROTOCOL_PATH",
    "PROTOCOL_RELATIVE_PATH",
    "SUCCESS_BOUNDARY",
    "UNBOUND",
    "AuthorityDecision",
    "AuthorityRequestKind",
    "BoundedSaturationOutcome",
    "BoundedSaturationState",
    "CheckableCriterion",
    "CriterionCheck",
    "CriterionResult",
    "CriterionStatus",
    "EvidenceUseClass",
    "EvidenceUseReport",
    "FrozenEvaluatorSpec",
    "FrozenLiveResearchPacket",
    "FrozenProviderIdentity",
    "FrozenResourceLimits",
    "FrozenTaskBinding",
    "LiveProviderStatus",
    "LiveTrialPreflight",
    "MatchedBaselineSpec",
    "ProtectedTargetGold",
    "QueryTrace",
    "QuestionSurfaceCoverage",
    "RawTrialTrace",
    "RepairProposal",
    "TaskOutcomeInput",
    "TraceItem",
    "blocked_mechanic_ids",
    "classify_evidence_use",
    "credential_present",
    "emit_open_questions",
    "evaluate_task",
    "execution_manifest",
    "failure_pattern_candidates",
    "frozen_live_research_packet",
    "live_trial_mechanic_cells",
    "load_packet_document",
    "main",
    "missing_credential_env_vars",
    "packet_document",
    "pre_execution_saturation_state",
    "preflight",
    "propose_repair",
    "question_surface_coverage",
    "question_surface_summary",
    "refusal_episodes",
    "request_promotion",
    "write_packet_document",
]

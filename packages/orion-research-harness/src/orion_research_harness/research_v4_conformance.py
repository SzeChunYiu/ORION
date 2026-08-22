from __future__ import annotations

from orion import registry
from orion.core.research_resolution import (
    AssimilationDisposition,
    ResearchOutcomeKind,
    ResolutionAction,
    ResolutionState,
    UnresolvedClass,
)

from . import recursive_runner as _rr
from .research_resolution import assimilate_negative_result, build_resolution_obligation


TERMINAL = "ORION_PAPER_FRAMEWORK_HARNESS_COVARIANCE_V4_OPERATIONAL"


def research_v4_conformance() -> dict[str, object]:
    resource = build_resolution_obligation(
        subject_id="conformance:resource",
        unresolved_class=UnresolvedClass.RESOURCE,
        reason_codes=("RESOURCE_BOUND",),
    )
    protected = build_resolution_obligation(
        subject_id="conformance:protected",
        unresolved_class=UnresolvedClass.PROTECTED_EXTERNAL,
        reason_codes=("PROTECTED_NOT_RELEASED",),
        blocker_ids=("protected:evidence",),
    )
    donor = assimilate_negative_result(
        result_id="conformance:negative:donor",
        subject_id="conformance:method",
        negative_kind="DONOR_SUBSUMED",
        evidence_ids=("e:donor",),
        reason_codes=("SAME_REACH",),
    )
    obstruction = assimilate_negative_result(
        result_id="conformance:negative:obstruction",
        subject_id="conformance:method",
        negative_kind="VERIFIED_OBSTRUCTION",
        evidence_ids=("e:obstruction",),
        reason_codes=("NONREACHABILITY",),
    )

    probes = {
        "framework_registers_resolution_obligation": "ResearchResolutionObligation.v1" in registry.MECHANICS_SUBSTRATE_IDS,
        "framework_registers_negative_result": "ResearchNegativeResult.v1" in registry.MECHANICS_SUBSTRATE_IDS,
        "resource_unresolved_is_active_and_nonstopping": (
            resource.outcome_kind is ResearchOutcomeKind.UNRESOLVED
            and resource.state is ResolutionState.ACTIVE
            and ResolutionAction.REQUEST_RESOURCE_WIDENING in resource.next_actions
            and ResolutionAction.TASK_STOP not in resource.next_actions
        ),
        "protected_unresolved_is_typed_external_block": (
            protected.state is ResolutionState.BLOCKED_EXTERNAL
            and protected.next_actions == (ResolutionAction.REQUEST_PROTECTED_EVIDENCE,)
        ),
        "donor_subsumption_is_negative_not_unknown": (
            donor.outcome_kind is ResearchOutcomeKind.NEGATIVE
            and AssimilationDisposition.REGISTER_DONOR_SUBSUMPTION in donor.dispositions
        ),
        "obstruction_is_negative_and_reframes": (
            obstruction.outcome_kind is ResearchOutcomeKind.NEGATIVE
            and AssimilationDisposition.ASSIMILATE_OBSTRUCTION in obstruction.dispositions
            and AssimilationDisposition.REFRAME in obstruction.dispositions
        ),
        "recursive_unresolved_projection_installed": bool(
            getattr(_rr, "_research_resolution_v4_installed", False)
        ),
        "resolution_objects_never_grant_authority": not any(
            (
                resource.grants_scientific_authority,
                resource.grants_novelty_authority,
                resource.grants_promotion_authority,
                resource.grants_global_task_stop_authority,
                donor.grants_scientific_authority,
                donor.grants_novelty_authority,
                donor.grants_promotion_authority,
                donor.grants_global_task_stop_authority,
            )
        ),
    }
    failed = sorted(key for key, passed in probes.items() if not passed)
    return {
        "schema": "ORION.PaperFrameworkHarnessCovarianceConformance.v4",
        "terminal": TERMINAL if not failed else "ORION_PAPER_FRAMEWORK_HARNESS_COVARIANCE_V4_FAILED",
        "operational": not failed,
        "failed_probes": failed,
        "probes": probes,
        "framework_version": registry.FRAMEWORK_VERSION,
        "paper_sync_epoch": registry.PAPER_SYNC_EPOCH,
        "grants_scientific_authority": False,
        "grants_novelty_authority": False,
        "grants_promotion_authority": False,
        "grants_global_task_stop_authority": False,
        "note": (
            "V4 proves outcome-lifecycle and covariance wiring only. It does not prove every scientific question is decidable, "
            "and it does not convert verified negative results into positive ones."
        ),
    }


__all__ = ["TERMINAL", "research_v4_conformance"]

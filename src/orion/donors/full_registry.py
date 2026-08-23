from __future__ import annotations

from .registry import (
    DonorCapability,
    DonorDisposition,
    DonorExecutionMode,
    DonorRegistry,
    normal_orion_donor_registry as _public_registry,
    orion_q_donor_registry as _q_public_registry,
)


def _engineering(
    fibre_id: str,
    disposition: DonorDisposition,
    mechanic_ids: tuple[str, ...],
    *,
    reason: str = "",
    trigger: str = "",
) -> DonorCapability:
    if disposition is DonorDisposition.DEFER_WITH_TRIGGER:
        mode = DonorExecutionMode.DEFERRED
    elif disposition is DonorDisposition.TESTS_RESULTS_REUSED:
        mode = DonorExecutionMode.REGRESSION_ONLY
    else:
        mode = DonorExecutionMode.NATIVE
    boundary = reason or trigger
    return DonorCapability(
        capability_id=f"rakl-engineering:{fibre_id}",
        donor_id="RAKL-engineering",
        source_version="70f5f7c4a6771ffd1158765b42ac9f8aee8a270f",
        disposition=disposition,
        execution_mode=mode,
        mechanic_ids=mechanic_ids,
        supported_task_classes=("GENERAL",),
        output_type="EngineeringConformanceOrRegressionReceipt",
        verifier_contract_ids=("ORION_ENGINEERING_CONFORMANCE",),
        resource_coordinates=("reliability", "latency", "storage", "operations"),
        failure_modes=(
            "identity_or_sequence_corruption",
            "idempotency_or_recovery_failure",
            "state_or_receipt_mismatch",
            "unsafe_readiness_or_release",
        ),
        applicability_boundary=(
            boundary
            or "Engineering donor is retained as a conformance/regression obligation; it grants no scientific authority."
        ),
        evidence_paths=("provenance/rakl/DONOR_DISPOSITION_V3.json",),
        reopen_trigger=trigger,
    )


def engineering_donor_capabilities() -> tuple[DonorCapability, ...]:
    R = DonorDisposition.RECONSTRUCTED
    T = DonorDisposition.TESTS_RESULTS_REUSED
    D = DonorDisposition.DEFER_WITH_TRIGGER
    return (
        _engineering("E1", R, ("CROSS.MEMORY", "CROSS.EXECUTION"), reason="Typed K/W/M, mechanic cells and versioned transition projection provide the donor state role."),
        _engineering("E2", D, ("CROSS.MEMORY", "CROSS.EXECUTION"), trigger="When ORION introduces production multi-plane persistence, reuse RAKL repository protocols/parity fixtures before defining new storage APIs."),
        _engineering("E3", D, ("CROSS.MEMORY", "CROSS.EXECUTION"), trigger="Before production SQLite/Postgres persistence, carry CAS, sequence-rewind and action-payload binding regressions."),
        _engineering("E4", T, ("REOPEN", "SATURATE", "DETECT.COVERAGE"), reason="Retain stale-certificate, missing-route, residual-reopen and coverage-not-reachability hostile results."),
        _engineering("E5", D, ("CROSS.EXECUTION",), trigger="Before durable workflow workers/leases, reuse exact idempotency, retry, recovery, heartbeat and crash-window contracts."),
        _engineering("E6", D, ("CROSS.EXECUTION", "CROSS.AUTHORITY"), trigger="Before a network service/UI, preserve read-only observatory and render-never-calculate epistemic-state boundaries."),
        _engineering("E7", D, ("CROSS.EXECUTION", "CROSS.REVIEW"), trigger="Before production deployment, execute provenance/security/backup/restore/doctor/telemetry hostile campaigns."),
        _engineering("E8", T, ("CROSS.AUTHORITY", "CROSS.REVIEW"), reason="Retain typed terminal vocabulary, fresh hostile assurance and no-clean-release-overclaim regressions."),
        _engineering("E9", T, ("CROSS.BENCHMARK", "CROSS.EXPERIENCE"), reason="Retain RAKL engineering conformance and negative-history methodology as donor regressions."),
        _engineering("E10", D, ("CROSS.EXECUTION",), trigger="Before a production service front, reuse route completeness, receipts-on-every-outcome and state-in-store-not-service contracts."),
        _engineering("E11", T, ("CROSS.MEMORY", "CROSS.EXECUTION"), reason="Retain restore/cross-plane corruption findings as production-persistence obligations."),
        _engineering("E12", D, ("CROSS.EXECUTION",), trigger="Before telemetry exporter integration, preserve exporter-outage must-not-take-request-down regression."),
        _engineering("E13", D, ("CROSS.AUTHORITY", "CROSS.EXECUTION"), trigger="Before real OIDC/secret-manager deployment, reuse donor identity/secret boundary tests."),
        _engineering("E14", T, ("CROSS.MEMORY", "CROSS.EXECUTION"), reason="Retain schema/index hostile findings as fail-closed state-validation regressions."),
        _engineering("E15", D, ("CROSS.MEMORY", "CROSS.EXECUTION"), trigger="Before PostgreSQL production backend, require WAL/PITR/failover and frozen schema execution."),
        _engineering("E16", T, ("CROSS.EXECUTION",), reason="Retain concurrency/idempotency failure classes as protected transaction-lifecycle obligations."),
        _engineering("E17", D, ("CROSS.EXECUTION", "CROSS.BENCHMARK"), trigger="Before setting production budgets, obtain production hardware capacity/SLO measurements rather than laptop proxies."),
        _engineering("E18", D, ("CROSS.REVIEW",), trigger="Before production release, require independent hostile assurance on the exact release."),
        _engineering("E19", T, ("CROSS.AUTHORITY", "CROSS.REVIEW"), reason="Retain release/conformance traceability as a promotion prerequisite."),
        _engineering("E20", D, ("CROSS.EXECUTION", "CROSS.REVIEW"), trigger="Before operational readiness claims, execute a live operator/runbook drill on the exact release."),
    )


def normal_orion_donor_registry() -> DonorRegistry:
    public = _public_registry()
    return DonorRegistry(
        (*public.capabilities, *engineering_donor_capabilities()),
        registry_id="orion:donors:normal:v2",
    )


def orion_q_donor_registry() -> DonorRegistry:
    q_public = _q_public_registry()
    # q_public already contains the 24 public RAKL families + 13 quantum specialists.
    return DonorRegistry(
        (*q_public.capabilities, *engineering_donor_capabilities()),
        registry_id="orion:donors:orion-q:v2",
    )


__all__ = [
    "engineering_donor_capabilities",
    "normal_orion_donor_registry",
    "orion_q_donor_registry",
]

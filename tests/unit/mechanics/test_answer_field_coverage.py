from __future__ import annotations

from orion.mechanics.answers import _STRING_FIELDS_BY_DIMENSION
from orion.mechanics.model import MechanicDimension

# Fields `questioning._satisfied` consults, per dimension. Kept explicit rather
# than introspected, so a change to either side has to be reconciled here.
_SATISFYING_FIELDS: dict[MechanicDimension, tuple[str, ...]] = {
    MechanicDimension.INPUTS: ("input_ids",),
    MechanicDimension.OUTPUTS: ("output_ids",),
    MechanicDimension.STATE: ("state_ids",),
    MechanicDimension.OBSERVABILITY: ("observable_ids",),
    MechanicDimension.ACTIONS: ("action_ids",),
    MechanicDimension.TRANSITION_MODEL: ("transition_semantics",),
    MechanicDimension.MATHEMATICS: ("mathematical_semantics",),
    MechanicDimension.INVARIANTS: ("invariant_ids", "constraint_ids"),
    MechanicDimension.OBJECTIVE: ("objective_ids",),
    MechanicDimension.OPTIMIZATION: ("optimization_rules",),
    MechanicDimension.UNCERTAINTY: ("uncertainty_semantics",),
    MechanicDimension.RESOURCES: ("resource_coordinates",),
    MechanicDimension.FAILURE: ("failure_signatures", "falsifiers"),
    MechanicDimension.DIAGNOSIS: ("diagnosis_rules",),
    MechanicDimension.STORAGE: ("storage_contracts",),
    MechanicDimension.PROVENANCE: ("provenance_contracts",),
    MechanicDimension.VERIFICATION: ("verification_contracts",),
    MechanicDimension.AUTHORITY_SECURITY: ("authority_boundaries",),
    MechanicDimension.ENGINEERING: ("engineering_contracts",),
    MechanicDimension.DEPENDENCIES: ("dependency_ids", "external_dependency_contract_ids"),
    MechanicDimension.REOPEN: ("reopen_triggers",),
    MechanicDimension.SEARCH_COVERAGE: ("search_coverage_obligations",),
    MechanicDimension.PARENT_DISCIPLINE: ("parent_domain_hypotheses",),
    MechanicDimension.SATURATION: ("saturation_criteria",),
    MechanicDimension.EMPIRICAL_OPEN: ("empirical_open_coordinates",),
}


def test_every_field_that_can_satisfy_a_dimension_is_writable_by_an_answer():
    """A cell must not be satisfiable through a field no answer may write.

    Found by merging a stale lane whose records wrote
    `external_dependency_contract_ids` for DEPENDENCIES: `_satisfied` accepted
    that field, the answer allowlist did not, so a question could be closed by
    hand in a way no answer record could ever reproduce. That asymmetry makes
    the audit unclosable through the governed path while looking closable.
    """

    gaps: list[str] = []
    for dimension, fields in _SATISFYING_FIELDS.items():
        writable = set(_STRING_FIELDS_BY_DIMENSION.get(dimension, ()))
        for field in fields:
            if field not in writable:
                gaps.append(f"{dimension.value}.{field}")
    assert not gaps, f"satisfying fields that no answer may write: {gaps}"


def test_no_answer_may_write_a_field_outside_its_dimension():
    """The converse: the allowlist must not grant reach beyond the dimension."""

    for dimension, writable in _STRING_FIELDS_BY_DIMENSION.items():
        allowed = set(_SATISFYING_FIELDS.get(dimension, ()))
        assert set(writable) <= allowed, (
            f"{dimension.value} may write fields that do not satisfy it: "
            f"{sorted(set(writable) - allowed)}"
        )

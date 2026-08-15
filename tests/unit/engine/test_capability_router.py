from orion.engine.capability_router import ExecutionModality, route_capability


def test_protected_control_mechanics_require_mechanical_execution():
    assert route_capability("SATURATE.STOP.v0").modality is ExecutionModality.MECHANICAL_REQUIRED
    assert route_capability("REOPEN.DEPENDENCY.v0").modality is ExecutionModality.MECHANICAL_REQUIRED
    assert route_capability("CROSS.AUTHORITY.v0").modality is ExecutionModality.MECHANICAL_REQUIRED
    assert "may not decide" in route_capability("CROSS.AUTHORITY.v0").llm_authority


def test_scientific_language_is_hybrid_but_llm_output_stays_candidate_only():
    route = route_capability("ABSORB.SCIENTIFIC_LANGUAGE.v0")
    assert route.modality is ExecutionModality.HYBRID_SEMANTIC
    assert "candidate structure" in route.llm_authority
    assert "deterministic" in route.fallback


def test_reframing_can_use_llm_as_proposer_but_not_authority():
    route = route_capability("REFRAME.REPRESENTATION.v0")
    assert route.modality is ExecutionModality.LLM_PROPOSAL
    assert "cannot authorize adoption" in route.llm_authority


def test_new_unknown_mechanic_defaults_to_mechanical_preference_not_llm_control():
    route = route_capability("NEW.MECHANIC.v0")
    assert route.modality is ExecutionModality.MECHANICAL_PREFERRED
    assert "supplemental proposal" in route.llm_authority

from __future__ import annotations

from orion_research_harness.mechanics_bridge import (
    EXPECTED_MECHANIC_CELL_COUNT,
    atom_calculus_surface,
    compile_workspace_development_fibre,
    mechanic_catalog,
    mechanics_coverage,
    method_fibre_surface,
    navigate_mechanics,
    saturation_surface,
)
from orion_research_harness.workspace import ResearchWorkspace


def _ids(result: dict) -> set[str]:
    return {row["surface_id"] for row in result["matches"]}


def test_full_canonical_mechanics_graph_is_discoverable():
    coverage = mechanics_coverage()
    assert coverage["mechanic_cell_count"] == EXPECTED_MECHANIC_CELL_COUNT == 59
    assert coverage["structurally_discoverable"] is True
    assert coverage["missing_anchor_ids"] == []
    assert coverage["missing_runtime_cells"] == []
    assert coverage["unknown_child_count"] == 0
    assert coverage["containment_cycle_count"] == 0
    assert coverage["unknown_dependency_count"] == 0
    assert coverage["dependency_cycle_count"] == 0
    assert coverage["mixed_cycle_count"] == 0


def test_catalog_exposes_atomization_fibre_and_saturation_cells():
    ids = {row["surface_id"] for row in mechanic_catalog()}
    assert "ORION_SOLVE.v1" in ids
    assert "FRAME.DECOMPOSE.v0" in ids
    assert "REOPEN.FIBRE.v0" in ids
    assert "SATURATE_BOUNDED.v3" in ids
    assert "SATURATE.KNOWLEDGE_FLATNESS.v0" in ids
    assert "SATURATE.FORMULATION_FLATNESS.v0" in ids
    assert "SATURATE.ROUTE_COVERAGE.v0" in ids
    assert "SATURATE.OMISSION_CHALLENGE.v0" in ids
    assert "SATURATE.STOP.v0" in ids


def test_fibre_problem_solver_navigation_finds_development_fibre_and_reopen():
    result = navigate_mechanics("fibre problem solver")
    ids = _ids(result)
    assert "SELF_ORION.DEVELOPMENT_FIBRE.v1" in ids
    assert "REOPEN.FIBRE.v0" in ids
    assert "FRAME.DECOMPOSE.v0" in ids


def test_problem_atomization_navigation_finds_decompose_and_atom_calculus():
    result = navigate_mechanics("atomization of a problem")
    ids = _ids(result)
    assert "FRAME.DECOMPOSE.v0" in ids
    assert "DISCOVERY.RECURSIVE_ATOM_CALCULUS.v1" in ids


def test_knowledge_saturation_navigation_finds_runtime_and_development_surfaces():
    result = navigate_mechanics("saturation of knowledge")
    ids = _ids(result)
    assert "SATURATE.KNOWLEDGE_FLATNESS.v0" in ids
    assert "SELF_ORION.DEVELOPMENT_SATURATION.v1" in ids
    assert "SATURATE.STOP.v0" in ids


def test_method_fibre_is_distinct_from_development_fibre():
    result = navigate_mechanics("method fibre")
    ids = _ids(result)
    assert "P6.METHOD_FIBRE.v1" in ids
    surface = method_fibre_surface()
    assert surface["authority"].startswith("FORMAL_EQUIVALENCE_FOR_DECLARED_CLAIM_ONLY")
    assert "preconditions" in surface["claim_relative_coordinates"]
    assert "lineage" in surface["claim_relative_coordinates"]


def test_development_fibre_compiles_from_actual_canonical_mechanic_graph(tmp_path):
    workspace = ResearchWorkspace.initialize(tmp_path / "ws", project_root=tmp_path)
    result = compile_workspace_development_fibre(workspace, "FRAME.DECOMPOSE.v0")
    fibre = result["fibre"]
    assert fibre["mechanic_id"] == "FRAME.DECOMPOSE.v0"
    assert result["mechanic"]["surface_id"] == "FRAME.DECOMPOSE.v0"
    assert result["authority"].startswith("DERIVED_WORKING_VIEW_ONLY")
    assert "snapshot_hash" in fibre
    assert len(fibre["snapshot_hash"]) == 64


def test_recursive_atom_calculus_surface_preserves_full_negative_and_stop_vocabularies():
    surface = atom_calculus_surface()
    assert len(surface["dispositions"]) == 10
    assert len(surface["recursion_stop_reasons"]) == 7
    assert len(surface["negative_history_categories"]) == 8
    assert surface["authority"].startswith("STUDY_CALCULUS_ONLY")


def test_saturation_surface_exposes_runtime_growth_and_multi_axis_development_flatness():
    surface = saturation_surface()
    assert "verified_closures" in surface["runtime_growth_coordinates"]
    assert "new_route_families" in surface["runtime_growth_coordinates"]
    assert "KNOWLEDGE" in surface["development_saturation_axes"]
    assert "SEARCH_UNIVERSE" in surface["development_saturation_axes"]
    assert "FORMULATION" in surface["development_saturation_axes"]
    assert "META_METHOD" in surface["development_saturation_axes"]
    assert surface["authority"].startswith("BOUNDED_FLATNESS_ONLY")

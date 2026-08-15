from orion.mechanics import (
    DimensionWaiver,
    MechanicCell,
    MechanicDimension,
    audit_recursive,
)


def _waive_all(cell_id: str, *, children=()):
    return MechanicCell(
        cell_id,
        "fixture mechanic",
        "known-answer fixture",
        child_mechanic_ids=children,
        waivers=tuple(
            DimensionWaiver(dimension, "fixture establishes this dimension out of band")
            for dimension in MechanicDimension
        ),
    )


def test_recursive_audit_can_be_mechanically_complete_for_frozen_fixture():
    cells = {
        "root": _waive_all("root", children=("child",)),
        "child": _waive_all("child"),
    }
    report = audit_recursive(cells, "root")
    assert report.bounded_ready
    assert not report.unknown_child_ids
    assert not report.cycle_paths


def test_recursive_audit_refuses_unknown_child_and_cycle():
    cells = {
        "a": _waive_all("a", children=("b",)),
        "b": _waive_all("b", children=("a", "missing")),
    }
    report = audit_recursive(cells, "a")
    assert not report.bounded_ready
    assert report.unknown_child_ids == ("missing",)
    assert report.cycle_paths


def test_recursive_audit_refuses_unknown_dependencies_and_dependency_cycles():
    cells = {
        "root": _waive_all("root", children=("a", "b")),
        "a": MechanicCell(
            "a",
            "fixture mechanic",
            "known-answer fixture",
            dependency_ids=("b", "missing-dependency"),
            waivers=tuple(
                DimensionWaiver(dimension, "fixture")
                for dimension in MechanicDimension
                if dimension is not MechanicDimension.DEPENDENCIES
            ),
        ),
        "b": MechanicCell(
            "b",
            "fixture mechanic",
            "known-answer fixture",
            dependency_ids=("a",),
            waivers=tuple(
                DimensionWaiver(dimension, "fixture")
                for dimension in MechanicDimension
                if dimension is not MechanicDimension.DEPENDENCIES
            ),
        ),
    }

    report = audit_recursive(cells, "root")

    assert not report.bounded_ready
    assert report.unknown_dependency_ids == ("missing-dependency",)
    assert report.dependency_cycle_paths == ("a -> b -> a",)


def test_recursive_audit_includes_dependencies_outside_child_containment():
    root = MechanicCell(
        "root",
        "fixture mechanic",
        "known-answer fixture",
        dependency_ids=("external",),
        waivers=tuple(
            DimensionWaiver(dimension, "fixture")
            for dimension in MechanicDimension
            if dimension is not MechanicDimension.DEPENDENCIES
        ),
    )
    external = MechanicCell(
        "external",
        "unresolved dependency",
        "dependency closure fixture",
        dependency_ids=("root",),
    )

    report = audit_recursive({"root": root, "external": external}, "root")

    assert {item.mechanic_id for item in report.reports} == {"root", "external"}
    assert report.dependency_cycle_paths == ("external -> root -> external",)
    assert not report.bounded_ready

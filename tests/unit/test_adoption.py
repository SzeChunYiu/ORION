from __future__ import annotations

import pathlib

from orion.adoption import (
    AdoptionState,
    declared_state,
    find_adoption_violations,
)

SOURCE_ROOT = pathlib.Path("src")


def test_no_v1_surface_has_adopted_a_v2_mechanism() -> None:
    """Issue #136 requires paper integrations to stay additive until separately
    execution-frozen. Adoption without that freeze is the failure this checks
    for, and it is silent by nature — an import is all it takes.
    """

    violations = find_adoption_violations(SOURCE_ROOT)
    assert not violations, [
        f"{item.importer} -> {item.imported}: {item.reason}" for item in violations
    ]


def test_the_v2_surfaces_declare_themselves() -> None:
    """Being unconsumed is the correct state for these modules, not a defect.

    An orphan audit run earlier in this session reported `staged_gate` as
    unwired when it was behaving exactly as its issue required. The boundary
    existed, but only as prose at the top of two of the three files, so nothing
    could read it. A declaration a tool can see is the difference between "no
    consumer yet" and "forgotten".
    """

    for relative in (
        "src/orion/self_orion/staged_gate.py",
        "src/orion/study/p1/licensing.py",
        "src/orion/study/p1/diagnosability.py",
    ):
        assert declared_state(pathlib.Path(relative)) is AdoptionState.V2_ADDITIVE, relative


def test_the_checker_catches_an_adoption_it_should_refuse(tmp_path) -> None:
    """Prove the alarm fires. A checker that has only ever returned zero on the
    real tree has not been shown to detect anything."""

    package = tmp_path / "orion" / "demo"
    package.mkdir(parents=True)
    (tmp_path / "orion" / "__init__.py").write_text("")
    (package / "__init__.py").write_text("")
    (package / "v2_thing.py").write_text('ADOPTION_BOUNDARY = "V2_ADDITIVE"\n')
    (package / "v1_thing.py").write_text(
        'ADOPTION_BOUNDARY = "V1_FROZEN"\n'
        "from orion.demo.v2_thing import something\n"
    )
    violations = find_adoption_violations(tmp_path)
    assert len(violations) == 1
    assert violations[0].importer == "orion.demo.v1_thing"
    assert violations[0].imported == "orion.demo.v2_thing"


def test_the_reverse_direction_is_allowed(tmp_path) -> None:
    """A V2 surface reading V1 is what building on a frozen base means. Only
    V1 importing V2 is adoption, so a symmetric check would refuse the normal
    case and get switched off."""

    package = tmp_path / "orion" / "demo"
    package.mkdir(parents=True)
    (tmp_path / "orion" / "__init__.py").write_text("")
    (package / "__init__.py").write_text("")
    (package / "v1_thing.py").write_text('ADOPTION_BOUNDARY = "V1_FROZEN"\n')
    (package / "v2_thing.py").write_text(
        'ADOPTION_BOUNDARY = "V2_ADDITIVE"\n'
        "from orion.demo.v1_thing import something\n"
    )
    assert find_adoption_violations(tmp_path) == ()


def test_undeclared_modules_are_not_errors() -> None:
    """Most of the repository declares nothing, and that is fine. A checker
    that demanded a declaration everywhere would fire on hundreds of correct
    files on its first run, which is how a checker gets disabled."""

    assert declared_state(pathlib.Path("src/orion/kernel/gate.py")) is AdoptionState.UNDECLARED

"""Activation remains withheld; live Phase-4 programme workflows are a defect."""

from __future__ import annotations

from pathlib import Path

from orion.programme.activation import (
    BLOCKING_DEPENDENCIES,
    PREPARATORY_STATUS,
    activation_authorized,
    activation_blockers,
    forbidden_phase4_runner_present,
    grants_phase4_closure,
    grants_self_sustaining_authority,
    live_phase4_programme_workflow_names,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
WORKFLOWS_DIR = REPO_ROOT / ".github" / "workflows"
TEMPLATE_DIR = REPO_ROOT / "research" / "phase-4-protocol" / "workflows"


def test_activation_is_hardwired_false() -> None:
    assert activation_authorized() is False
    assert grants_self_sustaining_authority() is False
    assert grants_phase4_closure() is False


def test_no_live_phase4_programme_workflows() -> None:
    assert live_phase4_programme_workflow_names(WORKFLOWS_DIR) == ()


def test_forbidden_runner_tree_is_absent() -> None:
    assert forbidden_phase4_runner_present(REPO_ROOT) is False


def test_relocated_templates_are_not_github_yaml() -> None:
    templates = sorted(TEMPLATE_DIR.glob("p4-*.yml.template"))
    assert [path.name for path in templates] == [
        "p4-anti-collapse.yml.template",
        "p4-epoch-manifest.yml.template",
        "p4-programme-cycle.yml.template",
    ]
    for path in templates:
        text = path.read_text(encoding="utf-8")
        assert PREPARATORY_STATUS in text
        assert "MUST NOT live under .github/workflows/" in text
        assert path.suffix == ".template"


def test_activation_blockers_name_the_open_dependencies() -> None:
    blockers = activation_blockers(workflows_dir=WORKFLOWS_DIR, repo_root=REPO_ROOT)
    for dependency in BLOCKING_DEPENDENCIES:
        assert f"blocked on {dependency}" in blockers
    assert "programme activation is withheld" in blockers
    assert not any(item.startswith("live Phase-4 programme workflow present:") for item in blockers)


def test_scanner_flags_a_live_yaml(tmp_path: Path) -> None:
    workflows = tmp_path / "workflows"
    workflows.mkdir()
    (workflows / "p4-programme-cycle.yml").write_text("name: live\n", encoding="utf-8")
    (workflows / "p4-programme-cycle.yml.template").write_text("name: inert\n", encoding="utf-8")
    assert live_phase4_programme_workflow_names(workflows) == ("p4-programme-cycle.yml",)

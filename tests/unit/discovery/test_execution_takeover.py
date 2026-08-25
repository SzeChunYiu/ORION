from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


def test_v3_workflow_installs_project_dependencies_before_hostile_suite() -> None:
    workflow = (ROOT / ".github/workflows/orion-discovery-v3.yml").read_text()

    install_at = workflow.find("python -m pip install -e .")
    hostile_at = workflow.find("python -m pytest -q tests/unit/discovery/test_frontier_dominance.py")

    assert install_at >= 0, "the V3 workflow must install ORION's declared dependencies"
    assert install_at < hostile_at, "project dependencies must be installed before test collection"

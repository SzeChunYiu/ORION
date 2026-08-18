from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "research" / "development" / "cannot_check_inventory.py"
INVENTORY_PATH = ROOT / "research" / "development" / "cannot_check_inventory.json"


def _load_module():
    spec = importlib.util.spec_from_file_location("cannot_check_inventory", MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_committed_inventory_matches_derived() -> None:
    module = _load_module()
    committed = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    assert committed["schema_version"] == module.SCHEMA_VERSION
    assert module.validate_inventory(committed) == []


def test_inventory_is_machine_readable_and_non_authorizing() -> None:
    committed = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    assert committed["grants_authority"] == "NONE"
    assert committed["closes_gate"] is None
    assert committed["total_sites"] == len(committed["sites"])
    assert committed["blocker_sites"] + committed["observing_sites"] == committed["total_sites"]


def test_every_inventory_site_has_a_stable_locator() -> None:
    committed = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    for site in committed["sites"]:
        assert site["file"]
        assert isinstance(site["lineno"], int) and site["lineno"] > 0
        assert site["kind"]
        assert site["role"] in {"EMITS", "OBSERVES"}
        assert site["context"]


def test_reason_extractor_filters_status_noise() -> None:
    """Bare terminal/status identifiers are not explanations.

    This guards the false-positive family found when the inventory initially counted
    declarations like `CANNOT_CHECK`, `REFUTED`, and `RED` as reasons for themselves.
    """

    module = _load_module()
    for token in (
        "CANNOT_CHECK",
        "REFUTED",
        "SUPPORTED",
        "GREEN",
        "RED",
        "UNKNOWN",
        "PASS",
        "FAIL",
        "MISSING",
    ):
        assert not module._is_reason(token), token


def test_domain_values_survive_the_filter() -> None:
    """No alarm, and the reason the first filter was too blunt.

    Rejecting every bare `SCREAMING_CASE` token threw away `CREDENTIALS_PRESENT` in
    `study/p5/causal_repair.py` -- a status value stating exactly why that site is
    `CANNOT_CHECK`, and one that was correctly driving its classification. Case does
    not separate a terminal name from a domain value; only the name does.
    """

    module = _load_module()
    for name in (
        "CREDENTIALS_PRESENT",
        "required_core_feature_unresolved",
        "no held-out root was declared to protect",
        "protected path does not exist in the checkout",
    ):
        assert module._is_reason(name), f"{name!r} states a cause and must be kept"


def test_the_precision_fix_lost_no_classification() -> None:
    """Filtering noise must not remove signal.

    Every classification in the inventory is driven by a genuine reason. The original
    precision-fix floor was 141 classified sites; P4 method-authority adds three new
    reviewed classified obligations (two custody, one declaration), ratcheting the
    exact frozen count to 144. Future authority additions must update this sentinel
    deliberately rather than weakening it to a lower-bound assertion.
    """

    committed = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    classified = {k: v for k, v in committed["classification"].items() if k != "UNCLASSIFIED"}
    assert sum(classified.values()) == 144, classified
    assert committed["with_reason"] < committed["blocker_sites"]
    assert committed["with_reason"] >= sum(classified.values()), (
        "more sites are classified than carry a reason, so something is classifying on nothing"
    )


def test_roles_are_derived_from_context_not_token_text() -> None:
    module = _load_module()
    source = """
def producer(x):
    if x:
        return \"CANNOT_CHECK\"
    state = \"CANNOT_CHECK\"
    return state

def observer():
    if decision == \"CANNOT_CHECK\":
        return False
"""
    sites = module.extract_sites(Path("transfer/example.py"), source)
    emits = [s for s in sites if s["role"] == "EMITS"]
    observes = [s for s in sites if s["role"] == "OBSERVES"]
    assert emits
    assert observes


def test_reason_classification_is_fail_closed() -> None:
    module = _load_module()
    assert module._classify_reason("provider not available") == "UNAVAILABLE_PROVIDER"
    assert module._classify_reason("missing evaluator custody") == "MISSING_CUSTODY"
    assert module._classify_reason("missing exact subject sha") == "MISSING_IDENTITY"
    assert module._classify_reason("not enough external evidence") == "INSUFFICIENT_EVIDENCE"
    assert module._classify_reason("something surprising") == "UNCLASSIFIED"


def test_unknown_file_is_not_silently_skipped(tmp_path: Path) -> None:
    module = _load_module()
    src = tmp_path / "src" / "orion"
    src.mkdir(parents=True)
    file = src / "sample.py"
    file.write_text('def f():\n    return "CANNOT_CHECK"\n', encoding="utf-8")
    sites = module.extract_tree(src)
    assert len(sites) == 1
    assert sites[0]["file"] == "sample.py"


def test_non_python_files_are_outside_this_inventory(tmp_path: Path) -> None:
    module = _load_module()
    src = tmp_path / "src" / "orion"
    src.mkdir(parents=True)
    (src / "a.md").write_text("CANNOT_CHECK", encoding="utf-8")
    assert module.extract_tree(src) == []


def test_nested_reason_is_associated_with_cannot_check() -> None:
    module = _load_module()
    source = """
def f():
    return {
        \"terminal\": \"CANNOT_CHECK\",
        \"reason\": \"protected path does not exist in the checkout\",
    }
"""
    sites = module.extract_sites(Path("transfer/example.py"), source)
    assert len(sites) == 1
    assert sites[0]["has_reason"] is True
    assert "protected path does not exist in the checkout" in sites[0]["reasons"]


def test_status_identifier_is_not_a_reason() -> None:
    module = _load_module()
    source = """
def f():
    status = \"CANNOT_CHECK\"
    return {\"terminal\": status, \"reason\": \"RED\"}
"""
    sites = module.extract_sites(Path("transfer/example.py"), source)
    assert len(sites) == 1
    assert sites[0]["has_reason"] is False


def test_inventory_schema_requires_no_extra_authority() -> None:
    committed = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    allowed = {
        "schema_version",
        "issue",
        "generated_at",
        "total_sites",
        "blocker_sites",
        "observing_sites",
        "with_reason",
        "classification",
        "sites",
        "grants_authority",
        "closes_gate",
    }
    assert set(committed) <= allowed


def test_inventory_generation_is_deterministic() -> None:
    module = _load_module()
    first = module.build_inventory(ROOT / "src" / "orion")
    second = module.build_inventory(ROOT / "src" / "orion")
    first.pop("generated_at", None)
    second.pop("generated_at", None)
    assert first == second


def test_committed_inventory_contains_no_obvious_secret_material() -> None:
    committed = INVENTORY_PATH.read_text(encoding="utf-8")
    for marker in ("OPENAI_API_KEY=", "ANTHROPIC_API_KEY=", "github_pat_", "sk-"):
        assert marker not in committed


@pytest.mark.parametrize("site", json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))["sites"])
def test_each_committed_inventory_site_is_still_present(site: dict[str, object]) -> None:
    """Each individual site is retained as a regression surface.

    The stronger aggregate equality test catches additions/removals; this parameterized
    test gives a precise failure location when a historical site disappears.
    """

    module = _load_module()
    current = module.extract_tree(ROOT / "src" / "orion")
    locator = (site["file"], site["lineno"], site["kind"], site["role"])
    current_locators = {
        (entry["file"], entry["lineno"], entry["kind"], entry["role"])
        for entry in current
    }
    assert locator in current_locators

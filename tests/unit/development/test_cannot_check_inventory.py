from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
INVENTORY_SCRIPT = ROOT / "research" / "development" / "cannot_check_inventory.py"
INVENTORY_PATH = ROOT / "research" / "development" / "cannot_check_inventory.json"

_spec = importlib.util.spec_from_file_location("cannot_check_inventory", INVENTORY_SCRIPT)
assert _spec is not None and _spec.loader is not None
module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(module)


def test_inventory_is_current() -> None:
    committed = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    generated = module.build_inventory(ROOT)
    assert committed == generated


def test_inventory_is_non_authorizing() -> None:
    inventory = module.build_inventory(ROOT)
    assert inventory["grants_authority"] == "NONE"
    assert inventory["closes_gate"] is None


def test_inventory_contains_emitting_and_observing_sites() -> None:
    inventory = module.build_inventory(ROOT)
    roles = {site["role"] for site in inventory["sites"]}
    assert "EMITS" in roles
    assert "OBSERVES" in roles
    assert inventory["blocker_sites"] > 0


def test_every_site_has_a_normalized_category() -> None:
    inventory = module.build_inventory(ROOT)
    categories = set(inventory["classification"])
    assert categories == {
        "MISSING_CUSTODY",
        "MISSING_IDENTITY",
        "MISSING_ACCESS",
        "UNAVAILABLE_PROVIDER",
        "INSUFFICIENT_EVIDENCE",
        "MISSING_DECLARATION",
        "UNCLASSIFIED",
    }
    assert sum(inventory["classification"].values()) == inventory["blocker_sites"]


def test_reason_fields_are_preserved_for_audit() -> None:
    inventory = module.build_inventory(ROOT)
    sites_with_reason = [site for site in inventory["sites"] if site["has_reason"]]
    assert sites_with_reason
    assert inventory["with_reason"] == len(sites_with_reason)
    for site in sites_with_reason:
        assert site["reasons"]


def test_false_positive_words_are_not_treated_as_reasons() -> None:
    for name in (
        "unresolved",
        "unavailable",
        "missing",
        "unknown",
        "blocked",
        "failure",
        "cannot_check",
    ):
        assert not module._is_reason(name), f"{name!r} is a status word, not an explanation"


@pytest.mark.parametrize(
    ("token", "expected"),
    [
        ("missing_required_declaration", "MISSING_DECLARATION"),
        ("provider_unavailable", "UNAVAILABLE_PROVIDER"),
        ("missing_identity", "MISSING_IDENTITY"),
        ("credential_access_missing", "MISSING_ACCESS"),
        ("protected_result_missing", "MISSING_CUSTODY"),
        ("evidence_insufficient", "INSUFFICIENT_EVIDENCE"),
    ],
)
def test_reason_classifier_maps_explicit_obligations(token: str, expected: str) -> None:
    assert module._category((token,)) == expected


def test_classifier_does_not_invent_missing_obligations() -> None:
    assert module._category(("unresolved",)) == "UNCLASSIFIED"
    assert module._category(("unknown",)) == "UNCLASSIFIED"


def test_ast_scan_does_not_double_count_observing_constants() -> None:
    inventory = module.build_inventory(ROOT)
    keys = [
        (site["file"], site["lineno"], site["role"], site["kind"], site["context"])
        for site in inventory["sites"]
    ]
    assert len(keys) == len(set(keys))


def test_inventory_is_repository_relative_and_stable() -> None:
    inventory = module.build_inventory(ROOT)
    for site in inventory["sites"]:
        assert not site["file"].startswith("/")
        assert "\\" not in site["file"]


def test_scan_ignores_generated_inventory_itself() -> None:
    inventory = module.build_inventory(ROOT)
    assert all(site["file"] != "research/development/cannot_check_inventory.json" for site in inventory["sites"])


def test_scan_ignores_python_cache_and_git_metadata() -> None:
    inventory = module.build_inventory(ROOT)
    for site in inventory["sites"]:
        assert "__pycache__" not in site["file"]
        assert not site["file"].startswith(".git/")


def test_observer_scan_recognizes_terminal_literals() -> None:
    assert module._looks_like_cannot_check_value("CANNOT_CHECK")
    assert module._looks_like_cannot_check_value("cannot-check")
    assert module._looks_like_cannot_check_value("cannot check")
    assert not module._looks_like_cannot_check_value("SUPPORTED")


def test_reason_detection_keeps_explicit_causal_tokens() -> None:
    for name in (
        "CREDENTIALS_PRESENT",
        "required_core_feature_unresolved",
        "no held-out root was declared to protect",
        "protected path does not exist in the checkout",
    ):
        assert module._is_reason(name), f"{name!r} states a cause and must be kept"


def test_the_precision_fix_lost_no_classification() -> None:
    """Filtering noise must not remove signal.

    Every classification in the inventory was driven by a genuine reason. The
    original precision-fix inventory contained 141 classified sites; P4 added
    three reviewed classified obligations, T8's prospective preflight added two
    identity-bound obligations, and the integrated science-first closure stack
    adds five reviewed classified obligations: two INSUFFICIENT_EVIDENCE and
    three MISSING_DECLARATION sites. The exact ratchet is therefore 151. Future
    additions must update this sentinel deliberately rather than weakening it to
    a lower-bound check.
    """

    committed = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    classified = {k: v for k, v in committed["classification"].items() if k != "UNCLASSIFIED"}
    assert sum(classified.values()) == 151, classified
    assert committed["with_reason"] < committed["blocker_sites"]
    assert committed["with_reason"] >= sum(classified.values()), (
        "more sites are classified than carry a reason, so something is classifying on nothing"
    )

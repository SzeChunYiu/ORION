"""The #322 `CANNOT_CHECK` inventory is derived, and its categories mean something.

The value of this inventory is entirely in whether it can be re-derived and whether
its classification distinguishes anything. A snapshot nobody can regenerate goes
stale silently, and a classifier that puts everything in one bucket reports a
checker that ran as a checker that worked.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "research" / "development" / "cannot_check_inventory.py"
INVENTORY_PATH = ROOT / "research" / "development" / "cannot_check_inventory.json"


def _load_module():
    spec = importlib.util.spec_from_file_location("cannot_check_inventory", MODULE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_committed_inventory_matches_derived() -> None:
    module = _load_module()
    committed = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    assert committed["schema_version"] == module.SCHEMA_VERSION
    assert module.validate_inventory(committed) == []


def test_inventory_grants_no_authority_and_closes_no_gate() -> None:
    committed = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    assert committed["grants_authority"] == "NONE"
    assert committed["closes_gate"] is None
    assert committed["issue"] == 322


def test_observing_sites_are_not_counted_as_blockers() -> None:
    """`if status is Status.CANNOT_CHECK:` has nothing to resolve.

    Counting consumers as blockers inflates the inventory with sites that can
    never come off it, which makes the remaining count meaningless as a measure
    of progress.
    """

    committed = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    blockers = [site for site in committed["sites"] if site["role"] == "EMITS"]
    observers = [site for site in committed["sites"] if site["role"] == "OBSERVES"]
    assert committed["blocker_sites"] == len(blockers)
    assert committed["observing_sites"] == len(observers)
    assert observers, "no observing sites found; the role split is not doing anything"
    assert all(site["category"] == "NOT_A_BLOCKER" for site in observers)
    assert sum(committed["classification"].values()) == len(blockers)


def test_unclassified_is_a_distinct_state_from_a_category() -> None:
    """`could not classify` must not be reported as `classified as other`."""

    module = _load_module()
    assert "OTHER" not in module.CATEGORIES
    assert "UNCLASSIFIED" in module.CATEGORIES
    committed = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    assert "OTHER" not in committed["classification"]
    assert "UNCLASSIFIED" in committed["classification"]


def test_classifier_separates_the_vocabulary() -> None:
    module = _load_module()
    assert module.classify(("external provider unavailable",), "") == "UNAVAILABLE_PROVIDER"
    assert module.classify(("protected evaluator custody absent",), "") == "MISSING_CUSTODY"
    assert module.classify(("subject_revision is UNBOUND",), "") == "MISSING_IDENTITY"
    assert module.classify(("corpus is unreachable over the network",), "") == "MISSING_ACCESS"
    assert module.classify(("no samples were executed",), "") == "INSUFFICIENT_EVIDENCE"
    # No-alarm control: a site with nothing to go on is UNCLASSIFIED, not
    # silently bucketed. Without this the classifier could pass by labelling
    # everything, which is the failure the previous draft actually had.
    assert module.classify((), "") == "UNCLASSIFIED"
    assert module.classify(("returned early",), "helper") == "UNCLASSIFIED"


def test_provider_outranks_identity_when_both_appear() -> None:
    """Rule order is a claim about causation, so it is pinned.

    A reason naming both an absent provider and an unbound identity is a provider
    problem: supplying the provider is what would produce the identity. Reversing
    these would send every blocked live campaign to MISSING_IDENTITY and hide the
    single action that unblocks them.
    """

    module = _load_module()
    both = ("provider credential absent so subject_revision stays UNBOUND",)
    assert module.classify(both, "") == "UNAVAILABLE_PROVIDER"

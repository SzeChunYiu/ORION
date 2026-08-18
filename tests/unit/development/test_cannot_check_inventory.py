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


def test_the_derived_obligation_comes_from_the_guard_not_a_pattern() -> None:
    """`missing_obligation` is read off an `is None` / falsiness guard.

    This is the one part of #322's box 2 -- "one earliest missing obligation" --
    that can be derived rather than guessed, so it must stay derived. A richer
    condition is deliberately not interpreted; guessing at it would put invented
    obligations next to real ones with nothing to tell them apart.
    """

    import ast

    module = _load_module()
    is_none = ast.parse("observation.hidden_label_exposed is None", mode="eval").body
    assert module._unmet_precondition(is_none) == "observation.hidden_label_exposed"
    falsy = ast.parse("not records", mode="eval").body
    assert module._unmet_precondition(falsy) == "records"
    # Not interpreted: a comparison that does not establish absence.
    richer = ast.parse("len(records) < 2", mode="eval").body
    assert module._unmet_precondition(richer) is None
    equality = ast.parse("status == 'PASS'", mode="eval").body
    assert module._unmet_precondition(equality) is None


def test_a_reason_that_places_the_site_beats_the_derived_obligation() -> None:
    """The obligation says *which* input is absent, not what kind of blocker it is.

    A guard on a protected-evaluator field is still a custody problem, so
    MISSING_DECLARATION is the fallback for sites the reason rules cannot place --
    never an override of a category they can.
    """

    committed = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    with_obligation = [s for s in committed["sites"] if s["missing_obligation"]]
    assert with_obligation, "no site carries a derived obligation; the derivation is inert"
    assert any(s["category"] != "MISSING_DECLARATION" for s in with_obligation), (
        "every obligation-carrying site is MISSING_DECLARATION; the reason rules are being overridden"
    )
    assert committed["with_derived_obligation"] == len(with_obligation)


def test_the_else_branch_does_not_inherit_the_guard() -> None:
    """The `else` body runs when the precondition *held*.

    Attributing the same missing input to it would be exactly backwards, and the
    resulting obligation would point at a field that was present.
    """

    module = _load_module()
    source = (
        "def f(x):\n"
        "    if x is None:\n"
        "        return 'CANNOT_CHECK'\n"
        "    else:\n"
        "        return 'CANNOT_CHECK'\n"
    )
    import ast

    tree = ast.parse(source)
    enclosing = module._enclosing(tree)
    preconditions = [
        enclosing[id(node)][2]
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant) and node.value == "CANNOT_CHECK"
    ]
    # The `if` body carries the guard; the `else` body carries none.
    assert sorted(preconditions, key=lambda v: (v is None, v or "")) == ["x", None]


def test_terminal_and_field_names_are_not_counted_as_reasons() -> None:
    """`with_reason` was inflated by 12 sites in the first published inventory.

    A site returning `{"status": "PASS"}` was recorded as carrying a reason when
    nothing there says why the check could not run, so the gap this inventory exists
    to measure read smaller than it is.
    """

    module = _load_module()
    for name in ("PASS", "FAIL", "status", "authority", "CANNOT_CHECK", "verdict", "ACCEPT"):
        assert not module._is_reason(name), f"{name!r} is a terminal or field name, not a cause"


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

    Every classification in the inventory was driven by a genuine reason, so tightening
    the extractor lowers `with_reason` without moving a single site between categories.
    If this ever fails, the filter has started eating causes.
    """

    committed = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    classified = {k: v for k, v in committed["classification"].items() if k != "UNCLASSIFIED"}
    assert sum(classified.values()) == 141, classified
    assert committed["with_reason"] < committed["blocker_sites"]
    assert committed["with_reason"] >= sum(classified.values()), (
        "more sites are classified than carry a reason, so something is classifying on nothing"
    )

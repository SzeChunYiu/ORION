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
    assert module.classify((), "") == "UNCLASSIFIED"
    assert module.classify(("returned early",), "helper") == "UNCLASSIFIED"


def test_provider_outranks_identity_when_both_appear() -> None:
    module = _load_module()
    both = ("provider credential absent so subject_revision stays UNBOUND",)
    assert module.classify(both, "") == "UNAVAILABLE_PROVIDER"


def test_the_derived_obligation_comes_from_the_guard_not_a_pattern() -> None:
    import ast

    module = _load_module()
    is_none = ast.parse("observation.hidden_label_exposed is None", mode="eval").body
    assert module._unmet_precondition(is_none) == "observation.hidden_label_exposed"
    falsy = ast.parse("not records", mode="eval").body
    assert module._unmet_precondition(falsy) == "records"
    richer = ast.parse("len(records) < 2", mode="eval").body
    assert module._unmet_precondition(richer) is None
    equality = ast.parse("status == 'PASS'", mode="eval").body
    assert module._unmet_precondition(equality) is None


def test_a_reason_that_places_the_site_beats_the_derived_obligation() -> None:
    committed = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    with_obligation = [s for s in committed["sites"] if s["missing_obligation"]]
    assert with_obligation, "no site carries a derived obligation; the derivation is inert"
    assert any(s["category"] != "MISSING_DECLARATION" for s in with_obligation), (
        "every obligation-carrying site is MISSING_DECLARATION; the reason rules are being overridden"
    )
    assert committed["with_derived_obligation"] == len(with_obligation)


def test_the_else_branch_does_not_inherit_the_guard() -> None:
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
    assert sorted(preconditions, key=lambda v: (v is None, v or "")) == ["x", None]


def test_terminal_and_field_names_are_not_counted_as_reasons() -> None:
    module = _load_module()
    for name in ("PASS", "FAIL", "status", "authority", "CANNOT_CHECK", "verdict", "ACCEPT"):
        assert not module._is_reason(name), f"{name!r} is a terminal or field name, not a cause"


def test_domain_values_survive_the_filter() -> None:
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

    Every classification in the inventory was driven by a genuine reason. The
    original precision-fix inventory contained 141 classified sites; P4 added
    three reviewed classified obligations, T8's prospective preflight added two
    identity-bound obligations, and the integrated science-first closure stack
    adds five reviewed classified obligations: two INSUFFICIENT_EVIDENCE and
    three MISSING_DECLARATION sites. The P1-P10 superiority adjudicator
    (``orion.programme.superiority``, issues #649-#663) adds four more reviewed
    obligations: three MISSING_DECLARATION sites where a gate's evidence, its
    artifact, or the independence of its reviewer is not recorded, and one
    INSUFFICIENT_EVIDENCE site where a terminal demanding a claim wider than the
    registered families has not yet been reached. The third MISSING_DECLARATION
    site arrived with ``INDEPENDENT_REVIEW``, added after PR #739 review found
    three review terminals unpassable via their own unblock path.

    The guard-exercise vocabulary (``orion.programme.guard_exercise``, issue
    #650) adds four more: three ``MISSING_DECLARATION`` sites where a guard's
    exercise denominator is absent --- once for a single-arm guard, once for a
    non-inferiority candidate, once for its comparator --- and one
    ``INSUFFICIENT_EVIDENCE`` site where *neither* arm was exercised, which is
    not a missing declaration but an absence of evidence on both sides. These
    are the inventory working as designed: each is a checker that now reports
    "no denominator" where the previous rate metric reported a pass.

    The same wave adds six more of the same character. P3's coordinate-necessity
    contrast (#651) adds one ``MISSING_DECLARATION`` where an ablation arm's
    treatment was never applied. P4's identifiability audit (#652) adds four ---
    two ``MISSING_DECLARATION`` where no probe is registered or no evaluation
    split exists, and two ``INSUFFICIENT_EVIDENCE`` where a probe could not be
    fitted or the audit's own evidence is too thin to license a verdict --- and
    its promotion-cue adapter adds one ``MISSING_CUSTODY`` for a case whose
    custody class declares no split. The exact ratchet is therefore 165. Future
    additions must update this sentinel deliberately rather than weakening it to
    a lower-bound check.
    """

    committed = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    classified = {k: v for k, v in committed["classification"].items() if k != "UNCLASSIFIED"}
    assert sum(classified.values()) == 165, classified
    assert committed["with_reason"] < committed["blocker_sites"]
    assert committed["with_reason"] >= sum(classified.values()), (
        "more sites are classified than carry a reason, so something is classifying on nothing"
    )

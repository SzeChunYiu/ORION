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
    custody class declares no split.

    P5's commitment-custody audit (``orion.programme.commitment_custody``, issue
    #653) adds six ``MISSING_CUSTODY`` sites, all in
    ``audit_commitment_custody``: the states in which a sealed secret's custody
    cannot be judged rather than judged safe --- no probe registered, no probe
    that computed anything, a canary that did not demonstrate the scheme, and
    the rest. They are ``MISSING_CUSTODY`` rather than
    ``MISSING_DECLARATION`` because what is absent is the protected material's
    custody itself, not a declaration about it.

    P7's decided-premise measure (``orion.programme.decided_premises``, issue
    #655) adds two ``MISSING_DECLARATION`` sites in
    ``measure_decision_constraint``: a premise whose deciding inputs the model
    does not carry, and one no enumerated case constrains. Both are
    ``CANNOT_CHECK`` rather than ``FAIL`` because a checker cannot be blamed for
    a distinction its state space cannot express. P6's and P8's mechanisms add
    none of their own --- they reach their blocked states through
    ``guard_exercise.assess_guard``, whose sites are already inventoried. The
    The construction-decided-verdict batch (P9, P10, P12, P14) adds six: four
    ``MISSING_CUSTODY`` in ``comparator_response.measure_contrast_margin``, where
    the comparator's own execution record is absent so no contrast can be taken;
    one ``MISSING_ACCESS`` in ``assess_attainable_margin`` for a margin whose
    reachable support cannot be read; and one ``MISSING_DECLARATION`` in
    ``TerminalReach.outcome`` for a terminal whose admissible worlds were never
    declared. All six report that a verdict could not be computed, which is the
    distinction this whole batch exists to make: a gate no world can clear is
    ``CANNOT_CHECK``, not a negative result. That put the exact ratchet at 179.

    The P3 coordinate-necessity build adds the 180th, a ``MISSING_IDENTITY`` in
    ``p3_coordinate_necessity_build`` emitted when the built atlas cannot be
    identified against its frozen declaration --- schema version, atlas id,
    freeze document and parent atlas among them. A build whose subject cannot be
    named has not produced a negative result about that subject; it has produced
    no result. (P4's identifiability audit moved within its module in the same
    batch, which changes a line number and not a count.)

    Three later batches take the ratchet from 180 to 195, and the inventory had
    gone stale against all three before this was noticed --- the generator is
    re-derivable precisely so that a drift like that is a test failure rather
    than something a reader has to spot.

    Eleven are ``MISSING_DECLARATION``. Eight sit in P3's partial-observation
    probe: one where the probe does not have the structure its freeze specifies,
    so it is not the world under study and no arm number is reported over it;
    and seven across ``evaluate_gates`` where a gate's own denominator is
    absent --- ``PROBE_DERIVATION`` produced no case, so the guard has no
    exercise at all; an over-resolution rate is ``None``; a held-out probe
    yields no rate; there are no intact failures to explain, or no
    over-resolutions to explain them against. Two more sit in P9's frontier
    grid, where a cell missing from an outcome file makes the whole grid
    ``CANNOT_CHECK`` and a fully executed grid whose crossing tests never had
    two uncensored frontiers is ``CANNOT_CHECK`` rather than ``PASS`` --- a
    crossing rate over an empty set is not a rate. The eleventh is P9's
    campaign runner refusing to report a verdict it did not compute.

    Four are ``MISSING_CUSTODY``, all in P9's hostile representation battery,
    and they are the same rule the battery states in prose: an attack that had
    no opportunity is ``CANNOT_CHECK``, never "the attack failed". A component
    whose comparator answered with a single label has no margin to be attacked,
    so there is nothing for the attack to have failed against.

    Every one of the fifteen reports that a verdict could not be computed, which
    is the distinction this whole batch exists to make. Future additions must
    update this sentinel deliberately rather than weakening it to a lower-bound
    check.

    P9's transfer audit takes the ratchet from 195 to 196 with a single
    ``MISSING_IDENTITY`` in ``OracleIdentity.outcome``. It is the right category
    and the right terminal: the D1 exact typed-relational comparator agrees with
    the evaluator gold on every point of three separate spaces --- the frozen 512,
    the protected 128, and 1,280 method pairs the D1 generator never builds ---
    because it is the evaluator's own classification read back through the same
    payload. That is an identity, so the failure branch it is supposed to grade
    cannot be reached, and the honest report is that the check could not be taken
    rather than that it failed. The same module's ``ViewCollapse.outcome`` is
    ``UNCLASSIFIED`` and so is not counted here.

    P3's partial-observation probe takes it 196 to 199 with three
    ``MISSING_DECLARATION`` sites, all of them a gate declining to read a zero it
    cannot use. ``G9_HARM_A3`` withholds a harm count of 0 three times over: on
    the three symmetric atlases because no intact pair has a one-sided absence
    for the arm to fire on, and on the harm corpus because that corpus's gold is
    derived by the very criterion the arm decides by, so the arm reproduces it on
    every case and its harm is 0 by arithmetic rather than by safety. A zero from
    a denominator of nothing and a zero from a tautology are both absent
    measurements, and the gate says so instead of reporting the arm as harmless.

    P9's reproduction check takes it 199 to 200 with one more
    ``MISSING_IDENTITY``, in ``ArmReproduction.outcome``. Re-running the frozen
    D1 protocol reproduces three of the four archived arms exactly and disagrees
    with the fourth --- ``TYPED_SERIALIZED_BAG``, same dataset digest and same
    selected configuration, 0.75 against the archived 0.5. That disagreement is
    not licensed to convict the archive, because the environment
    ``RESULT_EXECUTION_ENVIRONMENT_V1`` records is not the one measuring: Python
    3.12.13, numpy 2.5.2 and scipy 1.18.0 against 3.11.15, 2.4.6 and 1.17.1. Two
    things changed and only one was measured, so the identity of the environment
    is the blocker and the site names it. Under the recorded environment the same
    divergence would be ``FAIL``, and that branch is reachable and tested.

    Two ``INSUFFICIENT_EVIDENCE`` sites take it 200 to 202, and both are the
    same shape: an instrument that produced no evidence either way, saying so.
    P6's ``frame_conditions_are_load_bearing`` reports a condition whose
    countermodel search did not settle --- no countermodel found, and none shown
    not to exist --- rather than reporting it as an inert axiom, which is what a
    loaded machine used to make it publish. P9's ``OracleIndependence.outcome``
    reports a second comparator that turned out to be the first under another
    name: there was no verdict it could have returned other than the one it did.
    Both name their blocker in the returning statement so this inventory records
    an examined site rather than one carrying no extractable reason, and
    ``UNCLASSIFIED`` is unchanged at 385 across both.
    """

    committed = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    classified = {k: v for k, v in committed["classification"].items() if k != "UNCLASSIFIED"}
    assert sum(classified.values()) == 202, classified
    assert committed["with_reason"] < committed["blocker_sites"]
    assert committed["with_reason"] >= sum(classified.values()), (
        "more sites are classified than carry a reason, so something is classifying on nothing"
    )

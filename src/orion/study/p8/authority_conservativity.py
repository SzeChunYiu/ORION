"""P8's donor-conservativity count, and the guard that could not produce it.

All three claim-expansion checkers under ``research/claim_expansion/p8`` publish
``donor_conservativity_violations: 0`` for T1 --- "adding the scientific-discharge
layer never changes the donor-native verdict". Until this module's repair landed,
none of them had measured it. ``check_p8_x2_authority_lifting.py`` read::

    projected_native = native_valid
    if projected_native != native_valid:
        donor_conservativity_violations += 1

with ``_x3`` and ``_x4`` carrying the same two statements over ``native``.
``projected_native`` has exactly one binding in ``main()`` --- an assignment whose
value is the bare name it is then compared against --- and nothing rebinds either
operand between the assignment and the guard, so both operands load the same
object and the guard is ``x != x``: False for every bool. It was evaluated 18,432,
30,720 and 39,936 times respectively and satisfied 0 times, and it never called
``scientific_terminal`` at all, so its zero held for every possible input.

The same three files carried a second guard of the same kind for T9/T10, the
ideal decentralized-product tie::

    terminal = scientific_terminal(native, flags, narrowing, blocker, ...)
    ideal    = scientific_terminal(native, flags, narrowing, blocker, ...)
    if terminal != ideal:
        ideal_product_mismatches += 1

--- one deterministic call written twice on the same arguments. :func:`identity_guards`
finds both shapes, and it finds none in the repaired files.

What replaced them is what P6 and P7 already did to their twins: the checkers
carry ``project_to_donor``, ``native_verdict`` and the image of
``scientific_terminal`` along that projection, and T1 is the equality of that
image with the donor's own verdict over the donor-visible judgments. The two
sides are held apart by an AST independence gate; collapsed back into one
expression the counter reports ``CANNOT_CHECK`` rather than a clean zero.

:func:`donor_conservativity_capacity` is the evidence that the repair fires. It
runs each shipped checker end to end under
:func:`discharges_without_donor_authority` --- the shipped calculus with the
donor-native gate deleted, so a scientific target is discharged for a donor whose
own verdict is invalid, which is exactly what T1 forbids. That theory changes
nothing at ``native_valid=True``, so every assertion in each file still passes and
each script runs to completion; before the repair each still printed 0.
"""

from __future__ import annotations

import ast
import contextlib
import importlib.util
import io
import json
import sys
from functools import lru_cache
from pathlib import Path
from types import ModuleType
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[4]

X2_CHECKER = REPO_ROOT / "research/claim_expansion/p8/check_p8_x2_authority_lifting.py"
X3_CHECKER = REPO_ROOT / "research/claim_expansion/p8/check_p8_x3_authority_lifting.py"
X4_CHECKER = REPO_ROOT / "research/claim_expansion/p8/check_p8_x4_authority_lifting.py"

#: The three claim-expansion passes, by the label their schema uses.
CHECKERS: dict[str, Path] = {"X2": X2_CHECKER, "X3": X3_CHECKER, "X4": X4_CHECKER}

DONOR_CONSERVATIVITY_COUNT = "donor_conservativity_violations"
IDEAL_PRODUCT_COUNT = "ideal_product_mismatches"

#: The counts each file derives from its assertion blocks. They are the control's
#: other half: a theory that moves the conservativity count while leaving all of
#: these standing is one the rest of the artifact cannot see.
ASSERTION_COUNTS: tuple[str, ...] = (
    "type_separation_witnesses",
    "protected_coercion_successes",
    "unprotected_coercion_countermodels",
    "blocker_refuted_successes",
    "blocker_undetermined_cannot_check",
    "blocker_established_blocks",
    "single_support_revocation_survivals",
    "all_support_revoked_blocks",
)


def _load(path: Path, module_name: str) -> ModuleType:
    """Import a shipped checker by path without putting it on the import graph."""

    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def checker_module(label: str, suffix: str = "") -> ModuleType:
    """A fresh module object for one shipped checker.

    Fresh rather than cached, because every caller below substitutes something
    into it and a shared object would leak one measurement into the next.
    """

    return _load(CHECKERS[label], f"orion_p8_{label.lower()}_authority_lifting{suffix}")


def run_checker(module: ModuleType) -> dict[str, Any]:
    """Run a shipped checker's ``main()`` and parse the receipt it prints."""

    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        module.main()
    return json.loads(buffer.getvalue())


@lru_cache(maxsize=None)
def shipped_result(label: str) -> dict[str, Any]:
    """The receipt the unmutated checker publishes."""

    return run_checker(checker_module(label, "_shipped"))


def _adjacent_identical_calls(
    function: ast.FunctionDef, bindings: dict[str, int]
) -> set[frozenset[str]]:
    """Pairs of names bound by back-to-back assignments of the identical call.

    Adjacency is required and it is not decoration. ``x = f(a); y = f(a)`` with
    nothing between them is one deterministic call written twice, which is the
    shape all three P8 checkers used for their ideal-product tie. The same two
    calls with a statement between them is the ordinary before/after measurement
    around a mutation and is a real comparison, so it is not reported.
    """

    pairs: set[frozenset[str]] = set()
    for node in ast.walk(function):
        for field in ("body", "orelse", "finalbody"):
            block = getattr(node, field, None)
            if not isinstance(block, list):
                continue
            for first, second in zip(block, block[1:]):
                if not (isinstance(first, ast.Assign) and isinstance(second, ast.Assign)):
                    continue
                if not (
                    len(first.targets) == 1
                    and len(second.targets) == 1
                    and isinstance(first.targets[0], ast.Name)
                    and isinstance(second.targets[0], ast.Name)
                    and isinstance(first.value, ast.Call)
                    and isinstance(second.value, ast.Call)
                ):
                    continue
                left, right = first.targets[0].id, second.targets[0].id
                if bindings.get(left, 0) != 1 or bindings.get(right, 0) != 1:
                    continue
                if ast.dump(first.value) == ast.dump(second.value):
                    pairs.add(frozenset((left, right)))
    return pairs


def identity_guards(path: Path) -> tuple[str, ...]:
    """Guards in a shipped checker whose two operands cannot differ.

    Two shapes, because P8 shipped both. The first is P7's: a guard comparing
    ``x`` against a name ``x`` was just assigned from cannot fire, whatever the
    enumeration does around it, so its violation count is a property of the source
    rather than a measurement. The second is a guard comparing two names assigned
    from the *same call expression* --- ``terminal`` and ``ideal`` both bound to
    ``scientific_terminal`` on identical arguments. A deterministic function
    equals itself, so that guard is as dead as the first while looking like a
    comparison of two things.

    Both are decided from the AST rather than from a comment: an alias map over
    each function's single-target assignments, with call values keyed by their
    dumped tree so two syntactically identical calls compare equal.

    A name bound more than once in the function is not an alias, because a later
    binding can make the two operands differ --- ``x = y`` inside a loop that
    rebinds ``y`` is a real comparison and is not reported. That single-binding
    requirement is what the claim about the shipped guards rests on:
    ``projected_native`` had exactly one binding in ``main()`` and so did the name
    it was compared against, so nothing between them could pull them apart.
    """

    tree = ast.parse(path.read_text(encoding="utf-8"))
    found: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue
        bindings: dict[str, int] = {}
        for child in ast.walk(node):
            if isinstance(child, ast.Name) and isinstance(child.ctx, ast.Store):
                bindings[child.id] = bindings.get(child.id, 0) + 1
            elif isinstance(child, ast.arg):
                bindings[child.arg] = bindings.get(child.arg, 0) + 1
        aliases: dict[str, str] = {}
        for child in ast.walk(node):
            if (
                isinstance(child, ast.Assign)
                and len(child.targets) == 1
                and isinstance(child.targets[0], ast.Name)
                and isinstance(child.value, ast.Name)
            ):
                target = child.targets[0].id
                if bindings.get(target, 0) != 1 or bindings.get(child.value.id, 0) != 1:
                    continue
                aliases[target] = child.value.id
        twice_called = _adjacent_identical_calls(node, bindings)
        for child in ast.walk(node):
            if not isinstance(child, ast.If) or not isinstance(child.test, ast.Compare):
                continue
            test = child.test
            if len(test.ops) != 1 or not isinstance(test.ops[0], (ast.Eq, ast.NotEq)):
                continue
            left, right = test.left, test.comparators[0]
            if not isinstance(left, ast.Name) or not isinstance(right, ast.Name):
                continue
            same_name = aliases.get(left.id) == right.id or aliases.get(right.id) == left.id
            if same_name or frozenset((left.id, right.id)) in twice_called:
                found.add(f"{node.name}: {ast.unparse(test)}")
    return tuple(sorted(found))


# ---------------------------------------------------------------------------
# The registered false theory, and the theory held consistently
# ---------------------------------------------------------------------------
def discharges_without_donor_authority(
    native, flags, narrowing, blocker, support_a, support_b, coercion
):
    """The shipped calculus with the donor-native authority gate deleted.

    A scientific target is discharged on the scientific state alone, so a donor
    family whose own verdict is invalid acquires scientific authority it was never
    given --- the violation T1 names, in the direction no assertion in any of the
    three files can reach. It agrees with the shipped rule everywhere at
    ``native_valid=True``, which is why the shipped scripts run to completion on
    it, and why the pre-repair guard printed 0 for it.

    Written as a module-level ``def`` rather than a lambda because the checkers'
    ``_independently_defined`` gate reads the substituted rule's source: a rule
    whose source cannot be recovered makes the counters report ``CANNOT_CHECK``,
    which would hide the terminal this measurement is about.
    """

    if not narrowing:
        return "BLOCK"
    if blocker == "ESTABLISHED":
        return "BLOCK"
    if blocker == "UNDETERMINED":
        return "CANNOT_CHECK"
    if not (support_a or support_b):
        return "BLOCK"
    if not (all(flags) or coercion):
        return "BLOCK"
    return "DISCHARGE"


def _gates_without_native_authority(module: ModuleType) -> tuple[tuple[str, str], ...]:
    """The decentralized product's gates with the same native gate removed.

    Substituted alongside the rule so the false theory is held *consistently*
    across both sides of both counters. That is the sharp control: an
    inconsistently applied theory is caught by the ideal-product tie as well, so
    only under this one is the conservativity count the sole thing that moves.
    """

    return tuple(
        gate for gate in module.DECENTRALIZED_GATES if gate[0] != "native_authority"
    )


def _collapsed_image(donor_judgment):
    """``discharge_image_in_donor_language`` written as ``native_verdict`` again.

    The durability probe: this is what a later edit that "simplifies" the
    projection away would leave behind, and the checkers must report
    ``CANNOT_CHECK`` for it rather than the clean zero it would produce.
    """

    _donor, native_valid = donor_judgment
    return native_valid


def donor_conservativity_capacity(label: str) -> dict[str, Any]:
    """What one checker's repaired conservativity count rejects, and by what number.

    Reported rather than asserted, because a repaired guard that still rejects
    nothing is the defect it replaced. Four runs of the same shipped file:

    ``shipped``
        the unmutated checker, for the published value.
    ``theory_on_the_calculus_only``
        :func:`discharges_without_donor_authority` substituted for
        ``scientific_terminal``. Both counters move --- the ideal-product tie sees
        it too, because the decentralized product still holds the native gate.
    ``theory_held_consistently``
        the same theory substituted into the decentralized product as well. The
        product ties again, every assertion count is unchanged, and the
        conservativity count is the only quantity in the artifact that moves.
    ``collapsed``
        the image of the discharge relation replaced by the donor's own verdict,
        which must report ``CANNOT_CHECK`` rather than 0.
    """

    shipped = shipped_result(label)

    inconsistent = checker_module(label, "_theory_only")
    inconsistent.scientific_terminal = discharges_without_donor_authority
    on_calculus = run_checker(inconsistent)

    consistent = checker_module(label, "_theory_consistent")
    consistent.scientific_terminal = discharges_without_donor_authority
    consistent.DECENTRALIZED_GATES = _gates_without_native_authority(consistent)
    held_consistently = run_checker(consistent)

    collapsed_module = checker_module(label, "_collapsed")
    collapsed_module.discharge_image_in_donor_language = _collapsed_image
    collapsed = run_checker(collapsed_module)

    unchanged = tuple(
        sorted(key for key in ASSERTION_COUNTS if held_consistently[key] == shipped[key])
    )
    return {
        "checker": str(CHECKERS[label].relative_to(REPO_ROOT)),
        "guard": (
            "discharge_image_in_donor_language(project_to_donor(...)) != "
            "native_verdict(project_to_donor(...))"
        ),
        "identity_guards_remaining": identity_guards(CHECKERS[label]),
        "status": shipped["donor_conservativity_status"],
        "violations": shipped[DONOR_CONSERVATIVITY_COUNT],
        "donor_judgments": shipped["donor_conservativity_states"],
        "distinct_donor_judgments": shipped["donor_conservativity_distinct_states"],
        "assertion_coverage_status": shipped["assertion_coverage_status"],
        "assertion_covered_states_native_invalid": shipped[
            "assertion_covered_states_native_invalid"
        ],
        "refuting_theory": "discharges_without_donor_authority",
        "violations_under_the_theory": on_calculus[DONOR_CONSERVATIVITY_COUNT],
        "ideal_mismatches_under_the_theory": on_calculus[IDEAL_PRODUCT_COUNT],
        "violations_under_the_theory_held_consistently": held_consistently[
            DONOR_CONSERVATIVITY_COUNT
        ],
        "ideal_mismatches_under_the_theory_held_consistently": held_consistently[
            IDEAL_PRODUCT_COUNT
        ],
        "terminal_under_the_theory": held_consistently["terminal"],
        "assertion_counts_unchanged_under_the_theory": unchanged,
        "collapsed_status": collapsed["donor_conservativity_status"],
        "collapsed_violations": collapsed[DONOR_CONSERVATIVITY_COUNT],
        "collapsed_terminal": collapsed["terminal"],
        "reading": (
            f"the count compares the image of scientific_terminal along project_to_donor "
            f"against the donor's own verdict over {shipped['donor_conservativity_states']} "
            f"donor judgments with {shipped['donor_conservativity_distinct_states']} distinct "
            f"verdicts. Under discharges_without_donor_authority --- a scientific target "
            f"discharged for a donor whose own verdict is invalid, which the shipped script "
            f"used to run to completion on and report 0 for --- it reports "
            f"{held_consistently[DONOR_CONSERVATIVITY_COUNT]} violations and the checker's "
            f"terminal is {held_consistently['terminal']}, with the theory held consistently "
            f"so the ideal-product tie reports "
            f"{held_consistently[IDEAL_PRODUCT_COUNT]} and all "
            f"{len(unchanged)} of {len(ASSERTION_COUNTS)} assertion-derived counts unchanged. "
            f"Its zero is an observation"
        ),
    }


def conservativity_report() -> dict[str, Any]:
    """The capacity measurement for all three claim-expansion passes."""

    return {label: donor_conservativity_capacity(label) for label in CHECKERS}


__all__ = [
    "ASSERTION_COUNTS",
    "CHECKERS",
    "DONOR_CONSERVATIVITY_COUNT",
    "IDEAL_PRODUCT_COUNT",
    "REPO_ROOT",
    "X2_CHECKER",
    "X3_CHECKER",
    "X4_CHECKER",
    "checker_module",
    "conservativity_report",
    "discharges_without_donor_authority",
    "donor_conservativity_capacity",
    "identity_guards",
    "run_checker",
    "shipped_result",
]

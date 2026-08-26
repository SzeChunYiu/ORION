#!/usr/bin/env python3
"""Derive the inventory of every `CANNOT_CHECK` site in `src/orion` (issue #322).

Issue #322 needs a machine-readable inventory that can be *re-derived* after each
dependency changes, not a snapshot taken once. So this is a generator with a
committed output and a `--check` mode, following `research/publication/scoreboard.py`:
the artifact is derived, and drift between derived and committed is a test failure
rather than something a reader has to notice.

Five decisions are load-bearing.

**`UNCLASSIFIED` is not `OTHER`.** A site whose reason cannot be extracted has not
been classified as "none of the above" -- it has not been classified at all. An
earlier draft of this inventory put 197 of 199 sites in `OTHER` with the literal
placeholder `<call_with_CANNOT_CHECK>` as their reason, which reports a checker
that ran as a checker that worked. The two states are counted separately here, and
`unclassified` is the number that has to come down.

**Sites are classified from evidence, never from position.** The rules read the
reason text and the enclosing names. When none matches, the site is `UNCLASSIFIED`;
nothing is assigned a category because it happened to sit in a particular file.

**A definition of the vocabulary is not an emission.** `CANNOT_CHECK = "CANNOT_CHECK"`
inside an `Enum` is how the token exists at all; it is not a check that failed to
run. Such sites are `ENUM_MEMBER`, role `DEFINES`, category `NOT_A_BLOCKER`, counted
as `instrument_sites`. The v2 inventory never emitted `ENUM_MEMBER`: the kind was
keyed on the enclosing statement being the `ClassDef`, but a member's value node is
always wrapped in the `Assign` inside the class body, so all 117 member definitions
were mis-counted as blockers. The kind is now keyed on that `Assign` sitting
directly in an `Enum`-derived class body -- an assignment inside a *method* of such
a class is an ordinary emission, not a member definition.

**A ternary's taken branch owes what its `if` form owes.** `Verdict.CANNOT_CHECK if
frozen_round is None else ...` means the caller never supplied `frozen_round`, which
is a `MISSING_DECLARATION` exactly as the matching `if` form was always read. The
v2 guard reader only walked `ast.If`, so ternary sites silently carried no derived
obligation. In both forms only the taken branch inherits the guard; the `else` side
runs when the precondition held.

**A reason can live one statement away.** `missing.append("no declared scope")`
followed by `return Report(CANNOT_CHECK, tuple(missing))` is one idiom split across
statements; reading only the site statement records the second half as carrying no
reason at all. When a site statement carries no literal of its own, reasons are
also read from accumulation calls (`.append`/`.extend`/`.add`) earlier in the same
function, and a site classified that way says so with `method: "adjacent_literal"`.
Nothing else in the function is read -- docstrings, log lines and dict keys are not
causes -- and a site with no extractable literal anywhere in its function stays
`UNCLASSIFIED` rather than being forced into a category. A stated cause, whether
sibling or adjacent, outranks a derived obligation; `method` records which evidence
produced the category.
"""

from __future__ import annotations

import argparse
import ast
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE_ROOT = REPO_ROOT / "src" / "orion"
INVENTORY_PATH = Path(__file__).resolve().parent / "cannot_check_inventory.json"
SCHEMA_VERSION = "orion.cannot-check-inventory.v3"

#: Issue #322's blocker vocabulary, plus the explicit "could not classify" state.
CATEGORIES = (
    "MISSING_DECLARATION",
    "MISSING_IDENTITY",
    "MISSING_CUSTODY",
    "MISSING_ACCESS",
    "UNAVAILABLE_PROVIDER",
    "INSUFFICIENT_EVIDENCE",
    "UNCLASSIFIED",
)

#: Ordered (category, substrings) rules, first match wins. Ordering matters: a
#: reason naming both an absent provider and an unbound identity is a provider
#: problem, because supplying the provider is what would produce the identity.
CLASSIFICATION_RULES: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        "UNAVAILABLE_PROVIDER",
        ("provider", "api_key", "apikey", "credential", "entitlement", "model_unavailable", "llm"),
    ),
    (
        "MISSING_CUSTODY",
        ("custody", "protected", "evaluator", "holdout", "held_out", "heldout", "outside_the_answering_lane"),
    ),
    (
        "MISSING_ACCESS",
        ("access", "unreachable", "network", "paywall", "inaccessible", "not_found", "missing_file"),
    ),
    (
        "MISSING_IDENTITY",
        ("unbound", "identity", "revision", "hash", "fingerprint", "subject", "epoch", "not_declared", "undeclared"),
    ),
    (
        "INSUFFICIENT_EVIDENCE",
        (
            "insufficient",
            "no_evidence",
            "no evidence",
            "not_executed",
            "not executed",
            "were executed",
            "unexecuted",
            "not_run",
            "not run",
            "empty",
            "zero_",
            "no_samples",
            "no samples",
            "underpowered",
        ),
    ),
)
# Blocker codes in this repository are snake_case, but reasons also appear as
# prose in receipts and error strings. Both spellings are listed rather than
# normalising separators, which would make `zero_` match "zero " and pull in
# unrelated numeric text.


def _git(*args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(REPO_ROOT), *args], capture_output=True, text=True, check=True
    ).stdout.strip()


def _is_cannot_check(node: ast.AST) -> bool:
    """True for the string literal and for `SomeEnum.CANNOT_CHECK`."""

    if isinstance(node, ast.Constant) and node.value == "CANNOT_CHECK":
        return True
    return isinstance(node, ast.Attribute) and node.attr == "CANNOT_CHECK"


#: Statement kinds that *observe* an existing `CANNOT_CHECK` rather than produce
#: one. `if status is Status.CANNOT_CHECK:` is a consumer, not a blocker, and
#: counting it as one inflates the inventory with sites that have nothing to
#: resolve.
OBSERVING_KINDS = frozenset({"BRANCH"})

#: Statement kinds that *define* the `CANNOT_CHECK` vocabulary rather than emit a
#: verdict. An enum member definition is how the token exists; it is not a check
#: that failed to run, so it has nothing to resolve and is counted separately as
#: `instrument_sites` instead of inflating `blocker_sites`.
INSTRUMENT_KINDS = frozenset({"ENUM_MEMBER"})

#: Bases that make a `ClassDef` an enum for `ENUM_MEMBER` purposes.
_ENUM_BASE_NAMES = frozenset({"Enum", "IntEnum", "StrEnum", "Flag", "IntFlag"})


def _derives_from_enum(classdef: ast.ClassDef) -> bool:
    for base in classdef.bases:
        if isinstance(base, ast.Name) and base.id in _ENUM_BASE_NAMES:
            return True
        if isinstance(base, ast.Attribute) and base.attr in _ENUM_BASE_NAMES:
            return True
    return False


def _is_enum_member_definition(statement: ast.AST, node: ast.AST) -> bool:
    """True when `node` is the value being bound as the enum member itself.

    The enclosing statement of a member's value is always the `Assign` (or
    `AnnAssign`) inside the class body, never the `ClassDef`; keying `ENUM_MEMBER`
    on the `ClassDef` made the kind unreachable. The value must be the bound node
    itself and the target a bare name, so `x = Status.CANNOT_CHECK` elsewhere in
    the class body -- an alias at best -- and attribute/subscript assignments in
    methods are not member definitions.
    """

    if isinstance(statement, ast.Assign):
        return (
            len(statement.targets) == 1
            and isinstance(statement.targets[0], ast.Name)
            and statement.value is node
        )
    if isinstance(statement, ast.AnnAssign):
        return isinstance(statement.target, ast.Name) and statement.value is node
    return False


def _site_kind(statement: ast.AST, node: ast.AST, in_enum_body: bool) -> str:
    if in_enum_body and _is_enum_member_definition(statement, node):
        return "ENUM_MEMBER"
    if isinstance(statement, ast.Return):
        return "RETURN"
    if isinstance(statement, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
        return "ASSIGN"
    if isinstance(statement, ast.Raise):
        return "RAISE"
    if isinstance(statement, (ast.If, ast.While)):
        return "BRANCH"
    if isinstance(statement, ast.Expr):
        return "EXPRESSION"
    return "OTHER_STATEMENT"


#: Sibling literals that are terminal names, field names or enum members rather
#: than causes. Counting these as reasons inflated `with_reason` by 18 sites in the
#: first published inventory: a site returning `("status", "PASS")` was recorded as
#: carrying a reason when nothing there says why the check could not run. The gap
#: this inventory exists to measure is understated by exactly that much.
_NON_REASON_LITERALS = frozenset(
    {
        "accept",
        "authority",
        "authority_flags",
        "blocked",
        "cannot_check",
        "deny",
        "denied",
        "fail",
        "failed",
        "inconclusive",
        "pass",
        "passed",
        "pending",
        "promoted",
        "protocol_id",
        "reject",
        "rejected",
        "status",
        "verdict",
        "verified",
    }
)


def _is_reason(value: str) -> bool:
    """A reason says why; a bare terminal or field name does not.

    Rejection is by *name*, not by case. A first attempt also rejected every bare
    `SCREAMING_CASE` token as an enum member, which was too blunt: it threw away
    `CREDENTIALS_PRESENT` in `study/p5/causal_repair.py`, a status value that states
    exactly why that site is `CANNOT_CHECK` and that was correctly driving an
    `UNAVAILABLE_PROVIDER` classification. Case does not distinguish a terminal name
    from a domain value; only the name does.

    Everything not named is kept, including short snake_case blocker codes such as
    `required_core_feature_unresolved`, which are genuine causes.
    """

    stripped = value.strip()
    if len(stripped) <= 2:
        return False
    return stripped.lower() not in _NON_REASON_LITERALS


def _reason_strings(statement: ast.AST) -> tuple[str, ...]:
    """Every string literal in the statement that states a cause.

    A `CANNOT_CHECK` carrying a reason nearly always carries it as a sibling
    literal in the same statement -- a returned tuple, a call argument, an appended
    blocker code. Reading the statement rather than the single node is what makes
    the difference between a reason and a placeholder.

    Sibling literals that name a terminal or a field are filtered out by
    `_is_reason`; see the note on `_NON_REASON_LITERALS` for why that matters to the
    headline count.
    """

    found: list[str] = []
    for node in ast.walk(statement):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            value = node.value.strip()
            if value != "CANNOT_CHECK" and _is_reason(value):
                found.append(value)
    return tuple(dict.fromkeys(found))


#: Calls that accumulate reasons for the report a function later emits.
_ACCUMULATION_METHODS = frozenset({"append", "extend", "add"})


def _accumulation_reasons(function: ast.AST, site: ast.AST) -> tuple[str, ...]:
    """Reason literals the function accumulates before reaching the site.

    The idiom is one report split across statements: `missing.append("no declared
    scope")` lines ending in `return Report(CANNOT_CHECK, tuple(missing))`. The
    site statement carries no literal of its own, so the causes are read from
    accumulation calls earlier in the same function -- earlier, because an
    accumulate-then-emit idiom cannot have been fed by a later line. Only
    `.append`/`.extend`/`.add` arguments are read: a docstring, a log line or a
    dict key in the same function is not a cause, and reading it would attribute
    incidental prose to the site. Nested `def` and `class` bodies are skipped;
    their accumulations feed their own sites.
    """

    found: list[str] = []
    stack = list(ast.iter_child_nodes(function))
    while stack:
        node = stack.pop()
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr in _ACCUMULATION_METHODS
            and node.lineno < site.lineno
        ):
            found.extend(_reason_strings(node))
        stack.extend(ast.iter_child_nodes(node))
    return tuple(dict.fromkeys(found))


def classify(reasons: tuple[str, ...], context: str) -> str:
    """Classify from the reason text and enclosing names, or say so."""

    haystack = " ".join((*reasons, context)).lower()
    for category, needles in CLASSIFICATION_RULES:
        if any(needle in haystack for needle in needles):
            return category
    return "UNCLASSIFIED"


def _dotted(node: ast.AST) -> str | None:
    """`observation.hidden_label_exposed` for an attribute/name chain, else None."""

    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        base = _dotted(node.value)
        return f"{base}.{node.attr}" if base else None
    return None


def _unmet_precondition(test: ast.AST) -> str | None:
    """The input a guard found missing, when the guard says so structurally.

    `if observation.hidden_label_exposed is None:` does not mean the evidence was
    weak -- it means the caller never declared the field. That is a different
    blocker from missing evidence, and it is the one case where the *earliest
    missing obligation* #322 asks for can be derived rather than guessed: the
    obligation is to populate exactly this name.

    Only `is None` and bare falsiness on a name or attribute chain are read. A
    richer condition is not guessed at; it stays unclassified.
    """

    if isinstance(test, ast.Compare) and len(test.ops) == 1:
        if isinstance(test.ops[0], ast.Is) and len(test.comparators) == 1:
            comparator = test.comparators[0]
            if isinstance(comparator, ast.Constant) and comparator.value is None:
                return _dotted(test.left)
    if isinstance(test, ast.UnaryOp) and isinstance(test.op, ast.Not):
        return _dotted(test.operand)
    return None


def _enclosing(
    tree: ast.AST,
) -> dict[int, tuple[str, ast.AST, str | None, ast.FunctionDef | ast.AsyncFunctionDef | None, bool]]:
    """Map each node id to (qualified enclosing name, statement, unmet
    precondition, enclosing function, directly-inside-an-Enum-body).

    The precondition is derived from `if` tests *and* ternary (`IfExp`) tests:
    `Verdict.CANNOT_CHECK if frozen_round is None else ...` owes exactly the
    obligation the matching `if` form would. In both forms only the taken branch
    inherits the guard; the `else` side runs when the precondition held.

    `in_enum_body` is true only for nodes sitting directly in the body of an
    `Enum`-derived class -- not inside a method of one, and not inside a nested
    plain class -- which is what separates an enum member definition from an
    ordinary emission.
    """

    mapping: dict[
        int, tuple[str, ast.AST, str | None, ast.FunctionDef | ast.AsyncFunctionDef | None, bool]
    ] = {}

    def walk(
        node: ast.AST,
        prefix: str,
        statement: ast.AST | None,
        guard: str | None,
        function: ast.FunctionDef | ast.AsyncFunctionDef | None,
        in_enum_body: bool,
    ) -> None:
        name = prefix
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            name = f"{prefix}.{node.name}" if prefix else node.name
        current = node if isinstance(node, ast.stmt) else statement
        mapping[id(node)] = (name, current or node, guard, function, in_enum_body)
        child_function = function
        child_enum_body = in_enum_body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            child_function = node
            child_enum_body = False
        elif isinstance(node, ast.ClassDef):
            child_enum_body = _derives_from_enum(node)
        if isinstance(node, (ast.If, ast.IfExp)):
            # Only the taken branch inherits the guard. The `else` side runs when
            # the precondition held, so attributing the same missing input to it
            # would be exactly backwards. The same holds for the ternary form.
            body_guard = _unmet_precondition(node.test) or guard
            walk(node.test, name, current, guard, child_function, child_enum_body)
            body = node.body if isinstance(node.body, list) else [node.body]
            orelse = node.orelse if isinstance(node.orelse, list) else [node.orelse]
            for child in body:
                walk(child, name, current, body_guard, child_function, child_enum_body)
            for child in orelse:
                walk(child, name, current, guard, child_function, child_enum_body)
            return
        for child in ast.iter_child_nodes(node):
            walk(child, name, current, guard, child_function, child_enum_body)

    walk(tree, "", None, None, None, False)
    return mapping


def collect_sites(source_root: Path = SOURCE_ROOT) -> list[dict[str, object]]:
    sites: list[dict[str, object]] = []
    for path in sorted(source_root.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        enclosing = _enclosing(tree)
        for node in ast.walk(tree):
            if not _is_cannot_check(node):
                continue
            context, statement, precondition, function, in_enum_body = enclosing.get(
                id(node), ("", node, None, None, False)
            )
            reasons = _reason_strings(statement)
            kind = _site_kind(statement, node, in_enum_body)
            if kind in OBSERVING_KINDS:
                role = "OBSERVES"
            elif kind in INSTRUMENT_KINDS:
                role = "DEFINES"
            else:
                role = "EMITS"
            adjacent: tuple[str, ...] = ()
            method: str | None = None
            if role != "EMITS":
                category = "NOT_A_BLOCKER"
            else:
                # The reason rules win when they match. A derived obligation says
                # *which input* is absent; it does not say what kind of blocker it
                # is, and a guard on `protected_evaluator_id` is still a custody
                # problem. MISSING_DECLARATION is the fallback for sites the reason
                # rules cannot place -- there it is strictly better than
                # UNCLASSIFIED, because the guard names the obligation exactly.
                # Adjacent reasons are reason text found one statement away, so
                # they keep the same precedence over the derived obligation; the
                # `method` field records which evidence produced the category.
                category = classify(reasons, context)
                if category != "UNCLASSIFIED":
                    method = "statement_literal"
                else:
                    # Sibling text that fails to place the site is usually an id or
                    # title riding along in the same call (`case_id=...`), not a
                    # cause; it has had its chance, so the accumulated reasons are
                    # still worth reading when the site remains unplaced.
                    if function is not None:
                        adjacent = _accumulation_reasons(function, node)
                        if adjacent:
                            adjacent_category = classify(adjacent, context)
                            if adjacent_category != "UNCLASSIFIED":
                                category, method = adjacent_category, "adjacent_literal"
                    if category == "UNCLASSIFIED" and precondition is not None:
                        category, method = "MISSING_DECLARATION", "unmet_precondition"
            sites.append(
                {
                    "file": str(path.relative_to(source_root)),
                    "lineno": getattr(node, "lineno", 0),
                    "context": context,
                    "kind": kind,
                    "role": role,
                    "reasons": list(reasons),
                    "has_reason": bool(reasons),
                    "adjacent_reasons": list(adjacent),
                    "derived_reason": (
                        "; ".join(adjacent) if method == "adjacent_literal" else None
                    ),
                    "method": method,
                    "unmet_precondition": precondition,
                    "missing_obligation": (
                        # What the guard establishes, and no more. Some of these
                        # names are locals derived from I/O, so "the caller must
                        # declare it" would overclaim about who supplies it; the
                        # guard only proves it was absent here.
                        f"{precondition} must be present at this guard"
                        if precondition is not None
                        else None
                    ),
                    "category": category,
                }
            )
    sites.sort(key=lambda site: (site["file"], site["lineno"], site["context"]))
    return sites


def derive_inventory(source_root: Path = SOURCE_ROOT) -> dict[str, object]:
    sites = collect_sites(source_root)
    blockers = [site for site in sites if site["role"] == "EMITS"]
    observers = [site for site in sites if site["role"] == "OBSERVES"]
    defines = [site for site in sites if site["role"] == "DEFINES"]
    counts = {category: 0 for category in CATEGORIES}
    for site in blockers:
        counts[str(site["category"])] += 1
    methods: dict[str, int] = {}
    for site in blockers:
        key = str(site["method"]) if site["method"] else "none"
        methods[key] = methods.get(key, 0) + 1
    return {
        "schema_version": SCHEMA_VERSION,
        "issue": 322,
        "grants_authority": "NONE",
        "closes_gate": None,
        "source_root": str(source_root.relative_to(REPO_ROOT)),
        "total_sites": len(sites),
        "blocker_sites": len(blockers),
        "observing_sites": len(observers),
        "instrument_sites": len(defines),
        "with_reason": sum(1 for site in blockers if site["has_reason"]),
        "with_adjacent_reason": sum(1 for site in blockers if site["adjacent_reasons"]),
        "with_derived_obligation": sum(1 for site in blockers if site["missing_obligation"]),
        "unclassified_without_evidence": sum(
            1
            for site in blockers
            if site["category"] == "UNCLASSIFIED"
            and not site["reasons"]
            and not site["adjacent_reasons"]
            and not site["unmet_precondition"]
        ),
        "classification": counts,
        "classification_methods": methods,
        "unclassified_note": (
            "UNCLASSIFIED is the residue after three reads, in precedence order: the "
            "site's own statement literals, literals accumulated one statement away "
            "(`missing.append(...)`) earlier in the same function, and a structurally "
            "nameable guard (`x is None`, `not x`). A site here either carries reason "
            "text that matches no category needle -- a vocabulary gap, resolvable only "
            "by adding a reviewed needle -- or carries no extractable evidence at all "
            "(see `unclassified_without_evidence`); those are the candidates for "
            "source-level obligation declarations, which this instrument will not "
            "invent. Driving the count down is the work; reclassifying it to OTHER is not."
        ),
        "sites": sites,
    }


def _comparable(payload: dict[str, object]) -> dict[str, object]:
    """The parts that must match; `subject_commit`/`generated_at` are informational."""

    return {key: value for key, value in payload.items() if key not in {"subject_commit", "generated_at"}}


def validate_inventory(committed: dict[str, object], source_root: Path = SOURCE_ROOT) -> list[str]:
    derived = derive_inventory(source_root)
    if _comparable(committed) == _comparable(derived):
        return []
    errors: list[str] = []
    if committed.get("total_sites") != derived["total_sites"]:
        errors.append(
            f"total_sites: committed {committed.get('total_sites')} != derived {derived['total_sites']}"
        )
    if committed.get("classification") != derived["classification"]:
        errors.append(
            f"classification: committed {committed.get('classification')} != derived {derived['classification']}"
        )
    committed_keys = {(s["file"], s["lineno"]) for s in committed.get("sites", [])}  # type: ignore[union-attr]
    derived_keys = {(s["file"], s["lineno"]) for s in derived["sites"]}  # type: ignore[index]
    for missing in sorted(derived_keys - committed_keys)[:10]:
        errors.append(f"site absent from committed inventory: {missing[0]}:{missing[1]}")
    for extra in sorted(committed_keys - derived_keys)[:10]:
        errors.append(f"committed site no longer exists: {extra[0]}:{extra[1]}")
    if not errors:
        errors.append("inventories differ in site detail; regenerate with --write")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="regenerate the committed inventory")
    parser.add_argument("--check", action="store_true", help="fail if committed differs from derived")
    args = parser.parse_args()

    if args.write:
        payload = derive_inventory()
        payload["subject_commit"] = _git("rev-parse", "HEAD")
        INVENTORY_PATH.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"wrote {INVENTORY_PATH.relative_to(REPO_ROOT)}: {payload['total_sites']} sites")
        print(json.dumps(payload["classification"], indent=2, sort_keys=True))
        return 0

    if args.check:
        errors = validate_inventory(json.loads(INVENTORY_PATH.read_text(encoding="utf-8")))
        for error in errors:
            print(error, file=sys.stderr)
        return 1 if errors else 0

    print(json.dumps(derive_inventory(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""A small LCF-style proof kernel for the papers' mechanized cores.

``P6-U-T1`` asks for kernel mechanization, not solver luck. The discipline here
is the standard one: :class:`Thm` can only be constructed by the rule functions
in this module, every rule re-validates its inputs from the term structure up,
and a proof is a serializable list of rule applications that a replay pass
re-checks from nothing. The trusted computing base is this file --- ORION
authored, not Lean --- and the artifacts that use it say so.

Terms are many-sorted with equality; formulas are ``Bool``-sorted terms. Sorts
and symbols come from a :class:`Signature` the caller declares, so the kernel
never knows which paper is using it.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

BOOL = "Bool"


class KernelError(Exception):
    """A rule was misapplied. Nothing is minted when this fires."""


@dataclass(frozen=True)
class Signature:
    """Declares the sorts and function symbols proofs may mention."""

    sorts: tuple[str, ...]
    functions: dict[str, tuple[tuple[str, ...], str]]

    def check_function(self, name: str, arg_sorts: tuple[str, ...]) -> str:
        try:
            domain, result = self.functions[name]
        except KeyError as error:
            raise KernelError(f"undeclared function {name}") from error
        if domain != arg_sorts:
            raise KernelError(
                f"{name} expects {domain}, got {arg_sorts}"
            )
        return result

    def has_sort(self, sort: str) -> bool:
        return sort in self.sorts


@dataclass(frozen=True)
class Term:
    """Variables and applications. Formulas are ``Bool``-sorted terms."""

    sort: str
    kind: str  # "var" | "app"
    name: str
    args: tuple["Term", ...] = ()

    def free_vars(self) -> frozenset[str]:
        if self.kind == "var":
            return frozenset({self.name})
        out: set[str] = set()
        for arg in self.args:
            out |= set(arg.free_vars())
        return frozenset(out)

    def render(self) -> str:
        if self.kind == "var":
            return self.name
        inner = ", ".join(arg.render() for arg in self.args)
        return f"{self.name}({inner})"

    # -- convenience constructors, sort-checked against nothing by themselves
    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, Term)
            and self.sort == other.sort
            and self.kind == other.kind
            and self.name == other.name
            and self.args == other.args
        )

    def __hash__(self) -> int:
        return hash((self.sort, self.kind, self.name, self.args))


def Var(name: str, sort: str) -> Term:  # noqa: N802 - term-language style
    return Term(sort, "var", name)


def App(name: str, *args: Term, result: str) -> Term:  # noqa: N802
    return Term(result, "app", name, tuple(args))


# -- connectives are ordinary Bool-sorted function symbols on fixed arities ----

CONNECTIVES = {
    "and": ((BOOL, BOOL), BOOL),
    "or": ((BOOL, BOOL), BOOL),
    "implies": ((BOOL, BOOL), BOOL),
    "not": ((BOOL,), BOOL),
    "equals": None,  # per-sort: eq_<sort>, declared by the caller
}


def eq(sort: str, a: Term, b: Term) -> Term:
    if a.sort != sort or b.sort != sort:
        raise KernelError("equality needs one sort on both sides")
    return App(f"eq_{sort}", a, b, result=BOOL)


def Imp(a: Term, b: Term) -> Term:  # noqa: N802
    return App("implies", a, b, result=BOOL)


def And(a: Term, b: Term) -> Term:  # noqa: N802
    return App("and", a, b, result=BOOL)


def Or(a: Term, b: Term) -> Term:  # noqa: N802
    return App("or", a, b, result=BOOL)


def Not(a: Term) -> Term:  # noqa: N802
    return App("not", a, result=BOOL)


def ForAll(var: Term | tuple[Term, ...] | list[Term], body: Term) -> Term:  # noqa: N802
    """Bind one variable, or fold a sequence into right-nested quantifiers."""

    if isinstance(var, (tuple, list)):
        if not var:
            raise KernelError("empty quantifier prefix")
        for item in var:  # nested right, so instantiation peels left-first
            if item.kind != "var":
                raise KernelError("quantifiers bind variables")
        out = body
        for item in reversed(var):
            out = ForAll(item, out)
        return out
    if body.sort != BOOL:
        raise KernelError("quantifiers bind Bool-sorted bodies")
    return _Quantified(
        sort=BOOL, kind="app", name=f"forall_{var.sort}", args=(body,),
        binder="forall", bound=var,
    )


@dataclass(frozen=True)
class _Quantified(Term):
    binder: str = "forall"
    bound: Term | None = None

    def free_vars(self) -> frozenset[str]:
        assert self.bound is not None and self.args
        return self.args[0].free_vars() - {self.bound.name}

    def render(self) -> str:
        assert self.bound is not None and self.args
        binder = f"forall {self.bound.name}:{self.bound.sort}"
        return f"{binder}. {self.args[0].render()}"

    def instantiate(self, witness: Term) -> Term:
        """Capture-avoiding substitution of the bound variable."""
        assert self.bound is not None
        if witness.sort != self.bound.sort:
            raise KernelError("instantiation sort mismatch")
        return _substitute(self.args[0], {self.bound.name: witness})


def _substitute(term: Term, mapping: dict[str, Term]) -> Term:
    """Capture-avoiding: quantified subterms rebind their variable first."""

    if isinstance(term, _Quantified):
        assert term.bound is not None
        inner = mapping.get(term.bound.name)
        renamed = dict(mapping)
        body = term.args[0]
        if inner is not None and term.bound.name in body.free_vars():
            fresh = _fresh_name(term.bound.name, body, mapping.values())
            body = _substitute(body, {term.bound.name: Var(fresh, term.bound.sort)})
            renamed.pop(term.bound.name, None)
            renamed[fresh] = inner
            return _Quantified(
                sort=term.sort, kind=term.kind, name=term.name,
                args=(_substitute(body, renamed),),
                binder=term.binder, bound=Var(fresh, term.bound.sort),
            )
        renamed.pop(term.bound.name, None)
        return _Quantified(
            sort=term.sort, kind=term.kind, name=term.name,
            args=(_substitute(body, renamed),),
            binder=term.binder, bound=term.bound,
        )
    if term.kind == "var":
        return mapping.get(term.name, term)
    return Term(
        term.sort, term.kind, term.name,
        tuple(_substitute(arg, mapping) for arg in term.args),
    )


def _fresh_name(base: str, body: Term, taken: Any) -> str:
    avoid = set(body.free_vars())
    avoid |= {t.name for t in taken if isinstance(t, Term) and t.kind == "var"}
    index = 0
    candidate = f"{base}'"
    while candidate in avoid:
        index += 1
        candidate = f"{base}'{index}"
    return candidate


# -- serialization -------------------------------------------------------------


def term_to_json(term: Term) -> dict[str, object]:
    if isinstance(term, _Quantified):
        assert term.bound is not None
        return {
            "sort": term.sort,
            "kind": "quant",
            "name": term.name,
            "binder": term.binder,
            "bound": {"name": term.bound.name, "sort": term.bound.sort},
            "body": term_to_json(term.args[0]),
        }
    return {
        "sort": term.sort,
        "kind": term.kind,
        "name": term.name,
        "args": [term_to_json(arg) for arg in term.args],
    }


def term_from_json(data: dict[str, object]) -> Term:
    kind = str(data["kind"])
    sort = str(data["sort"])
    if kind == "quant":
        bound = data["bound"]
        assert isinstance(bound, dict)
        body = term_from_json(data["body"])  # type: ignore[arg-type]
        var = Var(str(bound["name"]), str(bound["sort"]))
        return _Quantified(
            sort=sort, kind="app", name=str(data["name"]), args=(body,),
            binder=str(data["binder"]), bound=var,
        )
    args = tuple(term_from_json(arg) for arg in data["args"])  # type: ignore[union-attr]
    return Term(sort, kind, str(data["name"]), args)


# -- the kernel ----------------------------------------------------------------


@dataclass(frozen=True)
class Thm:
    """A proved formula under a set of undischarged hypotheses.

    Constructed only by :class:`Kernel`; the ``step`` field points into the
    kernel's append-only log so a serialized proof can name its own inputs.
    """

    concl: Term
    hyps: frozenset[Term]
    step: int


@dataclass(frozen=True)
class _Step:
    rule: str
    concl: Term
    hyps: frozenset[Term]
    inputs: tuple[int, ...]
    payload: tuple[Term, ...]


class Kernel:
    """The only source of :class:`Thm`. Every method re-validates its inputs."""

    def __init__(self, signature: Signature) -> None:
        self.signature = signature
        self._log: list[_Step] = []
        self._frozen = False

    # -- infrastructure
    def _record(self, rule: str, concl: Term, hyps: frozenset[Term],
                inputs: tuple[int, ...], payload: tuple[Term, ...]) -> Thm:
        if self._frozen:
            raise KernelError("kernel frozen for replay; no new steps")
        self._log.append(_Step(rule, concl, frozenset(hyps), inputs, payload))
        return Thm(concl, frozenset(hyps), len(self._log) - 1)

    def _check(self, thm: Thm) -> None:
        if not (0 <= thm.step < len(self._log)):
            raise KernelError("theorem handle from another kernel")
        step = self._log[thm.step]
        if step.concl != thm.concl or step.hyps != thm.hyps:
            raise KernelError("theorem handle does not match its log entry")

    @staticmethod
    def _bool(term: Term) -> None:
        if term.sort != BOOL:
            raise KernelError(f"expected a formula, got {term.sort}-sorted term")

    def _checked_function(self, name: str, args: tuple[Term, ...]) -> str:
        return self.signature.check_function(name, tuple(a.sort for a in args))

    # -- rules
    def assume(self, formula: Term) -> Thm:
        self._bool(formula)
        return self._record("assume", formula, frozenset({formula}), (), (formula,))

    def refl(self, term: Term) -> Thm:
        if not self.signature.has_sort(term.sort):
            raise KernelError(f"unknown sort {term.sort}")
        return self._record("refl", eq(term.sort, term, term), frozenset(), (), (term,))

    def symm(self, thm: Thm) -> Thm:
        self._check(thm)
        if thm.concl.kind != "app" or not thm.concl.name.startswith("eq_"):
            raise KernelError("symm needs an equality")
        left, right = thm.concl.args
        return self._record("symm", eq(thm.concl.args[0].sort, right, left),
                            thm.hyps, (thm.step,), ())

    def trans(self, first: Thm, second: Thm) -> Thm:
        for thm in (first, second):
            self._check(thm)
        if first.concl.kind != "app" or not first.concl.name.startswith("eq_"):
            raise KernelError("trans needs equalities")
        if first.concl.name != second.concl.name:
            raise KernelError("trans across sorts")
        mid_l, mid_r = first.concl.args
        if mid_r != second.concl.args[0]:
            raise KernelError("trans middle terms differ")
        sort = mid_l.sort
        return self._record(
            "trans", eq(sort, mid_l, second.concl.args[1]),
            first.hyps | second.hyps, (first.step, second.step), ())

    def congr(self, function: str, left: tuple[Term, ...],
              right: tuple[Term, ...], equalities: tuple[Thm, ...]) -> Thm:
        if len(left) != len(right) or len(equalities) != len(left):
            raise KernelError("congr arity mismatch")
        result = self.signature.check_function(
            function, tuple(a.sort for a in left))
        self.signature.check_function(
            function, tuple(a.sort for a in right))
        for term in left + right:
            if not self.signature.has_sort(term.sort):
                raise KernelError(f"unknown sort {term.sort}")
        for term, thm in zip(left, equalities):
            self._check(thm)
            if thm.concl.kind != "app" or thm.concl.name != f"eq_{term.sort}":
                raise KernelError("congr needs pointwise equalities")
            if thm.concl.args != (term, right[left.index(term)]):
                raise KernelError("congr equality does not align with arguments")
        hyps: frozenset[Term] = frozenset()
        for thm in equalities:
            hyps |= thm.hyps
        built_left = App(function, *left, result=result)
        built_right = App(function, *right, result=result)
        return self._record("congr", eq(result, built_left, built_right), hyps,
                            tuple(thm.step for thm in equalities),
                            (built_left, built_right))

    def eq_mp(self, equality: Thm, truth: Thm) -> Thm:
        self._check(equality)
        self._check(truth)
        if equality.concl.name != f"eq_{BOOL}" or equality.concl.kind != "app":
            raise KernelError("eq_mp needs a Bool equality")
        left, right = equality.concl.args
        if truth.concl != left:
            raise KernelError("eq_mp truth does not match equality's left side")
        return self._record("eq_mp", right, equality.hyps | truth.hyps,
                            (equality.step, truth.step), ())

    def mp(self, implication: Thm, truth: Thm) -> Thm:
        self._check(implication)
        self._check(truth)
        if implication.concl.kind != "app" or implication.concl.name != "implies":
            raise KernelError("mp needs an implication")
        left, right = implication.concl.args
        if truth.concl != left:
            raise KernelError("mp truth does not match the implication's premise")
        return self._record("mp", right, implication.hyps | truth.hyps,
                            (implication.step, truth.step), ())

    def impl_intro(self, premise: Term, thm: Thm) -> Thm:
        self._bool(premise)
        self._check(thm)
        if premise not in thm.hyps:
            raise KernelError("impl_intro premise is not an undischarged hypothesis")
        return self._record("impl_intro", Imp(premise, thm.concl),
                            thm.hyps - {premise}, (thm.step,), (premise,))

    def and_intro(self, left: Thm, right: Thm) -> Thm:
        self._check(left)
        self._check(right)
        self._bool(left.concl)
        self._bool(right.concl)
        return self._record("and_intro", And(left.concl, right.concl),
                            left.hyps | right.hyps, (left.step, right.step), ())

    def and_left(self, thm: Thm) -> Thm:
        self._check(thm)
        if thm.concl.kind != "app" or thm.concl.name != "and":
            raise KernelError("and_left needs a conjunction")
        return self._record("and_left", thm.concl.args[0], thm.hyps, (thm.step,), ())

    def and_right(self, thm: Thm) -> Thm:
        self._check(thm)
        if thm.concl.kind != "app" or thm.concl.name != "and":
            raise KernelError("and_right needs a conjunction")
        return self._record("and_right", thm.concl.args[1], thm.hyps, (thm.step,), ())

    def or_intro_l(self, disjunct: Term, thm: Thm) -> Thm:
        self._bool(disjunct)
        self._check(thm)
        self._bool(thm.concl)
        return self._record("or_intro_l", Or(disjunct, thm.concl), thm.hyps,
                            (thm.step,), (disjunct,))

    def or_intro_r(self, thm: Thm, disjunct: Term) -> Thm:
        self._check(thm)
        self._bool(thm.concl)
        self._bool(disjunct)
        return self._record("or_intro_r", Or(thm.concl, disjunct), thm.hyps,
                            (thm.step,), (disjunct,))

    def or_elim(self, disjunction: Thm, left: Thm, right: Thm) -> Thm:
        for thm in (disjunction, left, right):
            self._check(thm)
        if disjunction.concl.kind != "app" or disjunction.concl.name != "or":
            raise KernelError("or_elim needs a disjunction")
        left_dis, right_dis = disjunction.concl.args
        if left.concl.kind != "app" or left.concl.name != "implies":
            raise KernelError("or_elim left case must be an implication")
        if right.concl.kind != "app" or right.concl.name != "implies":
            raise KernelError("or_elim right case must be an implication")
        if left.concl.args[0] != left_dis or right.concl.args[0] != right_dis:
            raise KernelError("or_elim cases do not match the disjuncts")
        if left.concl.args[1] != right.concl.args[1]:
            raise KernelError("or_elim cases conclude different formulas")
        concl = left.concl.args[1]
        base = disjunction.hyps
        hyps = frozenset(base | (left.hyps - {left_dis}) | (right.hyps - {right_dis}))
        return self._record("or_elim", concl, hyps,
                            (disjunction.step, left.step, right.step), ())

    def forall_inst(self, quantified: Thm, witness: Term) -> Thm:
        self._check(quantified)
        if not isinstance(quantified.concl, _Quantified):
            raise KernelError("forall_inst needs a quantified formula")
        instance = quantified.concl.instantiate(witness)
        return self._record("forall_inst", instance, quantified.hyps,
                            (quantified.step,), (witness,))

    def forall_intro(self, var: Term, thm: Thm) -> Thm:
        self._check(thm)
        if var.kind != "var" or not self.signature.has_sort(var.sort):
            raise KernelError("forall_intro needs a declared variable")
        for hyp in thm.hyps:
            if var.name in hyp.free_vars():
                raise KernelError("forall_intro variable is free in a hypothesis")
        if var.name not in thm.concl.free_vars():
            raise KernelError("forall_intro variable not free in the conclusion")
        return self._record(
            "forall_intro", ForAll(var, thm.concl), thm.hyps, (thm.step,), (var,))

    def absurd(self, truth: Thm, negation: Thm, target: Term) -> Thm:
        self._check(truth)
        self._check(negation)
        self._bool(target)
        if negation.concl.kind != "app" or negation.concl.name != "not":
            raise KernelError("absurd needs a negation")
        if negation.concl.args[0] != truth.concl:
            raise KernelError("absurd truth and negation do not match")
        return self._record("absurd", target, truth.hyps | negation.hyps,
                            (truth.step, negation.step), (target,))

    def bool_cases(self, guard: Term, left: Thm, right: Thm) -> Thm:
        """Classical case split on a Bool-sorted term.

        ``left`` proves ``guard -> C`` and ``right`` proves ``not(guard) -> C``
        under hypotheses that must agree outside ``guard`` / ``not(guard)``.
        """
        self._bool(guard)
        for thm in (left, right):
            self._check(thm)
        if left.concl.kind != "app" or left.concl.name != "implies" \
                or left.concl.args[0] != guard:
            raise KernelError("bool_cases left case must be guard -> C")
        if right.concl.kind != "app" or right.concl.name != "implies" \
                or right.concl.args[0] != Not(guard):
            raise KernelError("bool_cases right case must be not(guard) -> C")
        if left.concl.args[1] != right.concl.args[1]:
            raise KernelError("bool_cases cases conclude different formulas")
        hyps = frozenset((left.hyps - {guard}) | (right.hyps - {Not(guard)}))
        return self._record("bool_cases", left.concl.args[1], hyps,
                            (left.step, right.step), (guard,))

    # -- export / replay
    def steps_as_json(self) -> list[dict[str, object]]:
        return [
            {
                "id": index,
                "rule": step.rule,
                "concl": term_to_json(step.concl),
                "hyps": [term_to_json(h) for h in sorted(step.hyps, key=term_to_json_str)],
                "inputs": list(step.inputs),
                "payload": [term_to_json(term) for term in step.payload],
            }
            for index, step in enumerate(self._log)
        ]

    def replay(self, log: list[dict[str, object]], expected: Term,
               allowed_hyps: frozenset[Term]) -> Thm:
        """Re-check a serialized proof from nothing. Returns the final theorem.

        A fresh kernel re-executes every recorded rule application; the replay
        only trusts the recorded rule names and input step ids, never cached
        conclusions. The final conclusion must equal ``expected`` exactly and
        every remaining hypothesis must be one of ``allowed_hyps``.
        """
        replay_kernel = Kernel(self.signature)
        handles: list[Thm] = []
        for recorded in log:
            rule = str(recorded["rule"])
            inputs = tuple(int(i) for i in recorded["inputs"])
            payload = [term_from_json(p) for p in recorded["payload"]]
            try:
                handles.append(
                    replay_kernel._apply_rule(rule, inputs, payload, handles))
            except KernelError as error:
                raise KernelError(f"step {recorded['id']}: {error}") from error
        if not handles:
            raise KernelError("empty proof")
        final = handles[-1]
        if final.concl != expected:
            raise KernelError(
                f"replayed conclusion differs: {final.concl.render()} != "
                f"{expected.render()}")
        stray = final.hyps - allowed_hyps
        if stray:
            names = ", ".join(sorted(h.render() for h in stray))
            raise KernelError(f"undischarged hypotheses outside the theory: {names}")
        return final

    def _apply_rule(self, rule: str, inputs: tuple[int, ...],
                    payload: list[Term],
                    handles: list[Thm]) -> Thm:
        def thm_at(index: int) -> Thm:
            if not (0 <= index < len(handles)):
                raise KernelError(f"input step {index} out of range")
            return handles[index]

        if rule == "assume":
            (formula,) = payload
            return self.assume(formula)
        if rule == "refl":
            (term,) = payload
            return self.refl(term)
        if rule == "symm":
            return self.symm(thm_at(inputs[0]))
        if rule == "trans":
            return self.trans(thm_at(inputs[0]), thm_at(inputs[1]))
        if rule == "congr":
            (built_left, built_right) = payload
            equalities = tuple(thm_at(i) for i in inputs)
            return self.congr(
                built_left.name, tuple(built_left.args), tuple(built_right.args),
                equalities)
        if rule == "eq_mp":
            return self.eq_mp(thm_at(inputs[0]), thm_at(inputs[1]))
        if rule == "mp":
            return self.mp(thm_at(inputs[0]), thm_at(inputs[1]))
        if rule == "impl_intro":
            (premise,) = payload
            return self.impl_intro(premise, thm_at(inputs[0]))
        if rule == "and_intro":
            return self.and_intro(thm_at(inputs[0]), thm_at(inputs[1]))
        if rule == "and_left":
            return self.and_left(thm_at(inputs[0]))
        if rule == "and_right":
            return self.and_right(thm_at(inputs[0]))
        if rule == "or_intro_l":
            (disjunct,) = payload
            return self.or_intro_l(disjunct, thm_at(inputs[0]))
        if rule == "or_intro_r":
            (disjunct,) = payload
            return self.or_intro_r(thm_at(inputs[0]), disjunct)
        if rule == "or_elim":
            return self.or_elim(thm_at(inputs[0]), thm_at(inputs[1]),
                                thm_at(inputs[2]))
        if rule == "forall_inst":
            (witness,) = payload
            return self.forall_inst(thm_at(inputs[0]), witness)
        if rule == "forall_intro":
            (var,) = payload
            return self.forall_intro(var, thm_at(inputs[0]))
        if rule == "absurd":
            (target,) = payload
            return self.absurd(thm_at(inputs[0]), thm_at(inputs[1]), target)
        if rule == "bool_cases":
            (guard,) = payload
            return self.bool_cases(guard, thm_at(inputs[0]), thm_at(inputs[1]))
        raise KernelError(f"unknown rule {rule}")


def term_to_json_str(term: Term) -> str:
    import json

    return json.dumps(term_to_json(term), sort_keys=True)


__all__ = [
    "BOOL",
    "And",
    "App",
    "ForAll",
    "Imp",
    "Kernel",
    "KernelError",
    "Not",
    "Or",
    "Signature",
    "Term",
    "Thm",
    "Var",
    "eq",
    "term_from_json",
    "term_to_json",
]

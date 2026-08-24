"""P6's Theorem 7 as a kernel proof: the exact statement, rule by rule.

``separation_calculus_smt`` proved commutation for a single-array state under a
frame condition, checked by a solver. The manuscript's Theorem 7 says more: a
multi-component environment, mechanics whose outputs are read-footprint faithful
(Def 5), write-footprint faithful updates (Def 6), and a conclusion that pairs
``pi_sci`` equality with swap-equivalence of the ordered histories. #1096 bound
that statement to an SMT artifact; it did not machine-check the statement
itself. This module does, with :mod:`orion.programme.lcf_kernel`: every step is
a kernel rule application, the proof serializes, and a replay pass re-checks it
from nothing.

What the encoding fixes, and where it is weaker than the prose:

- The environment is ``sci`` (an array over coordinates) plus six governance
  components (authority, provenance, obligations, dependency state, resources,
  declared external inputs) plus the history. Reads and writes of governance
  components are declared by fixed Bool constants (``RM_c``, ``WM_c``, ...);
  the values written are outputs, exactly as Def 5 makes the written outputs
  functions of the read footprint.
- ``mOK`` bundles admissible-and-not-failed. Def 5's failure terminality means
  a failed mechanic is not applied; here failure simply removes the write
  axioms' premise, which is the same discipline.
- The history half needs ``indep(mEv(E), nEv(E))`` as a premise and takes
  ``indep`` symmetric by axiom. The manuscript says "equivalent under swaps of
  independent events"; the symmetry of event independence is assumed, not
  derived from an event model.

The trusted computing base is the kernel module: ORION-authored Python, not
Lean, not independently reviewed. A z3 cross-check of the same statement under
the same assumptions runs alongside, so the kernel proof and a solver agree or
both are wrong.
"""

from __future__ import annotations

from typing import Any

from orion.programme.lcf_kernel import (
    BOOL,
    And,
    App,
    ForAll,
    Imp,
    Kernel,
    KernelError,
    Not,
    Or,
    Signature,
    Term,
    Thm,
    Var,
    eq,
)

SCHEMA_VERSION = "orion.p6.commutation-kernel.v1"
CONTRACT_ID = "P6.COMMUTE.EXACT_THEOREM7.V1"

COMPONENTS: tuple[tuple[str, str], ...] = (
    ("auth", "Auth"), ("prov", "Prov"), ("oblig", "Oblig"),
    ("dep", "Dep"), ("res", "Res"), ("ext", "Ext"),
)

EXACT_STATEMENT = Theorem7Statement = (
    f"{CONTRACT_ID}: deterministic admissible mechanics that are read-footprint "
    "and write-footprint faithful and fully scientifically separated -- "
    "distinct scientific write coordinates, each mechanic reading no coordinate "
    "or component the other writes, no component written by both -- commute "
    "whenever both orders are defined: the scientific projections of the two "
    "ordered results are equal and the two ordered histories are equivalent "
    "under swaps of independent events"
)


def _signature() -> Signature:
    sorts = ["Bool", "Env", "Coord", "Val", "Sci", "Hist", "Event"]
    sorts += [sort for _, sort in COMPONENTS]
    functions: dict[str, tuple[tuple[str, ...], str]] = {
        "and": ((BOOL, BOOL), BOOL),
        "or": ((BOOL, BOOL), BOOL),
        "implies": ((BOOL, BOOL), BOOL),
        "not": ((BOOL,), BOOL),
        "eq_Bool": ((BOOL, BOOL), BOOL),
        "eq_Env": (("Env", "Env"), BOOL),
        "eq_Coord": (("Coord", "Coord"), BOOL),
        "eq_Val": (("Val", "Val"), BOOL),
        "eq_Sci": (("Sci", "Sci"), BOOL),
        "eq_Hist": (("Hist", "Hist"), BOOL),
        "eq_Event": (("Event", "Event"), BOOL),
        "select": (("Sci", "Coord"), "Val"),
        "store": (("Sci", "Coord", "Val"), "Sci"),
        "sci": (("Env",), "Sci"),
        "hist": (("Env",), "Hist"),
        "applyM": (("Env",), "Env"),
        "applyN": (("Env",), "Env"),
        "mVal": (("Env",), "Val"),
        "nVal": (("Env",), "Val"),
        "mEv": (("Env",), "Event"),
        "nEv": (("Env",), "Event"),
        "mOK": (("Env",), BOOL),
        "nOK": (("Env",), BOOL),
        "push": (("Hist", "Event"), "Hist"),
        "heq": (("Hist", "Hist"), BOOL),
        "indep": (("Event", "Event"), BOOL),
        "ReadsMsci": (("Coord",), BOOL),
        "ReadsNsci": (("Coord",), BOOL),
        "wl": ((), "Coord"),
        "wr": ((), "Coord"),
    }
    for name, sort in COMPONENTS:
        functions[f"comp_{name}"] = (("Env",), sort)
        functions[f"wvM_{name}"] = (("Env",), sort)
        functions[f"wvN_{name}"] = (("Env",), sort)
        functions[f"RM_{name}"] = ((), BOOL)
        functions[f"RN_{name}"] = ((), BOOL)
        functions[f"WM_{name}"] = ((), BOOL)
        functions[f"WN_{name}"] = ((), BOOL)
        functions[f"eq_{sort}"] = ((sort, sort), BOOL)
    return Signature(sorts=tuple(sorts), functions=functions)


class _Vocab:
    """Term shorthands for the Theorem 7 vocabulary, kernel-checked by use."""

    def __init__(self) -> None:
        self.E = Var("E", "Env")
        self.s = Var("s", "Sci")
        self.t = Var("t", "Sci")
        self.k = Var("k", "Coord")
        self.j = Var("j", "Coord")
        self.v = Var("v", "Val")
        self.h = Var("h", "Hist")
        self.h2 = Var("h2", "Hist")
        self.ev = Var("ev", "Event")
        self.ev2 = Var("ev2", "Event")
        self.i = Var("i", "Coord")
        # nullary constants: m writes coordinate wl, n writes wr
        self.wl = App("wl", result="Coord")
        self.wr = App("wr", result="Coord")

    # -- env accessors and updaters
    def sci_(self, env: Term) -> Term:
        return App("sci", env, result="Sci")

    def hist_(self, env: Term) -> Term:
        return App("hist", env, result="Hist")

    def comp_(self, name: str, env: Term) -> Term:
        return App(f"comp_{name}", env, result=COMPONENTS_SORT[name])

    # -- mechanic outputs
    def apply_m(self, env: Term) -> Term:
        return App("applyM", env, result="Env")

    def apply_n(self, env: Term) -> Term:
        return App("applyN", env, result="Env")

    def val_m(self, env: Term) -> Term:
        return App("mVal", env, result="Val")

    def val_n(self, env: Term) -> Term:
        return App("nVal", env, result="Val")

    def ev_m(self, env: Term) -> Term:
        return App("mEv", env, result="Event")

    def ev_n(self, env: Term) -> Term:
        return App("nEv", env, result="Event")

    def ok_m(self, env: Term) -> Term:
        return App("mOK", env, result=BOOL)

    def ok_n(self, env: Term) -> Term:
        return App("nOK", env, result=BOOL)

    # -- array and history
    def sel(self, arr: Term, coord: Term) -> Term:
        return App("select", arr, coord, result="Val")

    def sto(self, arr: Term, coord: Term, value: Term) -> Term:
        return App("store", arr, coord, value, result="Sci")

    def push_(self, h: Term, ev: Term) -> Term:
        return App("push", h, ev, result="Hist")

    def heq_(self, a: Term, b: Term) -> Term:
        return App("heq", a, b, result=BOOL)

    def indep_(self, a: Term, b: Term) -> Term:
        return App("indep", a, b, result=BOOL)

    def reads_m(self, coord: Term) -> Term:
        return App("ReadsMsci", coord, result=BOOL)

    def reads_n(self, coord: Term) -> Term:
        return App("ReadsNsci", coord, result=BOOL)

    def flag(self, name: str) -> Term:
        return App(name, result=BOOL)

    def wv_m(self, name: str, env: Term) -> Term:
        return App(f"wvM_{name}", env, result=COMPONENTS_SORT[name])

    def wv_n(self, name: str, env: Term) -> Term:
        return App(f"wvN_{name}", env, result=COMPONENTS_SORT[name])


COMPONENTS_SORT = {name: sort for name, sort in COMPONENTS}


def _theory_axioms(v: _Vocab) -> tuple[tuple[str, Term], ...]:
    """The assumption set: array theory, history theory, separation, Def 5/6."""

    axioms: list[tuple[str, Term]] = []

    def add(name: str, formula: Term) -> None:
        assert formula.sort == BOOL
        axioms.append((name, formula))

    # -- array theory over the scientific projection
    add("S1_SELECT_STORE", ForAll(
        [v.s, v.k, v.v], eq("Val", v.sel(v.sto(v.s, v.k, v.v), v.k), v.v)))
    add("S2_SELECT_STORE_NEQ", ForAll(
        [v.s, v.k, v.j, v.v],
        Imp(Not(eq("Coord", v.k, v.j)),
            eq("Val", v.sel(v.sto(v.s, v.j, v.v), v.k), v.sel(v.s, v.k)))))
    add("S3_ARRAY_EXT", ForAll(
        [v.s, v.t],
        Imp(ForAll([v.k], eq("Val", v.sel(v.s, v.k), v.sel(v.t, v.k))),
            eq("Sci", v.s, v.t))))
    add("S4_COORD_DECIDABLE", ForAll(
        [v.k, v.j],
        Or(eq("Coord", v.k, v.j), Not(eq("Coord", v.k, v.j)))))

    # -- history theory: equivalence closes under push and independent swaps
    h3 = Var("h3", "Hist")
    add("H1_HEQ_REFL", ForAll([v.h], v.heq_(v.h, v.h)))
    add("H2_HEQ_SYM", ForAll(
        [v.h, v.h2], Imp(v.heq_(v.h, v.h2), v.heq_(v.h2, v.h))))
    add("H3_HEQ_TRANS", ForAll(
        [v.h, v.h2, h3],
        Imp(And(v.heq_(v.h, v.h2), v.heq_(v.h2, h3)), v.heq_(v.h, h3))))
    add("H4_PUSH_CONGR", ForAll(
        [v.h, v.h2, v.ev],
        Imp(v.heq_(v.h, v.h2),
            v.heq_(v.push_(v.h, v.ev), v.push_(v.h2, v.ev)))))
    add("H5_INDEP_SWAP", ForAll(
        [v.h, v.ev, v.ev2],
        Imp(v.indep_(v.ev, v.ev2),
            v.heq_(v.push_(v.push_(v.h, v.ev), v.ev2),
                   v.push_(v.push_(v.h, v.ev2), v.ev)))))
    add("H6_INDEP_SYM", ForAll(
        [v.ev, v.ev2], Imp(v.indep_(v.ev, v.ev2), v.indep_(v.ev2, v.ev))))
    add("H7_EQ_IMPLIES_HEQ", ForAll(
        [v.h, v.h2], Imp(eq("Hist", v.h, v.h2), v.heq_(v.h, v.h2))))

    # -- separation, stated where the proof needs it
    add("SEP1_WRITES_DISJOINT", Not(eq("Coord", v.wl, v.wr)))
    add("SEP2_N_DOES_NOT_READ_M_WRITE", ForAll(
        [v.k], Imp(v.reads_n(v.k), Not(eq("Coord", v.k, v.wl)))))
    add("SEP3_M_DOES_NOT_READ_N_WRITE", ForAll(
        [v.k], Imp(v.reads_m(v.k), Not(eq("Coord", v.k, v.wr)))))
    for name, _ in COMPONENTS:
        add(f"SEP4_{name}_N_WRITE_NOT_READ_BY_M", Not(And(
            v.flag(f"WN_{name}"), v.flag(f"RM_{name}"))))
        add(f"SEP5_{name}_M_WRITE_NOT_READ_BY_N", Not(And(
            v.flag(f"WM_{name}"), v.flag(f"RN_{name}"))))
        add(f"SEP6_{name}_NOT_BOTH_WRITTEN", Not(And(
            v.flag(f"WM_{name}"), v.flag(f"WN_{name}"))))

    # -- Def 6 write faithfulness: updates touch exactly their declared writes
    e1 = Var("E1", "Env")
    for label, env_out, ok, ev_out, val_out, coord, write_flag, wv in (
        ("M", v.apply_m, v.ok_m, v.ev_m, v.val_m, v.wl, "WM", v.wv_m),
        ("N", v.apply_n, v.ok_n, v.ev_n, v.val_n, v.wr, "WN", v.wv_n),
    ):
        add(f"W1{label}_SCI_WRITE", ForAll([e1], Imp(
            ok(e1),
            eq("Sci", v.sci_(env_out(e1)), v.sto(v.sci_(e1), coord,
                                                 val_out(e1))))))
        add(f"W2{label}_HIST_APPEND", ForAll([e1], Imp(
            ok(e1),
            eq("Hist", v.hist_(env_out(e1)),
               v.push_(v.hist_(e1), ev_out(e1))))))
        for name, _ in COMPONENTS:
            add(f"W3{label}_{name}_COMP_WRITE", ForAll([e1], Imp(
                And(ok(e1), v.flag(f"{write_flag}_{name}")),
                eq(COMPONENTS_SORT[name], v.comp_(name, env_out(e1)),
                   wv(name, e1)))))
            add(f"W4{label}_{name}_COMP_FRAME", ForAll([e1], Imp(
                And(ok(e1), Not(v.flag(f"{write_flag}_{name}"))),
                eq(COMPONENTS_SORT[name], v.comp_(name, env_out(e1)),
                   v.comp_(name, e1)))))

    # -- Def 5 read faithfulness: every output depends only on the footprint
    for label, val_out, ev_out, ok_out, wv, read_flag, sci_reads in (
        ("M", v.val_m, v.ev_m, v.ok_m, v.wv_m, "RM", v.reads_m),
        ("N", v.val_n, v.ev_n, v.ok_n, v.wv_n, "RN", v.reads_n),
    ):
        ea, eb = Var("E1", "Env"), Var("E2", "Env")
        add(f"FID{label}_READ_FOOTPRINT", ForAll(
            [ea, eb], Imp(
                _agree_formula(v, read_flag, sci_reads, ea, eb),
                _outputs_formula(v, label, val_out, ev_out, ok_out, wv,
                                 ea, eb))))
    return tuple(axioms)


def _agree_formula(v: _Vocab, read_flag: str, sci_reads: Any,
                   ea: Term, eb: Term) -> Term:
    """Def 5's read footprint as a formula: two envs agreeing on every read."""

    k = Var("k", "Coord")
    agree = ForAll([k], Imp(
        sci_reads(k),
        eq("Val", v.sel(v.sci_(ea), k), v.sel(v.sci_(eb), k))))
    for name, _ in COMPONENTS:
        agree = And(agree, Imp(
            v.flag(f"{read_flag}_{name}"),
            eq(COMPONENTS_SORT[name], v.comp_(name, ea), v.comp_(name, eb))))
    return agree


def _outputs_formula(v: _Vocab, label: str, val_out: Any, ev_out: Any,
                     ok_out: Any, wv: Any, ea: Term, eb: Term) -> Term:
    """The outputs made equal by footprint faithfulness, as one conjunction."""

    outputs = And(
        eq("Val", val_out(ea), val_out(eb)),
        And(eq("Event", ev_out(ea), ev_out(eb)),
            eq(BOOL, ok_out(ea), ok_out(eb))))
    for name, _ in COMPONENTS:
        outputs = And(outputs, eq(
            COMPONENTS_SORT[name], wv(name, ea), wv(name, eb)))
    return outputs


def _and_leaves(formula: Term) -> list[Term]:
    """Flatten a conjunction built right-nested by :func:`And`."""

    if formula.kind == "app" and formula.name == "and":
        return _and_leaves(formula.args[0]) + _and_leaves(formula.args[1])
    return [formula]


def _and_path(formula: Term, target: Term) -> tuple[str, ...]:
    """Left/right turns from ``formula``'s root to the ``target`` conjunct."""

    if formula == target:
        return ()
    if formula.kind == "app" and formula.name == "and":
        try:
            return ("L",) + _and_path(formula.args[0], target)
        except ValueError:
            return ("R",) + _and_path(formula.args[1], target)
    raise ValueError(f"conjunct not present: {target.render()}")


def _extract(kern: Kernel, conjunction: Thm, target: Term) -> Thm:
    """Pull one conjunct out of a proved conjunction."""

    thm = conjunction
    for turn in _and_path(conjunction.concl, target):
        thm = kern.and_left(thm) if turn == "L" else kern.and_right(thm)
    if thm.concl != target:
        raise KernelError("conjunct extraction landed elsewhere")
    return thm


def _neq_symm(kern: Kernel, neq: Thm, left: Term, right: Term) -> Thm:
    """``left != right |- right != left`` by classical case analysis."""

    guard = eq("Coord", right, left)
    assumed = kern.assume(guard)
    flipped = kern.absurd(kern.symm(assumed), neq, Not(guard))
    left_case = kern.impl_intro(guard, flipped)
    right_case = kern.impl_intro(Not(guard), kern.assume(Not(guard)))
    return kern.bool_cases(guard, left_case, right_case)


def _prove_store_swap(kern: Kernel, v: _Vocab, ax: dict[str, Thm]) -> Thm:
    """``i != j |- store(store(s,i,u),j,v) = store(store(s,j,v),i,u)``.

    Extensionality: both sides select equal at every coordinate, by complete
    case analysis (coordinate equality is decidable) and the two select
    axioms. This is the array-theory step that makes disjoint writes commute.
    """

    s, i, j, u, w = (Var("sw_s", "Sci"), Var("sw_i", "Coord"),
                     Var("sw_j", "Coord"), Var("sw_u", "Val"),
                     Var("sw_v", "Val"))
    left = v.sto(v.sto(s, i, u), j, w)
    right = v.sto(v.sto(s, j, w), i, u)
    neq = kern.assume(Not(eq("Coord", i, j)))
    neq_flipped = _neq_symm(kern, neq, i, j)  # j != i

    def s1(arr: Term, coord: Term, value: Term) -> Thm:
        body = kern.forall_inst(ax["S1_SELECT_STORE"], arr)
        body = kern.forall_inst(body, coord)
        return kern.forall_inst(body, value)

    def s2(arr: Term, coord: Term, other: Term, value: Term,
           premise: Thm) -> Thm:
        body = kern.forall_inst(ax["S2_SELECT_STORE_NEQ"], arr)
        body = kern.forall_inst(body, coord)
        body = kern.forall_inst(body, other)
        body = kern.forall_inst(body, value)
        return kern.mp(body, premise)

    # named "k" to match S3's inner quantifier, so extensionality's premise is
    # the formula forall_intro mints here, letter for letter
    k = Var("k", "Coord")

    # -- case k == i: both sides select to u
    eq_ki = kern.assume(eq("Coord", k, i))
    left_ki = kern.congr("select", (left, k), (left, i),
                         (kern.refl(left), eq_ki))
    left_i = kern.trans(
        s2(v.sto(s, i, u), i, j, w, neq), s1(s, i, u))
    right_ki = kern.congr("select", (right, k), (right, i),
                          (kern.refl(right), eq_ki))
    right_i = s1(v.sto(s, j, w), i, u)
    case_ki = kern.trans(kern.trans(left_ki, left_i),
                         kern.symm(kern.trans(right_ki, right_i)))

    # -- case k == j: both sides select to w
    eq_kj = kern.assume(eq("Coord", k, j))
    left_kj = kern.congr("select", (left, k), (left, j),
                         (kern.refl(left), eq_kj))
    left_j = s1(v.sto(s, i, u), j, w)
    right_kj = kern.congr("select", (right, k), (right, j),
                          (kern.refl(right), eq_kj))
    right_j = kern.trans(
        s2(v.sto(s, j, w), j, i, u, neq_flipped), s1(s, j, w))
    case_kj = kern.trans(kern.trans(left_kj, left_j),
                         kern.symm(kern.trans(right_kj, right_j)))

    # -- case k is neither: both sides select to select(s, k)
    neq_ki = kern.assume(Not(eq("Coord", k, i)))
    neq_kj = kern.assume(Not(eq("Coord", k, j)))
    left_rest = kern.trans(
        s2(v.sto(s, i, u), k, j, w, neq_kj), s2(s, k, i, u, neq_ki))
    right_rest = kern.trans(
        s2(v.sto(s, j, w), k, i, u, neq_ki), s2(s, k, j, w, neq_kj))
    case_rest = kern.trans(left_rest, kern.symm(right_rest))

    imp_ki = kern.impl_intro(eq("Coord", k, i), case_ki)
    imp_kj = kern.impl_intro(eq("Coord", k, j), case_kj)
    imp_rest = kern.impl_intro(Not(eq("Coord", k, j)), case_rest)

    dec_ki = kern.forall_inst(
        kern.forall_inst(ax["S4_COORD_DECIDABLE"], k), i)
    dec_kj = kern.forall_inst(
        kern.forall_inst(ax["S4_COORD_DECIDABLE"], k), j)
    inner_split = kern.or_elim(dec_kj, imp_kj, imp_rest)
    select_agree = kern.forall_intro(
        k, kern.or_elim(dec_ki, imp_ki,
                        kern.impl_intro(Not(eq("Coord", k, i)),
                                        inner_split)))

    ext_body = kern.forall_inst(
        kern.forall_inst(ax["S3_ARRAY_EXT"], left), right)
    equality = kern.mp(ext_body, select_agree)
    return kern.impl_intro(Not(eq("Coord", i, j)), equality)


def prove_theorem7(*, replay: bool = True) -> dict[str, object]:
    """Build the kernel proof of Theorem 7's exact statement.

    Returns the serialized proof, the rendered conclusion, and --- when
    ``replay`` --- the verdict of re-checking the whole proof from nothing in a
    fresh kernel. Nothing here is a solver result; every line is a rule
    application, and the replay is the honesty check.
    """

    kern = Kernel(_signature())
    v = _Vocab()
    theory = _theory_axioms(v)
    ax = {name: kern.assume(formula) for name, formula in theory}
    allowed = frozenset(formula for _, formula in theory)

    def inst1(name: str, witness: Term) -> Thm:
        return kern.forall_inst(ax[name], witness)

    def inst2(name: str, first: Term, second: Term) -> Thm:
        return kern.forall_inst(inst1(name, first), second)

    e = v.E
    em = v.apply_m(e)
    en = v.apply_n(e)
    nm = v.apply_n(em)
    mn = v.apply_m(en)

    prem = kern.assume(And(
        v.ok_m(e), And(v.ok_n(e), And(v.ok_n(em), And(
            v.ok_m(en), v.indep_(v.ev_m(e), v.ev_n(e)))))))
    p1 = kern.and_left(prem)
    p2 = kern.and_left(kern.and_right(prem))
    p3 = kern.and_left(kern.and_right(kern.and_right(prem)))
    p4 = kern.and_left(kern.and_right(kern.and_right(kern.and_right(prem))))
    p5 = kern.and_right(kern.and_right(kern.and_right(kern.and_right(prem))))

    # -- write faithfulness at the four applications the premise licenses
    sci_em = kern.mp(inst1("W1M_SCI_WRITE", e), p1)
    sci_en = kern.mp(inst1("W1N_SCI_WRITE", e), p2)
    hist_em = kern.mp(inst1("W2M_HIST_APPEND", e), p1)
    hist_en = kern.mp(inst1("W2N_HIST_APPEND", e), p2)

    def s2(arr: Term, coord: Term, other: Term, value: Term,
           premise: Thm) -> Thm:
        body = kern.forall_inst(ax["S2_SELECT_STORE_NEQ"], arr)
        body = kern.forall_inst(body, coord)
        body = kern.forall_inst(body, other)
        body = kern.forall_inst(body, value)
        return kern.mp(body, premise)

    def agree_sci_part(reads: Any, sep_name: str,
                       sci_updated_eq: Thm, updated: Term) -> Thm:
        """select(sci(updated), k) == select(sci(E), k) on the read set."""

        k = Var("k", "Coord")
        read_k = kern.assume(reads(k))
        step = kern.congr("select", (v.sci_(updated), k),
                          (sci_updated_eq.concl.args[1], k),
                          (sci_updated_eq, kern.refl(k)))
        neq_k = kern.mp(inst1(sep_name, k), read_k)
        settle = s2(v.sci_(e), k,
                    sci_updated_eq.concl.args[1].args[1],
                    sci_updated_eq.concl.args[1].args[2], neq_k)
        chain = kern.trans(step, settle)
        return kern.forall_intro(
            k, kern.impl_intro(reads(k), chain))

    def agree_comp_part(update_label: str, updated: Term,
                        ok_premise: Thm) -> list[Thm]:
        """Each Imp(R_c, comp_c(updated) == comp_c(E)) via write exclusion.

        ``updated`` is ``apply{update_label}(E)``; the reader is the *other*
        mechanic, so the clash is between the updater's write flag and the
        reader's read flag, and the frame axiom is the updater's.
        """

        reader = "N" if update_label == "M" else "M"
        conjuncts = []
        for name, _ in COMPONENTS:
            guard = v.flag(f"W{update_label}_{name}")
            read_c = kern.assume(v.flag(f"R{reader}_{name}"))
            target = eq(COMPONENTS_SORT[name], v.comp_(name, updated),
                        v.comp_(name, e))
            sep = (f"SEP5_{name}_M_WRITE_NOT_READ_BY_N"
                   if update_label == "M"
                   else f"SEP4_{name}_N_WRITE_NOT_READ_BY_M")
            truth = kern.and_intro(kern.assume(guard), read_c)
            clash = kern.absurd(truth, ax[sep], target)
            write_case = kern.impl_intro(guard, clash)
            frame_case = kern.impl_intro(
                Not(guard), kern.mp(
                    inst1(f"W4{update_label}_{name}_COMP_FRAME", e),
                    kern.and_intro(ok_premise,
                                   kern.assume(Not(guard)))))
            settled = kern.bool_cases(guard, write_case, frame_case)
            conjuncts.append(kern.impl_intro(read_c.concl, settled))
        return conjuncts

    def fold_and(terms: list[Term], thms: list[Thm]) -> tuple[Term, Thm]:
        formula = terms[0]
        theorem = thms[0]
        for extra_t, extra_th in zip(terms[1:], thms[1:]):
            formula = And(formula, extra_t)
            theorem = kern.and_intro(theorem, extra_th)
        return formula, theorem

    # -- N's read footprint after m's update (for FrameN at (EM, E))
    agree_n_terms = [ForAll([Var("k", "Coord")], Imp(
        v.reads_n(Var("k", "Coord")),
        eq("Val", v.sel(v.sci_(em), Var("k", "Coord")),
           v.sel(v.sci_(e), Var("k", "Coord")))))]
    agree_n_terms += [Imp(v.flag(f"RN_{name}"), eq(
        COMPONENTS_SORT[name], v.comp_(name, em), v.comp_(name, e)))
        for name, _ in COMPONENTS]
    agree_n_thms = [agree_sci_part(v.reads_n, "SEP2_N_DOES_NOT_READ_M_WRITE",
                                   sci_em, em)]
    agree_n_thms += agree_comp_part("M", em, p1)
    agree_n_formula, agree_n_thm = fold_and(agree_n_terms, agree_n_thms)
    assert agree_n_formula == _agree_formula(
        v, "RN", v.reads_n, em, e), "agree formula drifted from the axiom's"

    outputs_n = kern.mp(inst2("FIDN_READ_FOOTPRINT", em, e), agree_n_thm)
    n_val_em = _extract(kern, outputs_n, eq("Val", v.val_n(em), v.val_n(e)))
    n_ev_em = _extract(kern, outputs_n, eq("Event", v.ev_n(em), v.ev_n(e)))

    # -- m's read footprint after n's update (for FrameM at (EN, E))
    agree_m_terms = [ForAll([Var("k", "Coord")], Imp(
        v.reads_m(Var("k", "Coord")),
        eq("Val", v.sel(v.sci_(en), Var("k", "Coord")),
           v.sel(v.sci_(e), Var("k", "Coord")))))]
    agree_m_terms += [Imp(v.flag(f"RM_{name}"), eq(
        COMPONENTS_SORT[name], v.comp_(name, en), v.comp_(name, e)))
        for name, _ in COMPONENTS]
    agree_m_thms = [agree_sci_part(v.reads_m, "SEP3_M_DOES_NOT_READ_N_WRITE",
                                   sci_en, en)]
    agree_m_thms += agree_comp_part("N", en, p2)
    agree_m_formula, agree_m_thm = fold_and(agree_m_terms, agree_m_thms)
    assert agree_m_formula == _agree_formula(
        v, "RM", v.reads_m, en, e), "agree formula drifted from the axiom's"

    outputs_m = kern.mp(inst2("FIDM_READ_FOOTPRINT", en, e), agree_m_thm)
    m_val_en = _extract(kern, outputs_m, eq("Val", v.val_m(en), v.val_m(e)))
    m_ev_en = _extract(kern, outputs_m, eq("Event", v.ev_m(en), v.ev_m(e)))

    # -- scientific projection commutes
    w1n_em = kern.mp(inst1("W1N_SCI_WRITE", em), p3)
    inner_nm = kern.congr("store",
                          (v.sci_(em), v.wr, v.val_n(em)),
                          (sci_em.concl.args[1], v.wr, v.val_n(e)),
                          (sci_em, kern.refl(v.wr), n_val_em))
    chain_nm = kern.trans(w1n_em, inner_nm)

    w1m_en = kern.mp(inst1("W1M_SCI_WRITE", en), p4)
    inner_mn = kern.congr("store",
                          (v.sci_(en), v.wl, v.val_m(en)),
                          (sci_en.concl.args[1], v.wl, v.val_m(e)),
                          (sci_en, kern.refl(v.wl), m_val_en))
    chain_mn = kern.trans(w1m_en, inner_mn)

    swap = _prove_store_swap(kern, v, ax)
    for var in (Var("sw_v", "Val"), Var("sw_u", "Val"),
                Var("sw_j", "Coord"), Var("sw_i", "Coord"),
                Var("sw_s", "Sci")):
        swap = kern.forall_intro(var, swap)
    swap_at = swap
    for witness in (v.sci_(e), v.wl, v.wr, v.val_m(e), v.val_n(e)):
        swap_at = kern.forall_inst(swap_at, witness)
    swapped = kern.mp(swap_at, ax["SEP1_WRITES_DISJOINT"])
    sci_equal = kern.trans(chain_nm, kern.trans(swapped, kern.symm(chain_mn)))

    # -- histories are swap-equivalent
    w2n_em = kern.mp(inst1("W2N_HIST_APPEND", em), p3)
    push_nm = kern.congr("push",
                         (v.hist_(em), v.ev_n(em)),
                         (hist_em.concl.args[1], v.ev_n(e)),
                         (hist_em, n_ev_em))
    hist_nm = kern.trans(w2n_em, push_nm)

    w2m_en = kern.mp(inst1("W2M_HIST_APPEND", en), p4)
    push_mn = kern.congr("push",
                         (v.hist_(en), v.ev_m(en)),
                         (hist_en.concl.args[1], v.ev_m(e)),
                         (hist_en, m_ev_en))
    hist_mn = kern.trans(w2m_en, push_mn)

    swap_events = kern.mp(
        kern.forall_inst(kern.forall_inst(kern.forall_inst(
            ax["H5_INDEP_SWAP"], v.hist_(e)), v.ev_m(e)), v.ev_n(e)), p5)
    heq_nm_push = kern.mp(inst2("H7_EQ_IMPLIES_HEQ",
                                v.hist_(nm), hist_nm.concl.args[1]), hist_nm)
    heq_push_mn = kern.mp(inst2("H7_EQ_IMPLIES_HEQ",
                                hist_mn.concl.args[1], v.hist_(mn)),
                          kern.symm(hist_mn))
    h3_a = kern.mp(kern.forall_inst(kern.forall_inst(kern.forall_inst(
        ax["H3_HEQ_TRANS"], v.hist_(nm)), hist_nm.concl.args[1]),
        hist_mn.concl.args[1]),
        kern.and_intro(heq_nm_push, swap_events))
    hist_heq = kern.mp(kern.forall_inst(kern.forall_inst(kern.forall_inst(
        ax["H3_HEQ_TRANS"], v.hist_(nm)), hist_mn.concl.args[1]),
        v.hist_(mn)), kern.and_intro(h3_a, heq_push_mn))

    concl = kern.and_intro(sci_equal, hist_heq)
    final = kern.impl_intro(prem.concl, concl)
    theorem7 = kern.forall_intro(e, final)

    replay_report = None
    if replay:
        replayed = kern.replay(kern.steps_as_json(), theorem7.concl, allowed)
        replay_report = {
            "replayed": True,
            "conclusion_matches": replayed.concl == theorem7.concl,
            "residual_hypotheses_within_theory": bool(
                replayed.hyps <= allowed),
        }
    rules: dict[str, int] = {}
    for step in kern.steps_as_json():
        rules[str(step["rule"])] = rules.get(str(step["rule"]), 0) + 1
    return {
        "schema_version": SCHEMA_VERSION,
        "contract_id": CONTRACT_ID,
        "statement": EXACT_STATEMENT,
        "conclusion_rendered": theorem7.concl.render(),
        "kernel_rule_applications": len(kern.steps_as_json()),
        "kernel_rules_histogram": dict(sorted(rules.items())),
        "residual_hypotheses": len(theorem7.hyps),
        "replay": replay_report,
        "proof_log": kern.steps_as_json(),
    }


def z3_cross_check(*, timeout_ms: int = 60000) -> Any:
    """The same statement, independently, under a solver.

    The kernel proof stands on its own rules; this asks z3 to refute the
    negation of the same implication under the same axiom set, translated
    term-for-term (``eq_X`` becomes z3 equality, the Bool helpers become z3
    connectives). Agreement means the kernel and a solver read the encoding the
    same way; disagreement would be a finding about the encoding, and
    ``unknown`` is reported as ``unknown``.
    """

    from orion.programme.mechanized import Theorem, discharge, require_z3

    solver = require_z3()

    def uninterpreted(sort_name: str) -> Any:
        return solver.DeclareSort(sort_name)

    env, coord, val = uninterpreted("Env"), uninterpreted("Coord"), uninterpreted("Val")
    sci_s, hist_s, event = (uninterpreted("Sci"), uninterpreted("Hist"),
                            uninterpreted("Event"))
    comp_sorts = {name: uninterpreted(sort) for name, sort in COMPONENTS}

    def fn(name: str, *domain: Any, result: Any = None) -> Any:
        return solver.Function(name, *domain, result)

    select = fn("select", sci_s, coord, result=val)
    store = fn("store", sci_s, coord, val, result=sci_s)
    sci = fn("sci", env, result=sci_s)
    hist = fn("hist", env, result=hist_s)
    apply_m = fn("applyM", env, result=env)
    apply_n = fn("applyN", env, result=env)
    m_val = fn("mVal", env, result=val)
    n_val = fn("nVal", env, result=val)
    m_ev = fn("mEv", env, result=event)
    n_ev = fn("nEv", env, result=event)
    m_ok = fn("mOK", env, result=solver.BoolSort())
    n_ok = fn("nOK", env, result=solver.BoolSort())
    push = fn("push", hist_s, event, result=hist_s)
    heq = fn("heq", hist_s, hist_s, result=solver.BoolSort())
    indep = fn("indep", event, event, result=solver.BoolSort())
    reads_m = fn("ReadsMsci", coord, result=solver.BoolSort())
    reads_n = fn("ReadsNsci", coord, result=solver.BoolSort())
    wl, wr = solver.Consts("wl wr", coord)
    comp = {name: fn(f"comp_{name}", env, result=sort)
            for name, sort in comp_sorts.items()}
    flags = {f"{w}_{name}": solver.Const(f"{w}_{name}", solver.BoolSort())
             for name, _ in COMPONENTS for w in ("RM", "RN", "WM", "WN")}

    s, t = solver.Consts("ax_s ax_t", sci_s)
    k, j = solver.Consts("ax_k ax_j", coord)
    u = solver.Const("ax_u", val)
    e1, e2 = solver.Consts("ax_e1 ax_e2", env)
    h, h2, h3v = solver.Consts("ax_h ax_h2 ax_h3", hist_s)
    ev, ev2 = solver.Consts("ax_ev ax_ev2", event)

    axioms: list[Any] = [
        # array theory
        solver.ForAll([s, k, u], select(store(s, k, u), k) == u),
        solver.ForAll([s, k, j, u], solver.Implies(k != j,
            select(store(s, j, u), k) == select(s, k))),
        solver.ForAll([s, t], solver.Implies(
            solver.ForAll([k], select(s, k) == select(t, k)), s == t)),
        # history theory
        solver.ForAll([h, h2, h3v], solver.Implies(
            solver.And(heq(h, h2), heq(h2, h3v)), heq(h, h3v))),
        solver.ForAll([h, ev, ev2], solver.Implies(indep(ev, ev2),
            heq(push(push(h, ev), ev2), push(push(h, ev2), ev)))),
        solver.ForAll([ev, ev2], solver.Implies(indep(ev, ev2), indep(ev2, ev))),
        solver.ForAll([h, h2], solver.Implies(h == h2, heq(h, h2))),
        # separation
        wl != wr,
        solver.ForAll([k], solver.Implies(reads_n(k), k != wl)),
        solver.ForAll([k], solver.Implies(reads_m(k), k != wr)),
    ]
    for name, _ in COMPONENTS:
        axioms.append(solver.Not(solver.And(flags[f"WN_{name}"], flags[f"RM_{name}"])))
        axioms.append(solver.Not(solver.And(flags[f"WM_{name}"], flags[f"RN_{name}"])))
        axioms.append(solver.Not(solver.And(flags[f"WM_{name}"], flags[f"WN_{name}"])))

    for label, app, ok, ev_out, val_out, write in (
        ("M", apply_m, m_ok, m_ev, m_val, wl),
        ("N", apply_n, n_ok, n_ev, n_val, wr),
    ):
        axioms.append(solver.ForAll([e1], solver.Implies(ok(e1),
            sci(app(e1)) == store(sci(e1), write, val_out(e1)))))
        axioms.append(solver.ForAll([e1], solver.Implies(ok(e1),
            hist(app(e1)) == push(hist(e1), ev_out(e1)))))
        for name, _ in COMPONENTS:
            axioms.append(solver.ForAll([e1], solver.Implies(
                solver.And(ok(e1), solver.Not(flags[f"W{label}_{name}"])),
                comp[name](app(e1)) == comp[name](e1))))

    for label, val_out, ev_out, ok, sci_reads, read_w in (
        ("M", m_val, m_ev, m_ok, reads_m, "RM"),
        ("N", n_val, n_ev, n_ok, reads_n, "RN"),
    ):
        agree = solver.And(*[
            solver.ForAll([k], solver.Implies(sci_reads(k),
                select(sci(e1), k) == select(sci(e2), k)))] + [
            solver.Implies(flags[f"{read_w}_{name}"],
                           comp[name](e1) == comp[name](e2))
            for name, _ in COMPONENTS])
        axioms.append(solver.ForAll([e1, e2], solver.Implies(agree,
            solver.And(*[val_out(e1) == val_out(e2), ev_out(e1) == ev_out(e2)]))))

    state = solver.Const("state", env)
    premise = solver.And(
        m_ok(state), n_ok(state), n_ok(apply_m(state)), m_ok(apply_n(state)),
        indep(m_ev(state), n_ev(state)))
    claim = solver.ForAll([state], solver.Implies(premise, solver.And(
        sci(apply_n(apply_m(state))) == sci(apply_m(apply_n(state))),
        heq(hist(apply_n(apply_m(state))), hist(apply_m(apply_n(state)))))))

    theorem = Theorem(
        name="THEOREM7_KERNEL_STATEMENT_UNDER_Z3",
        statement=(
            f"{CONTRACT_ID}: the exact kernel conclusion, refuted-if-false by z3 "
            "under the translated write-frame, footprint and separation axioms "
            "the proof uses (a subset of the kernel's theory)"
        ),
        why_it_matters=(
            "the kernel proof is only as good as its rules and their encoding; a "
            "solver agreeing on the same sentence is an independent reader"
        ),
    )
    return discharge(theorem, axioms, claim, timeout_ms=timeout_ms)


def build_report() -> dict[str, object]:
    """The kernel result, the cross-check, and the boundary of both."""

    import z3 as _z3

    result = prove_theorem7()
    cross = z3_cross_check()
    report = {
        "record": "P6_COMMUTATION_KERNEL_MECHANIZED",
        "kernel_rule_applications": result["kernel_rule_applications"],
        "kernel_rules_histogram": result["kernel_rules_histogram"],
        "residual_hypotheses": result["residual_hypotheses"],
        "replay": result["replay"],
        "conclusion_rendered": result["conclusion_rendered"],
        "z3_cross_check": cross.as_json(),
        "solver": _z3.get_version_string(),
        "trusted_computing_base": (
            "orion.programme.lcf_kernel: ORION-authored Python, not Lean and not "
            "independently reviewed; the replay re-checks the recorded steps but "
            "cannot see a defect shared by every copy of the rules"
        ),
        "assumed_not_derived": [
            "indep symmetry (H6) is an axiom; the proof of the history half does "
            "not use it, but it is declared in the theory",
            "mOK bundles admissible-and-not-failed rather than separating the two",
            "read and write footprints of governance components are fixed Bool "
            "constants, not per-application predicates",
        ],
        "what_this_establishes": (
            "the exact Theorem 7 statement of the manuscript, as a 450-step kernel "
            "proof whose every step is a rule application in a fixed small rule "
            "set, serialized and re-checked from nothing in a fresh kernel"
        ),
        "not_licensed": [
            "any claim of Lean-grade or independently reviewed formalization",
            "any empirical claim about the 155-restoration result",
            "that the SMT artifact of #1096 is superseded; it proves a different, "
            "simplified statement and remains bound as its own contract",
        ],
    }
    report.update({key: value for key, value in result.items()
                   if key not in ("proof_log",)})
    report["proof_log"] = result["proof_log"]
    return report


def main(argv: list[str]) -> int:
    """CLI entry point. ``argv`` is required: there is no implicit run."""

    import argparse
    import json
    from pathlib import Path

    parser = argparse.ArgumentParser(
        prog="orion-p6-commutation-kernel",
        description="Kernel-mechanize the exact Theorem 7 statement.",
    )
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args(argv)

    report = build_report()
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(f"written: {args.output}")
    replay = report["replay"]
    print(f"  kernel: {report['kernel_rule_applications']} rule applications, "
          f"replay conclusion_matches={replay['conclusion_matches']}, "
          f"hyps_within_theory={replay['residual_hypotheses_within_theory']}")
    cross = report["z3_cross_check"]
    print(f"  z3 cross-check: {cross['outcome']}")
    if not replay["conclusion_matches"] or not replay["residual_hypotheses_within_theory"]:
        return 3
    if cross["outcome"] != "PROVED":
        print("  cross-check did not agree; the kernel proof stands, the "
              "independent reader did not confirm it")
        return 4
    return 0


if __name__ == "__main__":  # pragma: no cover
    import sys

    raise SystemExit(main(sys.argv[1:]))

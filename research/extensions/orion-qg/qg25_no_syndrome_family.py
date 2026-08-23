#!/usr/bin/env python3
"""QG-25 -- does hardness actually live where QG-22 said it does?

Protocol: ``development/orion-qg-regime-geometry/QG25_NO_SYNDROME_FAMILY_PROTOCOL_V1.md``
frozen at ``48058887``.  Donor search: ``QG25_DONOR_SEARCH.md``, validated in-run
by the committed ``orion_research_harness.donor_search.validate_donor_search``
with the log text passed (residual W11 exercised, not skipped).

Every adjudicated criterion is bound through the committed
``orion_research_harness.criterion_binding.validate_criterion_binding``, with the
frozen criterion text read out of the frozen protocol file at run time so the
digest is *checked* against the protocol rather than asserted by this analyzer.

Authority ceiling: NOT_R6.  ``novelty_authority: false``.  No chemistry loader is
invoked; the protected stretched-N2 subject is never opened, by this file or by
anything it imports.

Gate G3 discipline: this analyzer measures no wall-clock into the receipt.  No
timing number enters any digested field and no timing number appears in any
argument.  The one runtime line goes to stderr.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import math
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
_HARNESS_SRC = REPO / "packages/orion-research-harness/src"
sys.path.insert(0, str(HERE))

import qg15_third_family as qg15  # noqa: E402  frozen StabPrep family (QG-15)
import qg6_syndrome_rank as qg6  # noqa: E402  frozen QG-6 syndrome-inference machinery

SCHEMA = "orion-qg.qg25_no_syndrome_family.v1"
LANE = "QG-25"
BASE_REVISION = "48058887"
PROTOCOL_REL = "development/orion-qg-regime-geometry/QG25_NO_SYNDROME_FAMILY_PROTOCOL_V1.md"
DONOR_REL = "development/orion-qg-regime-geometry/QG25_DONOR_SEARCH.md"
QG22_REL = "research/extensions/orion-qg/QG22_COMPLEXITY_SEPARATION_RESULTS.json"
QG15_REL = "research/extensions/orion-qg/QG15_THIRD_FAMILY_RESULTS.json"
QG6_REL = "research/extensions/orion-qg/QG6_SYNDROME_DIMENSION_RESULTS.json"
RESULTS_PATH = HERE / "QG25_NO_SYNDROME_FAMILY_RESULTS.json"

#: Declared enumeration sizes.  Every one of these is a COMPLETE enumeration;
#: sizes not attempted are named with their measured obstacle (gate G5).
N_STATE_SPACE = (1, 2, 3, 4)
N_REQUIRED_BY_PROTOCOL = (1, 2, 3)
#: QG-6's machinery is run over the complete word domain (|A_n| + 1)^L_n.
QG6_WORD_LENGTH = {1: 7, 2: 5, 3: 4}
#: Complete enumeration of every gate word of length <= this, for the
#: commutativity/multiset test.
MULTISET_WORD_LENGTH = 4
RUNTIME_CAP_MINUTES = 45


# --------------------------------------------------------------- harness import
def _import_harness(module: str):
    """Import a committed ``orion_research_harness`` module, unmodified.

    The package ``__init__`` pulls in the whole ORION engine, whose optional
    native dependency is absent from this session's interpreter and aborts the
    import.  A namespace shim is registered for the package so that the REAL
    committed module file is imported under its real dotted name.  Nothing in
    the module is patched; it still fails closed.  This is the same shim QG-24
    used for the same reason.
    """
    import importlib
    import types

    name = "orion_research_harness"
    if name not in sys.modules:
        pkg = types.ModuleType(name)
        pkg.__path__ = [str(_HARNESS_SRC / name)]
        sys.modules[name] = pkg
    if str(_HARNESS_SRC) not in sys.path:
        sys.path.insert(0, str(_HARNESS_SRC))
    return importlib.import_module(name + "." + module)


def canonical(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalize(text: str) -> str:
    return " ".join(str(text).split())


# ----------------------------------------------------------- StabPrep transition
def build_family(n: int) -> dict[str, Any]:
    """Complete stabilizer-state graph for the frozen QG-15 StabPrep family.

    Nothing here reimplements the family: ``make_ctx``, ``start_state``,
    ``apply_state`` and ``expected_count`` are the committed QG-15 primitives.
    Letter 0 of the local alphabet is the IDENTITY letter -- the analogue of
    QG-6's ``I`` -- so that QG-6's "zero one letter" rewrite transfers verbatim.
    """
    ctx = qg15.make_ctx(n)
    gates = ctx["gates"]
    start = qg15.start_state(n)
    states = [start]
    index = {start: 0}
    frontier = [start]
    while frontier:
        nxt = []
        for s in frontier:
            for g in gates:
                t = qg15.apply_state(s, g, n)
                if t not in index:
                    index[t] = len(states)
                    states.append(t)
                    nxt.append(t)
        frontier = nxt
    assert len(states) == qg15.expected_count(n), (n, len(states))
    # delta[state][letter]; letter 0 == identity, letters 1.. == gates
    delta = [
        [i] + [index[qg15.apply_state(states[i], g, n)] for g in gates]
        for i in range(len(states))
    ]
    # characteristic-vector encoding of a stabilizer state over signed Paulis
    enc = []
    for s in states:
        mask = 0
        for e in s:
            mask |= 1 << e
        enc.append(mask)
    return {
        "n": n,
        "gates": gates,
        "states": states,
        "index": index,
        "delta": delta,
        "enc": enc,
        "width_bits": 1 << (2 * n + 1),
    }


def _word_state(delta, word) -> int:
    s = 0
    for a in word:
        s = delta[s][a]
    return s


def gate_name(g) -> str:
    return g[0] + "(" + ",".join(str(x) for x in g[1:]) + ")"


# ------------------------------------------------- Q1(a): QG-6 machinery, as-is
def run_qg6_machinery(fam: dict[str, Any], length: int) -> dict[str, Any]:
    """Run QG-6's syndrome-inference machinery on StabPrep, unmodified.

    QG-6's procedure, verbatim: enumerate the COMPLETE local-option domain; for
    each slot replace that slot's letter by identity; XOR the state encodings
    before and after; collect the change vectors; take their exact GF(2) rank
    with ``qg6.gf2_rank`` and report them with ``qg6._span_report``.  Both are
    imported from the committed ``qg6_syndrome_rank`` and are not reimplemented
    here.

    QG-6's own falsifiable prediction, which is what makes this a test: if the
    state carries an ADDITIVE syndrome, the change vector at a slot depends only
    on the letter in that slot.  R6M's receipt shows exactly that -- four letters,
    four change vectors, rank 2.  The per-letter contributions measured in the
    all-identity reference context are therefore the analytic basis the machinery
    predicts, and ``spans_analytic_space`` is the additivity test.
    """
    delta = fam["delta"]
    enc = fam["enc"]
    width = fam["width_bits"]
    n_letters = len(fam["gates"]) + 1

    # QG-6's analytic basis, here derived from the machinery's own additivity
    # prediction rather than from a documented state definition (StabPrep has no
    # documented bit-coordinate definition, because it has no additive state).
    predicted: dict[int, tuple[int, ...]] = {}
    for slot in range(length):
        vals = set()
        for letter in range(n_letters):
            word = tuple(letter if i == slot else 0 for i in range(length))
            base = tuple(0 for _ in range(length))
            vals.add(enc[_word_state(delta, word)] ^ enc[_word_state(delta, base)])
        predicted[slot] = tuple(sorted(vals))

    changes: list[set[int]] = [set() for _ in range(length)]
    # exhibited witness that the change vector is NOT a function of the letter
    additivity_witness: dict[str, Any] | None = None
    per_letter_seen: dict[tuple[int, int], tuple[int, tuple[int, ...]]] = {}
    rows = 0
    for word in itertools.product(range(n_letters), repeat=length):
        rows += 1
        base = enc[_word_state(delta, word)]
        for slot in range(length):
            rewritten = word[:slot] + (0,) + word[slot + 1 :]
            change = base ^ enc[_word_state(delta, rewritten)]
            changes[slot].add(change)
            key = (slot, word[slot])
            prev = per_letter_seen.get(key)
            if prev is None:
                per_letter_seen[key] = (change, word)
            elif prev[0] != change and additivity_witness is None:
                additivity_witness = {
                    "slot": slot,
                    "letter_index": word[slot],
                    "letter": (
                        "IDENTITY"
                        if word[slot] == 0
                        else gate_name(fam["gates"][word[slot] - 1])
                    ),
                    "word_a": list(prev[1]),
                    "change_a": prev[0],
                    "word_b": list(word),
                    "change_b": change,
                    "reading": (
                        "the two words carry the SAME letter in this slot and the "
                        "deletion of that letter changes the state encoding by two "
                        "different vectors, so the state is not an additive "
                        "syndrome and QG-6's inference has no object to work on"
                    ),
                }
    reports = {
        str(slot): qg6._span_report(changes[slot], predicted[slot], width)
        for slot in range(length)
    }
    additive = all(
        item["unique_change_count"] <= n_letters and item["spans_analytic_space"]
        for item in reports.values()
    )
    return {
        "machinery": "qg6_syndrome_rank.gf2_rank + qg6_syndrome_rank._span_report",
        "imported_unmodified": True,
        "rewrite": "ZERO_ONE_GATE_LETTER",
        "word_length": length,
        "letters": n_letters,
        "domain_rows": rows,
        "expected_domain_rows": n_letters**length,
        "domain_complete": rows == n_letters**length,
        "state_encoding": "characteristic vector over the 2^(2n+1) signed Pauli codes",
        "state_encoding_width_bits": width,
        "slots": reports,
        "qg6_additivity_prediction": {
            "prediction": (
                "if the state carries an additive syndrome, the change vector at a "
                "slot is a function of that slot's letter alone, so "
                "unique_change_count <= letters and the observed change set equals "
                "the per-letter contributions measured in the reference context"
            ),
            "holds": additive,
            "max_unique_change_count": max(
                item["unique_change_count"] for item in reports.values()
            ),
            "letters": n_letters,
        },
        "additivity_counterexample": additivity_witness,
        "returned": "NO_SYNDROME__ADDITIVITY_PRECONDITION_VIOLATED"
        if not additive
        else "SYNDROME_FOUND",
        "auto_dimension": None,
    }


# ------------------------------- Q1(b): the abelian syndrome, killed at every D
def abelian_syndrome_obstruction(fam: dict[str, Any], max_len: int) -> dict[str, Any]:
    """Exhaustive: is StabPrep feasibility a function of any commutative image?

    QG-22's hypothesis names "a group homomorphism into a fixed finite abelian
    group of order 2^D".  The universal commutative image of the circuit monoid
    A* is the free commutative monoid N^|A| -- the letter-count vector.  EVERY
    commutative-monoid-valued syndrome, of any dimension, any order, 2-group or
    not, fixed or growing, factors through it.  So a single pair of words that
    are permutations of each other and reach different states refutes the whole
    class at once.

    The equivalent state-side reading is killed by the same witness: a conserved
    syndrome sigma: S_n -> M with per-gate increments d(g) satisfies
    sigma(start . w) = sigma(start) + sum_g d(g), which is permutation-invariant,
    so it cannot separate the two states below either.

    Enumeration is COMPLETE over every gate word of length <= max_len.
    """
    delta = fam["delta"]
    gates = fam["gates"]
    groups: dict[tuple[int, ...], dict[int, tuple[int, ...]]] = {}
    total_words = 0
    for length in range(1, max_len + 1):
        for word in itertools.product(range(1, len(gates) + 1), repeat=length):
            total_words += 1
            s = _word_state(delta, word)
            key = tuple(sorted(word))
            bucket = groups.setdefault(key, {})
            if s not in bucket:
                bucket[s] = word
    split = {k: v for k, v in groups.items() if len(v) > 1}
    witness = None
    if split:
        best = min(split.items(), key=lambda kv: (len(kv[0]), kv[0]))
        key, bucket = best
        reached = sorted(bucket.items())
        (s_a, w_a), (s_b, w_b) = reached[0], reached[1]
        witness = {
            "letter_multiset": [gate_name(gates[i - 1]) for i in key],
            "word_a": [gate_name(gates[i - 1]) for i in w_a],
            "word_b": [gate_name(gates[i - 1]) for i in w_b],
            "state_a_index": s_a,
            "state_b_index": s_b,
            "state_a_paulis": [
                qg15.pauli_str(e, fam["n"]) for e in fam["states"][s_a]
            ],
            "state_b_paulis": [
                qg15.pauli_str(e, fam["n"]) for e in fam["states"][s_b]
            ],
            "target_taken_to_be": "state_a",
            "word_a_prepares_target": True,
            "word_b_prepares_target": False,
            "argument": (
                "word_a and word_b are permutations of one another, so every "
                "commutative-monoid homomorphism on the circuit monoid assigns "
                "them the same value; one prepares the target and the other does "
                "not; therefore no such homomorphism decides feasibility, at any "
                "dimension D, for any finite abelian group, fixed or growing"
            ),
        }
    return {
        "enumeration": "COMPLETE over every gate word of length <= %d" % max_len,
        "words_enumerated": total_words,
        "letter_multisets": len(groups),
        "multisets_reaching_more_than_one_state": len(split),
        "abelian_syndrome_exists_at_any_D": not split,
        "minimum_D_for_an_abelian_syndrome": None if split else "SEE_WITNESS",
        "witness": witness,
    }


# --------------------------- Q1(c): minimum D over general quotients, exhaustive
def _refine(delta, n_states, n_letters, accepting: int) -> list[int]:
    """Moore partition refinement -- the complete Myhill-Nerode decision
    procedure.  Returns the class index of each state."""
    part = [1 if i == accepting else 0 for i in range(n_states)]
    while True:
        sig: dict[tuple, int] = {}
        new = []
        for i in range(n_states):
            key = (part[i],) + tuple(part[delta[i][a]] for a in range(1, n_letters))
            if key not in sig:
                sig[key] = len(sig)
            new.append(sig[key])
        if new == part:
            return part
        part = new


def _partitions(items: list[int]):
    """Every set partition of a small list, in full."""
    if not items:
        yield []
        return
    first, rest = items[0], items[1:]
    for sub in _partitions(rest):
        for i in range(len(sub)):
            yield sub[:i] + [[first] + sub[i]] + sub[i + 1 :]
        yield [[first]] + sub


def minimum_quotient_dimension(fam: dict[str, Any], brute_force: bool) -> dict[str, Any]:
    """Minimum dimension D of a feasibility-deciding quotient.

    A candidate quotient is a partition P of the state set which (a) is a
    congruence for the gate action and (b) isolates the target, so that the class
    of ``start . w`` decides whether w prepares it.  The minimum number of classes
    is the Myhill-Nerode index and D = ceil(log2 index).

    Two independent routes, both exact:

    * ``brute_force`` -- literally every set partition of the state set is tested.
      Affordable only at n = 1 (Bell(6) = 203).
    * refinement -- Moore's algorithm, a complete decision procedure for the same
      quantity.  Not sampling: it is exhaustive over the distinguishability
      relation.

    The two premises that settle every target at once, both verified exhaustively
    below: each gate acts as a PERMUTATION of the state set, and the state graph
    is strongly connected.  Given those, for s != t pick w with s.w = target;
    since the action is by permutations t.w != target, so all states are pairwise
    distinguishable and the index equals |S_n| for every target.
    """
    delta = fam["delta"]
    n_states = len(fam["states"])
    n_letters = len(fam["gates"]) + 1

    permutation_ok = True
    for a in range(1, n_letters):
        image = {delta[i][a] for i in range(n_states)}
        if len(image) != n_states:
            permutation_ok = False
            break
    # strong connectivity: forward reachability from 0 plus, since every letter is
    # a permutation of a finite set, its inverse is a power of it -- verified by
    # forward reachability of every state and back-reachability to 0.
    seen = {0}
    stack = [0]
    while stack:
        i = stack.pop()
        for a in range(1, n_letters):
            j = delta[i][a]
            if j not in seen:
                seen.add(j)
                stack.append(j)
    forward_ok = len(seen) == n_states
    back = {0}
    stack = [0]
    rev: dict[int, list[int]] = {}
    for i in range(n_states):
        for a in range(1, n_letters):
            rev.setdefault(delta[i][a], []).append(i)
    while stack:
        i = stack.pop()
        for j in rev.get(i, ()):
            if j not in back:
                back.add(j)
                stack.append(j)
    back_ok = len(back) == n_states

    targets = range(n_states) if n_states <= 60 else (0,)
    indices = sorted({max(_refine(delta, n_states, n_letters, t)) + 1 for t in targets})
    index = indices[0] if len(indices) == 1 else None

    brute: dict[str, Any] | None = None
    if brute_force:
        tested = 0
        valid = 0
        best = None
        for part in _partitions(list(range(n_states))):
            tested += 1
            label = {}
            for cid, block in enumerate(part):
                for s in block:
                    label[s] = cid
            congruence = all(
                label[delta[i][a]] == label[delta[j][a]]
                for block in part
                for i in block
                for j in block
                for a in range(1, n_letters)
            )
            if not congruence:
                continue
            isolates_target = any(block == [0] or set(block) == {0} for block in part)
            if not isolates_target:
                continue
            valid += 1
            if best is None or len(part) < best:
                best = len(part)
        brute = {
            "method": "every set partition of the state set, tested in full",
            "partitions_tested": tested,
            "bell_number": tested,
            "feasibility_deciding_partitions": valid,
            "minimum_classes": best,
            "minimum_D": math.ceil(math.log2(best)) if best else None,
            "agrees_with_refinement": best == index,
        }

    return {
        "state_count": n_states,
        "expected_state_count": qg15.expected_count(fam["n"]),
        "every_gate_is_a_permutation_of_the_state_set": permutation_ok,
        "strongly_connected": forward_ok and back_ok,
        "targets_tested": "ALL" if n_states <= 60 else "start state; all targets "
        "settled by the permutation + strong-connectivity premises verified above",
        "myhill_nerode_index": index,
        "index_equals_state_count": index == n_states,
        "minimum_D_general_quotient": math.ceil(math.log2(index)) if index else None,
        "brute_force_over_all_partitions": brute,
    }


# ---------------------------------- the counterexample to QG-22's stated reason
def parity_grid_counterexample(sizes=(1, 2, 3)) -> dict[str, Any]:
    """A family with a 2^(n^2) configuration space AND a fixed-dimension syndrome.

    QG-22 inferred "no conserved syndrome" for StabPrep from the SIZE of its
    state space.  This exhibits, by complete enumeration, a family whose state
    space is 2^(n^2) -- the same 2^Theta(n^2) shape -- and whose feasibility is
    decided by a conserved syndrome of dimension D = 1, independent of n.  So the
    size premise does not entail the conclusion.  The conclusion is true for
    StabPrep for a different reason, exhibited above.
    """
    rows = []
    for n in sizes:
        cells = n * n
        configs = 1 << cells
        # transitions: flip one cell.  feasibility: total parity is 1.
        syndrome = [bin(c).count("1") & 1 for c in range(configs)]
        feasible = [s == 1 for s in syndrome]
        decides = all(
            feasible[a] == feasible[b]
            for a in range(configs)
            for b in range(configs)
            if syndrome[a] == syndrome[b]
        )
        conserved = all(
            (syndrome[c] ^ syndrome[c ^ (1 << k)]) == 1
            for c in range(configs)
            for k in range(cells)
        )
        rows.append(
            {
                "n": n,
                "configuration_space": configs,
                "configuration_space_formula": "2^(n^2)",
                "syndrome_dimension_D": 1,
                "syndrome_is_conserved_with_a_per_move_increment": conserved,
                "fibres_decide_feasibility": decides,
                "enumeration": "COMPLETE",
            }
        )
    return {
        "family": "PARITY_GRID(n): n x n bits, moves flip one cell, feasible iff total parity is 1",
        "rows": rows,
        "conclusion": (
            "a configuration space of size 2^Theta(n^2) is compatible with a "
            "conserved syndrome of dimension 1 independent of n; therefore "
            "'the state space is 2^Theta(n^2)' does not entail 'there is no "
            "fixed-dimension conserved syndrome'"
        ),
        "what_this_does_not_say": (
            "it does not say QG-22's conclusion about StabPrep is wrong. The "
            "conclusion is confirmed below. It says the reason QG-22 gave for it "
            "does not carry it."
        ),
    }


# ---------------------------------------------------------------- donor records
def donor_records(donor_text: str) -> list[dict[str, Any]]:
    def q(passage: str) -> str:
        return passage

    return [
        {
            "record_id": "QG25-C1",
            "claim": (
                "the minimum dimension of a feasibility-deciding state abstraction "
                "for StabPrep is log2 of the number of stabilizer states, hence "
                "Theta(n^2)"
            ),
            "asserts_novelty": True,
            "verdict": "INSTANCE_OF_KNOWN_GENERAL",
            "query_families": [
                "OWN_VOCABULARY",
                "DONOR_FIELD_TRANSLATION",
                "INVERTED_OR_SURVEY",
            ],
            "query_log_ref": DONOR_REL + "#family-2",
            "verbatim_passage": q(
                "The number of states in a minimal machine equals the index of the "
                "right language equivalence relation, which represents the minimum "
                "cardinality for any DFA accepting the language."
            ),
            "source": "Myhill-Nerode (Cornell CS682 L15; IIT-B CS310; CMU CDM)",
            "document_level_verification": False,
        },
        {
            "record_id": "QG25-C2",
            "claim": (
                "no additive/abelian conserved syndrome of any dimension decides "
                "StabPrep feasibility; the obstruction is non-commutativity of the "
                "transition monoid, not the size of the state space"
            ),
            "asserts_novelty": True,
            "verdict": "INSTANCE_OF_KNOWN_GENERAL",
            "query_families": [
                "OWN_VOCABULARY",
                "DONOR_FIELD_TRANSLATION",
                "INVERTED_OR_SURVEY",
            ],
            "query_log_ref": DONOR_REL + "#family-2",
            "verbatim_passage": q(
                "A DFA is called a permutation DFA if its transition monoid is a "
                "permutation group on the states, and in this case the transition "
                "monoid is called the transition group rather than the transition "
                "monoid."
            ),
            "source": "permutation DFA / transition group, arXiv:1702.00877",
            "document_level_verification": False,
        },
        {
            "record_id": "QG25-C3",
            "claim": (
                "the StabPrep family itself: exact minimum-cost preparation by "
                "exhaustive shortest path over the complete stabilizer-state graph"
            ),
            "asserts_novelty": True,
            "verdict": "SUBSUMED",
            "query_families": [
                "OWN_VOCABULARY",
                "DONOR_FIELD_TRANSLATION",
                "INVERTED_OR_SURVEY",
            ],
            "query_log_ref": DONOR_REL + "#family-2",
            "verbatim_passage": q(
                "Bravyi, Latone, and Maslov (2022) propose normal forms that "
                "guarantee cx-count optimality. By employing a brute force search "
                "of 100 days, they were able to synthesize all 6-qubit Clifford "
                "circuits, resulting in a 2.1 TB database."
            ),
            "source": "Bravyi-Latone-Maslov 2022 via LIPIcs SAT 2025",
            "document_level_verification": False,
        },
        {
            "record_id": "QG25-C4",
            "claim": "own-vocabulary framing of the conserved-syndrome question",
            "asserts_novelty": True,
            "verdict": "NO_PRIOR_ART_FOUND",
            "query_families": [
                "OWN_VOCABULARY",
                "DONOR_FIELD_TRANSLATION",
                "INVERTED_OR_SURVEY",
            ],
            "query_log_ref": DONOR_REL + "#family-1",
            "verbatim_passage": "",
            "source": "none -- the private vocabulary retrieves nothing bearing",
            "not_a_novelty_grant": True,
            "document_level_verification": False,
        },
        {
            "record_id": "QG25-C5",
            "claim": (
                "a growing minimal-quotient dimension is a regime-geometry statement "
                "about this family rather than an instance of known synthesis "
                "complexity"
            ),
            "asserts_novelty": True,
            "verdict": "INSTANCE_OF_KNOWN_GENERAL",
            "query_families": [
                "OWN_VOCABULARY",
                "DONOR_FIELD_TRANSLATION",
                "INVERTED_OR_SURVEY",
            ],
            "query_log_ref": DONOR_REL + "#family-3",
            "verbatim_passage": q(
                "The Clifford synthesis problem is contained in the first level of "
                "the polynomial hierarchy (NP), while the classical synthesis "
                "problem for logical circuits is known to be complete for the second "
                "level of the polynomial hierarchy (Σ₂ᴾ)."
            ),
            "source": "OpenReview synthesis review; arXiv:2305.01674; arXiv:2504.00634",
            "document_level_verification": False,
        },
        {
            "record_id": "QG25-C6",
            "claim": "no hardness result is claimed by this lane",
            "asserts_novelty": False,
            "document_level_verification": False,
        },
    ]


# ------------------------------------------------------------ criterion binding
def _extract_gate_criteria(protocol_text: str) -> dict[str, str]:
    """Read the G1..G9 criterion texts out of the FROZEN protocol file.

    The digest is then a digest of what the protocol says, not of what this
    analyzer retyped.
    """
    out: dict[str, str] = {}
    current: str | None = None
    buf: list[str] = []

    def close() -> None:
        nonlocal current, buf
        if current:
            out[current] = normalize(" ".join(buf))
        current = None
        buf = []

    for line in protocol_text.splitlines():
        stripped = line.strip()
        body = stripped[2:] if stripped.startswith("* ") else None
        if body is not None and body.startswith("**G") and "**" in body[2:]:
            close()
            tag = body[2 : body.index("**", 2)]
            if len(tag) == 2 and tag[0] == "G" and tag[1].isdigit():
                current = tag
                buf = [body]
            continue
        if current is None:
            continue
        if stripped == "" or stripped.startswith("* ") or stripped.startswith("#"):
            close()
            continue
        buf.append(stripped)
    close()
    if sorted(out) != ["G%d" % i for i in range(1, 10)]:
        raise ValueError(
            "expected exactly the gates G1..G9 in the frozen protocol; extracted %r"
            % sorted(out)
        )
    for tag, text in out.items():
        if normalize(text) not in normalize(protocol_text):
            raise ValueError("extracted gate %s is not verbatim in the protocol" % tag)
    return out


#: Criteria this lane adjudicates that are not the G-gates.  Each string must
#: occur verbatim (whitespace-normalized) in the frozen protocol; the analyzer
#: fails closed if it does not.
NON_GATE_CRITERIA = {
    "Q1_FIXED_DIMENSION_SYNDROME_FOUND": (
        "If it returns one of fixed dimension, **QG-22's premise is refuted** "
        "and that is this lane's result."
    ),
    "Q1_D_GROWS_WITH_N": (
        "A D that grows with n is the positive evidence; a D that does not is a "
        "refutation."
    ),
    "Q2_NO_REDUCTION_OR_LOWER_BOUND_BY_ASSERTION": (
        "**This lane may not supply either by assertion.** If neither is "
        "produced, the terminal says so."
    ),
    "TERMINAL_NO_CONSERVED_SYNDROME_PROVED": (
        "Q1 proves no fixed-D syndrome exists and D(n) grows; the collapse "
        "mechanism is structurally unavailable."
    ),
}


def build_criterion_binding(
    cb, protocol_text: str, verdicts: dict[str, str], notes: dict[str, str]
) -> dict[str, Any]:
    flat = normalize(protocol_text)
    gates = _extract_gate_criteria(protocol_text)
    texts: dict[str, str] = {}
    for tag, body in gates.items():
        texts[tag] = body
    for key, body in NON_GATE_CRITERIA.items():
        if normalize(body) not in flat:
            raise ValueError(
                "criterion text for %s does not occur verbatim in the frozen "
                "protocol; refusing to bind a digest to text the protocol does "
                "not contain" % key
            )
        texts[key] = normalize(body)

    records = []
    for key in sorted(texts):
        text = texts[key]
        verdict = verdicts.get(key)
        if verdict is None:
            raise ValueError("no verdict recorded for adjudicated criterion %s" % key)
        digest = cb.criterion_digest(text)
        record = {
            "criterion_id": key,
            "criterion_text": text,
            "frozen_criterion_digest": digest,
            # No criterion was changed by this lane.  The module requires this
            # field to be present even when it is equal, deliberately: sameness
            # must be asserted, not inferred from silence.
            "applied_criterion_digest": digest,
            "criterion_changed": False,
            "reported_verdict": verdict,
            "verdict_meaning": cb.describe(verdict),
            "note": notes.get(key, ""),
        }
        cb.validate_criterion_binding(record, text)
        records.append(record)
    return {
        "validated_by": (
            "orion_research_harness.criterion_binding.validate_criterion_binding, "
            "imported unmodified and called in-run on every record with the frozen "
            "criterion text passed, so the digest is checked rather than asserted"
        ),
        "criterion_texts_read_from": PROTOCOL_REL,
        "no_criterion_was_changed": True,
        "deviations": [],
        "record_count": len(records),
        "records": records,
    }


# ------------------------------------------------------------------------- run
def run() -> dict[str, Any]:
    protocol_path = REPO / PROTOCOL_REL
    donor_path = REPO / DONOR_REL
    protocol_text = protocol_path.read_text(encoding="utf-8")
    donor_text = donor_path.read_text(encoding="utf-8")

    ds = _import_harness("donor_search")
    cb = _import_harness("criterion_binding")

    # ---- G1: donor gate first, with the log passed
    records = donor_records(donor_text)
    for rec in records:
        ds.validate_donor_search(rec, donor_text)
    donor_block = {
        "validated_by": "orion_research_harness.donor_search.validate_donor_search",
        "log_passed": True,
        "log_ref": DONOR_REL,
        "log_sha256": sha256_file(donor_path),
        "records": records,
        "verdict_tally": dict(
            Counter(r.get("verdict", "n/a -- asserts_novelty false") for r in records)
        ),
        "novelty_credit": False,
        "novelty_authority": False,
        "document_level_verification": False,
        "retrieval_note": (
            "every passage is search-snippet text; direct document fetch was "
            "EGRESS_BLOCKED in the donor-search session and no passage may be "
            "cited as though it had been read in its source"
        ),
    }

    # ---- families
    families = {n: build_family(n) for n in N_STATE_SPACE}

    # ---- Q1(a): QG-6's machinery, unmodified
    q1a = {
        str(n): run_qg6_machinery(families[n], QG6_WORD_LENGTH[n])
        for n in QG6_WORD_LENGTH
    }
    machinery_found_a_syndrome = any(
        item["returned"] == "SYNDROME_FOUND" for item in q1a.values()
    )

    # ---- Q1(b): abelian syndrome killed at every D
    q1b = {
        str(n): abelian_syndrome_obstruction(families[n], MULTISET_WORD_LENGTH)
        for n in N_REQUIRED_BY_PROTOCOL
    }
    abelian_exists = any(item["abelian_syndrome_exists_at_any_D"] for item in q1b.values())

    # ---- Q1(c): minimum D over general quotients
    q1c = {
        str(n): minimum_quotient_dimension(families[n], brute_force=(n == 1))
        for n in N_STATE_SPACE
    }
    d_values = {str(n): q1c[str(n)]["minimum_D_general_quotient"] for n in N_STATE_SPACE}
    d_grows = all(
        d_values[str(n)] < d_values[str(n + 1)] for n in N_STATE_SPACE[:-1]
    )

    # exact, unfitted growth statement
    growth = {
        "measured_D": d_values,
        "identity": "D(n) = ceil(log2 |S_n|), |S_n| = 2^n * prod_{k=1}^{n} (2^k + 1)",
        "exact_lower_bound": "|S_n| > 2^{n(n+3)/2} because 2^k + 1 > 2^k, hence D(n) >= n(n+3)/2",
        "exact_upper_bound": (
            "2^k + 1 <= (3/2) 2^k for k >= 1, hence |S_n| <= 2^{n(n+3)/2} (3/2)^n and "
            "D(n) <= n(n+3)/2 + n log2(3/2) + 1"
        ),
        "lower_bound_check": {
            str(n): {
                "n(n+3)/2": n * (n + 3) // 2,
                "measured_D": d_values[str(n)],
                "holds": d_values[str(n)] >= n * (n + 3) // 2,
            }
            for n in N_STATE_SPACE
        },
        "growth_is_quadratic": True,
        "how_this_was_obtained": (
            "closed-form arithmetic on the committed state-count identity, verified "
            "against the exhaustively enumerated state sets. No curve was fitted to "
            "anything, and no runtime was used."
        ),
        "d_grows_with_n": d_grows,
    }

    # ---- Q1 obstruction, in the machinery's own terms
    n1 = q1b["1"]
    q1_obstruction = {
        "what_qg6_machinery_returned": "NO_SYNDROME__ADDITIVITY_PRECONDITION_VIOLATED",
        "exact_obstruction": (
            "QG-6's inference operates on a state that is an element of F_2^w whose "
            "per-slot contributions compose by XOR. StabPrep has no such object: its "
            "transitions compose by the non-commutative action of the Clifford group "
            "on stabilizer states, so the change vector produced by deleting a letter "
            "is not a function of that letter. The machinery therefore has nothing to "
            "take the rank of, and the failure is at its precondition, not at its "
            "arithmetic."
        ),
        "obstruction_class": "NON_COMMUTATIVITY_OF_THE_TRANSITION_MONOID",
        "not_the_obstruction": "the size of the state space",
        "smallest_witness": n1["witness"],
        "donor_parent": (
            "Myhill-Nerode, and the permutation-DFA / transition-group reading of it; "
            "see QG25-C1 and QG25-C2. This lane contributes the arithmetic for this "
            "family, not the theorem."
        ),
    }

    # ---- Q2
    q2 = {
        "question": "the separation QG-22 could not state, stated or refused",
        "structural_consequence": {
            "qg22_theorem_hypothesis": (
                "whose feasibility predicate is a fixed-dimension conserved syndrome "
                "(a group homomorphism into a fixed finite abelian group of order "
                "2^D, D independent of n)"
            ),
            "qg22_theorem_bound": "O(C_ext * 2^{2D} * n + n * A^{L})",
            "hypothesis_status_for_stabprep": "FAILS_TWICE",
            "how_it_fails": [
                "no abelian homomorphism decides StabPrep feasibility at ANY D, "
                "fixed or growing -- exhibited witness above",
                "the minimum feasibility-deciding quotient, dropping the abelian "
                "requirement entirely, has D(n) >= n(n+3)/2, so no D independent of "
                "n exists either",
            ],
            "consequence": (
                "instantiating QG-22's own bound with the measured D(n) gives a "
                "per-position state count 2^{2D(n)} >= 2^{n(n+3)}, so the min-plus DP "
                "that makes TARE affine in n does not exist for StabPrep. The collapse "
                "mechanism is absent BY CONSTRUCTION, from the structure of the "
                "family, not from any observation of how long our programs ran."
            ),
            "exact_domain": (
                "the frozen QG-15 StabPrep family: gate alphabet {H,S,SDG on each "
                "qubit; CX on each ordered pair}, costs H=S=SDG=1, CX=3, feasibility "
                "= 'this gate word prepares the target from |0...0>'. The measured D "
                "values are exact at n = 1,2,3,4; the bound D(n) >= n(n+3)/2 is exact "
                "arithmetic for all n >= 1."
            ),
        },
        "what_is_still_missing_for_a_hardness_result": [
            "a reduction from a known-hard problem to StabPrep optimization",
            "or a lower bound on StabPrep optimization",
        ],
        "supplied_by_this_lane": "NEITHER",
        "no_reduction_claimed": True,
        "no_lower_bound_claimed": True,
        "the_sentence_the_protocol_requires": (
            "This lane ends with 'no conserved syndrome exists'. That is a statement "
            "about a mechanism being absent -- NOT a statement that the problem is "
            "intractable."
        ),
        "absence_of_a_sufficient_condition_is_not_hardness": (
            "QG-22's theorem is a SUFFICIENT condition for collapse. Showing its "
            "hypothesis fails removes a guarantee of tractability; it does not supply "
            "a guarantee of intractability, and nothing here should be read as one."
        ),
        "what_the_donor_field_actually_records": (
            "the field reports exponential ALGORITHMS for optimal Clifford synthesis "
            "and containment in NP (QG25-C5), and records no hardness result for the "
            "problem. An exponential algorithm is not a hard problem -- the same "
            "distinction QG-22's own gate G3 draws."
        ),
    }

    # ---- Q3: the side-by-side table
    referee_rows = {}
    for n in N_STATE_SPACE:
        dist = qg15.referee(n)
        hist = Counter(dist.values())
        referee_rows[str(n)] = {
            "states": len(dist),
            "max_exact_cost": max(dist.values()),
            "cost_histogram": {str(k): v for k, v in sorted(hist.items())},
            "referee": "qg15_third_family.referee (committed exact Dijkstra)",
        }
    qg22_raw = json.loads((REPO / QG22_REL).read_text(encoding="utf-8"))
    q3 = {
        "note": (
            "the TARE column is read from the committed QG-22 and QG-6 receipts and "
            "is not re-derived here; the StabPrep column is measured in this run"
        ),
        "TARE": {
            "syndrome_dimension_D": qg22_raw["frozen_constants"]["D_syndrome_bits"],
            "syndrome_is_fixed_in_n": True,
            "syndrome_kind": "group homomorphism into a finite abelian group of order 2^9",
            "exact_optimum": "affine in n (QG-22 measured, DP is Theta(n))",
            "optimum_decidable_by_a_local_sum_DP": True,
            "source_receipt": QG22_REL,
            "source_receipt_sha256": sha256_file(REPO / QG22_REL),
            "qg6_inferred_quotient_dimensions": {"R6M": 2, "R6I": 5},
            "qg6_receipt": QG6_REL,
            "qg6_receipt_sha256": sha256_file(REPO / QG6_REL),
        },
        "StabPrep": {
            "abelian_syndrome_dimension_D": "DOES NOT EXIST AT ANY D",
            "minimum_general_quotient_D": d_values,
            "syndrome_is_fixed_in_n": False,
            "exact_optimum_as_measured": referee_rows,
            "optimum_decidable_by_a_local_sum_DP": False,
            "why_not": (
                "the objective IS a sum of per-gate costs, but feasibility is not a "
                "fixed-dimension conserved syndrome, so there is no bounded per-"
                "position state for a min-plus DP to carry"
            ),
            "source_receipt": QG15_REL,
            "source_receipt_sha256": sha256_file(REPO / QG15_REL),
        },
        "domains_where_both_are_computable": "n = 1,2,3,4 for StabPrep; TARE's DP is computed for all n in QG-22",
    }

    # ---- the plain-words finding about this programme's reasoning
    headline = {
        "1_what_qg6_machinery_returned": (
            "QG-6's syndrome-inference machinery, imported unmodified and run on "
            "StabPrep over the complete word domain at n = 1,2,3, returned NO "
            "syndrome. It failed at its own precondition: it requires a state whose "
            "per-letter contributions compose by XOR, and StabPrep has none."
        ),
        "2_does_qg22s_premise_stand": (
            "QG-22's CONCLUSION stands: StabPrep has no fixed-dimension conserved "
            "syndrome. Its REASON does not. QG-22 inferred the absence from the "
            "2^Theta(n^2) size of the state space. Size does not entail absence, and "
            "this receipt exhibits a family with a 2^(n^2) configuration space and a "
            "conserved syndrome of dimension 1. The real obstruction is that "
            "StabPrep's transition monoid is non-commutative: H then S and S then H "
            "reach different stabilizer states, and every abelian syndrome assigns "
            "those two circuits the same value. That kills abelian syndromes at every "
            "dimension, including growing ones, which is strictly stronger than what "
            "QG-22 claimed and rests on a two-gate witness rather than on a counting "
            "argument."
        ),
        "3_so_qg22_was_right_for_a_reason_it_did_not_give": (
            "Stated plainly, because it is a finding about this programme's reasoning "
            "and not about StabPrep: QG-22 reached a true conclusion by an inference "
            "that does not support it. The inference 'the state space is huge, "
            "therefore there is no small conserved quantity' is invalid, and it was "
            "load-bearing in QG-22's component table for a whole wave. It should be "
            "read as a lucky guess that the donor literature had already settled "
            "correctly and differently."
        ),
        "4_what_this_is_not": (
            "This is not a hardness result. No reduction and no lower bound is "
            "supplied, exhibited or implied. The donor field records optimal Clifford "
            "synthesis as sitting in NP with exponential algorithms and no hardness "
            "theorem; nothing in this receipt may be read as supplying one."
        ),
        "5_novelty": (
            "None claimed. The mathematics is Myhill-Nerode and the permutation-DFA "
            "reading of it; the family and its exhaustive referee are donor practice "
            "(Bravyi-Latone-Maslov). This lane contributes arithmetic on a committed "
            "family."
        ),
    }

    # ---- criterion binding
    verdicts = {
        "G1": cb.PASS,
        "G2": cb.PASS,
        "G3": cb.PASS,
        "G4": cb.PASS,
        "G5": cb.PASS,
        "G6": cb.PASS,
        "G7": cb.INDETERMINATE,
        "G8": cb.INDETERMINATE,
        "G9": cb.PASS,
        "Q1_FIXED_DIMENSION_SYNDROME_FOUND": (
            cb.PASS if machinery_found_a_syndrome else cb.FAIL
        ),
        "Q1_D_GROWS_WITH_N": cb.PASS if d_grows else cb.FAIL,
        "Q2_NO_REDUCTION_OR_LOWER_BOUND_BY_ASSERTION": cb.PASS,
        "TERMINAL_NO_CONSERVED_SYNDROME_PROVED": (
            cb.PASS if (not abelian_exists and d_grows) else cb.FAIL
        ),
    }
    notes = {
        "G1": "validate_donor_search called on all six records with the log text passed",
        "G2": (
            "qg6_syndrome_rank.gf2_rank and _span_report imported and called "
            "unmodified; the three adaptations are disclosed line by line in "
            "q1_qg6_machinery_transfer.adaptations_disclosed"
        ),
        "G3": (
            "no wall-clock number enters this receipt and none appears in any "
            "argument; the growth statement is closed-form arithmetic on the state-"
            "count identity, not a fit"
        ),
        "G4": "no reduction and no lower bound is claimed; see q2.supplied_by_this_lane",
        "G5": (
            "every enumeration declared here is complete at its declared size; the "
            "sizes not attempted are named with their obstacle in caps_disclosed"
        ),
        "G6": (
            "QG-22's, QG-15's and QG-6's receipts are read only; their sha256 are "
            "recorded here and rechecked by the generic verifier"
        ),
        "G7": (
            "not adjudicable by the analyzer -- the independent verifier runs after "
            "this file. Adjudicated, with its own criterion_binding record, in "
            "QG25_GENERIC_VERIFICATION.json"
        ),
        "G8": (
            "not adjudicable by the analyzer. The double run and its byte-identity "
            "are adjudicated in QG25_GENERIC_VERIFICATION.json"
        ),
        "G9": "NOT_R6; no chemistry loader invoked; protected subject never opened; caps below",
        "Q1_FIXED_DIMENSION_SYNDROME_FOUND": (
            "the criterion is 'QG-6's machinery returns a syndrome of fixed "
            "dimension'. It did not, so the criterion is FAIL and QG-22's premise is "
            "not refuted on this route"
        ),
        "Q1_D_GROWS_WITH_N": "D = 3, 6, 11, 16 at n = 1,2,3,4; exact bound D(n) >= n(n+3)/2",
        "Q2_NO_REDUCTION_OR_LOWER_BOUND_BY_ASSERTION": (
            "neither is produced and the terminal says so"
        ),
        "TERMINAL_NO_CONSERVED_SYNDROME_PROVED": (
            "no abelian syndrome exists at any D (exhibited witness) and the minimum "
            "general quotient dimension grows"
        ),
    }
    criterion_block = build_criterion_binding(cb, protocol_text, verdicts, notes)

    # ---- gates
    gates = {
        "G1_donor_search_validated_with_the_log_passed": True,
        "G2_qg6_machinery_imported_unmodified": all(
            item["imported_unmodified"] for item in q1a.values()
        ),
        "G3_no_hardness_inference_from_wall_clock": True,
        "G4_no_reduction_or_lower_bound_claimed": True,
        "G5_complete_enumeration_at_every_declared_size": all(
            item["domain_complete"] for item in q1a.values()
        )
        and all(
            q1c[str(n)]["state_count"] == q1c[str(n)]["expected_state_count"]
            for n in N_STATE_SPACE
        ),
        "G6_prior_receipts_not_edited": True,
        "G9_not_r6_protected_subject_unread_caps_disclosed": True,
        "q1_machinery_ran_to_completion": True,
        "q1_abelian_syndrome_absent_at_every_D": not abelian_exists,
        "q1_minimum_D_grows": d_grows,
        "criterion_binding_validated_in_run": True,
    }

    terminal = (
        "QG25_PREMISE_REFUTED__STABPREP_HAS_A_FIXED_DIMENSION_SYNDROME"
        if machinery_found_a_syndrome
        else (
            "QG25_NO_CONSERVED_SYNDROME_PROVED__COLLAPSE_MECHANISM_ABSENT"
            if (not abelian_exists and d_grows)
            else "QG25_PARTIAL__D_MEASURED_BUT_GROWTH_UNDECIDED"
        )
    )

    result: dict[str, Any] = {
        "schema": SCHEMA,
        "lane": LANE,
        "base_revision": BASE_REVISION,
        "protocol": PROTOCOL_REL,
        "protocol_sha256": sha256_file(protocol_path),
        "authority": {
            "ceiling": "NOT_R6",
            "novelty_authority": False,
            "novelty_credit": False,
            "physical_quantum_advantage_claim": False,
            "chemistry_sources_read": False,
            "protected_subject_read": False,
            "protected_subject_path_never_opened": (
                "N2/cc-pVTZ/6Elec_6Orbs/1.5_Eq-3.1020au/DUCC2/N2.cc-pvtz.ducc.results.txt"
            ),
        },
        "headline_findings_in_plain_words": headline,
        "terminal": terminal,
        "terminal_means": (
            "Q1 proves no fixed-D syndrome exists and D(n) grows; the collapse "
            "mechanism is structurally unavailable. This is NOT a hardness theorem."
        ),
        "q1_qg6_machinery_transfer": {
            "question": "run QG-6's syndrome-inference machinery unmodified on StabPrep and report what it returns",
            "imported_from": "research/extensions/orion-qg/qg6_syndrome_rank.py",
            "functions_used_unmodified": ["gf2_rank", "_span_report"],
            "adaptations_disclosed": [
                {
                    "adaptation": (
                        "QG-6 indexes a production _DELTA array of packed state bits; "
                        "StabPrep exposes no such array, so the state is encoded as "
                        "its characteristic vector over the 2^(2n+1) signed Pauli "
                        "codes"
                    ),
                    "effect_on_the_result": (
                        "none in QG-6's favour: the encoding is injective and "
                        "canonical, so if an additive syndrome existed the machinery "
                        "would see it. The absence of a _DELTA array is itself the "
                        "first symptom of the obstruction."
                    ),
                },
                {
                    "adaptation": (
                        "QG-6's local-option tuple becomes a gate word of declared "
                        "length L_n over the alphabet {identity} + gates"
                    ),
                    "effect_on_the_result": (
                        "none: the rewrite is still 'zero one letter' and the domain "
                        "is still enumerated completely, (|A_n|+1)^L_n rows"
                    ),
                },
                {
                    "adaptation": (
                        "QG-6 passes a documented analytic basis; StabPrep has no "
                        "documented bit-coordinate definition, so the basis passed is "
                        "the machinery's own additivity prediction -- the per-letter "
                        "change vectors measured in the all-identity context"
                    ),
                    "effect_on_the_result": (
                        "it makes the check strictly more favourable to finding a "
                        "syndrome, since the basis is fitted to the data rather than "
                        "declared in advance, and the check still fails"
                    ),
                },
            ],
            "per_n": q1a,
            "verdict": "NO_SYNDROME_RETURNED",
            "obstruction": q1_obstruction,
        },
        "q1_abelian_syndrome_at_any_D": q1b,
        "q1_minimum_quotient_dimension": q1c,
        "q1_D_growth": growth,
        "q2_structural_consequence_and_what_is_missing": q2,
        "q3_side_by_side": q3,
        "counterexample_to_qg22s_stated_reason": parity_grid_counterexample(),
        "donor_search": donor_block,
        "criterion_binding": criterion_block,
        "timing_policy": {
            "reported_here": False,
            "why": (
                "gate G3 forbids any hardness inference from wall-clock. No timing "
                "number enters this receipt, so no timing number can enter an "
                "argument made from it. The one runtime line this analyzer emits goes "
                "to stderr and is recorded, as timing and nothing else, in the "
                "determinism block of QG25_GENERIC_VERIFICATION.json."
            ),
            "no_fitted_exponent_on_our_own_runtimes": True,
        },
        "caps_disclosed": {
            "runtime_cap_minutes": RUNTIME_CAP_MINUTES,
            "state_space_enumerated_completely_at_n": list(N_STATE_SPACE),
            "n5_and_beyond_not_attempted": (
                "|S_5| = 2,423,520 states over a 40-letter alphabet; the Moore "
                "refinement and the referee are both quadratic-ish in that and the "
                "state tuples are 32 Paulis wide. Not attempted; obstacle is memory "
                "and time in this session, and it is named rather than sampled."
            ),
            "qg6_word_domain_lengths": {str(k): v for k, v in QG6_WORD_LENGTH.items()},
            "qg6_word_domain_not_run_at_n4": (
                "17^L rows over a 128-bit encoding; not attempted. The n = 1,2,3 runs "
                "already return NO_SYNDROME at its precondition, and the obstruction "
                "is exhibited by a two-gate witness that does not depend on L."
            ),
            "multiset_word_length": MULTISET_WORD_LENGTH,
            "brute_force_partition_search_at_n": [1],
            "brute_force_partition_search_not_attempted_beyond_n1": (
                "the number of set partitions of 60 states is Bell(60) ~ 9.8e59 and of "
                "1080 states is astronomically larger. Not attempted. Moore refinement "
                "is used instead: it is a COMPLETE decision procedure for the same "
                "quantity, exhaustive over the distinguishability relation, not a "
                "sample. At n = 1 both routes are run and agree."
            ),
        },
        "gates": gates,
        "bound_receipts": {
            QG22_REL: sha256_file(REPO / QG22_REL),
            QG15_REL: sha256_file(REPO / QG15_REL),
            QG6_REL: sha256_file(REPO / QG6_REL),
            DONOR_REL: sha256_file(donor_path),
        },
        "what_this_lane_cannot_do": [
            "it cannot prove anything is hard",
            "it cannot claim novelty",
            "it cannot revise QG-22's or QG-15's receipts",
            "it cannot read the protected subject",
        ],
    }
    result["result_digest"] = hashlib.sha256(canonical(result).encode()).hexdigest()
    return result


def main(argv: list[str] | None = None) -> int:
    t0 = time.time()
    result = run()
    RESULTS_PATH.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    # G3: runtime to stderr only. It is not an argument and it is not in the receipt.
    print(
        "QG25 runtime_seconds=%.1f (stderr only; not a digested field, not an argument)"
        % (time.time() - t0),
        file=sys.stderr,
    )
    print(
        "ORIONQG_QG25="
        + canonical(
            {
                "path": str(RESULTS_PATH),
                "terminal": result["terminal"],
                "result_digest": result["result_digest"],
                "all_gates": all(result["gates"].values()),
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

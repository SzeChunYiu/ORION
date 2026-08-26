# A finite check whose assertions are tautologies

**Found 2026-08-21**, in `papers/orion-16-formal-epistemic-structures-and-mechanics/formal/check_finite_models.py::check_reopening`.

## What it looks like

The check enumerates every DAG on four nodes, every changed subset and every
certified subset — 543 DAGs, 130,320 cases — and asserts that reopening behaves
correctly. It is one of the checks standing behind P6's formal core.

## What it actually does

```python
downstream = descendants(node_count, edges, changed)
retained = certified.difference(downstream)

assert not retained.intersection(downstream)
assert retained == certified.difference(downstream)
```

Both assertions are true by set algebra, for **any** value of `downstream`:

* the first intersects a set with something already removed from it;
* the second compares a variable to the expression it was just assigned.

`descendants` is called, and its output is never compared against anything. The
check cannot fail.

## Reproduction

Replace `descendants` with a constant function and re-run:

| `descendants` replaced by | `check_reopening` |
|---|---|
| the real implementation | passes, `(25, 1400)` at n=3 |
| `lambda …: frozenset()` — always empty | **passes**, `(25, 1400)` |
| `lambda …: frozenset(range(n))` — always everything | **passes**, `(25, 1400)` |

Identical case counts, because the case count is a count of vacuous assertions.
`orion.study.p6.reopening_calculus_smt.committed_check_is_vacuous` reproduces
this and is pinned by a test.

## Why it survived

Three things, and each is worth naming separately.

1. **It has a large, growing denominator.** 130,320 cases over 543 DAGs reads
   like thorough coverage. The number is real; what it counts is not.
2. **It calls the function under test.** A reader checking whether the mechanism
   is exercised sees `descendants(...)` on the line above the assertion and
   stops there. The call is not the test; the comparison is, and there is none.
3. **It is self-referential rather than differential.** The expected value is
   computed from the same expression as the actual value. Comparing a function
   to itself is always agreement — this is the same defect as a differential
   check with only one arm, which turned up the same day in P8's authority
   lift agreeing 60 of 60 while every trial came out identically.

## What was done

The mechanism itself turns out to be **correct**. Checked properly for the first
time: `descendants` was compared against an independently written specification
over every directed graph on four nodes — cyclic ones included, since none of the
reopening theorems need acyclicity — and every changed subset. **61,440 of
61,440 agree, with 51,712 cases in which something is actually reopened.**

Six theorems now cover the general case over graphs of any size
(`P6_REOPENING_CALCULUS_MECHANIZED_2026-08-21.json`): soundness, completeness,
minimality, conservativity, monotonicity, and what a cycle does.

The committed check is **not edited**. Its output is not cited by any P6 claim —
the 155 restorations and 1,055 strict-subset failures come from the separate
320-state model — so it is left standing as the record of what it did, and the
non-vacuous check is added alongside it.

## General lesson candidate

**An assertion that cannot fail is not a check, however many times it runs.**
The diagnostic is mutation, and it is cheap: replace the function under test
with a constant, and if the check still passes, it was never testing that
function. Every exhaustive-enumeration check in this repo should be asked the
same question, because the enumeration is what makes the result *look*
authoritative and the enumeration is orthogonal to whether anything is compared.

The narrower rule: **an expected value must be computed by a different route
from the actual value.** When both sides come from one expression, the check
degenerates into a tautology no matter how elaborate the loop around it.

---

## Repaired 2026-08-22

This record states that "the committed check is **not** edited". It has now been
edited, and the reproduction tables above are historical.

The two assertions are replaced by three, each naming a theorem and each compared
against a specification built from an independently computed transitive closure —
a Warshall-style all-pairs relational composition, a different algorithm from the
worklist traversal the implementation uses, so it is not a second copy of the
thing under test. Sufficiency, minimality and exactness now carry Theorem 1 and
Corollary 2.1 rather than restating set difference's own property.

Measured in the same frame this record used: all eight declared wrong propagation
operators were accepted before and none is accepted after, both mutants die where
both survived, and the case counts are byte-identical at 130,320 over 543 graphs.
The cases can now fail; that is the whole of what changed.

The closure checker's `assert certified & changed <= got` had the same shape —
`A ⊆ A ∪ B` — and gained the direction that did not exist: `got ⊆ roots |
downstream`, the upper bound Corollary 4.1 needs. Nothing had bounded the
affected set from above, so a full reset — the operator that corollary names as
strictly non-minimal — passed.

Two things this did not buy, pinned separately so they keep being reported:
nothing the closure check says about node `a` is falsifiable, because the graph
generator emits only earlier-to-later edges and `a` is a universal source; and
that check never varies `certified`, which is reported as a constant axis rather
than counted.

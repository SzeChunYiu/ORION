# A mechanized theorem whose checks compare an expression to a copy of itself

**Observed:** 2026-08-21, tracing why P6-U-T1 (#654) — "general theorem proved
from primitive semantics" — is `BLOCKED_ON_PROOF` against an artifact that
records `"terminal": "PASS"`.

## Failure

P6's authority is two deterministic checker scripts. The superiority ledger
names `research/claim_expansion/p6/P6_X_FINITE_MODEL_RESULT_V1.json` for
P6-U-T1, and the V4 claim ledger's P6.V4.6 cites
`P6_X2_CERTIFICATE_LIFTING_RESULT_V1.json` — "320 states, 25 minimal
separations, 31 product countermodels, 155 full revalidation successes, 1,055
proper-subset failures, zero donor-conservativity/ideal-product violations".

Both report a case count and a violation count of zero. Both are reproducible to
the digest. The question neither artifact answers is whether any of those zeros
could have been anything else.

The 1,536-state artifact's terminal is computed by its own generator:

```python
"terminal": "PASS" if not (t1_violations or t3_violations or t4_violations)
            and len(t2_pairs) == 96 and len(t5_countermodels) == 96 else "FAIL"
```

and `t4_violations` counts

```python
def scientific_admissible(state, embedding):
    return donor_valid(state, embedding) and all(state[f] for f in SCI_FIELDS)

def ideal_product(state, embedding):
    return donor_valid(state, embedding) and all(state[f] for f in SCI_FIELDS)

if scientific_admissible(s, emb) != ideal_product(s, emb): t4_violations += 1
```

Two definitions, one expression, written twice. `t1` compares `donor_valid(s, emb)`
against the same expression recomputed through `forget`, which copies every donor
field verbatim. `t3` compares `scientific_admissible` against `donor_valid`
*inside* `if all(s[f] for f in SCI_FIELDS)`, under which the first reduces to the
second by its own definition.

The checker enumerates the complete Boolean cube — `2^9 = 512` states per
embedding, 1,536 in all — so exhaustion settles the question rather than
sampling it:

| violation counter | states evaluated | states where the condition held |
| --- | --- | --- |
| `t1_violations` (conservativity) | 1,536 | **0** |
| `t3_violations` (no-alarm preservation) | 96 | **0** |
| `t4_violations` (ideal-product equivalence) | 1,536 | **0** |

Three zeros that read alike and are not alike. `t1` and `t4` are zero because
their conditions are unsatisfiable — no rule, right or wrong, makes either fire.
`t3`'s zero is a fact about the shipped rule, and it is the one counter here
that is evidence.

The 320-state certificate-lifting checker carries the same two shapes:
`donor_conservativity_violations` compares `projected_native = native_valid`
against `native_valid` — an assignment on the line above — and
`ideal_product_mismatches` compares `liftable(...)` against `native_valid and
all(science)`, which is the body of `liftable`. Instrumented over all 320 rows,
each condition is satisfied **0 times and false 320 times**, and the first of the
two is 0 for any rule whatsoever — there is no second definition for it to drift
from. The re-implementation that produced those counts reproduces
`canonical_rows_sha256 = e1e3c48b…` exactly.

### What a wrong theory does to each check

Registering wrong theories of lifting — each one naming the P6 claim it breaks —
and asking each shipped check whether it still says PASS
(`python -m orion.study.p6.refutation_audit`):

| shipped check | of 8 false theories: refuted | accepted | verdict |
| --- | --- | --- | --- |
| `single_coordinate_separation_witnesses` | 7 | 1 | PASS |
| `certificate_product_countermodels` | 6 | 2 | PASS |
| `selective_revalidation` | 7 | 1 | PASS |
| `donor_conservativity_violations` | **0** | **8** | FAIL |
| `ideal_product_mismatches` | **0** | **8** | FAIL |

and on the 1,536-state checker, against 7 false theories of scientific
admissibility:

| shipped check | refuted | accepted | verdict |
| --- | --- | --- | --- |
| `t1_violations` | **0** | **7** | FAIL |
| `t3_violations` | 4 | 3 | PASS |
| `t4_violations` | **0** | **7** | FAIL |
| `t2_separation_pairs` | 6 | 1 | PASS |
| `t5_countermodels` | **0** | **7** | FAIL |

`t5`'s assertion is `assert donor_valid(changed, emb)` — a claim about the donor
side alone — so no theory of scientific admissibility can reach it, and both its
96 and `t2`'s 96 are appended unconditionally: given the script terminates, both
counts are 96 whatever the theory is.

The script as a whole is not defenceless, and saying otherwise would overstate
this. Replaying the shipped `run()` under each of the 7 false theories, all 7 are
caught — 6 die at line 60, `assert scientific_admissible(base,emb) and not
scientific_admissible(changed,emb)`, and `science_without_donor` completes with
`"terminal": "FAIL"`. What is being denied is narrower and is what the JSON
publishes: of the five quantities the terminal is computed from, exactly one —
`t3`, the only counter that compares two genuinely different functions — can be
non-zero for a wrong theory. `t1` is 0 in every completing run. `t2` and `t5` are
96 in every completing run.

`t4` is the interesting one, and the two readings both end in the same place.
Edit `scientific_admissible` and leave its textual duplicate `ideal_product`
alone, and `t4` reports 72 — it is a copy-drift detector, and a good one. Edit
both, which is what P6.V4.5's own words require ("an ideal donor product with
**identical** scientific fields/rules"), and `t4` is 0 for all 7. Under the
reading that makes it a theorem, it has no falsifier; under the reading that
gives it a falsifier, it is not about donor products.

### One wrong theory walks through the entire lifting checker

`science_lifts_without_donor` — scientific standing preserved with no valid
lower-level certificate underneath it, the direct denial of P6.V4.1 — is refuted
by **none** of the five shipped checks. The cause is exact: every assertion in
`check_p6_x2_certificate_lifting.py` evaluates the rule at `native_valid=True`.

| | points |
| --- | --- |
| distinct `(native_valid, science)` states enumerated | 64 |
| states reached by any rule evaluation | 64 |
| states reached by an **assertion** | **32** |
| of those, with `native_valid = False` | **0** |
| assertion evaluations in the whole script | 1,426 |

The other 32 states are enumerated into the row list, hashed into
`canonical_rows_sha256`, and never asserted about.

Run against the published file verbatim, with `liftable` replaced by
`lambda native_valid, science: all(science)`:

| reported quantity | as shipped | under the donor-irrelevant theory |
| --- | --- | --- |
| `state_evaluations` | 320 | 320 |
| `single_coordinate_separation_witnesses` | 25 | 25 |
| `certificate_product_countermodels` | 31 | 31 |
| `full_revalidation_successes` | 155 | 155 |
| `partial_revalidation_failures` | 1,055 | 1,055 |
| `donor_conservativity_violations` | 0 | 0 |
| `ideal_product_mismatches` | 0 | 5 |
| `canonical_rows_sha256` | `e1e3c48b…` | `17add4fb…` |

The script completes and prints P6.V4.6's headline sentence unchanged. The two
quantities that move are the ones no reader checks: a digest the primary prints
rather than asserts, and the copy-drift counter, which reports 5 here only
because `liftable` was edited and its inline duplicate was not — co-edit both, as
P6.V4.5's "identical rules" requires, and it stays 0 for all eight theories.

### The independent verifier cannot disagree

`independent_check_p6_x2_certificate_lifting.py` implements `independent_lift`
as an early-return loop where the primary writes `native_valid and all(science)`.
Measured over the 320 enumerated points, the two rules **differ on 0**. It is a
paraphrase, and its assertions have the same `native_valid=True` blind spot.

The one thing in either implementation that notices the donor-irrelevant theory
is line 46 of the verifier:

```python
assert digest == "e1e3c48bcefea3750d952c6b0ff37ac660a2e21f9823fdfdeb50bb62e819ff93"
```

a comparison against a frozen hash of the primary's own output. That is
agreement, not verification — and the primary itself only prints its digest.

`P6_X_INDEPENDENT_VERIFICATION_V1.json` records `"state": "BOUNDED_VERIFIED"` and
`"imports_primary_checker": false`. Not importing the primary is the wrong test
of independence, and it is satisfied by copying it. The test that matters is
whether the second implementation can disagree with the first, and this one
cannot on any of the 320 points either of them enumerates. That is the state
P6-U-T4 is actually in: a review was arranged, and it was a paraphrase.

### The donor axis multiplies every count by five

`liftable` never receives the donor. Comparing only points that agree on every
other axis, **0 of 640** sibling pairs change the verdict, so:

| published | distinct facts | multiplicity |
| --- | --- | --- |
| 320 state evaluations | 64 | ×5 |
| 25 separation witnesses | 5 | ×5 |
| 155 full revalidation successes | 31 | ×5 |
| 1,055 proper-subset failures | 211 | ×5 |
| 31 product countermodels | 31 | ×1 |

Only the one quantity not enumerated inside the donor loop is un-multiplied.

### What the enumeration does establish

`liftable` agrees with a plain conjunction of its six free booleans on **320 of
320** points, and its verdict is unchanged under **all 38,400** permutations of
the five lift-coordinate values (36,864 for the four `SCI_FIELDS` on the other
checker). The coordinates are exchangeable: nothing in either model distinguishes
`measurement_semantics` from `scientific_epoch`, or from any other Boolean.

So the 25 separations, the 31 countermodels and the 155 / 1,055 revalidation
results are the truth table of `and`, enumerated five times over. That is a
correct table. It is not evidence about scientific revalidation, because the
scientific content of P6's claim lives entirely in *which five coordinates* and
*what makes one change*, and neither is represented in the model at all. This is
the precise form of P6-U-T1's block: the finite result is not a weaker authority
than a proof, it is a truth table for conjunction over five uninterpreted
variables, and no amount of further enumeration converts it into the theorem
#654 asks for.

### The same shape in the paper's own proof-support checkers

`papers/paper-06-formal-epistemic-structures-and-mechanics/formal/check_finite_models.py`
prints `P6 finite-model checks: PASS` with 543 DAGs and 130,320 reopening cases.
Its two assertions are

```python
retained = certified.difference(downstream)
assert not retained.intersection(downstream)
assert retained == certified.difference(downstream)
```

— the first is set difference's defining property, the second is `x == x`.
Replacing `descendants` with rules that are maximally wrong in both directions:

| `descendants` | `check_reopening(4)` → (DAGs, cases) |
| --- | --- |
| as shipped | (543, 130320) |
| `≡ ∅` — nothing is ever downstream | (543, 130320) |
| `≡ everything` — all nodes are downstream | (543, 130320) |

`check_theory_closure_v2_1.py::check_root_inclusive_safety` behaves identically:
`(960, 2048)` for the shipped `descendants` and for both wrong ones, because
`affected` is defined as `(certified & changed) | (certified & descendants(...))`
and the assertions are `A ⊆ A ∪ B`.

## Failure class

`UNFALSIFIABLE_CHECK_ZERO_REFUTATION_CAPACITY`

A mechanized check reports a pass and a case count when no state of the system
under test could have made it fail. The case count is real, the enumeration is
exhaustive, the digest is stable, and the check is a statement about the
checker's own definitions rather than about the theory it names.

This is the formal-side member of the family the four records beside it build:

- `2026-08-unreachable-operator-inert-ablation/` — the **independent** variable
  never varied: the arm never reached the operator it ablated.
- `2026-08-vacuous-guard-zero-denominator/` — the **dependent** variable never
  varied: the guard was never pressed, so its zero had no denominator.
- `2026-08-unapplied-treatment-vacuous-null/` — the **cause** did not vary: the
  treatment was configured and applied and was the identity.
- `2026-08-label-recoverable-from-construction-cue/` — both varied, and the
  correlation was with the construction.
- here — **the verdict could not vary.** Not the input, not the outcome, not the
  label: the *predicate*. `t4_violations` is 0 for the same reason `x != x` is
  false, and it would be 0 for any theory anyone ever writes.

Three properties let it survive review.

1. **A theorem check has no denominator to ask about.** P2's lesson — demand the
   denominator — has an answer here, and the answer is impressive: 320 states,
   1,536 states, 130,320 reopening cases. The denominator was never the problem.
   Nothing asked how many of those cases had a reachable false branch.
2. **Reproduction is not independence.** The repository did the right thing and
   commissioned a second implementation; it reproduced the digest to the byte
   because it was a paraphrase of the first. A second implementation is a
   falsifier only where it can disagree, and this one differs on 0 of 320 points.
3. **The tautologies sit under the load-bearing claims.** The two counters with
   zero refutation capacity in the lifting checker are exactly P6.V4.1 (donor
   conservativity) and P6.V4.5 (the "NEGATIVE EQUIVALENCE THEOREM"); in the
   finite-model checker, four of the five quantities its `"terminal"` reads
   cannot be non-zero for a wrong theory. The checks that do have capacity are
   the ones re-deriving `all()`, which the claim ledger does not cite as a
   result because it is not one.

## Correct response

1. Do not report a mechanized result before establishing that something could
   have made it fail. `orion.programme.refutation_capacity` takes a rule, the
   checker's own enumerated space, and a register of **declared false theories**,
   and measures which ones each check rejects.
2. Return three values. A check with no live falsifier is
   `Outcome.CANNOT_CHECK`, which by `Outcome.blocks` stops a promotion exactly as
   `FAIL` does; a check that rejects nothing is `FAIL`. The verdict is built from
   `GuardExercise` rather than beside it — the opportunities are the live false
   theories and the violations are the survivors — so "nobody proposed a wrong
   theory" and "the guard was never pressed" are one state with one answer, and
   `GuardAssessment` already refuses to pair `PASS` with a vacuity reason.
3. Require every false theory to be *extensionally* different from the reference
   somewhere in the space. This is
   `orion.study.p3.treatment_contrast.TreatmentContrast`'s question asked about a
   rule instead of a corpus, and it is what names the shipped independent
   verifier for what it is: `divergence_of(independent_lift, …)` returns
   `points_changed = 0` out of 320.
4. Ask the question at two levels, because they are two failures.
   Per check: does it reject anything at all? Per panel
   (`assess_theory_coverage`): is every false theory rejected by *some* check?
   The lifting panel has three checks with real capacity and still lets
   `science_lifts_without_donor` through all five; the finite-model panel covers
   its whole register and still computes its terminal from three tautologies.
   Neither level sees the other's failure.
5. Only count a refutation the theorem earned. `AssertionError` kills a false
   theory; a `TypeError` propagates, because a mutant refuted by the interpreter
   was not refuted by the theory — the distinction
   `2026-08-digest-representation-boundary-mixup/` is about.
6. Name the axes that only multiply. `axis_sensitivity` compares points that
   agree on every other axis, so `donor` reports **0 of 640** verdict-changing
   sibling pairs and every count enumerated inside that loop is marked ×5.
7. Refuse to score the panel: `require_refutable(capacities, label="P6.V4.6")`
   raises, naming both the checks no wrong theory can fail and the wrong theories
   no check catches, before any case count is read as evidence.
8. Point the instrument at the shipped artifact. `orion.study.p6.lift_theories`
   rebuilds the published row list and its `canonical_rows_sha256` byte for byte
   before transcribing a single claim, and one test execs the published
   `check_p6_x2_certificate_lifting.py` itself. An instrument that only ever runs
   on its own fixture is the failure it was written to catch.
9. Register the missing assertion as code. `DONOR_REQUIREMENT_CHECK` is one line
   — nothing lifts where `native_valid` is false — and adding it to the panel
   takes coverage from 7 of 8 to 8 of 8.
10. Repair the model so the coordinates are not exchangeable Booleans: give
    `measurement_semantics` and `scientific_epoch` content that a change can act
    on, so that "this coordinate is load-bearing" is a claim the enumeration can
    fail. That is the theory lane's call and is **not** done here; the diagnosis
    and the instrument are.

## General lesson candidate

**A check is evidence only for as long as some reachable state would have made
it fail.** Enumeration exhaustiveness, case counts, content digests, deterministic
reproduction and independent re-implementation all survive a tautology intact —
every one of them held here, across two implementations — because none of them
is a statement about what the assertion is made of.

The sharper form, and the one that generalizes past this repository: **a
mechanized theorem must be tested against theories it should reject, not only
against the theory it was written from.** Writing the same expression twice and
comparing them is the formal analogue of a guard that never fires: it returns the
same value whether the claim is deep or empty, and the second copy is
indistinguishable from an independent model right up until someone asks what
would happen if the theory were different.

Stated once for the family this extends: `UNREACHABLE_OPERATOR_INERT_ABLATION`
is a mechanism that never ran, `VACUOUS_GUARD_ZERO_DENOMINATOR` an outcome that
could not vary, `UNAPPLIED_TREATMENT_VACUOUS_NULL` a cause that did not vary,
`LABEL_RECOVERABLE_FROM_CONSTRUCTION_CUE` a label explained by the construction
— and this one a **verdict that could not vary**. Every check in this repository
that reports "PASS over N cases" should be asked which of the N had a reachable
false branch, and every count of violations should be asked whether its condition
is satisfiable at all.

---

## Resolved 2026-08-22

The five checks this record was written about now refute. Both P6 checkers moved
`FAIL -> PASS` and `refutation_audit` exits 0.

Item 10 said "Repair the model... That is the theory lane's call and is **not**
done here." It has now been made, and the before-tables above are historical.

All five had one cause, and it is sharper than "trivially satisfiable": **the
predicate was not a function of the rule at all.** Four of the five discarded
their `rule` argument outright. The model had states and a verdict and no map, so
every claim that needed a map to state it got written as a claim about an atom
instead — which makes it an identity.

- `donor_conservativity_violations` and `t1_violations` — the projection was
  applied to the donor atom, so the comparison was `x != x`.
- `ideal_product_mismatches` and `t4_violations` — the "ideal product" was the
  predicate's own body written a second time, so the comparison was `x == x`. It
  moved only when one copy was edited and the other was not: a copy-drift
  detector, not an equivalence theorem.
- `t5_countermodels` — the block asserted the countermodel's *premise* and
  appended its count unconditionally. 96 in every completing run, for every rule.

The repair was three semantic extensions, not three exceptions: a projection from
a lifted state to the donor certificate under it, an enriched donor product
constructed as the donor theory's own validator over a requirement set enlarged
by the scientific coordinates, and donor-valid transitions in which the donor
side may change while staying valid. The one-line exception that would also have
made the coverage number go green is kept beside the extension, unshipped, with a
test pinning that its refuted set is a strict subset — so "extend the semantics,
not the exception list" is a comparison a reviewer can run rather than a claim.

Registers grew: 7 to 8 and 8 to 9 declared false theories, both additions taken
from the frozen theorem documents' own falsifier lists. Every published number is
preserved, `canonical_rows_sha256` included.

Two things this did **not** buy, both tested so they keep being reported:
`t5`'s marginal refutation capacity over `t2` on this register is zero, and the
independent implementation still diverges from the primary on 0 of 320 points —
a second implementation is a falsifier only where it can disagree, and what
`P6-U-T4` needs is a reviewer, which a repository cannot produce for itself.

# A theorem whose hard predicate is one of its parameters

**Observed:** 2026-08-21, tracing why P7-U-T1 and P7-U-T2 (#655) are
`BLOCKED_ON_PROOF` — "there is no general compositional calculus or checker" —
against two artifacts that enumerate their spaces exhaustively, print `PASS`, and,
in the case the ledger cites, reproduce to the digest under a second
implementation.

## Failure

P7's claims all have the same shape: **the system decides X, therefore terminal
T.** Its checkers all verify: **given X, terminal T.** The mapping is enumerated
completely. The decision is a keyword argument.

`papers/paper-07-epistemic-navigation-open-worlds/formal/check_theory_closure_v2.py`
is the authority `REPRODUCE_V2_1.md` names for "all 64 transport-coordinate
combinations". It prints `P7 THEORY CLOSURE V2: PASS` and `support_transport: 64`
from

```python
def transfer_terminal(t: Transport, *, target_ambiguous_if_missing: bool) -> str:
    if t.complete:
        return "TRANSFER_CLOSURE"
    return "REOPEN" if target_ambiguous_if_missing else "CANNOT_CHECK"
```

`target_ambiguous_if_missing` **is** the paper's C4. `FORMAL_CORE_V2.md`
Definition 14 defines it — "an incomplete witness is target-ambiguous iff there
exist two target completions consistent with every established mapping fact, one
preserving the old certificate derivation and one invalidating it" — and the
Boundary paragraph under Theorem 6 says deciding it correctly is what "closes the
V1 logical gap". `check_support_transport` supplies it as `True` on all 64 states
and again as `False` on each of the 63 incomplete ones, and asserts the terminal
that each literal implies.

Measured over that space (`python -m orion.study.p7.premise_audit`), asking each
state whether it excludes any value of the premise:

| | |
| --- | --- |
| transport states enumerated | 64 |
| rule evaluations | 127 |
| states where **both** ambiguity values are accepted | **64 / 64** |
| states that exclude either value | **0** |
| ambiguity predicates the check accepts | **2⁶⁴ = 18,446,744,073,709,551,616** |
| random predicates accepted, seed `20260821` | **5,000 / 5,000** |

Every one is admissible, including `lambda t: True`, `lambda t: False` — which is
"incompleteness never means ambiguity", the exact V1 error V2 says it repaired —
and the parity of the six witness bits. The assertion cannot separate them,
because the expected value moves with the input: the shipped body asserts
`transfer_terminal(t, amb) == ("REOPEN" if amb else "CANNOT_CHECK")`, and `amb`
appears on both sides.

The same file already contains a real ambiguity decider:

```python
def extension_ambiguous(completions: tuple[Completion, ...]) -> bool:
    return any(observationally_equivalent(a, b) and a.mandatory_satisfied != b.mandatory_satisfied
               for a in completions for b in completions)
```

`check_stopping_impossibility` and `check_certificate_absence_not_ambiguity` both
call it. `check_support_transport` does not. The artifact demonstrably could
decide the premise and, in the theorem the premise belongs to, does not.

### The same shape carries the P7-U programme's foundation

`research/claim_expansion/p7/check_p7_x2_closure_carrying.py` is what the
superiority ledger names for P7-U-T1. Its composition block, in full:

```python
for d1 in DONORS:
    for d2 in DONORS:
        c1 = carries(True, full)
        c2 = carries(True, full)
        assert compose(c1, c2, True)
        composition_successes += 1
        assert not compose(c1, c2, False)
        composition_bridge_countermodels += 1
```

`d1` and `d2` appear in no expression. `c1` and `c2` are the same constant.
`bridge_match` — P7.V3.5's "exact intermediate closure-contract binding", the one
claim that distinguishes P7-X2 from P6-X2 — is a literal. There is no object in
the model that is a closure contract and no function anywhere from a pair of
transforms to whether their contracts bind.

Traced over a verbatim run:

| | |
| --- | --- |
| donor pairs enumerated | 25 |
| donor pairs read by any expression | **0** |
| `compose` evaluations | 50 |
| distinct `(c1, c2, bridge_match)` triples | **2 of 8** |
| pairs where both bridge values are accepted | **25 / 25** |
| bridge predicates the block accepts | **2²⁵ = 33,554,432** |
| Boolean composition rules of `(c1, c2, bridge)` the block accepts | **64 / 256** |

The published `composition_successes: 25` and
`composition_bridge_countermodels: 25` are one fact, counted 25 times, at two
points of a three-argument truth table.

Running the shipped `main()` verbatim under wrong theories of composition:

| `compose` | run | successes | bridge countermodels | `canonical_rows_sha256` |
| --- | --- | --- | --- | --- |
| as shipped, `c1 and c2 and bridge` | completed | 25 | 25 | `25f40385…` |
| `bridge` alone — **both operands' closure irrelevant** | completed | 25 | 25 | `25f40385…` |
| `c1 and bridge` — right operand irrelevant | completed | 25 | 25 | `25f40385…` |
| `bridge and (c1 or c2)` — either part suffices | completed | 25 | 25 | `25f40385…` |

Byte-identical output, digest included, under the direct denial of P7.V3.5. The
shipped "independent" verifier is weaker still: it defines no composition rule at
all, and its 25 bridge countermodels are `assert not (c1 and c2 and False)` —
`assert not False`, evaluated 25 times.

`successor/P7_U_MANUSCRIPT.tex` makes this the ground the successor stands on:
"The existing 155 successful restorations, 1,055 strict-subset failures, **25
successful heterogeneous compositions and 25 matched missing-bridge cases remain
immutable and must be derived as instances** rather than encoded into
definitions." What P7-U-T2 must derive is `True and True and True` and
`True and True and False`.

### Why P6's instrument clears both

This is not the P6 tautology in another shape, and that is the whole point.

`check_support_transport` **has** refutation capacity. Registering four wrong
theories of the terminal map and measuring with
`orion.programme.refutation_capacity`:

| false theory | breaks | refuted |
| --- | --- | --- |
| `incomplete_always_reopens` | C4's non-ambiguous branch (the V1 error) | yes |
| `incomplete_always_cannot_check` | C4's ambiguous branch | yes |
| `closure_always_transports` | the support-transport criterion itself | yes |
| `five_of_six_coordinates_suffice` | completeness of the witness | yes |

4 of 4, 0 survivors, `Outcome.PASS`. The check is not a tautology; it constrains
its rule properly. What no register of false theories can reach is a wrong theory
of *ambiguity*, because there is no rule to perturb — perturbing a keyword
argument changes the case, not the theory.

**The space of false theories a checker can be measured against is bounded by
which of the claim's predicates it computes.** A supplied premise removes itself
from the register silently, and the register then reports full coverage of what
remains.

The other instruments are equally clean here. Operator coverage sees checkers
that run. `GuardExercise` sees denominators of 64 and 25. Treatment contrast sees
genuinely varying inputs. `benchmark_identifiability` scores a label, and neither
formal artifact has one. `commitment_custody` has nothing sealed. Every one of
them passes, and the paper still has no mechanized decision.

### The rest of P7's formal surface, same shape

- `recovery_transition` decides `REFRAME` from `current_chart_can_resolve` and
  `candidate_chart_expresses_need`, both keyword booleans. Over its 64-point
  input space, `check_recovery_transitions` asserts **5 points**, leaving 59
  unasserted and 5⁵⁹ completions admissible; on all 5, the sibling with the
  reframe premise flipped is not asserted. There is no chart in the model.
- `task_terminal` takes `mandatory_open` and `censored_unknown` as parameters.
  `check_stop_terminals` asserts **4 of 16** points.
- `formal/check_countermodels.py` prints `P7 deterministic countermodels: PASS`.
  **6 of its 9** `check_*` functions call no module-level rule at all — their
  assertions are over literals declared inside their own bodies.
  `check_unnecessary_reframe_negative_control`, the paper's harmful-reframe
  negative control, is `reframe_required = False; assert reframe_required is
  False`.
- `papers/candidates/checkers/p7_finite_falsifiers_v1.py`, named for falsifiers,
  has **5 of 7** in the same state, including
  `task_stop_allowed = not mandatory_open; assert task_stop_allowed is False`.

And in the empirical instrument, the same move in data rather than code. The
"reference-policy oracle" exists twice — `check_benchmark_contracts_v2.py::
evaluate_benchmark_case` and a duplicate in `check_contract_manifest_v2.py::
oracle`, which is what `REPRODUCE_V2_1.md`'s "all 8 frozen prospective contract
cases" runs. Both read exactly three fields: `topology_change_required`,
`family`, `censored_regions`. Neither reads `mandatory_obligations` or `gold`,
which are the task. Measured on `benchmark/instances_v1.jsonl`:

- `expected_terminal` is a function of `family` alone, on 8 of 8;
- `topology_change_required` is `True` on exactly the two `REFRAME` cases;
- `censored_regions` is non-empty on exactly the two `CANNOT_CHECK` cases.

`topology_change_required` is the reframe judgement, declared as a field of the
case. `BENCHMARK_AUDIT_V2.md` argues the battery has headroom because "a policy
that always reframes, always stops or always returns `CANNOT_CHECK` therefore
cannot satisfy the intended prospective evaluation" — true, and answered by
reading one string. (`instances_v1.jsonl` and `instances_v2.jsonl` are also byte
identical, sharing `af0da575…` in `SHA256SUMS`.)

### What the enumeration does establish

The donor axis of the closure-carrying checker is inert: over its 320 rows, **0
of 640** sibling pairs agreeing on every other axis change the verdict. So 320
state evaluations are 64 distinct facts and a five-fold relabelling, exactly as
in P6. The composition counts are the extreme case of the same thing — a 25-fold
relabelling of one.

## Failure class

`SUPPLIED_PREMISE_UNBUILT_DECISION`

A mechanized claim is verified against a model in which the predicate the claim
is about arrives as an input. The checker enumerates that input's values and
asserts the terminal each one implies, so the case count measures the mapping
downstream of the decision and the decision itself is never made, never
constrained, and never wrong.

This is the sixth variance an experiment has to establish, and the five beside it
are why it is a distinct one:

- `2026-08-unreachable-operator-inert-ablation/` — the **mechanism** never ran.
- `2026-08-vacuous-guard-zero-denominator/` — the **dependent** variable could not vary.
- `2026-08-unapplied-treatment-vacuous-null/` — the **cause** did not vary.
- `2026-08-label-recoverable-from-construction-cue/` — both varied and the
  correlation was with the **construction**.
- `2026-08-invertible-commitment-vacuous-custody/` — the **blind** was not blind.
- `2026-08-unfalsifiable-check-zero-refutation-capacity/` — the **verdict** could
  not vary: the predicate compared an expression to a copy of itself.
- here — the verdict varies correctly, the check refutes wrong theories, and the
  **predicate under test was never built.** It is a parameter.

The sharpest way to see the difference from P6 is that P6's instrument is *run*
here and returns `PASS`. A tautology has no falsifier; this has falsifiers, and
all of them are falsifiers of the half of the claim nobody doubted.

Three properties let it survive review.

1. **The easy half looks like the whole claim once it is enumerated.** "All 64
   transport-coordinate combinations" is a true and impressive sentence. Sixty-four
   is the size of the *witness* space; the ambiguity space over it has 2⁶⁴ points
   and none of them was visited.
2. **A parameter is indistinguishable from a case description.** The six transport
   bits are legitimately the case: the claim is a statement about them. The
   seventh argument looks identical in the signature and is the conclusion. Only
   asking what each one must be *decided from* separates them, and that is a
   sentence a schema cannot supply.
3. **The independent verifier is downstream of the same parameter.**
   `independent_check_p7_x2_closure_carrying.py` reproduces
   `canonical_rows_sha256` to the byte and inlines the composition assertion as
   `assert not (c1 and c2 and False)`. Reproduction is not independence, which is
   P6's second lesson arriving unchanged.

## Correct response

1. Ask which premises the artifact computes, as a type.
   `orion.programme.decided_premises` takes a premise, the checker's own case
   space, and a replay of the checker's assertions with the premise supplied by a
   *candidate deciding rule* instead of the caller's literal, and measures how
   many cases exclude any value of it. `Premise` requires a written
   `decision_obligation` and a `decided_from`, for the reason
   `GuardExercise.opportunity_definition` and `SealedSecret.domain_rationale` are
   required: a decision nobody can describe cannot be shown to have been made.
2. Return three values. The verdict is built from `GuardExercise` rather than
   beside it — opportunities are the enumerated cases, violations are the cases
   that leave the premise free — so "the checker enumerated nothing" and "the
   guard was never pressed" are one state with one answer.
   `DecisionConstraint` refuses at construction to pair `PASS` with any vacuity
   reason or with any free case, so the substitution cannot return by edit.
3. Separate the omission from the impoverished model. `bridge_match` is
   `PREMISE_SUPPLIED` → `FAIL`: both donors are axes of the enumerated space, so
   it could have been decided there. `target_ambiguous_if_missing` is
   `UNDECIDABLE_IN_MODEL` → `CANNOT_CHECK`: `admissible_target_completions` is not
   an axis of anything the transport checker enumerates, so no rule written
   against that space could decide it. Those need different repairs — one is a
   missing function, the other a missing model — and a single `FAIL` would hide
   which.
4. Report how many deciding rules survive, not whether any do.
   `DecisionConstraint.admissible_assignments` is 2⁶⁴ and 2²⁵ on the two shipped
   artifacts and 1 on a checker that decided its premise. It is the number
   `support_transport: 64` conceals, in the way `TreatmentContrast.resolution` is
   what `[0.0, 0.0]` conceals.
5. Refuse to hold the number. `DecidedResult` cannot be constructed while any
   constraint blocks, so publishing "25 successful compositions and 25 matched
   missing-bridge cases" as support for P7.V3.5 requires deleting the type rather
   than forgetting a check — the refusal `AuditedScore` makes about a leaking
   benchmark and `ProspectiveScore` about an invertible commitment.
6. Carry both verdicts together, because they are independent.
   `DecidedResult.capacities` holds the `RefutationCapacity` results for the same
   checks. P7's transport check is `PASS` on refutation capacity and
   `CANNOT_CHECK` on its premise, in the same report, which is the fact this
   record exists to make visible.
7. `require_decided(constraints, label=...)` raises before any case count is read
   as evidence, naming the premises the artifact was handed and, separately, the
   premises its model cannot express — the decision-side counterpart of
   `require_operators_exercised`, `require_treatment_applied` and
   `require_refutable`.
8. Point the instrument at the shipped artifact. `orion.study.p7.closure_premises`
   loads both checkers from disk and rebuilds `canonical_rows_sha256` byte for
   byte before transcribing a claim; `python -m orion.study.p7.premise_audit`
   audits them and exits 3. An instrument that only ever runs on its own fixture
   is the failure it was written to catch.
9. Give the transport model an admissible-completion class, so ambiguity is a
   function of the case rather than an argument; give the closure-carrying model a
   contract object, so `bridge_match` is computed from the two transforms rather
   than typed. Both are the theory lane's call and are **not** done here. The
   diagnosis and the instrument are.
10. Re-audit the 8-case benchmark with `orion.programme.benchmark_identifiability`
    before any P7-U-T3 comparison is scored on it. `topology_change_required` is
    the answer written into the question; that is
    `LABEL_RECOVERABLE_FROM_CONSTRUCTION_CUE` and its instrument already exists.
    Also **not** done here — this record's scope is the formal lane.

## What this costs P7 and what it does not

Very little of P7 is overturned, and the paper's own caution should be preserved.
`CLAIM_LEDGER_V1.md` already marks C10–C14 `CANNOT_CHECK`;
`CLAIM_LEDGER_ADDENDUM_V2.md` marks the agent claims `CANNOT_CHECK` with "no
candidate-agent run"; `BENCHMARK_AUDIT_V2.md` says plainly that "no agent
comparison has been run"; `REPRODUCE_V2_1.md` calls the manifest "a
reference-policy oracle and prospective instrument preflight" that "does not
constitute a live-agent performance result". None of that is contradicted.

What this record removes is narrower and it is exactly what #655 asks for next.
The `155 / 1,055` restoration law is a real result of a different kind: those
counts are assertions about `carries`, a rule the checker actually computes, and
wrong theories of it do fail them. Replaying the shipped `main()` under four:

| `carries` | run | full / partial / separations |
| --- | --- | --- |
| as shipped | completed | 155 / 1,055 / 25 |
| `native_valid` alone | `AssertionError` | refuted |
| `native_valid and any(closure)` | `AssertionError` | refuted |
| `native_valid and all(closure[:4])` | `AssertionError` | refuted |
| `all(closure)` — **donor validity irrelevant** | completed | 155 / 1,055 / 25 |

The last one walks through, and its cause is exact: `carries` is evaluated 1,796
times, 1,476 of them inside an assertion block, and those reach **32 of the 64
distinct states, 0 of them with `native_valid=False`**. The other 32 are
enumerated into `canonical_rows_sha256` and never asserted about. That is
`UNFALSIFIABLE_CHECK_ZERO_REFUTATION_CAPACITY`'s "one wrong theory walks through
the entire checker", reproduced state for state in P7's sibling script, and it is
already recorded there.

The `25 / 25` composition panel is the part this record is about, and it is the
half the successor manuscript declares immutable and requires P7-U-T2 to derive as
instances. Deriving it as an instance of a general calculus would mean deriving
`x ∧ y ∧ z` at two points.

And P7-U-T1's blocker is sharper than the ledger states it. The ledger says "the
25 successful compositions against 25 matched missing-bridge cases are a
registered navigation model, not a calculus over arbitrary transformation
chains." Measured, they are not a registered navigation model either: no
transform, no contract and no bridge appears in the expression the counts come
from.

## General lesson candidate

**A mechanized claim is evidence about the predicate it computes, not about the
predicate it names.** Enumeration exhaustiveness, case counts, content digests,
deterministic reproduction, independent re-implementation and a clean refutation
audit all survive a supplied premise intact — every one of them held here — because
none of them is a statement about where the checker's inputs came from.

The sharper form, and the one that generalizes past this repository: **the hard
half of a claim is usually the one the checker takes as an argument.** Split every
theorem into "which way does the predicate go" and "what follows once it has gone
that way", then ask which half the code contains. Mechanizing the second half is
easy, exhaustively checkable, and produces impressive case counts; mechanizing the
first is the science. When a signature carries a parameter whose name is a
question — `target_ambiguous_if_missing`, `bridge_match`,
`candidate_chart_expresses_need`, `topology_change_required` — that parameter is
the claim, and every count downstream of it is a count of the answer sheet.

Stated once for the family this extends: `UNREACHABLE_OPERATOR_INERT_ABLATION` is
a mechanism that never ran, `VACUOUS_GUARD_ZERO_DENOMINATOR` an outcome that could
not vary, `UNAPPLIED_TREATMENT_VACUOUS_NULL` a cause that did not vary,
`LABEL_RECOVERABLE_FROM_CONSTRUCTION_CUE` a label explained by the construction,
`INVERTIBLE_COMMITMENT_VACUOUS_CUSTODY` a blind that was not blind,
`UNFALSIFIABLE_CHECK_ZERO_REFUTATION_CAPACITY` a verdict that could not vary — and
this one a **decision that was never made**. Every check in this repository that
reports "PASS over N cases" should be asked, of each of its rule's arguments,
whether that argument is part of the question or part of the answer.

---

## Closed 2026-08-22

Both P7 exhibits are repaired, and each repair is the one this class prescribes:
supply the axis the decision needs, do not soften the assertion.

**`bridge_match`** was free on 25 of 25 composition cases, admitting 33,554,432
deciding rules including the constants. Two mechanisms compounded. The replay
asserted `compose(c1, c2, bridged)` with the expected value chosen by `bridged`
itself, so the premise stood on both sides. Underneath that was a fidelity error:
the shipped block makes 50 assertions — 25 under the bridging registry and 25
under the empty one — and the audit modelled 25 cases with one premise value
each, folding two rows that disagree into one. The decision inputs were already
in the repository; nothing was computing `Match(Tgt(d1), Src(d2))`. Now decided
on 50 of 50 with exactly one admissible rule, 0 of 5,000 random whole rules
accepted, and no published verdict moved: 50 of 50 agreement with the shipped
literal, `canonical_rows_sha256` still `25f40385`.

**`target_ambiguous_if_missing`** was the harder one and is the reason item 9
deferred it: it was `UNDECIDABLE_IN_MODEL`, free on all 64 states, because
`admissible_target_completions` was not an axis of anything the checker
enumerated. The shipped file already contained a real decider,
`extension_ambiguous`, and could not call it — there was no completion class to
hand it. The checker now enumerates one beside each witness: **960 cases, 0 free,
one admissible rule, 0 of 5,000 random rules accepted**, and
`theory_closure_terminal` moves `CANNOT_CHECK` to `PASS`.

Three things are reported rather than glossed. The 960 is **not a larger 64** —
it is 64 coordinate states crossed with 15 completion classes, and both counts
are carried side by side as incomparable. On the 15 complete-witness cases
Theorem 6 returns `TRANSFER_CLOSURE` whatever ambiguity is, so those decide the
premise without testing the terminal's dependence on it; the shipped body now
asserts that insensitivity, making it a checked property rather than a gap, and a
separate floor re-measures with the direct transcription dropped — **945 of 960
cases still exclude a value**, leaving 2^15 rules against 2^64 before. And the
pre-repair model is retained as an explicitly labelled counterfactual, still
reporting `UNDECIDABLE_IN_MODEL` on its 64, so the contrast stays runnable rather
than becoming a claim about a file nobody can execute.

What remains open in P7 is a different question and is stated where it belongs:
the decided hand-off is still inert against `left_donor` and `right_donor` — only
the registry moves it — and no shipped function takes a donor argument at all.
Deciding a premise is not the same as making it depend on what one hoped it
would.

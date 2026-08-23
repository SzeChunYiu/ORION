# EAJ finite-menu dominance V1

**Date:** 2026-08-23  
**Issue:** #963  
**Terminal:** `EAJ_FINITE_MENU_CLASS_CLOSED`  
**Scope:** candidate-selection benchmarks with a finite fully enumerable schema-edit set and exact verifier.

## 1. Statement

Let a task instance `x` have a finite registered schema-edit candidate set

```text
C(x) = {c_1, ..., c_n}.
```

Let `V_x(c)` be an exact deterministic verifier of the full frozen success contract for candidate `c`, returning `1` iff the candidate is valid/successful under the registered task semantics.

Assume the benchmark budget permits evaluating every member of `C(x)`.

Define exhaustive evaluation:

```text
EXH(x) = 1  iff  exists c in C(x) with V_x(c)=1.
```

For any proposer `P` whose output is restricted to `C(x)`, define

```text
P-SUCCESS(x) = V_x(P(x)).
```

Then, pointwise for every `x`,

```text
P-SUCCESS(x) <= EXH(x).
```

Therefore no proposer restricted to the same finite candidate set can have a strictly higher solve/success rate than complete exhaustive evaluation when the budget permits verifying all candidates.

## 2. Proof

There are two cases.

### Case A — `P-SUCCESS(x)=1`

Then `P(x)` is some candidate in `C(x)` and `V_x(P(x))=1`. Hence a successful candidate exists in `C(x)`, so by definition `EXH(x)=1`.

### Case B — `P-SUCCESS(x)=0`

Then trivially `P-SUCCESS(x) <= EXH(x)` because `EXH(x)` is either `0` or `1`.

Thus the inequality holds for every task instance. Taking an average/expectation over any task distribution preserves the inequality.

QED.

## 3. What this closes

A benchmark cannot establish **schema-invention solve-rate superiority** by:

- hiding one correct edit among a finite menu;
- giving the learned model the same menu;
- allowing an exact verifier to test the whole menu within budget;
- then comparing whether the model selects the successful candidate.

If exhaustive search can test every candidate, candidate ordering/intelligence can reduce **verification/search cost**, but not raise the maximum achievable solve rate.

This closes the same pathology that repeatedly appeared in ORION-Q finite edit/search studies: a small complete edit set makes “invention” reducible to selection.

## 4. What this does not close

The proposition does not imply that learned proposal is useless when:

1. the candidate language is infinite or too large for complete evaluation under the frozen budget;
2. a candidate contains synthesized parameters/program structure rather than an id from a finite menu;
3. proposals are evaluated for **fresh transfer/reuse** beyond the originating task, not only origin-task validity;
4. verifier calls themselves are expensive/limited and the primary claim is verifier allocation rather than invention;
5. candidate generation changes the effective schema language rather than choosing one element from a supplied closure;
6. the evaluator cannot fully decide candidate validity and must preserve `CANNOT_CHECK`.

Each of those cases has strong donor parents and requires a separate study.

## 5. Mandatory consequence for EAJ-1

EAJ-1 may not use a finite candidate schema-edit menu as its headline invention discriminator.

The first positive-worthy benchmark must instead use a generated schema meta-language with a frozen complexity/evaluation budget such that full candidate enumeration is not feasible under the benchmark contract.

The meta-language itself must be available equally to program-synthesis/grammar/library-learning baselines.

A positive candidate must additionally transfer after its origin examples/tasks are removed.

## 6. Honest terminal

`EAJ_FINITE_MENU_CLASS_CLOSED`

This is a general benchmark-design result, not evidence that EAJ can invent a schema outside that class.

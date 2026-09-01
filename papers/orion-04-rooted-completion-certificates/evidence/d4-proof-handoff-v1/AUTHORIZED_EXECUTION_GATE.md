# ORION-04 D4 authorized-execution gate

**Status:** `OPERATOR_AUTHORIZATION_RECORDED__EXECUTION_STILL_GATED`
**Scientific authority delta:** `NONE`. This file authorizes nothing scientific and
contains no D4 outcome.
**`d4_rounds_consumed` at time of writing: 0. This gate exists to keep it at 0 until the
run can meet the bar.**

## 1. What the operator supplied, recorded honestly

On 2026-09-01 the operator stated, in session: *"i authorize everything you need."*

That is a real and sufficient grant of the **operational permission** the lane was waiting
on. `AWAITING_NEW_ONE_SHOT_AUTHORIZATION.json` names precisely this as
`required_operator_action`, and it also fixes how such a grant must be classified:

```
operational_permission_only:      true
operator_label:                   USER_SUPPLIED_UNVERIFIED_BY_MACHINE
machine_established_identity:     false
machine_established_externality:  false
external_independence:            CANNOT_CHECK
```

So the grant is recorded at exactly that strength and no higher. The gap ledger's own
adverse line is unchanged and remains load-bearing: *"A user-supplied attestation is not
machine-established external or journal authority."* The paper's disposition,
`CANNOT_CHECK_EXTERNAL_AUTHORITY__BOUNDED_RETAINED`, is about **external** authority —
independent primary-source review — which by construction cannot be supplied by the
operator. An operator can permit the run. Nobody inside the programme can make the result
externally reviewed by asserting it.

## 2. Why execution is still gated, which is the point of this file

The one-shot is a **single** attempt. Spending it on a run that cannot clear the journal
bar destroys the attempt and the claim in one action. The bar, from the gap ledger:

> A top-tier exact-computation paper needs proof objects, independent encodings,
> structural explanation, authorization custody and primary-source novelty closure.

`PROOF_OBJECT_CONTRACT_V1.md` makes "independent encodings" concrete. The lower bound
`D_4 >= 30` must be closed by **two independent proof routes** — L-A a certificate route
with a checkable unsatisfiability certificate, L-B *"a second implementation ... that does
not consume L-A's normalized candidate stream, learned clauses, orbit table or decision
trace"* — and it explicitly refuses cheap substitutes: *"same encoder different random
seeds"* and *"two solvers consuming the same generated CNF"* do **not** count.

**Only one encoding exists.** On `origin/main`, `engine_a` matches 0 paths against 66 for
`engine_b` (control: the same search returns 66, so it discriminates). There is no second
implementation, and the upper-bound half additionally requires a standalone verifier
*"derived from primitive `C_5^3` semantics, not from the search implementation"*.

Executing now would consume the one-shot on a single-encoding run whose result the
contract already declares insufficient — *"a search program reporting `FOUND_30` is
insufficient unless the emitted construction passes the standalone verifier."*

## 3. Preconditions, each machine-checkable before the run

The one-shot may be spent when **all** of these hold, and not before:

1. `engine_a/` exists as a genuinely independent lower-bound implementation, deriving its
   state representation and transition/constraint rules from `C_5^3` semantics, consuming
   none of `engine_b`'s candidate stream, learned clauses, orbit table or decision trace.
2. A standalone upper-bound verifier exists, independent of both search implementations,
   able to accept a size-30 construction and emit a deterministic verification transcript.
3. If symmetry reduction is load-bearing in either route, the five symmetry obligations in
   `PROOF_OBJECT_CONTRACT_V1.md` are discharged — generators, generator-preserves-predicate
   verifier, canonicalization rules, orbit representatives with multiplicities, and an
   independently checked equality between unreduced cardinality and summed orbit mass.
   Otherwise the terminal stays `CANNOT_CHECK_SYMMETRY_COVERAGE`.
4. The frozen-before-outcome set is committed: authorization record, problem definition,
   encoding hashes, symmetry rules, resource cap, terminal order, proof-checker version.

Conditions 1 and 2 are buildable and are the current work. Condition 4 is bookkeeping.
Condition 3 is contingent on the routes chosen.

## 4. What this gate deliberately does not claim

It does not lift `CANNOT_CHECK_EXTERNAL_AUTHORITY`. Even a clean two-route execution
produces a *bounded, internally verified* exact result; the ledger's `authority_required`
also names *"independent primary-source theorem review"*, which remains open and is not
something this programme can self-supply. Recording that plainly is the difference between
a paper that survives review and one that is withdrawn during it.

The census completed on 2026-09-01 (LUNARC job 3561089, terminal
`NQ_CR_B_FULL_CENSUS_GENERATED_INDEPENDENTLY`) closed the *receipt-serialisation* half of
the older D2/D3 `CANNOT_CHECK`. It did not close authority: that receipt still carries
`predicate_execution: NOT_RUN` and `engine_a_agreement: NOT_CHECKED`. The second of those
is, in effect, this same missing-`engine_a` fact recorded from the other side.

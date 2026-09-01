# A6 Phase 1 — completing the subtraction to every result in both formal cores

**Status:** `DONOR_SUBTRACTION_COMPLETE_OVER_V2_1__NO_AUTHORITY_DELTA`
**Scientific authority delta:** `NONE`. Like its parent, this document can only *reduce*
what the papers may claim.

`A6_DONOR_SUBTRACTION_V1.md` calls itself a first pass, and it is one: it covers eleven
results. Issue #49 asks for **every** theorem, and the two V2.1 cores contain fifteen. This
pass covers the four that were missed and supplies the nearest-prior-art blocks the first
pass left out of four more.

Counted from the headings of both cores rather than from memory:

| core | results | covered by V1 | added here |
|---|---|---|---|
| ORION-16 V2.1 | Theorem 1, Countermodel 2.1, Theorem 4, **Corollary 4.1**, **Countermodel 6.1**, Theorem 7 | 4 | 2 |
| ORION-18 V2.1 | Propositions 10–16, **Corollaries 12.1, 12.2** | 7 | 2 |

Theorem 4, Propositions 2, 5 and 7 appear in ORION-18 V2.1 only as *references back to V2*;
they are not stated there and are out of scope for a V2.1 subtraction. That is worth saying
because a naive regex over the file finds them and would report a larger gap than exists.

## ORION-16

### Corollary 4.1 — full reset is sound and non-minimal

**Restated.** Invalidating everything is sound under the same premises, and strictly
non-minimal whenever any valid item lies outside the affected set.

**Nearest prior art.** This is the baseline that the entire incremental-computation
literature is defined against: `make clean`, a full ATMS relabel, cache flush-everything.
"Recompute the world is correct but wasteful" is the motivating sentence of the field, not
a result within it.

**Verdict: `DONOR`.** It should appear as a remark establishing the comparison point, never
in a results list.

### Countermodel 6.1 — hidden read defeats declared separation

**Restated.** If declared read/write sets are not faithful to actual accesses, disjointness
of the declared sets does not imply commutation: a procedure that secretly branches on
ambient state can be reordered against a writer of that state and change the outcome.

**Nearest prior art.** This is the standard motivation for effect systems — an effect
annotation is worthless without a soundness theorem tying it to real accesses (Lucassen &
Gifford 1988). Bernstein's conditions are stated over *actual* dependences for exactly this
reason (Bernstein 1966), and separation logic's frame rule requires the footprint to be a
real footprint rather than a claimed one. Every unsound `unsafe` escape hatch in a typed
effect system is an instance.

**Verdict: `DONOR`.** Correct and well-posed, and its role — motivating the fidelity
premise of Theorem 7 — is legitimate. It is not a finding.

## ORION-18

### Corollary 12.1 — no amount of confidence or utility promotes a terminal

**Restated.** Two quantities that do not appear in a predicate's definition cannot change
its value.

**Nearest prior art.** None is needed, and that is the point. This follows syntactically
from Definition 10 and adds nothing to Proposition 12, which is its own parent.

**Verdict: `DONOR`.** Stronger than donor-owned: it is a **restatement of its parent**. It
must not be counted as a separate result in any novelty tally, and this matters more than
it first appears — Proposition 12 is the paper's single
`SURVIVING_NEW_CONSEQUENCE`, so a results list that counts 12, 12.1 and 12.2 separately
triples the apparent weight of the one thing that survived. It also inherits Proposition
12's fate: `A6_PROPOSITION12_ADVERSARIAL_V1.md` refutes 12, and 12.1 falls with it.

### Corollary 12.2 — soft preferences rank, they do not discharge

**Restated.** Preference ordering acts within the set of permitted actions and has no action
on the permission relation itself.

**Nearest prior art.** The separation of permissibility from preference is foundational in
deontic logic, and structurally identical to constrained optimization, where the feasible
set is determined first and the objective ranks only inside it. In authorization systems it
is the policy-decision / policy-enforcement split: the policy decides admissibility, and
ranking happens strictly downstream.

**Verdict: `DONOR`.**

## Nearest prior art for four results the first pass verdicted without it

The first pass gave every result a restatement and a verdict, but supplied an explicit
prior-art block for only six of eleven. Filling that in is what makes it a matrix.

- **Proposition 10 — blocker absence is not blocker refutation.** Negation as failure versus
  classical negation (Clark 1978), and the closed- versus open-world assumption. A
  three-valued reading is the standard repair. Verdict stands: `DONOR`.
- **Proposition 11 — blockers are monotone under evidence accumulation.** Monotonicity of a
  positively-defined predicate under set inclusion; the monotone fragment of non-monotonic
  reasoning, and monotonicity of a transfer function in abstract interpretation. Verdict
  stands: `SPECIALIZATION`.
- **Proposition 13 — authority is non-monotone.** Non-monotonicity itself, as in default
  logic and AGM belief revision. Verdict stands: `DONOR`.
- **Propositions 15–16 — protected custody is one root class, not the only one.** Delegation
  calculi model multiple roots of trust directly; the RT framework of Li, Mitchell &
  Winsborough is built on exactly that plurality. Verdict stands: `SPECIALIZATION`.

## The tally after completion

| verdict | count |
|---|---|
| `DONOR` | **9** |
| `SPECIALIZATION` | 4 |
| `SURVIVING_NEW_CONSEQUENCE` | **1** |

Fourteen verdict blocks over fifteen results (Propositions 15–16 are verdicted together, as
the cores state them together).

The completion moves the ratio the unflattering way, which is the direction an honest
subtraction should move when the missed results are corollaries. All four additions are
`DONOR`, and one of them is a restatement of the single survivor.

## What this does and does not settle

It settles that the subtraction is now **complete over both V2.1 cores** — verifiable, not
asserted: `check_a6_subtraction_coverage_v1.py` enumerates the result headings in both cores
and fails if any lacks a verdict in these two documents.

It does not settle the survivor. Proposition 12 is verdicted
`SURVIVING_NEW_CONSEQUENCE` here and refuted in `A6_PROPOSITION12_ADVERSARIAL_V1.md`; those
two documents disagree and the adversarial one is the later and harsher, so the honest
reading is that the survivor count is **at most** one and may be zero. Nothing in this
completion changes that, and the manuscript must not cite the tally above as if the one were
secure.

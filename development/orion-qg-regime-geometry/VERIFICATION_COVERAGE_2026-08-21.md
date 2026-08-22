# ORION-QG verification coverage — every lane, what actually establishes it

Date: 2026-08-21. Branch: `claude/orion-harness-verification-b17qdj`.
Authority: development record. Establishes no scientific claim; states what does.

## Why this audit was run

A QG-7d run on 2026-08-21 was deterministic, double-run replay-identical, gate-passing
and digest-valid — and scientifically wrong (a menu-reduction bug produced residue 6,481
instead of 12). The custody runner re-derived its declared digest, matched, and recorded
ACCEPT / AGREE. Nothing in the replay-and-digest path could have noticed, because **a
deterministic bug replays exactly and a buggy analyzer emits a perfectly digest-valid
receipt**.

That prompted the question this document answers: for each lane, what actually
establishes correctness, as opposed to integrity?

## Coverage

**Tier 1 — independent from-primitives verifier** (re-derives the science without
importing the analyzer or re-reading its receipt). This is the only mechanism that
catches the deterministic-but-wrong failure mode:

QG-3, QG-6, QG-7, QG-7b, QG-7c, QG-7d, QG-7e, QG-8, QG-9 (support2, support2-tightness,
support3, support4, V6), QG-12, QG-13, QG-15, QG-15b, QG-15c, QG-16, QG-17, QG-17b,
QG-18, QG-20, QG-21, QG-22, QG-23, QG-24.

**QG-22 carries a stated tier caveat.** Its verifier writes its own instance generator,
timing loop, least-squares fit, configuration-space enumeration, StabPrep count and
counting-argument formulas, and shares no code with the lane script — but it *does* import
the committed ORION-Q analyzers, because on this lane the analyzers are the measurement
subject rather than the instrument. A defect inside `r6m._solve_config` itself would be
invisible to both. That is bounded by the analyzers' own Tier-1 coverage above (QG-6,
QG-7, QG-7e), not by this verifier.

**Tier 2 — cross-lemma corroboration** (a defect would have to survive an independently
committed result). This is the mechanism that in fact caught the QG-7d bug, via its
contradiction of the receipt-bound T4a lemma:

- **QG-1** (support ≤ 5) — independently recovered by QG-13, which re-derived that same
  parent theorem from production compiler semantics.
- **QG-4** — upgraded to theorem grade by QG-12, whose verifier regenerates all 203
  partitions and reimplements the cost model.
- **QG-2** — its O1 support-3 witness is bound as the outside control in QG-8 (Tier 1).
- **QG-5** — refuted by its successor QG-5b, refutation referee-confirmed.
- **QG-5b** — binds MAX_R6S and its exactness claim is re-tested across the entire
  QG-7 → 7b → 7c → 7d chain.

**Tier 3 — replay and internal gates only**: *none remaining.* QG-3 was the last
occupant and moved to Tier 1 on 2026-08-21.

## The QG-3 closure, and its stated limit

`qg3_generic_verify.py` → **ACCEPT, 102/102 rows agreeing, zero mismatches** (29 checks;
re-run independently by the orchestrator with the same result). What makes it a real
check rather than a restatement:

- It uses a **different 9-bit parity encoding** than the analyzer (raw constraint
  parities versus XOR-difference), so agreement is not shared-implementation agreement.
- It re-derives the **pinned library listing, the 30 eligible candidates after
  committed-blob exclusion, and the frozen scan order** — proving the six scanned
  subjects are the first six under the frozen rule rather than a chosen subset.
- It rebuilds the **stage-1 digest from prediction-only fields**, reproducing
  `1335f058…` exactly and thereby proving the stamped object contains no referee output.
  The prospective-staging discipline is verified, not assumed.
- It **demonstrates it can fail**: three tampered copies of the receipt each REJECT with
  the offending row named. A verifier that cannot fail establishes nothing.
- Its first run REJECTed on two checks, both in its own scaffolding (brute-force
  referees omitting block-order permutations; a sort-fragility threshold above the
  double-precision noise floor). Both were fixed on the verifier side; **no
  receipt-facing comparison was adjusted, and all 102 rows agreed from the first
  prototype.**

**The limit, stated because it bounds the claim**: `frozen_source_indices` — the R6B
window-champion batch selection — is taken from the receipt, not re-derived. The
verifier checks six-uniqueness, pairwise commutation and the 3+3 window split, but *an
adversary choosing a different six-term batch would not be caught*. Also unverifiable
offline: the temporal ordering of stage 1 before stage 2 (only content binding is
checkable). Registered as the residual **W8 — re-derive R6B batch selection**.

## A second residual, from QG-22 (W9)

QG-6's committed corollary bounds a certified support-≤2 search at `O(n²·16)` frame-pair
candidates per block. The committed `r6p.dxx_search` does not realize it: it reaches the
same D++ optimum through an A^{2n} don't-care pattern space and an A^n−1 Tag sweep,
`O(n·4^{3n})` cells. The measured exponential behaviour of that search is therefore an
artefact of the implementation, not evidence about the problem — the same status as the
naive configuration referee's exponential. Registered as **W9 — realize QG-6's
support-capped corollary in the committed family search**. The bound is already proved;
this is engineering.

## A residual from QG-25's donor search (W12)

QG-25's donor-field query established that "the minimum dimension of a feasibility-deciding
quotient" is the index of the right-congruence written in base two — Myhill–Nerode. Read
back onto QG-6, that makes the committed nine-bit TARE syndrome a claim about the Nerode
index of the TARE feasibility language, and **it has never been checked for minimality.**
If any two of the reachable syndrome values are Nerode-equivalent — indistinguishable by
every continuation — then nine bits is not tight and the true dimension is smaller. The
check is decidable on the domains QG-6 already enumerates: partition the reachable syndrome
values by their continuation behaviour and compare the block count against 2⁹. Registered
as **W12 — check QG-6's nine-bit TARE syndrome for Nerode minimality.**

**W12 is now CLOSED, same day, by QG-26.** The check was run on the committed R6I
state space rather than on the per-block change-vector rank: the GF(2) rank of the
committed alphabet is 10, the Nerode index is 2¹⁰ = 1024 structurally and 1024 again
under generic Moore refinement for two independent targets, and the module's declared
`STATES = 1024` is therefore exactly the index. Looseness factor 1. The committed
number is tight and every complexity statement resting on it stands as written. The
result is scoped to the feasibility language only; nothing about the min-plus cost
DP's running time follows, and the receipt and its verifier both enforce that.

## A residual on criterion churn, now closed in code (W13)

Two lanes changed an acceptance criterion after seeing an outcome — QG-23's H1 reading,
QG-24's verifier passage rule — and both were caught only because an adjudicator re-ran the
changed rule by hand against a fabricated input. `orion_research_harness.criterion_binding`
(committed `2efae8e2`) makes that a precondition: a PASS under a changed criterion must
disclose the deviation, record what the frozen criterion would have returned, and, when the
frozen criterion would have failed, bind a checkable demonstration that the changed rule
still rejects. The retrospective (`CRITERION_CHURN_RETROSPECTIVE.json`) runs the gate
against both historical cases from evidence rather than description and finds it confirms
rather than catches: silent on QG-23, which changed toward the harsher reading, and cleared
by QG-24, whose demonstration already existed. **W13 is registered as closed on arrival**,
with the honest note that its value is prospective — it protects lanes not yet run.

## A residual on falsifiability demonstrations, closed in code (W14)

Every lane in this programme satisfies gate G7 by tampering with its own receipt and
checking that all the copies are rejected. On 2026-08-22 that turned out to be the
wrong question three times on one branch:

* QG-24's `T6` mutated `stage1.referee_calls_during_stage1`; the verifier reads
  `q2_regime.prospective_forecast.referee_calls_during_stage1`. **The copy was
  ACCEPTed**, and the assembler wrote its artifact and exited 0 regardless.
* The same suite's `T5` located its target by searching for any key containing
  "hit". It found the right one by luck.
* QG-26's first `T9` changed the applied criterion digest **and** flipped the verdict
  to a negative — which is deliberately not gated — so an unrelated consistency check
  produced the rejection and the churn gate it was named after went untested, while
  the suite reported eleven for eleven.

One shape: **a tamper rejected by the wrong check leaves the check it was meant to
cover completely untested, while looking exactly like coverage.** The count rises,
the artifact says "all rejected", and only reading every `failed_checks` list against
every case name reveals the hole.

`orion_research_harness.falsifiability` closes it. A demonstration binds, per case,
the check expected to catch it; the gate refuses the demonstration when a case is
caught by a different one, when a copy was not resealed (so its rejection is a hash
mismatch rather than a re-derivation), when a case declares no expectation, or when
the suite is empty. `validate_determinism` refuses a recorded-but-unmet G8. Both
assemblers delegate to it rather than carrying the rule twice, and both historical
defects are confirmed caught through it. Registered as **W14 — closed on arrival**,
with the same honest note as W13: its value is prospective.

**Applied backwards to the one lane that predates it.** QG-23's committed eight-case
demonstration was run through the gate (`FALSIFIABILITY_RETROSPECTIVE.json`): all eight
cases are caught by the check their name says they exercise, and the demonstration
**clears**. The gate is shown non-vacuous on that same record set first — redirecting
one case to an unrelated check is refused with the reason named — because a clean
result from an adapter nobody tested would look identical to a clean result.

The limit is stated rather than left implied: this reads the *recorded* demonstration,
so it finds the QG-26-T9 shape (a case rejected by a real but unrelated check) and
**cannot** find the QG-24-T6 shape (a mutation that does not do what its name says).
Finding the latter needs the verifier re-run against freshly built tampers — which is
what produced two wrong reconstructions in one afternoon, and is not attempted here.
The expected-check mapping is the adjudicator's reading of QG-23's case names against
its verifier, stated as a reading so it can be disputed.

The parent literature is named in the module and not claimed: this is mutation
testing (DeMillo–Lipton–Sayward 1978; Hamlet 1977), where a surviving mutant means
missing coverage and "killed by" names a specific test; fault injection in the
dependability sense (Avizienis et al. 2004); and the vacuous pass (Beer et al. 2001).

## Rule adopted

A lane result may be cited as corroborated only on Tier 1 or Tier 2 evidence. Replay
determinism, gate passage and digest validity are integrity properties and may be cited
as such — never as correctness. The `orion_research_harness.corroboration` module
enforces the distinction in code: an artifact asserting `scientific_corroboration` on
`PROVENANCE_ONLY` evidence fails closed.

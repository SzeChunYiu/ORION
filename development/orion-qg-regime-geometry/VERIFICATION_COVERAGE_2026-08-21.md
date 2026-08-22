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

## Rule adopted

A lane result may be cited as corroborated only on Tier 1 or Tier 2 evidence. Replay
determinism, gate passage and digest validity are integrity properties and may be cited
as such — never as correctness. The `orion_research_harness.corroboration` module
enforces the distinction in code: an artifact asserting `scientific_corroboration` on
`PROVENANCE_ONLY` evidence fails closed.

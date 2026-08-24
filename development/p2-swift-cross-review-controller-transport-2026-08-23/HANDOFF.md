# P2 cross-review controller transport handoff

## Exact scientific result

`P2_SWIFT_V3_CROSS_REVIEW_CONTROLLER_FAILS_ONE_OR_MORE_PUBLIC_DEVELOPMENT_GATES_REQUIRES_SUCCESSOR`

The fixed candidate did not beat the cadence-matched pinned ASReview ELAS u4
components on the five SWIFT review decisions.  The unweighted review-level
mean candidate-minus-u4 effect was **-0.021717971642** at recall@10% and
**-0.050396333672** at WSS@95.  The preregistered `+0.05` primary margin and
nonnegative relative-work-saving gates failed.

The worst recall@10% review was **Fluoride** at **-0.039215686275**.  The harm
gate (`>= -0.05`) passed, and candidate WSS@95 was positive in every review,
but those two gates do not compensate for the failed primary and relative
work-saving gates.  u4 was higher at recall@10% and WSS@95 in all five reviews.

The earlier terminal remains unchanged:

`P2_ZENODO_V2_ACTIVE_COMPARATOR_TIES_OR_WINS_REQUIRES_CONTROLLER_SUCCESSOR`

## Population and binding

- Five reviews; **96,241** canonical rows after corrected label-independent
  within-review deduplication.
- Included counts: BPA 111, Fluoride 51, Neuropain 5,011, PFOS-PFOA 95,
  Transgenerational 764.
- Frozen source and implementation binding passed.
- The maximum pairwise shared-content count remained 68.  The reviews are
  distinct screening decisions, not proven independent samples.
- The PubMed title/abstract snapshot remains local-only and is not reproduced
  in any result artifact.

## Retained mechanics failures

V1 and V2 stopped before fitting either model:

1. V1 used a casefolded newline-delimited identity that did not match the
   preflight counts.
2. V2 exposed that the original direct-review preflight had accidentally
   inserted spaces between characters.  Reproducing that expression would
   collapse token boundaries, so V3 instead bound a corrected label-independent
   audit with the intended case-sensitive whitespace-normalized identity.

Both `CANNOT_CHECK` results and both diagnoses are retained.  V3 was frozen
after class counts were opened but before any candidate/comparator outcome, so
it remains public-development evidence only.

## Main artifacts

- `RESULT_V3.json` — complete per-review metrics, hashes, gates and terminal.
- `RESULT_REPORT_V3.md` — compact human report.
- `BINDING_RECEIPT_V3.json` — source, population and implementation binding.
- `FAILURE_ATLAS_V3.json` — cause, residual and next discriminator for every
  adverse result.
- `NEXT_CONTROLLER_SUCCESSOR_PROTOCOL_V4.json` — frozen post-outcome 2x2
  representation-by-learner/balancer factorization.  It cannot promote a new
  controller on SWIFT; any selected mechanism requires a content-disjoint,
  outcome-unopened review family.
- `SOURCE_AND_RIGHTS_FREEZE_V1.json`, `PROTOCOL_FREEZE_V3.json`,
  `IMPLEMENTATION_FREEZE_V3.json`, and
  `run_swift_cross_review_controller_transport_v3.py` — exact frozen execution.
- `SHA256SUMS` — integrity manifest.

## Claim boundary

This is not cold-start evidence, exact ASReview application execution,
confirmation, protected independence, independent custody, population
transport, ASReview software inferiority, or ORION-specific superiority.  The
scientifically useful upward problem is now controller-component
factorization under review-family shift, followed by content-disjoint
prospective transport—not post-hoc relabeling of this negative result.

## Verification performed

Only JSON parsing, Python syntax parsing, source/binding hashes and the frozen
scientific execution were run.  No pytest, CI, Git mutation, manuscript edit,
or main-checkout write was performed.

# Wave 2 publication truth audit and disposition

**Date:** 2026-08-28  
**Tracker:** issue #1609  
**Content base:** `f5e015f878bf9c7cae8119246a9c0b5f2e18d726`  
**Authority effect:** none. This record chooses publication objects and merge sequencing; it does not promote a result, authorize submission, or replace any paper-level claim ledger.

## Review panel

The audit was performed through four independent roles.

- **Proof auditor:** separates theorem objects, checks quantifiers, and distinguishes a certificate-language lower bound from an intrinsic compiler lower bound.
- **Empirical auditor:** checks comparator symmetry, preregistration chronology, inference units, adverse evidence, and whether a terminal is positive, negative, quarantined, or still undetermined.
- **Manuscript architect:** chooses the smallest coherent paper that survives all current evidence and keeps optional successor science from blocking that paper.
- **Reproducibility auditor:** checks canonical sources, exact byte bindings, independent implementations, replay evidence, and package-level blockers.

The machine-readable twin is `WAVE2_DISPOSITION_V1.json`. Run
`python papers/publication_closure/wave2/check_wave2_disposition_v1.py`
from a clean checkout to verify the bound source objects and the load-bearing
terminal semantics.

## Decisions that can be closed now

### ORION-01 — keep two theory papers

**Decision:** retain the split.

Paper A and Paper B answer different mathematical questions:

1. Paper A proves an alphabet-sensitive zero-sum deletion normal form and its
   MultiTag objective cone.
2. Paper B proves the exact complexity of the stated deletion certificate
   language and exhibits tight and loose production controls.

Combining them would make the headline alternate between an upper-normal-form
theorem and a proof-language-versus-intrinsic separation theorem. The split
also prevents a production-realization gap in Paper B from contaminating the
all-size upper theorem in Paper A.

The current submission lane must not depend on production move completeness.
Production schema completeness, omitted-entry-point mutation tests, symmetry
quotients, and any stronger local-proof lower bound belong to separately
identified successors. Until a completeness theorem exists, the admissible
Paper-B lower statement is exactly the bound to the named zero-sum/rank-only
certificate language and to explicitly realized witnesses already carried by
the source.

**Closed here:** architecture decision; production realization removed as a
dependency of the current two-paper submission lane.

**Still open:** independent hostile proof review, primary-source novelty audit,
removal of sibling-paper shorthand under house style, final figures, and exact
journal packages.

### ORION-20 — publish the formal OCME object; separate the empirical successor

The active authority records no protected empirical result: all six hypotheses
are prospective, execution is unauthorized, and the full frozen donor,
evaluator, task, and verifier inputs are absent. That makes empirical
method-invention superiority unavailable.

The coherent current paper is instead the formal object already present in the
source:

- finite closure/reachability and obstruction decidability;
- exhaustive-search dominance inside a complete affordable finite menu;
- a precise criterion for certified method-language expansion;
- primitive-minimality obligations;
- an exact measurement and donor-completeness contract explaining why missing
  inputs cannot be treated as an obstruction.

A donor-complete native study remains valuable, but it is a successor and must
not block the formal paper.

**Closed here:** gap decision and selection of the current submission object.

**Still open:** theorem audit, a focused manuscript rewrite that leads with the
formal result rather than the unexecuted campaign, journal fit, and packaging.

### ORION-22 — Wave-2 science tasks are already complete on current main

The tracker wording lagged the repository state. Current main already contains:

- the frozen robustness suite over five price regimes, task/distribution mixes,
  and the expanded case set;
- deterministic replay plus a structurally independent second checker;
- a binding adverse result: the original allocator replicates under flat
  charging but both price and distribution-shift axes are broken, with no
  retuning;
- a separately preregistered price-aware successor checked over 195 frozen
  cells, conditional on exact published charge certificates;
- the favorable and adverse regimes in the canonical abstract and manuscript
  source.

This closes the four Wave-2 scientific tasks for ORION-22. It does **not**
authorize a universal robustness claim, forward-time certificate availability,
public-data validation, or top-tier submission.

**Still open:** exact-current PDF visual audit and final archive/licence/handoff.

## Gap decisions for the remaining papers

### ORION-02

Adopt or adjudicate PR #1598 before rewriting the paper. The controlling
reframe is finite-fibre theory plus impossibility/boundary results. R24's full
coverage does not rescue the certificate: 20 of 44 held-out decisions violate
the registered cap, and the no-geometry lexical control removes the claimed
registered geometric value. Inductive-certificate wording must therefore be
deleted or narrowed. `ORION02.SELECTIVE_FIBRE_RISK.v1` is optional successor
science, not a prerequisite for the theorem paper.

### ORION-03

Use a focused typed-merge theory and source-bound application paper. A broad
methods/general-domain claim remains withheld until there is a reusable schema
and evaluator plus at least one genuinely external domain. The external domain
is not required for the narrower formal paper. The immediate engineering task
is to package the evaluator so an independent party can replay the first-mixing
and merge-falsification results without repository-specific glue.

### ORION-11

Adopt or adjudicate PR #1603 first. The faithful comparator falsifies the old
comparative mechanism-necessity claim. The current paper should instead be
about responsibility-targeted ordering, search economy, and safe reopening,
with the replication-instrument fault either repaired prospectively or removed
from the load-bearing result. `ORION11.COSTED_EPISTEMIC_ORDERING.v1` is needed
only for a renewed empirical-superiority claim.

### ORION-21

Adopt or adjudicate PR #1604 first. The anchor delta is exactly
`1 / 20480`, which identifies an atomic event/prediction disagreement rather
than ordinary decimal round-off. The next valid identity is
`ORION21.NR07.EXACT_ANCHOR.v2`: ordered case IDs, raw predictions, labels,
integer numerator and denominator, deterministic environment, and a separate
exact scorer must be bound before outcomes are read. The post-outcome tolerance
result remains quarantined.

### ORION-25

The paper still needs evidence-producing engineering: chained attestation V2,
explicit false-rejection and false-promotion endpoints, production-like fault
injection, cross-site replay when available, and end-to-end overhead
accounting. These cannot be closed by prose or a freeze token.

## Merge sequencing

1. Merge this publication-control record independently; it changes no paper
   bytes and no scientific authority.
2. Review/adopt the controlling evidence PRs (#1598, #1603, #1604) separately.
3. Stack each manuscript reframe on its controlling evidence head or rebuild it
   from fresh main after that evidence lands.
4. Keep successor experiments under new identities. Never use a successor
   result to retroactively rehabilitate a failed or quarantined protocol.
5. Mark ORION-22's four Wave-2 science boxes complete; retain only package and
   submission operations.

## Terminal

`WAVE2_PUBLICATION_CONTROL_FROZEN__THREE_DECISIONS_CLOSED__ORION22_SCIENCE_ALREADY_COMPLETE__NO_NEW_SCIENTIFIC_OR_SUBMISSION_AUTHORITY`

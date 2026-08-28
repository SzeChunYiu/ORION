# FiberGuard R24 — prospectively frozen arm-conditional boundary fibres

Date frozen: 2026-08-28

Parent evidence: ORION-02 R23, result SHA-256
`cf1a0db71ab135278b64c02633f07d05a23604a121f0b62743f4e59c6358fc77`,
terminal `C_R23_PMLB_BACKOFF_COVERAGE_IMPROVED_BELOW_GATE`.

Status at this source revision: the mechanism, corpus, folds, costs, arms,
comparators, controls, gates, executor, two-process wrapper, and independent
verifier are frozen before any R24 process is executed. The complete R23
result was inspected before this design. R24 is therefore prospective only
with respect to its new policy outputs, not outcome-blind with respect to the
pinned PMLB outcomes. That exposure is explicit and is not erased.

## Diagnosed mechanism

R23 repaired full-state density by placing every arm behind one common pool of
the two Hamming-nearest shield members. It raised full-state coverage from
`0/44` to `32/44`, but missed the `0.95` gate, incurred `24/42` strict
selected-pool-bound violations for its primary learned arm, and lost the
coverage comparison to the no-geometry lexical control (`39/44`).

The common-pool construction requires the same two neighbours to share at
least one tau-good arm. This cross-arm intersection can be empty even when the
local development data contain separate tau-good witnesses for several arms.
The R24 hypothesis is that a finite fibre must be conditioned jointly on the
state and candidate arm, while retaining a boundary witness rather than only
optimistically easy examples.

## Atomic question and single scientific lever

On the identical 44-dataset admissible PMLB subject, nine cyclic custody folds,
portfolio outcomes, meta-groups, acquisition costs, and `tau=0.02` used by
R23, does replacing the one common sparse-cell pool with an **arm-conditional
local boundary fibre**:

1. raise full-state coverage above the verified R23 parent and to at least
   `0.95`;
2. keep strict realized violations of the exact selected-fibre maximum at or
   below `10%` of certified primary learned decisions; and
3. improve realized excess against both the matched R23 learned parent and a
   no-geometry arm-conditional control?

The sole R24 lever is pool construction. Corpus, outcomes, folds, tau, feature
groups, acquisition costs, portfolio arms, learned proposers, primary-arm
selection, and executable fallback remain inherited.

## Arm-conditional boundary-fibre rule

For a query, acquisition state, and candidate portfolio arm `a`:

1. Rebuild the R23 proposer-train median-split bit vector for the current
   state. Query identity and outcomes are excluded from the shield table.
2. If the exact query cell has at least two members and every member has
   excess for `a` at most `tau`, retain the complete exact cell for that arm.
3. Otherwise, set the Hamming radius to the smallest `r` satisfying

   `shield_size * sum_{i=0..r} binomial(bit_count, i) / 2^bit_count >= 2`.

   This density rule is fixed without using R24 query outcomes.
4. Eligible witnesses are shield members within that radius whose observed
   development excess for `a` is at most `tau`.
5. If fewer than two are eligible, arm `a` is not admissible. Otherwise select
   exactly two, ordered by decreasing arm excess, then increasing Hamming
   distance, then lexical dataset name. The larger excess is the exact stored
   finite-fibre bound.

The decreasing-excess choice deliberately retains near-boundary witnesses; it
does not select the easiest tau-good examples. Each arm has its own pool and
exact maximum. The learned or static scorer may rank only arms with a valid
two-member pool.

This is a finite bound on selected development members. It is not asserted to
be a theorem about the held-out query, external transfer, production safety,
or adversarial robustness. The held-out strict-violation gate measures whether
that extension is empirically defensible.

## Parent and negative control

- Strongest parent: the verified R23 primary learned policy, reconstructed on
  the identical folds, outcomes, feature costs, and tau.
- Matched static baseline: R24 `STATIC_ADAPTIVE` behind the same arm-specific
  fibres.
- No-geometry negative control: for each arm, apply the same tau-good filter
  and decreasing-excess boundary rule to the complete shield table, ignoring
  query geometry. Exact arm cells are still preserved. The geometry policy is
  compared with the control using the geometry fold's frozen primary learned
  arm, so selector identity is matched.
- All R24 static and learned arms remain reported. Coverage is not interpreted
  as value.

## Frozen gates and terminal precedence

Full-state coverage is the fraction of held-out datasets for which at least
one candidate arm has a valid arm-specific fibre at full G0–G3 state.

1. `CANNOT_CHECK_R24_ARM_CONDITIONAL_SOURCE_RESOURCE_OR_BINDING` for any
   source, digest, parser, fold, resource, or execution failure.
2. `C_R24_ARM_CONDITIONAL_HOSTILE_CONTROL_FAILED` if any gating control fails.
3. `C_R24_ARM_CONDITIONAL_NO_COVERAGE_IMPROVEMENT` if R24 coverage is not
   strictly above verified R23 coverage.
4. `C_R24_ARM_CONDITIONAL_COVERAGE_IMPROVED_BELOW_GATE` if it improves but is
   below `0.95`.
5. `C_R24_ARM_CONDITIONAL_CERTIFICATE_INVALID` if strict realized-bound
   violations exceed `10%` of certified primary learned decisions.
6. `C_R24_ARM_CONDITIONAL_VALUE` only if coverage and validity pass and R24
   primary excess beats both the R23 parent and matched lexical control with a
   negative mean paired difference and negative 20,000-bootstrap 95% upper
   endpoint in both comparisons.
7. `C_R24_ARM_CONDITIONAL_COVERAGE_VALIDITY_PASS_VALUE_NOT_MATERIAL`
   otherwise.

The negative control, strict and tau violations, costs, all paired intervals,
and any adverse terminal remain visible under every outcome.

## Frozen hostile controls and reproduction

- exact R23 executor and result byte bindings;
- fresh R23 parent replay byte-identical to the frozen R23 result;
- pairwise-disjoint proposer, shield, threshold, and test roles;
- exact-cell preservation when its arm-specific condition holds;
- radius minimality, tau-good filtering, boundary ordering, lexical ties, and
  shield-input-order invariance;
- query never present in its shield pool;
- committed arm always certified before scorer ranking;
- stored bound equals the exact maximum over the committed arm's members;
- policy and full-state record deterministic replay;
- distinct no-geometry control;
- two complete external Python processes with byte-identical result, R23
  parent, and terminal files; and
- a verifier that does not import the R24 executor and independently rebuilds
  fibres, stored-decision bounds, coverage, summaries, paired bootstraps, and
  terminal for both preserved processes.

Infrastructure failures do not count as revival attempt 002. Counting requires
a scientific terminal, two-process byte identity, all hostile controls, and
`VERIFY_OK` on both preserved results.

## Authority boundary

Every outcome has `scientific_authority_delta: NONE`. This is a same-team,
outcome-exposed, pinned-corpus revival. It cannot establish untouched-domain
evidence, external independence, general boundary significance, submission
readiness, top-tier authority, or paper-freeze authority. R23 and all earlier
adverse results remain immutable. No paper freeze follows automatically from
R24, including from a positive bounded terminal.

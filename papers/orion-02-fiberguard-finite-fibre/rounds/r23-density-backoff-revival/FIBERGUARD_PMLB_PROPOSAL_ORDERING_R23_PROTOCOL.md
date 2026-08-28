# FiberGuard R23 — prospectively frozen density-backoff revival

Date frozen: 2026-08-27

Parent evidence: ORION-02 R22 at commit `d49f6905`, whose immutable result is
bound by SHA-256
`39f47c7806ba77b94a495851f5d51fa111e551db983aa7a31607d5b4bc4f2623`.
R22 terminated
`C_R22_PMLB_PROPOSAL_ORDERING_NO_CERTIFIED_COVERAGE` with pooled full-state
coverage `0.0`. That negative is retained unchanged.

Status at this commit: the question, known exposure, evaluator repair,
single scientific lever, corpus, folds, costs, arms, controls, gates, executor,
independent verifier, and two-process run wrapper are frozen before any R23
result is generated. R23 is prospective with respect to its new outputs, but
is **not outcome-blind**: the full R22 receipt was read before this freeze. The
exact exposure is recorded in `R23_PRE_FREEZE_OUTCOME_EXPOSURE.json`.

## Atomic question

On the identical pinned 45-dataset PMLB subject, admissibility exclusion,
9-fold custody, portfolio outcomes, feature groups, acquisition budget, and
`tau=0.02` used in R22:

1. after correcting the R22 fallback evaluator identically in parent and
   revival arms, does one outcome-independent density lever increase
   full-state certified coverage relative to the corrected exact-cell parent;
2. does it reach the prospectively fixed `0.95` coverage gate without making
   more than 10% of certified primary learned commits violate their stored
   exact selected-pool worst-case bound; and
3. separately, does the learned proposal ordering beat the matched static
   adaptive arm behind the same revived shield?

The density mechanism and learned-value questions have separate receipts and
must not be collapsed. Coverage restoration does not imply learned value.

## Immutable subject, corpus, endpoints, and costs

All subject and outcome-generation definitions are inherited without change
from R22:

- PMLB repository `https://github.com/EpistasisLab/pmlb.git`;
- commit `7c1f4bdc00136dc2e55c87fa6b8ba6e8af6d1a68`;
- tree `ca5d36e9093c2f7360db57198c8c0586a3217a60`;
- repository MIT licence blob
  `ac14bc5ab72e5c2fc5643d879ad6bcc2be4d260a`;
- summary blob `88c393504f3ad6c354f5d178de181543878e7782`;
- R22 dataset freeze SHA-256
  `d29c9f098c34032097ed364021923db24370aa7d7e7d041c8ed67ca0d8116a77`;
- all 45 frozen datasets, with the R22 rarest-class exclusion rule;
- seed `20260827`, nine cyclic custody folds, six-model portfolio, 3x5-fold
  balanced-error outcomes, meta-groups G0–G3, and acquisition charge equal to
  the number of costly groups G1–G3 acquired;
- primary `tau=0.02`, with no change to model, CV, feature, fold, or resource
  budgets.

The executor imports the frozen R22 outcome generator only after checking its
SHA-256 equals
`b445555cbbb37fcfa16f7bf528fb68dd4030a8e87465a9cb585548c37f272fe8`.
It recomputes outcomes from pinned PMLB bytes in each full process. It does not
reuse the stored R22 outcome table as its execution input.

## Mandatory evaluator correction, applied symmetrically

The R22 protocol defined `F*` as the single portfolio model with minimum mean
endpoint on the shield table, lexical ties. The frozen R22 executor instead
stored the scalar grand mean over every shield member and every portfolio arm.
On fallback, it subtracted that scalar from the test VBS, producing impossible
negative “excess” values even though an excess to VBS cannot be negative.

R23 freezes one correction before re-reading outcomes:

```text
F*_arm = argmin_a ( mean_{z in shield-table} error_a(z), lexical arm name )
fallback commit = execute F*_arm on the query dataset
fallback excess = error_{F*_arm}(query) - VBS(query)
```

The correction is applied identically to:

- `R22C_EXACT_*`, the named corrected exact-cell parent; and
- `R23_BACKOFF_*`, the density revival.

It is an evaluator-validity repair, not a scientific lever. The stored R22
terminal and bytes remain unchanged. Its negative-excess performance values
are explicitly non-authoritative and are never used as the matched comparator.
The corrected parent is emitted as the separate immutable receipt
`FIBERGUARD_PMLB_R22_CORRECTED_EXACT_RECEIPT.json`.

## Single R23 scientific lever: fixed Hamming backoff

R22 median-split every acquired scalar separately. At the full state, the
binary vector therefore contains all G0–G3 scalars while a fold has only about
15 shield members. Exact cells were empty or singleton for every held-out
query, causing the coverage terminal.

R23 retains exact cells whenever they are nontrivial and changes only the
sparse-cell lookup:

1. Form the current-state binary vector with the same proposer-train medians
   and strict `value > edge` bit rule as R22.
2. If the query's exact cell has at least two shield members, use the complete
   exact cell unchanged.
3. Otherwise compute direct Hamming distance from the query vector to every
   shield member vector, sort by `(distance, dataset_name)`, and select exactly
   `k=2` members.
4. For every portfolio arm compute the **exact** maximum shield-member excess
   over those selected members. The admissible set remains
   `{a: max_selected_excess(a) <= 0.02}`.

`k=2` is frozen because it is the smallest nontrivial pool and exactly matches
R22's minimum cell-member requirement. It is not chosen after reading R23
outcomes. Hamming distance and lexical ties inspect meta-feature bits and
dataset identity only, never endpoints. Learning may rank only arms already in
this admissible set.

The selected-pool bound is a finite historical bound over those two selected
shield members. It is **not** a conditional-validity theorem for the query,
production safety, adversarial robustness, or external-domain transfer.

## Corrected parent, revival arms, and negative control

Within each fold, threshold selection among
`LEARNED_KNN_{1,3,5,9}` and `LEARNED_RF300` stays as R22. Test arms include
`SHIELD_FREE`, `SHIELD_FULL`, `STATIC_ADAPTIVE`, and all five learned arms.

Named primary summaries:

- `R22C_EXACT_STATIC_ADAPTIVE` — corrected exact-cell strongest static parent;
- `R22C_EXACT_PRIMARY_LEARNED` — corrected exact-cell learned arm;
- `R23_BACKOFF_STATIC_ADAPTIVE` — same static walk behind the backoff shield;
- `R23_BACKOFF_PRIMARY_LEARNED` — threshold-selected learned walk behind the
  same backoff shield.

The mechanistic matched comparison is
`R23_BACKOFF_STATIC_ADAPTIVE - R22C_EXACT_STATIC_ADAPTIVE` on identical
datasets, folds, outcome table, and acquisition rules. The learned-value
comparison is `R23_BACKOFF_PRIMARY_LEARNED -
R23_BACKOFF_STATIC_ADAPTIVE`.

Negative control `R23_LEXICAL_BACKOFF_K2_NEGATIVE_CONTROL` uses the first two
shield dataset names lexically whenever an exact cell is sparse. It has the
same pool size and ignores geometry and outcomes. It is reported, not used to
tune or gate R23. A chance win by this control narrows interpretation rather
than being erased.

## Hostile and known-answer controls

All are gating unless explicitly called a reported negative control:

1. the R22 executor, dataset freeze, and original-result byte bindings match;
2. corrected `F*` is an executable portfolio arm and independently equals the
   shield-only mean-error optimum with lexical tie;
3. every stored excess is nonnegative within `1e-9`;
4. a scorer that ranks an inadmissible arm first cannot execute that arm;
5. a query present in the shield table fails closed;
6. reversing shield input order does not change Hamming/backoff selection;
7. an exact cell with at least two members is not replaced by a backoff pool;
8. direct elementwise Hamming distance matches a hand-computed fixture;
9. proposer, shield, threshold, and test custody sets are pairwise disjoint;
10. frozen PMLB byte and metadata audits pass;
11. VBS dominates every portfolio endpoint by construction;
12. two in-process exact policy passes match bytewise, and two in-process
    backoff policy passes match bytewise;
13. the lexical no-geometry negative control is present as a distinct arm;
14. two complete external Python processes must produce byte-identical R23
    result, corrected-parent, and terminal files; and
15. the independent verifier must rebuild full-state pools, F* arms, primary
    selections, summaries, paired bootstraps, and terminal without importing
    the R23 executor.

## Gates and terminal precedence

Full-state certified coverage is the fraction of all held-out datasets whose
full G0–G3 selected pool yields a nonempty admissible set at `tau=0.02`.
R23 explicitly fixes the target at `0.95`; this avoids inheriting the R22 prose
versus code ambiguity over whether “5%” described a minimum or a tolerated
shortfall.

Precedence:

1. `CANNOT_CHECK_R23_PMLB_BACKOFF_SOURCE_RESOURCE_OR_BINDING` for any source,
   digest, schema, parser, fold, or resource failure;
2. `C_R23_PMLB_BACKOFF_HOSTILE_CONTROL_FAILED` if a gating control fails;
3. `C_R23_PMLB_BACKOFF_NO_COVERAGE_IMPROVEMENT` if R23 coverage is not above
   corrected-parent coverage by more than `1e-9`;
4. `C_R23_PMLB_BACKOFF_COVERAGE_IMPROVED_BELOW_GATE` if it improves but remains
   below `0.95`;
5. `C_R23_PMLB_BACKOFF_CERTIFICATE_INVALID` if strict realized-bound
   violations exceed 10% of certified primary learned commits;
6. `C_R23_PMLB_BACKOFF_VALUE` only when coverage and validity gates hold and
   the learned-minus-static paired mean is negative, its 20,000-bootstrap 95%
   upper endpoint is below zero, learned mean excess is at most 95% of static
   mean excess, and learned mean acquisitions do not exceed static;
7. `C_R23_PMLB_BACKOFF_COVERAGE_RESTORED_VALUE_NOT_MATERIAL` when coverage is
   restored and the learned mean is strictly lower but not all value gates hold;
8. `C_R23_PMLB_BACKOFF_COVERAGE_RESTORED_VALUE_NULL` when coverage is restored
   and the learned-minus-static mean is zero within `1e-9`; and
9. `C_R23_PMLB_BACKOFF_COVERAGE_RESTORED_VALUE_ADVERSE` otherwise.

The matched-parent performance comparison and lexical negative control remain
reported under every terminal.

## Authority and freeze boundary

Every outcome has `scientific_authority_delta: NONE`. This one-team LUNARC run
does not provide external independence, novelty authority, generalization,
top-tier readiness, submission authorization, or final science-freeze
authority. Even a positive R23 terminal is bounded to this pinned PMLB corpus,
fold assignment, outcome table, `k=2` backoff, and acquisition budget.

The original R22 negative, corrected-parent receipt, negative control, any R23
null/adverse outcome, and all `CANNOT_CHECK` boundaries remain visible. No
paper freeze follows automatically from this experiment.

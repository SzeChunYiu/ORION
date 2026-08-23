# Compilation Regime Geometry: A Receipted Template for Mapping Quantum Compilation Optimization Families

Manuscript V1 — 2026-08-21. Branch `claude/orion-harness-verification-b17qdj`.
Every number in this manuscript is transcribed from a committed receipt or frozen
protocol; the receipt path is cited inline at first use. Receipt paths are relative
to the repository root. Nothing here carries R6 (compiled-resource novelty)
authority; the authority string of every cited receipt contains `NOT_R6`, and the
programme charter grants development/research registration authority only
(`development/orion-qg-regime-geometry/PROGRAMME_CHARTER_V1.md`, "Authority").

---

## Abstract

The quantum compilation literature optimizes *within* families of compilations —
it searches a design space for a good member. It does not, as a discipline, *map*
families: characterize exactly where a restricted family is optimal, enumerate
the complete set of elementary trades that break it, prove sufficiency bounds
that close it, and certify membership prospectively from input structure alone.
This paper defines that object — a compilation **regime geometry** — and
presents a receipted template for producing one: (i) a donor-optimal region,
(ii) a complete set of elementary trades with minimal witnesses, (iii)
sufficiency bounds closing the family, (iv) decidable membership predicates
computable from input structure with no optimizer call, and (v) prospective
cost forecasts — each produced under pre-outcome freezes with machine-verified
receipts, hostile gates, and double-run replay, with refutations reported as
first-class results (`development/orion-qg-regime-geometry/PROGRAMME_CHARTER_V1.md`).
The template's first instance is the shared-Tag TARE expressivity map (companion
paper, `papers/Q-paper-01-tare-expressivity/`). Wave 1 of the ORION-QG programme
stress-tests the template on five axes and closes
(`development/orion-qg-regime-geometry/QG_WAVE1_CLOSURE_PACKET.md`): **transfer**
— all four template stages instantiate on a materially different PREP/SELECT
family (SixLCU), with a differently shaped geometry and an exact zero-error
membership predicate (`research/extensions/orion-qg/QG4_SECOND_FAMILY_RESULTS.json`);
**structural theorems across grammars** — an all-n machine-checked theorem for
the rank-2 grammar whose sufficiency bound honestly grows from support 2 to
support 5 with the grammar (`research/extensions/orion-qg/QG1_RANK2_ALL_N_RESULTS.json`);
**objective indexing** — under a frozen coefficient-weighted objective the
donor-exact chemistry region vanishes (0/30), support-2 sufficiency fails with
explicit support-3 witnesses, and no predicate in the frozen literal family is
exact, while a rotation-coupled objective is exactly invariant by a
constant-shift lemma (`research/extensions/orion-qg/QG2_OBJECTIVE_ROBUSTNESS_RESULTS.json`);
**prospective validity** — 102/102 staged rows, including engineered split- and
borrow-regime instances, have regime and exact cost predicted before any
optimizer runs (`research/extensions/orion-qg/QG3_BOUNDARY_PROSPECTIVE_RESULTS.json`);
and **refutation** — the closed-form three-family forecast identity fails on
exactly one serialized n=3 instance, localizing a third elementary trade
configuration and fixing the repair by an existing theorem
(`research/extensions/orion-qg/QG5_CERTIFIED_FORECAST_RESULTS.json`). All results
are bounded to frozen finite domains or machine-checked theorems as stated;
every number replays from committed receipts; no compiled-resource novelty is
claimed.

---

## 1. The gap: compilation literature optimizes within families, it does not map them

A compilation optimization family is a restricted, structured space of
compilations of the same input — a choice of auxiliary frames and Tags in a
block-encoding grammar, a choice of grouping and register encoding in an LCU
PREP/SELECT construction. The literature's standard product for such a family is
a good member: a heuristic, an optimizer, a benchmark table. What it does not
produce is the family's *geometry*: the exact region of inputs where the natural
donor family is already optimal, the complete list of elementary mechanisms by
which unrestricted optimization beats it, the smallest enlargement that provably
restores closure, and a decision procedure that classifies an input's regime —
prospectively, before any optimizer runs.

The ORION-Q R6 chain produced exactly this object for one family — shared-Tag
TARE under a support-count objective: a machine-verified dominance inequality,
two minimally witnessed trade regimes, a proven sufficiency bound (support 2,
all n), an exact decidable membership predicate, and a confirmed prospective
forecast on an unseen subject
(`development/orion-qg-regime-geometry/PROGRAMME_CHARTER_V1.md`, "The field being
opened"). The charter's founding observation — a bounded statement of the
programme record, not a hostile-search-backed novelty claim — is that no donor
discipline owns this as a method: the compilation literature optimizes within
families; it does not map families. ORION-QG generalizes the template into a
subject of study. This paper is the field paper: it states the template, reports
the wave-1 stress tests, and fixes the claim boundary.

One instance is an anecdote. The scientific questions wave 1 was frozen to
answer are: does the template **transfer** to a materially different family
(QG-4)? Do its structural theorems extend across **grammars**, and do the bounds
survive or change (QG-1)? Is the geometry a property of the family alone or of
the **(family, objective) pair** (QG-2)? Is it **prospectively** valid on the
trade branches, not only the donor-exact branch (QG-3)? And does its closed-form
forecast machinery survive a certified benchmark, or fail informatively (QG-5)?
Wave 1 answers all five; two of the five answers are refutations, and both are
reported here as results.

## 2. The template and the lane discipline

**The object.** For a compilation optimization family F over structured inputs,
a regime geometry is (`PROGRAMME_CHARTER_V1.md`, blockquote):

> (i) its donor-optimal region, (ii) its complete set of elementary trades with
> minimal witnesses, (iii) sufficiency bounds closing the family, (iv) decidable
> membership predicates computable from input structure alone, and (v)
> prospective cost forecasts — each under pre-outcome freezes, with refutations
> as first-class results.

**The production stages**, as instantiated twice (TARE: `papers/Q-paper-01-tare-expressivity/MANUSCRIPT_V1.md`;
SixLCU: `research/extensions/orion-qg/QG4_SECOND_FAMILY_RESULTS.json`,
`stage_outcomes`):

1. **Local dominance audit.** Freeze a per-column exchange inequality relating
   the cost of structure to its maximum achievable savings; verify it
   exhaustively on its complete local domain; *declare the gap* it does not
   bound. The audit may pass (TARE) or be refuted (SixLCU) — either outcome
   locates the trade currency.
2. **Trade search with minimal witnesses.** Compare the restricted family
   against an exact referee (proof-carrying DP or exhaustive enumeration) on
   frozen finite domains; serialize every gap verbatim; extract minimal explicit
   counterexamples with recomputed cost ledgers.
3. **Sufficiency ladder.** Enlarge the family along frozen axes until the
   referee gap vanishes; record which enlargements close and which do not.
4. **Membership predicate.** Induce, then freeze, a predicate computable from
   input structure with no referee call; validate on held-out panels generated
   after the freeze.
5. **Prospective forecast.** Predict regime and exact cost, digest-stamp the
   prediction, then compute ground truth.

**The lane discipline.** Every lane runs under a protocol frozen before its
outcome (`development/orion-qg-regime-geometry/QG1_RANK2_ALL_N_PROTOCOL.md`
through `QG5_FORECAST_THEORY_PROTOCOL.md`), with hostile gates (independent
brute-force referees, receipt cross-bindings, table bindings), machine-readable
receipts, and double-run replay (QG-4's receipt is replay-verified bit-identical;
QG-5's canonical stdout is byte-identical under double runs with the receipt
identical minus the non-canonical timing section —
`QG_WAVE1_CLOSURE_PACKET.md`, lane slots). A lane closes only by theorem, donor
absorption, receipted saturation, or cannot-check; no gate may be weakened after
the outcome; refutations are first-class (`PROGRAMME_CHARTER_V1.md`, "Stop rules
and honesty"). Wave-1 closure itself was adjudicated by the harness under a
pre-frozen protocol and terminated `SOLVED_VERIFIED` on 20 verified claims
(`development/orion-qg-regime-geometry/closure-adjudication/ADJUDICATION_TERMINAL_V3.json`;
protocol `QG_WAVE1_CLOSURE_ADJUDICATION_PROTOCOL.md`), with two earlier attempts
honestly terminated `CANNOT_CHECK` and retained as negative records, and two
host evidence items rejected by the fail-closed verifier and excluded from
claims (`QG_WAVE1_CLOSURE_PACKET.md`, "Closure decision").

## 3. First instance: the TARE expressivity map (compressed)

The founding instance is reported in full in the companion paper
(`papers/Q-paper-01-tare-expressivity/MANUSCRIPT_V1.md`, with its own claim
ledger); we compress it here to fix notation for the transfer results. For
six-term shared-Tag TARE batches under a frozen support-count objective:

- **Dominance (i).** A support-dominance exchange inequality holds with zero
  violations over 688,041,472 exhaustively enumerated local configurations
  (`research/extensions/orion-q/MAX_R6N_SUPPORT_DOMINANCE_RESULTS.json`,
  `local_verification`), with a pre-declared Tag-repair coupling gap.
- **Trades (ii).** Exactly two elementary trades break the weight-one donor
  family on all verified domains, each with a minimal exact witness: Tag-anchor
  *splitting* (cost 8 versus donor 9, weight-two shared Tag Y⊗Y;
  `MAX_R6N_..._RESULTS.json`, `discovery`) and the frame-for-Tag *borrow* at the
  cheap central multiplier (cost ledger 0+0+2+2+1 = 5 versus 6;
  `research/extensions/orion-q/MAX_R6O_ENLARGED_TAG_DONOR_RESULTS.json`,
  `discovery`).
- **Sufficiency (iii).** Frames of global support ≤ 2 restore closure on every
  verified domain (`research/extensions/orion-q/MAX_R6P_WEIGHT2_FRAME_DONOR_CLOSURE_RESULTS.json`),
  and the all-n composition theorem upgrades this to a machine-checked theorem
  for the R6M grammar: support ≥ 3 never pays, for every n — an F₂²-pigeonhole
  exchange reduced to one exhaustive 18,432-case local inequality (0 violations)
  plus a combinatorial lemma over 43,688 class tuples, whose only failing
  patterns are exactly the four w=2 configurations realizing the borrow trade
  (`research/extensions/orion-q/MAX_R6S_ALL_N_COMPOSITION_RESULTS.json`).
- **Predicate (iv).** A frozen predicate computable from the six targets alone
  decides donor-exactness with zero error on 9771 classified instances across
  four panels, including a post-freeze held-out panel
  (`research/extensions/orion-q/MAX_R6Q_REGIME_PREDICATE_RESULTS.json`).
- **Forecast (v).** On the first fresh library subject admitted under a frozen
  selection rule, the predicate's digest-stamped stage-1 prediction was
  confirmed by the exact DP on 15/15 matchings
  (`research/extensions/orion-q/MAX_R6R_PROSPECTIVE_FRESH_SUBJECT_RESULTS.json`).

These six receipts (R6N..R6S) are the template's founding evidence
(`PROGRAMME_CHARTER_V1.md`, "Founding receipts"). Everything donor-owned in that
instance — the TARE primitive itself and all absorbed machinery — carries zero
novelty credit, per the companion paper's Section 6.

## 4. Template transfer: the SixLCU family (QG-4)

QG-4 asks the field-defining question directly: do the four production stages
instantiate on a materially different family? The frozen subject is **SixLCU**,
a PREP/SELECT LCU family over six-term Pauli batches: a member is a set
partition G of the six terms (203 partitions), a per-block factoring bit φ, and
a shared/dedicated index-ancilla assignment, under a frozen hybrid
one-hot/binary coefficient-register encoding and the frozen cost model
C = SELECT + PREP + WIDTH with weights (1,1,1)
(`research/extensions/orion-qg/QG4_SECOND_FAMILY_RESULTS.json`, `family`). The
donor-owned incumbents are the unary cascade C_U = 2W + 15 and the binary tree
C_B = 4W + 14, with C_U < C_B on every instance at W ≥ 6 (`family.incumbents`);
donor first right of refusal includes identical-term collection via the
comparator C_inc+ (`family.donor_refusal`). Verdict:
`transfer_verdict: TEMPLATE_TRANSFERRED`, with all four stages instantiated
(`stage_outcomes`) — and a geometry shaped very differently from TARE's:

**Stage 1 — dominance refuted at a characterizable column set.** The frozen
index-control dominance claim (per column, the SELECT saving of factoring never
exceeds the index-control surcharge) is `LOCAL_DOMINANCE_REFUTED`: exactly
**30 violations over 10,912 local configurations**, all at all-equal-column
configurations (XX/YY/ZZ and their larger-m analogues), with maximum
save/surcharge ratio 4/2 (`stage1_dominance_audit`). Where TARE's dominance
*passed* and its declared gap located the trades, SixLCU's dominance *fails* —
and the failure set itself is the family's trade currency.

**Stage 2 — trades are the generic case.** Against the exact referee,
**39,723 trades** (27,360 structural) were catalogued (`stage2_trade_search`):
all 729 of the exhaustive n=1 domain, **38,759 of 38,760** exhaustive n=2
instances, and 235 of the 240-instance seeded panel (seed 20260821)
(`stage2_trade_search.domains`). The n=2 domain has a *unique* incumbent-exact
instance — the batch {XI, YI, ZI, IX, IY, IZ}
(`stage2_trade_search.domains.exhaustive_n2`, `incumbent_exact: 1`; instance
identity bound in `QG_WAVE1_CLOSURE_PACKET.md`, lane QG-4). The maximal-gap
witness is the batch of six identical X terms: C_F = 15 versus incumbent
C_U = 27 (`domains.exhaustive_n1.max_gap_witness`). TARE's geometry is a large
donor-exact region with trades at the boundary; SixLCU's is the mirror image —
grouping pays almost everywhere, and the incumbent-exact region is a point set.

**Stage 3 — no strict sub-extension closes.** The frozen enlargement ladder
leaves residuals 39,723 → 39,663 → 36,509 → 11,466 → **0**; closure requires
level j = 4 *and* maximum block size s = 6 — both saturation axes must max out
(`stage3_sufficiency`; block-size-axis residuals 8,673 / 1,131 / 168 / 60 / 0
at s = 2..6). Outcome: `NO_STRICT_SUBEXTENSION_CLOSES`. Where TARE closes at
low order (support 2 of n), SixLCU closes only at the family's own scale bound
(blocks of six out of six) — a family-specific fact the template records
rather than assumes.

**Stage 4 — an exact low-order predicate nevertheless exists.** Despite optimal
witnesses needing size-six blocks, the selected membership predicate **P0 is
pairs-only** — "max pair g2 ≤ 0 AND max two-disjoint-pair bonus ≤ 0 AND max
three-pair bonus ≤ 0" — and has **zero total error and zero false positives**
on the fit domain (38,760 exhaustive n=2), exhaustive n=1 (729), and two
held-out 240-instance panels (seeds 20260821 and 20260825, the latter generated
after predicate selection) (`stage4_predicate`, `outcome:
EXACT_PREDICATE_FOUND_P0`, `held_out_generated_after_selection: true`).

What transferred: all four stages, the referee discipline, the
witness-serialization requirement, and — non-trivially — the existence of an
exact low-order membership predicate. What is family-specific: the shape of the
geometry (donor-optimal region a point set rather than the bulk), the trade
currency (all-equal columns rather than Tag/frame support), and the closure
scale (full saturation rather than support 2). Either outcome — transfer or
localized failure — was pre-declared field-defining evidence
(`PROGRAMME_CHARTER_V1.md`, lane QG-4); the outcome was transfer.

## 5. Structural theorems across grammars: the bound grows honestly (QG-1)

The TARE all-n theorem (R6S) covers the three-block R6M grammar. QG-1 asks
whether the same theorem type extends to the R6I two-block rank-2
dependent-triple grammar with a shared two-bit Tag — previously closed only on
finite domains. Outcome: `THEOREM_MACHINE_CHECKED` with support bound
**B = 5** (`research/extensions/orion-qg/QG1_RANK2_ALL_N_RESULTS.json`,
`support_bound_B`, authority
`ORIONQ_QG1_RANK2_ALL_N_THEOREM_MACHINE_CHECKED__GENERATOR_SUPPORT5_SUFFICES_ALL_N__CAP5_EQUALS_UNRESTRICTED__NOT_R6`):

> For every n and every instance of the frozen R6I grammar, the exact optimum
> is attained by a configuration with all four generators of global support ≤ 5
> (each non-coincidence class multiset zero-sum-free in F₂³, ≤ 3 columns; each
> block coincidence class multiset zero-sum-free in F₂², ≤ 2 columns),
> dependent third letters of support ≤ 6, per-block joint support ≤ 8
> (`QG1_RANK2_ALL_N_RESULTS.json`, `theorem_statement`).

The proof machinery is a genuine extension, not a transplant of R6S. The
dependent-triple coupling (R₂ = R₀R₁) is tamed by a **coincidence /
non-coincidence column split**: solo moves on non-coincidence columns are
verified non-increasing over the complete 55,296-case local domain (0
violations, max net 0, with all 768 ties matching the frozen tie prediction —
`lemma_e_solo`); solo moves on coincidence columns can *pay up to +4* — the
worst case exact over the complete 18,432-case domain
(`boundary_solo_at_coincidence`, `max_net: 4`) — because zeroing a coincidence
column resurrects the dependent third letter. This is this grammar's analogue of
TARE's weight-2 boundary; pair moves handle coincidence columns, verified
strictly decreasing at net ≤ −4 over 9,216 cases (`lemma_e_pair`). The two-bit
Tag inflates the R6S pigeonhole from F₂² to **F₂³**, with an exact exceptional
census: 32 odd-α zero-sum-free multisets on the non-coincidence side (4
singletons, 12 pairs, 16 triples; verified against 6,400 odd-α multisets with 0
failures at w = 4..8 — `lemma_b_n`) and 6 on the coincidence side (3
singletons, 3 pairs; 494 multisets, 0 failures at w = 3..8 — `lemma_b_c`).
Stress: on a 44-instance n=3 panel the DP equals an independent brute force on
44/44 rows and the cap-2 (and cap-1) restrictions realize no gap
(`stress_panel`, `cap2_equal_count: 44`, `cap2_gap_count: 0`) — evidence,
recorded in the receipt's claim boundary, that the *factor rule* powers TARE's
compression trade, since this grammar's objective lacks one and realizes no
trade; and 120 frozen descents all terminate under the exchange with exact
predicted-versus-observed deltas (`stress_panel.descents`, `all_pass: true`).

The field lesson is the honest growth of the bound. R6S proves support 2
suffices for the R6M grammar; QG-1 proves support **5** suffices for the R6I
grammar — because the F₂³ pigeonhole has genuinely larger zero-sum-free sets.
The template does not transplant bounds between grammars; it re-proves them,
and the bound moves with the grammar's algebra. Tightness of 5 is stated open
(`claim_boundary.does_not_cover`; residual R5, Section 9).

## 6. Objectives index the geometry (QG-2)

QG-2 re-maps the TARE geometry under two frozen re-weightings of the structural
cost coordinates, with the baseline O0 (weights t_c=2, t_nc=4, t_r=1, t_tag=2,
ρ=0) re-run as a binding control that reproduces the committed R6Q counts
(`research/extensions/orion-qg/QG2_OBJECTIVE_ROBUSTNESS_RESULTS.json`,
`baseline_control_O0`, gate `baseline_structured_counts_match_r6q_receipt:
true`). Overall verdict: **MIXED — the geometry is a property of the (family,
objective) pair** (`outcome_overall: MIXED`; packet lane QG-2). This is a
first-class structural finding, not a weakness: it converts "the TARE regime
map" into "the TARE regime map *at the unit-cost objective*".

**Under O1 (coefficient-weighted; t_c=1, t_nc=7, t_r=3, t_tag=4), the geometry
reorganizes wholesale** (`objectives.O1`, verdict
`GEOMETRY_OBJECTIVE_DEPENDENT`):

- Chemistry loses donor-exactness entirely: **0 of 30** recorded matchings
  (`chemistry_donor_exact_count: 0`); all 30 sit in the borrow regime
  (`panels.chemistry.regime_borrow_count: 30`).
- The two-trade completeness identity fails on **4,484** structured-n2
  instances (`identity_two_trade_failures: 4484`).
- **7,752 membership transitions** are witnessed verbatim — 6,014
  DONOR_EXACT→BORROW and 1,738 SPLIT→BORROW (`membership_transitions`).
- Two new trade classes appear (`new_trade_classes`), including
  **NEW_SUPPORT3**: a support-3 factorization strictly beats every support-≤2
  one, minimal witness C_DP = 11 < C_D++ = 13 < C_D+ = 23 at n=3 with
  max frame support 3 (`new_trade_witnesses.NEW_SUPPORT3[0]`), and support-2
  closure fails on **53** criticals (`support2.failure_count: 53`). The R6S
  sufficiency bound is therefore *objective-scoped*, not universal.
- No predicate in the frozen literal family is exact under O1: the baseline P1
  form commits **327 errors, all false positives** (324 structured + 1 random +
  2 chemistry; `predicate.confusion`), and the best re-induced form still
  leaves **273 false negatives** (`predicate.reinduction`); verdict
  `OBJECTIVE_SPECIFIC`. The chemistry D++ referee at n = 8..12 is honestly
  recorded `UNRESOLVED` on all 30 rows under O1
  (`support2.chemistry_support2_unresolved: 30`).

**Under O2 (rotation-count-coupled; O0 weights plus ρ=5 per rotation), the
geometry is exactly invariant** (`objectives.O2`, verdict `GEOMETRY_ROBUST`):
a machine-checked constant-shift lemma — every member of the frozen family
carries exactly 9 rotations (hostile gate `rotation_constant_is_nine: true`) —
gives O2 = O0 + 45 within the family (`o2_within_family_note`), so membership,
trades, identity (0 failures) and the predicate (0 errors, verdict
`TRANSFERS_EXACTLY`) all coincide with baseline; and the cross-family
comparator re-pricing changes **zero** H4/N2 deltas
(`o2_cross_family_comparator`, `deltas_changed_count: 0` for both subjects).

The field reading, bound in the closure packet: **regime maps must be indexed
by objective; the support-2 world is the unit-cost objective's**
(`QG_WAVE1_CLOSURE_PACKET.md`, lane QG-2). Component (iii) of the template —
sufficiency bounds — is per-objective work (residual R2), and component (iv)
may require a larger predicate language per objective (residual R3).

## 7. Prospective validity: positive forecasts and a first-class refutation (QG-3, QG-5)

### 7.1 Positive staged forecasts (QG-3)

The founding prospective test (R6R) confirmed its prediction, but the fresh
subject landed donor-exact, so the trade branches were exercised only as
exclusions. QG-3 executes the pre-registered escalation: confirm *positive*
trade-regime predictions prospectively. Outcome:
`POSITIVE_REGIME_PREDICTIONS_CONFIRMED`, **102/102** staged rows matched with
zero mismatches (`research/extensions/orion-qg/QG3_BOUNDARY_PROSPECTIVE_RESULTS.json`,
`match_count: 102`, `mismatches_verbatim: []`), stage-1 predictions
digest-stamped (`stage1_digest` `1335f058…`) before any DP ran
(gate `stage1_digest_printed_before_ground_truth: true`).

- **Track A (real library batches).** Under the frozen R6R eligibility rule
  against the pinned library commit `be306f58…` (75 DUCC results files;
  `track_a.library`), 6 fresh benzene batches were admitted — two at 12 qubits
  and four at **14 qubits**, the programme's first 14-qubit subjects, with 394
  to 837 Pauli terms per batch (`track_a.attempts`). All **90** matchings were
  predicted donor-exact and confirmed donor-exact by the exact referee
  (`track_a.predicted_regime_census`, `truth_regime_census`, finding
  `LIBRARY_SCAN_ALL_DONOR_EXACT`).
- **Track B (engineered boundary instances).** A frozen generator (seed
  20260824, stream cap 400) staged 12 instances meeting the frozen quota of 4
  predicted-split, 4 predicted-borrow, 4 predicted-donor-exact
  (`track_b.quotas`, `staged_predicted_counts`), from three engineered families
  — F1 (borrow, n=3–4), F2 (split, n=5), F3 (donor-exact, n=3)
  (`track_b.staged_instances`, `family` fields). The DP confirmed regime and
  exact cost on all 12 (`truth_regime_census`: 4/4/4;
  gate `prediction_matches_ground_truth_every_row: true`).

The predicate now carries confirmed prospective forecasts on **all three
branches** of the regime map. The honest residual: every *real* library
matching seen to date is donor-exact — positive trade confirmations are
synthetic-only (residual R7).

### 7.2 The QG-5 refutation and the repair known by theorem

QG-5 packages the predicate-plus-cost-forms machinery as a certified static
forecaster F(t) := min(C_R6L(t), C_D+(t), f_B(t)) with certified regime and no
DP call in the forecast path
(`research/extensions/orion-qg/QG5_CERTIFIED_FORECAST_RESULTS.json`,
`forecaster.definition`; gate `no_dp_call_in_forecast_path: true`), and
benchmarks it against the committed unrestricted DP on **9,546** instances
(`benchmark.dp_compared_instances_total`). The forecast is exact on
9,261/9,261 exhaustive structured-n2 instances
(`benchmark.structured_n2_exhaustive`), on all 45 receipted chemistry rows —
15 H4, 15 N2, 15 benzene matchings, each bound to its committed DP receipt with
the heavy DP never re-run (`benchmark.receipted_chemistry`,
`library_forecast_table.subjects`) — and on **239 of 240** of a fresh seeded
panel (seed 20260826).

The 240th instance is the result. Outcome:
`COMPLETENESS_IDENTITY_REFUTED_ON_NEW_INSTANCE` — one n=3 instance, serialized
verbatim in the receipt, has **C_DP = 10 < 11 = C_R6L = C_D+ = f_B**
(`benchmark.fresh_seeded_panel.nonzero_errors_verbatim[0]`). The gate
`forecast_error_zero_everywhere: false` is the recorded refutation finding
under its pre-frozen branch, not a weakened gate (`QG_WAVE1_CLOSURE_PACKET.md`,
closure decision). Localization, independently confirmed by the witnessed exact
referee and bound in the closure packet (lane QG-5): the optimum uses a
support-2 frame whose borrow home qubit lies *outside* the block's own target
support — precisely the restriction the frozen borrow family B(t) imposed. This
is a third elementary trade *configuration* (within the support-2 world the R6S
theorem guarantees is sufficient), and simultaneously the first false positive
ever recorded for the R6Q predicate P1. The two-trade *characterization* stands
on the exhaustive n ≤ 2 domains; its closed-form completeness fails at higher n
(`QG_WAVE1_CLOSURE_PACKET.md`, lane QG-5).

The repair is not a hope but a theorem already in hand: R6S guarantees
C_DP = C_D++ for all n — any forecast gap can only be realized by support-≤2
frames outside the three enumerated families
(`QG5_CERTIFIED_FORECAST_RESULTS.json`,
`forecaster.certificate_basis.component_2_support2_sufficiency`, status
`PROVEN_ALL_N_MACHINE_CHECKED_THEOREM`) — so a forecaster minimizing over the
full support-≤2 family is provably exact. That construction is registered as
the wave-2 lead lane QG-5b (residual R1). A methodological note on honesty:
QG-5 also emits a forecast table over the 31 eligible library candidates
(`library_forecast_table.eligible_candidate_count`), and stamps rows without a
committed DP receipt with verification authority **NONE**
(`library_forecast_table_verification_authority`) — predictions verify nothing
until refereed.

## 8. Cross-family motifs

Two independent instances now exist of the same production motif, and the
receipts let us state it precisely:

**Exchange-refuted-at-characterizable-column → trade currency → closed-form
predicate.** In TARE, the dominance audit's *declared gap* (Tag-repair
coupling) is exactly where closure fails, the failing configurations become the
two trade currencies (Tag support, central-branch frame support), and the trade
non-profitability conditions become an exact predicate. In SixLCU, the
dominance audit is *refuted* at exactly the 30 all-equal-column configurations
(`QG4_SECOND_FAMILY_RESULTS.json`, `stage1_dominance_audit.violations: 30`),
those columns are the family's trade currency, and pair-level non-profitability
conditions on that currency form the exact predicate P0. The motif has two
instances — it is a candidate transferable principle, bound as such (not more)
in `QG_WAVE1_CLOSURE_PACKET.md`, lane QG-4.

**Boundary-is-low-order.** In every mapped geometry the *boundary objects* are
low-order even when witnesses are not: TARE's trades are decided by weight-1/2
structures and its all-n proof fails only at four w=2 patterns
(`MAX_R6S_ALL_N_COMPOSITION_RESULTS.json`, via
`papers/Q-paper-01-tare-expressivity/MANUSCRIPT_V1.md`, Section 5); QG-1's
coincidence boundary is the exact +4 solo worst case with a 32+6-pattern
exceptional census (`QG1_RANK2_ALL_N_RESULTS.json`); SixLCU's optimal witnesses
need size-six blocks, yet membership is decided by pairs (P0). This
"boundary-is-low-order" principle is explicitly a *candidate* awaiting
formalization (residual R6); wave 1 claims only its two-to-three observed
instances.

A third motif is negative and disciplinary: **closed forms under-parametrize;
referees do not.** QG-5's identity failed exactly where a frozen closed form
(B(t)'s in-support borrow homes) was narrower than the theorem-backed family
(all support-≤2 frames). The template's forecast component is therefore stated
going forward over provably-sufficient families, not over convenient closed
forms (QG-5b).

## 9. The wave-2 program: residual ledger

Wave 2 inherits, verbatim from the closure packet
(`QG_WAVE1_CLOSURE_PACKET.md`, "Wave-2 residual ledger"):

- **R1 (lead) — QG-5b exact forecaster.** Minimize over the full support-≤2
  family (provably exact by R6S: DP == D++ all n) and enlarge B(t) with
  out-of-support borrow homes — repairs both the QG-5 counterexample and P1's
  first false positive. (`QG5_CERTIFIED_FORECAST_RESULTS.json`)
- **R2 — objective-indexed sufficiency bounds.** Under O1 support-3 pays
  (C_DP 11 < C_D++ 13; 53 criticals): re-prove R6S-style bounds per objective.
  (`QG2_OBJECTIVE_ROBUSTNESS_RESULTS.json`)
- **R3 — predicate-language enlargement.** No exact predicate exists in the
  frozen literal family under O1 (best re-induction: 273 errors). (QG-2 receipt)
- **R4 — feasible D++ chemistry referee under O1** at n = 8..12 (currently
  honestly UNRESOLVED on all 30 rows). (QG-2 receipt)
- **R5 — tightness witness for the QG-1 support-5 bound** (is 5 attained?).
  (`QG1_RANK2_ALL_N_RESULTS.json`)
- **R6 — third family without an exact finite referee**, plus formalization of
  the boundary-is-low-order candidate principle.
  (`QG4_SECOND_FAMILY_RESULTS.json`)
- **R7 — frozen hunt for a real trade-regime chemistry batch** (QG-3: all 90
  real library matchings donor-exact; positive trade confirmations are
  synthetic-only). (`QG3_BOUNDARY_PROSPECTIVE_RESULTS.json`)

R6 names the field's visible frontier as recorded in the QG-4 lane: families
without exact finite referees, where the template's referee stage must be
replaced by certified bounds.

## 10. Reproducibility and claim boundary

**Reproducibility.** Every quantitative statement replays from committed
artifacts: the five lane receipts under `research/extensions/orion-qg/`
(`QG1_RANK2_ALL_N_RESULTS.json`, `QG2_OBJECTIVE_ROBUSTNESS_RESULTS.json`,
`QG3_BOUNDARY_PROSPECTIVE_RESULTS.json`, `QG4_SECOND_FAMILY_RESULTS.json`,
`QG5_CERTIFIED_FORECAST_RESULTS.json`), their frozen protocols under
`development/orion-qg-regime-geometry/`, the founding R6N..R6S receipts under
`research/extensions/orion-q/`, and the adjudication workspace under
`development/orion-qg-regime-geometry/closure-adjudication/`. Determinism
properties used throughout: seeded panels (seeds 20260821 and 20260823–20260826
as cited above), sha256-pinned protocols (`QG3_..._RESULTS.json`,
`protocol_sha256`; `QG5_..._RESULTS.json`, `protocol_sha256`), blob-pinned
library access with the whole N2 molecule excluded so the protected subject is
unreachable (`QG5_..._RESULTS.json`, `library_forecast_table.enumeration_rule`;
gate `protected_stretched_n2_unreachable: true`), receipt cross-bindings (QG-2
binding its baseline to the R6Q counts; QG-5 binding structured-n2 and
chemistry rows to the R6O/R6M/R6R receipts), and double-run replay as recorded
per lane in the closure packet. Every lane receipt asserts
`reserved_stretched_n2_accessed: false`.

**Status vocabulary, per claim.** THEOREM (machine-checked): the QG-1 B=5
theorem; the R6S support-2 all-n theorem it extends; the QG-2 O2 constant-shift
lemma; and each exact counterexample (the QG-5 boundary instance, the QG-2
support-3 witnesses, the QG-4 dominance violations) — an exactly verified
counterexample is a theorem that the respective closure fails. EVIDENCED
(machine-verified on stated finite frozen domains, not theorems for all n):
everything else quantitative here — the SixLCU trade catalogue, ladder, and
predicate P0; the QG-2 per-objective regime maps; the QG-3 confirmations; the
QG-5 forecast agreements; and all chemistry statements, which cover exactly the
recorded matchings of the named subjects. OPEN: tightness of B=5; O1
sufficiency bounds and predicates; the all-n completeness of any closed-form
forecast family (refuted for the current one, to be re-based on D++ in QG-5b).

**Claim boundary.** This paper claims exactly: (a) the template as a defined,
twice-instantiated production method, with the lane discipline as stated; (b)
the wave-1 lane results enumerated in Sections 4–7, each bounded to its
receipt's stated domain and status; (c) the cross-family motifs of Section 8 as
observations with the stated instance counts, the transferable-principle
candidates explicitly unformalized; (d) the residual ledger as the wave-2
program. It does not claim: theorems beyond those machine-checked and cited;
anything about objectives, grammars, term counts, encodings, or cost rules
outside the frozen ones (qubitization walk operators, coherent alias sampling,
and amplitude-dependent PREP costs are explicitly out of scope —
`QG4_SECOND_FAMILY_RESULTS.json`, `claim_boundary`); any full-circuit,
hardware, or global block-encoding optimality; any donor-owned machinery as
novel (TARE and all absorbed machinery per the companion paper's Section 6;
SixLCU incumbents and identical-term collection per the QG-4 claim boundary);
and **no R6 compiled-resource novelty anywhere** — every cited receipt's
authority string contains `NOT_R6`, and the wave-1 closure verdict itself
grants no scientific or novelty authority (`QG_WAVE1_CLOSURE_PACKET.md`,
closure decision). The two refutations (QG-5's identity failure, QG-2's MIXED
verdict) and the two adjudication CANNOT_CHECK terminations are part of the
record this paper stands on, with the same standing as its confirmations. The
protected stretched-N2 subject was never read by any receipt cited here and
remains sealed. Numbers not present in the cited receipts do not appear in
this manuscript.

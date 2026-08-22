# ORION-QG wave-2 record

Status: UNDER ASSEMBLY — running ledger for wave-2 lanes as they close; each entry bound
from committed, replay-verified receipts. Wave-1 record: `QG_WAVE1_CLOSURE_PACKET.md`
(CLOSED). Authority: development record only; no lane entry grants scientific or novelty
authority; all cited authorities carry NOT_R6.

## Closed wave-2 lanes

- **R1 / QG-5b — exact forecaster, full positive branch** (bound in the wave-1 packet's
  ledger entry; `QG5B_EXACT_FORECASTER_RESULTS.json`): theorem-backed F2 zero error on
  9,547 instances; enlarged borrow B′ closed the identity on all verified domains; no
  fourth configuration **on those domains** (see QG-7 below for the all-n answer).
- **R2 / QG-8 — objective-indexed support-2 cone, all n, machine-checked** (merged
  `f90c7dfa`, PR #761, independently re-verified pre-merge: analyzer digest bit-identical,
  generic verifier ACCEPT): support ≤ 2 for all n exactly within the half-space cone
  `t_c ≥ 2·t_r ∧ t_nc ≥ 2·t_r`; O0 sits exactly on the central hyperplane (margin 0);
  O1 outside with the QG-2 support-3 witness as control; global boundary sharpness OPEN.
- **QG-12 — SixLCU P0 all-instance boundary theorem** (merged `e0b73bd8` via PR #782
  delivering PR #766; digest bit-identical, generic verifier ACCEPT): `C_F == C_U iff P0`
  for every admitted batch and every n — certificate arity separation (globally rich
  witnesses, pair-derived boundary). Upgrades wave-1 QG-4 to theorem grade.
- **QG-13 V1 — theorem miner recovery control** (merged `cad8b1b4`, PR #778; digest
  bit-identical, generic ACCEPT, native ACCEPT_RECOVERY): production semantics alone
  suffice to re-derive the R6M cone and R6I support-5 parent theorems; authorizes the V2
  new-edit freeze (#777, prospective mined candidate: R6I all-n support ≤ 4).
- **R7 instrument — #745/#746 dual-custody positive-forecast lane** (merged `164462bf`;
  custody reconciliation notes in the wave-1 packet's R7 entry).

## QG-7 — FOURTH SUPPORT-TWO REGIME FOUND (discovery; the B′ closed form is not all-n complete)

`QG7_BPRIME_COMPLETENESS_RESULTS.json` (replay-verified: double-run canonical stdout
byte-identical, digest `159d174f…37d152f` both runs; generic verifier ACCEPT;
protocol frozen pre-outcome at `ee27dcf4`, sha256 `04281622…373645`;
authority `ORIONQG_QG7_FOURTH_SUPPORT2_REGIME_FOUND__HOSTILE_SEARCH_WITNESS_REFEREE_
CONFIRMED__NOT_R6`).

- **Counterexample-first arm**: the frozen adversarial H-shape search (issue #757's
  H1–H5, B′ imported verbatim from QG-5b and never enlarged) found **64 fourth-regime
  witnesses with C_D++ < min(C_D+, f_B′)**, all gap −1, on 740 evaluated instances;
  every witness independently replayed through the proof-carrying referees; 0 replay
  failures; 0 R6S contradictions (C_DP == C_D++ on all 740 — the support-2 theorem
  stands; the *closed-form family* is what breaks, one level deeper than QG-5).
- **Mechanism** (witness 0, n=3: C_DP = C_D++ = 7 < 8 = C_D+ = f_B′): a
  **weight-2-Tag + phantom hybrid** — blocks anchored at two distinct tag qubits plus a
  phantom block whose support-two frame borrows its label-1 syndrome at an existing tag
  qubit. Weight-2-Tag configurations are definitionally outside B′ (a weight-1-Tag
  family), and D+ pays strictly more. Exactly the hybrid split+borrow shape the charter
  hypothesized (H1/H4). QG-5b's 9,547 zero-gap instances missed it because random
  panels essentially never align targets with frames; the frozen Restore-template
  grammar produces that alignment deliberately.
- **Normalization arm** (ran regardless): L1 (2,2)-block elimination CLOSED all-n
  (complete 27,216-case domain, 0 failures); L2 support-two orientation CLOSED all-n;
  L3 home normalization CLOSED for the weight-1-Tag pre-B′ form; L4a tag-prune closed
  (1,440-check complete domain) with the consolidation shapes proven
  **non-consolidatable — they are the new regime**; L5 all closed steps use
  full-environment tables. Per-H census with disclosed caps: H1 15, H2 23, H3 11,
  H4 15, H5 0 witnesses.
- **Field reading**: the elementary trade basis of unit-cost TARE has at least four
  members: split (D+ / multi-anchor Tag), borrow (anchored B), phantom borrow (B′,
  out-of-support home, weight-1 Tag), and the **split+borrow hybrid** (weight-2 Tag
  with phantom borrow). Each was discovered by refutation of the previous closed form,
  each time with C_DP == C_D++ intact — the discovery ladder climbs *inside* the
  support-2 world exactly as R6S guarantees.

## QG-7b — HYBRID FAMILY B″ CLOSES ON VERIFIED DOMAINS (the ladder rests at four configurations)

`QG7B_HYBRID_FAMILY_RESULTS.json` (protocol frozen pre-outcome at `17191922`, sha256
`f45767bf…97fe6ac`; double-run canonical stdout and RESULTS-minus-timing byte-identical
per lane receipts, result digest `abc66e26…95cc41`; generic verifier — pure-primitive
rebuild, no analyzer imports — ACCEPT, independently re-run by the orchestrator against
the committed receipt; authority
`ORIONQG_QG7B_HYBRID_FAMILY_CLOSES_ON_VERIFIED_DOMAINS__WEIGHT2_TAG_PHANTOM_BORROW_
BSECOND__NOT_R6`).

- **B″ frozen before outcome**: weight-2 Tag over the union-support pool, ≥1 phantom
  block with off-tag home borrowing at a tag qubit; proof-carrying witness verifier ran
  on 100% of exact rows (205, 0 failures).
- **Completeness on 10,481 instances, zero gap**: all 64 QG-7 fourth-regime witnesses
  covered with f_B″ == C_DP; the full QG-7 H-panels (740) re-bound exactly; the QG-5b
  slices (9,261 + 240) unbroken; and the NEW anti-B″ adversarial Panel X (176
  instances: weight-3 Tags, non-tag chain borrows, tag-supported phantoms,
  double-borrow phantoms) produced 52 fourth-regime rows — **all covered by B″, zero
  fifth-configuration candidates**.
- **Q3 delimits the endgame (QG-7c)**: L1/L2 receipt values bound exactly; the two
  remaining obligations between "closes on verified domains" and the all-n identity
  are **L4b** (consolidate the still-open feasible weight-≤2-Tag shapes into
  D+ ∪ B′ ∪ B″: tag-supported phantoms, double-borrow phantoms, cyclic borrows,
  l1-phantom-at-home) and **L4c** (bound the Tag weight: L4a prunes only tag letters
  outside the union frame support, so weight-≥3 Tags with frame-supported letters owe
  an exchange lemma or a B‴). If both close, L5 inherits and
  `C_DP == min(C_D+, f_B′, f_B″)` becomes an all-n theorem.

## QG-9 ladder — R6I INTRINSIC SUPPORT NUMBER κ = 1 (all n), and QG-16's objective cone

Merged `beea3034` (delivery PR #830 of the stacked lanes #786/#789/#792/#796/#809/#813/#815).
Independently verified before merge: V6's analyzer re-run reproduced `result_digest`
`587b4b80…d31a4f` bit-identically against its committed protected receipt and again on the
merged tree; support-4/3/2 analyzers re-run with all gates true; `qg9_support2_generic_verify`
ACCEPT and `qg16_generic_verify` ACCEPT_SUPPORT; harness suite 132 passed.

| Rung | Terminal |
|---|---|
| QG-1 | support ≤ 5 all n |
| V2 | `QG9_RANK2_ALL_N_SUPPORT4_SUFFICIENCY_MACHINE_CHECKED` |
| V3 | `QG9_RANK2_ALL_N_SUPPORT3_SUFFICIENCY_MACHINE_CHECKED` |
| V4 | `QG9_RANK2_ALL_N_SUPPORT2_SUFFICIENCY_MACHINE_CHECKED` |
| V5 | `QG9_NO_SUPPORT2_TIGHT_WITNESS_IN_FROZEN_INVERSE_PANEL` (honest negative; correctly granted no support-1 authority) |
| **V6** | **`QG9_RANK2_ALL_N_SUPPORT1_SUFFICIENCY_MACHINE_CHECKED`** — `C_DP = C_cap1` all n; support-0 infeasible ⇒ **κ_R6I = 1 exactly** |
| QG-16 | `QG16_R6I_OBJECTIVE_INDEXED_SUPPORT1_CONE_ALL_N_MACHINE_CHECKED`; `GLOBAL_PHASE_BOUNDARY_SHARPNESS = OPEN` preserved |

**Method finding.** V1–V5 all stalled because their edit grammars were per-block and
syndrome-preserving. V6 closed the ladder by *relocating* the shared Tag after localizing
each rank-2 block to one anticommuting core — a whole-system rebuild. The five earlier
rungs were not wasted: each obstruction census is what showed the residue was structural
rather than local, motivating a change of proof system instead of a bigger move menu.
This directly answers, for R6I, the question QG-7's ladder poses for TARE.

**Consequence for the tightness hunts**: "is support-4 tight?" (#797) and "is support-2
tight?" (#805) are both answered NO by V6 — the ladder settled them two rungs below.

## QG-6 — production syndrome-rank inference, and a sound-but-loose bound

Merged `c5ba39fe` (delivery PR #833 of #759); digest `f065afc8…b023eb` reproduced
bit-identically, independent generic verifier (no `_DELTA` import) ACCEPT, 10/10 gates.
Terminal: rank **2** for every R6M frame slot (recovering the earned support-2 theorem
from production semantics alone), rank **5** for R6I block deletion.

**Cross-lane finding (visible only once QG-6 and QG-9 V6 are both bound):** the
syndrome-quotient rank for R6I is 5 while its true intrinsic support number is 1. The
production-syndrome pipeline is therefore **sound but loose** — it certifies that *some*
finite-support normal form exists, but the rank is not the intrinsic support number.
Closing that gap needed exactly the whole-system Tag relocation of V6, which no
per-block syndrome-preserving argument — including the rank argument itself — can
express. This is the programme's sharpest statement about the reach of its own
meta-method.

## QG-15 — THIRD FAMILY TRANSFERRED; BOUNDARY-IS-LOW-ORDER REFUTED AS A UNIVERSAL MOTIF

`QG15_THIRD_FAMILY_RESULTS.json` (protocol frozen pre-outcome, sha256 `765dc86a…4b38b3f`;
double-run byte-identical, result digest `04f19d33…f76ddc` — independently reproduced
bit-identically by an orchestrator re-run; generic verifier — pure-primitive rebuild with
deliberately different internals — ACCEPT 17/17; authority
`ORION_QG15_THIRD_FAMILY_TEMPLATE_TRANSFERRED__STABPREP_CLIFFORD_SYNTHESIS_REGIME_
GEOMETRY_ON_VERIFIED_DOMAINS__NOT_R6`). Family: StabPrep — stabilizer-state preparation
under H/S/SDG (cost 1) + CNOT (cost 3), exact Dijkstra referee over the complete
stabilizer-state graphs (6/60/1080/36,720 states at n=1..4), frozen greedy-echelon donor.

- **All five template components instantiated** — the terminal is TEMPLATE_TRANSFERRED —
  with two first-class refutations inside them: (1) regime map complete (donor-exact
  region collapses 83% → 17.5% from n=1 to n=3); (2) four trade classes with serialized
  minimal witnesses (ORDER/PIVOT/ROUTE/GLOBAL; the GLOBAL minimal witness is |+i⟩ at
  n=1: donor 4 vs optimal 2); (3) NO_STRICT_SUBEXTENSION_CLOSES on the schedule axis
  (639-instance irreducible global residue — unlike TARE's support-2 closure), but
  uniform budget bounds h*(n)=n+1, c*(n)=n−1 (tight), s*(n)=2n, and a machine-checked
  n=1 exchange/normal-form lemma; (4) **NO_CLEAN_PREDICATE** — the donor-exact boundary
  is not expressible in the frozen positive-conjunction language (best form: 117/1080
  errors), though P1/P2 are zero-false-positive certified sufficient conditions on every
  panel; (5) **prospective forecast REFUTED** on the digest-stamped held-out n=4 panel
  (regime 100/120, cost 67/120; stamp printed before any n=4 referee call, verifier
  reconstructs it bit-exactly; 20 witnesses serialized).
- **Cross-family verdict** (the field-defining evidence #740 asks a third instance for):
  the trade-currency-from-characterizable-refutation motif transferred a third time;
  **boundary-is-low-order FAILED for the first time** — TARE and SixLCU had exact
  low-order predicates, StabPrep's boundary resists every frozen bounded form. The motif
  is a property of those two families, not of the template. Successor questions: which
  structural property separates predicate-admitting families from StabPrep (candidate:
  the existence of an exact finite trade *currency* at a characterizable column vs
  StabPrep's global schedule residue), and whether a negation-admitting predicate
  language recovers exactness (registered as QG-15b, pre-outcome freeze required).

## QG-15b — PREDICATE COMPLEXITY MEASURED: THE BOUNDARY-IS-LOW-ORDER GAP IS INFORMATION-THEORETIC

`QG15B_PREDICATE_LANGUAGE_RESULTS.json` (protocol frozen pre-outcome, sha256
`8d2c52fc…c944a5`; double-run byte-identical; generic verifier — independent
ground-truth rebuilds for BOTH families plus reduction-free brute-force re-proof of the
sub-lattice minima — ACCEPT 28/28, independently re-run by the orchestrator; terminal
`QG15B_PARTIAL__Q1_UNDECIDED`, authority `…__NOT_R6`). The two calibration numbers:

- **SixLCU incumbent-exact boundary: exact at (K=1, D=1)** — the single literal
  `maxg2 == -2` is a zero-error predicate on all 38,760 n=2 instances and the n=1
  cross-check. The published low-order boundary is literally one literal.
- **StabPrep donor-exact boundary: zero error UNACHIEVABLE at ANY (K, D)** — 12 mixed
  cells (identical 13-feature vectors carrying both labels, serialized verbatim) give a
  budget- and grid-independent irreducible floor of 43/1146. The failure is not a
  complexity gap in the language: the frozen structural vocabulary cannot separate the
  boundary at all — the gap is information-theoretic.
- The honestly-capped cell (3,3) carries a certified bracket minerr ∈ [43, 59] with the
  cap disclosed (`L1_UNDECIDED_CAP`); untruncated surface values receipted
  (e.g. K1_D1 = 119, K2_D2 = 74).
- **Field reading**: "boundary-is-low-order" is not about predicate budget — it is
  about whether the family's natural structural features *determine* regime membership
  at all. TARE and SixLCU boundaries are feature-determined (one to two literals);
  StabPrep's is not feature-determined in its own natural vocabulary. The successor
  question is which *enlarged vocabulary* (path/schedule-aware features) restores
  determination, and whether feature-determination itself is the transferable property
  — registered as QG-15c (pre-outcome freeze required).
- ~~QG-7c~~ **EXECUTED — see the QG-7c entry below.**

## QG-7c — CLASSIFICATION CHAIN MACHINE-CHECKED TO ONE LINK (honest partial)

`QG7C_CLASSIFICATION_RESULTS.json` (protocol frozen pre-outcome, sha256
`14129aea…1592646`; double-run byte-identical, digest `0b127438…ded656b6`; generic
verifier — pure-primitive full re-derivation of every lemma domain including exact
census equality — ACCEPT, independently re-run by the orchestrator; terminal
`QG7C_PARTIAL__L4B_OPEN`, authority
`ORIONQG_QG7C_PARTIAL__L4B_COMM_S2_PINNED_SECTOR_OPEN__L4C_CLOSED_CONDITIONAL__NOT_R6`).

- **L4c is closed (conditional on the comm-s2 sector)** — the hard rung: the T1 prune
  (frame-supported tag letters, exact refund 2, beyond L4a's reach), the T2 occupancy
  bound, and the T3 consolidation exchange on a complete 14,680,064-case domain with
  **zero failures** reduce every weight-≥3-Tag configuration into B′/B″ shape at Δ ≤ 0,
  all n. Weight-≥3 Tags never strictly pay.
- **L4b: three of four shape classes closed all-n** by the new M1 irreducible-block
  inventory lemma (262,144-case complete domain — the irreducible blocks are exactly
  {anchored 288, phantom 864, comm-s2 864}): tag-supported phantoms and
  l1-phantom-at-home are reducible or infeasible; cyclic borrows are structurally
  impossible. The double-borrow residual is the **comm-s2 shape**; its unpinned sector
  closes (T4a, 134,217,728 cases, worst Δ = 0) — the **pinned sector stays open**
  (T4b: 536,870,912 cases, 135,604 lemma failures at worst Δ = +2, census serialized).
- **The open link is lemma-open, not identity-open**: the hostile search realized the
  worst T4b failing patterns as 50 deterministic instances (plus 150 frozen random
  controls) and found **zero gap rows** — every realized pinned comm-s2 configuration
  was strictly dominated by min(C_D+, f_B′, f_B″). No fifth configuration; the trade
  basis is not extended.
- The RESULTS carries a step-by-step `proof_audit`: R6S → MG gauge → L1/L2/Lemma-E/L4a
  receipts → M1 → T1/T2 → T3 → T4a → T5 grammar pinch, each link naming its receipt.
  The single remaining link to the all-n theorem `C_DP == min(C_D+, f_B′, f_B″)` is
  the comm-s2 pinned sector.

## R7 — REAL-CHEMISTRY TRADE HUNT EXECUTED: HONEST NEGATIVE, CENSUS EXTENDED TO 16 QUBITS

`QG_R7_REAL_TRADE_HUNT_RESULTS.json` + `QG_R7_EXECUTION_RECORD.md`. Terminal
`QG3_NO_POSITIVE_PREDICTION_IN_FROZEN_SCAN`; authority
`ORIONQG_R7_REAL_TRADE_HUNT_EXECUTED__…__NOVELTY_NOT_AUTHORIZED__NOT_R6`; stage-1
digest `0a62b73a…c8a0f294`. The instrument (#745/#746) had been merged but **never
run**; this is its first execution.

- **Census: 12 candidates scanned, 12 admitted, 0 skipped; 180 matchings evaluated
  structurally; `positive_matching_found: false` on every one.** No matching anywhere
  had `predicted_C_DP < C_R6L`, so `positive_found: false` and `selected: null`.
- **The result is a prospective confirmation, not merely an absence.** Candidates 1–6
  are the batches already carrying committed DP ground truth in
  `QG3_BOUNDARY_PROSPECTIVE_RESULTS.json` (recomputed structurally, same donor-exact
  verdict). Candidates **7–12 are six genuinely unread 16-qubit batches** — outside the
  boundary receipt, outside the R6R blob list, beyond wave-1's scan cap of 6. All six
  admitted; all 90 of their matchings predicted donor-exact. The real-library
  donor-exact census now spans **180 matchings at 12, 14 and 16 qubits**, with the 16q
  tier added under DP-forbidden custody. Wave-1's census — that trade regimes require
  weight-2 structure these DUCC batches do not produce — held prospectively on a qubit
  tier it had never seen.
- **Custody intact throughout**: `dp_call_count = 0`, ground truth never opened (with
  no positive selected, the honest-terminal branch returns before the referee is
  reached), protected stretched-N2 never a candidate and never read, both lanes
  independently `NO_POSITIVE` on the same stage-1 digest (a concordant negative, not a
  disagreement), stage-2 referee double-run byte-identical, and the workflow's own
  gate-enforcement block re-run verbatim to `ALL_WORKFLOW_GATES_PASS`.
- **Two plumbing fixes were required and are disclosed verbatim** in the receipt's
  `execution_notes`, both wall-clock/transport only with no scientific parameter,
  threshold, cap, gate, ordering, exclusion or predicate touched: the harness's 120 s
  process clamp (a single 16q candidate measures 213 s, so twelve could never fit) and
  a bounded retry for a transient 502 from the egress proxy, which never retries
  401/403/407 and leaves the pinned blob-SHA gate deciding what bytes are admitted.
  Four run attempts were needed; the artifacts bind the fourth (1,952 s).
- **Disclosed limitation**: run locally rather than in CI, so the workflow's two
  lineage assertions (exact protected-head checkout, merge-base against the frozen
  base) were not re-implemented; the frozen base remains bound inside the stage-1
  packet and is checked by both lanes.
- Residual **W5 is discharged** as far as this instrument reaches. The open successor
  is not "hunt harder" but QG-2's reading: a real trade-regime batch is far likelier
  under a re-weighted objective (O1-style), where chemistry flips to borrow regime on
  all 30 receipted rows.

## QG-7d — THE LAST LINK: 12 STATES FROM THE ALL-N THEOREM

`QG7D_LAST_LINK_RESULTS.json` (protocol frozen pre-outcome, sha256 `e9ebe4e6…3c65bd0e`;
double-run canonical stdout and RESULTS-minus-timing byte-identical, digest
`cdca51a1…0ff9650c`; independent pure-primitive generic verifier ACCEPT 9/9, re-deriving
the residue row-for-row; all 10 gates true; terminal `QG7D_PARTIAL__P1_RESIDUE_OPEN`,
authority `ORIONQG_QG7D_PARTIAL__P1_RESIDUE_OPEN__NOT_R6`).

- **A2 (domination) was the winning attack**, as the hostile evidence predicted. Its
  decisive ingredient is not a bigger move menu but the **MG mirror** of the whole
  configuration combined with the per-block **target permutation** — a configuration
  degree of freedom of the committed `r6p.dxx_search` that T4b's per-block menu never
  exploited. A1's joint exchange and A3's chain induction fold in as special cases and
  covered geometries (double pinner 136, comm-s2 chain 323 — both of QG-7c's
  declared-open sub-cases are now covered domains).
- **P1 domain: 6,341,787,648 states** (27 roles → 378 geometries × 16,777,216), no
  sampling. **373/378 geometries closed; residue 12 states** (worst local deficit +1)
  in 5 geometries, serialized verbatim. P1 also **supersedes T4a** as an independent
  cross-check — and a mid-run discrepancy against T4a is what exposed a real
  menu-reduction bug (see `RECEIPT_CHURN_HAZARD_2026-08-21.md`).
- **Census dispatch**: T4b independently re-derived, reproducing the committed
  536,870,912-domain / 135,604-failure / worst-+2 values verbatim; **all 135,604
  patterns dispatched CLOSED, 0 open**. The 12 residual states lie *outside* the T4b
  census entirely — they are a newly located obstruction, not the old one.
- **Hostile arm**: 229 instances (census realizations, frozen random controls, and
  P1-residue-extremal instances at n = 2/3/4) → **0 gap rows**, full referee coverage,
  0 sandwich failures. Every realized residue state shows gap 0. No fifth configuration.
- **Chain status**: steps 1–6 and 8–11 of the assembled `proof_audit` carry
  (R6S → MG/G2 → G3 gauge → L1/L2/Lemma-E/L4a → M1 → T1/T2 → P1 → induction → T3 → T5 →
  sandwich). Step 7 is closed on 6,341,787,636 of 6,341,787,648 states. **The TARE all-n
  classification theorem is twelve states from complete.**
- **Why those twelve resist**: at each, the Δ ≤ 0 optimum is itself comm-s2 on a
  *different* block, so the comm-s2 count does not strictly decrease — the frozen A3
  induction cannot apply. The honest successor is a composition/fixpoint argument, which
  is exactly the FAILED_DECOMPOSITION move the reopen adjudication independently derived
  for this negative.

## QG-17b — THE TIE LOCUS: A NEGATIVE CONVERTED, AND TWO BOUNDARY FACES THE CERTIFICATE MISSES

`QG17B_TIE_LOCUS_RESULTS.json` (protocol frozen pre-outcome, sha256 `27ede632…54f889`;
double-run byte-identical; 17/17 gates; independent verifier `ACCEPT_EXACT_PHASE_BOUNDARY`
with `failed: []`, re-run by the orchestrator). Terminal
`QG17B_EXACT_PHASE_BOUNDARY_LOCATED`. The annotation
`QG17B_QG16_FACET_LOCALLY_SHARP_BY_TIE_LOCUS` was **not** earned — see Q3.

**The conversion worked.** The reopen adjudication read QG-17's exact-zero tie on 4,896
of 211,248 candidates at `O_nc_out` as the signature of sitting *on* the phase boundary
rather than of narrowly missing a witness, and derived the move: solve for the tie locus.
Executed:

- **Q1** — the 4,896 ties reproduce verbatim with **zero degenerate (d = 0)** ties and
  collapse to exactly **two** hyperplanes: `t_c + t_nc = t_tag + 2·t_r` (2,456 ties) and
  `t_c + t_nc = 3·t_r` (2,440), each realized by a single raw `d`. `O_nc_out =
  (3/2, 3/2, 1, 1)` lies **exactly on both**, verified over the integers for all 4,896.
- **Q2** — both hyperplanes sign-flip, completely: on the minus side **every** tying
  candidate becomes a strict support-2 winner (4,896 crossing witnesses at an exact
  rational offset of 1/128); on the plus side, zero. Since `C_DP ≤ C2 < C_cap1`, these are
  the **first machine-checked points in the programme where support 1 provably fails**.
  Representative: candidate 1309 at θ = (191,191,129,130)/128 gives `C2 = 511/64` against
  `C_cap1 = 259/32`, gap 7/64.
- **Q3 — the more interesting branch, and the reason the sharpness annotation was
  refused.** Neither tie-hyperplane is proportional to any QG-16 facet normal; both are
  classified `NEW_TRUE_BOUNDARY_FACE_NOT_IN_QG16_CERTIFICATE`. **The true boundary has two
  faces QG-16's certificate does not describe.** The near-misses are instructive:
  `[1,1,0,-3]` against facet `[1,1,0,-5]`, and `[1,1,-1,-2]` against facet `[1,1,-2,-2]`
  — same direction in the frame coordinates, differing in the Restore/Tag trade. So
  QG-16 facet local sharpness remains **undemonstrated**, and the certificate is now known
  to be incomplete in a located, quantified way rather than merely unproven.

Anti-overclaim intact and verified: `global_phase_boundary_sharpness: OPEN`,
`global_phase_boundary_complete: false`, `qg16_certificate_refuted: false`,
`support2_required_anywhere_else_claimed: false`. The lane also passes a **tamper test** —
injecting a false gap and a phantom witness index flips the verifier to REJECT on three
independent checks.

## QG-7e — THE TARE ALL-N CLASSIFICATION THEOREM IS COMPLETE

`QG7E_TWELVE_STATES_RESULTS.json` (protocol frozen pre-outcome, sha256 `dee3ff16…fb62`,
with two pre-outcome corrections disclosed inside it; double-run byte-identical, digest
`099359e4…4eb3642`, 334.4 s / 331.7 s; **all 12 gates true**; independent pure-primitive
verifier ACCEPT with `failed: []`, re-run by the orchestrator). Terminal
`QG7E_ALL_N_CLASSIFICATION_THEOREM_COMPLETE`; authority
`ORIONQG_QG7E_ALL_N_CLASSIFICATION_THEOREM_COMPLETE__COMM_S2_SECTOR_CLOSED_BY_PER_BLOCK_
TARGET_PERMUTATION_DOMINATION__NOT_R6`.

**`C_DP == min(C_D+, f_B′, f_B″)` now holds for all n.** With R6S (`C_DP == C_D++`, all n)
and QG-18 (κ_TARE = 2, two-sided), unit-cost TARE becomes the field's first **fully
closed regime-geometry object**: a provably exhaustive four-configuration trade basis, an
all-n support bound, an exact intrinsic support number, an all-n cost envelope, an exact
decidable predicate, and a certified forecaster — every link machine-checked and
receipt-named in a 12-step `proof_audit`.

**What actually closed it.** QG-7d's own protocol declares the **per-block target
permutation** a configuration degree of freedom of `r6p.dxx_search`, and
`r6p._block_arrays` enumerates it independently per block. QG-7d's implemented P1 menu
realized only the **global MG mirror** — all three blocks swapped together, `p ∈ {000,
111}` of the eight subsets. Admitting all eight closes the residue: **378/378 geometries,
residue 0 over the complete 6,341,787,648-state domain**, covering both of QG-7c's
declared-open sub-cases (double-pinner 136, comm-s2-chain 323).

**The control that makes this credible** (gate G7): with the enlargement switched off,
the menu reproduces QG-7d's 12 residual states **row-for-row over 83,886,080 states, 0
mismatches** — so the *enlargement*, not an implementation difference between the two
lanes, is what closed them. The orchestrator's independent verifier reproduces both
sides: residue 0 enlarged, residue 12 un-enlarged. Gate G8 binds the permutation itself
on 5,340,816 rows with 0 mismatches plus an operational n=2 panel against `dxx_search`.

**E1 refuted its own premise, and this falsifies a programme prediction.** The frozen E1
attack assumed a Δ ≤ 0 replacement always exists and merely relocates comm-s2 to another
block. Exact enumeration shows **10 of the 12 states admit no Δ ≤ 0 alternative at all**
(empty replacement set, empty orbit); only 2 have images, all re-entrant. So the residue
was a **local-optimality failure, not a descent failure**, and no re-choice of descent
measure could ever have repaired it.

That matters beyond this lane. The reopen adjudication classified N1 as
`FAILED_DECOMPOSITION` and predicted the fix would be to *change the decomposition, not
enlarge the move menu* — explicitly citing the "enlarging move menus failed repeatedly;
redefinition succeeded repeatedly" method finding. **The prediction was wrong.** What
closed the residue was precisely a move-menu enlargement (admitting the full permutation
subgroup), and the decomposition-change attack was refuted by exact enumeration. The
method finding is therefore not a law: a negative *can* be an insufficient search, and
here it was — specifically, a menu that failed to realize a degree of freedom its own
protocol had already declared. Recorded as a falsified prediction rather than quietly
dropped; the reopen adjudication's terminal stands as issued, with this outcome scored
against it.

## Registered successor (requires its own pre-outcome freeze)

- ~~QG-7e~~ **EXECUTED — theorem complete, see above.** A composition/fixpoint argument over the residue, where
  strict descent fails because the replacement optimum is comm-s2 on another block. The
  reopen adjudication classifies this negative FAILED_DECOMPOSITION and predicts it
  converts (`reopen-adjudication/REOPEN_TERMINAL.json`).
- ~~QG-7d~~ **EXECUTED — see above.** Close the comm-s2 pinned sector: a sharper exchange
  (the T4b failure census delimits exactly which 135,604 patterns need it, worst
  residue +2) or a new composition argument for the two declared-open sub-cases
  (double pinners; comm-s2 chains). The hostile evidence says the identity holds
  there — what is missing is the lemma, not the truth.

## Stop rules

Inherited verbatim from the wave-1 packet and charter: theorem, donor absorption,
receipted saturation, confirmed prospective test, first-class refutation, or
cannot-check; no post-outcome gate changes; the protected stretched-N2 subject remains
sealed.

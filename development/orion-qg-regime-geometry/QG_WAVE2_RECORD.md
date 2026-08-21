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

## Registered successor (requires its own pre-outcome freeze)

- **QG-7d — the last link.** Close the comm-s2 pinned sector: a sharper exchange
  (the T4b failure census delimits exactly which 135,604 patterns need it, worst
  residue +2) or a new composition argument for the two declared-open sub-cases
  (double pinners; comm-s2 chains). The hostile evidence says the identity holds
  there — what is missing is the lemma, not the truth.

## Stop rules

Inherited verbatim from the wave-1 packet and charter: theorem, donor absorption,
receipted saturation, confirmed prospective test, first-class refutation, or
cannot-check; no post-outcome gate changes; the protected stretched-N2 subject remains
sealed.

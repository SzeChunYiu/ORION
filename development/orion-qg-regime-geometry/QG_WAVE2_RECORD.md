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

## Registered successor (requires its own pre-outcome freeze)

- **QG-7b — hybrid-family closed form.** Freeze an enlarged family `B″` admitting
  weight-2 Tags with phantom borrows (guided by QG-7's L4a non-consolidatability
  classification, which delimits the shape), and test
  `C_DP == min(C_D+, f_B′, f_B″)` on the QG-7 witness set, the QG-5b panels, and fresh
  frozen panels — or find a fifth configuration. The charter rule stands: no silent
  post-hoc enlargement; B″ must be frozen before its outcome.

## Stop rules

Inherited verbatim from the wave-1 packet and charter: theorem, donor absorption,
receipted saturation, confirmed prospective test, first-class refutation, or
cannot-check; no post-outcome gate changes; the protected stretched-N2 subject remains
sealed.

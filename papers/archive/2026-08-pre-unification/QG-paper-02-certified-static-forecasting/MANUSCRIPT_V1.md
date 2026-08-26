# Certified Static Resource Forecasting for Quantum Compilation: Per-Component Proof Status, Prospective Confirmation, and a Refutation That Worked

Manuscript V1 — 2026-08-21. Branch `claude/orion-harness-verification-b17qdj`.
Every number in this manuscript is transcribed from a committed receipt or frozen
protocol; the receipt path is cited inline at first use. Receipt paths are relative
to the repository root. Nothing here carries R6 (compiled-resource novelty)
authority; the authority strings of all cited receipts contain `NOT_R6` or an
equivalent bounded-authority marker.

---

## Abstract

Static resource estimation for quantum compilation usually reports a number; it
rarely reports what part of that number is proven and what part is extrapolated.
We present a DP-free static resource forecaster for a frozen shared-Tag TARE
compilation grammar whose *certificate architecture* makes exactly that
distinction first-class: the forecast `F(t) = min(C_R6L, C_Dplus, f_B)` is
emitted with a per-component certificate basis that labels its upper-bound
component PROVEN (constructive family enumeration), its support-2 sufficiency
component PROVEN for all qubit counts (a machine-checked exchange theorem), and
its exactness identity and regime classification MACHINE-EVIDENCED only
(`research/extensions/orion-qg/QG5_CERTIFIED_FORECAST_RESULTS.json`,
`forecaster.certificate_basis`). Under a prospective staging discipline —
predictions digest-stamped before any dynamic-programming referee runs — the
forecaster's predictions were confirmed on 12 engineered boundary instances with
hand-derived costs (positive split and borrow confirmations, 11→11 and 7→7) and
on 90/90 real Hamiltonian-library matchings
(`research/extensions/orion-qg/QG3_BOUNDARY_PROSPECTIVE_RESULTS.json`). Against
the committed unrestricted exact DP the forecaster matched 9,545 of 9,546
compared instances at a fresh-panel median speedup of ~9.8×. The 9,546th
instance is the paper's centerpiece: a fresh seeded panel produced a genuine
counterexample (C_DP = 10 versus forecast 11, serialized verbatim), and the
failure landed exactly where the certificate said it could — in the
machine-evidenced exactness identity and regime label — while both PROVEN
components held on the same instance. The mechanism (a support-2 frame whose
borrow home lies outside the block's own target support) localizes a third
elementary trade configuration and, because the support-2 sufficiency theorem is
already proven for all n, fixes a repair path that is exact by theorem.
A 31-candidate library forecast table is emitted with explicit per-row
verification status, including rows honestly labeled unverified forecasts with
no verification authority. All results are bounded to frozen finite domains; the
exactness identity remains a conjecture for all n; refutation was a pre-frozen
outcome branch, not an accident of reporting.

---

## 1. Resource estimation today versus certified static forecasting

A compiler pass that predicts the cost of an optimized compilation without
running the optimizer is useful exactly insofar as its error model is explicit.
The common practice in quantum resource estimation is to publish point estimates
whose internal provenance is homogeneous: every term of the estimate carries the
same implicit confidence, whether it comes from a theorem, a fitted model, or a
finite benchmark. When such an estimator is later found wrong, the failure
cannot be localized — nothing in the artifact says which part was load-bearing
proof and which part was extrapolation.

This paper takes the opposite discipline on a small, fully frozen domain: the
three-block shared-Tag TARE-M2 compilation grammar under a frozen raw
support-count objective, whose exact optimization landscape was previously
mapped witness-by-witness (the two elementary trade regimes, the support-2
family closure, and the exact regime predicate of the R6N–R6S receipt chain
under `research/extensions/orion-q/`). We convert that closed-form regime
machinery into a **certified static forecaster**: a function of the six target
Paulis alone, with **no dynamic-programming call in the forecast path**
(`QG5_CERTIFIED_FORECAST_RESULTS.json`, `gates.no_dp_call_in_forecast_path:
true`), which emits, per instance:

- a forecast cost `F(t)`,
- a predicted regime label (donor-exact / split / borrow),
- a certificate: the closed-form witness family, both trade-profitability
  checks, and the predicate P1, and
- a **certificate basis** stating, component by component, whether the
  component is proven or merely machine-evidenced.

The scientific question is then not "is the forecaster right?" but "when the
forecaster is wrong, does it fail where its own certificate said it could?" The
answer, on a fresh panel that produced a genuine counterexample, is yes — and we
argue this designed-for refutation is the strongest evidence in the paper that
the certificate architecture works.

All receipts cited here carry bounded authority strings ending in `NOT_R6`; no
novelty or compiled-resource authority is claimed anywhere
(`QG5_CERTIFIED_FORECAST_RESULTS.json`, `authority:
QG5_FORECAST_IDENTITY_REFUTED__BOUNDARY_INSTANCES_REPORTED_VERBATIM__NOT_R6`,
`r6_authority: false`, `novelty_credit: false`).

## 2. The forecaster and its certificate

### 2.1 Definition

The forecaster is the three-family closed-form minimum

```
F(t) := min( C_R6L(t), C_Dplus(t), f_B(t) )
```

over the six frozen target Paulis, with certified regime label by the frozen
R6R rule and certificate consisting of the closed-form witness family, the
Gsplit and borrow profitability checks, and the predicate
`P1(t) := [C_Dplus == C_R6L] AND [f_B >= C_R6L]`; coefficients enter only the
reported Lambda field; no DP is invoked
(`QG5_CERTIFIED_FORECAST_RESULTS.json`, `forecaster.definition`). Here `C_R6L`
is the weight-one common-anchor donor-family minimum, `C_Dplus` the
arbitrary-anchor minimum-weight-spread-Tag enlargement, and `f_B` the frozen
borrow-family minimum — each an exact minimum of a complete enumeration of an
explicitly constructible sub-family of the frozen R6M grammar, inherited
unmodified from the committed R6L/R6O/R6Q machinery.

### 2.2 Per-component proof status as first-class metadata

The receipt's `certificate_basis` records four components with heterogeneous —
and honestly labeled — proof status
(`QG5_CERTIFIED_FORECAST_RESULTS.json`, `forecaster.certificate_basis`):

| Component | Statement (abridged) | Status (verbatim) |
|---|---|---|
| 1. Upper bound | `C_DP <= F(t)` always: each family value is the exact minimum of a constructible sub-family; the containments `C_DP <= C_Dplus <= C_R6L` and `C_DP <= f_B` are hard-asserted on every DP-compared instance | `PROVEN_CONSTRUCTIVE` |
| 2. Support-2 sufficiency | `C_DP == C_Dxx` for every n, every target six-tuple, every matching: frames of global support ≥ 3 never pay | `PROVEN_ALL_N_MACHINE_CHECKED_THEOREM` |
| 3. Exactness identity | `C_DP == min(C_R6L, C_Dplus, f_B)` — machine-evidenced on the verified domains only; for all n and all targets it is CONJECTURE | `MACHINE_EVIDENCED_ON_VERIFIED_DOMAINS__CONJECTURE_FOR_ALL_N` |
| 4. Regime certificate | Regime label and predicate P1 exact on all verified domains with zero confusion errors | `MACHINE_EVIDENCED_ON_VERIFIED_DOMAINS` |

The two PROVEN components have independent backing. Component 1 is
constructive: a family minimum is an upper bound on the unrestricted optimum by
membership, and the receipt additionally hard-asserts the containment sandwich
and borrow soundness on every DP-compared instance of the run
(`gates.sandwich_and_borrow_soundness_asserted: true`). Component 2 is the
all-n composition theorem of
`research/extensions/orion-q/MAX_R6S_ALL_N_COMPOSITION_RESULTS.json` (authority
`MAX_R6S_ALL_N_COMPOSITION_THEOREM_MACHINE_CHECKED__SUPPORT3_NEVER_PAYS__DXX_EQUALS_DP_ALL_N__NOT_R6`,
`outcome: THEOREM_MACHINE_CHECKED`): for every n and every target configuration
of the frozen R6M grammar the unrestricted exact DP optimum equals the D++
(support-≤2) optimum (`theorem_statement`). Its proof shape is a qubit-local
exchange with zero Tag repair — an F₂² pigeonhole lemma (Lemma B,
machine-corroborated over 43,688 odd-alpha class tuples at w ≤ 8, with the four
failing w=2 patterns exactly the known weight-2 trade and provably unrealizable
at w ≥ 3) plus one exhaustive 18,432-case local inequality (Lemma E, 0
violations) (`lemma_b`, `lemma_e`, `claim_boundary.proof_shape`).

Component 2 does real work in the certificate even though `F(t)` does not
enumerate D++: it proves that **any** gap between `F(t)` and `C_DP` can only be
realized by support-≤2 frames outside the three enumerated families
(`certificate_basis.component_2_support2_sufficiency.statement`). This is the
clause that will localize the counterexample in Section 5 and dictate the
repair in Section 6.

Components 3 and 4 inherit their evidence from the committed predicate chain:
the exact regime predicate receipt
`research/extensions/orion-q/MAX_R6Q_REGIME_PREDICATE_RESULTS.json` (authority
`MAX_R6Q_REGIME_PREDICATE_EXACT__TWO_TRADE_CHARACTERIZATION_ON_VERIFIED_DOMAINS__NOT_R6`,
`outcome: EXACT_PREDICATE_FOUND`; zero classification error on 9,261 + 240 +
240 + 30 = 9,771 instances across four panels, `panels`) and the prospective
fresh-subject receipt
`research/extensions/orion-q/MAX_R6R_PROSPECTIVE_FRESH_SUBJECT_RESULTS.json`
(authority
`MAX_R6R_PROSPECTIVE_FRESH_SUBJECT_PREDICTION_CONFIRMED__TWO_TRADE_PREDICATE_HELD_ON_UNSEEN_SUBJECT__NOT_R6`;
15/15 matchings of an unseen subject predicted before computation, stage-1
digest `898f49a4…`). Nothing in that chain proves the identity for all n, and
the certificate says so verbatim.

## 3. Prospective staging discipline (QG-3)

Before benchmarking the forecaster at scale, the regime machinery it packages
was subjected to a prospective test designed to exercise the *positive* trade
branches, not merely the donor-exact exclusion branch that all previously
recorded chemistry had landed in. The protocol
(`development/orion-qg-regime-geometry/QG3_BOUNDARY_PROSPECTIVE_PROTOCOL.md`)
was frozen before any prediction subject was generated or selected, and the
engineered families were designed from hand-derived closed-form costs fixed in
the frozen protocol itself.

The receipt (`research/extensions/orion-qg/QG3_BOUNDARY_PROSPECTIVE_RESULTS.json`,
authority
`ORIONQG_QG3_BOUNDARY_PROSPECTIVE_POSITIVE_REGIME_PREDICTIONS_CONFIRMED__SPLIT_AND_BORROW_PREDICTED_BEFORE_DP__NOT_R6`)
records:

- **Staging before computation.** All 102 staged rows (90 real-library
  matchings + 12 engineered instances) had regime and exact-cost predictions
  committed under a stage-1 digest printed before any DP call
  (`stage1_digest: 1335f058…`; `gates.stage1_digest_printed_before_ground_truth:
  true`).
- **Track B (engineered synthetics, seed 20260824).** Twelve instances staged
  under a frozen quota gate of 4 predicted-split, 4 predicted-borrow, 4
  donor-exact (`track_b.quotas`, `quota_gate_met: true`). Every hand-derived
  prediction was confirmed exactly by the unrestricted DP: each borrow-family
  (F1) instance was predicted at cost 7 and refereed at `C_DP = 7` against
  family values `C_R6L = C_Dplus = 8`; each split-family (F2) instance was
  predicted at 11 and refereed at `C_DP = 11` against `C_R6L = 13`
  (`track_b.staged_instances`; predicted closed forms frozen in
  `QG3_BOUNDARY_PROSPECTIVE_PROTOCOL.md`, Section 4). Truth census equals
  predicted census, 4/4/4 (`track_b.truth_regime_census`).
- **Track A (real library batches).** Six fresh DUCC Hamiltonian-library
  batches admitted under the frozen R6R eligibility-and-order rule with the
  committed subject blobs excluded (`track_a.selection_rule`), including
  14-qubit subjects — the largest yet refereed by the exact DP in this
  programme (`track_a.admitted_batches`, entries with `n_qubits: 14`). All 90
  refereed matchings were predicted donor-exact and were donor-exact
  (`matchings_refereed: 90`, `finding: LIBRARY_SCAN_ALL_DONOR_EXACT`).
- **Zero mismatches anywhere**: `match_count: 102`,
  `mismatches_verbatim: []`, `gates.prediction_matches_ground_truth_every_row:
  true`.

The frozen claim boundary is part of the result: the positive split and borrow
confirmations are **synthetic-only** — no real library batch has yet landed in
a trade regime, and the hunt for one is a named residual
(`development/orion-qg-regime-geometry/QG_WAVE1_CLOSURE_PACKET.md`, residual
R7). After QG-3 the predicate carried confirmed prospective forecasts on all
three branches of the regime map; what it had never faced was a fresh random
panel drawn *after* the forecaster itself was frozen. That is Section 5.

## 4. Benchmark results and speedups

The forecaster was benchmarked against the committed unrestricted exact DP on
**9,546 DP-compared instances**
(`QG5_CERTIFIED_FORECAST_RESULTS.json`, `benchmark.dp_compared_instances_total`),
with **9,545 exact matches** and exactly one nonzero error
(`benchmark.nonzero_forecast_errors_total: 1`):

| Domain | Instances | Forecast exact | DP truth source | Receipt field |
|---|---|---|---|---|
| Exhaustive structured n=2 | 9,261 | 9,261 | committed unrestricted DP reader | `benchmark.structured_n2_exhaustive` |
| H4 chemistry matchings (n=8) | 15 | 15 | committed MAX_R6M receipt (heavy DP never re-run) | `benchmark.receipted_chemistry.H4` |
| Equilibrium N2 chemistry matchings (n=12) | 15 | 15 | committed MAX_R6M receipt | `benchmark.receipted_chemistry.N2` |
| Benzene 12-qubit matchings | 15 | 15 | committed MAX_R6R receipt | `library_forecast_table.subjects[0]` |
| Fresh seeded panel (seed 20260826; 120 × n=2, 120 × n=3) | 240 | 239 | unrestricted frozen-config DP | `benchmark.fresh_seeded_panel` |

The structured-n2 sweep is additionally bound row-wise to the committed R6O
receipt (`r6o_receipt_binding.receipt_equal_count: 8775` equal to
`recomputed_equal_count: 8775`); the chemistry rows are bound to the committed
R6M/R6O receipts with the heavy subject DP never re-run
(`heavy_subject_dp_rerun: false`,
`gates.chemistry_bound_to_r6m_and_r6o_receipts: true`); every fetched source is
blob-pinned (`gates.all_fetches_blob_pinned: true`). The fresh panel is a
digit-frozen copy of the frozen R6Q panel generator, 120 instances per n for
n ∈ {2, 3}, seed 20260826 (`benchmark.fresh_seeded_panel.generator`, `seed`).
Its predicted regime census is 153 donor-exact / 26 split / 61 borrow
(`predicted_regime_census`) — the panel exercises all three branches, not just
the easy one.

**Speedups.** On the fresh panel, cold per-instance timing gives a median
forecast time of ~0.016 s versus a median DP time of ~0.149 s — median speedup
**9.84×**, p10–p90 range 3.58×–18.44×, maximum 25.09×
(`timing.fresh_panel_cold_per_instance`). At n=2 the median speedup is
**15.72×**; at n=3 it is 4.21× (`timing.fresh_panel_by_n`). On the
warm-cache structured-n2 sweep — where the DP reader amortizes — the median is
a more modest 3.24× with a minimum below 1
(`timing.structured_n2_warm_cache`), reported as honestly as the maximum.
Per the inherited R6P convention, timing fields are excluded from the canonical
stdout line and live only in the receipt's timing section and on stderr
(`timing.convention`), so replay determinism is judged on timing-free output.

**The library forecast table.** The forecaster was then pointed at the pinned
public DUCC Hamiltonian library (`npbauman/DUCC-Hamiltonian-Library`, commit
`be306f58…`, listing digest `6191553e…`, 75 results files at the commit): the
frozen R6R eligibility rule yields **31 eligible candidates** in frozen order,
of which the attempt cap of 4 admitted **4 subjects** (Benzene active spaces at
12 and 14 qubits), i.e. **60 matchings**, all forecast with certificates
(`library_forecast_table`). Each subject row carries an explicit
per-row verification status:

- one subject (Benzene cc-pVDZ 6Elec/6Orbs DUCC2, 12 qubits) is
  `DP_RECEIPT_COMMITTED__FORECAST_BOUND`: its 15 matchings are bound to the
  committed MAX_R6R DP receipt and the forecast has zero error on all 15
  (`library_forecast_table.subjects[0]`);
- three subjects (Benzene DUCC3 at 12 qubits in two bases, and Benzene cc-pVDZ
  6Elec/7Orbs DUCC2 at 14 qubits) are `UNVERIFIED_FORECAST__NO_DP_RECEIPT`:
  predicted cost ranges 8–9 (12-qubit) and 9–10 (14-qubit), predicted regime
  census 15/0/0 donor-exact per subject — and **no verification authority**:
  "Rows without a committed DP receipt are predictions only and verify nothing"
  (`library_forecast_table.verification_authority`;
  top-level `library_forecast_table_verification_authority: "NONE"`).

The enumeration rule excludes the whole N2 molecule, so the protected
stretched-N2 subject is unreachable by construction
(`library_forecast_table.enumeration_rule`;
`gates.protected_stretched_n2_unreachable: true`;
`reserved_stretched_n2_accessed: false`).

## 5. The counterexample

The single nonzero forecast error is serialized verbatim in the receipt
(`QG5_CERTIFIED_FORECAST_RESULTS.json`,
`benchmark.fresh_seeded_panel.nonzero_errors_verbatim[0]`): fresh panel seed
20260826, n = 3, panel index 7, target pairs (as `(x, z)` bit-integer pairs)

```
A: ( (3,6) , (7,3) )     B: ( (7,3) , (3,4) )     C: ( (0,3) , (2,2) )
```

with

```
C_DP = 10   <   11 = C_R6L = C_Dplus = f_B = F(t),    forecast error 1.
```

The run's outcome field is the refutation itself:
`outcome: COMPLETENESS_IDENTITY_REFUTED_ON_NEW_INSTANCE`, under the pre-frozen
refutation branch of the protocol (`protocol: QG5_FORECAST_THEORY_PROTOCOL`,
`protocol_sha256: 0af2439d…`); the gate
`forecast_error_zero_everywhere: false` is the recorded finding, not a weakened
gate (`development/orion-qg-regime-geometry/QG_WAVE1_CLOSURE_PACKET.md`,
closure decision).

**Mechanism.** The localization, independently confirmed by the witnessed
exact referee, is recorded in the wave-1 closure packet
(`QG_WAVE1_CLOSURE_PACKET.md`, QG-5 lane slot): the optimum uses a support-2
frame whose borrow home qubit lies **outside the block's own target support** —
precisely the restriction the frozen borrow family B(t) imposed on its phantom
blocks. The frozen closed form `f_B` therefore under-parametrizes the weight-2
trade at n = 3. This is a **third elementary trade configuration** — an
out-of-support borrow — and simultaneously the **first false positive for the
predicate P1** on any verified instance: on this instance
`C_Dplus == C_R6L` and `f_B >= C_R6L`, so P1 declares donor-exact, but
`C_DP = 10 < 11 = C_R6L`.

**Why the failure hit the EVIDENCED components and only those.** Read the
counterexample against the certificate basis of Section 2.2, component by
component:

1. *Upper bound (PROVEN):* **held.** `C_DP = 10 ≤ 11 = F(t)`; the hard-asserted
   sandwich and borrow soundness held on this instance as on all 9,546
   (`gates.sandwich_and_borrow_soundness_asserted: true`).
2. *Support-2 sufficiency (PROVEN, all n):* **held.** The refuting optimum is
   realized by frames of global support ≤ 2, exactly as the R6S theorem
   requires; indeed the theorem's contrapositive is what confines the escape
   route to support-≤2 configurations outside the three enumerated families —
   which is precisely where the counterexample lives.
3. *Exactness identity (MACHINE-EVIDENCED / CONJECTURE):* **failed.** The
   two-trade completeness identity `C_DP = min(C_R6L, C_Dplus, f_B)` is false
   on this instance. Its *characterization* content stands on the exhaustive
   n ≤ 2 domains (9,261/9,261 in this same run); its closed-form completeness
   fails at higher n (`QG_WAVE1_CLOSURE_PACKET.md`, QG-5 slot).
4. *Regime certificate (MACHINE-EVIDENCED):* **failed** on the same instance —
   the first P1 false positive.

This is the paper's thesis made concrete. The certificate architecture did not
merely survive the refutation; it *predicted its shape*. The two components the
receipt labeled PROVEN were exactly the two that held; the two it labeled
machine-evidenced-only were exactly the two that broke; and the proven
component 2 then converts the failure from an open wound into a bounded search
problem — the missing mechanism must be a support-≤2 configuration, and it is.
A forecaster with a homogeneous confidence label would have reported "one error
in 9,546" and stopped; this one reports *which load-bearing beam cracked and
why the building stood*.

We emphasize the honest framing required here: the refutation is a
**designed-for outcome**. The frozen protocol carried an explicit refutation
branch requiring verbatim serialization of every boundary instance
(`responsibility:
RESP:NONZERO_FORECAST_ERRORS_REPORTED_VERBATIM__IDENTITY_BOUNDARY_LOCALIZED`),
and the harness-driven wave-closure adjudication verified that no gate was
weakened post-outcome
(`QG_WAVE1_CLOSURE_PACKET.md`, closure decision;
`development/orion-qg-regime-geometry/closure-adjudication/ADJUDICATION_TERMINAL_V3.json`).

## 6. Repair by theorem, and the objective-indexing caveat

### 6.1 The QG-5b repair path is exact by theorem

The repair is not a patch; it is already proven correct. The R6S theorem
guarantees `C_DP == C_Dxx` for **all** n — the unrestricted optimum is always
attained within the full support-≤2 family D++
(`MAX_R6S_ALL_N_COMPOSITION_RESULTS.json`, `theorem_statement`). Therefore a
forecaster that minimizes over the full support-≤2 family, rather than over the
three closed-form sub-families, is **provably exact for every n and every
instance of the frozen grammar** — the exactness component of its certificate
would be promoted from EVIDENCED to PROVEN, at the price of enumerating a
larger (but still DP-free and finitely structured) family. This is registered
as the wave-2 lead residual R1 (QG-5b): minimize over the full support-≤2
family and enlarge B(t) with out-of-support borrow homes, repairing both the
QG-5 counterexample and P1's first false positive
(`QG_WAVE1_CLOSURE_PACKET.md`, "Wave-2 residual ledger", R1). The
counterexample thus not only localized the missing trade configuration; it
landed in a region already covered by a theorem that dictates the exact repair.

### 6.2 The whole apparatus is objective-indexed

A second honesty constraint bounds everything above: the regime geometry —
including the PROVEN support-2 sufficiency — is a property of the
*(family, objective)* pair, not of the family alone. Under the frozen
coefficient-weighted objective O1 (weights t_c=1, t_nc=7, t_r=3, t_Tag=4), the
committed QG-2 receipt
(`research/extensions/orion-qg/QG2_OBJECTIVE_ROBUSTNESS_RESULTS.json`,
authority
`ORIONQ_QG2_OBJECTIVE_ROBUSTNESS_MIXED__FROZEN_REWEIGHTED_OBJECTIVES__NOT_R6`)
records that support-3 frames *strictly pay*: a NEW_SUPPORT3 witness with
`C_DP = 11 < C_Dxx = 13 < C_Dplus = 23`
(`objectives.O1.new_trade_witnesses.NEW_SUPPORT3[0]`) among 53 support-2
closure failures (`objectives.O1.support2.failure_count`); chemistry loses
donor-exactness entirely (0/30, `objectives.O1.chemistry_donor_exact_count`);
the two-trade identity fails on 4,484 structured instances
(`objectives.O1.identity_two_trade_failures`); 7,752 membership transitions are
witnessed (6,014 DONOR_EXACT→BORROW, 1,738 SPLIT→BORROW,
`objectives.O1.membership_transitions`); and the baseline predicate P1 commits
327 errors, all false positives (`objectives.O1.predicate.errors_total`).
Under the rotation-count-coupled objective O2 the geometry is exactly invariant
by a machine-checked constant-shift lemma (`objectives.O2`,
`identity_two_trade_failures: 0`). The R6S sufficiency bound — and with it the
QG-5b exactness guarantee — is therefore **objective-scoped to the frozen
unit-support objective**, and any port of the certified forecaster to another
objective must re-prove its per-component statuses from scratch
(re-proving sufficiency bounds per objective is residual R2 of
`QG_WAVE1_CLOSURE_PACKET.md`).

## 7. Discussion: what the certificate architecture buys

Three observations generalize beyond this grammar, stated carefully within the
finite domains that ground them.

**Three grades of confirmation, kept distinct in the artifact.** The results
above use three different confirmation modes, and the receipts never let them
blur. *Retrospective benchmarking* (Section 4) compares the forecaster against
committed DP truth — strong on coverage (9,546 instances) but incapable of
distinguishing a forecaster from a curve fit to its own training domains.
*Prospective staging* (Section 3) commits predictions under a digest before any
referee runs — weaker on volume (102 rows) but immune to that critique, and it
was deliberately pointed at the trade branches a passive benchmark would rarely
sample. *Forecast-only emission* (the three unverified library subjects) is the
mode most estimation pipelines silently operate in everywhere; here it is
explicitly labeled and stripped of authority
(`library_forecast_table_verification_authority: "NONE"`). A reader of the
receipt can tell, per row, which mode produced it.

**A refutation is an instrument reading, not an accident.** The QG-5 protocol's
outcome space contained the refutation branch before the fresh panel was drawn,
with verbatim serialization required for any boundary instance; the wave-closure
adjudication then verified from git history that freezes precede receipts and
that no gate was weakened after the outcome
(`QG_WAVE1_CLOSURE_PACKET.md`, closure decision). Under that discipline the
single miss in 9,546 is the most informative row of the benchmark: it measures
where the conjectured component's boundary actually sits (n = 3, out-of-support
borrow homes) rather than merely that a boundary exists. The certificate
architecture is what made the measurement legible — the failure had a labeled
compartment waiting for it.

**Heterogeneous certificates compose.** Because component 2 is a theorem
quantified over all n, it remains load-bearing even while component 3 is
refuted: it both confines the counterexample's mechanism to support ≤ 2 and
proves the enlarged QG-5b forecaster exact in advance of its implementation.
This is the practical argument for carrying proof status per component rather
than per artifact: the PROVEN parts of a partially-evidenced system keep
working — and keep *explaining* — exactly when the evidenced parts break.

## 8. Claim boundary and limits

This paper claims exactly what its receipts cover, in their words.

**Covered.** A certified static resource forecaster for the frozen R6L/R6M
three-block TARE-M2 shared-one-bit-Tag grammar under the frozen raw
support-count objective: `F(t) = min(C_R6L, C_Dplus, f_B)` with certified
regime and two-trade certificate, benchmarked against the committed
unrestricted DP on the stated finite domains and emitted as an
explicitly-labeled forecast table over the pinned library enumeration
(`QG5_CERTIFIED_FORECAST_RESULTS.json`, `claim_boundary.covers`). The
prospective confirmations of Section 3 cover exactly the 102 staged rows of the
QG-3 run in addition to the committed R6Q/R6R domains
(`QG3_BOUNDARY_PROSPECTIVE_RESULTS.json`, `claim_boundary`).

**Proven versus evidenced, restated.** The upper bound `C_DP ≤ F(t)`
(constructive) and support-2 sufficiency `C_DP = C_Dxx` for all n (MAX_R6S
theorem) are the receipt's `proven_components`. The exactness identity and the
regime certificate are machine-evidenced only on the verified finite domains
recorded in the R6Q/R6R receipts plus the DP-compared instances of the QG-5
run; **for all n and all targets the identity is CONJECTURE** — and, since
Section 5, a conjecture known to be false as a closed-form identity at n = 3 in
its frozen B(t) parametrization, with its repair (QG-5b) proven but not yet
executed (`claim_boundary.machine_evidenced_only`,
`claim_boundary.proven_components`).

**Not covered.** Other objectives (Section 6.2 shows the geometry moves under
O1), other grammars (including the R6I rank-2 grammar), rotation-count
trade-offs, Tag ranks above the enumerated families, the protected stretched-N2
subject, or any claim of donor or R6 novelty credit
(`claim_boundary.does_not_cover`; `donor_novelty_credit: false`). The
library-table rows without a committed DP receipt are **unverified forecasts
that verify nothing** — the run grants them no verification authority, and
neither does this paper
(`library_forecast_table_verification_authority: "NONE"`). Positive
trade-regime confirmations exist only on engineered synthetic instances; all
90 + 60 real-library matchings touched by QG-3 and QG-5 are (predicted and,
where refereed, confirmed) donor-exact, and finding a real trade-regime
chemistry batch remains an open, frozen hunt (`QG_WAVE1_CLOSURE_PACKET.md`,
residual R7). The protected file
`N2/cc-pVTZ/6Elec_6Orbs/1.5_Eq-3.1020au/DUCC2/N2.cc-pvtz.ducc.results.txt` was
never read by any receipt cited here and is unreachable under the frozen
enumeration rule. Chemistry sources enter only through blob-verified frozen
batch paths (`chemistry_sources_read_via_frozen_batch_only: true`). Numbers not
present in the cited receipts do not appear in this manuscript.

**Reproducibility.** The QG-5 receipt replays deterministically: double runs
are byte-identical on the canonical stdout line and identical in the receipt up
to the non-canonical timing section (`QG_WAVE1_CLOSURE_PACKET.md`, QG-5 slot);
the QG-3 receipt's stage-1 digest binds its predictions before any ground
truth; the generating modules
(`research/extensions/orion-qg/qg5_certified_forecast.py`,
`research/extensions/orion-qg/qg3_boundary_prospective.py`) and frozen
protocols (`development/orion-qg-regime-geometry/QG5_FORECAST_THEORY_PROTOCOL.md`,
`QG3_BOUNDARY_PROSPECTIVE_PROTOCOL.md`) are committed alongside the receipts.

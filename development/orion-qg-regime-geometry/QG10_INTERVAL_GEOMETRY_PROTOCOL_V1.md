# QG-10 certified interval regime geometry protocol V1 (FROZEN BEFORE OUTCOME)

Lane: ORION-QG **QG-10 — certified interval regime geometry without an exact global
referee** (chartered as issue #763, never executed). Authority ceiling **NOT_R6**;
`novelty_authority` **false**; no physical-quantum-advantage claim is made or implied.
No chemistry data is read; the protected stretched-N2 subject
(`N2/cc-pVTZ/6Elec_6Orbs/1.5_Eq-3.1020au/DUCC2/...`) is never touched. **No repository
file is modified.** Every piece of committed machinery is imported read-only and
unmodified. This lane writes only:

- `research/extensions/orion-qg/qg10_interval_geometry.py` (analyzer, new)
- `research/extensions/orion-qg/QG10_INTERVAL_GEOMETRY_RESULTS.json` (receipt, new)
- `development/orion-qg-regime-geometry/qg10_generic_verify.py` (independent verifier, new)
- `development/orion-qg-regime-geometry/QG10_GENERIC_VERIFICATION.json` (verifier receipt, new)
- this protocol.

Files owned by other concurrent lanes (`qg21_*`, `QG21_*`) are neither read nor written.

## 0. Pre-freeze disclosure (honesty)

Before this protocol was frozen, method-development calibration probes were run in a
scratchpad (never in the repository): timing probes of the committed referee and family
enumerators at n ∈ {2..64}, and small seeded gap probes (≤ 200 instances, n ≤ 16) used
only to (a) confirm the lower-bound construction never fired a violation before being
committed to, and (b) size the panels below within the runtime cap. Those probes produced
no committed artefact and are superseded by the panels frozen here; every number reported
in the receipt comes from the frozen run. The construction of `L` and `U`, the panel plan,
the gates and the terminals below were fixed before the analyzer was written.

## 1. The object under study (bound, not re-argued)

The frozen unit-cost TARE grammar of MAX-R6M. An instance `t` is three blocks, each an
ordered pair of Pauli targets on `n` qubits (`target_pairs`). A *configuration* is
six frame Paulis `f_0..f_5` (block `j` owns `f_{2j}, f_{2j+1}`), one shared Tag Pauli `s`,
a per-block central bit, and per-block relative target permutations. Its cost is
`r6s.config_cost` and its acceptance predicate is `r6s.config_labels`:

```
cost = 2·wt(s) + Σ_i m_i·(wt(f_i) − 1) + Σ_{k∈{0,1}} Σ_q F3(u_{k,q}, u_{2+k,q}, u_{4+k,q})
u_i = t_i · f_i ,  m_{2j+e} = 2 if central_j == e else 4 ,  F3(a,b,c) = 1 if a=b=c≠0 else wt(a)+wt(b)+wt(c)
accept ⟺ ⟨f_{j0},f_{j1}⟩ = 1 ∀j , ⟨s,f_{j0}⟩ = l0 ∀j , ⟨s,f_{j1}⟩ = l1 ∀j , l0 ≠ l1
```

`C_DP(t)` is the exact minimum over all accepted configurations — the *exact global
referee* (`max_r6o.dp_cost_frozen_configs`, the frozen 9-bit XOR DP of MAX-R6M).

Receipt bindings that must be reproduced exactly and recorded verbatim (sha256 of each
receipt file plus its `terminal`/`authority` string):

- `research/extensions/orion-q/MAX_R6S_ALL_N_COMPOSITION_RESULTS.json` (`C_DP == C_D++` all n)
- `research/extensions/orion-qg/QG7E_TWELVE_STATES_RESULTS.json` (`C_DP == min(C_D+, f_B′, f_B″)` all n)
- `research/extensions/orion-qg/QG8_OBJECTIVE_SUPPORT_PHASE_RESULTS.json` (the support-2 cone)
- `research/extensions/orion-qg/QG5B_EXACT_FORECASTER_RESULTS.json` (DP-free forecaster + certificate architecture)
- `research/extensions/orion-qg/QG6_SYNDROME_DIMENSION_RESULTS.json` (`search_complexity_corollary`)

## 2. Q1 — the certified interval object (frozen construction)

For every instance a pair of integers `[L(t), U(t)]` is produced with **no call to the
exact referee**. Both are exact integers throughout; a gate asserts that no floating-point
value enters any decision.

### 2.1 U — upper bound, PROVEN BY EXHIBITION

`U(t) = min(U_W1, U_B′, U_B″)` where each member is the minimum over a closed-form family
of *accepted configurations*, each returning an explicit witness configuration:

- **U_W1** — this lane's independent enumerator of the complete weight-one-frame family
  (every frame Pauli of weight exactly 1). Per block a hub qubit, an ordered distinct
  frame-letter pair and a target permutation; the Tag letter at each hub is forced by the
  label orientation and the Tag is zero elsewhere. Hubs range over the union target
  support plus at most three empty representatives.
- **U_B′** — `qg5b.bprime_family_min` (committed, unmodified) + `qg5b.verify_bprime_witness`.
- **U_B″** — `qg7b.bsecond_family_min` (committed, unmodified) + `qg7b.verify_bsecond_witness`.

**Proof obligation (must be discharged per instance, not assumed):** the witness achieving
`U` is replayed through `r6s.config_labels` (acceptance) and `r6s.config_cost` (cost) at
the instance's full `n`, and the replay must return exactly `U`. A witness that fails
replay invalidates the row. Because an accepted configuration of cost `U` exists,
`C_DP ≤ U` holds by exhibition — **independently of the QG-7e classification theorem and
of any referee**. Status: **PROVEN**.

Two auxiliary claims about U are declared separately and are *not* used to prove the
sandwich: (i) that hub restriction to support+3 spares is WLOG (justified by column
equivalence of empty qubits, machine-checked as gate G6); (ii) that `U_W1 == C_D+`
(machine-checked against `r6p.dxx_search(max_weight=1)` on every instance where that
committed enumerator can run, i.e. `n ≤ 4`) — status **PROVEN on n ≤ 4, EVIDENCED beyond**.

### 2.2 L — lower bound, three components, each labelled

`L(t) = max(L_TRIV, L_COL, L_SEP)`.

- **L_TRIV = 2. Status: PROVEN.** Acceptance forces `l0 ≠ l1`, hence `s ≠ I`, hence
  `2·wt(s) ≥ 2`; every other summand of `cost` is non-negative.

- **L_COL = 2 + W(t) − 18 − 2·M_free(t). Status: PROVEN (machine-checked complete local
  domain).** Here `W(t) = Σ_i wt(t_i)` and `M_free(t) = #{(k,q) : t_{k,q} = t_{2+k,q} =
  t_{4+k,q} ≠ 0}`, both O(n) and referee-free. Derivation, verbatim: writing
  `Δ_i := wt(t_i f_i) − wt(t_i) + wt(f_i) ≥ 0` and distributing the frame credit,
  `cost = 2·wt(s) + W − 18 + Σ_{k,q} Ψ_{k,q}` with
  `Ψ(a,φ) = Σ_j [ (m_j − 1)·[φ_j ≠ 0] + d(a_j, φ_j) ] − 2·[a_0φ_0 = a_1φ_1 = a_2φ_2 ≠ 0]`,
  `d(a,φ) = wt(aφ) − wt(a) + wt(φ)`. The **proof obligation** is the per-column inequality
  `Ψ(a,φ) ≥ −2·[a_0 = a_1 = a_2 ≠ 0]` verified over the **complete** domain
  `a ∈ {0..3}^3 × φ ∈ {0..3}^3 × (m_0,m_1,m_2) ∈ {2,4}^3` (**32,768 cases**, zero
  violations required), together with the identity check that the re-derived
  `2·wt(s) + W − 18 + Σ Ψ` equals `r6s.config_cost` on a complete local domain.
  Any violation refutes L_COL and is serialized verbatim.

- **L_SEP = the label-consistency relaxation. Status: PROVEN (homomorphic syndrome
  projection; machine-checked).** The MAX-R6M acceptance syndrome is the 9-bit XOR
  accumulator `δ` with accepting states `{0b010000111, 0b100000111}`. Define the
  **F₂-linear** projection `π : F₂⁹ → F₂⁶`,
  `π(δ) = (b0, b1, b2, b7⊕b8, b3⊕b5⊕b7⊕b8, b4⊕b6⊕b7⊕b8)`,
  i.e. *(each block's two frame Paulis anticommute; each block's Tag syndrome separates its
  two frame Paulis)*. Both accepting states map to `0b111111`. `L_SEP` is the exact
  minimum of the same per-qubit cost over the same option space subject only to
  `π(Σ_q δ_q) = 0b111111`, minimised over the same relative permutations and central
  bits, minus 18. Since every accepted configuration satisfies the projected constraint,
  the relaxed feasible set contains the true one, so `L_SEP ≤ C_DP`. **Proof obligations:**
  (a) `π` is verified linear and `RED = π(FULL)` is verified on the **complete** 4⁷ =
  **16,384**-option local domain and the complete **512**-state syndrome domain;
  (b) both accepting states map to the relaxed target. Interpretation: `L_SEP` is the cost
  the instance would have if the three blocks were **not required to share one Tag label
  orientation**; `C_DP − L_SEP` is exactly the price of cross-block label consistency.

No component of `L` may be asserted from observation. If any component's complete domain
shows a violation the lane terminates `QG10_LOWER_BOUND_REFUTED`.

## 3. Q2 — tightness geometry (frozen measurement)

For every instance record `L`, `U`, `gap = U − L`, the achieving `U` family, the achieving
`L` component, and (where a referee is run) `C_DP`. Report per `n`: the number of rows,
the **tight fraction** `#{gap == 0} / #rows`, and the full gap histogram. Where `gap == 0`
the optimum is **determined without a referee** and regime membership is DECIDED; where
`gap > 0` the row is reported **UNDECIDED** and no regime is assigned. The structural
characterization of the tight region is reported as an **EVIDENCED** predicate only —
never as a theorem.

## 4. Q3 — validation and extrapolation (frozen panels)

The **committed** referee-verified domains of the QG-5b/QG-7c/QG-7d/QG-7e receipts stop at
`n ≤ 4`, because the committed D++/D+ enumerator `r6p.dxx_search` is hard-guarded at
`n ≤ 4` (`EXPECTED_PAIR_COUNTS`) and its tables are `4^{2n}`. Panels:

- **A (complete)** `n = 1`: all `3^6 = 729` instances (each target one of X, Y, Z).
- **B (complete)** `n = 2`: all `6^6 = 46,656` instances whose six targets are weight-one
  Paulis on two qubits. Complete over the stated sub-domain; the sub-domain is declared,
  not silently truncated.
- **C (seeded)** `n = 3` and `n = 4`, 150 instances each, seed `20260822`, targets of
  weight ≤ 2. Within the committed receipts' referee domain.
- **D (seeded, beyond the committed referee)** `n ∈ {5, 6, 8, 12}`, 120 instances each,
  same seed stream. `r6p.dxx_search` cannot run here at all.
- **E (scaling frontier)** `n ∈ {24, 48, 96}`, 40 instances each, same seed stream.

On **every** instance of panels A–E the sandwich `L ≤ C_DP ≤ U` is asserted and the count
recorded. A single violation of `L ≤ C_DP` terminates the lane
`QG10_LOWER_BOUND_REFUTED` with the instance serialized verbatim.

`C_DP` on panels A–E is obtained from this lane's own vectorized re-implementation of the
frozen 9-bit XOR DP, which is **bound instance-by-instance to the committed referee**
`max_r6o.dp_cost_frozen_configs` on panels A and C in full and on a declared seeded
binding sample of panels B, D and E; the binding sample size and zero-mismatch requirement
are gate G3. A mismatch terminates `QG10_CANNOT_CHECK`.

Panels D and E carry results that **no committed receipt of this programme can confirm**;
they are labelled `VERIFIED_BY_LANE_EXTENDED_REFEREE`, never `VERIFIED`. A further panel

- **F (certification-only)** `n ∈ {192, 384}`, 12 instances each,

is run with the referee **deliberately withheld** to exercise the certification-only
operating mode; its rows are labelled `CERTIFIED_NOT_VERIFIED` and carry only the proofs
of `L` and `U`, never empirical confirmation.

## 5. Gates (all must pass; each recorded with its domain size)

- **G1 tables bound** — this lane's independent `LM/SY/LW/F3` tables equal `r6m._LM/_SY/_LW/_F3`.
- **G2 cost identity** — the re-derived `cost = 2·wt(s) + W − 18 + ΣΨ` equals
  `r6s.config_cost` on a complete local domain (size recorded).
- **G3 referee binding** — lane DP == `max_r6o.dp_cost_frozen_configs`, zero mismatches,
  count recorded.
- **G4 L_COL complete domain** — 32,768 cases, zero violations.
- **G5 L_SEP projection** — complete 16,384-option and 512-state checks, both accepting
  states mapped, zero failures.
- **G6 U_W1 column equivalence** — empty-qubit columns identical; spare-representative
  restriction machine-checked.
- **G7 U witness replay** — every reported `U` witness replays through
  `r6s.config_labels`/`r6s.config_cost` to exactly `U`; failures = 0.
- **G8 U_W1 == C_D+** — on every `n ≤ 4` instance where `r6p.dxx_search(max_weight=1)`
  runs; count and zero mismatches recorded.
- **G9 sandwich** — `L ≤ C_DP ≤ U` on every panel A–E instance; count recorded.
- **G10 receipt bindings** — the five receipts above bound by sha256 + terminal string.
- **G11 exact integers** — no float enters any decision; asserted.
- **G12 caps disclosed** — every cap, every sub-domain restriction, every withheld referee
  disclosed in the receipt.
- **G13 no protected access / no chemistry read / no repository file modified.**

## 6. Runtime and reproducibility

Runtime cap **1,500 s (< 25 min)** per run, measured and disclosed. The analyzer is run
**twice**; the two `QG10_INTERVAL_GEOMETRY_RESULTS.json` files must be **byte-identical**
and the canonical stdout token identical. The only RNG is the frozen seed `20260822`.

An **independent pure-primitive verifier**
`development/orion-qg-regime-geometry/qg10_generic_verify.py` is mandatory. It imports no
lane analyzer and no `orion-q`/`orion-qg` module. From pure primitives it re-derives, for
every serialized referee-domain row: its own exact 9-bit DP `C_DP`, its own 6-bit
projected relaxation `L_SEP`, its own `L_COL`, and its own replay of the recorded `U`
witness (acceptance + cost). It re-checks `L ≤ C_DP ≤ U` on every such row and emits
`ACCEPT` or `REJECT`.

## 7. Terminals (frozen, all valid)

- `QG10_CERTIFIED_INTERVAL_GEOMETRY_ESTABLISHED` — every component of `L` proven on its
  stated complete domain, the sandwich holds on every referee instance, and the method
  certifies a stated non-trivial (non-empty, non-degenerate) tight region beyond the
  committed receipts' referee domain.
- `QG10_INTERVAL_TOO_LOOSE__REGION_CHARACTERIZED` — bounds hold but the tight region is
  empty or trivial beyond the committed referee domain.
- `QG10_LOWER_BOUND_REFUTED` — a referee instance violates `L`; first-class discovery,
  serialized verbatim.
- `QG10_CANNOT_CHECK` — a binding, gate or replay obligation could not be discharged.

## 8. Claim boundary (frozen)

Beyond-referee rows are **certifications, never verifications**. The receipt must state,
per row, whether the row was confirmed by a referee and by which one. No claim is made
about other objectives, other grammars, rotation-count trade-offs, chemistry subjects, the
protected stretched-N2 subject, donor novelty or R6 authority.

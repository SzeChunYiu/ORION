# Prior-art gate on the support-2 sharp normal form (κ_R6M = 2) — verdict: NOT novel as mathematics

Gate run 2026-08-23 against the compilation, symplectic, weight-reduction, and gadget
literatures, under fetch-and-quote discipline. Summary of verdicts:

| question | verdict | anchor |
|---|---|---|
| support-≤2 achievability | **FOUND (proven lemma)** | Cowtan–Dilkes–Duncan–Simmons–Sivarajah, arXiv:1906.01734 (QPL 2019), **Lemma 4.5**: every support-`n` Pauli exponential is a Clifford conjugation — assembled from support-≤2 pieces, canonical in the string — of a support-1 rotation; ladder uses `2(n−1)` CX |
| shared-resource ("Tag") cost idea | FOUND | GraySynth / Amy–Azimzadeh–Mosca, arXiv:1712.01859 (2017): shared CNOT ladders across terms; parity-network cost synthesis NP-hard |
| "2 suffices" (universality half) | FOUND | DiVincenzo 1995 (PRA 51, 1015) |
| "1 impossible" (sharpness half) | folklore | weight-1 operators touch one qubit, so any term anticommuting with two commuting independent terms defeats it — elementary symplectic combinatorics; commuting sets DO reach weight 1 (Crawford et al., arXiv:1908.06942), so any counterexample necessarily uses non-commutation |
| the packaged theorem (grammar + cost objective + per-exchange monotonicity + sharpness, parameterised in `n`) | NOT FOUND | searches recorded in gate transcript |
| Hastings weight reduction as the source | NO | arXiv:2102.10030 targets *codes*, adds qubits, achieves weight ≤ 5 — different object and theorem type |
| perturbative gadgets as the source | NO | KKR quant-ph/0406180 etc. are spectral/approximate, not exact cost-preserving rewrites |

Also established by the gate (constrains what the theorem can even claim): the **strong**
simultaneous-conjugation form — "any Pauli set is Clifford-equivalent to all-weight-≤2" —
is **provably false** (a term anticommuting with `m` independent commuting terms must map to
weight ≥ `m`), so κ = 2 is necessarily a *splitting* statement, which is exactly the
Lemma 4.5 / CX-ladder territory.

## The judgement

Every load-bearing mathematical ingredient is published or folklore. What is unclaimed is
the *packaging*: TARE-M2's specific cost objective with per-exchange monotonicity. The
genuine content of the theorem therefore reduces to **TARE's grammar-specific cost
bookkeeping**. The H2O demonstration (8078 → 4972, −38%) lies inside the band that
heuristic compilers already report empirically (PCOAST 32–43%, Symphony ~59% 2q-count,
QuCLEAR up to 77.7% CNOT), so the practical-value half is covered by widely-implemented
heuristics without any theorem.

**Positioning consequence:** the paper cannot stand as a mathematics contribution. If
written, it is a formalization/monotonicity note for the TARE cost model, and must cite
1906.01734 (Lemma 4.5), 1712.01859, DiVincenzo 1995, Fattal et al. quant-ph/0406168, and
distinguish itself from 2102.10030 / quant-ph/0406180. The status
`COMPLETE_FOR_SCOPED_THEOREM_PAPER__SUBMISSION_FORMATTING_REMAINS` is **superseded**: the
scoped theorem's novelty premise did not survive the gate.

## The flagged monotonicity concern — AUDITED, resolved: sound, no defect

A full audit (2026-08-23, same day) traced the objective, the exchange rule, and the H2O
number. Findings:

- **Per-exchange monotonicity is genuinely established and order-free**: each zeroed
  coordinate refunds multiplier `m ∈ {2,4}` while Lemma E bounds the associated `F3`
  increase by ≤ 2, so `ΔC ≤ Σ(2−m) ≤ 0`; termination is well-founded on total frame
  support. Verified by hand on a minimal example: worst case `ΔC = −2` (noncentral),
  `ΔC = 0` (central, exactly the proof's tight case).
- **No smuggling** — the sharing discounts make monotonicity *harder*, not tautological:
  under a naive undiscounted objective the same exchange is strictly easier (`ΔC = −1`).
  The gate's `n → 4(n−1)+1` ladder scenario is a category mismatch: the exchange never
  splits a term into more terms (rotation count fixed at 9); it zeroes coordinates of
  auxiliary generators.
- **The H2O 8078 → 4972 uses a different objective and a greedy heuristic** (R4D pair
  objective + 1%-slack matching), not the R6M theorem's normal form — and the body and the
  results JSON already say so (`authority: ...confirmation_only__not_novelty_authority`).
  The abstract's juxtaposition is a **disclosure item**, not an objective switch.

Two disclosure obligations for any future write-up: (1) state loudly at the abstract that
the H2O point is R4D pair-objective + greedy, not the theorem; (2) gloss "support-count
objective" early as auxiliary-rotation support in a fixed 9-rotation template, to preempt
exactly the CX-ladder misreading this gate itself made.

**Final standing of Q-paper-01:** internally sound (proof, DP referee, and independent
checker consistent; no defect found) — and not novel as mathematics (this gate). A
formalization/monotonicity note for the TARE cost model at specialist venue tier, with the
prior-art citations above mandatory.

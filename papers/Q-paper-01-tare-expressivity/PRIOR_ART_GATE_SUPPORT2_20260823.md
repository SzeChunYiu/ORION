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

## A flagged potential defect — audit required before ANY further use

Under a naive sum-of-supports objective, the ladder rewrite **increases** cost
(`n → 4(n−1)+1`). The theorem's claimed monotonicity therefore leans entirely on the
Tag-sharing accounting. Whether that accounting (i) is internally consistent, (ii) is the
same objective under which the H2O number 8078 → 4972 was computed, and (iii) does not
smuggle the reduction in via the cost definition itself, is **unaudited**. Until that audit
lands, the monotonicity claim is treated as unverified.

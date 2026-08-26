# ORION-22 certificate-necessity theorem V1

**Status:** theorem/falsification contract, frozen BEFORE the necessity checker is executed on this branch. This is the next upward step named by `P12_SELECTION_SUFFICIENCY_THEOREM_V1.md` §7 and by its result receipt's authority boundary: the parent law proved that exact additive charge certificates are **sufficient**; this study asks and answers the converse — are they **necessary**?

This result does not alter the parent theorem, its checker, the parent allocator, the BROKEN robustness receipt, the price-aware successor, any price regime, case, budget, or success gate.

## 1. Model (inherited unchanged from the parent theorem)

A ledger is a finite list of structures `s` with declared integer cost `c_s >= 0` and realized serve-charge delta `delta_s` (the additive certificate difference that enters the objective). With prices `(p_b, p_s) > 0` and integer budget `B`, the charged objective of subset `X` is

`J(X) = p_b * sum_{s in X} c_s + p_s * [sum_{s in X} t_s + sum_{s not in X} r_s]`

which by parent Theorem T1 reduces exactly to budgeted maximization of `sum_{s in X} v_s` with `v_s = p_s * delta_s - p_b * c_s`.

A **selector** is a function `sigma` that maps an information state to one budget-feasible subset. A **coarsening** `pi` maps a ledger to an information state that is a deterministic function of the ledger; `sigma` is `pi`-measurable when its output depends on the ledger only through `pi(L)` (prices, budget, and declared costs are always exactly readable; only the certificate channel is coarsened). `sigma` is **optimal on L** when it returns a subset attaining the full-information optimum of `J` (or equivalently of the marginal-value sum) on `L`.

The registered reduced state for mechanization (identical to the parent checker's, plus `n = 2`):

- structures per ledger `n in {1, 2}`;
- declared costs `{1, 2, 3}`;
- deltas `{-1, 0, 1, 2, 3, 4, 5}`;
- price pairs `{(1,1),(2,1),(1,2),(4,1),(1,4)}`;
- budgets `{0,1,2,3,4,5,6}`.

## 2. Theorem N1 — indistinguishability impossibility (general)

Let `pi` be any coarsening. If there exist ledgers `L, L'` with `pi(L) = pi(L')` at a common `(prices, budget)` such that both full-information optima are **unique** and the two unique optimal subsets are **distinct** (disjointness suffices but is not required), then:

1. every deterministic `pi`-measurable selector fails to be optimal on at least one of `L, L'`;
2. every randomized `pi`-measurable selector has `P(optimal on L) + P(optimal on L') <= 1`, hence worst-case error probability at least `1/2` on the pair.

**Proof.** (1) is the parent T4 argument lifted from price-obliviousness to certificate-obliviousness: a `pi`-measurable selector returns the same subset `Y` for both ledgers; optimality would force `Y` to equal both unique optima, contradicting their distinctness. (2) by averaging: the returned subset distribution is identical on the pair, and two distinct singleton optimal sets cannot both carry the whole distribution. QED.

## 3. Registered coarsening families

The frozen families (each a strict coarsening of the exact certificate field unless noted):

- `C1 sign_only`: `delta -> {-, 0, +}` class of the delta.
- `C2a interval_k2`: `delta -> 2*floor(delta/2)`.
- `C2b interval_k3`: `delta -> 3*floor(delta/3)`.
- `C3a threshold_theta1`: `delta -> 1[delta >= 1]` (one "good-enough" bit at theta=1).
- `C3b threshold_theta2`: `delta -> 1[delta >= 2]`.
- `C4 declared_cost_only`: certificates entirely absent (pi constant in every delta).

Family `C0 identity`: `delta -> delta` (the exact field; not a coarsening — the control).

## 4. Theorem N2 — every registered coarsening admits an impossibility witness (mechanized)

Within the registered reduced state, for each family in Section 3 the checker exhaustively enumerates all unordered ledger pairs sharing the same `pi`-image at common `(prices, budget)` and records whether a **witness pair** exists: both optima unique and the two unique optimal subsets distinct. The claim to falsify: **every coarsening family `C1`–`C4` admits at least one witness pair, while the exact-field control `C0` admits none.**

`C0` admitting none is automatic (equal `pi`-images under identity mean identical ledgers, hence identical optima); it is nonetheless executed as a live control, because a `C0` witness would expose a checker defect (oracle non-determinism or budget mishandling) rather than a theorem failure.

This section is a falsifiable claim, not a guarantee: a family with zero witnesses turns this theorem RED for that family and is reported as such.

## 5. Theorem N3 — reconstruction selectors fail on witnesses (mechanized)

For each family, the two natural reconstruction selectors — **optimistic** (reconstruct every delta in a cell as the cell's maximum reachable delta, then run the exact parent DP) and **pessimistic** (cell's minimum) — must each be caught erring (budget violation or strict objective shortfall) on at least one enumerated cell of the registered state. This proves the witnesses bite real selectors, so N2 is not a vacuous existence claim.

## 6. Theorem N4 — sufficiency/necessity equivalence (the iff)

Within the registered environment (Section 1 state, additive charging, exactly readable prices/budget/costs):

- **(⇐ sufficiency, parent T1–T2)** reading the exact per-structure additive certificates and running the registered integer DP is optimal on **every** ledger of the state;
- **(⇒ necessity, N1–N2)** every strict coarsening of the certificate channel in the registered families admits an indistinguishable pair on which no `pi`-measurable selector — deterministic or randomized — can be optimal on both.

Therefore guaranteed-everywhere optimality by a black-box selector is attainable **iff** the selector's certificate channel is exact (a coarsening injective on the reachable delta set is information-equal to exact, so "strict" is the honest qualifier). This answers the parent receipt's next question in the negative-for-coarser direction: **none of the registered partial/prospective certificate coarsenings recovers the full-information optimum**, so the value of the exact realized certificates cannot be traded away for cheaper prospective information at zero optimality loss.

## 7. Authority boundary

- Necessity here is bounded to the registered reduced state for the witness families, while N1 is general. Nothing here claims real systems cannot be optimized with partial information at some acceptable regret; the claim is exact-optimality impossibility on witnessed pairs.
- No prospective-cost, external, or deployment authority is granted; the parent boundary is inherited unchanged.
- The in-process T2 re-verification (Gate G4 below) does not replace the parent CI falsifier, which remains bound unchanged.

## 8. Frozen checker contract

`check_p12_certificate_necessity_theorem_v1.py` must be implemented independently of the parent DP oracle usage (it reuses `price_aware_selection` only as the *candidate* under test, exactly as the parent checker does) and must fail closed unless ALL of the following hold, printing the full witness counts:

1. **G1 exact-field control (C0).** The identity coarsening yields zero witness pairs over the whole registered enumeration.
2. **G2 family witnesses.** Every family `C1, C2a, C2b, C3a, C3b, C4` yields at least one witness pair; for each family the checker reports total witness pairs, the minimal ledger size of a witness, and the set of unordered delta pairs `{(delta, delta')}` that at least one witness separates.
3. **G3 reconstruction mutants.** For every family, both the optimistic and the pessimistic reconstruction selector err on at least one enumerated cell (budget violation or strict objective shortfall vs. the exhaustive oracle).
4. **G4 in-process sufficiency re-verification.** On every enumerated cell, the parent `price_aware_selection` returns a budget-feasible subset whose objective value equals the exhaustive oracle optimum (parent T2 remains green on shared ground).
5. **G5 enumeration completeness disclosure.** The checker prints the exact counts of ledgers, cells, and pairs evaluated per family; no silent caps. A truncated enumeration is a RED terminal.

Terminal on all gates green: `P12_CERTIFICATE_NECESSITY_THEOREM_FALSIFIER_GREEN`; otherwise `P12_CERTIFICATE_NECESSITY_THEOREM_FALSIFIER_RED` with the failed gates and counts. Both outcomes are publishable results; neither edits any frozen parent artifact.

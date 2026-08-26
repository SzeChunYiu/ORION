# Q1 proof and evidence map V2

**Purpose:** close Q1 mock-review items R1.1–R2.2 by making theorem scope, proof obligations and exact-referee lineage reviewer-auditable.

## Canonical scope label

Throughout Q1, use:

> **R6M/raw-support scope** = the frozen three-block TARE-M2, shared-one-bit-Tag R6M grammar with donor-owned all-three Restore common-factor rule, under the frozen raw support-count objective with multipliers 4 (non-central) / 2 (central).

Any shorthand statement “support two suffices all `n`” means **only** this scope.

## What “frame support ≤2” means

For one frame Pauli `R`, `support(R)` is the number of qubit positions on which `R` is non-identity. The theorem states that every frame Pauli in an exact optimal R6M configuration can be chosen with `support(R) <= 2`.

It does **not** state:

- Tag weight is ≤2;
- only two qubits are active globally;
- only two blocks may be nontrivial;
- every optimal configuration belongs to one small named closed-form family such as `D+`, `B`, `B′`, or `B″`;
- the same bound holds under reweighted objectives or other TARE grammars.

## All-`n` theorem proof-obligation map

| Obligation | Role in theorem | Authority type | Evidence / implementation binding | Scope consequence |
|---|---|---|---|---|
| R6M grammar/objective exactness | defines the object being minimized | frozen definition + exact DP/referee bindings | R6M protocols/results; DP-vs-brute hostile bindings inherited by R6M/R6P | theorem cannot migrate to R6I/other objectives |
| Class construction `class(q)=(alpha,beta) in F_2^2` | records partner anticommutation and Tag-syndrome contribution of each support position | mathematical definition | `MAX_R6S_ALL_N_COMPOSITION_RESULTS.json.exchange_construction` | enables local-to-global parity reasoning |
| Odd-`alpha` multiset property | follows because selected frame anticommutes with its partner | mathematical argument | theorem proof shape in R6S receipt | holds for arbitrary `n` in frozen grammar |
| Lemma B / zero-sum subset | for support `w>=3`, finds proper subset `Q`, `|Q|<=2`, preserving anticommutation and Tag syndrome with zero Tag repair | combinatorial all-`n` lemma; machine corroboration over bounded tuple sizes | R6S `lemma_b`: 43,688 odd-alpha tuples checked through `w=8`; four `w=2` failures exactly match registered boundary | the **written parity argument**, not the bounded census alone, carries arbitrary-`n` authority |
| Exact `w=2` failure classification | explains why the all-`n` descent cannot eliminate every support-two frame | exact finite class characterization + realized witnesses | R6S `w2_failing_tuples_*`; R6O/R6P borrow witnesses | support two is a genuine theorem boundary, not arbitrary cap |
| Lemma E local cost inequality | deleting the selected parity-preserving subset never increases total frozen objective once frame refund and F3 change are included | complete finite local-domain check | R6S `lemma_e`: 18,432 cases, 0 violations, max net 0 | universal local inequality because local alphabet/central choices are finite and exhaustively enumerated |
| No Tag repair after exchange | prevents the coupling term that defeated the earlier R6N local argument | consequence of beta parity preservation | R6S exchange construction | closes the declared R6N analytic gap for `w>=3` |
| Descent measure | repeated exchange terminates in a no-more-expensive configuration with every frame support ≤2 | mathematical induction on lexicographic `(cost,total frame support)` / finite support descent | R6S `exchange_construction.induction`; stress descents are corroboration only | converts local exchange into all-`n` family theorem |
| `D++` equality | identifies support≤2 optimum with the registered D++ family minimum | family-definition / Tag-relaxation binding | R6P D++ definition + R6S theorem claim boundary | yields `C_DP=C_D++` all `n` |

## Machine-check versus theorem distinction

The publication wording must distinguish:

- **Finite exhaustive lemma:** Lemma E is complete because the relevant local state alphabet is finite and the 18,432 cases enumerate it exactly.
- **Combinatorial arbitrary-`n` step:** Lemma B's theorem authority comes from its parity/pigeonhole argument. The `w<=8` census is corroboration and exact boundary checking, not the reason the statement holds for arbitrary `n`.
- **Stress panels:** R6S fresh `n=3/n=4` equality rows and seeded descents are implementation/proof corroboration, never a substitute for the all-`n` argument.

## Exact-referee / witness lineage

| Scientific use | Primary artifact | Independent or hostile binding | Permitted statement |
|---|---|---|---|
| unrestricted R6M optimum | `MAX_R6M_EXACT_THREE_TARE2_SHARED_FACTOR_DP_RESULTS.json` + exact DP implementation | registered DP-vs-brute hostile checks in R6M/R6P lineage | exact cost/witness on the registered frozen grammar |
| split counterexample `8<9` | `MAX_R6N_SUPPORT_DOMINANCE_RESULTS.json` + `MAX_R6O_ENLARGED_TAG_DONOR_RESULTS.json` | witness replay under exact R6M cost/referee | exact counterexample to common-anchor weight-one closure |
| borrow counterexample `5<6` | R6O result | R6P critical-witness re-verification / row-by-row cross-check | exact counterexample to D+ closure |
| finite D++ closure | `MAX_R6P_WEIGHT2_FRAME_DONOR_CLOSURE_RESULTS.json` | exact witness referees + source-row binding to R6O/R6M | finite-domain equality only |
| all-`n` support theorem | `MAX_R6S_ALL_N_COMPOSITION_RESULTS.json` | protocol-bound lemma checks; fresh stress/equality panels and exact predicted-vs-observed descent deltas | theorem only within R6M/raw-support scope |
| finite predicate | `MAX_R6Q_REGIME_PREDICATE_RESULTS.json` | frozen features before labels; held-out/post-freeze panel | exact only on recorded domains |
| prospective 15/15 Benzene result | `MAX_R6R_PROSPECTIVE_FRESH_SUBJECT_RESULTS.json` | stage-1 digest printed before ground truth; exact DP witness checks | prospective bounded confirmation, not theorem |
| later closed-form refutation | `QG5_CERTIFIED_FORECAST_RESULTS.json` / `QG5B_EXACT_FORECASTER_RESULTS.json` | refuting row bound to exact D++/DP witness | refutes universal extension of old closed form, not R6S |
| fourth-regime boundary | `QG7_BPRIME_COMPLETENESS_RESULTS.json`, QG7 generic verification | all 64 witnesses referee-confirmed | companion counterexamples inside D++ |

## Figure/caption scope rule

Any figure containing the all-`n` theorem must state “R6M/raw-support scope” in either the panel title or first caption sentence. Any finite predicate/chemistry panel must show its denominator/domain in the caption and must not share an unlabeled visual glyph with theorem-grade results.

## Publication theorem statement

Recommended exact wording:

> **Theorem (R6M/raw-support support ceiling).** For every qubit count `n` and every instance of the frozen R6M three-block shared-Tag grammar under the frozen raw support-count objective, there exists a minimum-cost compilation in which each frame Pauli has support at most two. Consequently `C_DP=C_D++` for all instances in this scope.

This theorem does not imply a complete closed-form `D+/B′/B″` taxonomy.
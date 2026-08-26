# ORION-22 selection-sufficiency theorem — result receipt V1

**Terminal:** `P12_SELECTION_SUFFICIENCY_THEOREM_FALSIFIER_GREEN`

**GitHub Actions run:** `32693543498`  
**Job:** `97331398280` (`falsify`)  
**Artifact:** `p12-selection-sufficiency-theorem-v1`, artifact id `9508087948`  
**Uploaded artifact ZIP SHA-256:** `c7d51d839f6b08dc96a79cd3f42839f67157a38411a86f90a248da62bf2e95b1`

## Frozen-theorem falsification result

The independent checker executed the exact contract in `P12_SELECTION_SUFFICIENCY_THEOREM_V1.md` without changing the parent allocator, successor allocator, cases, regimes, budget, or result gates.

- ordered reduced-state ledgers checked: **204,204**;
- abstract candidate/oracle cells checked: **7,147,140**;
- shipped `P12_PRICE_AWARE_ALLOCATOR_V1` objective mismatches: **0**;
- deliberate wrong selectors caught: **3/3**;
- bound NR-13 successor cells replayed at zero regret: **195/195**;
- expanded-battery unique-oracle regime cells: **134**;
- expanded cases exhibiting at least two different **unique** price-regime optima: **18/27**.

The 18 empirical T4 witnesses span all three domains. One case (`KNAP_T9_MIXED`) exhibits three distinct unique optimal subsets across the five price regimes. Therefore, on those witnessed cases, no price-oblivious fixed subset can be optimal across all corresponding regimes.

## Mutation witnesses

The exhaustive checker rejected each predeclared hostile mutant:

1. **declared-cost greedy:** rejected on an objective counterexample;
2. **positive-value without budget:** rejected by a budget violation;
3. **reversed-sign marginal value:** rejected on an objective counterexample.

Mutation sensitivity is therefore GREEN rather than a vacuous self-check.

## Scientific interpretation

The parent negative remains authoritative: the frozen q-greedy selector is BROKEN on the price and distribution-shift axes.

The stronger successor statement is now supported at two levels:

1. **proof level:** under additive exact charge certificates and an integer nominal budget, charged-objective minimization reduces exactly to budgeted marginal-value maximization, and the registered dynamic program is globally optimal;
2. **falsification level:** no counterexample was found in the exhaustive 7,147,140-cell reduced state, while all three wrong selector families were detected.

The real battery supplies 18 direct impossibility witnesses for price-oblivious fixed selection under differing unique optima.

## Authority boundary

This receipt does **not** establish that exact charge certificates are free, prospective, externally measured, or available in a deployment before materialization. It establishes optimal selection **conditional on** those exact additive certificates. The next ORION-22 study must ask how much prospective/partial cost information is sufficient and must score abstention/coverage so a trivial refuse-all policy cannot count as success.

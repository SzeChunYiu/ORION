# DONOR-FIRST REFUSAL -- DISC-Q-TRANSFER-01
Authority: **target-domain result only**. No quantum authority is transferred; nothing below is a physical, hardware, or quantum-advantage claim.
## 1. The donor names its own donors
QG-paper-03 (`papers/candidates/qg-paper-03-stub/MANUSCRIPT_V1.md`, sha256 `f29edbad739e86dd61181e7162c2d579c219d64f765e6b5612c446df9b8a6c2e`) states, in its own words, that it
> claims no novelty for finite-field dependence, support sparsification, Pauli symplectic representations, or parametric/polyhedral optimization
Support sparsification is therefore a **donor discipline, not a transferred contribution**. Any target result that classical sparsification or minimum set cover already delivers must be credited to that donor.
## 2. What the strongest donor achieves WITHOUT the transfer
**D1 -- total exact enumeration.** Enumerating all 524288 subsets returns the exact Pareto frontier (2 optima) and, as a by-product, the exact value kappa_t = 9. The donor alone answers the entire question.
**D2 -- classical irredundant-cover sparsity, no enumeration at all.** Every frontier plan is an irredundant cover: if a job could be dropped with coverage preserved, the smaller plan's node and edge unions are subsets, so its cost vector is componentwise <= and the larger plan would be dominated. In an irredundant cover each member holds a private obligation, so support <= |obligations| = 13. This is textbook set-cover reasoning and needs zero search. Verified on the frontier: holds, 0 violations.
## 3. Residual after subtraction
| Object | Donor alone | With Q transfer | Residual |
|---|---|---|---|
| Exact frontier | yes (D1) | same | none |
| Support bound | <= 13 (D2, free) | kappa_t = 9 | 4 tighter, but only via the D1 oracle |
| Two-sided typing | not asked | asked and answered | **discipline only** |
| Objective indexing | not asked | asked, NOT EXERCISABLE | **question only** |

The objective-indexing phenomenon cannot be exercised here, and it would overstate the evidence to call it refuted. kappa_t = 9 under the Pareto order and under every single-component objective, because support 9 is forced by COVERAGE -- a combinatorial floor independent of the objective -- and every frontier cost is attained at that floor. Since any strictly monotone objective attains its optimum at a non-dominated cost vector, no objective whatsoever can yield a different kappa on this instance (relation R4, NOT_EXERCISED).

The tightening from 13 to 9 is a real target-domain fact, but it is not a capability the transfer supplies: kappa_t is knowable only after the same total enumeration D1 performs. Charged honestly, the transferred arm costs at least as much as the donor on every resource component.
## 3b. The transferred quantity collapses to a covering number
kappa_t = 9 is exactly the minimum cardinality of a covering subset -- the classical minimum set-cover optimum. So in this target the transfer does not even contribute a new QUANTITY: it renames one the donor disciplines already own, and QG-paper-03 itself disclaims novelty for support sparsification. This is the sharpest reason the residual is empty.
## 4. Refusal
The transfer claim is **refused** for: computing the frontier, computing kappa_t, and any search-cost advantage. The objective-indexing phenomenon is neither credited nor refuted: this instance cannot exercise it. It is **credited only** with one thing: the two-sided claim-typing discipline that distinguishes a one-sided support bound from an intrinsic support number, and the habit of asking whether a bound is objective-indexed. That discipline changed what was ASKED in the target; it did not change what could be computed, and on this instance both questions came back answerable by the donor alone.
## 5. Where the donor wins, stated plainly
On this instance the donor wins outright. D1 answers everything; D2 supplies a sound bound for free. The honest verdict is that ORION-Q contributed a QUESTION here, not a METHOD.

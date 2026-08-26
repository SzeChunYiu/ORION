# ORION-01 figure contract — V3

This contract follows the journal-aware figure workflow from the pinned `academic-paper-skills` repository. It defines scientific roles before visual styling. It is not a production-format specification; exact dimensions/fonts/export rules are resolved only after the target journal/article type is fixed.

## Figure 1 — From unrestricted support to the sharp support-two normal form

**Reader question:** What does the theorem change about the compiler design space?

**Scientific conclusion:** Although a frame Pauli may have support growing with `n`, an optimum always has a representative with frame support <=2.

**Panel plan**

- **a, unrestricted object:** one frame `R` with active coordinates `q_1,...,q_w`, `w>=3`, paired with `R'` and the common Tag `S`.
- **b, local invariant:** each active coordinate carries `c_q=(alpha_q,beta_q) in F_2^2`; highlight either a `(0,0)` singleton or an equal-class pair whose sum is zero.
- **c, exchange:** remove the selected one/two coordinates; show `Delta frame <= -2 per coordinate`, `Delta Restore <= +2`, and unchanged Tag syndrome.
- **d, descent:** repeated exchanges end in support <=2, visually separated from system size `n`.

**Must show:** the operation is support deletion inside one frame, not deletion of physical qubits or gates.

**Must not imply:** runtime speedup of the production DP, two-qubit-only quantum circuits, or a general TARE theorem.

## Figure 2 — Why the bound cannot be reduced to one

**Reader question:** Why is two sharp rather than an artifact of the proof?

**Scientific conclusion:** the only two-coordinate parity obstruction is realized by an exact optimum.

**Panel plan**

- **a, zero-sum failure at w=2:** show the four ordered class patterns `(1,2),(1,3),(2,1),(3,1)` under class coding `2 alpha + beta`; visually mark that no proper nonempty zero-sum subset exists.
- **b, compiler meaning:** one coordinate carries Tag syndrome even when local partner anticommutation contribution can look removable.
- **c, exact witness:** side-by-side cost boxes `support-one optimum C_D+=6` and `unrestricted/support-two optimum C_DP=5`.
- **d, interpretation:** `pay local frame support -> save shared Tag/Restore cost`.

**Must not imply:** these four class patterns are a complete taxonomy of all support-two compiler regimes.

## Figure 3 — Evidence ladder and scope

**Reader question:** How was an all-size theorem separated from finite evidence and later follow-up?

**Scientific role:** confidence/reproducibility, not novelty.

Suggested sequence:

`local exact checks -> support-one counterexample -> finite support-two closure -> prospective benzene forecast -> analytic all-n theorem`

Add a side boundary box:

`later QG: richer support-two taxonomy; does not refute kappa_R6M=2`.

## Main-text / supplementary allocation

- Figures 1 and 2 are main-text priority.
- Figure 3 can be main text for PRX Quantum if space permits, otherwise Supplementary/Extended presentation.
- Chemistry/H2O numerical grounding should be a compact table or supplementary figure unless the target editor specifically asks for application breadth.
- The original 18,432/43,688 enumerations belong in a proof-verification table/SI, not a visually dominant main figure.

## Visual integrity requirements

- Use the same symbols `R`, `R'`, `S`, `alpha`, `beta`, `c_q` as the manuscript.
- Keep theorem evidence and finite-domain corroboration visually distinct.
- Use no 3D effects or decorative quantum-circuit imagery unrelated to the proof.
- Every diagram arrow must correspond to an allowed exchange or logical implication in the proof.
- Final source should be vector (SVG/PDF) with editable labels and a reproducible generation source when possible.

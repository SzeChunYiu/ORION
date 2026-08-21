# QG-14C compositional regime closure — frozen protocol

Issue #844. Base `c5ba39fef4f25c46de5fb69bf07f50530f4693ca`.

## Separable positive theorem
For components i with local choice set A_i and costs c_i(a_i), if global cost is exactly `sum_i c_i(a_i)` and feasibility is Cartesian, then choosing an argmin independently for every component is globally optimal. Machine-check the algebraic inequality and exhaustive finite control families.

## Mandatory shared-resource refutation
Freeze two components with local options:
- A: local cost 0, shared-resource demand 1;
- B: local cost 1, shared-resource demand 0.
Independent local optimization chooses `(A,A)`.
Global coupled objective adds penalty 5 when total shared demand >=2.
Thus:
- `(A,A)=5`
- `(A,B)=1`
- `(B,A)=1`
- `(B,B)=2`
and independent local selection is globally wrong.

## Coupling-aware repair
Export one additional interface coordinate: total shared-resource demand. A composition layer that optimizes local costs plus the frozen penalty over that summary must recover the monolithic optimum set `{(A,B),(B,A)}` exactly.

## Scientific interpretation
- Separable regime composition is theorem-valid under exact separability.
- Hidden coupling refutes unconditional local-optimum composition.
- A sufficient exported coupling coordinate can restore exactness on this control, but no universal compressed interface is claimed.

Terminal:
`QG14_SEPARABLE_COMPOSITION_PROVED__HIDDEN_COUPLING_REFUTES_LOCAL_SELECTION__COUPLING_AWARE_SUMMARY_RECOVERS_CONTROL`.
No novelty/R6/physical-advantage authority.
# QG-11C fault-tolerant lift closure — frozen protocol

Issue #843. Base `c5ba39fef4f25c46de5fb69bf07f50530f4693ca`.

## Positive theorem
For structural resource vector `r`, affine FT map `r_F=A r+b`, and physical scalar objective `lambda^T r_F`, prove exactly
`lambda^T(A r+b) = (A^T lambda)^T r + lambda^T b`.
Thus a structural polyhedral phase certificate may be pulled back through an affine resource map by `theta=A^T lambda`, with the additive constant irrelevant to regime comparison.

The machine packet must verify the coefficient identity componentwise over several exact integer/rational matrices and also by exhaustive finite resource-vector controls. This is ordinary linear algebra and receives no novelty credit.

## Mandatory nonlinear counterexample
Use the frozen integer-factory surrogate
`P(T,D)=10*ceil(T/8)+D`.
Compare routes:
- A: `(T,D)=(9,0)`, structural scalar `T+D=9`, physical `P=20`;
- B: `(T,D)=(8,2)`, structural scalar `T+D=10`, physical `P=12`.
The structural linear objective prefers A while the nonlinear FT surrogate prefers B. Also certify non-affinity by midpoint/additivity failure.

This proves that affine phase pullback does not automatically survive integer factory batching / piecewise resource maps; the physical interface must expose the nonlinear coordinate or use piecewise certificates.

## Real hardware boundary
No live FT resource-estimator identity/backend is frozen in this closure packet. Real hardware/QEC transfer is therefore `CANNOT_CHECK_REAL_ESTIMATOR` and must not be inferred from the surrogate.

Terminal:
`QG11_AFFINE_FT_PHASE_PULLBACK_PROVED__NONLINEAR_FACTORY_COUNTEREXAMPLE__REAL_ESTIMATOR_CANNOT_CHECK`.
No novelty/R6/physical quantum-advantage authority.
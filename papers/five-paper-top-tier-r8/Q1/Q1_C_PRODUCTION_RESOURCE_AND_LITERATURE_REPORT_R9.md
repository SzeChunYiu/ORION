# Q1-C R9 production-resource and current-literature audit

**Source base:** PR #1428 at `1e18787841d99d76a3c7661505838d2eca8780db`  
**Search cutoff:** 2026-08-26 18:29:50 UTC  
**Resource terminal:** `PARTIAL_RESOURCE_MAP`  
**Literature terminal:** `NOVELTY_NOT_ESTABLISHED`  
**Portfolio terminal:** `Q1_THEOREM_CLEAR__PRODUCTION_MAP_PARTIAL` is the highest possible terminal from this lane alone; Q1-A/D and the portfolio owner still control theorem-selection and independent-review authority.

## What the theorem counts

For the frozen R6M three-block TARE-M2 family, the support objective is

\[
C=\sum_{j,k}m_{jk}\bigl(w(R_{jk})-1\bigr)
  +2w(S)+\sum_{q,k}F_3(T_{Ak}[q],T_{Bk}[q],T_{Ck}[q]),
\qquad m_{jk}\in\{2,4\}.
\]

Here `w` counts nonidentity system-register Pauli letters. It is not a physical-qubit count. The support-two theorem says that, for this grammar and objective, an optimum has each of its six frame Paulis supported on at most two system positions.

## Conditional production map

Under one explicit logical circuit template—an all-to-all compute/rotate/uncompute parity ladder, native single-control Pauli Cliffords, the TARE-M2 three-exponential sandwich, and no routing or cross-operation cancellation—the coefficients have a circuit meaning:

- noncentral frame excess support: `4` logical two-qubit Clifford entanglers per coordinate;
- central frame excess support: `2` such entanglers per coordinate;
- shared Tag support: `2` controlled-Pauli letters per coordinate (Tag plus Tag-dagger);
- factored Restore: `1` controlled-Pauli letter per surviving `F3` unit; and
- non-Clifford content: exactly `3(2m-1)=9` arbitrary-angle rotations for three `m=2` blocks, independent of frame support.

Thus, only under these premises,

\[
\Theta_{\mathrm{logical}}(x)
=9\,\kappa_{\mathrm{rot}}
+c_{2q}\,C(x),
\]

where `kappa_rot` cannot be priced without the angles, precision allocation, synthesis method, and fault-tolerant execution model. The theorem preserves the optimum for the variable logical Clifford term because the rotation term is family-constant. It does **not** imply a reduction in T count, T depth, logical depth, qubits, physical spacetime, wall-clock time, or hardware error.

The internal QG-21 receipt is retained only as a bound cross-check. Its adverse result remains visible: primary `theta_FT` chemistry was donor-exact on `90/90` rows; only sensitivity `S1` improved `18/90`, by two logical two-qubit Cliffords, against an invariant nine-rotation backdrop.

## Current primary-source subtraction

Sixteen version-bound primary sources were inspected from public arXiv records/PDFs. The closest current boundaries include:

- TARE v4: owns TARE, Tag/Restore, auxiliary-frame/control freedom, and the donor resource tradeoffs;
- PCOAST, PHOENIX, and Symphony v2 (updated 2026-08-25): own broad Pauli-frame and binary-symplectic compiler optimization territory;
- Izmaylov et al. and van den Berg–Temme: own anticommuting unitary partitioning and Pauli-cluster optimization;
- Cowtan et al.: owns phase-gadget/parity-network synthesis territory;
- Amy–Maslov–Mosca: owns matroid-partition T-depth optimization;
- Kliuchnikov–Maslov–Mosca and Ross–Selinger: own exact/approximate Clifford+T rotation-synthesis results;
- Li et al. and Zhang–Shao: own current general sparse-T-count and low-ancilla block-encoding results; and
- Sun–Koczor, Harvest, FTCircuitBench, and MQT Bench delimit physical space/time, resource-aware compilation, and benchmark methodology.

After subtraction, the only residual candidate is the exact, sharp, grammar-specific statement `kappa_R6M=2`, including its support-one lower witness and weight-two obstruction. The bounded search did not locate a direct equivalent, but this is **not** a novelty certificate. Exact-phrase arXiv queries produced false negatives even for the known donor, OpenAlex contained duplicate donor identities, and same-lane review is not independent review.

## Required next evidence

1. Q1-A plus the portfolio owner must select the portfolio-authoritative theorem source.
2. A target architecture must freeze native gates, connectivity, routing, cancellation, ancillas, and scheduling.
3. A precision/error budget and rotation-synthesis protocol must bind T count and T depth.
4. A fault-tolerant model must bind code, physical error rate, code distance, factories, decoder, and failure target.
5. Q1 needs measured compiler benchmarks with registered baselines rather than structural receipts alone.
6. Q1-D must perform independent quantum-compilation and submission-date novelty review.

Until then, physical-resource, superiority, novelty, venue, and journal-grade authority remain `CANNOT_CHECK` or false, not silently inferred from CI or hashes.

# ORION-Q MAX-R6 coefficient-factorisation donor absorption

Date: 2026-08-20
Parent: #679
Branch: `shadow/orion-q-max-r0`
Status: frozen before any fresh R6 coefficient read.
Authority: theorem/donor absorption only; no novelty credit.

## Why this is absorbed

Generic block-encoding/LCU theory already owns asymmetric state-preparation pairs: two normalized preparation amplitudes may have elementwise products proportional to the desired LCU coefficients, with the l1 norm as the optimal normalization. ORION therefore receives no novelty credit for coefficient factorisation itself.

TARE v4 fixes the coefficient magnitudes entirely in the anticommuting system unitary and uses a uniform final projection over tag states. That choice yields `sqrt(m) ||alpha||_2`. Once native Self-ORION has selected method-language growth, the fair donor-composed language must include the generic state-preparation-pair degree of freedom rather than artificially keeping TARE's coefficient placement fixed.

## Exact generalized construction

Let

`A = sum_k alpha_k P_k`, `a_k=|alpha_k|`.

Choose a real parameter `p in [0,1]` and define

`u_k = a_k^p / U_p`, with `U_p = sqrt(sum_k a_k^(2p))`,

`v_k = a_k^(1-p) / V_p`, with `V_p = sqrt(sum_k a_k^(2(1-p)))`.

For any pairwise anticommuting auxiliary family `R_k`,

`U_anti(p) = sum_k u_k R_k`

is unitary. After Tag and Restore, replace TARE's uniform final projection by a state-preparation-pair projection whose overlap with tag state `|c_k>` is `v_k`. The encoded block is then

`sum_k u_k v_k exp(i phi_k) P_k = A / (U_p V_p)`.

Hence the exact subnormalization is

`Lambda_p = U_p V_p`.

At `p=1`, this recovers the coefficient placement used by TARE v4:

`Lambda_1 = sqrt(m) ||alpha||_2`.

At the symmetric split `p=1/2`,

`U_{1/2}=V_{1/2}=sqrt(sum_k a_k)`

and therefore

`Lambda_{1/2}=||alpha||_1`.

## Optimality theorem

For arbitrary normalized real amplitude vectors `u,v` satisfying

`u_k v_k = a_k / Lambda`,

Cauchy-Schwarz gives

`sum_k a_k / Lambda = sum_k u_k v_k <= ||u||_2 ||v||_2 = 1`,

so `Lambda >= ||alpha||_1`.

The symmetric square-root factorization attains equality. Thus `p=1/2` is normalization-optimal within this factorized anticommuting/tag-projection family.

This theorem is a specialization of the standard state-preparation-pair mechanism and is not claimed as a new block-encoding normalization result.

## Resource consequence

Changing `p` changes rotation angles and the final preparation/projection amplitudes, but not:

- auxiliary-frame anticommutation constraints;
- number of `2m-1` Uanti Pauli rotations;
- Tag/Restore support topology for a fixed frame/label assignment;
- block cardinality.

At fixed synthesis tolerance, arbitrary-angle synthesis cost must be recomputed from the actual preparation circuit. It may not be assumed angle-independent if a special uniform preparation simplifies.

## ORION residual after absorption

The remaining candidate operation is not coefficient factorization. It is the joint compiler that chooses, under one proof-carrying resource model:

`partition -> cardinality -> direct vs corrected block -> coefficient placement -> auxiliary frame -> native matches -> Tag/Restore -> controlled implementation -> outer composition`.

All donor pieces retain first right of refusal.

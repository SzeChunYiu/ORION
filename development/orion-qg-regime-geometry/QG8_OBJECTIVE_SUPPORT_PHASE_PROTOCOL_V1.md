# ORION-QG QG-8 — objective-indexed support phase theorem protocol V1

Date: 2026-08-21
Parent: #740
Issue: #760
Base: `318d1cbbec451170448bb8e126c7ab50801930ce`
Status: **FROZEN BEFORE QG-8 MACHINE OUTCOME**.
Authority: theorem-research only; no novelty, paper, merge, or physical-advantage authority.

## Scientific question

For the frozen R6M shared-Tag grammar, determine an objective-parameter region in which the existing R6S zero-sum exchange still proves an all-n support-<=2 optimal normal form.

Parameterized within-family objective:

`C_theta = t_nc U_nc + t_c U_c + t_tag w(S) + t_r F3 + rho * rotations`,

with positive `t_nc,t_c,t_r`, nonnegative `t_tag,rho`. Grammar/semantics/F3 are unchanged. Every R6M family member has the same frozen 9 rotations.

## Frozen theorem candidate

R6S Lemma E zeroes selected frame support on a class-zero-sum subset while preserving Tag syndrome exactly. The full local domain has 18,432 cases. For each deleted support unit, let `df3 = F3(new)-F3(old)`.

QG-8 independently re-enumerates that domain from production local Pauli/F3 tables and must recover:

- maximum `df3` for a central-frame deletion = 2;
- maximum `df3` for a noncentral-frame deletion = 2;
- an explicit central equality witness with `df3=2`;
- production R6S receipt binding (`domain_size=18432`, `max_delta_f3=2`, zero violations).

The weighted deletion therefore satisfies

- central: `Delta <= 2*t_r - t_c`;
- noncentral: `Delta <= 2*t_r - t_nc`.

If

`t_c >= 2*t_r` AND `t_nc >= 2*t_r`,

every R6S zero-sum deletion is non-increasing. On equality, lexicographic `(objective,total frame support)` minimality gives strict progress in support; above equality cost strictly decreases. R6S Lemma B/F2^2 subset existence is unchanged. Hence:

> For all n and every admitted frozen-R6M instance, objective parameters in this cone imply an unrestricted optimum with every frame Pauli of global support <=2; equivalently `C_DP(theta)=C_D++(theta)`.

`t_tag` does not enter because Tag is preserved by the exchange. `rho` does not enter because all R6M family members have nine rotations.

## Controls

The checker binds QG-2's committed receipt and classifies:

- O0 `(t_nc,t_c,t_tag,t_r,rho)=(4,2,2,1,0)`: inside, central equality boundary;
- O2 `(4,2,2,1,5)`: inside, same structural phase;
- O1 `(7,1,4,3,0)`: outside (`1<6`) and QG-2 supplies a global `NEW_SUPPORT3` witness with `C_DP=11<C_D++=13`.

This proves no objective-independent support-two theorem exists. O1 does NOT prove the half-space boundary globally sharp.

## Certificate-boundary sharpness

The local enumeration must serialize at least one central case with `df3=2`. Thus the R6S *certificate* is exact at `t_c=2*t_r`: below that hyperplane the same local rewrite can increase weighted cost. This is a proof-method boundary only until a global family witness is available arbitrarily close to the hyperplane.

## Production binding

The checker imports only frozen production local algebra/F3 arrays and receipts. It must assert independent tables equal R6M `_LW/_LM/_SY/_F3`. No chemistry loader is called.

R6S required fields:
- authority prefix `MAX_R6S_ALL_N_COMPOSITION_THEOREM_MACHINE_CHECKED`;
- `lemma_e.domain_size=18432`, `violations=0`, `max_delta_f3=2`;
- `lemma_b.w3_to_w8_all_admit_subset=true`;
- `gates.bindings_exact=true`, `gates.no_new_subject_data=true`.

QG-2 required fields:
- authority `ORIONQ_QG2_OBJECTIVE_ROBUSTNESS_MIXED__FROZEN_REWEIGHTED_OBJECTIVES__NOT_R6`;
- O0/O1/O2 weights recovered from receipt;
- at least one serialized O1 support-three witness with `C_DP=11` and `C_Dxx=13` or an equivalently exact support-two failure;
- no new subject access beyond QG-2's frozen receipt.

## Independent generic verification

The generic ORION verifier must independently rebuild F3 from local weight/multiply primitives and rerun the 18,432 symbolic-resource domain. It compares maxima, histogram, equality witness class and receipt hashes; it does not trust the theorem terminal.

## Native ORION-Q controller

Consumes only analyzer + generic verifier serialized evidence and records `ACCEPT_SUPPORT2_CONE / REJECT / CANNOT_CHECK`. It may not classify an outside-cone objective as requiring support >=3 unless a separate global witness is bound.

## Positive terminal

`QG8_OBJECTIVE_INDEXED_SUPPORT2_CONE_ALL_N_MACHINE_CHECKED`

## Honest alternatives

- `QG8_LOCAL_RESOURCE_VECTOR_REFUTED`
- `QG8_R6S_BINDING_REFUTED`
- `QG8_QG2_OUTSIDE_CONTROL_REFUTED`
- `QG8_NATIVE_GENERIC_DISAGREEMENT`
- `QG8_CANNOT_CHECK`

## Scope boundary

This theorem is only for the frozen R6M grammar and the stated linear within-family objective. It does not prove support-three sufficiency outside the cone, global sharpness of the cone, a complete objective phase diagram, or physical quantum advantage. Linear/polyhedral parametric optimization itself receives zero novelty credit.

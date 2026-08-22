# QG-16 — objective-indexed all-n support1 phase for R6I

Date: 2026-08-21
Issue: #811
Parent support1 theorem: #807 / PR #809 / protected receipt commit `9397a6b671b3f568e635355e2dc01ed263ae1e13`
Parent support2 theorem: PR #792 / protected receipt commit `a80dbd57d9124f058de7465a13de8c69416c368b`
Branch: `shadow/orion-qg-qg16-r6i-support1-phase`
Status: **FROZEN BEFORE PARAMETRIC CHECKER OUTCOME.**
Authority ceiling: bounded theorem about frozen R6I objective space only; no novelty/R6/physical-advantage authority.

## Target

For the frozen R6I grammar, reweight only structural coordinates:

`C_theta = sum_blocks [ t_c*(w(R_c)-1) + t_nc*sum_{k!=c}(w(R_k)-1) ] + t_tag*(w(S0)+w(S1)) + t_r*sum_k w(Restore_k)`

with nonnegative coefficients and `t_r>0`.

Prove that every objective satisfying the mechanically derived support1 certificate cone has

`C_DP(theta) = C_cap1(theta)` for every n.

Support0 is infeasible, hence `kappa(theta)=1` throughout the certified cone.

## Parent structural lemma

The protected support<=2 parent gives `w(R0),w(R1)<=2`. Global `<R0,R1>=1` means the number of local anticommuting columns is odd. Each anticommuting column contributes one support unit to both generators, so under support<=2 there can be at most two; hence there is **exactly one** local anticommuting core. Every non-core active column is locally commuting.

The parametric theorem therefore needs only the resource geometry of deleting a commuting active column.

## P1 — complete commuting deletion resource domain

Enumerate every local pair `(a,b)!=(I,I)` with `local_symp(a,b)=0`, every target-letter triple `(p0,p1,p2) in {I,X,Y,Z}^3`, and every central branch `c in {0,1,2}`.

For each row zero `(a,b)->(I,I)` and recompute dependent `R2=a*b`. Record the exact resource-change vector in **credit coordinates**:

- `refund_c`: number of support units removed from the central frame branch;
- `refund_nc`: number removed from noncentral frame branches;
- `delta_restore`: `Restore_after - Restore_before` in support units.

Weighted deletion credit is

`refund_c*t_c + refund_nc*t_nc - delta_restore*t_r`.

The checker must enumerate the complete domain, Pareto-reduce it in the direction “smaller refunds / larger Restore increase is worse for all nonnegative coefficients”, and identify the exact worst affine forms. Expected certificate forms are:

- `t_c + t_nc - 2*t_r`;
- `2*t_nc - 2*t_r`.

This expectation is a frozen falsifiable target, not an authority source. Serialize equality witnesses for every retained worst vector.

## P2 — core alignment resource domain

Enumerate all 6 ordered old anticommuting local bases x 6 new bases x 64 target triples x 3 central choices = 6,912 rows.

Record resource changes. The frame-coordinate delta must be zero for every row and the exact maximum Restore increase must be `3`, yielding alignment obligation `3*t_r`.

## P3 — Tag currencies

Bind and independently reconstruct the V6 Tag facts:

- same-core canonical Tag support units = 2 -> cost `2*t_tag`;
- distinct-core canonical Tag support units = 4 -> cost `4*t_tag`;
- every feasible original shared Tag has support units >=2 -> old cost floor `2*t_tag`;
- when both localized blocks are already support1 on distinct cores, exact old Tag support floor = 4 -> cost floor `4*t_tag`.

## P4 — mechanically derived cone

Let the two worst commuting-deletion credits be `D1(theta)` and `D2(theta)` from P1.

The V6 composition requires every possible extra-column credit to pay:

- alignment: `3*t_r`;
- additional Tag relocation over the universal old-Tag floor: `2*t_tag`.

Therefore require each retained worst deletion form to dominate both obligations. The intended irredundant full certificate is the four inequalities:

1. `t_c + t_nc >= 5*t_r`
2. `2*t_nc >= 5*t_r`
3. `t_c + t_nc >= 2*t_r + 2*t_tag`
4. `2*t_nc >= 2*t_r + 2*t_tag`

Under the separately declared conventional ordering `t_c<=t_nc`, the checker may prove (2),(4) redundant and report the simplified pair (1),(3). No redundancy may be assumed without the ordering premise.

## P5 — exact rational controls

All classification uses `fractions.Fraction`.

Frozen points:

- `O0=(t_nc,t_c,t_tag,t_r)=(4,2,2,1)` — expected inside and exactly on a Tag-relocation facet;
- `O_in=(5,3,2,1)` — expected strict interior;
- `O_tag_out=(4,2,5/2,1)` — expected outside Tag-relocation certificate;
- `O_restore_out=(4,2,2,5/4)` — expected outside at least one Restore/alignment certificate;
- `O_nc_out=(3/2,3/2,1,1)` — expected outside noncentral/refund certificates.

Serialize all facet margins exactly as rational numerator/denominator pairs.

## P6 — certificate-boundary witnesses

Require exact local equality witnesses for every retained P1 worst resource vector and at least one equality objective/witness combination on the unit-objective Tag facet.

`GLOBAL_PHASE_BOUNDARY_SHARPNESS = OPEN` remains mandatory. A point outside the cone means only `THIS_PROOF_CERTIFICATE_DOES_NOT_APPLY`; it must never be interpreted as `SUPPORT2_REQUIRED`.

## P7 — parent bindings

Bind:

- V6 protected terminal `QG9_RANK2_ALL_N_SUPPORT1_SUFFICIENCY_MACHINE_CHECKED`, both harnesses accepted, support bound/kappa one;
- V4 protected support2 parent;
- V6 exact local constants (deletion -4 unit commuting, alignment +3, Tag floors 2/4 support units).

Parent unit-objective results are controls/lemmas; the parametric cone must be re-derived from resource vectors, not copied from prose.

## Independent generic ORION

Rebuild phase-free Pauli algebra as `F_2^2` without importing production R6I/P10 tables. Re-enumerate P1/P2, derive the Pareto-worst vectors and four inequalities, classify all rational controls, and verify parent identities only after the independent derivation is sealed.

## Native ORION-Q

May accept only `SUPPORT1_PHASE_CERTIFICATE` if:

- production and generic resource vectors/facets agree;
- parent support1 theorem is protected;
- every composition obligation is explicit;
- `OUTSIDE_CONE != SUPPORT2_REQUIRED`;
- global sharpness remains OPEN.

## Intended positive terminal

`QG16_R6I_OBJECTIVE_INDEXED_SUPPORT1_CONE_ALL_N_MACHINE_CHECKED`

Honest alternatives: resource-vector mismatch, facet/composition gap, parent-binding gap, generic/native disagreement, CANNOT_CHECK.

## Novelty boundary

Multi-objective/Pareto quantum compilation, scalar weight tuning, parametric/polyhedral optimization and hardware-aware cost selection receive zero novelty credit. Candidate contribution is only this compiler-specific, proof-carrying all-n normal-form phase theorem.
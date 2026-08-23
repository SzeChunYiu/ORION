# QG-17 — sharpness attack on the R6I support1 objective phase

Date: 2026-08-21
Issue: #814
Parent phase theorem: #811 / PR #813 / protected receipt `406886f55aaaa08a4b310d336e3c98a87371e97e`
Parent support1 theorem: #807 / PR #809
Frozen candidate generator owner: #795 / PR #796
Branch: `shadow/orion-qg-qg17-r6i-phase-sharpness`
Status: **FROZEN BEFORE WEIGHTED CANDIDATE SCORING.**

Authority ceiling: exact finite support-phase witness / sharpness evidence for frozen R6I only; no novelty/R6/physical-advantage authority.

## Question

At QG-16's pre-registered outside objectives, does a verified feasible support2 configuration beat the exact support<=1 optimum?

A strict gap

`C2(theta) < C_cap1(theta)`

implies `C_DP(theta) <= C2(theta) < C_cap1(theta)` and is therefore sufficient to prove that support1 is not globally sufficient at that objective. No weighted unrestricted DP is required.

## Frozen objectives and order

All arithmetic uses exact `Fraction`.

Control first:
- `O0=(t_nc,t_c,t_tag,t_r)=(4,2,2,1)`; QG-16 proves support1 exact, so strict witnesses MUST be zero.

Outside controls, frozen order:
1. `O_tag_out=(4,2,5/2,1)`;
2. `O_restore_out=(4,2,2,5/4)`;
3. `O_nc_out=(3/2,3/2,1,1)`.

No other objective may be added after scoring.

## Candidate generator — exact V5 reuse

Import without modification the generator functions from `qg9_support2_tightness.py`:

- `obstruction_blocks()`;
- `candidate_pairs()`;
- `template_instances()`;
- family order `IDENTITY_RESTORE`, `ONE_DEFECT_A`, `ONE_DEFECT_B`, `MATCHED_DEFECT`;
- original pair/template enumeration order.

Recompute the generator pre-score and require its SHA-256 to equal canonical V5's committed `candidate_generator_digest_before_scoring = bb07c127d037f68e2a1f6ca6b5defee0fbadcebdb3ae23aedd4e7266f184a4fa`.

Expected frozen metadata:
- 1,296 unique blocks;
- 4,104 compatible SELF/CROSS pairs;
- 211,248 candidate instances across all four template families.

## Feasible support2 witness resource vector

For candidate blocks A/B and targets:

1. frame triples are `(R0,R1,R0*R1)` from the raw candidate block records;
2. shared `(S0,S1)` must be identical across the compatible pair and reproduce equal nonzero distinct R6I labels;
3. choose the minimum frame-extra central branch separately per block under `(t_c,t_nc)`;
4. block-A target order remains frozen;
5. block-B chooses the minimum Restore support over all six relative target permutations (independent of positive `t_r`);
6. exact resource vector:
   `r2=(U_c_extra,U_nc_extra,TagSupport,RestoreSupport)`;
7. exact cost `C2 = r2 dot (t_c,t_nc,t_tag,t_r)`.

This is only a feasible support2 member, not assumed cap2-optimal.

## Exact weighted cap1 referee

Enumerate the exact 12 ordered n=2 support1 anticommuting frame pairs per block.

For every candidate target pair:
- compute A Restore support for all 12 pairs;
- compute B minimum Restore support across all six target permutations for all 12 pairs;
- precompute exact minimum shared Tag **support units** for every 12x12 A/B frame-pair combination by enumerating all 16 two-qubit `S0` x 16 `S1` choices and requiring equal nonzero distinct labels;
- frame extra is zero for all support1 frames;
- score all 144 pair combinations exactly as `t_r*RestoreSupport + t_tag*TagSupport`.

Cache target-side vectors; cache keys are exact target triples, never objective scores.

Return both exact `C_cap1(theta)` and the selected support1 resource vector `r1=(0,0,TagSupport,RestoreSupport)`.

## Full scan / prospective selection

Scan **all 211,248 frozen candidates** once. For each objective:
- count strict `C2<C_cap1` witnesses;
- preserve the first strict witness in frozen candidate order;
- preserve the maximum-gap witness, tie-broken by candidate order;
- histogram by V5 template family and SELF/CROSS pair kind;
- record maximum exact gap `C_cap1-C2`.

O0 strict witness count must be exactly zero; otherwise parent/QG-16 binding fails.

## Affine witness analysis

For every first/max selected witness serialize integer vectors `r2,r1` and difference

`d = r2-r1 = (d_c,d_nc,d_tag,d_r)`.

The fixed-configuration cost difference is

`Delta(theta)=d_c*t_c+d_nc*t_nc+d_tag*t_tag+d_r*t_r`.

Normalize `d` by integer gcd and sign chosen so Delta(O0)>=0. Compare this normalized hyperplane against each normalized QG-16 facet vector from the protected parent.

- exact proportionality -> `QG16_FACET_AFFINE_MATCH`;
- otherwise -> `NEW_TRUE_PHASE_BOUNDARY_CANDIDATE`.

A finite witness proves support1 failure at its objective. Hyperplane proportionality is evidence of local facet sharpness for that witness family; it does NOT prove the complete global phase diagram.

## Independent generic ORION

For every selected positive witness:
- rebuild phase-free Pauli algebra independently;
- verify raw support2 frame/Tag acceptance;
- recompute `r2` and `C2`;
- re-enumerate the exact 12x12 weighted cap1 optimum and `r1`;
- verify strict gap and affine difference vector;
- verify any claimed QG-16 facet proportionality against the committed QG-16 parent facet list.

Generic ORION need not regenerate the full 211,248-candidate search; V5 generator identity and O0 zero-witness control are separately bound.

## Native ORION-Q

Responsibilities:
- `SUPPORT2_PHASE_WITNESS` when at least one outside objective has a verified strict gap;
- `NO_WITNESS_ON_FROZEN_V5_DOMAIN` otherwise;
- `PARENT_BINDING_GAP` / `GENERIC_DISAGREEMENT` fail closed.

Mandatory:
- `GLOBAL_PHASE_BOUNDARY_COMPLETE=false`;
- no outside objective is generalized beyond its exact coordinates;
- no physical quantum-advantage claim.

## Honest terminals

- `QG17_SUPPORT2_PHASE_WITNESS_FOUND_AT_FROZEN_OUTSIDE_OBJECTIVE`;
- annotation `QG17_QG16_FACET_LOCALLY_SHARP_BY_AFFINE_WITNESS` if at least one selected witness hyperplane exactly matches a parent facet;
- `QG17_NO_SUPPORT2_WITNESS_IN_FROZEN_V5_DOMAIN`;
- disagreement / CANNOT_CHECK terminals.

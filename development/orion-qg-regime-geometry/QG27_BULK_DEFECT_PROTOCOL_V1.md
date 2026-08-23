# ORION-QG QG-27 — bulk-defect law and thermodynamic cost density V1

Date: 2026-08-22
Issue: #886
Parent programme: #740
Execution branch: `codex/orion-qg-qg27-bulk-defect-20260822`
Direct parents:
- QG-23 protected auxiliary-support compactness
- QG-26 protected guarded histogram geometry
Status: **FROZEN BEFORE QG-27 MACHINE OUTCOME.**
Authority: compiler asymptotic/bulk theorem only; no physical thermodynamics, novelty, R6, finite-n phase-boundary, chain-closure, B''-completeness, or sharp-defect-constant authority.

## Frozen theorem candidate

For a valid fixed-matching target histogram `N in N^4096`, let

`B_min(N)=min_pi B_pi(N)`

over the eight QG-26 spectator baselines (four distinct vectors).

QG-26 gives an exact accepted-template representation with an optimum using at most six active auxiliary columns.

### Lower defect bound

For every feasible support-capped auxiliary configuration:
- all six frame Paulis are nonzero, hence each three-block frame structural term contributes at least `2+4=6`, total at least 18 before the frozen `-18` offset;
- the shared Tag has support at least one because identity Tag cannot produce distinct branch labels, hence Tag term at least 2;
- therefore the total structural term is at least 2.

At one active column, both spectator and auxiliary two-branch F3 values lie in `[0,6]`, so the local correction lies in `[-6,+6]`.

With at most six active columns,

`K_tau >= 2 - 6*6 = -34`.

Hence

`C_DP(N) >= B_min(N)-34`.

### Upper defect bound

Choose a permutation pi attaining `B_min(N)` and any target column type present in N. Put any one of the exact 48 feasible one-qubit shared-label frame/Tag rows on one occurrence and identity auxiliary letters everywhere else.

Its structural term is exactly 2, and the active F3 correction is at most +6. Thus

`C_DP(N) <= B_min(N)+8`.

Frozen all-n band:

`B_min(N)-34 <= C_DP(N) <= B_min(N)+8`.

The constants are universal but explicitly **not claimed sharp**.

## Thermodynamic density

For any valid sequence `N^(m)` with total qubit count `n_m -> infinity` and empirical frequencies `N_t^(m)/n_m -> p_t` componentwise,

`C_DP(N^(m))/n_m -> e(p) := min_pi sum_t p_t b_pi(t)`.

Thus all optimized Tag/frame structure is subextensive O(1), while the exact asymptotic density is a four-form bulk lower envelope.

## Pure scaling rays

For a valid integer motif histogram `h`, let `N(k)=k h`.

QG-26's finite guarded affine template theorem implies each template is either never feasible on the ray or eventually feasible, and when feasible has form

`k*B_pi(h)+K_tau`.

The finite lower envelope is therefore eventually exactly affine with period one:

`C_DP(kh)=k*s+q` for all sufficiently large k,

with slope

`s=B_min(h)`.

V1 authorizes existence and exact slope only. It does not compute the eventual threshold or intercept globally.

## Frozen bulk-slope controls

Codes use `I=0,X=1,Y=2,Z=3`. Baseline representatives are `000,001,010,011`.

1. Unary four-way tie:
   - motif: `XXXXXX = (1,1,1,1,1,1)`
   - expected slopes `(2,2,2,2)`.

2. Strict selectors, each a two-column motif `IIIIII + t`:
   - 000: `t=XYXYXY=(1,2,1,2,1,2)`, expected `(2,6,6,6)`;
   - 001: `t=XYXYYX=(1,2,1,2,2,1)`, expected `(6,2,6,6)`;
   - 010: `t=XYYXXY=(1,2,2,1,1,2)`, expected `(6,6,2,6)`;
   - 011: `t=XYYXYX=(1,2,2,1,2,1)`, expected `(6,6,6,2)`.

3. Two-way tie:
   - motif `IIIIII + XXXYXY`, second type `(1,1,1,2,1,2)`;
   - expected `(4,6,6,4)`, tie 000/011.

These controls test baseline slopes/ties only. They do not authorize a finite-size threshold/intercept claim.

## Complete local controls

Production and generic ORION independently reconstruct local Pauli/F3 algebra and verify:
- all 8×4096 spectator coefficients lie in `[0,6]` and attain both endpoints;
- over all 4096 target types and all `4^6` local frame-letter choices, the two-branch auxiliary F3 value lies in `[0,6]` and attains both endpoints;
- over that complete domain and all 8 permutations, `F3_aux-F3_spectator` has exact range `[-6,+6]`;
- all 48 feasible one-active shared-label rows have structural term exactly 2 for every central tuple;
- at least one such row exists independent of target type/permutation, making the +8 construction universally available.

The structural >=2 global inequality is separately derived from support/nonzero semantics and bound to QG-24/QG-26 production `config_cost` decomposition.

## Asymptotic phase geometry

Because QG-26 has four distinct baseline coefficient vectors, define four linear forms `beta_r(p)`. The frequency simplex admits a finite exact bulk-cell decomposition under

`e(p)=min_r beta_r(p)`.

QG-27 may authorize existence of this asymptotic count-space compiler phase geometry and the exact pairwise tie forms. It may not call these finite-n global or physical phase boundaries.

## Independent generic ORION

Must rebuild F2^2/F3 independently, reproduce the QG-26 four baseline hashes, derive the local extrema and defect constants independently, verify the frozen motif slopes/ties, and audit the finite-lower-envelope scaling-ray proof without importing production QG-27 code.

## Native ORION-Q

May authorize only:
- `BULK_DEFECT_UNIFORM_BOUND_ALL_N`
- `ASYMPTOTIC_COST_DENSITY_EXACT`
- `PURE_SCALING_RAY_EVENTUALLY_AFFINE`
- `ASYMPTOTIC_COUNT_SPACE_PHASE_GEOMETRY`

Mandatory false:
- `DEFECT_CONSTANTS_SHARP`
- `FINITE_N_GLOBAL_PHASE_BOUNDARY`
- `PHYSICAL_PHASE_TRANSITION`
- `CHAIN_ALL_N`
- `CLOSED_FORM_BDOUBLEPRIME_COMPLETENESS`
- novelty/R6/physical-advantage authority.

## Intended terminal

`QG27_TARE_BULK_DEFECT_LAW_AND_EXACT_ASYMPTOTIC_COST_DENSITY_ALL_N_MACHINE_CHECKED`

Honest alternatives: local-bound refutation, one-active construction gap, QG-26 binding gap, generic/native disagreement, CANNOT_CHECK.

## Donor subtraction

Thermodynamic-limit arguments, finite defect/boundary corrections, lower envelopes of affine functions and normal-fan geometry are established donor mathematics. Candidate contribution is only the exact TARE-specific bounded-defect law, bulk cost-density formula and period-one scaling-ray consequence.
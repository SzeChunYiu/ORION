# ORION-QG QG-29 — six-count defect saturation and universal k<=43 affine crossover V1

Date: 2026-08-22
Issue: #890
Parent programme: #740
Execution branch: `codex/orion-qg-qg29-defect-saturation-20260822`
Direct parents:
- QG-26 protected finite guarded histogram-template theorem
- QG-27 protected bulk-defect theorem
Optional control only: QG-28 protected 715-orbit quotient
Status: **FROZEN BEFORE QG-29 MACHINE OUTCOME.**
Authority: exact finite-size compiler theorem only; no sharpness-for-real-TARE, explicit forecaster, finite-n global phase-boundary, chain/B'' completeness, novelty, R6 or physical-advantage authority.

## Scientific question

QG-26 writes the exact fixed-matching optimum as

`C_DP(N)=min_{tau feasible on N}[B_{r(tau)}(N)+K_tau]`,

where every template uses at most six active target-column occurrences and has only multiplicity guards `N_t>=m_tau(t)`. QG-27 proves four distinct bulk forms and a universal defect band sufficient to place the optimal bulk-class defect potentials in the integer interval `[-34,8]`.

What exact finite-size saturation follows before any explicit template basis is enumerated?

## P1 — four bulk-class defect potentials

For each distinct QG-26/QG-27 bulk form `r in {0,1,2,3}`, define

`kappa_r(N)=min{K_tau : tau has bulk form r and G_tau(N)}`.

QG-26's one-active construction exists for every valid histogram and every target-permutation/bulk form, so each `kappa_r(N)` is finite and `<=8`. Every feasible template has `K_tau>=-34` by QG-27, so

`kappa_r(N) in Z intersect [-34,8]`.

Thus each defect potential has exactly 43 possible integer levels available under the universal bound calculus.

Exact cost is

`C_DP(N)=min_r [B_r(N)+kappa_r(N)]`.

## P2 — coordinatewise monotonicity

If `N' >= N` coordinatewise, every template feasible at N remains feasible at N'. Therefore

`kappa_r(N') <= kappa_r(N)`.

This monotonicity is about the defect potential only. The total exact cost generally increases with N because the bulk term grows.

## P3 — clip-at-six sufficient statistic for the defect potential

Every active template contains at most six occurrences total. Hence for every target type t,

`0 <= m_tau(t) <= 6`.

Define

`clip6(N)_t=min(N_t,6)`.

For every template tau,

`G_tau(N) iff G_tau(clip6(N))`.

Therefore the complete feasible-template set for every bulk class is unchanged and

`kappa_r(N)=kappa_r(clip6(N))`.

Counts above six affect only the extensive linear bulk forms, never which defect templates are available.

## P4 — bounded defect-level changes

Along any coordinatewise nondecreasing histogram path, each integer `kappa_r` is monotone nonincreasing and lies in the 43-level interval `[-34,8]`. Hence each bulk-class defect potential can strictly decrease at most **42 times**.

This does not bound the total number of winning-template identity changes within a level or the total exact-regime switches caused by competition among different bulk slopes.

## P5 — pure scaling-ray guard saturation by k=6

Fix any valid nonzero integer motif histogram h and let `N(k)=k h` for integer `k>=1`.

If `h_t=0`, type t is absent forever. If `h_t>0`, then `k h_t>=6` for every `k>=6`.

Since every guard threshold is at most six, every template is either:
- never feasible on the ray; or
- feasible for every `k>=6`.

Thus for each bulk class r there is a stabilized integer intercept `kappa_r^*(h)` such that

`kappa_r(kh)=kappa_r^*(h)` for every `k>=6`.

## P6 — universal affine onset by k=43

For `k>=6`,

`C_DP(kh)=min_r [k*b_r(h)+kappa_r^*(h)]`,

where all bulk slopes `b_r(h)=B_r(h)` are integers and each stabilized intercept lies in `[-34,8]`.

Let `b_min=min_r b_r(h)`. Any strictly worse bulk slope has integer gap at least 1. Its maximum possible intercept advantage over a minimal-slope line is 42. Therefore for every `k>=43`,

`k*(b_r-b_min)+(kappa_r^*-kappa_min^*) >= 43-42 > 0`.

No strictly worse bulk slope can be optimal at or beyond k=43. Among minimal-slope forms, the smallest stabilized intercept wins or ties forever.

Hence for every valid motif h there exists an exact integer `q_h` such that

`C_DP(kh)=k*B_min(h)+q_h`

for every integer `k>=43`.

This strengthens QG-27's unbounded eventual-affinity result to a universal grammar-level onset bound.

## P7 — abstract bound-calculus tightness control

The value 43 is not claimed sharp for real TARE. However the abstract interval/slope-gap argument itself must be tight at its stated information level.

Machine-enumerate all four-line abstract systems with:
- one normalized minimum slope 0;
- other integer slope gaps in `{0,1,2,3,4,5,6}`;
- integer intercepts in `[-34,8]`;
- at least one zero-gap line.

It is sufficient to quotient common intercept shifts and line permutations, but the enumerated domain and symmetry reduction must be explicit.

Require:
- at k=43 every line with positive slope gap is strictly above the best zero-gap line for every abstract system;
- k=42 is not universally sufficient, with an explicit tight abstract witness such as two lines `(slope,intercept)=(0,8)` and `(1,-34)`, tied at k=42.

This witness proves only sharpness of the **derived universal bound calculus**, not realization by an actual TARE motif.

## P8 — parent bindings

Bind QG-26:
- terminal GREEN;
- finite guarded template representation true;
- max active coordinates/occurrences =6;
- guards are multiplicity thresholds `N_t>=m_tau(t)`;
- one-active accepted construction exists for every target type/permutation as established by its exhaustive controls.

Bind QG-27:
- terminal GREEN;
- defect interval `[-34,8]`;
- exactly four bulk forms;
- all costs/resource constants integral;
- QG-27 scaling slopes are exact integer baseline sums.

QG-28 may be bound as an optional control showing the same count clipping can later be transported to 715 orbit counts, but QG-29 V1 authority must not depend on it.

## Independent generic ORION

Generic ORION must derive clip6 equivalence, monotonicity, the 42-drop bound and k=43 line-dominance argument independently from serialized QG-26/QG-27 parent facts. It must independently execute the abstract tightness control and not import production QG-29 code.

## Native ORION-Q

May authorize only:
- `DEFECT_POTENTIAL_CLIP6_SUFFICIENT`
- `DEFECT_LEVEL_CHANGES_AT_MOST_42_PER_BULK_CLASS`
- `PURE_SCALING_RAY_DEFECTS_STABLE_BY_K6`
- `PURE_SCALING_RAY_AFFINE_BY_K43`

Mandatory false:
- `K43_SHARP_FOR_REAL_TARE`
- `EXPLICIT_Q_H_FORECASTER`
- `FINITE_N_GLOBAL_PHASE_BOUNDARY`
- `CHAIN_ALL_N`
- `CLOSED_FORM_BDOUBLEPRIME_COMPLETENESS`
- novelty/R6/physical-advantage authority.

## Intended terminal

`QG29_TARE_DEFECTS_CLIP_AT_6_AND_ALL_SCALING_RAYS_AFFINE_BY_K43_MACHINE_CHECKED`

Honest alternatives:
- `QG29_GUARD_THRESHOLD_PREMISE_REFUTED`
- `QG29_DEFECT_BAND_BINDING_GAP`
- `QG29_ABSTRACT_CROSSOVER_ARITHMETIC_REFUTED`
- `QG29_GENERIC_NATIVE_DISAGREEMENT`
- `QG29_CANNOT_CHECK`

## Donor subtraction

Monotone threshold systems, finite-size scaling and affine-envelope arguments are established donor mathematics. Candidate contribution is only the exact TARE-specific clip-at-six defect theorem and universal k<=43 affine-onset bound.
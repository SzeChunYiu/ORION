# QG-21 — certified regime robustness protocol V1

Date: 2026-08-22
Issue: #864
Parent programme: #740
Direct parents: QG-8, QG-16, frozen QG-17; later interfaces QG-10/QG-11/QG-14
Branch: `codex/orion-qg-wave3-frontier-20260822`
Status: **FROZEN BEFORE ANY QG-21 MARGIN, UNCERTAINTY-CONTAINMENT, TRUE-BOUNDARY BRACKET, OR STACK-TRANSFER OUTCOME.**
Authority ceiling: certificate robustness/sensitivity evidence for frozen compiler theorems only; no novelty, R6, or physical-advantage authority.

## 1. Question and non-negotiable distinction

For an ORION-QG theorem that is valid on a certified objective region `K`, how far may objective coefficients or downstream stack parameters move before the theorem's authority must stop?

QG-21 distinguishes:

- **certificate margin**: distance to the boundary of the currently proved sufficient region;
- **true phase margin**: distance to an actual globally optimal regime change.

A certificate cone may be conservative. `rho_certificate` may never be relabeled `rho_true` without a separate exact sharpness/completeness result.

Robust optimization, parametric sensitivity, polyhedral distance, interval analysis, dual norms and uncertainty propagation are donor mathematics.

## 2. Frozen calibration parents

The first execution is limited to already-earned structural theorem regions.

### K8 — QG-8 R6M support<=2 certificate

Use the protected mechanically derived cone, not handwritten re-entry, and independently verify its exact facet representation before margin calculations. Expected human-readable inequalities are the earned QG-8 forms:

`t_c >= 2*t_r`

`t_nc >= 2*t_r`

with any parent coefficient-domain assumptions preserved exactly.

### K16 — QG-16 R6I support1 certificate

Use the full protected four-facet certificate unless a reduction is accompanied by the exact ordering premise that makes facets redundant:

`t_c + t_nc >= 5*t_r`

`2*t_nc >= 5*t_r`

`t_c + t_nc >= 2*t_r + 2*t_tag`

`2*t_nc >= 2*t_r + 2*t_tag`.

Do not silently impose `t_c<=t_nc`.

### Frozen QG-16 point controls

Evaluate exact slacks at:
- `O0=(t_nc,t_c,t_tag,t_r)=(4,2,2,1)`;
- `O_in=(5,3,2,1)`;
- `O_tag_out=(4,2,5/2,1)`;
- `O_restore_out=(4,2,2,5/4)`;
- `O_nc_out=(3/2,3/2,1,1)`.

The first execution may not add points after seeing margin results.

## 3. Gauge / scale convention

Linear objective coefficients are homogeneous under positive common scaling, so a distance is undefined/misleading until a gauge is declared.

Freeze two reporting views:

### G1 — structural slice

Set `t_r=1` for QG-8/QG-16 calibration when `t_r>0`. Report rational facet slacks and directional distances in the remaining coordinates.

### G2 — normalized coefficient simplex

For scale-free comparison, restrict nonnegative coefficients to

`sum_i t_i = 1`.

Use only exact rational polyhedral calculations for certification. Euclidean distances requiring square roots may be represented symbolically or as rigorously enclosed intervals; they are secondary.

No conclusion may mix distances from G1 and G2 without an explicit map.

## 4. Primary exact robustness metric

Represent a certified region as rational inequalities

`K = {theta : a_i·theta >= b_i, i=1..m}`

within the frozen gauge domain.

For a point theta0, primary machine object is the **facet slack vector**

`s_i(theta0)=a_i·theta0-b_i`.

This is exact rational data and avoids norm ambiguity.

Secondary declared-norm radius:

`rho_cert(theta0)=min_i s_i/||a_i||_*`

only over facets reachable within the frozen gauge/domain. State the norm and dual norm explicitly.

Required controls:
- any point on a certificate facet has zero radius exactly;
- outside points are `CERTIFICATE_NOT_APPLICABLE`, not negative-radius regime claims;
- strict interior points have positive minimum slack.

## 5. Uncertainty-set containment

Freeze uncertainty families before calculations.

### U1 — axis-aligned rational box

Around each inside calibration point theta0 use relative/absolute rational perturbation radii from fixed set:

`eps in {0, 1/20, 1/10, 1/5}`

applied only to nonnegative coefficient coordinates and clipped by the frozen gauge domain. This set/order is frozen before any containment result.

### U2 — rational directional segment

For each retained facet normal and selected scientifically meaningful coefficient direction, use a line segment with rational endpoints spanning toward/through the certificate boundary.

### U3 — simplex/polytope control

Use the convex hull of the inside controls and declared facet-equality controls where type-correct.

A theorem is robustly valid on uncertainty set Theta iff exact optimization proves

`min_{theta in Theta} (a_i·theta-b_i) >= 0`

for every certificate facet.

For boxes use exact endpoint/worst-sign evaluation. For rational polytopes use an exact rational LP/vertex certificate or independently checked rational witness. No nominal-point shortcut.

Outputs:
- per-facet worst slack;
- worst-case theta witness;
- `Theta subseteq K` boolean;
- maximal expansion within the frozen uncertainty family, reported exactly/bracketed if necessary.

## 6. QG-17 true-boundary bracket interface

QG-17 is a frozen independent parent and has no QG-21 outcome authority until its own result is sealed.

After QG-17 produces verified strict support2-vs-cap1 witnesses, QG-21 may import only their serialized resource vectors/objective coordinates and recompute independently:

`Delta(theta)=(r2-r1)·theta`.

A witness tie hyperplane `Delta=0` provides a **candidate/witness-side transition surface**. Along a frozen line/slice:

- a theorem-certified support1 interval supplies one side;
- a verified strict cap1 failure supplies the other side;
- together they bound the location of at least one true phase transition if continuity/piecewise-linear assumptions are type-correct for the finite optimization envelope.

Allowed labels:
- `TRUE_PHASE_BRACKET`
- `CERTIFICATE_FACET_AFFINE_MATCH`
- `BRACKET_COLLAPSES_TO_EXACT_BOUNDARY` only if both sides mathematically coincide and no intervening competing regime remains possible under a separate completeness argument.

A finite witness hyperplane alone is never a complete global phase diagram.

## 7. Anisotropic robustness profile

For every reported point/set also serialize:
- full facet slack vector;
- active/nearest certificate facets;
- directional boundary distance along each frozen direction;
- whether multiple facets become active simultaneously;
- certificate label under small positive/negative rational moves along each direction.

This profile is primary over a single scalar radius when geometry is anisotropic.

## 8. FT/QEC transfer — successor stage only

Only after structural calibration passes may a successor execution bind a QG-11-style downstream map.

For an exact affine cell:

`r_F=A r_S+b`, `objective=lambda·r_F`, hence `theta=A^T lambda`.

Freeze exact rational/interval uncertainty in A and/or lambda and derive a certified enclosure `Theta_S` for theta. Structural theorem transfer is authorized only if

`Theta_S subseteq K_structural`.

If the downstream map is piecewise-affine, split by independently verified cell predicates. If it is nonseparable/witness-dependent due to routing, scheduling, code distance, integer factories or congestion, either enrich the state/map under a new freeze or return:

`QG21_STACK_NONLINEARITY_BREAKS_SINGLE_RADIUS`.

Estimator samples cannot substitute for a map theorem.

## 9. Compositional robustness — successor stage only

For a QG-14 component certificate export:
- certificate region `K_i`;
- current uncertainty set `Theta_i`;
- per-facet margins;
- latent coupling coordinates;
- dependency/reopen edges.

Strictly separable components may compose their validity domains through the exact parameter map. Under shared budgets/couplings, a global robust region must be recomputed; `min_i rho_i` is not automatically valid.

Hostile control: construct a case where every local component remains within its own positive margin but a shared coupling flips the global optimum. If found, preserve it as a missing-coupling result rather than weakening the global gate.

## 10. Prospective drift forecast

After structural calibration and, where used, QG-17 witness binding, freeze one trajectory before revealing the exact optimizer/estimator along it.

First structural trajectory family:
- start at QG-16 `O0` and `O_in`;
- vary exactly one ratio/direction among `t_tag`, `t_r`, `t_nc`, `t_c` according to a predeclared rational grid crossing a known certificate facet;
- predict the last point with theorem authority from the certificate alone;
- if witness-side evidence exists, predict a bracket for the first true support-regime change.

Primary safety metric: **false authority continuation count must be zero**. Conservative cessation at a certificate boundary is correct even if the true phase continues farther.

## 11. Independent verification

### Generic ORION

Must independently:
- reconstruct parent facet inequalities from protected machine receipts or re-derived resource domains;
- canonicalize rational half-spaces;
- compute all point slacks and uncertainty worst cases;
- verify all rational LP/vertex certificates;
- recompute QG-17 tie hyperplanes from primitive resource vectors if/when imported;
- reconstruct downstream affine pullbacks/enclosures when successor stages run.

### Native ORION-Q

Keep separate authority states:
- `CERTIFICATE_MARGIN`
- `UNCERTAINTY_CONTAINMENT`
- `TRUE_PHASE_BRACKET`
- `TRUE_PHASE_BOUNDARY`
- `FT_TRANSFER_MARGIN`
- `COMPOSITION_MARGIN`
- `STACK_NONLINEARITY`
- `CANNOT_CHECK`

`CERTIFICATE_MARGIN` must never imply `TRUE_PHASE_BOUNDARY`.

## 12. Honest terminals

Positive candidates:
- `QG21_CERTIFIED_REGIME_ROBUSTNESS_RADIUS_MACHINE_CHECKED`
- `QG21_UNCERTAINTY_POLYTOPE_FULLY_COVERED_BY_REGIME_CERTIFICATE`
- `QG21_CERTIFICATE_AND_WITNESS_BRACKET_TRUE_PHASE_ON_FROZEN_SLICE`
- `QG21_CERTIFICATE_MARGIN_MATCHES_TRUE_BOUNDARY_ON_FROZEN_SLICE`
- `QG21_HARDWARE_UNCERTAINTY_SET_COVERED_BY_TRANSFERRED_CERTIFICATE`

Negative/partial:
- `QG21_CERTIFICATE_MARGIN_LOOSE__TRUE_BOUNDARY_UNRESOLVED`
- `QG21_STACK_NONLINEARITY_BREAKS_SINGLE_RADIUS`
- `QG21_LOCAL_MARGINS_FAIL_UNDER_HIDDEN_COMPOSITION_COUPLING`
- `QG21_PARENT_FACET_RECONSTRUCTION_MISMATCH`
- `QG21_PARTIAL__<obligation>_OPEN`
- `QG21_CANNOT_CHECK`

## 13. Donor and claim boundary

Robust optimization, sensitivity analysis, polyhedral geometry, norm duality, parametric programming, interval uncertainty, affine resource propagation and critical-region analysis are donor mathematics/methods. Candidate contribution is only the proof-carrying frozen compiler theorem persistence/bracketing/transfer result. No physical quantum advantage follows. The protected stretched-N2 subject is excluded.

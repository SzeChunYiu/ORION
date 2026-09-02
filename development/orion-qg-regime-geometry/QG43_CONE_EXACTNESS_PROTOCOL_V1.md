# QG43 — Cone exactness: exhaustive n=1 support-2 region vs the QG8 cone (V1)

> **Provenance (registration note).** This study was first registered as
> "QG22" in (closed) PR #2153. The repo's QG-22 slot is already occupied by
> the hidden-home-state study (globs `QG22_*` / `qg22_*` in
> `.github/workflows/orion-qg-qg22-hidden-home-state.yml`), so the number is
> reissued as QG-43. Machinery, grid, panels, gates, terminals, and seeds are
> byte-identical modulo the identifier rename (`QG22`->`QG43`, `Q22G`->`Q43G`);
> the registered outcome is regenerated deterministically from this fresh
> registration. The original registration commits (3ba2e0aef, 1c59a2023) stay
> visible on the closed PR.

## Aim

QG8 proved (all-n, machine-checked) that the cone `t_c >= 2*t_r AND t_nc >= 2*t_r`
implies support `<= 2` for every instance, and left `global_boundary_sharpness`
OPEN. QG19 probed ONE outside objective (`O19`, margins `(t_c-2t_r, t_nc-2t_r) =
(-1, 0)`) on a 53-row frozen panel and found ZERO support-3 gap witnesses —
ambiguous between "panel poverty" and "the exact support-2 region strictly
contains the cone". This study removes the ambiguity at n=1 by EXHAUSTIVE
instance enumeration, and maps the witness frontier on a margin grid.

## Definitions (frozen machinery, no new semantics)

For an instance `I` (3 branch-pairs of nonzero `(x,z)` targets at width `n`)
and integer objective `O = (t_nc, t_c, t_tag, t_r, rho)` with `t_c <= t_nc`:

- `C_DP(I,O) = qg2.dp_cost_pairs_ob` — exact unrestricted optimum (parity DP).
- `C_Dxx(I,O) = qg2.dxx_cost_ob` — exact support-`<=2` (D++) family optimum.
- `gap(I,O) = C_DP(I,O) - C_Dxx(I,O) <= 0`; `I` is a **support-3 witness at
  O** iff `gap(I,O) < 0` (and the serialized DP witness must then have
  `max_frame_support > 2`).
- Exact support-2 region at width n: `R_n = {O : gap(I,O) = 0 for ALL I}`.
- Cone `C = {t_c >= 2*t_r, t_nc >= 2*t_r}`. QG8: `C ⊆ R_n` for all n.

## Registered outcome run (single pass, exit 0 = complete)

1. **Objective grid** (rho = 0 throughout; `dc = t_c - 2*t_r`,
   `dnc = t_nc - 2*t_r`; every objective keeps `t_c >= 1`, `t_nc >= 1`,
   `t_c <= t_nc` — margins are truncated at the valid-objective boundary):
   - `G_main` = Slice A (t_r=2, t_tag=2): all `(dc,dnc) ∈ {-3..2}²` with
     `dc <= dnc` (`t_c = 4+dc`, `t_nc = 4+dnc`) → 15 objectives, covering
     outside points (`dc < 0`), the cone boundary (`dc = 0` or `dnc = 0`),
     and strictly-inside controls `(1,1)`, `(1,2)`, `(2,2)`.
   - Slice B (t_r=3, t_tag=2): `dc ∈ {-5..0} × dnc ∈ {0,1}`
     (`t_c = 6+dc`, `t_nc = 6+dnc`) → 13 deep-central-margin objectives;
     `dc = -5` matches O1's central margin.
   - `O1ANCHOR`: the exact frozen QG2 objective O1 = (t_nc,t_c,t_tag,t_r,rho)
     = (7,1,4,3,0), margins `(-5,+1)` → 1 objective.
   - `G_tag` (t_r=2, dnc=0): `t_tag ∈ {0,4}` on `dc ∈ {(-3,-2,-1)}` → 6.
   - `G_scale` (t_tag=2): `t_r = 1` at `(dc,dnc) = (-1,0)` (`t_c=1,t_nc=2`)
     → 1 margin-plane scale-probe objective, giving `(dc,dnc)=(-1,0)` at
     `t_r ∈ {1,2,3}` (t_r=3 via Slice B), plus exact integer rays:
     `λ ∈ {2,3}` times the deterministic base `O_base` = the witness-bearing
     `G_main` point first in `(-(witness count), dc, dnc)` order → 2 more
     (evaluated only on `O_base`'s serialized witnesses).
   Total: 36 registered grid objectives.
2. **Instance panels**:
   - `P1` EXHAUSTIVE n=1: all 729 ordered instances (6 targets from
     `{X=(1,0), Y=(1,1), Z=(0,1)}`) × every grid objective.
   - `P2` hostile: the frozen `r6m._HOSTILE_N1_PANELS` (3) and
     `_HOSTILE_N2_PANELS` (2) × every grid objective.
   - `P3` witness continuation: the QG2 `NEW_SUPPORT3` O1 rows (gap −2 at
     margins `(-5,+1)`) re-evaluated on every grid objective.
   - `P4` discovery (seed 20260824, `numpy.default_rng`): 60 random n=2 + 40
     random n=3 instances (6 nonzero `(x,z)` targets each, exactly as QG19's
     generator) × the 15 `G_main` objectives only.
3. **Registered questions** (authored before the run):
   - **Q1 (primary):** does there exist a grid objective OUTSIDE the cone with
     `gap = 0` on ALL of P1? Prediction: YES (exhaustive upgrade of QG19's
     panel-zero at `(-1,0)`).
   - **Q2 (frontier):** which outside grid points admit >= 1 witness anywhere
     in P1∪P2∪P3∪P4; report `min |dc|` among witness-bearing points.
   - **Q3 (homogeneity):** (a) exact-ray check: `gap(λ·O_base) = λ·gap(O_base)`
     for every serialized witness instance of `O_base`, `λ ∈ {2,3}` (theory:
     both optima are minima of integer-linear forms with shared constants, so
     positive integer scaling commutes with the min — this certifies the
     machinery's arithmetic, not new geometry); (b) margin-plane scale probe:
     report whether witness existence at fixed `(dc,dnc)` changes between
     `t_r ∈ {1,2,3}` on the probed slice.
   - **Q4 (tag):** does witness existence at a fixed margin change with
     `t_tag ∈ {0,2,4}` on `G_tag`?
4. **Gates (hard):**
   - `G1`: `C_DP <= C_Dxx` on every evaluation (assert, abort on violation).
   - `G2`: every strictly-inside grid objective (`dc > 0 AND dnc > 0`:
     `(1,1)`, `(1,2)`, `(2,2)`) has zero gaps on all of P1 (consistency
     with the all-n QG8 theorem).
   - `G3`: every serialized witness row has `max_frame_support > 2`.
   - `G4`: independent n=1 brute cross-check (full config enumeration via
     `qg2.brute_config_n1_ob`) at two objectives — the most witness-bearing
     grid point and the first zero-gap outside point in `(dc, dnc)` order —
     on 12 fixed P1 instances plus every n=1 witness found.
   - `G5`: anti-instrument import gate (as QG19).
   - `G6`: O1-anchor replay — every frozen QG2 O1 witness instance must
     reproduce exactly `C_DP = 11`, `C_Dxx = 13` (gap −2) at `O1ANCHOR`,
     binding this study's machinery to the frozen QG2 receipt.
5. **Artifacts:** `QG43_CONE_EXACTNESS_RESULTS.json` (schema
   `ORION.QG.QG43.ConeExactness.v1`: grid, per-objective aggregates
   `{n_eval, n_gaps, n_gaps_p1, min_gap}`, witness rows capped at 20,
   `q1_outside_zero_gap_objectives`, `q2_frontier_witness_objectives`,
   `q2_min_abs_dc_witness`, `q3_ray_check`, `q3b_scale_probe`,
   `o1_anchor_replay_rows`, `g4_brute_report`, gate verdicts),
   `RUN_QG43.log`.

## Terminals

- `QG43_REGION_STRICTLY_CONTAINS_CONE_AT_N1` — Q1 YES (exit 0): the cone is
  NOT the exact support-2 region at n=1 on the grid; R_1 ∩ grid ⊋ C ∩ grid.
- `QG43_CONE_EXACT_ON_GRID_AT_N1` — Q1 NO (exit 0): every outside grid point
  has an n=1 witness; finite-n evidence FOR cone = region.
- `QG43_CONSISTENCY_FAILURE` — G1/G2/G3/G4/G5 violated (exit 3, no claims).

## Discipline & authority

No fitted parameters; every number is an exact integer from the frozen
`qg2_objective_robustness` machinery (imported, not copied). Each grid
objective gets a unique `Objective.name` (the machinery caches by name).
`clear_caches()` between objectives only (keyed correctly by name).
Authority: EXACT, EXHAUSTIVE IN INSTANCES at n=1, GRID-ONLY in objective
space; NO all-n sharpness claim, NOT R6. All-n statements remain QG8's.

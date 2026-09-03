# QG47 empty-frontier attribution (V1) — 2026-09-03

Lane: negative-revival attribution (task #28). Input: the certified QG47 outcome
(terminal `QG47_N2_FRONTIER_EMPTY`, digest `67c73bf9db92d272a7ab88f60f8aef3e74b53fd12ffabf62b05b160abd6769db`).
This document is ANALYSIS of a certified result — it carries no new authority and
amends nothing; per lab discipline the negative is treated as a lead, the failure
is attributed to exactly one stage, and a falsifiable revival test is designed.

## 1. Verdict (one-stage attribution)

**The population collapses to zero at the witness predicate inside instance
evaluation (`gap < 0` in `run_chunk`) — before any frontier gate receives a
single object.** All 68,343,750 evaluations executed; the predicate fired 0
times; 0 witness objects were ever constructed. Every merge gate is green and
`problems == []`: no gate rejected anything, so no rejection reason strings
exist. The emptiness is not a gating artifact and not a scarcity — it is a
**structural identity**: `C_DP == C_Dxx` exactly, for every n=2 instance, at
every one of the 6 frozen objective cells (gap support over the whole sweep is
the point mass `{0: 68,343,750}`). Near-miss depth (protocol Q2) is uniformly
0: there is no gradient toward a witness anywhere in the space. Mechanistically:
the support<=2 D++ comparator family is already **exact** at n=2 — the cap never
binds, so no instance exists whose optimum needs what the capped family cannot do.

## 2. Data and verification (all 1,350 parts, programmatically)

Loaded `QG47_PARTS/part_00000..01349.json`; independently recomputed every part
content digest (1350/1350 match), task-id coverage (exactly 0..1349, unique),
`completions == 15^4 == 50,625` per part, letters sha uniformity
(`ea37cd453faea988a762811a504f50ba10cdb76c9ccb99810cb86bad3b64e4c2`), and
internal histogram self-consistency (histogram sums, `min_gap == min key`,
`witness_count == mass at gap<0`, sample lengths): 0 defects. Per-objective
totals re-derived from parts match the certified merged receipt exactly.
Additionally, 30 probe slices spanning all 6 objectives were re-evaluated
through the frozen engine (`qg47_n2_full_sweep.eval_gap` → `qg2`) on this
machine: 30/30 reproduce `gap = 0` (merge's own recheck: 6,750/6,750, 0 failures).

## 3. Stage tallies

| # | Stage (engine construct) | Population in | Population out |
|---|-------------|--------------:|---------------:|
| S0 | Tasks decomposed (objective, prefix pair) | 1,350 | 1,350 parts written |
| S1 | Part integrity (digest, coverage, letters sha, 5 probes/part) | 1,350 | 1,350 (0 problems) |
| S2 | Instance evaluations (`eval_gap`, G1 assert live) | 68,343,750 | 68,343,750 (0 G1 trips) |
| S3 | **Witness predicate `gap < 0`** | 68,343,750 | **0** (0/1,350 tasks; 0 truncated samples) |
| S4 | Witness serialization (`witness_sample`) | 0 | 0 entries |
| S5 | Frontier aggregation (`q1_frontier`, unique instances) | 0 | 0 objects enter any gate |
| S6 | Merge gates (7 booleans + G4 + G5 + G6) | 0 candidates | 0 rejections; all gates green |
| S7 | Final frontier | — | 0 → `QG47_N2_FRONTIER_EMPTY` |

Campaign cost: 2,283,419 core-seconds = 634.3 core-hours, 29.9 evals/s/core
realized (protocol estimate 36.2). The binding constraint at S3 is the strict
inequality itself; since the entire mass sits AT 0, no threshold relaxation
short of `gap <= -1` — i.e. no legitimate one — could change the outcome.

## 4. Cross-tabs (conditioned analysis: emptiness is uniform, not slice-driven)

Gap-value support across ALL evaluations: `{0: 68,343,750}`. Every cross-tab is
therefore constant; the counts below prove the uniformity rather than exhibit a
slice. (Axis note: the sweep's pair axis is 225 = 15x15 ordered prefixes — 120
classes under (i,j)~(j,i). A "90" axis does not exist in the decomposition; 90
is only objectives x letters.)

Per objective (each: 11,390,625 = 15^6 instances, 0 witnesses, min_gap 0):

| objective | class | instances | witnesses | min_gap | wall (core-h) |
|---|---|---:|---:|---:|---:|
| Q45G_tr2_dc-2_dnc0_tag2 | lift | 11,390,625 | 0 | 0 | 105.8 |
| Q45G_tr2_dc-2_dnc1_tag2 | lift | 11,390,625 | 0 | 0 | 101.8 |
| Q45G_tr2_dc-3_dnc0_tag2 | home | 11,390,625 | 0 | 0 | 105.3 |
| Q45G_tr2_dc-3_dnc1_tag2 | home | 11,390,625 | 0 | 0 | 104.9 |
| Q45G_tr3_dc-3_dnc0_tag2 | lift | 11,390,625 | 0 | 0 | 106.6 |
| Q45G_tr3_dc-3_dnc1_tag2 | lift | 11,390,625 | 0 | 0 | 109.8 |

Per letter (15): each letter appears in 9,112,500 evaluations as a prefix member
(2 positions x 15 partners x 50,625 completions x 6 objectives) — witnesses 0,
min_gap 0, for all 15 masks (x,z). No letter class (X-type, Z-type, mixed,
weight-2) deviates.

Per ordered prefix pair (225): 303,750 instances each (50,625 x 6 objectives),
6 parts each; witnesses 0 in all 225 cells (and all 120 swap-reduced classes);
the 15x15 per-pair min_gap matrix is identically 0.

Per cell class: lift 0, home 0 (4 lift cells, 2 home cells).

## 5. Frozen coordinates and the revival lever

Coordinates frozen by engine + protocol (`qg47_n2_full_sweep.py`, PR #2167):

1. `n = 2` (`N_BITS`); authority `...N2...EXACT__NO_ALL_N_CLAIM__NOT_R6` — n>=3 untouched.
2. Alphabet: all 15 masks (x,z) in {0..3}^2 \ {(0,0)}, canonical sorted order.
3. Instance shape: 6 target letters = 3 ordered pairs (matching (0,1),(2,3),(4,5)).
4. Objective grid: the 6 QG45/QG46 cells loaded verbatim from the QG46 receipt
   (t_c 1–3, t_nc 4–7, t_r 2–3; all rho=0 — and rho cancels algebraically in the
   gap: `family_charge` is added to BOTH machines).
5. Comparator pair: `C_DP` (`dp_cost_pairs_ob`, unrestricted parity DP over
   2x2 branch perms x 8 centrals) vs `C_Dxx` (`dxx_cost_ob`, D++ support-capped
   family, cap 2 = weight-2 frame donor closure, `r6p._tables(n, 2)`).
6. Predicate: exact integer `gap = C_DP - C_Dxx < 0`; G1 hard-asserts `<= 0`.
   No budget multiplier exists anywhere in the QG43–QG47 machinery (grep-verified
   with a control match): "1.01x" is not a coordinate of this engine.
7. Gates: G1 (per-eval assert), G4 (12-sextuple n=1 brute cross-check, exact),
   G5 (AST anti-instrument import), G6 (QG45+QG46 receipt binding, 3,804
   round-trip evals), plus 7 merge booleans. (No G2/G3 in QG47's gate set.)

**The one legitimate lever is the dimension n -> 3.** Grounds, mechanics first:

- The frontier's only known inhabitants are n=3: QG45 `witness8`
  (targets [[3,7],[5,0],[2,4],[0,2],[5,4],[7,1]]) has gap **−2 at all 6 cells**
  of this same frozen grid, with a 7-of-35 single-bit-flip witnessing kernel;
  QG46's two-bit closure stays `KERNEL_PARTIAL`. The supporting mechanism — an
  optimal solution needing support >= 3 — plausibly requires >= 3 positions,
  which is consistent with the exhaustive ladder n=1 zero (QG43), n=2 zero +
  identity (QG47), n=3 >= 1 known witness.
- The authority string itself fences n>=3 out of QG47's claim, so an n=3 move is
  a NEW registration, not an amendment — exactly the sanctioned revival shape.
- Rejected alternatives, with reasons: grid weights (6 diverse cells all give the
  identical-zero histogram — no weight-response to exploit; searching weights
  until a gap opens is outcome tuning with no optimization-justified basis);
  alphabet (already exhaustive at n=2 — nothing left inside n=2); instance shape
  (witness8 has the SAME 3-pair shape and witnesses — shape is not the blocker);
  support cap (raising the cap only shrinks the frontier; lowering it to 1
  manufactures witnesses by weakening the comparator — tuning, not mechanics);
  rho (cancels in the gap).

## 6. Falsifiable revival test (LUNARC-sized, waves of 250)

New registration (successor, e.g. `QG48_N3_FRONTIER_PROSPECTION_V1`), same
frozen machinery/grid/gates; authority must state n=3, sampling-bounded, no
all-n claim (63^6 = 62.5e9 per objective is ~5,486x the n=2 space — exhaustive
is out of reach; ~580k core-hours per objective at the realized rate).

- **R1 (exact slice, cheap)**: three-bit-flip closure of the witness8 kernel —
  C(36,3) = 7,140 target rows x 6 objectives = 42,840 evaluations (~0.4 core-h),
  extending QG46's depth-2 anatomy to depth 3 exactly.
- **R2 (stratified seeded sampling)**: uniform over the full 63-letter n=3
  alphabet, 6 letters per instance, 3-pair shape, all 6 cells; registered PRNG
  seed; 1,350 tasks x 25,000 instances = 33.75M evaluations, run as 6 waves of
  250 (last 100) via the campaign script pattern. Budget ~= 630 core-hours at an
  ASSUMED ~15 evals/s/core at n=3 (n=2 realized 29.9); the rate must be measured
  on laptop billy pre-registration and the per-task size rescaled to hold the
  budget — same smoke discipline as QG47's registration.
- **Prediction (lever hypothesis H_n: dimension opens a frontier of non-negligible
  mass at n=3)**: R2 finds >= 1 witness OUTSIDE the known kernel closures
  (per-cell N = 5.625M gives a 95% detection floor of ln(20)/5.625e6 ≈ 5.3e-7;
  the kernel's local density is ~0.2 at Hamming-1). Lift-class enrichment is
  expected first, but witness8 hits all 6 cells, so home-cell hits are admissible.
- **Falsifiers**: (a) R2 completes at full size with 0 witnesses outside known
  closures → per-cell frontier mass < 5.3e-7 at 95% → H_n is falsified in favor
  of "isolated measure-zero kernel at n=3", and the lever moves off dimension
  (next candidate: structured sublattices / instance shape). (b) R1's depth-3
  closure contains 0 witnesses while R2 is sparse → the kernel decays faster
  than the dimension-geometry reading predicts, independently weakening H_n.
- Gates: retain G1/G4/G5 and extend G6 to also bind the QG47 receipt
  (sha `67c73bf9…`, terminal `QG47_N2_FRONTIER_EMPTY`) for chain continuity.

## 7. Honest limitations

- The identity `C_DP == C_Dxx` at n=2 is certified empirically over 68.3M
  evaluations, not proven as a theorem; this analysis produces no certificate of
  WHY the cap never binds at n=2 (a separate theory task).
- Parts carry only the gap integer — no per-instance cost decomposition
  (frame/tag/rotation split), so which cost term ties cannot be attributed.
- Independent re-computation covers 6,750 merge probes + 30 local re-evals; the
  remaining evaluations rest on the digest chain plus the internal-consistency
  checks verified here for all 1,350 parts — not on a second full sweep.
- Grid coverage is 6 cells (all rho=0); the identity could in principle fail at
  untested extreme weights, though zero variation across t_c 1–3, t_nc 4–7,
  t_r 2–3 argues strongly against.
- All available conditioning variables (letter, pair, objective, class) have a
  constant outcome: the cross-tabs prove uniformity, not mechanism; there is no
  slice-level near-miss structure to exploit.
- R2's eval-rate assumption is unmeasured; if n=3 runs slower than assumed the
  sample count (and detection floor) must be rescaled before registration.

Inputs: `research/extensions/orion-qg/QG47_PARTS/` (1,350 parts),
`QG47_N2_FULL_SWEEP_RESULTS.json`, `qg47_n2_full_sweep.py`,
`qg2_objective_robustness.py`, `QG45_WITNESS8_ANATOMY_RESULTS.json`,
`QG46_KERNEL_ANATOMY_RESULTS.json`,
`development/orion-qg-regime-geometry/QG47_N2_FULL_SWEEP_PROTOCOL_V1.md`,
`RUN_QG47_CAMPAIGN.log`. Analysis scripts ran outside the repo; no input file
was modified.

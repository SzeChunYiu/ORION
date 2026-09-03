# QG45 — witness #8 anatomy: structural stability of the unique t_c >= 2 lift (V1)

## Aim

QG44 (receipt `QG44_N2_FRONTIER_RESULTS.json`, terminal
`QG44_FRONTIER_IS_GEOMETRY`) established that across all its panels exactly
ONE instance — QG-43 witness #8, `P4:RANDOM_n3:11` (n=3, targets
`[(3,7),(5,0),(2,4),(0,2),(5,4),(7,1)]`) — carries witnesses at objectives
with the absolute central cost lifted off 1 (`t_c >= 2`), holding all 4 such
cells (`(dc,dnc) = (-2,0),(-2,1)` at `t_r = 2` (`t_c = 2`) and `(-3,0),(-3,1)`
at `t_r = 3` (`t_c = 3`), all gap -2). Every other witness in the run is
confined to `t_c = 1`. This study asks whether #8's lift is **structurally
stable** (a neighborhood of nearby instances also lifts) or **isolated**
(a thin set of exact masks), and adds two exhaustive n=2 letter-subclass
closures that QG44's minimal-mask alphabet and uniform random panel did not
cover. It is the direct successor to QG44's registered open questions
(a)+(b).

## Frozen machinery (identical to QG43/QG44, imported not copied)

`qg2.dp_cost_pairs_ob`, `qg2.dxx_cost_ob`, `qg2.dp_witness_ob`,
`qg2.brute_config_n1_ob`, `qg2.clear_caches`, `qg2.Objective`;
`gap(I,O) = C_DP - C_Dxx`; a **witness** is `gap < 0` (serialized DP witness
then has `max_frame_support > 2`). rho = 0, t_tag = 2 throughout. Targets are
n-bit masks: every `(x,z)` target of a width-n instance satisfies
`0 <= x,z < 2^n`, `(x,z) != (0,0)` (the machinery's own domain; the
registration smoke test caught and rejected an earlier ±1-perturbation
design that violates it). The base witness and its lift cells are LOADED
FROM THE QG44 RECEIPT (nothing hand-copied): `q4_continuation_rows` row for
instance `P4:RANDOM_n3:11` gives the witnessed objective set; the QG-43
receipt's `witness_rows` entry with `instance == "P4:RANDOM_n3:11"` gives n
and targets (G6 re-verifies both).

## Registered outcome run (single pass, exit 0 = complete)

1. **Objective grid** (6 objectives, all `t_tag = 2`, rho = 0):
   - The 4 `t_c >= 2` lift cells from QG44: `Q45G_tr2_dc-2_dnc0_tag2`
     (`t_nc,t_c,t_r` = 4,2,2), `Q45G_tr2_dc-2_dnc1_tag2` (5,2,2),
     `Q45G_tr3_dc-3_dnc0_tag2` (6,3,3), `Q45G_tr3_dc-3_dnc1_tag2` (7,3,3).
   - The 2 `t_c = 1` home cells: `Q45G_tr2_dc-3_dnc0_tag2` (4,1,2),
     `Q45G_tr2_dc-3_dnc1_tag2` (5,1,2).
2. **Instance panels**:
   - `PA` n=3 mask neighborhood: #8 itself + its single-BIT-FLIP neighbors —
     each of the 6 targets x 2 coordinates x 3 bit positions (`XOR 1<<q`,
     q in {0,1,2}), a flip being skipped and counted iff it would zero the
     target (35 valid + 1 skipped + base = 37 instances) x all 6 objectives
     (222 evaluations). Bit flips are the canonical move on the mask domain
     (domain-safe by construction, uniform across positions).
   - `PB` n=2 projection: #8's targets truncated to the low 2 bits
     (`(x & 3, z & 3)`) at width n=2 — the canonical mask projection of the
     unique lifting instance onto the n=2 domain (5 of 6 targets change,
     `(0,2)` is fixed) x all 6 objectives (6 evaluations).
   - `PC` n=2 exhaustive saturated-letter closures: all `3^6 = 729` ordered
     instances over each of two alphabets, the width-2 analogues of the
     minimal letters `{(1,0),(1,1),(0,1)}` that QG44's P1 exhausted:
     `A_max = {(3,0),(3,3),(0,3)}` (full masks) and
     `A_mid = {(2,0),(2,2),(0,2)}` (mid masks) x all 6 objectives
     (2 x 729 x 6 = 8748 evaluations).
3. **Registered questions** (authored before the run):
   - **Q1 (primary, stability):** how many of the valid PA bit-flip
     neighbors witness (`gap < 0`) at >= 1 of the 4 `t_c >= 2` objectives?
     Registered threshold: **at least half of the valid flips
     (`ceil(F/2)` at runtime, recorded in the receipt)** = structurally
     stable.
   - **Q2 (local geometry):** per-flip witness/gap at each cell; is the
     killing structured (coordinate-, target-, or bit-position-specific) or
     uniform?
   - **Q3 (n=2 projection):** does #8's low-2-bit projection at width 2
     witness anywhere (any of the 6 objectives)?
   - **Q4 (n=2 exhaustive subclasses):** witness count in PC per alphabet
     per cell. Zero everywhere extends the "no n=2 witness" evidence from
     minimal letters + uniform random to full-mask and mid-mask letters;
     nonzero would be the FIRST n=2 witness anywhere (breaking the
     "n >= 3 necessary" reading).
4. **Gates (hard):**
   - `G1`: `C_DP <= C_Dxx` on every evaluation (assert, abort on violation).
   - `G3`: every serialized witness row has `max_frame_support > 2`.
   - `G4`: independent n=1 brute cross-check (full config enumeration via
     `qg2.brute_config_n1_ob`) at the most witness-bearing objective, on 12
     fixed minimal-letter instances.
   - `G5`: anti-instrument import gate (as QG43/QG44).
   - `G6` (QG44 receipt binding): `QG44_N2_FRONTIER_RESULTS.json` sha256
     recorded; its terminal must be `QG44_FRONTIER_IS_GEOMETRY`; #8's
     `q4_continuation_rows` entry must round-trip — reconstruct every
     objective in its `qg44_witness_at` map from the QG44 receipt's own
     serialized grid weights (or its name), re-evaluate #8, and require the
     same gap at every entry; and #8 must be present in the QG-43 receipt's
     `witness_rows` with the same serialized targets/n used to build PA/PB.
5. **Artifacts:** `QG45_WITNESS8_ANATOMY_RESULTS.json` (schema
   `ORION.QG.QG45.Witness8Anatomy.v1`: objectives, `q1_neighbor_witness_count`,
   `q1_valid_flips`, `q1_threshold`, `q1_threshold_met`, per-flip table (Q2),
   `q3_projection_rows`, `q4_pc_verdicts`, `g4_brute_report`,
   `g6_qg44_binding`, witness rows capped at 40), `RUN_QG45.log`.

## Terminals

- `QG45_LIFT_IS_STRUCTURALLY_STABLE` — Q1 meets the half-of-valid-flips
  threshold: #8's lift survives single-bit perturbation; the `t_c >= 2`
  frontier at n=3 has interior.
- `QG45_LIFT_IS_ISOLATED` — Q1 below threshold: the lift is confined to a
  thin set of exact masks (isolated up to single-bit moves).
- `QG45_CONSISTENCY_FAILURE` — any gate violated (exit 3, no claims).

Independent of the terminal, Q3/Q4 outcomes are recorded as fields: an n=2
witness in PB/PC would be the first n=2 witness anywhere; zero extends the
"n >= 3 necessary" reading to the saturated and mid letter subclasses.

## Discipline & authority

No fitted parameters; every number is an exact integer from the frozen
`qg2_objective_robustness` machinery (imported, not copied). Unique
`Objective.name` per grid point; `clear_caches()` between objectives only.
PA/PB are finite defined sets (exact in instances); PC is EXHAUSTIVE over
its two registered subclasses at width 2. Authority: EXACT IN INSTANCES for
the evaluated panels; NO all-n claim, NO region claim; NOT R6. Successor
(QG46, conditional): if STABLE — extend the neighborhood (two-bit flips,
mask-scaling ladder) toward a positive-measure lift-set statement; if
ISOLATED — the n-threshold attack (exhaustive signed/full-alphabet n=2
sweep beyond letter subclasses, chunked) as the width analogue of QG8's
cone theorem.

# QG-17b — the tie locus: converting QG-17's bounded negative into an exact phase-boundary location

Date: 2026-08-22
Lane: ORION-QG QG-17b
Parent negative: QG-17 (`research/extensions/orion-qg/QG17_R6I_PHASE_SHARPNESS_RESULTS.json`, terminal `QG17_NO_SUPPORT2_WITNESS_IN_FROZEN_V5_DOMAIN`)
Parent protocol: `development/orion-qg-regime-geometry/QG17_R6I_PHASE_SHARPNESS_PROTOCOL_V1.md`
Parent phase theorem: QG-16 (`research/extensions/orion-qg/QG16_R6I_SUPPORT1_PHASE_RESULTS.json`, `GLOBAL_PHASE_BOUNDARY_SHARPNESS = OPEN`)
Frozen candidate generator owner: QG-9 V5 (`research/extensions/orion-qg/qg9_support2_tightness.py`)
Reopen adjudication: `development/orion-qg-regime-geometry/reopen-adjudication/REOPEN_TERMINAL.json` — `INACTIVE_NO_ATOM_CONDITION`
Status: **FROZEN BEFORE ANY TIE-LOCUS SCORING, HYPERPLANE EXTRACTION, OR CROSSING EVALUATION.**

Authority ceiling: exact finite tie-locus geometry for the frozen R6I n=2 obstruction-block domain only.
**NOT_R6.** No novelty authority, no physical quantum-advantage authority, no global phase theorem.

## Why this lane exists

QG-17 scanned all 211,248 frozen V5 candidates at three pre-registered outside objectives for a
support-2 witness strictly beating the exact weighted support-1 optimum, and found none. Its own
post-hoc diagnostic (authority `NONE`) recorded that at `O_nc_out` the maximum of `C_cap1 - C2` is
**exactly 0**, attained as an exact tie on **4,896 of 211,248** candidates, while at `O0`,
`O_tag_out` and `O_restore_out` the maximum is strictly negative (`-5`, `-5`, `-13/4`).

The reopen adjudication's reading: a tie at exactly zero is the signature of sitting **ON** the phase
boundary, not of narrowly missing a witness. QG-17's frozen rule demanded strict inequality, so its
witness condition is inactive precisely where the objective is boundary-valued. This lane therefore
stops hunting witnesses and instead **solves for the locus where the tie occurs**.

## Frozen questions

Verbatim, and the protocol is designed around exactly these three:

- **Q1 (the locus).** For each frozen V5 candidate, the difference `d = r2 - r1` of its integer
  resource vectors defines a hyperplane `d . theta = 0` in objective space. Compute the exact set of
  hyperplanes realized by the 4,896 tied candidates at `O_nc_out` (exact rational/integer arithmetic
  — no floats). Is `O_nc_out` exactly ON those hyperplanes? Report the exact hyperplane set, its
  multiplicity, and whether it is a single hyperplane or several.
- **Q2 (sharpness).** For each realized hyperplane, does crossing it flip the sign of `C_cap1 - C2`
  for the tying candidate — i.e. does a support-2 member strictly beat support-1 on the far side? If
  yes for at least one, an **exact local phase boundary** has been located: the support-1 certificate
  genuinely fails immediately across it, and QG-16's facet is locally sharp there. Serialize each
  such crossing witness verbatim with its theta, its d, and both costs, referee-recomputed. If no
  crossing flips the sign, say so — that is a real negative and means the tie is degenerate rather
  than boundary-marking.
- **Q3 (relation to QG-16's facets).** Compare each realized tie-hyperplane's normalized normal to
  QG-16's four facet normals (exact proportionality, not numeric closeness). An exact match earns the
  annotation `QG17B_QG16_FACET_LOCALLY_SHARP_BY_TIE_LOCUS`. A tie-hyperplane that is *not*
  proportional to any facet is equally interesting — it means the true boundary has a face QG-16's
  certificate does not describe; report it verbatim.

## Coordinate and sign conventions (frozen)

Resource vectors are integer 4-vectors in the order

`r = (U_c_extra, U_nc_extra, TagSupport, RestoreSupport)`,

paired with the objective coefficient order `(t_c, t_nc, t_tag, t_r)`, so that

`C(theta) = r . (t_c, t_nc, t_tag, t_r)`.

`d = r2 - r1 = (d_c, d_nc, d_tag, d_r)` is the fixed-configuration cost-difference normal, exactly as
in QG-17's `witness_record`. Hyperplane normalization is QG-17's committed
`normalize_vector`: divide by the integer gcd of the components, then fix the sign so that the dot
product with `O0 = (t_c, t_nc, t_tag, t_r) = (2, 4, 2, 1)` is non-negative, with ties broken by making
the first nonzero component positive. The same normalization is applied to QG-16's facet normals, so
proportionality is decided by exact integer vector equality after normalization.

The scanner's internal objective tuple order is `(t_nc, t_c, t_tag, t_r)` scaled by a positive
integer `scale`; this protocol keeps that representation for the imported referee and converts to
`d`-order only for hyperplane arithmetic. All conversions are integer permutations.

## Instrument reuse — no re-derivation, no modification

The analyzer imports, unmodified:

- `research/extensions/orion-qg/qg9_support2_tightness.py` — `obstruction_blocks()`,
  `candidate_pairs()`, `template_instances()`, family order
  `IDENTITY_RESTORE, ONE_DEFECT_A, ONE_DEFECT_B, MATCHED_DEFECT`, original enumeration order;
- `research/extensions/orion-qg/qg17_r6i_phase_sharpness.py` — `support2_static`, `support2_score`,
  `WeightedCap1` (the exact weighted cap-1 referee, including its 12 ordered support-1
  anticommuting frame pairs, its 12x12 shared-Tag support table and its target-triple caches),
  `OBJECTIVES`, `FAMILIES`, `normalize_vector`, `QG16_FACETS`.

The generator pre-score digest is recomputed and must equal V5's committed
`candidate_generator_digest_before_scoring = bb07c127d037f68e2a1f6ca6b5defee0fbadcebdb3ae23aedd4e7266f184a4fa`.

No QG-16, QG-17, V5 or harness file may be edited by this lane. This lane writes only new files.

## Domains (complete, sizes recorded, no truncation)

- unique obstruction blocks: 1,296;
- compatible SELF/CROSS block pairs: 4,104;
- candidate instances: 211,248, with family counts
  `IDENTITY_RESTORE 4104`, `ONE_DEFECT_A 69768`, `ONE_DEFECT_B 69768`, `MATCHED_DEFECT 67608`;
- objectives re-scanned (QG-17's frozen four, same order):
  `O0 = (t_nc,t_c,t_tag,t_r) = (4,2,2,1)`;
  `O_tag_out = (4,2,5/2,1)`; `O_restore_out = (4,2,2,5/4)`; `O_nc_out = (3/2,3/2,1,1)`.

Every candidate is scored at every one of the four objectives. Nothing is sampled; nothing is
truncated.

## Q1 procedure — the exact tie locus

1. Scan the complete domain once. For every candidate and every objective record the exact scaled
   integer costs `C2` and `C_cap1` returned by the imported referee.
2. At each objective record the exact maximum of `C_cap1 - C2` as a reduced rational, the exact count
   of strict witnesses (`C2 < C_cap1`) and the exact count of ties (`C2 == C_cap1`).
3. The **tie set** `T` is the set of candidates with `C2 == C_cap1` at `O_nc_out`, in frozen
   candidate order.
4. For every member of `T` compute `d = r2 - r1` over the integers.
   - If `d` is the zero vector the candidate is a **degenerate tie**: it defines no hyperplane. Such
     candidates are counted and reported separately and are never counted as locating a boundary.
   - Otherwise the candidate realizes the hyperplane `H_d = {theta : d . theta = 0}` with normalized
     normal `normalize_vector(d)`.
5. Assert exactly, over the integers, that `d . O_nc_out = 0` for every non-degenerate tie — this is
   the literal statement that `O_nc_out` lies ON the realized hyperplane. Any failure is a hard
   `QG17B_CANNOT_CHECK`.
6. Report the exact set of distinct normalized normals with multiplicities, the raw `d` vectors
   collapsing to each, and whether the set is a single hyperplane or several.

## Q2 procedure — the crossing test (pre-registered, deterministic)

For a realized non-degenerate normalized normal `d`, the two **crossing objectives** are defined by
the frozen rule, with the pre-registered integer offset multiplier `M = 64`:

`theta_minus(d) = M * O_nc_out - d`,  `theta_plus(d) = M * O_nc_out + d`,

computed componentwise in the scanner's `(t_nc, t_c, t_tag, t_r)` integer representation at scale
`2M = 128` (`M * O_nc_out` has integer coefficients `(192, 192, 128, 128)` at scale `128`), with `d`
permuted from `d`-order into that order. By construction

`d . theta_minus = -(d . d) < 0`  and  `d . theta_plus = +(d . d) > 0`,

so the two objectives straddle `H_d` exactly, at equal and opposite exact rational offsets from
`O_nc_out`, and no other point of objective space is consulted. `M` is fixed before scoring and is
never tuned to an outcome.

Feasibility gate: every component of both crossing objectives must be strictly positive. If not, the
hyperplane is recorded `CROSSING_OBJECTIVE_INFEASIBLE` and contributes no witness.

For every tied candidate realizing `d`, and for each of `theta_minus` and `theta_plus`:

- recompute `C2` and the exact weighted `C_cap1` from scratch with the same committed referee at that
  objective (the referee re-optimizes both the support-2 central-branch choice and the entire
  support-1 12x12 frame/Tag/permutation family at the new objective; nothing is extrapolated
  linearly);
- the candidate is a **crossing witness** on that side iff `C2 < C_cap1` strictly.

A strict crossing witness is, by the same logic QG-17 committed, a proof that support 1 is not
sufficient at that exact objective: `C_DP <= C2 < C_cap1`.

Serialization, complete and without truncation:

- per hyperplane and per side, the complete list of crossing-witness candidate indices;
- per hyperplane and per side, the first crossing witness in frozen candidate order and the
  maximum-gap crossing witness (tie-broken by candidate order), each serialized verbatim with its
  full theta as exact rationals, its blocks, targets, template metadata, `r2`, `r1`, `d`, both exact
  costs and the exact gap.

Each serialized witness additionally records QG-16 cone membership of its objective, evaluated
exactly against QG-16's four committed halfspaces.

## Q3 procedure — facet comparison

For every realized normalized tie-hyperplane normal, compare by exact integer equality against
`normalize_vector` applied to each of QG-16's four committed facet coefficient vectors in
`(t_c, t_nc, t_tag, t_r)` order:

`[0,2,0,-5]`, `[1,1,0,-5]`, `[0,2,-2,-2]`, `[1,1,-2,-2]`.

Exact equality after normalization is proportionality; nothing numeric is used. A realized normal
matching no facet is reported verbatim as `NEW_TRUE_BOUNDARY_FACE_NOT_IN_QG16_CERTIFICATE`, and this
is reported whether or not it carries a crossing witness.

## Terminals (frozen, all valid)

- `QG17B_EXACT_PHASE_BOUNDARY_LOCATED` — at least one realized tie-hyperplane carries at least one
  sign-flipping crossing witness, and all gates pass;
- optional annotation `QG17B_QG16_FACET_LOCALLY_SHARP_BY_TIE_LOCUS` — additionally, at least one such
  boundary-locating hyperplane is exactly proportional to a QG-16 facet normal;
- `QG17B_TIE_LOCUS_DEGENERATE__NO_CROSSING_WITNESS` — the tie set is reproduced and its hyperplanes
  extracted, but no crossing on any side produces a strict support-2 win. Honest negative;
- `QG17B_CANNOT_CHECK` — any gate failure, digest drift, exception, or arithmetic-exactness
  violation. Fails closed.

## Gates (all must pass; hostile)

1. `protocol_present` — this file exists and its SHA-256 is recorded in the result.
2. `parents_bound` — QG-16 terminal `QG16_R6I_OBJECTIVE_INDEXED_SUPPORT1_CONE_ALL_N_MACHINE_CHECKED`
   and `global_phase_boundary_sharpness == "OPEN"`; V5 terminal
   `QG9_NO_SUPPORT2_TIGHT_WITNESS_IN_FROZEN_INVERSE_PANEL`; QG-17 terminal
   `QG17_NO_SUPPORT2_WITNESS_IN_FROZEN_V5_DOMAIN` with `both_accept == true`.
3. `generator_digest_exact` — recomputed pre-score generator digest equals `bb07c127...f184a4fa`.
4. `unique_blocks_1296`, `pair_count_4104`, `candidate_count_211248`, `family_counts_match_v5`.
5. `qg17_strict_counts_reproduced_verbatim` — zero strict witnesses at all four objectives.
6. `qg17_max_margins_reproduced_verbatim` — exact maxima of `C_cap1 - C2` equal QG-17's recorded
   `O0 = -5`, `O_tag_out = -5`, `O_restore_out = -13/4`, `O_nc_out = 0`.
7. `qg17_tie_counts_reproduced_verbatim` — exact tie counts equal QG-17's recorded
   `O0 = 0`, `O_tag_out = 0`, `O_restore_out = 0`, `O_nc_out = 4896`.
8. `O0_control_zero_strict_and_zero_tie` — the inside control holds on both counts.
9. `objective_on_every_tie_hyperplane` — `d . O_nc_out == 0` exactly for every non-degenerate tie.
10. `crossing_objectives_from_frozen_rule` — every evaluated crossing objective equals
    `M * O_nc_out -/+ d` with `M = 64`, recomputed from the recorded `d`.
11. `every_crossing_witness_referee_recomputed` — every serialized crossing witness's `C2`, `C_cap1`
    and gap were produced by the committed referee at that witness's own objective.
12. `no_float_in_decisions` — every value entering a comparison, a gate, a cost or a hyperplane is an
    `int` or a `fractions.Fraction`; the analyzer asserts this at each decision point and no
    floating-point value is constructed anywhere in the scientific path.
13. `complete_domain_no_truncation` — all four domain sizes recorded and matched; all crossing-witness
    index lists complete.
14. `authority_ceiling` — `novelty_authority == false`, `physical_quantum_advantage_claim == false`,
    `global_phase_boundary_complete == false`, `global_phase_boundary_sharpness == "OPEN"`.

## Determinism

The analyzer is run twice. Both the canonical stdout token line and the results JSON minus timing
fields must be byte-identical. Timing lives outside the digested result object.

## Independent generic verifier

`development/orion-qg-regime-geometry/qg17b_generic_verify.py` re-derives the result from primitives
and emits an ACCEPT/REJECT token. It must:

- implement its own phase-free two-qubit Pauli algebra (`mul`, `wt`, `symp`, `labels`, frame triple)
  from scratch, and its own exact weighted support-1 optimizer and support-2 scorer, in
  `fractions.Fraction` arithmetic, **without importing `qg17b_tie_locus.py` or
  `qg17_r6i_phase_sharpness.py`**;
- rebuild the complete 211,248-candidate domain from the digest-gated frozen V5 generator;
- independently recompute the tie set at `O_nc_out`, the `d` vectors, the normalized hyperplane set
  and its multiplicities, and compare them to the committed result;
- independently re-derive both crossing objectives for every realized hyperplane from the frozen
  `M = 64` rule;
- independently re-evaluate the crossing test for every tied candidate on both sides, and compare
  the full crossing-witness index lists and every serialized witness's exact costs, gap, `r2`, `r1`
  and `d`;
- re-check the result digest, the protocol SHA-256, the generator digest, all gates and the
  anti-overclaim block;
- decide `ACCEPT_EXACT_PHASE_BOUNDARY`, `ACCEPT_TIE_LOCUS_NEGATIVE` or `REJECT`.

A digest-valid receipt proves nothing about correctness; this verifier is not optional and its
REJECT is binding.

## Runtime

Disclosed cap: **< 25 minutes** of wall time per run for the analyzer and, separately, for the
verifier. Exceeding the cap is a `QG17B_CANNOT_CHECK`, never a silent truncation of the domain.

## Anti-overclaim (mandatory, regardless of outcome)

- `GLOBAL_PHASE_BOUNDARY_COMPLETE` stays **false** and global phase-boundary sharpness stays
  **OPEN**.
- Locating one face of the boundary is **local** evidence at exact objectives. It is never a complete
  global phase theorem.
- A crossing witness proves support 1 fails **at its own exact objective on this frozen domain**. It
  never claims support 2 is required anywhere else, and it never generalizes to a neighbourhood
  beyond the exact rational points evaluated.
- QG-16's certificate remains valid where it applies; nothing here refutes it. Outside its cone the
  QG-16 semantics `THIS_PROOF_CERTIFICATE_DOES_NOT_APPLY__NOT_SUPPORT2_REQUIRED` continue to hold for
  every point not explicitly evaluated here.
- No novelty authority, no physical quantum-advantage claim, no network access, no chemistry sources
  read, no protected subject read. **NOT_R6.**

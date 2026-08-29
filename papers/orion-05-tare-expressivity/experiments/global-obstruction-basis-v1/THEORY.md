# ORION05.GLOBAL_OBSTRUCTION_BASIS.v1 — frozen theory

Date: 2026-08-28. Status: FROZEN_BEFORE_ANY_CENSUS_OUTPUT (frozen 2026-08-28, commit 1404c56cd freezes the protocol). scientific_authority_delta: NONE.
Promotion target: issue #1649 (five-paper review gate for ORION-05).
All definitions below are the repo's own formalism (R6M / R6S / R6O / QG-7c);
nothing is redefined post outcome.

## 1. Frozen background (already established, cited, not re-proved)

- **Grammar/objective.** Frozen R6M three-block shared-one-bit-Tag TARE-M2
  grammar under the frozen support-count objective: three ordered anticommuting
  frame pairs `(R_{j0},R_{j1})`, one shared Tag `S`, common label orientation,
  per-block target permutation and central choice, 15 canonical perfect
  matchings; cost = frame multipliers `m∈{2,4}` + `2 w(S)` + donor-owned
  three-way `F_3` Restore factoring
  (`papers/orion-05-tare-expressivity/manuscript/sections/02-methods.tex`,
  `MANUSCRIPT_V3_REFINED.md` §2).
- **Families.** `C_DP` unrestricted exact optimum; `D+` = complete
  split-anchor support-one frame family with the unique minimum-weight
  compatible Tag (R6O `dplus_definition`); `D++` = frames of support ≤ 2.
- **kappa theorem.** `C_DP = C_D++` for every admitted instance and every `n`
  (R6S, `HUMAN_PROOF_R6S_2026-08-22.md`), and `kappa_R6M = 2` via the exact
  R6O `5 < 6` counterexample.
- **Class formalism (R6S).** For a frame `R` with partner `R'` and Tag `S`,
  each `q ∈ supp(R)` carries `c_q = (alpha_q, beta_q) ∈ F_2^2`,
  `alpha_q = <R_q, R'_q>`, `beta_q = <S_q, R_q>`. Global anticommutation gives
  `sum alpha_q = 1`. A subset with class sum `(0,0)` is deletable without Tag
  repair; the exchange fails at support two on exactly **four ordered class
  tuples** (`MANUSCRIPT_V3_REFINED.md` §4): the tuples with no `(0,0)` member,
  i.e. ordered pairs from the unordered patterns
  `{(0,1),(1,0)}` and `{(0,1),(1,1)}`.
- **Local block-shape inventory (QG-7c M1).** On the complete 262,144-case
  3-qubit block-local domain (frame pair + block-local Tag), every feasible
  irreducible block is exactly one of **three shapes** — `anchored`,
  `phantom`, `comm_s2` — with zero unclassified rows and zero structure
  assertion failures (`research/extensions/orion-qg/qg7c_classification.py`
  `m1_inventory`, receipt `QG7C_CLASSIFICATION_RESULTS.json`,
  `irreducible_shape_counts = {anchored:288, phantom:864, comm_s2:864}`,
  `holds: true`). The comm-s2 **pinned** sector (another block's frame letters
  pinning the borrow-side tag letter) is the one lemma-open sector
  (QG-7c/7d/7e chain).

## 2. New definitions (prospective; freeze before any of the 5,005 outcomes)

**D1 (census family).** The instance family is the complete distinct-target
`n = 2` census: all unordered 6-subsets of the 15 nonidentity phase-ignored
two-qubit Paulis, `C(15,6) = 5,005` instances. Canonical encoding: local
letters `I=0,X=1,Y=2,Z=3` (production convention), Pauli code
`c = 4*a_0 + a_1 ∈ {1..15}` for dense letters `(a_0, a_1)`; instance
`t_i` = the `i`-th 6-combination of `{1..15}` in lexicographic order,
`i ∈ {0..5004}`. The six targets are handed to the solver as dense
letter lists; the solver itself optimizes over the 15 matchings, relative
orders, orientations and centrals, so the unordered set is the correct
instance granule. *Note:* admitted R6M instances in general allow repeated
targets (the registered R6O gap witnesses repeat targets); the census family
is the frozen distinct-target sub-family, and the repeated-target known
witnesses enter only as registered controls (§6).

**D2 (support-one gap).** For instance `t`,
`Delta_1(t) := C_{D+}(t) − C_{DP}(t)`
computed as
`solve_six_targets(t, max_support=1).cost − solve_six_targets(t, max_support=2).cost`
using only the paper's own solver
(`papers/orion-05-tare-expressivity/orion05_r11_sparse_direct_solver.py`,
sha256 `642cc67a…c25d3`). `t` is an **admitted support-one gap** iff
`Delta_1(t) > 0`. (By R6S, `max_support=2` cost equals `C_DP`.)

**D3 (optimal support-two representative).** The canonical
`SparseWitness` returned by `solve_six_targets(t, max_support=2)` under the
solver's frozen deterministic tie-break (canonical matching order +
`_witness_key`). Fully deterministic; no RNG.

**D4 (branch roles).** In a witness with orientation `(l_0, l_1)`, for each
pair the **comm member** `f0` is the member whose Tag label is 0
(`sparse_symp(S, f0) = 0`) and the **anti member** `f1` the one with label 1.
This matches the M1 local model's `(f0, f1)` roles exactly.

**D5 (frozen reduction RED).** Given an optimal witness, repeatedly delete
any coordinate `q` of any weight-two frame `R` with class
`c_q = (0,0)` (i.e. `R_q ≠ I`, `<R_q, R'_q> = 0`, `<S_q, R_q> = 0`),
re-verifying after each deletion that (i) all three pairs still anticommute,
(ii) all Tag labels still equal the orientation, (iii) the recomputed total
cost (via the solver's own `frame_cost` / `restore_cost_full_scan` /
`2·w(S)`) is unchanged. Terminates (support strictly decreases). Output: the
**reduced canonical witness**. Every step is Lemma-E-licensed, so cost
equality is a theorem-backed assertion, not a hope; any violation is a
pipeline defect (CANNOT_CHECK), never silently accepted.

**D6 (the frozen basis B).** `B = {O_ANCHORED, O_PHANTOM, O_COMM_S2}`, the
QG-7c M1 shapes transcribed verbatim to witness geometry. For a pair with
roles `(f0, f1)`, weights `(w0, w1)`, Tag `S`:

- `O_ANCHORED` (`w0 = 1, w1 = 1`): common coordinate `q` (forced by
  anticommutation), structure: `S_q = f0_q ≠ I` and `<S_q, f1_q> = 1`.
  Tag-syndrome occupancy `occ = 1`.
- `O_PHANTOM` (`w0 = 1, w1 = 2`): home `h = supp(f0)`, requires
  `h ∈ supp(f1)`; borrow `b` = the other coordinate of `f1`. Structure:
  `S_h = I`; `S_b ≠ I` with `<S_b, f1_b> = 1`; `f0_h ≠ f1_h`; `occ = 1`.
  (Failure classes: `phantom_home_off_anti`, `phantom_tagged_home` /
  `l1_phantom_at_home`, `phantom_untagged_borrow`, `phantom_home_commute`.)
- `O_COMM_S2` (`w0 = 2, w1 = 1`): partner anchor `a = supp(f1)`, requires
  `a ∈ supp(f0)`; `b` = the other coordinate of `f0`. Structure:
  `S_b ≠ I` with `<S_b, f0_b> = 1`; `S_a ≠ I` with `<S_a, f0_a> = 1`;
  `f1_a ∉ {I, S_a, f0_a}`; `occ = 2`.
  (Failure classes: `comm_s2_partner_off`, `comm_s2_structure`.)

A `(2,2)` block surviving RED is class `NEEDS_L1_REDUCTION` (M1 proved
`(2,2)` blocks reducible only on the block-local domain; a witness-level
survivor is a recorded escalation, not a guessed reduction). Additional
recorded flag per obstruction block: `pinned` — some *other* block's frame
member has a nonidentity letter with nonzero local symplectic against the
borrow-side Tag letter (`<S_b, g_b> = 1`). Pinned comm-s2 stays **inside**
`B` structurally but is reported separately because it is the lemma-open
sector.

**D7 (membership predicate P_B).** For a witness `W` of a gap instance:
`P_B(W) = true` iff at least one pair of `W` containing a weight-two frame
classifies as `O_PHANTOM` or `O_COMM_S2` with *all* structure assertions and
the occupancy check passing. `O_ANCHORED` blocks are recorded but do not
certify a gap obstruction (their frames are weight-one). Non-membership is
always reported with the specific failure-class names above — never as a bare
boolean.

## 3. Symmetry closure of B

Let `G_n = (S_3)^n ⋊ S_n` act by per-qubit permutations of `{X,Y,Z}`
(single-qubit-Clifford letter relabelings, which preserve every local
symplectic product) and qubit permutations; extend by block permutations
`S_3^{blocks}`. Then:

1. Admission, feasibility, and the frozen objective are `G`-invariant
   (`F_3` depends only on equality/nonidentity patterns; frame and Tag costs
   only on supports; all constraints are symplectic).
2. Every predicate in D6 is built from local symplectic products, letter
   equalities under a common relabeling, nonidentity tests, and supports —
   hence `G`-covariant: `shape(g·W) = shape(W)` blockwise.
3. Therefore `B` is a finite union of `G`-orbits: **symmetry-closed**.
4. Remark (candidate, to verify at freeze, not asserted): the orientation
   involution `(l_0,l_1) → (l_1,l_0)` swaps the comm/anti roles and hence
   interchanges `O_PHANTOM ↔ O_COMM_S2`; `B` contains both, so closure holds
   under the extended group either way.

At `n = 2`, `|G_2| = 72` (times block/orientation symmetries); the census of
5,005 instances decomposes into `G_2`-orbits, which the aggregation step
reports (orbit-level consistency of outcomes is a free internal check: two
`G`-equivalent instances must have equal `Delta_1` and equal shape censuses).

## 4. Theorem statement candidates

**T-strong (raw form).** *Every admitted support-one gap in the census family
has, in its raw canonical optimal support-two representative, at least one
block obstruction from `B_gap = {O_PHANTOM, O_COMM_S2}`.*

**T-main (reduced form; the intended promotion theorem).** *Every admitted
support-one gap in the census family has, in its reduced canonical optimal
support-two representative (D5), at least one block obstruction from
`B_gap`.*

**T-weak (provable skeleton; the floor).** *Every admitted support-one gap
has SOME optimal witness containing a weight-two frame whose class tuple is
one of the four R6S irreducible ordered class tuples.*
Proof sketch (from existing machinery, to be written out at freeze):
if `Delta_1(t) > 0`, every optimal witness has a weight-two frame (else it
lies in the `D+` enumeration, contradiction). Repeatedly delete class-`(0,0)`
coordinates (Lemma E: cost cannot increase; optimality: cannot decrease).
Termination with all frames weight-one would again contradict the gap, so a
weight-two frame with no `(0,0)` coordinate survives; its class tuple avoids
`(0,0)` and has odd alpha-sum — exactly the four R6S tuples. ∎ (This form is
*not* the campaign's discovery surface; it is the guaranteed floor. The
campaign's refutable content is T-main/T-strong at the finer M1 shape level,
plus the completeness of the three-shape vocabulary on real optima with a
*global* Tag — precisely where the pinned sector escapes M1's block-local
proof.)

**Relation between forms.** T-weak is expected provable outright. T-main
sharpens "some optimal witness / class level" to "the canonical
representative after frozen reduction / M1 shape level with structure
assertions". T-strong additionally drops the reduction. The campaign decides
T-strong and T-main exactly on the census; a T-main failure with a coherent
verified pattern is a **new obstruction class** (the QG-7 fourth-regime
precedent shows this is a live possibility, not a formality).

## 5. What would count as a new obstruction class (T2 trigger)

A gap instance whose reduced canonical witness has *every* weight-two block
failing D6 — reported as one of the named failure classes
(`phantom_*`, `comm_s2_*`, `NEEDS_L1_REDUCTION`, or occupancy failure) — and
whose failure is replay-verified (witness re-checked by
`verify_witness` + independent classification recomputation). Verbatim rows
are preserved; the class is *named by its failure signature*, never absorbed
by post-hoc basis enlargement (prospective-refutation discipline,
`02-methods.tex` §"Prospective refutation").

## 6. Anti-vacuity controls (frozen with the protocol; must pass before the census runs)

- **C_POS (three planted positives).** The registered R6O gap instances
  16, 17, 19 (repeated-target `n=2`, `C_DP=5 < 6=C_D+`; targets verbatim from
  `MAX_R6O_ENLARGED_TAG_DONOR_RESULTS.json`) run through the *identical*
  pipeline: each must yield `Delta_1 > 0` and `P_B = true`.
- **C_NEG_CORRUPT (corrupted basis; must fire).** For each C_POS result, the
  same membership function is re-evaluated with a basis mask that removes the
  shape class the real run found. It MUST return `NOT_IN_BASIS` with the
  correct residual failure report. A corrupted-basis control that does not
  fire aborts the campaign (`CANNOT_CHECK_CONTROL_FAILURE`).
- **C_SYNTH_B (planted structure violation; predicate-only; must fire).** The
  hand-built block-local triple `f0 = X@q0`, `f1 = (X@q0, Y@q1)`,
  `S = (Z@q0, X@q1)` routes through the SAME classifier: no Lemma-E-deletable
  coordinate (both classes `(0,1)`), phantom candidate with
  `phantom_tagged_home`/`l1_phantom_at_home` and `phantom_home_commute`
  firing. Expected: `NOT_IN_BASIS` with exactly those classes.
- **C_SYNTH_A (reduction-path control).** `f0 = X@q0`,
  `f1 = (Y@q0, X@q1)`, `S = X@q0`: coordinate `q1` of `f1` has class `(0,0)`
  and must be deleted by RED, leaving an `O_ANCHORED` `(1,1)` block with no
  failures.
- **Terminal-level anti-vacuity.** `T1_BASIS_COMPLETE` is claimable only if
  `gap_count ≥ 1` in the census; `gap_count = 0` routes to the distinct
  terminal `T4_NO_GAPS_IN_CENSUS` (the theorem would be vacuous on the
  census family and only the registered repeated-target panel carries it —
  a materially different, weaker paper claim).

## 7. Explicit non-claims

No all-`n` theorem (the census is `n=2`-complete only; all-`n` requires the
pinned comm-s2 lemma or a new composition argument). No production/search
value (R12 terminal `ORION05_R12_EXACT_BUT_NO_PRODUCTION_VALUE` and R13
completion-only stand; the compiler/search-consequence lane of #1649 is a
separately frozen successor protocol under information-matched baselines,
not this campaign). No novelty, venue, or submission authority.

## Prospective clarifications (pre-outcome, 2026-08-28, before any census row was read)

Recorded while the census executes and strictly before any outcome access;
each answers an ambiguity the independent checker flagged (CHECKER_NOTES.md
A0-A9). Nothing below changes a predicate; each fixes a previously
under-specified reading, chosen now so no post-outcome arbitration can occur.

- **A0 (reduction order).** Order-independence of the membership verdict is
  NOT assumed. The runner's deletion order (pair, then member, then
  coordinate, with restart) is normative for the RECORDED reduced witness.
  The checker verifies membership of the recorded reduced witness with its
  own predicates AND independently re-reduces in its own order; if its
  verdict differs, the row is CANNOT_CHECK__CHECKER_DISAGREEMENT — a
  genuine finding about order sensitivity, never arbitrated post hoc.
- **A2 (header).** The former draft header wording is superseded by the
  status line; this file is frozen as of commit 1404c56cd.
- **A4 (occ domain).** The occupancy count ranges over
  union(supp f0, supp f1), matching the frozen runner and checker.
- **A5 (T2 replay).** "Replay-verified" for a GAP_NOT_IN_BASIS row means: a
  separate verification job re-solves THAT instance once with the same
  frozen solver and recomputes membership through BOTH the runner's and the
  checker's predicate implementations; T2 requires gap > 0 and NOT_IN_BASIS
  to reproduce under both. Rows failing replay are CANNOT_CHECK rows, not T2
  evidence.
- **A6 (requeue provenance).** The requeue pass writes
  REQUEUE_MANIFEST_V1.json listing retried instance ids; only rows still
  TIMEOUT/ERROR after appearing there ground CANNOT_CHECK_INCOMPLETE_CENSUS.
- **A8 (aggregate schema).** The aggregation job writes RESULT_V1.json with
  exactly: schema, counts per per-instance outcome, gap_count, terminal (via
  the frozen decision order), control block verbatim, requeue manifest sha,
  solver/protocol/checker shas, and environment. No other authority fields.
- **A9 (adverse rows).** TIMEOUT/ERROR rows must not carry an outcome
  field; additional diagnostic fields are permitted and non-authoritative.
- **A1 (base binding).** The design-base is bound by branch history: freeze
  commit 1404c56cd; the PROTOCOL.json placeholder is superseded by this
  note rather than rewritten.

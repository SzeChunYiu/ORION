# ORION-QG lane QG-2 — Objective robustness of the TARE regime geometry: protocol V1

Date frozen: 2026-08-21 (frozen BEFORE any QG-2 outcome was computed).
Parent: ORION-QG programme charter V1 (`PROGRAMME_CHARTER_V1.md`, issue #740), lane QG-2.
Branch: `claude/orion-harness-verification-b17qdj`.
Authority ceiling: NOT_R6. No novelty credit, no donor credit, no scientific authority.
The protected stretched-N2 subject remains sealed and is never read.

## 1. Question

The R6N..R6S chain mapped a complete regime geometry for the frozen R6M three-block
TARE-M2 shared-Tag grammar **under one scalar objective** — the raw support-count
objective `C = Σ_blocks [4·(w_nc−1) + 2·(w_c−1)] + 2·w(S) + support(factored Restore)`
(non-central frame support 4/unit, central 2/unit, Tag 2/unit, Restore 1/unit, with the
donor-owned all-three factor rule pricing a matched non-identity letter triple at 1
unit). The geometry consists of:

- weight-one donor optimality on chemistry (C_DP == C_R6L on all 30 recorded matchings),
- the anchor-**split** trade (R6N/R6O: C_D+ < C_R6L) and the Tag-**borrow** trade
  (R6O/R6Q: C_DP < C_D+ via one weight-2 central-branch frame),
- support-2 sufficiency (R6P empirically, R6S as an all-n machine-checked theorem whose
  refund/repair arithmetic — Lemma E, ΔF3 ≤ m ∈ {2,4} — is objective-specific),
- the exact membership predicate P1 (R6Q): donor-exact ⟺ [Gsplit = 0] ∧ [f_B ≥ C_R6L].

QG-2 asks: does this geometry survive materially different cost objectives, or is it an
artifact of the 4:2:2:1 exchange rates? Honest outcome space per objective:
GEOMETRY_ROBUST / GEOMETRY_OBJECTIVE_DEPENDENT; overall MIXED when the two objectives
disagree. Objective-dependence is a finding, not a failure.

## 2. Frozen objectives (chosen BEFORE any outcome was computed)

Every objective is a re-weighting of the same four structural cost coordinates of the
frozen grammar (the grammar, acceptance structure, factor rule, and rotation counts are
untouched), plus an optional per-rotation charge:

`C_ob = Σ_blocks [t_nc·(w_nc−1) + t_c·(w_c−1)] + t_tag·w(S) + t_r·U_factored + ρ·(#rotations)`

where `U_factored` is the factored-Restore support in units (a matched non-identity
all-three letter triple counts 1 unit; every other non-identity letter counts 1 unit
each), exactly the frozen R6L/R6M factor rule re-priced linearly.

- **O0 (baseline, control only)**: (t_nc, t_c, t_tag, t_r, ρ) = (4, 2, 2, 1, 0). This is
  the committed objective; it is computed only to bind the QG-2 machinery to the
  committed receipts (R6O/R6P/R6Q), never as a new result.

- **O1 (T-count-weighted)**: (t_nc, t_c, t_tag, t_r, ρ) = **(7, 1, 4, 3, 0)**.
  Rationale (declared model): in a fault-tolerant T-gate-dominated cost model the
  non-central branch of a TARE-M2 frame carries the arbitrary-angle rotation whose
  magic-state/T cost dominates — order 7 units per support unit (typical ~7–15 T per
  synthesized rotation) — while the central branch is Clifford-dominated at 1 unit;
  the frozen ratio 7:1 is materially different from the original 4:2 = 2:1. Tag: the
  shared Tag check is applied twice per protocol and each application is re-priced at 2
  T-model units, so t_tag = 4 (vs. original 2·1 = 2). Restore: Pauli-frame corrections
  must be commuted through the non-Clifford layer, re-priced at 3 units per support
  unit (vs. 1). The deliberate effect, stated before outcome: both trade currencies are
  re-priced — an extra Tag anchor now costs 4 against restore savings of 3/unit
  (original 2 against 1/unit), and the borrow surcharge (one weight-2 central-branch
  frame) now costs t_c·1 = 1 against restore savings of 3/unit (original 2 against
  1/unit) — so the split and borrow boundaries are both expected to move; whether the
  two-trade structure itself survives is the question.

- **O2 (rotation-coupled)**: (t_nc, t_c, t_tag, t_r, ρ) = **(4, 2, 2, 1, 5)**.
  Rationale: rotation count was a frozen non-compensatory coordinate in the whole R6
  chain (candidates were required to be rotation-nonworse; ties at 9 vs 10 rotations
  were never priced). O2 couples it into the scalar objective at ρ = 5 per rotation —
  comparable to the observed support deltas (0..3) — so the 9-rotation R6M-grammar
  family pays 45 while the 10-rotation two-M3 donor stack pays 50, and a one-rotation
  advantage now outweighs small support ties.
  Structural lemma (stated frozen, verified in-run): every member of the frozen R6M
  grammar family (DP optimum, R6L, D+, D++, borrow family) has exactly 9 rotations, so
  within-family O2 costs are the O0 costs plus the constant 45; all within-family cost
  *differences*, hence regimes, trades, and the predicate, are exactly invariant. The
  run states O2 within-family numbers as O0 + 45 under this lemma (the lemma's premise
  is the committed `ROTATIONS_R6M = 9` constant frozen in the R6M module) and the
  substantive O2 content is the **cross-family** re-pricing at chemistry: the R6L
  Erratum-1 comparator envelope is re-run with every donor point priced C + ρ·rotations
  and every candidate priced C_R6M + 9ρ, from the committed R6M receipt points.

t_c ≤ t_nc is asserted for every objective (it justifies the frozen cheap-on-heavy
central tie-break in the support-capped family).

## 3. Frozen families and their objective-parameterized minima

The committed modules are imported and **never edited**. The DP local tables are
objective-parameterized: they are rebuilt with the frozen weights above (frame-cost,
Tag-cost and F3 tables re-derived from `t_*`), reusing the committed option/parity
algebra (`_DELTA`, `_DIG`, `XOR512`, `ACCEPTING_STATES`) unchanged. The base constant
subtracted from raw DP values is `3·(t_nc + t_c)` (= 18 at baseline).

- **C_DP(ob)**: exact unrestricted DP optimum under objective ob (min over the 4
  relative-permutation configs × 8 central configs × 2 accepting states). n=2 uses the
  two-table XOR identity; general n uses the qubit fold. The DP is the referee.
- **C_R6L(ob)**: the weight-one common-anchor donor family. Its Tag always has weight 1
  and its choice set is objective-independent, so C_R6L(ob) = t_tag + t_r·s*, where s*
  is the minimum factored-Restore unit support over the committed R6L representation
  grammar (computed once per instance via the committed rep enumerator and fast factor
  support).
- **C_D+(ob)**: the R6O enlarged-anchor weight-one family. Cost is linear in the
  objective-independent pair (d, u) = (#distinct anchors, restore units), so
  C_D+(ob) = min_{d∈{1,2,3}} [t_tag·d + t_r·u_d] with u_d the exact per-d minimum
  computed once per instance over the committed R6O choice space (feasibility mask and
  choice arrays reused from the committed module).
- **f_B(ob)**: the frozen R6Q borrow family. Cost is linear in the
  objective-independent pair (p, u) = (#phantom blocks, restore units):
  f_B(ob) = t_tag + min_{p∈{1,2,3}} [t_c·p + t_r·u_p], with u_p the exact per-p minimum
  over the committed borrow option space (reusing the committed per-block option
  builder), the all-anchored corner excluded as frozen. f_B = INF when the family is
  empty, exactly as committed.
- **C_D++(ob)** (support-capped family, support ≤ 2 per frame Pauli): parameterized
  re-implementation of the R6P enumerator (uanti = t_nc·(w_min−1) + t_c·(w_max−1),
  cheap-on-heavy central, minimum-weight shared Tag via the full Tag sweep, don't-care
  min-transform). Computed only where it is informative: on every instance with
  C_D+(ob) > C_DP(ob) ("critical" under ob, n ≤ 3). Where C_D+(ob) == C_DP(ob),
  support-2 sufficiency holds by the exact containment pinch
  C_DP ≤ C_D++ ≤ C_D+ (family containment holds under every linear re-weighting).
  At chemistry (n = 8, 12) a direct D++ sweep is infeasible; unpinched chemistry rows
  are reported honestly as support-2 UNRESOLVED.

Hard integrity assertions on every instance and objective: C_DP ≤ C_D+ ≤ C_R6L
(containment survives linear re-weighting) and C_DP ≤ f_B (borrow soundness).

## 4. Frozen domains

1. **Structured n=2 slice** — the exhaustive 21³ = 9,261-instance panel, enumerated
   exactly as in the committed R6O/R6Q modules (weight-one letters at qubits 0,1;
   21 canonical unordered pairs per block).
2. **Seeded random panel** — seed **20260823**, n ∈ {2, 3}, **60 instances per n**
   (120 total ≥ the 120 floor), generated by the committed generator loop verbatim
   (default_rng, six nonzero uniform Paulis per instance).
3. **Chemistry** — both frozen subjects (H4 n=8, equilibrium-N2 n=12) via
   `r6f._frozen_batch` with blob verification, all 15 matchings each (30 rows).
   Baseline C_DP/C_R6L/C_D+/f_B are bound row-by-row to the committed R6M/R6O/R6Q
   receipts; O1 C_DP is recomputed by the full parameterized DP; O1 families by the
   parameterized enumerators above.

## 5. Frozen per-objective analysis

For each objective ob ∈ {O1, O2} (O0 is the binding control):

1. **Regimes**: per instance, donor_exact (C_DP == C_R6L), split
   (C_DP == C_D+ < C_R6L), borrow (C_DP < C_D+) — the frozen trichotomy.
2. **Trades**: split alive iff some instance has C_D+ < C_R6L with C_DP == C_D+;
   borrow alive iff some instance has C_DP < C_D+. Two-trade identity per instance:
   C_DP == min(C_R6L, C_D+, f_B). Support-2 closure per critical instance:
   C_D++ == C_DP. A **new trade** is any identity failure (NEW_BEYOND_TWO_TRADES) or
   any support-2 closure failure (NEW_SUPPORT3). Minimal witnesses (lowest instance
   index / panel order, cap 12 verbatim) are reported for every alive trade, every
   regime transition class vs baseline, and every new-trade class; new-trade witnesses
   include the parameterized DP backtrack (frames, Tag, supports) with an independent
   cost recomputation under ob.
3. **Chemistry**: all 30 matchings — donor-exact or not per objective, with the full
   cost quadruple per row. For O2, additionally the cross-family comparator re-pricing
   (§2) with per-matching deltas.
4. **Predicate transfer**: P1_ob(t) := [C_R6L(ob) == C_D+(ob)] ∧ [f_B(ob) ≥ C_R6L(ob)]
   against truth donor_exact(ob), confusion counts (tp/fp/fn/tn) reported honestly per
   panel. If P1_ob has any error, re-induction is attempted with the frozen R6Q literal
   family (features recomputed under ob; best conjunction of ≤ 3 literals, deterministic
   order, fit on the structured panel only, then evaluated held-out on the random and
   chemistry panels). Predicate verdict: TRANSFERS_EXACTLY (P1_ob zero error
   everywhere) / RE_INDUCED_EXACT (P1_ob fails, re-induced predicate zero error
   everywhere) / OBJECTIVE_SPECIFIC (neither reaches zero error; confusion reported).

## 6. Frozen verdict mapping

Per objective ob:

- **GEOMETRY_ROBUST** iff ALL of: (i) regime membership of every instance on every
  panel is identical to baseline; (ii) two-trade identity holds on every instance;
  (iii) support-2 closure holds on every resolved instance and no chemistry row is
  support-2-unresolved; (iv) P1_ob has zero errors on every panel; (v) chemistry is
  donor-exact on all 30 rows.
- **GEOMETRY_OBJECTIVE_DEPENDENT** otherwise, with the report stating exactly what
  changed: membership-transition counts and witnesses, trades alive/dead/new with
  witnesses, chemistry verdicts, predicate confusion.

Overall outcome: GEOMETRY_ROBUST if both objectives are robust,
GEOMETRY_OBJECTIVE_DEPENDENT if both are dependent, MIXED otherwise. The authority
string is
`ORIONQ_QG2_OBJECTIVE_ROBUSTNESS_<OVERALL>__FROZEN_REWEIGHTED_OBJECTIVES__NOT_R6`.

## 7. Frozen binding and hostile gates (integrity; failure aborts the run)

1. Parameterized F3/frame/Tag tables at baseline weights reproduce the committed
   `r6m._local_table` cost arrays exactly on a frozen deterministic sample of
   (p6, centrals) configurations (≥ 64 distinct), and the parameterized F3 table at
   baseline equals `r6m._F3`.
2. Parameterized DP equals a parameterized independent brute (full 4^7 at n=1 on the 3
   committed hostile n1 panels; global-Pauli enumeration at n=2 on the 2 committed
   hostile n2 panels) for **both** O1 and baseline weights, over all 32 configs.
3. Baseline binding on the structured panel: O0 regime counts equal the committed R6Q
   receipt exactly (donor_exact 6453, split 2322, borrow 486, identity 9261/9261), and
   O0 C_DP equals the committed reader on every instance (the committed reader IS the
   O0 evaluator).
4. Family-primitive binding at baseline, on deterministic samples: derived C_D+ equals
   `r6o.dplus_pairs` (every 500th structured instance and every 10th random instance);
   derived C_R6L equals `r6m.donor_r6l_matching` (every 500th structured, every 20th
   random); derived f_B equals `r6q.borrow_family_min` (+Tag constant) (every 1000th
   structured, every 30th random); parameterized D++ at baseline equals
   `r6p.dxx_search` on the first 12 baseline-critical structured instances.
5. Chemistry binding: source blobs verified; baseline row quadruples equal the
   committed R6M/R6O/R6Q receipt values on all 30 rows; the O1 general-n DP machinery
   at baseline weights reproduces the receipt C_R6M on the first 3 matchings per
   subject.
6. O2 lemma verification: the rotation count of every family evaluator is the frozen
   constant 9 (`r6m.ROTATIONS_R6M`), asserted; O2 rows are O0 rows + 45 by that lemma.
7. Sandwich and borrow-soundness assertions on every instance and objective (§3).

## 8. Determinism, receipts, runtime

Single deterministic run; RNG only via the frozen seed. Output: one stdout receipt line
`ORIONQ_QG2_OBJECTIVE_ROBUSTNESS=<canonical sorted JSON>` plus the pretty
`QG2_OBJECTIVE_ROBUSTNESS_RESULTS.json` next to the script (indent 2, sorted keys).
Runtime is printed to stderr only and is not part of either artifact, so a double run
must be byte-identical in both artifacts; the run is repeated twice and compared before
the receipt is accepted. Runtime bound: under 25 minutes per run on the session venv
python. Witness caps: 12 verbatim per class (counts always exact). The results file
contains `"r6_authority": false`, `"novelty_credit": false`,
`"reserved_stretched_n2_accessed": false`, and the authority string contains NOT_R6.

## 9. Stop rules and honesty

No gate may be weakened after outcomes are seen. Any integrity-gate failure aborts with
the failing gate verbatim. The expected result may well be that the predicate or the
regime map is objective-specific; that is reported as GEOMETRY_OBJECTIVE_DEPENDENT with
witnesses, not repaired post-hoc. The protected stretched-N2 subject is not read; no
new subject data is introduced; committed files are not modified — QG-2 adds exactly
this protocol, one script, and one results file.

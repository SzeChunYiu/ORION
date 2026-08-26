# ORION-17 necessity-scoping V2 frame protocol V1

**Revival lane:** NR-10 (`research/paper-programme-v1/NEGATIVE_REVIVAL_BACKLOG_V1.md`)
**Negative under revival:** `MATCH_IS_NOT_NECESSARY` (ORION-17.V4.8 / ORION-17-HIST-002 / ledger item
`ORION-17.MATCH_NECESSITY.HISTORICAL_LIMITATION`)
**Pre-registration:** this file is committed before the verification script is executed. The
frame, the theorems, the falsifiers and the decision rule below are frozen now. The script
is run once; its output is reported whatever it says.

## 1. What V1 asked, and why the negative is an artifact of the question

The registered mechanized frame
(`src/orion/study/p7/composition_calculus_smt.py`, artifact
`formal/mechanized/P7_COMPOSITION_CALCULUS_MECHANIZED_2026-08-21.json`) has two layers:

- **Checked layer.** `Match(a, b) := a = b \/ Bridge(a, b)` — ORION-17's T5 test, an
  *administrative* test over contract identity and the registered bridge table.
- **Semantic layer.** `Total(t) <-> forall o. Demands(Tgt t, o) -> Demands(Src t, o) \/
  Discharged(t, o) \/ Fresh(t, o)`, with bridge soundness
  `Bridge(a, b) -> forall o. Demands(a, o) = Demands(b, o)`.

V1 asked its necessity question *across* the layers — "is the administrative test
necessary for the semantic predicate to compose?" — and the witness correctly answers no:
`CONTAINMENT_IS_THE_EXACT_CONDITION` is the semantic answer, and the
`MATCH_IS_NOT_NECESSARY` witness (two obligation-equivalent contracts, no bridge,
composite total, test refuses) shows the administrative test is a strict approximation.

**Attribution (one stage):** the necessity failure is a failure of the *evidence scope*
of the rule, not of the composition semantics. The rule is denied access to `Demands`;
the semantic condition it approximates is defined on `Demands`. No V1 axiom is wrong and
no V1 theorem is weakened by this observation — it names which question each theorem
answers.

## 2. The V2 frame: evidence-bounded composition licensing

V2 makes the evidence boundary part of the frame. A **licensing rule** is a total
function from an *admissible observation* to `{LICENSE, REFUSE}`. Two scopes are
pre-registered:

- **Opaque scope (the registered default).** `obs(t, u) = (Tgt t, Src u, Bridge)` — the
  contract identities at the hand-off and the full registered bridge table. `Demands`,
  `Discharged`, `Fresh` and `Total` are **not admissible evidence**. This is the scope
  ORION-17's fail-closed rule actually operates in.
- **Witness-aware scope.** `obs` additionally admits `Demands` restricted to the two
  hand-off contracts (equivalently: the containment predicate
  `forall o. Demands(Src u, o) -> Demands(Tgt t, o)`).

A rule is **sound** if it never licenses a hand-off whose composite fails the semantic
predicate: for every completion (every `Demands` assignment and bridge table satisfying
bridge soundness) and every pair of total legs, `LICENSE` implies `Total(Comp(t, u))`.
A sound rule is **maximal** if no strictly more permissive rule is sound.

## 3. Pre-registered theorems

A desk derivation done before any execution corrects the obvious first guess and is
recorded here so the sweep tests a stated claim rather than a hope: bridge soundness
(`Bridge(a,b) -> forall o. Demands(a,o) = Demands(b,o)`) has a *symmetric* consequence,
so any undirected path of registered bridges between `a` and `b` already forces
containment at that hand-off — a sound opaque rule may legitimately license more than
`match`. Write `a ~_T b` for "same connected component of the undirected closure of the
bridge table `T`" (reflexive by construction).

| ID | Statement | Status before execution |
|---|---|---|
| N2-A (witness preserved) | The V1 `MATCH_IS_NOT_NECESSARY` witness is re-exhibited verbatim in the V2 frame: both legs total, composite total and demanding something, obligation-equivalent hand-off contracts, distinct, no bridge, opaque observation refuses. | expected HOLD (it is a theorem of V1) |
| N2-B (conditional theorem unchanged) | Under the same completions: both legs total + match ⇒ composite total; both legs total + containment ⇒ composite total. Re-verified, not restated more strongly. | expected HOLD |
| N2-C (containment necessity unchanged) | There is a completion and a both-total leg pair with containment false and composite not total (the V1 countermodel, re-exhibited). | expected HOLD |
| N2-D (opacity conflation) | For hand-off contracts in **different registry components**, there are two completions with the **same opaque observation** and the same leg identities in which both legs are total and match fails, the composite being total in one and not total in the other. Consequence: no sound opaque rule can license that observation — the unregistered-equivalence refusal and the genuine failure are indistinguishable at the evidence boundary. This is the class the V1 witness lives in. | the new mechanism claim |
| N2-E1 (exact opaque characterization) | In each finite frame: an opaque observation `(a, b, T)` is soundly licenseable **iff** `a ~_T b`. Hence the unique maximal sound opaque rule is *registry-connectivity*: it licenses on registry evidence alone, needs no obligation observables, and every strictly more permissive opaque rule is unsound. | the revived necessity claim |
| N2-E2 (where match sits) | `match(a,b,T) -> a ~_T b`, and the inclusion is strict in general (exhibited by a reversed or indirect registration); `match = connectivity` exactly when `T` is **component-complete** — every ordered pair of distinct contracts in the same undirected component is registered (self-pairs are covered by match's identity disjunct; a symmetric and transitively closed registry is component-complete, the converse fails only on self-pairs). The V1 incompleteness therefore decomposes into two administrative gaps, neither semantic: (i) **opacity proper** — unregistered equivalence, conflated with genuine failure, unlicensable by any sound opaque rule; (ii) **directional bookkeeping** — equivalence registered only indirectly, recoverable inside the opaque scope by the connectivity rule. | the scoping claim |

Necessity is thereby recovered in the precise form: *under the registered evidence
boundary, the exact sound-licensing condition is registry-connectivity* — a purely
administrative characterization — *and match coincides with it iff the registry is
closure-complete*. What fails in V1 is only match-as-the-whole-story; the semantic exact
condition (containment, witness-aware scope) is untouched.

## 4. Empirical correspondence (interpretive; boundary disclosed)

The third-change-class transport receipt
(`top_tier/P7_OBJECTIVE_CHANGE_TRANSPORT_RESULT_RECEIPT_V1.md`, PR #1016) maps onto the
two scopes by structural correspondence of the evidence boundary:

- `WITNESS_AWARE = 1.0` — the witness-aware scope: deciding on the changed obligation's
  actual evidence licenses exactly the valid transitions, including the ones a
  registry-style test would refuse.
- `VALUE_ONLY = 0.3` — an opaque-scope rule whose evidence is *coarser than the
  registry* (aggregate value in place of obligation observables): both false closures
  (unsound) and unnecessary reopens (sub-maximal).
- `ALWAYS_REOPEN = 0.1` — a sound strictly sub-maximal rule.

**Boundary:** that study concerns closure transport under an obligation change, not
literally contract hand-off licensing; the correspondence is at the level of the evidence
boundary, not of the modeled objects. It is offered as interpretation, not as proof.

## 5. Verification design (single targeted script, no suites)

`run_p7_necessity_scoping_v2.py`, pure standard-library Python, no pytest, no xdist, no
cloning. It re-implements the registered finite semantic world faithfully (carrier =
(discharged set, declared-new set, source, target); composite = componentwise union with
first-source/last-target — the construction of `_finite_semantic_world` in the registered
module) and then:

1. **Primary exhaustive sweep** — obligations `{o0}`, contracts `{k0, k1}`: every
   `Demands` assignment (4), every bridge-sound bridge table, every leg pair (16 x 16).
   Checks N2-A, N2-B, N2-C, N2-D and the observation-level N2-E1/N2-E2 directly against
   the registered semantics, at the leg level.
2. **Secondary exhaustive sweeps** — 2 obligations x 2 contracts (64 transformations,
   leg level) and 1 obligation x 3 contracts (36 transformations, leg level), plus an
   independent observation-level implementation of sound-licenseability
   (all consistent `Demands` make containment hold at the hand-off) that must agree with
   the leg-level enumeration on every frame where both run.
3. Emits `P7_NECESSITY_SCOPING_V2_RESULT_V1.json` with counts, exhibits and verdicts.

## 6. Falsifiers and decision rule

- N2-E1 is **REFUTED** if any observation's sound-licenseability disagrees with
   registry-connectivity — in either direction. That would mean the opaque-scope
   characterization is wrong and the revival falls back to the claim-boundary artifact
   alone (ORION-17.V4.8 rewrite with the witness as the boundary exhibit, no new necessity
   claim).
- N2-E2 is **REFUTED** if no observation separates match from connectivity, or if the
  match/connectivity agreement ever disagrees with component-completeness of `T`.
- N2-D is **REFUTED** if no conflated pair exists in a two-component situation — then
  the incompleteness mechanism is not conflation and the attribution of section 1 is
  wrong; the fallback is the same claim-boundary artifact with the attribution withdrawn.
- N2-A/B/C failing to hold would mean the re-implementation is unfaithful: halt, no
  claim, repair the implementation against the registered module.

**Outcome tuning prohibition:** no parameter of the frame is adjusted after a first
execution. If the sweep contradicts an expected HOLD, that is reported as a defect of
this re-implementation first (checked against the registered Z3 artifact), never as a
finding.

## 7. Hard-rule compliance

- The V1 conditional theorem (`TOTALITY_COMPOSES_UNDER_MATCH`,
  `CONTAINMENT_IS_THE_EXACT_CONDITION`) is re-verified verbatim; nothing is weakened.
- The V1 witness is preserved as evidence and re-exhibited (N2-A); the V2 reading names
  it the *price of the evidence boundary* rather than retracting it.
- The negative-null-history record `ORION-17-HIST-002` stays immutable; this lane adds a
  scoped successor reading, it does not relabel the negative.

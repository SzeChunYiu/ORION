# ORION-17 necessity-scoping revival receipt V1

**Lane:** NR-10 of `research/paper-programme-v1/NEGATIVE_REVIVAL_BACKLOG_V1.md`
**Branch:** `revive/p7-necessity-nr10` (draft PR, not merged)
**Negative revived:** `MATCH_IS_NOT_NECESSARY` for the broader necessity reading
(ORION-17.V4.8; history record `ORION-17-HIST-002`, immutable; ledger item
`ORION-17.MATCH_NECESSITY.HISTORICAL_LIMITATION`)
**Terminal:** `P7_NECESSITY_SCOPING_REVIVED__OPAQUE_FRAME_CHARACTERIZED__WITNESS_PRESERVED`

## Disposition

The negative is **scoped, not retracted**. Both backlog lever branches were taken: the
frame in which a necessity reading holds was constructed and verified (primary), and the
claim boundary was rewritten around it (ORION-17.V4.10 below). The V1 witness is preserved
unchanged as the boundary exhibit.

## One-stage attribution

The necessity failure is a failure of the **evidence scope of the rule**, not of the
composition semantics. V1 asked its necessity question *across* the two registered
layers: it asked whether the administrative test (`match(a,b) := a = b \/ Bridge(a,b)`,
defined on contract identity and the registry) is necessary for the semantic predicate
(`Total`, defined on `Demands`) to compose. The rule is denied access to `Demands`; the
condition it approximates is defined on `Demands`. No V1 axiom is wrong and no V1
theorem is weakened — the negative names which question each theorem answers.

## The V2 frame (pre-registered, then executed)

`P7_NECESSITY_SCOPING_V2_FRAME_PROTOCOL_V1.md` was committed before execution. A
**licensing rule** is a function from an admissible observation to `{LICENSE, REFUSE}`;
**sound** = never licenses a composite that is not total when both legs are; **maximal**
= no strictly more permissive rule is sound. Two scopes: the **opaque scope** (contract
identities + the full bridge table — what ORION-17's fail-closed rule actually sees) and the
**witness-aware scope** (adds `Demands` on the hand-off contracts).

## Results (single targeted script, stdlib only, no suites)

`run_p7_necessity_scoping_v2.py` re-implements the registered finite semantic world
verbatim (carrier `(discharged, fresh, src, tgt)`; composite = componentwise union,
first source, last target — the construction of `_finite_semantic_world` in
`src/orion/study/p7/composition_calculus_smt.py`) and sweeps three frames exhaustively:

| frame | transformations | completions | leg checks | observations |
|---|---|---|---|---|
| 1 obligation x 2 contracts | 16 | 40 | 9,992 | 64 |
| 2 obligations x 2 contracts | 64 | 112 | 428,424 | 64 |
| 1 obligation x 3 contracts | 36 | 1,216 | 1,549,056 | 4,608 |

All pre-registered claims hold (`ALL_PRE_REGISTERED_CLAIMS_HOLD`, 1.6 s):

- **N2-A witness preserved.** Re-exhibited: legs `(∅,∅,k0,k0)` and `(∅,∅,k1,k0)`, both
  total; hand-off `k0 -> k1` with `Demands(k0,o0) = Demands(k1,o0) = true`
  (obligation-equivalent); empty registry; composite total and demanding something;
  `match` refuses. Exactly the V1 witness.
- **N2-B conditional theorem unchanged.** Zero match-soundness violations and zero
  containment-soundness violations across all 1,987,472 both-total leg checks: match
  implies composability and containment implies composability, re-verified, not
  restated more strongly.
- **N2-C containment necessity unchanged.** The V1 countermodel (both legs total,
  containment false, composite not total) is re-exhibited.
- **N2-D opacity conflation.** Two completions differing only in `Demands` — invisible
  in the opaque scope — share the observation `(k0, k1, empty registry)` and the same
  legs; both legs total in both; the composite is total in the obligation-equivalent
  completion and not total in the other. No sound opaque rule can license that
  observation: the unregistered-equivalence refusal and the genuine failure are
  indistinguishable at the evidence boundary. This is the mechanism of V1's
  incompleteness, and it is the class the witness lives in.
- **N2-E1 exact opaque characterization.** An observation `(a, b, T)` is soundly
  licenseable **iff** `a` and `b` are in the same connected component of the undirected
  closure of `T`. Verified twice per frame — by the observation-level implementation
  (all consistent `Demands` force containment) and by leg-level enumeration — with zero
  disagreements. Hence the unique maximal sound opaque rule is *registry-connectivity*:
  it licenses on registry evidence alone, and every strictly more permissive opaque rule
  is unsound. This is the recovered necessity reading, and it is a necessity of the
  *evidence boundary's strongest sound rule*, not of match for the semantics.
- **N2-E2 where match sits.** `match -> connectivity`, strict in general: with
  `T = {(k0,k1)}`, the hand-off `k1 -> k0` is soundly licenseable (bridge soundness
  forces `Demands(k1) = Demands(k0)`) but refused by `match`. `match = connectivity`
  exactly when `T` is **component-complete** (every ordered pair of distinct
  same-component contracts registered; symmetric-transitive closure is the special
  case, self-pairs being covered by match's identity disjunct). V1's incompleteness
  therefore decomposes into two administrative gaps, neither semantic: (i) opacity
  proper — unregistered equivalence, conflated with genuine failure, unlicensable by
  any sound opaque rule; (ii) directional bookkeeping — equivalence registered only
  indirectly, recoverable inside the opaque scope by the connectivity rule.

## Checker validation

- **Two-run disclosure.** The first execution reported `N2_E2_closure_complete_iff_match`
  false. Diagnosis: the iff `match = connectivity <-> component-complete` is a
  table-level statement and the checker had scoped it per observation pair, counting
  every agreeing pair in a separating table as a violation. Checker defect, not a
  finding; repaired to the pre-registered table-level semantics; re-run green. No
  theorem statement was changed between runs.
- **Mutation sensitivity.** Directed-reachability components: E1 and E2-iff fire.
  Singleton components: E1 fires. Flipped containment direction: N2-B containment
  soundness and E1 fire (match-soundness correctly stays green — it rests on
  bridge-forced equality, not on the containment predicate). Dropping match's identity
  disjunct leaves these verdicts green, which is correct: that disjunct guards the unit
  law (`IDENTITY_NEEDS_A_REFLEXIVE_CONTRACT_TEST`), not licensing soundness.

## Claim-boundary artifact (ledger row added)

`CLAIM_LEDGER_V4.md` gains ORION-17.V4.10: in the evidence-bounded frame, the exact sound
opaque licensing condition is registry-connectivity; match coincides with it exactly
under component-complete registries; the V1 incompleteness decomposes into opacity
proper and directional bookkeeping. Forbidden upgrade stated there: reading any of this
as match being necessary for the semantics, or as weakening ORION-17.V4.8.

## Empirical correspondence (interpretive; boundary disclosed)

The third-change-class receipt
(`P7_OBJECTIVE_CHANGE_TRANSPORT_RESULT_RECEIPT_V1.md`, PR #1016) maps onto the two
scopes by the evidence boundary: `WITNESS_AWARE = 1.0` is the witness-aware scope
(deciding on the changed obligation's actual evidence licenses exactly the valid
transitions, including ones a registry-style test refuses); `VALUE_ONLY = 0.3` is an
opaque-scope rule with evidence coarser than the registry (both false closures and
unnecessary reopens); `ALWAYS_REOPEN = 0.1` is a sound strictly sub-maximal rule. That
study concerns closure transport under obligation change, not contract hand-off
licensing; the correspondence is structural, and is offered as interpretation, not
proof.

## Combination with the codex lane

`src/orion/study/p7/` (composition calculus SMT, closure premises, donor-stack family)
is byte-identical on `origin/main` and `origin/codex/p1-p15-takeover-20260823`
(`git diff` empty for the directory); this lane builds on that registered module as
its source frame and cites it. No rebase; the codex tests
(`tests/unit/study/p7/test_p7_composition_calculus_smt.py`) are untouched.

## Not licensed

- No claim that match — or connectivity — is *semantically* necessary; the semantic
  exact condition remains containment (V1, unchanged).
- No weakening of any V1 theorem; the V1 witness and countermodel are re-exhibited,
  not replaced.
- The general (arbitrary-sort) statements of N2-D/E1/E2 are supported here by the
  finite exhaustive sweeps plus the desk derivation recorded in the protocol (bridge
  soundness forces equality, hence undirected closure); they are **not** re-mechanized
  in Z3 in this lane. Upgrading them to the registered mechanized artifact is the
  named successor step.
- No deployed-agent, empirical or registry-design claim: nothing here says registries
  should be component-complete, only what follows if they are or are not.
- No independent formal review beyond same-lane double implementation and mutation
  sensitivity.

## Binding

| artifact | SHA-256 |
|---|---|
| protocol | `443388880797d589679a1dc56be6f015c5ccc0785f7fadec061be06ec995351c` |
| verifier | `7114202cc5e8a176a039ac09184cd3c7a5ea8660aa31368cffb2c95fcfd2d48d` |
| result JSON | `745db0c7882a8e68ed25857e87c70f4592f99b39c73a0abe53b82da63a5ac61f` |

Executed once (plus the disclosed checker-repair re-run) on Python 3.13.12, macOS,
standard library only.

# Typed Partial-Knowledge State for Research Interface Graphs: Six First-Right-of-Refusal Studies

Manuscript V1 — 2026-08-21. Assembled on branch `claude/orion-harness-verification-b17qdj`.
Every number in this manuscript is traceable to a committed, deterministically replayable
receipt file; every experimental design is traceable to a protocol document frozen before any
outcome existed. Paper boundary fixed by
`papers/Q-paper-02-recursive-recovery/PUBLICATION_PLAN.md` (Paper Q4 section).
Companion claim ledger: `papers/Q-paper-04-typed-state/CLAIM_LEDGER.md`.

## Abstract

Autonomous research pipelines accumulate epistemic state: feasibility beliefs about untried
interfaces, receipts for past failures, certificates transported across representation edits,
intervals where exact costs are unknown. We ask whether *typing and scoping* that state — as
opposed to merely possessing the same information — is load-bearing for decision quality. We
report six prospectively frozen studies on exact-synthetic research interface graphs, each
pitting a typed/scoped mechanism against matched-information strong baselines that hold first
right of refusal, with hostile controls designed to punish untyped shortcuts. Typed-prior
value-of-information probing recovers 71% of oracle utility where donor-complete optimization
on the known subgraph captures 8% and blind commitment is driven to −13.6 mean utility
(`research/extensions/orion-q/nlanes/N4_A_UNKNOWN_VOI_RESULTS.json`). Scope-bound reopening of
stale failure receipts beats never-reopen, always-reopen, and unscoped-change reopening,
pooled and per regime, while a designed wasteful-reopening regime drives always-reopen to
−13.4 (`N4_B_STALE_RECEIPT_REOPENING_RESULTS.json`). Verification targeted at
Pareto-ambiguous interval edges achieves 2.3× lower regret than random verification at the
same budget (`N4_C_INTERVAL_PARETO_RESULTS.json`). Full-chain certificate transport detects
every stronger-oracle laundering attempt — recall 1.000, false-positive rate 0.000, including
all 68 deep splices that provably evade last-hop checking
(`N4_D_LAUNDERING_DETECTION_RESULTS.json`). Decision-coupled experiment selection beats pure
information gain, which max-entropy decoy facts trap into spending 36.6% of its probes on
decision-irrelevant questions (`N4_E_ACTIVE_EXPERIMENTS_RESULTS.json`). Typed
remint/transport of receipts across representation edits beats matched-budget re-derivation
where transport is genuinely available and ties it *exactly* — to the last float — where
remints buy nothing (`N4_F3_REMINT_TRANSPORT_RESULTS.json`). Two honest negatives bound the
claim and show the methodology does not manufacture positives: a typed-failure-state study
whose allocation *policy* is exactly closed by an ideal value-of-information donor
(`N1_C_COSTLY_VERIFICATION_RESULTS.json`), and a crossover-prediction residual absorbed by a
model-selection donor on its original world, surviving only under misspecification
(`N2_F5B_DONOR_COMPARISON_RESULTS.json`). All worlds are deterministic and frozen-seeded;
all receipts replay byte-identically. The package doubles as a reusable benchmark suite for
partial-knowledge research-state mechanisms. All claims are exact-synthetic-bounded
mechanism-isolation results, not deployment claims.

## 1. Introduction

A research pipeline that runs longer than one experiment carries state that is not data about
the world but data about *its own knowledge of the world*: which interface constructions have
been tried and failed, under what representation version and access contract the failure was
recorded, which feasibilities are known versus unknown, which derivability certificates were
minted under a frame that has since been edited, which costs are bracketed by intervals rather
than measured. Most systems carry this state untyped — a bag of booleans, labels, and cached
summaries — and consume it with generic machinery: optimize the known subgraph, trust the
summary, memorize the failure forever, probe whatever is most uncertain.

The ORION programme's position, developed across its N-lane closures (issues #674, #675,
#677), is that this state should be *typed* and *scoped*: feasibility beliefs conditioned on
interface type; failure receipts bound to the context coordinates they depend on; certificates
carrying per-hop transport obligations; verification directed by what the decision needs, not
by what is most unknown. The question this paper isolates is whether that structure is
load-bearing, i.e. whether an agent holding *exactly the same visible information* but
consuming it without the typing/scoping does measurably worse — and whether the typed variant
knows when it has nothing to add.

That second half matters as much as the first. A mechanism paper that only reports wins is
suspect under ORION discipline, which requires (i) *first right of refusal*: the strongest
donor-complete baseline is run on the same world and any tie or donor win is reported as such;
and (ii) *hostile controls*: each world contains a regime constructed so that the obvious
untyped shortcut is punished — and if the trap fails to bite, the run is declared invalid
rather than counted as a positive. This paper reports six families where the typed mechanism
won or tied exactly as prespecified, and two families where the honest answer was a negative
or a donor absorption, which we present with the same prominence.

Scope, stated up front and repeated in Section 12: every world is exact-synthetic and frozen;
"LLM proxy" arms are declared deterministic heuristics, not measurements of any real LLM; no
result grants novelty, P10, real-quantum, or deployment authority.

## 2. The shared experimental discipline

All six primary studies (N4-A, N4-B, N4-C, N4-D, N4-E, N4-F3; parent issue #677) and both
negatives (N1-C, issue #674; N2-F5B, issue #675 lineage) follow the same contract, documented
per-family under `development/orion-q-nlane-closure/`:

1. **Prospective freezing.** The protocol document — world generator, arms, endpoints, gates,
   tie-breaks, terminal vocabulary — is committed before any result-bearing execution
   (`N4_CLOSURE_ASSESSMENT.md`, "Execution order and freeze discipline"). The single
   post-freeze code deviation in the N4 lane (a `TypeError` repair in an N4-C sort tie-break,
   made before any N4-C outcome was observed) is disclosed verbatim in that assessment; no
   world, arm, endpoint, or gate was altered.
2. **Matched information.** Every non-oracle arm sees the identical serialized state — graph,
   costs, types, receipts, intervals, edit history, declared generator rates. Arms differ
   only in the rule applied to the same facts. Any advantage is therefore attributable to the
   mechanism, not to an information asymmetry.
3. **First right of refusal.** The strongest donor-complete baseline for each family is
   registered in advance (exact graph optimization, uniform-prior VOI planning, robust
   shortest path, matched-budget re-derivation, ideal VOI allocation, parametric
   model-selection) and its win or tie is a prespecified honest terminal, not a failure.
4. **Hostile controls with validity gates.** Each family contains a construction designed to
   trap the untyped alternative (a wasteful-reopening regime, max-entropy decoy facts, deep
   hash splices, a remint-unnecessary regime). Critically, the trap's *bite* is itself gated:
   if blind commitment is not punished (N4-A G4), if always-reopen is not punished in the
   wasteful regime (N4-B G3), if deep splices do not evade last-hop checking (N4-D G4), if
   decoys do not attract pure information gain (N4-E G5), or if the typed mechanism wins
   where it should have nothing to add (N4-F3 G4), the run terminates `*_WORLD_INVALID` and
   no positive may be claimed.
5. **Determinism.** Single frozen seed (20260821 across the lane), stdlib RNG, exhaustive
   enumeration in the decision path, no wall-clock input; each runner emits one canonical
   receipt line and is required to reproduce it byte-identically on a second run
   (`development/orion-q-nlane-closure/REPLAY_VERIFICATION_LEDGER.md`).
6. **Typed terminals and bounded authority.** Every receipt carries an authority string
   (e.g. `exact-synthetic-bounded; no real-quantum, no P10, no novelty, no LLM-capability
   claims`) and a claim boundary naming exactly which construction the result covers.

## 3. Study 1 (N4-A): typed-prior value of information under unknown feasibility

**Protocol:** `development/orion-q-nlane-closure/N4_A_UNKNOWN_VOI_PROTOCOL.md`.
**Receipt:** `research/extensions/orion-q/nlanes/N4_A_UNKNOWN_VOI_RESULTS.json`.

*World.* A layered interface DAG (4 layers of width 3, 81 s–t paths, exhaustively enumerated),
edge feasibility drawn per interface type (T0: 0.90, T1: 0.50, T2: 0.15), 55% of edges known,
the rest resolvable only by probes at cost 0.4; commit pays reward 20 on a feasible path and
an additional penalty 8 on failure; 300 paired episodes, seed 20260821. All non-oracle arms
see the graph, costs, types, known truths, and the generator's type-conditional rates as
declared typed facts.

*Mechanism.* `ORION_TYPED_VOI` runs myopic value-of-information probing whose priors on
unknown edges are the *type-conditioned* rates from typed interface provenance, with a
principled abstain. The isolation arm `PURE_VOI_UNIFORM` runs the *identical* VOI machinery
with a uniform 0.5 prior — the difference between the two arms is precisely the typing.

*Results.* Mean utility over the 300 paired episodes: `FULL_ORACLE` 4.612;
`ORION_TYPED_VOI` 3.291 (regret 1.321, 1.39 probes/episode); `PURE_VOI_UNIFORM` 2.180;
`GREEDY_KNOWN_GRAPH` 0.358; `LLM_PROXY_HEURISTIC` −12.306; `OPTIMIST_COMMIT` −13.619. The
typed arm recovers 71% of oracle utility; the donor-complete exact optimizer restricted to
the known subgraph abstains in 93.3% of episodes and captures almost none of the value. All
five gates passed; terminal `N4_A_TYPED_VOI_SUPPORTED__EXACT_SYNTHETIC`.

*What the hostile control traps.* `OPTIMIST_COMMIT` treats every unknown edge as feasible and
commits blind: it succeeds in only 19% of episodes and is punished to −13.619 mean utility —
and gate G4 makes that punishment a validity condition, so a world too easy to punish
optimism could never have produced this positive.

## 4. Study 2 (N4-B): scope-bound reopening of stale failure receipts

**Protocol:** `development/orion-q-nlane-closure/N4_B_STALE_RECEIPT_REOPENING_PROTOCOL.md`.
**Receipt:** `research/extensions/orion-q/nlanes/N4_B_STALE_RECEIPT_REOPENING_RESULTS.json`.

*World.* Edges carry failure receipts scoped to context coordinates (`REP` version, `ACCESS`
contract), alongside an irrelevant `NOISE` coordinate that flips frequently. A receipted edge
becomes potentially feasible only after the first change of a coordinate *inside its recorded
scope*. Two 200-episode regimes: `STALE_MATTERS` (scoped coordinates flip often; hoarding
failures is costly) and the hostile `REOPEN_WASTEFUL` (scoped coordinates almost never flip,
`NOISE` flips 60% of rounds; reopening is a trap).

*Mechanism.* `ORION_SCOPED_REOPEN` reopens a receipt iff a coordinate in its recorded scope
changed since the receipt. Controls: `NEVER_REOPEN`, `ALWAYS_REOPEN`, and the registered raw
failure-memory baseline `UNSCOPED_CHANGE_REOPEN`, which reopens everything when *any*
coordinate — including `NOISE` — changed.

*Results.* Pooled mean round utility: oracle 8.297; `ORION_SCOPED_REOPEN` 3.199;
`NEVER_REOPEN` 2.782; `UNSCOPED_CHANGE_REOPEN` −7.813; `ALWAYS_REOPEN` −9.225. Per regime,
with the prespecified no-giveback gate: in `STALE_MATTERS`, ORION 2.870 > NEVER 2.096 (ALWAYS
−5.044); in `REOPEN_WASTEFUL`, ORION 3.528 ≥ NEVER 3.468 while ALWAYS collapses. All four
gates passed; terminal `N4_B_SCOPED_REOPENING_SUPPORTED__EXACT_SYNTHETIC`.

*What the hostile control traps.* In `REOPEN_WASTEFUL`, `ALWAYS_REOPEN` is punished to
−13.406 versus `NEVER_REOPEN` at 3.468 (gate G3, a validity condition), and the unscoped
change-reopener — the same information, minus the scope binding — is dragged to −11.522 with
an 83.8% failure-attempt rate because the constantly flipping `NOISE` coordinate keeps
reopening receipts that are still valid. Scope binding, not change detection, is the
load-bearing ingredient.

## 5. Study 3 (N4-C): dominance-targeted verification under interval costs

**Protocol:** `development/orion-q-nlane-closure/N4_C_INTERVAL_PARETO_PROTOCOL.md`.
**Receipt:** `research/extensions/orion-q/nlanes/N4_C_INTERVAL_PARETO_RESULTS.json`.

*World.* Two objectives (cost, error bound) per edge, each known only as an interval — 30% of
edges wide, the rest tight; a per-episode scalarization weight visible to all arms; a hard
budget of B = 4 edge verifications, each revealing both true values; 400 paired episodes.
Mean interval-dominance survivor count 23.12 of 27 paths, so the world genuinely poses
ambiguous choices (non-degeneracy gate G4).

*Mechanism.* `ORION_INTERVAL_PARETO` computes the interval-dominance-surviving path set, ranks
edges by interval width × membership in surviving ambiguous paths (excluding edges shared by
all survivors), verifies the top-B, and optimizes with verified truths plus midpoints. The
isolation arm `RANDOM_VERIFY_MIDPOINT` spends the *same* budget on random edges, so the
difference is attributable purely to targeting.

*Results.* Mean scalarized regret against a clairvoyant Pareto oracle (exactly 0 by gate G1):
`ORION_INTERVAL_PARETO` 0.1096 with 76.5% zero-regret episodes; `RANDOM_VERIFY_MIDPOINT`
0.2518; `MIDPOINT_OPTIMIZER` 0.2621; `ROBUST_WORSTCASE` 0.7755; `BEST_CASE` 1.2679. Targeted
verification is 2.3× better than untargeted verification at the identical budget. All gates
passed; terminal `N4_C_TARGETED_INTERVAL_PARETO_SUPPORTED__EXACT_SYNTHETIC`.

*What the controls trap.* The endpoint optimizers embody the untyped shortcuts: optimism
(`BEST_CASE`, regret 1.2679) and blanket pessimism (`ROBUST_WORSTCASE`, 0.7755) are both
several times worse than acknowledging the ambiguity structure — and random verification
shows that verification *volume* without dominance targeting recovers less than half of the
mechanism's improvement.

## 6. Study 4 (N4-D): full-chain transport verification against oracle laundering

**Protocol:** `development/orion-q-nlane-closure/N4_D_LAUNDERING_DETECTION_PROTOCOL.md`.
**Receipt:** `research/extensions/orion-q/nlanes/N4_D_LAUNDERING_DETECTION_RESULTS.json`.

*World.* 400 remint/edit chains (length 2–6) transporting an interface node to a target
label under a declared oracle-tier budget `T_max`. 200 chains are honest; 200 launder a
stronger oracle while the final label *always* matches the target: 66 `MISSING_RECEIPT`
(an interior hop with no receipt), 66 `SPOOFED_SUMMARY` (a hop that truly exceeded the tier
budget while the visible summary reports the minimum over hops), 68 `DEEP_SPLICE` (every
individual hop tier-legal, but an interior `input_hash` breaks the chain — a substituted
artifact whose true provenance required a stronger oracle, locally consistent at the last
hop). All checkers receive the identical serialized chain.

*Mechanism.* `ORION_CHAIN_TRANSPORT` walks the full chain: every hop must carry a receipt,
every `output_hash(k−1)` must equal `input_hash(k)`, and the recomputed maximum `tier_used`
must respect `T_max`; otherwise it returns the typed `CANNOT_ACCEPT`, never a silent accept.

*Results.* `ORION_CHAIN_TRANSPORT`: recall 1.000 on *every* laundering class — including all
68 deep splices — with false-positive rate 0.000 on honest transports (the mandatory hard
gate G1: any single miss or false rejection would have failed the family). The graded
alternatives on the same inputs: `LABEL_MATCH` recall 0.000; `SUMMARY_TIER` recall 0.000;
`LAST_HOP_CHECK` recall 0.085 overall and 0.000 on `DEEP_SPLICE`. Terminal
`N4_D_CHAIN_TRANSPORT_LAUNDERING_DETECTION_SUPPORTED__EXACT_SYNTHETIC`.

*What the hostile control traps.* The deep-splice class exists precisely to trap partial
typing: a checker that verifies the last hop's receipt — hash consistency, tier bound, and
all — still accepts 100% of deep splices (gate G4 requires this evasion; had last-hop
checking caught splices, the construction would have been declared invalid). Only walking the
whole typed chain closes the class. The claim boundary is explicit: completeness holds only
in this world, where per-hop receipts cannot be forged consistently end-to-end; hashes are
seeded integers, and no cryptographic or real-adversary claim is made.

## 7. Study 5 (N4-E): decision-coupled experiment selection versus pure information gain

**Protocol:** `development/orion-q-nlane-closure/N4_E_ACTIVE_EXPERIMENTS_PROTOCOL.md`.
**Receipt:** `research/extensions/orion-q/nlanes/N4_E_ACTIVE_EXPERIMENTS_RESULTS.json`.

*World.* Six unknown binary construction facts with typed priors and heterogeneous probe
costs; eight candidate plans whose feasibility clauses mention only the four *load-bearing*
facts; two *decoy* facts with near-maximal entropy (p ≈ 0.5) that appear in no clause; 400
paired episodes; exact enumeration of all residual fact assignments (no sampling). Crucially,
all probing arms share the *same stopping rule* (stop when no remaining probe has positive
myopic net decision value), so the arms differ only in which fact they probe next.

*Mechanism.* `ORION_DECISION_VOI` probes the fact maximizing expected decision-utility
improvement per unit cost. `INFOGAIN` — pure active learning — probes the maximal-entropy
fact, cost- and decision-blind.

*Results.* Mean net utility: oracle 12.054; `ORION_DECISION_VOI` 9.266 (2.71 probes/episode,
decoy probe fraction 0.000); `LLM_PROXY_HEURISTIC` 8.989; `CHEAPEST_FIRST` 8.075;
`RANDOM_ORDER` 7.568; `INFOGAIN` 7.121. Every arm reaches commit accuracy 1.0 under the
shared stopping rule, so the entire spread is probe-spend efficiency — i.e., pure
next-experiment selection quality. All gates passed; terminal
`N4_E_DECISION_COUPLED_SELECTION_SUPPORTED__EXACT_SYNTHETIC`.

*What the hostile control traps.* The max-entropy decoys attract pure information gain
exactly as designed: `INFOGAIN` spends 36.6% of its probes (decoy fraction 0.36588) on facts
no decision depends on, versus 0.000 for the decision-coupled selector — and gate G5 makes
the decoys' attractiveness a validity condition (had `INFOGAIN` not been measurably drawn to
them, the control would have been declared invalid). "Most uncertain" and "most
decision-relevant" are different types, and conflating them costs 2.15 utility per episode
here.

## 8. Study 6 (N4-F3): typed remint/transport across representation edits

**Protocol:** `development/orion-q-nlane-closure/N4_F3_REMINT_TRANSPORT_PROTOCOL.md`.
**Receipt:** `research/extensions/orion-q/nlanes/N4_F3_REMINT_TRANSPORT_RESULTS.json`.

This study closes residual 1 of `development/orion-q-nlane-closure/N4_CLOSURE_ASSESSMENT.md`:
family 3 (representation remints requiring transport/reverification) had been exercised only
as N4-D's laundering vector, never independently.

*World.* Every edge starts with a derivability receipt minted under frame F0, carrying an
obligation binding over frame aspects; two sequential frame edits per episode; a registered
typed transport-rule table (aspect × edge-type); a hard remint budget B = 6 shared by all
budgeted arms; a shared certification policy (identical code path for all three non-oracle
arms) that commits only fully certified paths. Three 200-episode regimes: `MIXED_TRANSPORT`
(a material fraction of receipts transports), `STALE_HOSTILE` (bindings broad, edits broad,
p_break = 0.85 — carry-forward keeps stale validity), and `REMINT_UNNECESSARY` (both edits
touch only the never-bindable `COSMETIC` aspect — typed transport has nothing to add).

*Mechanism.* `ORION_TYPED_TRANSPORT` applies the typed transport relation sequentially and
binding-preservingly; non-transportable receipts are marked INVALID (typed invalidation,
never silent carry-forward); the budget is spent only on invalidated edges. Baselines:
`RE_DERIVE_SCRATCH` (first right of refusal: discard all receipts, same budget, same policy)
and `NAIVE_CARRY_FORWARD` (treat every pre-edit receipt as valid).

*Results.* `MIXED_TRANSPORT`: ORION 9.421 > `RE_DERIVE_SCRATCH` 7.157 > `NAIVE_CARRY_FORWARD`
−7.821 (failure rate 0.695); oracle 9.728. Pooled: ORION 7.286 (regret 0.188) vs re-derive
6.439 (regret 1.034) vs naive −3.976. Soundness gate G5: over all 14,400 receipts checked,
ORION's valid/invalid classification matched ground-truth transportability with **zero**
mismatches and it committed **zero** infeasible paths. All five gates passed; terminal
`N4_F3_TYPED_REMINT_TRANSPORT_SUPPORTED__EXACT_SYNTHETIC`.

*What the two hostile controls trap.* In `STALE_HOSTILE`, naive carry-forward fails on 99.5%
of its commits and is punished to −15.916 mean utility, while both invalidating arms stay
non-negative (gate G3, a validity condition). In `REMINT_UNNECESSARY`, the first-refusal gate
G4 demanded that re-derivation win or tie — and the receipt shows an *exact four-way tie*:
`FULL_ORACLE`, `NAIVE_CARRY_FORWARD`, `ORION_TYPED_TRANSPORT`, and `RE_DERIVE_SCRATCH` all at
mean utility 11.809659685355605, with ORION spending zero remints. Where the mechanism has
nothing to add, it adds exactly nothing — any strict ORION advantage in that regime would
have invalidated the run by construction.

## 9. Synthesis: the pattern across six families

Across all six families the same two-sided pattern holds, and each side was prespecified as a
gate rather than observed post hoc.

**Side one: the typed/scoped variant wins or ties exactly against matched information.**
Typing the VOI prior is worth 3.291 vs 2.180 against the identical planner with the typing
removed (N4-A); binding receipts to scope is worth 3.199 vs −7.813 pooled against the same
reopening trigger without the scope (N4-B); targeting the verification budget by interval
dominance is worth 0.1096 vs 0.2518 regret at identical budget (N4-C); walking the full typed
chain is worth recall 1.000/FPR 0.000 vs 0.085 recall for the strongest partial checker
(N4-D); coupling probe choice to the decision is worth 9.266 vs 7.121 under a shared stopping
rule (N4-E); typed invalidation-plus-transport is worth 9.421 vs 7.157 at matched budget
where transport exists, and ties re-derivation to the last float — 11.809659685355605 on both
sides — where it does not (N4-F3).

**Side two: every untyped shortcut is punished by a designed-in trap, and the trap's bite is
itself receipt-verified.** Stated verbatim from the receipts:

- N4-A (`N4_A_UNKNOWN_VOI_RESULTS.json`): `OPTIMIST_COMMIT` mean utility −13.618992761055088
  at success rate 0.19; the declared LLM-proxy heuristic −12.306255589204312. Blind optimism
  about unknown feasibility is the single worst policy in the world built to test it.
- N4-B (`N4_B_STALE_RECEIPT_REOPENING_RESULTS.json`): in `REOPEN_WASTEFUL`, `ALWAYS_REOPEN`
  −13.40591619308622 vs `NEVER_REOPEN` 3.4681864758055134; `UNSCOPED_CHANGE_REOPEN`
  −11.52194977365361 with failure-attempt rate 0.8378839590443686 — unscoped change
  detection is nearly as bad as ignoring receipts entirely.
- N4-C (`N4_C_INTERVAL_PARETO_RESULTS.json`): `BEST_CASE` mean regret 1.267879405372331 and
  `ROBUST_WORSTCASE` 0.7754808759417671 vs targeted 0.10962008492273609 — endpoint optimism
  and blanket pessimism both lose to typed ambiguity handling.
- N4-D (`N4_D_LAUNDERING_DETECTION_RESULTS.json`): `LABEL_MATCH` recall 0.0; `SUMMARY_TIER`
  recall 0.0; `LAST_HOP_CHECK` per-class recall on `DEEP_SPLICE` 0.0 (0.085 overall) —
  every partial-inspection shortcut has a laundering class it cannot see.
- N4-E (`N4_E_ACTIVE_EXPERIMENTS_RESULTS.json`): `INFOGAIN` decoy probe fraction
  0.36587677725118484 vs 0.0 for the decision-coupled selector; utility 7.120762030763817 vs
  9.266267332447027 — the max-entropy decoys trap pure information gain at a 0.366 decoy
  fraction, exactly as gate G5 required.
- N4-F3 (`N4_F3_REMINT_TRANSPORT_RESULTS.json`): `NAIVE_CARRY_FORWARD` failure rate 0.995
  and mean utility −15.91596535801731 in `STALE_HOSTILE`; and the `REMINT_UNNECESSARY`
  four-way exact tie at 11.809659685355605 shows the mechanism claims nothing where nothing
  is available.

The N4 closure assessment (`development/orion-q-nlane-closure/N4_CLOSURE_ASSESSMENT.md`)
draws the lane-level conclusion we adopt here: the executed evidence does *not* support
extending the classical fully-known-graph negative (`FULLY_KNOWN_GRAPH_CLASSICALLY_CLOSED`,
the retained H0 boundary of issue #677) to the partial-information setting — on these
constructions, typed/scoped epistemic state is the load-bearing mechanism.

## 10. Two honest negatives: the methodology does not manufacture positives

The discipline's credibility rests on what it refuses to claim. Two families in this
package's scope terminated with the donor ahead or level, and both are reported as
first-class results.

**N1-C: the typed failure *state* is valuable; the allocation *policy* is donor-closed.**
Protocol `development/orion-q-nlane-closure/N1_C_PROTOCOL.md`; receipt
`research/extensions/orion-q/nlanes/N1_C_COSTLY_VERIFICATION_RESULTS.json`. Under a binding
verifier budget (40 candidates, budget 6, 20,000 held-out episodes), the typed/scoped arm —
which distinguishes fresh, current-context-failed, and stale-failed candidates — beats the
same learner with the scoping ablated by a paired solve-rate delta of +0.0271 (bootstrap 95%
CI [0.0248, 0.02955]; gate G4), and eliminates false escalations (0.0 vs 0.6959). But the
prespecified donor — an ideal value-of-information allocator given the *same typed facts* —
matches the typed arm *exactly*: paired delta 0.0 with bootstrap CI [0.0, 0.0], identical
solve rate 0.9866, identical verification counts (gate G5). The frozen terminal says both
things at once: `N1C_TYPED_FAILURE_STATE_VALUE__VOI_POLICY_PARENT_SUFFICIENT`. The bounded
positive is for typed scoped failure state *as decision information*; the policy claim is
closed by the donor and is not made.

**N2-F5B: the crossover-prediction residual is donor-absorbed on its original world.**
Protocol `development/orion-q-nlane-closure/N2_F5B_DONOR_COMPARISON_PROTOCOL.md`; receipt
`research/extensions/orion-q/nlanes/N2_F5B_DONOR_COMPARISON_RESULTS.json`. The earlier F5
residual (typed analytic crossover prediction) was granted no standing value until a
Predict-and-Conquer-style model-selection donor got first right of refusal — deliberately
given *more* fitting budget than the candidate. On the original world the donor ties the
candidate exactly (PRIMARY 0.9948 both; gate G3 donor sufficiency holds), so the original
claim is donor-absorbed. Only on the additionally frozen misspecified world — true forms
outside both libraries — does the candidate stay ahead (0.9844 vs 0.9531; crossover-distance
relative error 0.084 vs 0.441), yielding the mixed terminal
`N2_F5B_MIXED__CANDIDATE_AHEAD_ON_MISSPECIFIED_ONLY__EXACT_SYNTHETIC_ONLY`. What survives is
a misspecification-robustness edge on one frozen world pair — nothing more, and the receipt's
own claim boundary says so.

Both negatives were reachable because the terminals were frozen before outcomes; the same
machinery that certified the six positives certified these refusals.

## 11. Limitations

1. **Exact-synthetic worlds only.** Every world is a frozen construction with enumerable
   ground truth. This is what makes the mechanism isolation exact — matched information,
   paired episodes, oracle references — and also what bounds the claim: no receipt grants
   authority over real interface graphs, real representation migrations, or real research
   pipelines. Each receipt's `claim_boundary` field restates this per family.
2. **LLM baselines are declared proxies.** The `LLM_PROXY_HEURISTIC` arms in N4-A and N4-E
   are fixed deterministic heuristics, declared in the frozen protocols as *not* claims
   about any real LLM. The registered "generic LLM with same state/tools" baseline was not
   executed with a real model (residual 2 of `N4_CLOSURE_ASSESSMENT.md`).
3. **Residuals from the closure assessment**, carried forward honestly: no lower bound or
   impossibility theorem exists for any family (residual 4); the registered "P10 interface
   edit only after a certified residual" baseline rung was not executed (residual 3); N4-B
   excludes intra-episode receipt accrual (residual 5, a recorded scope limit in the receipt
   itself). Residual 1 — family 3 exercised only as N4-D's laundering vector — has since
   been closed standalone by N4-F3, in the positive direction, and is no longer open.
4. **Construction-level soundness assumptions.** N4-D's completeness holds only where
   per-hop receipts cannot be forged consistently end-to-end (hashes are seeded integers,
   not cryptographic digests); N4-F3's transport rules are sound by construction, and
   remints consume budget rather than utility — all recorded as scope limits in the
   respective receipts.
5. **Scalarized regret in N4-C** is not full Pareto-front hypervolume (recorded scope
   limit), and N1-C is a diagnostic with its own authority string
   (`N1C_DIAGNOSTIC__NO_P10_AUTHORITY__NO_NOVELTY_AUTHORITY__EXACT_SYNTHETIC_ONLY`).

## 12. The package as a reusable benchmark suite

Because every world is deterministic, exhaustively enumerable, and frozen by protocol, the
six studies are directly reusable as a benchmark suite for partial-knowledge research-state
mechanisms. A candidate mechanism can be dropped into any family as a new arm and scored
against the committed receipts without re-deriving anything: the worlds
(`research/extensions/orion-q/nlanes/n4_a_unknown_voi.py` through
`n4_f3_remint_transport.py`, plus `n1c_costly_verification_voi.py` and
`n2_f5b_donor_comparison.py`) regenerate byte-identically from seed 20260821; the gates —
including the hostile-control validity gates — are frozen in the protocol documents; and the
terminal vocabularies distinguish "mechanism loses" from "world invalid", so a new arm cannot
win by breaking the trap. The suite spans six distinct state types (unknown feasibility,
scoped failure receipts, interval costs, transported certificates, decision-coupled probes,
reminted receipts), each with a matched-information strong baseline holding first right of
refusal and at least one designed-in trap with receipt-verified bite.

## 13. Reproducibility

- **Frozen protocols:** all under `development/orion-q-nlane-closure/` (N4_A through N4_E,
  N4_F3, N1_C, N2_F5B), each dated 2026-08-21 and frozen before its result-bearing run.
- **Receipts:** all under `research/extensions/orion-q/nlanes/`, one canonical JSON per
  family, schema-tagged (`ORIONQ.N4A...v1` etc.), seed 20260821 throughout.
- **Independent replay:** `development/orion-q-nlane-closure/REPLAY_VERIFICATION_LEDGER.md`
  records 17/17 N-lane receipts replayed deterministically (Python 3.11.15, NumPy 2.4.6):
  every runner re-executed, its stdout receipt line canonically equal to the committed
  results file, and every in-place RESULTS rewrite byte-identical (clean `git status`).
  N4-F3 postdates that ledger's 17 rows; during preparation of this manuscript
  (2026-08-21) its runner was replayed twice fresh: both runs exited 0, produced
  byte-identical stdout, the receipt line was canonically equal to the committed
  `N4_F3_REMINT_TRANSPORT_RESULTS.json`, and the in-place rewrite left the git tree clean —
  the same pass criterion as the ledger's method.
- **Disclosure:** the single post-freeze code deviation (N4-C tie-break type repair, before
  any outcome was observed) is logged in `N4_CLOSURE_ASSESSMENT.md`.

## 14. Claim boundary

This paper claims, within exact-synthetic scope only: (i) on the six frozen constructions,
typed/scoped epistemic state strictly improved on every registered matched-information
baseline that did not itself embody the typing, and exactly tied the strongest baseline
wherever the typing had nothing to add — with all first-refusal and hostile-control gates
passing as prespecified; (ii) the two negative/absorbed families are correctly bounded
(N1-C's policy is VOI-donor-closed; N2-F5B's original claim is donor-absorbed, surviving
only under misspecification); (iii) the suite replays deterministically. This paper does not
claim: any property of real research pipelines, real interface graphs, real representation
migrations, or real adversaries; any LLM capability or incapability; any cryptographic
security; any lower bound or impossibility; any novelty beyond what the frozen hostile
protocols themselves establish; any P10 or real-quantum authority. Per the frozen plan, this
is a mechanism-isolation study, not a deployment claim
(`papers/Q-paper-02-recursive-recovery/PUBLICATION_PLAN.md`, Paper Q4).

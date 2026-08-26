# Typed and Scoped Partial-Knowledge State for Research Decisions

**ORION-ORION-04 Manuscript V3 — donor-synchronized publication draft**  
Scientific cut: `main@ca7df1055a43f97eaf8d142a62011c4c261af368`  
Claim authority: `CLAIM_LEDGER.md`, `PUBLICATION_FOUNDATION_V2.md`  
Parity/artifact contract: `INFORMATION_PARITY_AND_ARTIFACT_MAP_V2.md`

## Abstract

Research agents act not only on facts about the world but on partial knowledge about those facts: which unknowns belong to which interface class, which failure records remain applicable, which uncertainties can change a decision, and which certificates survive representation changes. We test a bounded mechanism question: **when competing methods receive the same underlying serialized information, can explicit type and scope change the downstream decision?** Across six prospectively frozen exact-synthetic studies, we isolate unknown-feasibility probing, failure-receipt reopening, interval verification, evidence transport, next-experiment selection and representation reminting. Typed-prior value-of-information probing reaches mean utility 3.291 versus 2.180 for the identical planner with a flattened prior; scope-bound failure reopening reaches 3.199 pooled utility while unscoped change reopening falls to -7.813; decision-boundary-targeted verification reduces scalarized regret to 0.1096 versus 0.2518 for random verification at the same budget; full-chain transport checking detects all 200 registered laundering chains at zero false positives in the frozen synthetic model; decision-coupled experiment selection reaches utility 9.266 versus 7.121 for pure information gain while avoiding registered entropy decoys; and typed remint/transport reaches 9.421 in the mixed-transport regime versus 7.157 for matched re-derivation while tying exactly when reminting is unnecessary. Two first-right-of-refusal negatives bound the claim: an ideal VOI donor closes the allocation-policy residual in a separate typed-failure-state study, and a model-selection donor absorbs the original crossover-prediction residual. We explicitly subtract current prior art: STALE studies agent-memory invalidation, ContextNest studies governed/versioned/provenanced context, and value-of-information/provenance methods are established donors. Our narrower result is exact-synthetic **mechanism isolation at matched information**: in registered worlds where a downstream responsibility depends on a distinction carried by type/scope, erasing that distinction changes the decision. No result establishes real-agent safety, scientific productivity, cryptographic security or deployment performance.

## 1. Introduction

A long-running research process accumulates more than observations. It accumulates state about its own knowledge: an interface is unknown but belongs to a particular class; a prior attempt failed under a named representation and access contract; a cost is an interval rather than a point; a certificate was transported through multiple edits; or a representation changed after a failure/certificate was recorded.

Many underlying ingredients are mature. Value-of-information methods ask which measurement is worth purchasing. Database and workflow provenance track how results were derived. Agent memory systems increasingly detect and revise stale state. Context-governance systems track versions, provenance, selectors and artifact identity. ORION-04 does not claim any of these primitives as new.

Two current donors are especially important.

**STALE** asks whether an agent can recognize that remembered state is no longer valid after later evidence creates an implicit conflict, and whether that revision propagates into downstream behavior. That is a genuine *memory invalidation* problem.

**ContextNest** instead treats provenance, version identity and deterministic context selection as governance infrastructure beneath retrieval. A relevant artifact can be stale, unapproved or impossible to reconstruct even when retrieval itself works.

ORION-04 studies a narrower object than either. We assume the compared non-oracle policies receive the same serialized facts and ask whether explicit **type/scope fields change a registered downstream responsibility**. In N4-B, for example, the old failure need not become false because later evidence contradicts it; it becomes potentially inapplicable because one of the exact context coordinates on which that receipt depended changed. We call this **scope invalidation**, not stale-memory detection.

The same distinction recurs across the other worlds. A high-entropy unknown can be decision-irrelevant. A certificate can be locally valid yet unsupported as a full chain. An interval can be large yet unable to change the preferred option. A representation edit can invalidate one receipt while leaving another transportable.

Our thesis is therefore not “typed state is good.” It is:

> **A partial-knowledge state is useful only relative to the responsibility that consumes it; at matched visible information, erasing the responsibility-relevant type/scope can change the decision.**

This is tested through six exact-synthetic mechanism worlds with prospectively frozen protocols, matched-information controls, strongest-donor first right of refusal and hostile validity regimes.

## 2. Common experimental contract

### 2.1 Matched visible information

For every primary comparison, all non-oracle arms receive the same serialized world facts. The paper does not give the candidate privileged hidden evidence. Instead the candidate and control consume the same information differently.

Examples:
- N4-A: same graph/unknown edges/type labels/rates; the isolation changes how type-conditioned priors are used;
- N4-B: same failure receipt and observed coordinate changes; the isolation removes the receipt's dependency scope;
- N4-C: same intervals/verification budget; the isolation changes which uncertainty is considered decision-relevant;
- N4-D: same serialized transport chain; the isolation changes whether support is checked over the whole chain or only a local summary/hop;
- N4-E: same unknowns/entropy; the isolation changes whether probes are scored for decision impact;
- N4-F3: same edit history/receipts; the isolation changes whether typed invalidation governs reuse/remint.

The reviewer-facing parity map is stored in `INFORMATION_PARITY_AND_ARTIFACT_MAP_V2.md`. Final submission should convert it to a machine-readable manifest.

### 2.2 First right of refusal

Each study registers strong alternatives before outcome access. A donor tie or win is an admissible endpoint. The candidate does not receive novelty credit for a policy or rule already closed by a stronger donor given the same facts.

### 2.3 Hostile validity regimes

Each positive world contains a construction designed to punish a specific shortcut. If the hostile control does not bite, the protocol declares the world invalid rather than counting a candidate advantage. This is how the study separates “candidate did well” from “the intended mechanism was actually exercised.”

### 2.4 Evidence class

The worlds are deterministic exact-synthetic stress tests. Episode counts are generated units under named frozen generators, not samples from a population of real scientific domains. Replay establishes determinism, not independent scientific replication.

## 3. Typed priors: which unknown is worth probing?

N4-A uses a layered interface graph where unknown edge feasibility depends on an exposed interface type. The candidate and isolation control use the same myopic VOI planner; the difference is whether the frozen type-conditioned rates are retained or flattened to a uniform prior.

Across 300 paired generated episodes, full-oracle mean utility is 4.612. `ORION_TYPED_VOI` reaches 3.291 with 1.39 probes/episode, versus 2.180 for the identical uniform-prior planner and 0.358 for exact optimization restricted to the known subgraph. Blind optimistic commitment is punished to -13.619, satisfying the hostile validity condition.

The result does not say an agent can learn the correct type in the wild. The type/rate facts are supplied by the frozen world. The result says that **given those same visible facts**, flattening the registered type distinction changes the value assigned to unknowns and reduces utility in this construction.

## 4. Scope invalidation: when does an old failure still apply?

N4-B stores a failure receipt together with the exact context coordinates it depends on. The world also contains an irrelevant `NOISE` coordinate that changes frequently. A receipted failure becomes potentially stale only when a coordinate *inside its recorded scope* changes.

This is not the same problem as STALE-style memory invalidation. No new observation semantically contradicts the old failure. The question is whether the **conditions under which the failure was established still match the current task state**.

Policies include `ORION_SCOPED_REOPEN`, `NEVER_REOPEN`, `ALWAYS_REOPEN` and `UNSCOPED_CHANGE_REOPEN`, which reopens after any coordinate change including `NOISE`.

Pooled mean utility is 3.199 for scope-bound reopening, 2.782 for never reopen, -7.813 for unscoped reopening and -9.225 for always reopen. In `STALE_MATTERS`, scope-bound reopening reaches 2.870 versus 2.096 for never reopen. In `REOPEN_WASTEFUL`, scope-bound reopening remains 3.528 versus 3.468 for never reopen, while always reopen falls to -13.406 and unscoped reopening to -11.522.

Thus a change event is not automatically a revocation event. The receipt needs an explicit dependency scope if the downstream responsibility is “does this old failure still apply?”

## 5. Interval verification: which uncertainty can change the choice?

N4-C gives every arm the same interval-valued cost/error state and the same budget of four exact edge verifications. The candidate identifies interval-dominance-surviving paths and prioritizes uncertainty that participates in unresolved comparisons among them; a matched control spends the same verification budget randomly.

Across 400 paired generated episodes, mean scalarized regret is 0.1096 for targeted verification and 0.2518 for random verification. The ratio is 2.3×, but the absolute regrets are the primary effect statement. Midpoint optimization yields 0.2621, robust worst-case 0.7755 and best-case 1.2679. The candidate has zero regret in 76.5% of episodes.

The result is not a universal active-learning theorem. It isolates a representation/decision relationship: **uncertainty matters when it can change the decision boundary, not merely when its interval is wide.**

## 6. Transport: local validity is not chain authority

N4-D contains 200 honest and 200 hostile transport chains in a constructed finite battery. Hostile classes include missing interior receipts, spoofed summary tiers and deep splices whose final hop looks locally legal while an interior input/output identity breaks the chain.

All checkers receive the same serialized chains. Full-chain checking detects all 200 registered hostile chains and rejects none of the 200 honest chains in this model. Label matching and summary-tier checking have zero recall; last-hop checking reaches 0.085 overall and zero on all 68 deep splices.

This is not a cryptographic/security guarantee against real adversaries. The synthetic model assumes the checker receives the declared receipt objects. The conclusion is structural: **authority to reuse/transport a result can depend on the support path, not only on the last local label.**

## 7. Experiment selection: entropy and decision relevance differ

N4-E uses a shared stopping/commit rule and adds high-entropy decoy facts that cannot change the decision. Pure information gain is therefore tempted by uncertainty that is scientifically irrelevant to the registered responsibility.

Decision-coupled probing reaches mean utility 9.266, compared with 7.121 for pure information gain, 8.075 for cheapest-first, 7.568 random and 8.989 for the declared deterministic LLM-proxy heuristic. All arms reach final commit accuracy 1.0; the difference is experiment-selection efficiency. Pure information gain spends 36.6% of probes on decoys while the decision-coupled selector spends zero.

Again the claim is bounded: this world demonstrates that information value and decision value can diverge even under identical visible uncertainty.

## 8. Representation edits: reuse, remint or re-derive?

N4-F3 studies whether receipts remain transportable across representation edits. A typed invalidation rule decides which state can be reused or reminted. Controls include matched-budget re-derivation and naive carry-forward.

In `MIXED_TRANSPORT`, typed remint/transport reaches 9.421 versus 7.157 for matched re-derivation and -7.821 for naive carry-forward. Pooled values are 7.286, 6.439 and -3.976 respectively, with zero registered invalidation mismatches across 14,400 receipts.

The first-right-of-refusal control is decisive: in `REMINT_UNNECESSARY`, all four arms tie exactly at 11.809659685355605 and the candidate spends zero remints. The paper therefore does not claim that typed reminting always helps; its value is conditional on the state distinction actually being needed.

## 9. Two negative/donor outcomes

### 9.1 Typed failure state without allocation-policy novelty

N1-C gives the typed state a bounded solve-rate advantage over an unscoped ablation (+0.0271 paired, bootstrap 95% interval `[0.0248,0.02955]`) and removes false escalation. But an ideal VOI donor given the same typed facts **exactly matches the candidate allocation policy** at solve rate 0.9866. The allowed claim is state-value, not policy novelty.

### 9.2 Crossover predictor absorbed on the original world

N2-F5B compares a candidate predictor with a model-selection donor. They tie at 0.9948 in the original world. The candidate retains only a bounded misspecification-robustness edge in a separately frozen misspecified world. The original residual is therefore donor-absorbed.

These negatives are central because they show that the methodology can return “donor sufficient” rather than forcing every study into a typed-state win.

## 10. Relation to provenance/context governance and ORION-23

ORION-04 assumes that relevant context can be identified, serialized and compared under exact synthetic rules. **ContextNest** and database/workflow provenance research own substantial infrastructure for version identity, provenance, deterministic selection and reconstructable history. ORION-04 does not replace that layer.

Its question sits downstream:

> **once trustworthy state is available, which distinctions in that state are required by the next responsibility?**

The paper is also narrower than ORION ORION-23. ORION-23 develops a general theory/contract of **responsibility-scoped sufficiency and recovery**. ORION-04 supplies bounded exact-synthetic mechanism-isolation evidence for several decisions that motivate such a theory. ORION-04 therefore does not claim the general principle “sufficiency is responsibility-scoped” as its unique theoretical novelty; it provides controlled experimental support/examples for specific responsibility/state distinctions.

## 11. Cross-study synthesis

The six primary worlds use different algorithms but share the same logic.

| Downstream responsibility | Required state distinction | Matched shortcut that fails in the frozen world |
|---|---|---|
| choose which unknown to probe | interface/type-conditioned feasibility | flatten all unknowns to one prior |
| decide whether old failure still applies | dependency scope | reopen on any change / never reopen |
| spend verification budget | uncertainty that can change choice | verify arbitrary/high-width uncertainty |
| accept transported evidence | full-chain support/continuity | trust final label/summary/last hop |
| choose next experiment | decision relevance | maximize entropy alone |
| reuse state after representation edit | transport/invalidation type | rederive everything or carry everything forward |

The commonality is not a universal type system. It is a design criterion: **the state representation should retain exactly the distinctions needed by the downstream responsibility, while first-right-of-refusal controls test whether a simpler donor already suffices.**

## 12. Reproducibility and statistical reporting

Every primary world is generated from a frozen protocol and deterministic code. The final package should bind one machine-readable manifest per study with:

- generator/seed;
- exact serialized information visible to each arm;
- policy difference;
- independent generated unit/episode count;
- hostile-control gate;
- source result digest;
- replay command.

Do not pool all episodes/chains across the six worlds into one p value or meta-effect. They are different constructed mechanisms with different outcomes/scales. For N4-D, 200 hostile/200 honest chains are an exact finite battery rather than IID draws from a real adversary population. For N1-C, the registered paired bootstrap interval must preserve the protocol's actual independent unit.

The repository is publicly inspectable. A final article may describe code/data as open/reusable only after an authorized licence and permanent archive are actually established.

## 13. Limitations

**Exact-synthetic worlds.** No primary result is a real-agent, real-laboratory or deployment study.

**Rules/types are supplied.** The experiments generally assume the relevant type/scope facts are present in the state. They do not show that an agent can learn correct responsibility types automatically.

**Current donors are broad.** STALE, ContextNest, VOI, active learning and provenance already own major primitives. ORION-04's residual is the controlled matched-information mechanism evidence.

**Constructed hostile regimes.** Hostile controls are intentionally designed to exercise the target distinction; they are not prevalence estimates.

**No cryptographic claim.** Hash/receipt objects in N4-D are synthetic provenance mechanisms, not proof of security against real attackers.

**ORION-23 ownership.** General responsibility-scoped sufficiency/recovery theory belongs to ORION-23; ORION-04 is bounded empirical/mechanism evidence.

**No single universal mechanism.** The six worlds need different type/scope coordinates because the downstream responsibilities differ.

## 14. Discussion

A useful state representation is not defined only by how much information it stores. It is defined by which distinctions survive long enough to matter for the next decision.

ORION-04's strongest examples are cases where a superficially reasonable scalarization loses that structure. “Changed” is weaker than “a coordinate inside the receipt's dependency scope changed.” “Uncertain” is weaker than “uncertainty can reverse the decision.” “Last hop valid” is weaker than “the full support chain remains valid.” “High entropy” is weaker than “worth probing for the current choice.”

This interpretation complements rather than competes with current agent-memory and context-governance work. Those systems help maintain trustworthy, current state. ORION-04 tests the next layer: **how the responsibility consuming that state determines which distinctions must remain explicit.**

The first-right-of-refusal negatives matter just as much. When an ideal VOI donor already has the typed facts, the candidate allocation policy earns no novelty. When model selection closes an original prediction residual, the paper retains the donor tie. This is evidence that the experimental discipline is capable of subtracting mechanisms rather than only accumulating wins.

## 15. Conclusion

Across six frozen exact-synthetic research-decision worlds, explicit type/scope is load-bearing precisely when the registered downstream responsibility depends on a distinction that a matched shortcut erases. The result is not a new generic memory, provenance, VOI or active-learning method. It is a bounded mechanism finding about **state consumption under matched information**, with donor ties and hostile controls preserved as first-class evidence.

The practical lesson is correspondingly narrow: before compressing a research state into one confidence, validity flag, relevance score or “changed/not changed” bit, ask which responsibility must consume it next—and whether the discarded distinction can change that decision.

# Typed Epistemic State for Scientific Decisions under Partial Knowledge

**Manuscript V2 — 2026-08-22.** This version reframes the existing exact-synthetic studies against the 2026 typed-memory, stale-memory, provenance and value-of-information literature. No real-domain validation is claimed; `TOP_TIER_UPGRADE_PROTOCOL_2026-08-22.md` registers the study needed for that upgrade.

---

## Abstract

Persistent agents increasingly use structured memory, provenance, temporal revision and value-of-information mechanisms. We study a narrower question relevant to scientific workflows: **when two decision systems receive the same visible partial information, does explicitly representing the epistemic role, applicability scope, provenance, uncertainty and decision relevance of that information change the resulting research decision?**

We report six prospectively frozen exact-synthetic studies in which a typed/scoped mechanism is compared with matched-information baselines and strong donor methods given first right of refusal. The studies isolate different research-state operations. Type-conditioned value-of-information probing recovers 71% of oracle utility and outperforms an otherwise identical uniform-prior planner. Scope-bound reopening of failure receipts beats never/always/unscoped reopening in a two-regime world where irrelevant context changes deliberately trap unscoped policies. Pareto-ambiguity-targeted verification reduces scalarized regret by 2.3x relative to random verification at the same budget. Full-chain evidence transport detects every registered laundering chain, including deep splices invisible to last-hop checking, while producing zero false positives on the frozen honest set. Decision-coupled experiment selection avoids high-entropy but decision-irrelevant decoys that attract pure information gain. Typed remint/transport beats matched-budget re-derivation when transport is genuinely useful and ties it exactly where reminting buys nothing. Two negative/donor-absorption studies bound the positive story: typed failure state adds decision information but an ideal VoI donor exactly closes its allocation policy, and a crossover predictor's original-world advantage disappears against a stronger model-selection donor.

The contribution is **not the invention of typed agent memory, stale-state handling or VoI**; all now have active literatures. The present evidence instead isolates a reusable hypothesis about scientific decision state: the same facts can support different decisions depending on whether validity, scope, uncertainty and decision relevance are explicit. The current suite is synthetic by design and therefore does not establish transfer to real scientific agents. We preregister a matched-information real-domain study over actual research decisions; until that study is executed, this paper should be read as a mechanism-isolation benchmark and theory-building result rather than a deployment claim.

---

## 1. From agent memory to scientific epistemic state

A long-lived research process stores more than ordinary facts. It accumulates statements such as:

- “candidate A failed under representation version 3”;
- “this certificate is valid only if access condition X and approximation assumption Y remain unchanged”;
- “resource coordinate T is known only within an interval”;
- “this negative result applies to one method grammar but not a representation edit outside the grammar”;
- “this observation is uncertain but cannot change the current decision”;
- “this proof receipt can be transported through one transformation only after a remint obligation is discharged.”

These are not merely memories to retrieve. They are **epistemic objects whose decision value depends on role and scope**.

The distinction has become important because the agent-memory literature is rapidly adopting typed, provenance-aware and temporally governed representations. MemIR, for example, explicitly separates evidence, retrieval cues and truth-bearing claims to mitigate provenance-role collapse. STALE measures whether agents notice when new evidence invalidates prior state. Other systems ground persistent memory in provenance or formalize scope/versioning/temporal supersession. At the same time, value-of-information is now used directly in LLM-agent decision making.

These developments mean that a broad claim such as “agents should use typed memory” would be both underspecified and poorly differentiated. We instead isolate a more specific scientific question:

> **Holding visible information fixed, when do explicit epistemic bindings change a research decision?**

This framing makes the baselines as important as the positive mechanism. If a strong planner given the same facts can reproduce the typed decision, the result is donor absorption rather than evidence for a special mechanism.

---

## 2. Shared experimental contract

All six primary families were frozen before their result-bearing execution. They use deterministic synthetic worlds because exact truth and exact matched-information comparisons are difficult to obtain in live scientific workflows.

### 2.1 Matched information

Within each family, non-oracle arms receive the same serialized world state. A positive result is intended to isolate **how facts are represented or consumed**, not access to extra evidence.

### 2.2 Strong donor first right of refusal

Each family includes the strongest relevant baseline available within the frozen information/resource contract. A tie or donor win is an honest terminal.

### 2.3 Hostile controls

Every claimed mechanism has a prespecified world where a plausible shortcut should fail or where the mechanism should have no advantage. If that control does not bite, the world is invalid rather than a positive.

Examples include:

- irrelevant `NOISE` changes that should not reopen scoped failures;
- high-entropy decoy observations with no downstream decision value;
- deep evidence splices that last-hop verification cannot detect;
- a regime where remint/transport is unnecessary and all correct methods should tie.

### 2.4 Typed authority

All receipts explicitly bound their authority to exact-synthetic mechanism isolation. The deterministic `LLM_PROXY` arms are heuristics and are not measurements of frontier LLM capability.

---

## 3. Study A: type-conditioned value of information

A layered research-interface graph contains feasible/infeasible edges whose unknown feasibility rates depend on interface type. Committing to an infeasible path is costly; probing unknown edges also costs utility.

The typed arm uses the declared type-conditioned rates when computing one-step value of information. The main isolation baseline runs the identical VoI machinery with a uniform 0.5 prior. Thus both arms have the same graph, known truths, unknown edges, costs and action set; the difference is whether interface type is used as an epistemic prior.

Mean utility over 300 paired episodes:

| arm | mean utility |
|---|---:|
| full oracle | 4.612 |
| typed-prior VoI | 3.291 |
| uniform-prior VoI | 2.180 |
| optimize known subgraph | 0.358 |
| deterministic LLM proxy | -12.306 |
| optimistic commit | -13.619 |

The typed arm recovers approximately 71% of oracle utility. The relevant conclusion is not “VoI works”—VoI is classical and now actively used in agent communication/planning—but that **type metadata has decision value even when the underlying visible facts are otherwise matched**.

Source: `N4_A_UNKNOWN_VOI_RESULTS.json`.

---

## 4. Study B: scope-bound reopening of stale failures

Failure receipts are bound to context coordinates such as representation version and access contract. A separate `NOISE` coordinate changes frequently but does not affect the truth of the recorded failure.

The typed rule reopens a failure only when a coordinate inside its recorded applicability scope changes. Baselines never reopen, always reopen, or reopen on any context change.

Pooled mean utility:

- scoped reopening: 3.199;
- never reopen: 2.782;
- unscoped change reopening: -7.813;
- always reopen: -9.225.

The hostile `REOPEN_WASTEFUL` regime is essential. There, relevant coordinates almost never change while `NOISE` changes frequently. Always reopening falls to -13.406 and unscoped change reopening to -11.522, while the scoped method remains close to never-reopen.

Current stale-memory literature already studies whether old state is superseded. The narrower mechanism here is **applicability scope**: a change matters only if it intersects a dependency recorded by the failure.

Source: `N4_B_STALE_RECEIPT_REOPENING_RESULTS.json`.

---

## 5. Study C: verification targeted by Pareto ambiguity

Some candidate resource vectors are only interval-known. A verifier can resolve a limited number of uncertain coordinates.

A generic strategy might verify randomly or according to midpoint/worst-case rankings. The typed mechanism asks a decision-specific question: **which uncertain edge prevents us from establishing Pareto dominance?**

At the same verification budget `B=4`, Pareto-ambiguity-targeted verification achieves mean scalarized regret 0.1096 versus 0.2518 for random verification, approximately a 2.3x reduction, with 76.5% zero-regret outcomes.

The mechanism is therefore not merely “uncertainty-aware.” It binds uncertainty to the particular comparison needed for the downstream choice.

Source: `N4_C_INTERVAL_PARETO_RESULTS.json`.

---

## 6. Study D: full-chain evidence transport

Scientific artifacts are frequently transformed across representations. A certificate that was valid on one object cannot automatically be treated as valid after a chain of edits.

The frozen transport world contains honest chains and laundering attempts. Some attacks splice invalid evidence deeper in the chain while leaving the final hop superficially consistent.

Full-chain typed transport verification detects 200/200 registered laundering chains, including all 68 deep splices, with false-positive rate 0/200 on the honest set. Last-hop checking catches only 8.5% overall and none of the deep splices.

This is not a cryptographic-security result: hashes are synthetic identifiers and an adversary able to forge the entire receipt model is out of scope. The mechanism claim is simply that **transport validity is a path property, not a property of the final label alone**, in this exact world.

Source: `N4_D_LAUNDERING_DETECTION_RESULTS.json`.

---

## 7. Study E: decision-coupled information acquisition

Pure information gain prefers observations that reduce uncertainty, even if that uncertainty cannot affect the current scientific decision.

The frozen world includes high-entropy decoy facts deliberately constructed to be decision-irrelevant. Under a shared stopping rule, pure information gain spends 36.6% of probes on decoys, while the decision-coupled selector spends zero.

Mean utility:

- decision-coupled: 9.266;
- deterministic LLM proxy: 8.989;
- cheapest-first: 8.075;
- random: 7.568;
- pure information gain: 7.121.

The distinguishing idea is not acquisition of information per se. It is evaluating information by **expected change in the actual downstream decision**, conceptually adjacent to VoI but instantiated over a research-state graph with explicit decoy controls.

Source: `N4_E_ACTIVE_EXPERIMENTS_RESULTS.json`.

---

## 8. Study F: typed remint and transport across representation edits

When a scientific representation changes, some prior evidence may transport unchanged, some may require a remint/reverification, and some may become invalid.

In the `MIXED_TRANSPORT` regime, typed remint/transport achieves mean utility 9.421 versus 7.157 for matched-budget re-derivation and -7.821 for naive carry-forward. Across 14,400 receipts, the frozen invalidation rule has zero mismatches and no infeasible commits.

The strongest first-right-of-refusal control is the `REMINT_UNNECESSARY` regime. All four arms tie **exactly** at 11.809659685355605 and the typed method spends zero remints. The mechanism therefore does not receive credit where transport metadata buys nothing.

Source: `N4_F3_REMINT_TRANSPORT_RESULTS.json`.

---

## 9. Negative controls and donor absorptions

### 9.1 Typed failure state is useful; the allocation policy is not uniquely ORION

N1-C finds a paired solve-rate gain of +0.0271 for typed scoped failure state over an unscoped ablation, with zero false escalations versus 0.6959. But an ideal VoI donor given the same typed facts matches the allocation policy exactly at solve rate 0.9866.

The correct conclusion is therefore about **state as decision information**, not a novel verification-allocation algorithm.

### 9.2 Crossover prediction survives only as misspecification robustness

N2-F5 initially appears to leave a predictive residual. A stronger model-selection donor later ties the candidate exactly on the original well-specified world. The candidate stays ahead only on the frozen misspecified world.

This prevents a broader extrapolation claim from leaking into Q4.

---

## 10. What the six studies jointly suggest

The suite points toward a common mechanism:

> In research decisions, a fact's value is often conditional on **what role it plays, where it is valid, what transformation history it survived, what uncertainty remains, and whether resolving it can change the decision**.

Flattening those bindings can make an agent behave as though:

- every context change invalidates every failure;
- every uncertain fact deserves verification;
- every recent certificate validates its full transformation history;
- every high-entropy observation is valuable;
- every old artifact must be re-derived or can be blindly reused.

The synthetic worlds deliberately isolate these failure modes. They do not show that real research agents exhibit the same effect sizes.

---

## 11. Related-work boundary

### Typed/provenance-aware memory

MemIR and other 2026 memory architectures already make evidence role and provenance explicit. Q4 therefore makes no priority claim for typed memory itself.

### Stale memory and state revision

STALE and follow-up work measure whether long-term agents detect/update invalidated memories. Q4's scope-bound failure-reopening experiment is related but asks a more specific dependency question: which context coordinates actually licensed the old failure?

### Value of information

VoI is classical and ACL 2026 applies it directly to agent clarification. Q4 uses VoI as a donor/planning primitive and asks whether typed scientific state changes its inputs/outcomes.

### Governed/versioned agent memory

Current work increasingly treats memory scope, provenance, temporal supersession and policy as systems/database concerns. Q4 is not a competing persistent-memory architecture; it is a controlled decision-mechanism suite.

A bounded map is recorded in `NOVELTY_RESEARCH_2026-08-22.md`.

---

## 12. Preregistered real-domain upgrade

The main limitation is synthetic transfer. `TOP_TIER_UPGRADE_PROTOCOL_2026-08-22.md` therefore freezes a real scientific decision study.

The planned primary unit is a versioned research decision under partial knowledge: reopen a negative, verify an uncertain resource, transport/remint evidence, choose a Pareto-relevant measurement, or select a decision-relevant experiment.

Every arm receives the same canonical fact bundle. The study compares typed/scoped representation with untyped-bag, retrieval-only and strong task-specific baselines, using multiple reasoning backends where feasible. Prospective items are frozen before later scientific resolution and scored only after the corresponding receipt/commit/public artifact exists.

Target: at least 100 real decision items across at least three programmes, with at least 30 genuinely prospective unresolved items if feasible.

Until those results exist, no real-agent transfer claim is permitted.

---

## 13. Limitations

1. All present primary studies are exact-synthetic.
2. The worlds intentionally expose the typed coordinates as usable facts; a real agent may fail to infer/maintain those coordinates.
3. The `LLM_PROXY` arms are deterministic heuristics, not LLM evaluations.
4. N4-D is not a cryptographic/adversarial-security experiment.
5. Some outcomes use scalarized regret rather than complete Pareto-front metrics.
6. No lower bound proves that the chosen typed schema is minimal or necessary.
7. The current literature contains direct neighboring work on typed memory, stale state and VoI, so novelty must lie in the research-decision mechanism/evidence, not the generic primitives.

---

## 14. Claim boundary

This version may claim only that the frozen synthetic suite demonstrates six matched-information mechanism effects under exact controlled worlds and that two negative/donor comparisons bound the positive interpretation.

It may not claim:

- superiority on real scientific workflows;
- novelty of typed memory, provenance, stale-memory handling or VoI;
- measured performance of real LLM agents;
- real security guarantees;
- execution/results of the preregistered real-domain study.

---

## Related-work anchors

- Z. Jin et al., *Mitigating Provenance-Role Collapse in Long-Term Agents via Typed Memory Representation*, arXiv:2605.25869 (2026).
- H. Chao et al., *STALE: Can LLM Agents Know When Their Memories Are No Longer Valid?*, arXiv:2605.06527 (2026).
- H. Sun and L. He, *When Memory Updates but Behavior Does Not: Repairing Implicit Stale Dependencies in Personalized Agent Responses*, arXiv:2608.01619 (2026).
- Y. R. Dong et al., *Value of Information: A Framework for Human-Agent Communication*, ACL 2026.

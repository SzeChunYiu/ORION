# P6–P8 mathematical completion path

**Status:** active candidate-paper programme.  
**External LLM API requirement:** **none**.

The three candidate papers can be completed as theorem-led mathematical and formal-methods papers. Internet access is still required for current literature closure and source verification, and independent scholarly review is required before claiming peer-review readiness. Neither task requires a paid or proprietary LLM API.

## 1. What “complete” means

Three terminals must remain distinct.

1. **Mathematically complete manuscript** — definitions, semantics, theorem statements, proofs/countermodels, examples, limitations, bibliography and reproducibility instructions are present.
2. **Novelty-bounded manuscript** — the smallest residual survives the nearest-work and P1–P5 ownership audits (#318, #287, #343).
3. **Peer-review ready** — mathematical arguments have independent review, mechanized or deterministic checks reproduce where applicable, the final literature closure is current, and the claim ledger authorizes every headline sentence.

A manuscript can reach (1) while remaining `CANNOT_CHECK`, `ALREADY_SOLVED`, or `MERGE_INTO_EXISTING_PAPER` at (2). No paper will be forced into existence by renaming an existing ORION contribution.

## 2. Non-LLM toolchain

The default completion path uses only deterministic/open tooling:

- Markdown/LaTeX for manuscripts;
- Python standard-library finite-model enumerators and counterexample generators;
- a proof assistant such as Lean 4 or Isabelle/HOL for selected structural theorems where the formalization cost is justified;
- SAT/SMT/model checking only when useful and reproducible;
- BibTeX plus DOI/arXiv/source-identity checks;
- Git/GitHub Actions for immutable execution and artifact hashes.

LLMs may be compared as an optional application layer in future work, but no theorem, proof, novelty verdict, or completion gate may depend on an LLM judge.

## 3. Expert-role review model

Every finding is pressure-tested from five explicit roles. These are review functions, not claims of human participation.

- **Formal logician:** syntax, semantics, soundness, countermodels and proof obligations.
- **Formal-methods engineer:** executable correspondence, finite-model checks, proof-assistant targets and reproducibility.
- **Epistemic-navigation theorist:** partial observability, route/topology semantics, stopping impossibility and transfer.
- **Authorization/governance logician:** obligation, permission, delegation, revocation, laundering and protected roots.
- **Scientific editor/novelty auditor:** P1–P5 ownership, nearest work, nonclaims, quantifier scope and journal-readiness authority.

A proposed theorem or novelty statement is not retained until each relevant role records what it establishes and what it does not.

## 4. P6 theorem programme — Formal Epistemic Structures and Mechanics

### Formal objects
- typed epistemic coordinates and valuations;
- claims/obligations with certification state;
- provenance and dependency hypergraphs;
- mechanic contracts with read/write sets, preconditions, evidence obligations, transition relation, authority scope, emitted obligations, failures and invariants;
- sequential, conditional, separated-parallel and recursive-audit composition;
- dependency-scoped reopening and retained negative history.

### Primary theorem targets

**P6.T1 — Minimal sound reopening.** Under a sound dependency graph, reopening the downstream closure of a changed coordinate is sufficient to prevent stale dependent certifications and is minimal among strategies that must be sound for every semantics compatible with that graph.

**P6.T2 — Commutation under separation.** Two deterministic mechanics commute when each mechanic’s write set is disjoint from the other’s read/write footprint and both preserve shared invariants.

**P6.T3 — Sequential non-escalation.** Sequential composition of mechanics that cannot mint stronger authority and consume only typed in-scope authority cannot increase authority beyond the union of trusted external grants.

**P6.T4 — Recursive-audit termination.** Recursive mechanic audit terminates when every recursive call strictly decreases a well-founded rank; a finite countermodel demonstrates nontermination when this condition is absent.

**P6.T5 — No internal self-authorization guarantee.** If an auditor may rewrite both the predicate and evidence by which its own change is authorized, nontrivial promotion soundness cannot be guaranteed without a protected authority root.

### Required proof artifacts
- mathematical proof for P6.T1–T4;
- explicit countermodel for P6.T5;
- bounded finite-model checker for reopening, separation and escalation cases;
- exact mapping from selected ORION registry objects into the formal signature;
- proof/nonproof boundary against AGM, dynamic epistemic logic, truth-maintenance and architecture formalisms.

## 5. P7 theorem programme — Epistemic Navigation in Open Worlds

### Formal objects
- epistemic topology, locations, frontiers and route signatures;
- observed history versus possible unobserved extensions;
- open/censored/unavailable obligations;
- local route stopping, global task stopping, defer/revisit and `CANNOT_CHECK`;
- topology-changing reframes with partial preservation maps;
- support-preserving transfer and dependency-based reopening.

### Primary theorem targets

**P7.T1 — Open-world stopping impossibility.** For any finite observation history lacking a closure certificate, there exist two observationally indistinguishable world extensions—one complete and one containing an unseen relevant state. Therefore no rule can soundly authorize global completion on that history for both worlds.

**P7.T2 — Strict expressivity of topology change.** There exists a task family whose goal is unreachable under every policy restricted to the initial topology but reachable after an admissible reframe; fixed-topology navigation is therefore strictly weaker on that family.

**P7.T3 — Preservation under reframe.** A closed obligation may transfer across a reframe only when its complete support substructure lies in the preservation map and the map preserves the predicates/relations used by its certificate; otherwise the obligation must reopen or become `CANNOT_CHECK`.

**P7.T4 — Output overlap does not identify route independence.** Equal observed outputs do not imply structural dependence, and disjoint observed outputs do not imply structural independence; constructive counterexamples establish both directions.

**P7.T5 — Fail-closed task stopping.** A task-stop judgment is sound only if every mandatory obligation is satisfied or is explicitly discharged by a valid closure certificate; low utility, route exhaustion or budget depletion alone cannot derive completion.

### Required proof artifacts
- indistinguishability proof for P7.T1;
- graph/topology countermodel for P7.T2;
- transfer lemma for P7.T3;
- explicit route counterexamples for P7.T4;
- deterministic generator/checker for finite dynamic-topology instances.

## 6. P8 theorem programme — Epistemic Authority for Autonomous Science

### Formal objects
- typed epistemic action domains: reframe, search/stop, map/merge, assert and self-modify;
- capability, support, defeaters, hard/soft obligations, authority, delegation, revocation and `CANNOT_CHECK`;
- typed authority certificates with issuer, domain, scope, evidence identity and expiry;
- explicit sound coercions between authority domains;
- dependency-tracked revocation and protected authority roots.

### Primary theorem targets

**P8.T1 — No authority laundering.** In a derivation system where judgments are domain-typed and the only cross-domain rules are registered sound coercions, a judgment from domain `d` cannot authorize an action in domain `d'` unless a valid coercion path exists. Proof is by induction over derivations.

**P8.T2 — Non-compensatory blockers cannot be represented by an unbounded additive evidence accumulator with finite penalties.** For every finite blocker penalty, sufficiently many positive evidence increments can cross a fixed threshold while the blocker remains unsatisfied. A hard obligation therefore requires a conjunctive/veto or lexicographic layer.

**P8.T3 — Dependency-grounded revocation.** Revoking an evidence or authority ancestor invalidates every downstream authorization certificate whose derivation depends on it; unrelated certificates remain unchanged under a sound dependency relation.

**P8.T4 — Self-promotion requires an authority root outside candidate control.** If a candidate can alter the policy and evidence that determine its own admission, it can construct a policy that admits any candidate; internal acceptance alone cannot establish promotion soundness.

**P8.T5 — Domain-gate embedding.** Each existing P1–P5 authority gate can be represented as an instance of the calculus. Consequently, P8’s possible incremental contribution is cross-domain composition, anti-laundering and revocation—not greater within-domain expressive power by vocabulary alone.

### Required proof artifacts
- derivation calculus and induction proof for P8.T1;
- algebraic construction for P8.T2;
- dependency proof for P8.T3;
- countermodel for P8.T4;
- explicit embeddings for P8.T5;
- deterministic hostile-case checker.

## 7. Literature and novelty obligations

Mathematics does not eliminate related-work obligations. The following must be treated as prior art where applicable:

- dynamic epistemic/action logics and belief change;
- AGM/iterated revision and formalized belief-revision libraries;
- truth-maintenance and dependency-directed backtracking;
- process/separation/temporal logics and typed transition systems;
- graph navigation, exploratory search, information foraging and POMDP information acquisition;
- deontic/input-output/action logics, access-control authorization logics and policy composition;
- abstention/selective prediction, provenance guardrails and shielding/formal runtime enforcement;
- current agent-architecture and capability-versus-permission work.

The novelty residual is recomputed after every close donor is absorbed. Renaming an established theorem or applying it to ORION is not a new theorem.

## 8. Completion order

1. Finish the P6/P7/P8 formal cores and theorem proofs.
2. Implement deterministic finite checks and countermodels.
3. Complete the P1–P5 overlap/embedding matrix.
4. Saturate nearest work and strike absorbed claims.
5. Convert drafts into complete LaTeX manuscripts and bibliographies.
6. Run independent proof/claim review.
7. Promote only candidates with a non-duplicative residual; merge or close the others honestly.

## 9. Current authority

All three papers remain candidates. The theorem statements above are research targets until proofs and literature boundaries are committed and independently checked. The absence of an LLM API dependency does not itself establish novelty, correctness or peer-review readiness.

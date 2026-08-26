# ORION-16–ORION-18 peer-review-ready gate — 2026-08-18

**Purpose:** convert the theory-complete package merged by #375 into journal-facing, externally submittable manuscripts without manufacturing peer review or empirical superiority.

## Terminal semantics

`PEER_REVIEW_READY` means all material required for an editor and external referee to evaluate the paper is frozen on one reproducible commit:

1. scoped theory is complete and all known hostile counterexamples are reflected in theorem premises;
2. a current literature delta has been run twice with no unabsorbed material change in the surviving claim;
3. nearest strong donors are cited in the manuscript, not merely in a programme ledger;
4. all broad donor-owned novelty claims are removed;
5. the manuscript contains a normal in-text citation system and reference list;
6. title page, corresponding-author metadata, keywords, declarations and transparent AI-use disclosure are supplied;
7. venue-specific submission assets are present;
8. deterministic theory/benchmark checks, a submission-package linter, and clean LaTeX PDF builds pass on the exact commit;
9. repository CI passes on the exact submission PR head;
10. no `TODO`, `TBD`, placeholder citation, fabricated result, unsupported superiority sentence, undefined reference/citation, or overfull PDF box remains.

`PEER_REVIEW_READY` does **not** mean `PEER_REVIEWED`, `ACCEPTED`, or `EMPIRICALLY_SUPERIOR`.

## Current target venues

- ORION-16 — *Artificial Intelligence* (AIJ), regular paper.
- ORION-17 — *Artificial Intelligence* (AIJ), regular paper.
- ORION-18 — *Autonomous Agents and Multi-Agent Systems* (JAAMAS), regular paper.

Fallback venues remain as recorded in `VENUE_DECISION_V2.md`; this gate is frozen against the primary venues.

## Current theory terminals inherited from main

- ORION-16: `THEORY_FINISHED_V2_1`.
- ORION-17: `THEORY_FINISHED_V2`.
- ORION-18: `THEORY_FINISHED_V2_1` (`FORMAL_CORE_V2.md` plus its superseding
  primitive-closure addendum `FORMAL_CORE_V2_1.md`).

## Current submission claim terminals after the 2026-08-18 delta

### ORION-16

Allowed central claim:

> A scientific-admissibility layer is required when dependency/effect repair carries scientific certification: support-sound repair gives safety, stronger affected-realizability is needed for graph-only minimax minimality, and erasing hard scientific obligations/commit authority/provenance is not fully abstract for admissibility.

Explicitly donor-owned: TMS/ATMS, self-adjusting computation, selective repair, effect typing, evidence-backed authorization, provenance, dependency-aware decision repair.

### ORION-17

Allowed central claim:

> Representation/objective change requires a scientific closure-transport contract stronger than evidence/artifact transport: evidence may remain valid while the active scientific obligation is no longer discharged, and unresolved/censored completion obligations remain fail-closed across chart change.

Explicitly donor-owned: graph/POMDP navigation, planning abstraction, representation refinement, schema/lens/ontology transport, categorical regime transport, sheaf transport/obstruction, goal/world-model evolution, route/task stopping.

### ORION-18

Allowed central claim:

> Cross-domain scientific authorization requires type-correct discharge of the target scientific obligation—domain, kind, scope, content and epoch—directly or through protected composable coercions; alternative complete derivations determine revocation, and a shared calculus has no inherent expressive advantage over an ideal typed product implementing the same semantics.

Explicitly donor-owned: generic authorization/delegation/revocation, UCON, effect typing, exact-artifact/action binding, evidence-vs-effect authority, pre-commit/stale authorization checks, provenance governance, abstention, multi-authority propagation.

## Human-only metadata boundary

The repository may use public institutional author identity, affiliation and corresponding e-mail. It must not infer or invent a grant number, private funding arrangement, competing/non-financial interest, or ORCID. Such personal declarations are confirmation-at-submit metadata, tracked in #377; they are not missing scientific content.

## Reopen rule

Any newly discovered work that proves the surviving interface under materially equivalent assumptions, any checker counterexample, or any referee-found proof defect reopens the relevant paper. This is maintenance of a finished theory, not permission to conceal the defect.

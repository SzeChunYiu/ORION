# ORION research harness — full paper-programme operationalization V2

Date: 2026-08-22
Branch: `codex/paper-contract-operational-harness`
Status: FROZEN BEFORE V2 IMPLEMENTATION
Parent packet: `PAPER_CONTRACT_OPERATIONALIZATION_V1.md`
Authority ceiling: engineering/development only. This packet grants no scientific, novelty, publication, promotion, merge, or global-stop authority.

## Development question

Can the shared ORION research harness expose a semantic execution surface for every current ORION paper-owned research mechanic, rather than treating paper identity, source-file existence, or mechanic discoverability as proof that the framework is operational?

V1 made three previously non-operational P0 objects executable:

- raw paper -> source-bound P1/P3 method structure;
- evidence-derived nine-axis saturation with structural route contracts;
- Paper-VII chart/obligation/reframe navigation.

V2 closes the remaining programme-level false-green boundary.

## Source-of-truth scope

The active paper programme contains ORION-P1 through ORION-P15. P1–P5 own the flagship runtime semantics; P6–P8 contain formal generalizations; P9–P14 own structured-learning/state/reasoning/successor research; P15 owns the harness guarantee surface.

A V2 conformance row may be GREEN only when it executes an actual decision or invariant through the canonical owner implementation or an additive harness runtime that implements a paper-defined gap. A file, module, ID, registration row, checker existence, or static import is insufficient.

## Atomic development fibres

### H1 — P6 operational epistemic mechanic calculus

Implement the closed P6 V2 theory as an executable harness control object without claiming novelty:

- typed epistemic state: coordinate values, claim statuses, dependencies, provenance, hard obligations, authority, append-only history;
- root-inclusive affected-certified-set calculation;
- preservation certificates that cannot self-preserve a changed certified root;
- certificate-aware reopening;
- mechanic contracts with declared read/write footprints, preconditions, hard requirements, authority requirements/effects, obligation emissions/discharges, provenance and failure terminals;
- admissibility checks before commit;
- hard residual-obligation persistence;
- non-escalating authority;
- semantic separation and history-aware commuting composition;
- fail-closed recursive/cycle boundary.

V2 must reuse live ORION dependency/reopen/authority concepts where they own semantics; the additive object is the unified executable composition layer described by P6.

### H2 — P8 operational cross-domain authority calculus

Implement the closed P8 theory as an executable shared authority layer:

- typed effect request and authority domain/scope;
- blocker and hard-obligation evaluation;
- protected roots/issuers;
- registered coercion from source authority domain to target domain;
- exact source/target scope, content/provenance, issuer/root and epoch constraints;
- dependency/support lineage;
- revocation of one derivation without automatically destroying an independently complete alternate derivation;
- fail closed for missing/stale/widening coercions;
- confidence, expected utility, model text and generic PASS/SUCCESS are never substitute authority.

The runtime must prevent a valid source-domain result from becoming foreign-domain scientific authority merely because glue code sees `success=true`.

### H3 — P1–P5 conservative native-decision equivalence

Create semantic probes that call the canonical owners and require both a positive and a fail-closed/native-negative case for:

- P1: reframe/reopen/dependency scope;
- P2: route-stop versus task-stop/open coverage;
- P3: source-local merge/alignment versus obstruction/unresolved ambiguity;
- P4: assertion/verification promotion versus missing/protected hard-gate block;
- P5: governed self-change/readiness versus missing fresh/protected evidence.

The probe must not reimplement the decision rule in the test. It must invoke the production owner.

### H4 — P6–P8 semantic conformance

P6, P7 and P8 must be probed through executable runtime behavior, including hostile counterexamples from their formal cores.

- P6: changed certified root must reopen; preservation certificate may preserve only unchanged descendant; hard obligation cannot disappear; unrooted authority widening denied; independent mechanics commute in current scientific state but histories preserve order.
- P7: V1 navigation/reframe/route/saturation probes remain required.
- P8: local PASS cannot cross authority domain without registered coercion; stale epoch/widening scope denied; revoking one support route may retain authority only if a separate complete trusted support family remains.

### H5 — P9–P14 owner-bound semantic probes

For every P9–P14 paper, identify the current canonical production owner from the repository's paper/programme manifests and execute at least:

- one accepted/supported/positive control; and
- one negative, obstructed, unresolved, `CANNOT_CHECK`, blocked or rejected control.

The conformance row must publish the exact owner module/API used. If a paper has no executable canonical owner, the V2 gate must mark it `NOT_OPERATIONAL` rather than invent a fake implementation. Any genuinely paper-defined runtime gap discovered here becomes an explicit implementation task before the full-programme terminal can turn GREEN.

### H6 — P15 harness guarantee probes

P15 must be tested semantically for its current systems-paper guarantee surface:

- host/capability failure is kept outside scientific evidence/state;
- deterministic request/result binding and replay;
- invalid/mismatched receipt content fails closed;
- receipt coverage does not by itself grant evidence/scientific authority;
- shared harness and domain campaign authority ceilings remain explicit.

### H7 — one programme-wide semantic gate

Add `paper-programme-conformance` that returns one row for every ORION-P1..P15 identity with:

- paper id/title;
- canonical owner/runtime API;
- positive probe id/result;
- fail-closed probe id/result;
- operational status;
- authority ceiling;
- notes for any bounded or non-empirical status.

The programme terminal is GREEN only if every paper row is operational under its actual bounded claim. A research-only empirical claim that correctly remains `CANNOT_CHECK` is not a harness failure if the runtime can execute and preserve that `CANNOT_CHECK` boundary; lack of any executable decision surface is a harness failure.

## Frozen hostile tests

### P6

1. Changing a certified root reopens that root even if it has no descendants.
2. A changed root cannot use its own preservation certificate to keep the old certificate.
3. A valid external preservation certificate may keep an unchanged descendant certified.
4. An undischarged hard obligation emitted by step N remains active after later successful steps.
5. A mechanic that writes outside its declared write footprint is rejected before commit.
6. Missing hard evidence/authority returns a fail-closed result and does not mutate state.
7. Unrooted authority widening is rejected.
8. Semantically separated deterministic mechanics commute in current scientific state while ordered history differs and is independently equivalent.
9. Recursive/self-audit cycle with no rank decrease is rejected.

### P8

10. `PASS`, confidence or utility without target-domain authority cannot authorize an effect.
11. A source-domain authority object cannot authorize a target-domain effect without a registered coercion.
12. Coercion with stale epoch is rejected.
13. Coercion that widens scope beyond its declared transformation is rejected.
14. Coercion whose protected issuer/root is absent is rejected.
15. Revoking one support derivation removes authority when no complete alternate derivation remains.
16. Revoking one support derivation retains/rederives authority only when a complete independent trusted alternate support family remains.
17. Revocation records append-only history and cannot erase the historical fact that authority previously existed.

### Programme matrix

18. There are exactly 15 current ORION paper rows, P1 through P15.
19. Every row has a non-empty canonical owner/API and executes a positive and fail-closed probe.
20. No row can be GREEN from module/import/path existence alone.
21. P1–P5 probes invoke production owners, not harness copies.
22. P6–P8 probes execute the operational calculi/counterexamples.
23. P9–P14 missing owners cause explicit `NOT_OPERATIONAL`, never silent green.
24. P15 host failure is not admitted as scientific evidence.
25. The overall terminal cannot be GREEN if any row is missing either semantic polarity.
26. No conformance row grants novelty, publication, merge or scientific authority merely for passing.

## Bounded implementation hypothesis

Implement additively:

- `epistemic_mechanics.py` for P6;
- `epistemic_authority.py` for P8;
- `paper_programme_conformance.py` for P1–P15 owner-bound probes;
- strict JSON adapters/CLI commands where operational use benefits from direct invocation;
- RED->GREEN tests dedicated to P6/P8/programme conformance;
- CI gate extending the existing paper-contract workflow.

Do not alter frozen paper evidence/checker outputs. The harness should import or call production owners/checkers as needed rather than copying them.

## Reopen triggers

Reopen this design if:

- a canonical P6 or P8 runtime owner already exists and the additive layer duplicates it;
- a P1–P5 probe cannot be constructed without changing the production scientific decision rule;
- P9–P14 paper identity/owner is ambiguous in the current machine-readable programme registry;
- a formal checker is the only existing executable surface for a paper and cannot be safely embedded as a runtime contract;
- the programme gate can report GREEN while a paper has no executable positive/negative semantic decision;
- full conformance requires mutating protected/frozen evidence artifacts.

## V2 terminal

`ORION_HARNESS_P1_P15_OPERATIONAL`

Allowed only if all frozen hostile tests pass and `paper-programme-conformance` reports semantic execution coverage for every current ORION paper identity P1–P15.

This terminal means the harness can execute the paper-owned research control/mechanic contracts at their bounded current claim ceilings. It does not imply every scientific hypothesis is true, every empirical superiority claim is established, or every future paper proposal is implemented.

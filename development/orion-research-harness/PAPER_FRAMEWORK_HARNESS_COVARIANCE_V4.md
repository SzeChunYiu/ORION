# Paper ↔ Framework ↔ Harness Covariance V4

Date: 2026-08-22
Status: FROZEN BEFORE IMPLEMENTATION
Authority: engineering/research-control contract only; grants no scientific, novelty, publication, promotion, merge, or global-stop authority.

## Purpose

ORION's papers, executable framework, and research harness must describe and execute the same research semantics. None of the three is allowed to drift silently from the others.

The V4 objective is to close two semantic gaps:

1. `CANNOT_CHECK` must normally create an active resolution obligation rather than a bare stopping token.
2. verified negative results must be assimilated into the research state and next-action policy rather than being treated as failed attempts to hide or coerce positive.

## Three-layer covariance invariant

For every research-control mechanic that changes stopping, authority, evidence, failure, reframe, reopen, method expansion, or outcome semantics:

- **paper layer** defines the epistemic/scientific contract and its limits;
- **framework layer** defines canonical typed state and decision objects;
- **harness layer** executes the framework objects against replayable host capabilities and emits receipts.

A material semantic change in any layer requires an audit of the other two. A release cannot claim operational conformance when a material mismatch remains.

## Outcome classes

V4 distinguishes three top-level outcome classes.

### POSITIVE

A positive result satisfies the relevant bounded decision/evidence contract. It does not automatically imply publication, novelty, promotion, adoption, merge, or global task-stop authority.

### NEGATIVE

A negative result is a verified scientific/research result such as an obstruction, non-identifiability result, donor subsumption, falsified hypothesis, failed transfer under a frozen model, or impossibility boundary.

A verified negative result must be assimilated. It may:

- close or demote a hypothesis branch;
- add an obstruction/failure object;
- reopen a representation/search/method obligation;
- trigger a reframe or donor route;
- refine a paper claim or framework mechanic;
- justify a bounded negative conclusion.

It must never be rewritten to `CANNOT_CHECK` merely because it is undesirable.

### UNRESOLVED / CANNOT_CHECK

`CANNOT_CHECK` means the current evidence/control state is insufficient to decide the target judgment under the declared contract. It is not a negative scientific result.

By default, every `CANNOT_CHECK` produces a `ResearchResolutionObligation.v1` containing:

- stable obligation identity;
- unresolved class;
- subject/judgment identity;
- reason codes;
- required evidence/capability/authority objects;
- admissible next actions;
- prior attempt identities;
- blockers;
- explicit bounded/external stop condition;
- authority ceilings.

A bare `CANNOT_CHECK` without a resolution obligation is a V4 conformance failure.

## Legitimate bounded unresolved terminals

The harness must actively try to resolve `CANNOT_CHECK`, but cannot honestly guarantee that every epistemic question becomes decidable. A resolution obligation may remain unresolved only when one of these typed conditions is established:

1. **protected/external boundary** — required evidence is intentionally unavailable until an external/protected protocol event;
2. **formal non-identifiability / extension ambiguity** — two admissible worlds remain observationally equivalent with different target truth values;
3. **declared resource bound** — the frozen protocol's resource limit is reached and no authorized widening exists;
4. **authority boundary** — required authority/coercion cannot be minted by the harness itself;
5. **unavailable capability** — the host cannot currently execute the required capability, preserved as an orchestration condition rather than scientific evidence.

These are not task-completion proofs. They are typed explanations of why the resolution obligation remains open.

## Resolution-first policy

Before returning or persisting an unresolved state, the harness must select at least one admissible resolution action when one exists, including:

- restore/retry capability;
- acquire/verify evidence;
- expand independent search routes;
- orient or reframe the epistemic chart;
- diagnose causal responsibility;
- repair representation/interface;
- assess OCME for a method gap;
- check typed authority;
- increase resources only when the protocol permits it;
- request protected/external evidence when that is the real blocker.

Repeated attempts must be content-addressed/replayable and may not erase earlier failed or negative evidence.

## Negative-result assimilation policy

Every verified negative result must have a typed assimilation disposition. Minimum dispositions are:

- `ASSIMILATE_OBSTRUCTION`
- `CLOSE_HYPOTHESIS_BRANCH`
- `REOPEN_DEPENDENCY`
- `REFRAME`
- `EXPAND_SEARCH`
- `REGISTER_DONOR_SUBSUMPTION`
- `REVISE_PAPER_CLAIM`
- `REVISE_FRAMEWORK_MECHANIC`
- `BOUNDED_NEGATIVE_TERMINAL`

The disposition is research-control metadata and never self-authorizes a scientific claim.

## V4 RED gates

Implementation is accepted only if frozen tests establish all of the following:

1. a `CANNOT_CHECK` recursive outcome carries a non-authorizing resolution obligation;
2. a resource-bound unresolved state proposes only bounded/authorized resolution actions and never task stop;
3. a protected/external blocker remains explicitly open rather than being retried as ordinary local evidence;
4. a verified negative outcome is represented as NEGATIVE, not `CANNOT_CHECK`;
5. donor subsumption and obstruction produce distinct assimilation dispositions;
6. no negative outcome can grant novelty/scientific/global-stop authority by itself;
7. framework registry and `papers/FRAMEWORK_SNAPSHOT.json` include the V4 resolution objects;
8. `papers/SYNC_CONTRACT.md` states paper ↔ framework ↔ harness covariance and the outcome lifecycle;
9. the shared harness exposes a host-callable resolution-plan surface;
10. the existing P0, P1–P15, V3, recursive-budget, execution-coverage, ORION-Q custody and repository-wide CI gates remain green.

## Required terminal

`ORION_PAPER_FRAMEWORK_HARNESS_COVARIANCE_V4_OPERATIONAL`

This terminal proves operational synchronization and resolution-lifecycle wiring only. It does not prove that every scientific question is solvable or that every negative result can be turned positive.

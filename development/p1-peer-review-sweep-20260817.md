# Development Packet — P1 peer-review sweep / causal-substrate integrity

Date: 2026-08-17
Lane: `shadow/p1-peer-review-sweep-20260817`
Base: `main@71b9e01be34f566c66702c4f31d0140017f80b96`
Owners: #98, #278, #316; verification dependency #283.

## Development question

Before executing or promoting P1 causal-responsibility evidence, does the merged `p1_causal` substrate actually enforce the frozen candidate access policy and do its hostile controls test the invariants they claim to test?

## Atomic fibres

1. Reproduce the concrete review findings on current main by source inspection: probe allowlist fallback / missing intervention allowlist enforcement, vacuous oracle-non-runnable control, and candidate-visible pair/cause identity.
2. Fail closed when no allowed probe exists instead of falling back to the full probe catalog.
3. Never execute a diagnosis-specific intervention unless its id is explicitly present in `PublicMemberView.allowed_intervention_ids`.
4. Keep bundle/pair identity and causal-family labels in host custody; candidate-facing member ids must be opaque with respect to protected responsibility.
5. Replace the vacuous oracle control with an executable structural check over the frozen protocol and every public candidate interface.
6. Add regression tests that fail on each pre-fix defect and no-alarm controls for the normal known-answer cycles.
7. Run targeted and repository CI on the exact PR head before any P1 scientific campaign is credited.

## Incumbent evidence / negative history

- Frozen P1 V1 remains unchanged: H1 root-success difference `0.0000 [0,0]`; 47/48 case-level abstention.
- PR #313 added P1 V2 causal-responsibility scaffolding and explicitly did **not** claim scientific closure.
- Cursor Bugbot review on PR #313 identified the allowlist and oracle-control defects; current main still contains them.
- A deeper protocol check found a third access-policy breach: `PublicMemberView` exposed `bundle_id` / `confusable_kind`, and fixture ids such as `m-retrieval` / `m-search-universe` carried protected causal labels even though the frozen protocol says pair/triple identity and hidden-gold identifiers remain host-side.
- These are instrument-integrity defects, not evidence that P1 V2 is positive or negative.

## Bounded saturation assessment

Relevant knowledge is local and sufficiently specific: `AGENTS.md`, `development/README.md`, frozen `P1.causal-responsibility.v2` access/resource policy, `cases.PublicMemberView`, `engine.run_cycle`, `discriminator.select_discriminator`, `controls.HOSTILE_CONTROLS`, and the PR #313 review findings. No new scientific mechanism is introduced, so a new nearest-work literature claim is not required for this repair.

## Challenge to saturation

A superficially stricter allowlist fix could itself break the instrument by converting a deliberately empty catalog into an exception or by suppressing legitimate known-answer interventions. The tests must therefore include both denial and no-alarm branches. Hiding field names is insufficient if opaque identifiers themselves encode the protected cause. The oracle control could remain vacuous if it checks only a literal string; it must inspect both the frozen protocol declaration and the executable candidate-facing probe/intervention ids.

## Why prior checks missed this

- Unit tests exercised only known-answer views whose allowlists already contain the selected probe/intervention.
- The hostile-control suite checked aggregate `satisfied` values but one control returned constant success.
- Gold-leak checks inspected only forbidden field names, not answer-bearing bundle metadata or member-id values.
- Review feedback was not converted into a post-merge regression before #313 landed.

## Frozen implementation hypothesis

`run_cycle` treats the public allowlists as a hard capability boundary. An empty intersection with the catalog yields `no_separating_probe` / unresolved state; it never falls back to unadvertised probes. A hypothesized intervention absent from `allowed_intervention_ids` is not executed and cannot set `intervention_backed`. `PublicMemberView` contains no bundle/family identity and uses opaque ids that do not encode the protected stage. The oracle ceiling remains analysis-only only if the frozen protocol names it `non_runnable`, its resource policy says it is never a candidate, and no public probe/intervention id exposes an oracle path.

## Reopen triggers

- targeted regression still permits an unadvertised probe/intervention;
- known-answer selectivity regresses under legitimate allowlists;
- a public view or identifier exposes bundle/cause/gold identity;
- protocol changes the oracle resource policy or candidate interface;
- another candidate-visible path reaches protected gold;
- CI exposes a coupled P1 defect requiring a different earliest-stage repair.

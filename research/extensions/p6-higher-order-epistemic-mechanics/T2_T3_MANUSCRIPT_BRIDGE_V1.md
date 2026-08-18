# T2/T3 successor manuscript bridge — responsibility and interface adequacy

**Status:** additive successor theory/framework material. It does not alter the frozen P6 V2.1 submission package and does not create a new paper terminal.

## Responsibility before revision

The tranche-1 minimal-revision calculus assumes a set of candidate mechanics. T2 adds a distinct object upstream: a claim-relative set of **competing revision-responsibility hypotheses**. Each hypothesis binds discriminator identities to outcomes it predicts. An observation may defeat a hypothesis, leave several hypotheses observationally indistinguishable, or leave required discriminators unobserved.

The executable `EpistemicRevisionResponsibilityReport.v1` therefore has four terminals:

- `IDENTIFIED` — exactly one surviving hypothesis and all of its registered discriminators are observed;
- `AMBIGUOUS` — multiple fully tested hypotheses survive the same observations;
- `UNRESOLVED` — at least one required discriminator is still missing;
- `NO_SURVIVING` — every registered responsibility hypothesis is contradicted.

None grants revision authority. In particular,

> a failure plus a plausible explanation is not yet a permission to rewrite the state associated with that explanation.

The current implementation is deliberately discrete and exact. It is a finite countermodel substrate, not a claim that scientific responsibility is generally categorical rather than probabilistic or credal.

## Interface adequacy as a prerequisite, not a new ontology

T3 adds `EpistemicInterfaceAdequacyCheck.v1`. A caller names the check scope; the formal layer does not freeze a universal list of observation, measurement, reward, representation or uncertainty coordinates.

Required checks aggregate fail closed:

```text
any required FAIL        -> REPAIR_REQUIRED
no FAIL + any UNRESOLVED -> UNRESOLVED
all required PASS        -> ADEQUATE
```

Advisory checks are retained but cannot compensate a failed or unresolved required check. `ADEQUATE` means only that the **registered** task-relative checks passed; it is not a proof that the representation is globally sufficient.

This formalizes the distinction exposed by state-sufficiency, Markov-violation, measurement, reward-interface and latent-uncertainty nearest work: poor downstream performance need not imply a defective model or method.

## Self-ORION V3 gate

`SelfOrionRevisionGateReport.v1` composes T2/T3 with the tranche-1 mechanic selector.

The gate is intentionally a recommendation boundary:

1. unresolved or ambiguous responsibility -> no material candidate nomination;
2. unresolved required interface adequacy -> no broader revision nomination;
3. required interface failure -> consider only explicitly registered interface-repair mechanics whose writes remain inside the declared interface coordinate set;
4. interface adequacy + identified responsibility -> filter candidate mechanics through the explicit responsibility binding and run claim-relative minimal-revision selection;
5. any selected candidate still requires isolated execution, replay, fresh transfer, protected assurance and external host disposition.

The gate hard-codes:

```text
grants_adoption_authority = false
grants_promotion_authority = false
grants_merge_authority = false
```

It does not modify the existing P5 invention-readiness gate or historical V1/V2 evidence.

## Countermodel surface

`T2_T3_COUNTERMODELS_V1.json` binds nine deterministic cases covering:

- ambiguity under identical discriminator predictions;
- identification after a separating observation;
- missing discriminator -> unresolved;
- all hypotheses defeated -> no forced repair;
- required interface failure;
- unresolved interface evidence;
- narrow interface repair before a broader rewrite;
- no broad fallback when no admissible interface repair is registered;
- clean adequate-interface path through the tranche-1 minimal selector.

The frozen summary terminal is `T2_T3_FORMAL_COUNTERMODELS_GREEN`. It is an implementation/formal terminal only.

## Paper consequences

### P1
A successor can map its responsibility/discriminator evidence into this object and ask whether its lower-level-exclusion result is a special case. Current bounded P1 science remains unchanged.

### P3/P7
Representation/transport and obstruction witnesses can eventually instantiate interface-check evidence. Similarity or a mapping proposal is not interface adequacy authority by itself.

### P4/P8
Protected authority remains downstream. Neither responsibility identification nor interface adequacy can promote a claim.

### P5
The current paper may accurately state that the non-authorizing V3 formal substrate exists. It may not claim that V3 improves self-revision until the prospectively frozen #455 experiment executes. H1--H4 remain `CANNOT_CHECK`.

### P6
#463 owns the successor mathematics. If stronger parent formalisms subsume the discrete objects, P6 should become an adapter/correspondence result rather than claim the ingredients as novel.

### P9/P10 successors
Learned systems may propose responsibility hypotheses, interface checks, or candidate mechanics, but their scores cannot determine the formal report terminal or scientific authority.

## Next research obligations

- nearest-work pressure on discrete responsibility versus Bayesian/credal diagnosis;
- task-relative sufficiency witnesses for interface checks;
- explicit intervention selection / value-of-information under #458;
- uncertainty containment as a non-revision transition;
- social-evidence correlation under #462;
- semantic revision ordering beyond set inclusion;
- prospective #455 evaluation against M-open, world-model, objective-evolution and strong causal-diagnosis parents.

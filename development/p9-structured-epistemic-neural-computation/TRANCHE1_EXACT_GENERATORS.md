# P9 tranche 1 — deterministic exact-world generators and contamination-safe splits

## Development question

Can the six hand-authored tranche-0 hostile worlds be lifted into a deterministic, scalable exact-world corpus **without introducing family/name/split shortcuts**, while preserving the exact information-sufficiency ladder needed for later model comparisons?

This tranche still does not train a model. It makes the evaluator/data-generating process large enough that the first learning experiment cannot simply memorize six fixtures.

## Upstream evidence and ownership

Consumes:

- merged PR #473 / commit `8879ba2e3380e414ea811c7de4aa067fb3e02a90`;
- #474 representation atom;
- #475 mechanic atom;
- #479 data/ground-truth atom;
- #480 scale/resource atom;
- P1/P3/P6 structural objects only as scientific owners of method/state coordinates.

No P4/P8 authority coordinate is learnable gold.

## Atomic fibres

1. Generate many independent hostile **pairs**, not independent examples, so each restricted-view collision is explicit.
2. Remint every atom/relation/mechanic/world identity per pair with opaque content-derived ids.
3. Keep human-readable surface labels opaque and family-neutral.
4. Preserve a shared surface/topology within each hostile pair while changing exactly the intended hidden coordinate.
5. Preserve the tranche-0 information ladder:
   - `SURFACE` ceiling = `1/2`;
   - `TOPOLOGY` ceiling = `1/2`;
   - `TYPED` ceiling = `2/3`;
   - `CURRENT` ceiling = `5/6`;
   - `SEMANTIC` ceiling = `1`;
   on a balanced mixed family corpus.
6. Make train/dev/test identities disjoint by construction, not only by random sampling.
7. Keep family metadata evaluator-side and absent from model-view fingerprints.
8. Ensure surface randomization/opaque ids do not alter semantic gold.
9. Reject duplicate or cross-split identities.
10. Bind the generated manifest by deterministic content digest.

## Hostile family generators

### F1 — relation semantics

Hold atom ids/types, endpoints, surface labels and mechanics fixed within a pair. Change only one relation type (`SUPPORTS` vs `DEFEATS`) and the appropriate mechanic target.

The mechanics expose structural action classes (`ASSIMILATE_EVIDENCE`, `REOPEN_CLAIM`) in typed contract fields; these are part of the admissible structured input and are visible to every typed baseline. Human-readable labels remain opaque.

### F2 — local transport / gluing

Hold typed graph and transport endpoints fixed. Generate one exact affine cycle whose composition is identity and one pair member with a bounded perturbation producing an obstruction.

Use numerically exact-friendly powers-of-two scales and dyadic/integer offsets to avoid turning floating error into the target.

### F3 — admitted negative history

Hold current atoms/relations/mechanics fixed. One pair member has no admitted failure; the other records a prior failure of the primary mechanic in the matching context, changing the correct selection to fallback.

History metadata must not appear in `CURRENT` or weaker views.

## Competing hypotheses

### H-G1 — scalable exact pairs preserve the intended information lattice
If ceilings drift as corpus size grows, the generator has introduced unintended collisions or leaked information.

### H-G2 — opaque identities remove fixture-family memorization
No model-visible id or surface label should contain `relation`, `transport`, `history`, `support`, `defeat`, `glue`, `obstruction`, `primary`, `fallback`, train/dev/test labels, or the raw generator seed.

### H-G3 — the generator accidentally hand-codes the target
If a target can be read directly from one field rather than inferred from the relationship between state and candidate mechanics, revise the generator before training.

### H-G4 — exact-family balance creates an artificial fixed prior
The balanced corpus is appropriate for information-sufficiency tests but not necessarily ecological training. Later experiments must vary family priors and report family-wise metrics.

## Frozen implementation hypothesis

Implement `orion.study.p9.generated_worlds` with:

- `HostileFamily` enum;
- `GeneratedPair` carrying evaluator-side family/pair metadata and two verified worlds;
- deterministic `generate_pair(family, seed)`;
- deterministic `generate_balanced_split(seed, split, pairs_per_family)`;
- `GeneratedSplit.verify()` for identity disjointness and pair contracts;
- `GeneratedCorpus.verify()` for cross-split disjointness;
- content-bound split/corpus manifests containing identities/digests but never model gold as an input feature.

No stochastic global RNG. Every generated artifact derives from explicit string seeds.

## RED tests before implementation

- repeated seed produces byte/value-identical pair/corpus;
- different seed remints identities/surfaces;
- no forbidden family/split/seed vocabulary in model-visible ids/surfaces;
- every pair has different gold;
- relation pair collides at SURFACE/TOPOLOGY but not TYPED;
- transport pair collides through TYPED but not CURRENT;
- history pair collides through CURRENT but not SEMANTIC;
- balanced split ceilings are exactly 1/2, 1/2, 2/3, 5/6, 1;
- train/dev/test identity sets are disjoint;
- generated transport gold agrees with exact cycle classifier;
- manifest changes when generator seed/count changes;
- no evaluator family/gold metadata enters any model-view fingerprint.

## Reopen triggers

- any generated id/surface leaks family/split/gold;
- a restricted-view ceiling differs from the analytic expectation;
- a later donor benchmark supplies a stronger exact paired generator we can adopt;
- floating transport arithmetic causes unstable labels;
- the first baseline can exploit generator artifacts rather than structural coordinates;
- natural/external data requires a different task interface rather than extension of this synthetic generator.

## Nonclaims

This tranche establishes neither ecological validity nor neural generalization. It only creates a larger exact controlled corpus for falsifying representation claims before expensive model work.

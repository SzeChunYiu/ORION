# Q4-P1 factorial typed-state confirmation protocol

Protocol identifier: `Q4-P1`

Protocol version: `1.0`

`EXECUTION_STATUS=NOT_STARTED`

This is a fresh successor study. It neither upgrades N4-C/D/E/F3 to prospective
status nor changes N1-C, N2-F5B, or any no-advantage regime.

## Primary question

When all non-focal serialized facts and compute budgets are controlled, what decision
value is attributable separately to:

1. availability of a responsibility-relevant type or scope field;
2. inference or reconstruction of that field;
3. a policy's ability to consume that field?

The study tests these factors on externally sourced tasks and held-out synthetic
world families. It does not select worlds conditional on the candidate beating
a shortcut.

## Task universe

Before any outcome, freeze a complete list of tasks from at least four domains.
Inclusion and sampling use outcome-blind metadata. Study authors and task
selection custodians cannot access protected outcomes or candidate/comparator
performance while constructing the universe. The complete sampling frame,
exclusions, and domain weights freeze before any outcome access. Outcome-informed
task selection is labelled exploratory and cannot support prospectivity,
generalization, or superiority.

The task families are:

- stale-dependency repair;
- representation or schema migration;
- provenance-chain validation;
- active experiment or verification selection.

Every unit used for a field-superiority claim must come from a fixed external
benchmark or be selected by task/generator custodians blind to candidate
identity and the study hypothesis, using an algorithmic sampling rule frozen
before policy exposure. Candidate-authored synthetic worlds may remain
as calibration or benchmark strata but cannot dominate or authorize field
superiority. Complete domain-specific sampling frames, domain weights, task
annotations, and a no-resampling rule freeze before any policy output. Each
task family has independent replication across programmes and at least two
domains; one domain cannot uniquely identify one mechanism. Positive, null,
tie, and reversal cases all remain in the denominator.

The domain is the replication unit for any cross-domain generalization.
Outcome-blind power or precision analysis determines the required domain and
programme replication. Four sampled domains do not by themselves authorize a
general claim. A study containing only authored synthetic worlds remains a
benchmark paper, not a field-superiority study.

## Factorial interventions

The first co-primary design is a complete `2 x 2` crossing field state with
consumer policy:

| Field condition | Consumer condition | Purpose |
|---|---|---|
| explicit | typed-aware | full candidate |
| explicit | typed-blind | consumption contrast while holding bytes fixed |
| withheld | typed-aware with frozen missing-field behavior | field-availability contrast for the typed consumer |
| withheld | typed-blind | matched joint control |

The prespecified main effects are the average field-availability contrast and
the average consumer-policy contrast; the interaction is the
difference-in-differences.

The second co-primary design isolates reconstruction in the `derivable` stratum.
Every unit receives byte-identical raw serialized inputs from which the focal
field is derivable but not explicit. Before allocation, freeze one audited
reconstruction operator and its resource budget. Randomize the operator to
`ENABLED` or `DISABLED`, crossed with the typed-aware and typed-blind consumer.
When enabled, its output, confidence, trace, cost, and failure state are bound
to the unit; when disabled, the consumer receives the frozen missing-field
value. The typed-blind consumer must ignore both a reconstructed field and its
status bytes. Thus the reconstruction main effect and its interaction with the
consumer are identified without changing the raw packet. Reconstruction
failure remains an intention-to-treat failure, never an excluded unit.

The co-primary reconstruction estimand is

```text
Delta_reconstruction = regret_DISABLED - regret_ENABLED
```

for the typed-aware consumer, with the corresponding
difference-in-differences against the typed-blind consumer. Inference accuracy,
calibration, latency, and compute are jointly reported. A strongest feasible
reconstruction donor is selected and parity-audited before outcomes; absence or
failure of that donor yields `CANNOT_COMPARE_INFERENCE`, not superiority.

A secondary extension crosses each feasible field condition—explicit,
derivable, and absent—with typed-aware, typed-blind, and unrestricted all-facts
consumers. It maps transport but cannot replace either co-primary design. The
unrestricted consumer may learn or reconstruct any equivalent latent
representation and receives the same training, tuning, context, tool, call,
and stopping resources. If serialized inputs differ, that contrast is labelled
an information intervention, not a pure policy intervention.

## Strongest-donor comparators

Every task family includes:

- optimal or strongest feasible Bayesian value-of-information policy;
- an unrestricted all-facts policy that may use the identical field and
  vocabulary or learn any equivalent latent representation;
- current provenance/dependency-repair or context-management donor;
- a learned baseline where a defensible trained system exists;
- simple always-verify, never-verify, and random/matched-budget controls only as
  calibration baselines, never as the sole superiority comparator.

Name the strongest donor for every task family before outcomes and use a
reference implementation where available. Donor versions, training/tuning
resources, hyperparameters, and an independent parity audit freeze before any
policy output. A donor that is inapplicable or fails its audit yields
`CANNOT_COMPARE`, never a candidate win. If a donor ties within a predeclared
equivalence margin, the result is donor absorption, not candidate superiority.

## Outcomes

### Primary outcome

The primary outcome is normalized decision regret, lower is better. Before any
policy output, each task family receives one fixed mapping from its native
utility or loss to normalized regret; task-local direction cannot be selected
after outcomes. Cross-domain synthesis uses prespecified standardized
domain-level effects, not pooled raw utilities with incomparable meanings.

### Secondary outcomes

- invalid reuse and stale-exposure duration;
- invalidation precision and recall;
- wasted verification or remint cost;
- abstention and calibration;
- repair latency and compute;
- field-inference accuracy and cost;
- sensitivity to utility weights, priors, generator shifts, and donor
  hyperparameters.

N1-C ideal-VOI absorption, N2-F5B donor absorption, and no-advantage remint
regimes remain named confirmatory boundary strata where applicable.

## Numerical and artifact contract

1. Python, NumPy, BLAS, OS, architecture, and dependency lock are frozen.
2. Exact integer or rational accumulation is used when feasible.
3. Otherwise, receipt fields use a predeclared canonical rounding rule.
4. Byte identity and semantic/numerical tolerance are separate gates.
5. Each unit binds protocol, generator/task source, runner, seed, raw result,
   environment, and source digests in a machine-readable manifest.
6. Independent reruns occur on the locked environment and on one portability
   environment; ULP drift is reported, not hidden.

## Analysis and release

Before any policy output or outcome access, freeze task/generator sources,
annotations, policies/runners, the reconstruction operator and its strongest
donor, allocations, scoring rules, utility weights, domain weights, parity
thresholds, smallest effects of interest, noninferiority/equivalence margins,
and a closed-testing multiplicity rule.
Outcome-blind simulation also freezes the minimum independent programme/domain
clusters and target interval precision. Estimate the factorial main effects and
interaction at the task level with the prespecified clustering. If the
replication, power, or precision gate is unmet, the study remains a
confirmatory pilot and cannot support generalization or superiority.

A general typed-state claim requires:

- an uncertainty interval for the prespecified field-availability or
  consumption contrast that excludes zero and exceeds the predeclared smallest
  effect of interest;
- advantage against every load-bearing strongest all-facts donor under the
  closed-testing rule, not only a deliberately flattened shortcut;
- noninferiority on prespecified resource and safety outcomes;
- replication across independent domains;
- retained nulls, reversals, and donor ties;
- information and compute differences within quantitative parity thresholds
  frozen before outputs.

A general inference/reconstruction claim additionally requires the
multiplicity-adjusted interval for `Delta_reconstruction` to exceed its
predeclared smallest effect of interest, the reconstruction-consumption
interaction to have the prespecified direction, accuracy/calibration and
resource gates to pass, and advantage over the frozen strongest reconstruction
donor. If any inference gate fails, Q4-P1 may still report the separately
identified availability or consumption effects but must say
`INFERENCE_SUPERIORITY_NOT_ESTABLISHED`.

With lower normalized regret better, each donor contrast is

```text
Delta_donor = regret_donor - regret_candidate.
```

For every load-bearing donor, the multiplicity-adjusted lower confidence bound
for `Delta_donor` must exceed the prespecified smallest effect of interest.

If these gates fail, Q4-P1 remains a valid negative or boundary study. It cannot
be replaced by weaker controls or by dropping unfavorable domains.

## Custody rule

This protocol commit must be a strict ancestor of generator/task and annotation
freeze, policy/runner freeze, allocation, scoring/utility freeze, and result
commits. Every design component freezes before any policy output or outcome
access. Protocol and result first appearing in one commit is not accepted as
prospective evidence.

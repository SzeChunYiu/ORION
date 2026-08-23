# Q2-P1 prospective comparative successor protocol

Protocol identifier: `Q2-P1`

Protocol version: `1.0`

`EXECUTION_STATUS=NOT_STARTED`

This is a successor study. It does not alter the retrospective 51-receipt graph
or any predecessor disposition. The protocol must be committed in a source cut
that is a strict ancestor of every task allocation, policy output, adjudication,
or scientific outcome used by Q2-P1.

## Question

At a fixed resource budget, does typed responsibility localization followed by
donor-first successor admission improve the quality and auditability of the
next research decision relative to strong existing succession policies?

## Contribution tested

The candidate contribution is not “negative results become positive.” It is the
more falsifiable proposition that a typed, append-only succession policy reduces
invalid promotion and duplicate rediscovery while maintaining or improving the
scientific value of admitted successor questions.

## Eligible universe

Before any policy output is generated, a custodian must freeze a complete list
of eligible unresolved research-frontier packets. Inclusion uses result-blind
metadata only:

- an unresolved scientific question with an explicit decision point;
- a bounded evidence packet available to all study arms;
- at least one retained negative, null, partial, or donor-absorbed predecessor;
- a protected adjudication route that can later evaluate the successor;
- no study author has seen the protected outcome.

The target confirmatory universe is at least 60 packets from at least three
scientific or engineering domains. The programme, not a receipt or model call,
is the clustering unit. Before allocation, outcome-blind simulation must set a
minimum number of independent programme clusters for the prespecified primary
contrast and precision target; the design floor is twelve programmes. Every
eligible packet remains in the denominator, including abstentions, invalid
runs, timeouts, donor ties, and no-successor decisions.

If either the packet target or simulated programme-cluster minimum is unmet,
the study remains a registered pilot and cannot support a superiority claim.
No outcome-based denominator repair is allowed.

## Study arms

Each packet is assigned by a pre-generated domain- and programme-blocked random
schedule to one of the following policies. Compute, context, tool access, human
review time, and elapsed decision budget are matched.

1. **Typed successor policy:** responsibility localization, donor-first refusal,
   explicit admission predicate, and append-only predecessor disposition.
2. **Provenance plus preregistration:** complete provenance and predeclared next
   test without the candidate responsibility ontology.
3. **CEGAR/CEGIS-style policy:** counterexample-driven refinement with the
   strongest applicable repair rule.
4. **Adaptive-design policy:** a strongest available Bayesian optimization,
   active-learning, or expected-information-gain selector appropriate to the
   packet.
5. **Human-investigator policy:** independent domain experts selecting the next
   action under the same evidence and time budget.

Each policy must be implemented and frozen before allocation. A policy may
abstain. No arm may access another arm's output before freeze.

For every packet, freeze the applicable donor implementation, version, tuning
budget, and an independent baseline-quality audit before allocation. A donor
that is inapplicable or fails its audit yields `CANNOT_COMPARE`, never a
candidate win. Use complete within-programme blocks when isolated programme
forks are available; otherwise allocate entire programmes to prevent
interference. Blocked randomization and the prespecified model address
programme imbalance and confounding. Downstream executions occur in isolated branches so one
policy cannot change another arm's programme state.

## Admission record

Every proposed edge is a machine-bound tuple containing:

```text
predecessor_protocol_sha256
predecessor_outcome_sha256
responsibility_record_sha256
donor_search_protocol_sha256
donor_refusal_or_absorption_sha256
successor_protocol_sha256
policy_version
allocation_id
freeze_timestamp
source_commit
```

The edge checker verifies chronology, completeness, immutability, and declared
safety predicates. It does not assign scientific truth. Semantic validity is
judged independently.

## Outcomes

### Primary outcome and estimand

The primary outcome is a blinded, anchored 0--100 decision-value score for the
frozen successor. The rubric defines scientific-validity anchors and one fixed
aggregation rule. The rubric, scale, aggregation, adjudicator sampling,
missing/invalid-output treatment, and task-local utility mapping freeze before
allocation and before any policy output.

`NO_SUCCESSOR`, `ABSTAIN`, invalid output, and timeout each have a frozen
primary-score treatment. `CANNOT_COMPARE` retains the unit and invalidates the
affected superiority contrast; it never permits silent omission.

The single primary estimand is the programme-clustered mean difference between
the typed successor policy and one `STRONGEST_COMPARATOR_ID` chosen from arms
2--5 using external evidence before allocation. The comparator cannot be
selected from study outcomes. All other arm contrasts are secondary and use a
predeclared closed-testing or intersection-union multiplicity procedure.

Before adjudication, outputs are normalized into a common presentation and
policy-identifying vocabulary is redacted. Adjudicators never see arm identity.

### Co-primary safety outcome

Invalid-promotion rate: the fraction of admitted successors whose stated
licensing predicate is not supported by the predecessor evidence under blinded
adjudication.

The protocol freezes a minimum admission-coverage target and interval-precision
gate before allocation. Zero admission is reported as
`CANNOT_ESTIMATE_SAFETY`, never as zero invalid promotion. Low coverage cannot
create an artificial safety win. No-successor outcomes retain their frozen
primary decision-value score and remain in the intention-to-treat denominator.

### Secondary outcomes

- duplicate-donor rediscovery rate;
- negative-erasure or retroactive-promotion rate;
- time and monetary cost to freeze a valid successor;
- protected-outcome utility at a fixed downstream budget;
- information gain per unit cost;
- abstention and no-successor rate;
- inter-adjudicator agreement with uncertainty;
- provenance completeness and replay success.

Productivity, novelty, and field superiority are not inferred from a single
secondary measure.

## Analysis

The programme is the independent unit. Use a prespecified hierarchical model or
cluster-robust comparison with domain and programme effects. Outcome-blind
simulation freezes the minimum programme count, smallest effect of interest,
target interval precision, multiplicity procedure, and invalid-promotion safety
noninferiority margin before allocation. A superiority statement requires the
primary candidate-versus-`STRONGEST_COMPARATOR_ID` interval to exclude zero and
exceed the smallest effect of interest, while invalid promotion remains within
the safety margin. Superiority is prohibited unless the frozen admission
coverage and safety-interval precision gates are also met; otherwise safety is
`CANNOT_ESTIMATE_SAFETY`. Human and remaining algorithmic comparisons are
reported under the frozen secondary multiplicity procedure. The strongest
comparator is never selected after outcomes, and superiority cannot be inferred
from an average that hides failure against a load-bearing comparator.

Null, reversal, donor tie, and abstention outcomes remain in the denominator.

## Custody and release gates

1. Protocol commit is a strict ancestor of allocation and outcome commits.
2. Eligible-universe digest is frozen before allocation.
3. Policy implementations and resource budgets are frozen before outputs.
4. Arm identities are hidden from scientific adjudicators.
5. Raw requests, outputs, tool receipts, and environment manifests are archived.
6. Independent replay and independent semantic adjudication both complete.
7. A checker PASS grants no causal or superiority authority.

If any gate fails, Q2-P1 is reported as invalid or exploratory; it cannot repair
the retrospective Q2 evidence.
